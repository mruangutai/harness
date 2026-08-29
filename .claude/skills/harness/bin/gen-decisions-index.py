#!/usr/bin/env python3
"""Generate .harness/harness/docs/DECISIONS-INDEX.md from .harness/harness/docs/DECISIONS.md.

Usage:
    gen-decisions-index.py            write .harness/harness/docs/DECISIONS-INDEX.md in place
    gen-decisions-index.py --stdout   write the index to stdout, touch nothing
    gen-decisions-index.py --help     print this and exit, touch nothing (also -h)

There is no --check: to check for drift without writing, pipe the read-only mode into
diff — `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`.

See FEAT-04-decisions-index PLAN.md T-02 for the full contract. Everything left
of ' :: ' on a row is generated; everything right of it is hand-written and
preserved verbatim across regeneration.
"""
import os
import re
import sys

import harness_boundary

_BIN_DIR = os.path.dirname(os.path.abspath(__file__))

DOCS_DIR = os.path.join(".harness", "harness", "docs")
DECISIONS_PATH = os.path.join(DOCS_DIR, "DECISIONS.md")
INDEX_PATH = os.path.join(DOCS_DIR, "DECISIONS-INDEX.md")

HEADING_RE = re.compile(r"^##\s+(DEC-(\d+))\b")
DEC_REF_RE = re.compile(r"DEC-(\d+)")

TOPIC_VOCAB = {
    "org": ("org",),
    "cost": ("cost",),
    "gates": ("gates",),
    "tests": ("tests",),
    "tdd": ("tdd",),
    "skills": ("skills",),
    "hooks": ("hooks",),
    "domain": ("domain",),
    "github": ("github",),
    "expertise": ("expertise",),
    "docs": ("docs",),
    "map": ("map",),
    "orchestrator": ("orchestrator",),
    "dispatch": ("dispatch",),
    "digest": ("digest",),
    "approval": ("approval",),
    "security": ("security",),
    "deploy": ("deploy",),
    "state": ("state",),
    "brief": ("brief",),
    "plan": ("plan",),
    "qa": ("qa",),
    "worktree": ("worktree",),
    "budget": ("budget",),
}

HEADER = """<!-- index-contract v1 -->
<!-- GENERATED except the text after ` :: ` on each row.
     Regenerate: .agents/skills/harness/bin/gen-decisions-index.py -->

# DECISIONS — index

**A row is an open-or-skip filter, never the rule itself.** Its only job is to answer "do I open this
entry?" Never act on a ruling here: open `.harness/harness/docs/DECISIONS.md` at the `@line` anchor and read
the entry. Rows written during the one-time backfill are second-hand paraphrase.

**Never read the authority whole (DEC-150).** Grep this index, then open the two or three entries that
bear on your task. Decisions cited in a dispatch are a floor, not a ceiling.

**Adding a decision:** its author writes its ruling here, in the same commit that appends the entry.

Row: `- DEC-NN @<line> [tags] refs: <graph> :: <ruling>`.
"""

                                       # THE row grammar, single-sourced. The unit test
                                       # imports these two by path rather than restating
                                       # them: a test carrying its own copy of the grammar
                                       # agreed with nothing, and the disagreement surfaced
                                       # only as a silently-dropped ruling (B-2).
ROW_RE = re.compile(r"^- (DEC-\d+) .*? :: (.*)$")
# Deliberately looser than ROW_RE: anything a human or agent MEANT as a row. A line that
# looks like a row but does not parse as one is an error, never a non-row — treating it as
# "no prior row" is what silently discarded a hand-written ruling and replaced it with
# RULING PENDING, a data loss recoverable only from git.
ROW_LOOKALIKE_RE = re.compile(r"^\s*-\s*(DEC-\d+)\b")


def defenced_lines(text):
    """Return [(orig_line_no, line), ...] for lines NOT inside a ``` code fence.

    A '## DEC-N' heading (or anything else) shown inside a fence is
    documentation of the format, not a live declaration, and must not be
    harvested. This must run BEFORE all extraction: headings, amendments,
    the reference graph, and tag scoring all see the de-fenced body.
    """
    out = []
    infence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            infence = not infence
            continue
        if infence:
            continue
        out.append((lineno, line))
    return out


def parse_decisions(text):
    """Return dict: key (e.g. 'DEC-83') -> {"num": int, "line": int, "body": str}."""
    lines = defenced_lines(text)
    headings = []  # (index_into_lines, key, num, orig_lineno)
    for idx, (lineno, line) in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            headings.append((idx, m.group(1), int(m.group(2)), lineno))

    decisions = {}
    for i, (idx, key, num, lineno) in enumerate(headings):
        if key in decisions:
            print(f"COLLISION: duplicate decision key {key} after fence-stripping", file=sys.stderr)
            sys.exit(1)
        end_idx = headings[i + 1][0] if i + 1 < len(headings) else len(lines)
        body_lines = [l for (_, l) in lines[idx:end_idx]]
        decisions[key] = {
            "num": num,
            "line": lineno,
            "title": lines[idx][1],
            "body": "\n".join(body_lines),
        }
    return decisions, lines, headings


def compute_refs(body, own_num, live_nums):
    seen = {}
    for m in DEC_REF_RE.finditer(body):
        n = int(m.group(1))
        if n == own_num or n not in live_nums:
            continue
        if n not in seen:
            seen[n] = m.group(0)
    return [seen[n] for n in sorted(seen)]


def compute_tags(body):
    body_lower = body.lower()
    scores = {}
    for tag, substrs in TOPIC_VOCAB.items():
        score = sum(body_lower.count(sub) for sub in substrs)
        if score > 0:
            scores[tag] = score
    tags = sorted(scores, key=lambda t: (-scores[t], t))[:4]
    return tags


def strip_trailing_clauses(ruling):
    """Repeatedly strip a trailing ok-stale marker. Returns
    (stripped_prose, had_ok_stale: bool)."""
    cur = ruling.strip()
    had_ok_stale = False
    prev = None
    while prev != cur:
        prev = cur
        m = re.search(r"<!--\s*ok-stale\s*-->\s*$", cur)
        if m:
            had_ok_stale = True
            cur = cur[: m.start()].strip()
    return cur, had_ok_stale


def build_index(text, existing_rows):
    decisions, lines, headings = parse_decisions(text)
    live_nums = {num for (_, _, num, _) in headings}

    # Orphan detection: existing rows with non-sentinel ruling text whose DEC
    # number has no live heading. Hard error, never a silent drop.
    orphans = []
    for key, raw_ruling in existing_rows.items():
        if key in decisions:
            continue
        prose, _ = strip_trailing_clauses(raw_ruling)
        if prose and prose != "\N{WARNING SIGN} RULING PENDING":
            orphans.append((key, raw_ruling))
    if orphans:
        for key, raw_ruling in orphans:
            print(
                f"ORPHAN: {key} {raw_ruling!r} has a ruling in the index but "
                f"no live heading in {DECISIONS_PATH}",
                file=sys.stderr,
            )
        return None

    rows = []
    for key, dec in sorted(decisions.items(), key=lambda kv: kv[1]["num"]):
        num = dec["num"]
        tags = compute_tags(dec["body"])
        refs = compute_refs(dec["body"], num, live_nums)

        if key in existing_rows:
            prose, had_ok_stale = strip_trailing_clauses(existing_rows[key])
        else:
            prose, had_ok_stale = "\N{WARNING SIGN} RULING PENDING", False

        # had_ok_stale IS DELIBERATELY NOT RE-EMITTED. The marker belonged to the
        # propagation checker, struck whole under DEC-188 — it now means nothing, and
        # a generator that faithfully preserved one would let a future author revive
        # dead syntax no gate can object to. Measured before this changed: a planted
        # marker propagated through regeneration while check-state.sh and the whole
        # unit suite stayed green. Stripping on read and never writing closes that.
        ruling = prose

        left = f"- {key} @{dec['line']}"
        left += f" [{','.join(tags)}] refs: {' '.join(refs)}"
        rows.append(f"{left} :: {ruling}")

    return rows


def parse_existing_index(text):
    """{'DEC-NN': ruling}. Raises MalformedRow rather than skipping a broken row."""
    rows, malformed = {}, []
    for n, line in enumerate(text.splitlines(), 1):
        m = ROW_RE.match(line)
        if m:
            rows[m.group(1)] = m.group(2)
        elif ROW_LOOKALIKE_RE.match(line):
            malformed.append((n, line))
    if malformed:
        raise MalformedRow(malformed)
    return rows


class MalformedRow(Exception):
    """A line in the index means to be a row but does not parse as one."""

    def __init__(self, rows):
        self.rows = rows
        super().__init__(f"{len(rows)} malformed row(s)")


def parse_argv(argv):
    """Return True for stdout mode, False for the write path — or exit.

    Unvalidated argv used to mean every unrecognized flag, `--help` first among them,
    fell through to the WRITE path (#140): the one command a reader runs to learn what
    this script does was the command that rewrote the repo, and it fired mid-review on
    PR #138. An unknown flag must therefore refuse LOUDLY rather than default to the
    only branch that touches the tree — silence here is indistinguishable from a
    legitimate regeneration, because the file is generated.
    """
    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        sys.exit(0)
    unknown = [a for a in argv if a != "--stdout"]
    if unknown:
        print(f"gen-decisions-index: unrecognized argument(s): {' '.join(unknown)}. "
              f"Wrote nothing.", file=sys.stderr)
        print(f"\n{__doc__.strip()}", file=sys.stderr)
        sys.exit(2)
    return "--stdout" in argv


def main():
    stdout_mode = parse_argv(sys.argv[1:])

    project_dir = harness_boundary.resolve_root(_BIN_DIR)
    os.chdir(project_dir)

    if not os.path.isfile(DECISIONS_PATH):
        print(f"gen-decisions-index: {DECISIONS_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    text = open(DECISIONS_PATH, encoding="utf-8").read()

    existing_rows = {}
    if os.path.isfile(INDEX_PATH):
        existing_text = open(INDEX_PATH, encoding="utf-8").read()
        try:
            existing_rows = parse_existing_index(existing_text)
        except MalformedRow as e:
            # REPAIR, never regenerate: this script is the only thing that can rebuild the
            # index, so telling the reader to regenerate would tell them to destroy the
            # hand-written rulings on every other row. Quote the line so the fix is local.
            print(f"gen-decisions-index: {INDEX_PATH} has "
                  f"{len(e.rows)} malformed row(s). Wrote nothing.", file=sys.stderr)
            for n, line in e.rows:
                print(f"  {INDEX_PATH}:{n}: {line}", file=sys.stderr)
            print("\nEach line above is meant to be a row but does not match the grammar:\n"
                  "  - DEC-NN @<line> [tags] refs: <graph> :: <ruling>\n"
                  "Repair those lines in place — the ' :: ' separator, with a single space on "
                  "each side, is what carries the hand-written ruling. Do NOT regenerate to "
                  "fix this; regenerating cannot recover a ruling it could not read.",
                  file=sys.stderr)
            sys.exit(1)

    rows = build_index(text, existing_rows)
    if rows is None:
        # Orphan detected; already reported to stderr. Write nothing.
        sys.exit(1)

    output = HEADER + "\n" + "\n".join(rows) + "\n"

    if stdout_mode:
        sys.stdout.write(output)
        return

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(output)


if __name__ == "__main__":
    main()
