#!/usr/bin/env python3
"""observations-merge.py — union-merge apply for per-feature observations logs
(FEAT-32 T-04, D-05).

Fixes the last-writer-wins loss #606 recorded: two contexts of the same agent each append a
whole-file write to the same `.harness/.../observations/<agent>.md`, and the second write
silently discards whatever bullets the first one added. This CLI never does that: it reads the
existing log under an exclusive lock (harness_merge.locked_update), computes an ORDER-PRESERVING
UNION of BULLET RECORDS keyed on the record's whitespace-normalised text, and writes that union
back atomically.

    observations-merge.py apply --file <path to an observations log> --entries <path or - for stdin>

D-05 is deliberately NOT expertise-merge.py's section-plus-id union: an observations log has no
entry ids to key on, so two records with different text are simply both kept. There is no
conflict exit for this file class and no cap, so this tool defines only three exit codes:

    0  applied — stdout lists one ADDED line per record added (first 60 chars of its normalised
       text), one PRESERVED line per base record kept, then a final APPLIED line
    6  the lock could not be acquired within the retry budget (harness_merge)
    9  --file does not resolve to an observations log this tool owns

THE FORMAT (D-05, taken from a real log): an optional title line beginning with a hash, then
bullet records. A record begins at a line matching a dash and a space at column zero and
continues through every following line — including an indented continuation line or a blank
line — until the next such dash line or end of file.

python3 stdlib only, no third-party imports, so this runs on any machine that runs the harness.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)

# Module-level literal guarding step 5 (the union computation) and nothing else. False
# reproduces today's naive behaviour exactly: the entries text replaces the file whole, with no
# comparison against the base at all — today's last-writer-wins, verbatim. Nothing outside this
# file's source text ever changes this: no environment variable, no flag. A test proves the
# union assertions are load-bearing by mutating this literal, by name, in a copy of this file.
UNION_MERGE = True

# A features directory either directly under a .harness segment or nested one segment deeper
# (repo-tier), a FEAT- or BUG- prefixed directory, the literal segment observations, and a
# filename of the form harness-<lowercase letters, digits, hyphens>.md. Matched on the RESOLVED
# path only (harness_merge.require_destination), never the literal argument.
OBSERVATIONS_TAIL = re.compile(
    r"(?:^|/)\.harness/(?:[^/]+/)?features/(?:FEAT|BUG)-[^/]+/observations/"
    r"harness-[a-z0-9-]+\.md$"
)

RECORD_RE = re.compile(r"^- ")


def parse_observations(text):
    """Parse observations markdown text into (title_line_or_None, [record_text, ...]).

    title_line, if present, includes no trailing newline. Each record_text is the raw text of
    the record, including its own trailing newline(s) where the source had them — WRITE the
    original text, never the normalised form.
    """
    if text is None:
        return None, []
    lines = text.splitlines(keepends=True)
    idx = 0
    title = None
    if lines and lines[0].startswith("#"):
        title = lines[0].rstrip("\n")
        idx = 1

    records = []
    current = []
    for line in lines[idx:]:
        if RECORD_RE.match(line):
            if current:
                records.append("".join(current))
            current = [line]
        else:
            if current:
                current.append(line)
            # else: content before the first bullet record (e.g. a blank line after the title)
            # belongs to no record and is discarded — the title/blank-line separator is
            # re-generated on output, not carried through.
    if current:
        records.append("".join(current))
    return title, records


def normalize(text):
    """Strip trailing whitespace from every line, collapse runs of whitespace to a single
    space, and join. This is the comparison key for dedup — WRITE the original text, compare on
    this. A record differing from another only in line wrapping, trailing spaces, or the number
    of trailing blank lines it carries normalises to the same string."""
    lines = [line.rstrip() for line in text.splitlines()]
    joined = "\n".join(lines)
    return re.sub(r"\s+", " ", joined).strip()


def apply_merge(base_bytes, entries_text, stem):
    """Returns (output_bytes, added_records, preserved_records) — the latter two lists of raw
    record text, in the order printed. Step 4's UNION_MERGE off path returns the entries bytes
    verbatim, with nothing added or preserved — today's last-writer-wins."""
    if not UNION_MERGE:
        return entries_text.encode("utf-8"), [], []

    base_text = base_bytes.decode("utf-8") if base_bytes is not None else None
    base_title, base_records = parse_observations(base_text)
    entries_title, entries_records = parse_observations(entries_text)

    title = base_title or entries_title or f"# Observations - {stem}"

    seen = {normalize(r) for r in base_records}
    added = []
    for record in entries_records:
        key = normalize(record)
        if key not in seen:
            seen.add(key)
            added.append(record)

    chunks = [title.rstrip("\n") + "\n", "\n"]
    chunks.extend(base_records)
    chunks.extend(added)
    output = "".join(chunks)
    return output.encode("utf-8"), added, list(base_records)


def _preview(record):
    return normalize(record)[:60]


def cmd_apply(args):
    file_path = args.file
    try:
        resolved = harness_merge.require_destination(
            file_path,
            OBSERVATIONS_TAIL,
            "an observations log under a features directory",
            [
                "  a legal path looks like "
                ".harness/features/FEAT-NN-slug/observations/harness-<agent>.md or",
                "  .harness/<repo>/features/FEAT-NN-slug/observations/harness-<agent>.md.",
                "  This tool merges observations logs only.",
            ],
        )
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    if args.entries == "-":
        entries_text = sys.stdin.read()
    else:
        with open(args.entries, encoding="utf-8") as f:
            entries_text = f.read()

    stem = os.path.splitext(os.path.basename(resolved))[0]
    result = {}

    def transform(base_bytes):
        out_bytes, added, preserved = apply_merge(base_bytes, entries_text, stem)
        result["added"] = added
        result["preserved"] = preserved
        return out_bytes

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    for record in result.get("added", []):
        print(f"ADDED {_preview(record)}")
    for record in result.get("preserved", []):
        print(f"PRESERVED {_preview(record)}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(prog="observations-merge.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_apply = sub.add_parser("apply", help="merge entries into an observations log")
    p_apply.add_argument("--file", required=True, help="path to the observations log")
    p_apply.add_argument(
        "--entries", required=True, help="path to the proposed entries, or - for stdin"
    )
    p_apply.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
