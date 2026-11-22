#!/usr/bin/env python3
"""FEAT-2297 T-10 release evidence: every inventory row is disposed and the old suites shrank.

    check-config-reduction.py --review-ref REF --receipt PATH [--base SHA]

Feature-only tooling, never a discovered suite. Subjects are read with `git show` at committed
refs; an unreadable ref or blob fails. The base defaults to `git merge-base REF origin/main`
(signed D-06 amendment), so features merged from main are never measured as this one's.

Gates, all hard: every non-UNAFFECTED row of the pinned inventory is disposed once in the receipt
and all 67 inventory files are assessed; a deleted or rewritten row's inventoried span no longer
appears verbatim at REF (a stale fail-open assertion); the pre-existing affected test/helper files
shrink on net (Gate A); every new one is enumerated with its exact line count and the SC/D it
covers (Gate B); no test or helper escapes the measured roots; the fleet loses only the smoke
entry. The measurement block of the receipt is rewritten on every run. Offline positive and
negative self-controls run first, every time.
"""
import argparse
import collections
import hashlib
import re
import subprocess
import sys

import yaml

FEATURE = ".harness/harness/features/FEAT-2297-harness-json-schema"
CHECKER = f"{FEATURE}/notes/check-config-reduction.py"
INVENTORY = f"{FEATURE}/notes/test-inventory-2026-11-22.md"
INVENTORY_SHA256 = "d3927f1b0fe6378b30284b3b7294bb2fd4dde814eb23e8b1bfc7024bfcf24496"
INVENTORY_REF = "c1724230c4d931ad46d433c8ba93df8cf312f898"  # the main the scouts classified
SIGNED_ROWS = {"REMOVABLE": 30, "UPDATE-BEHAVIOR": 12, "UPDATE-FIXTURE": 110}
SIGNED_FILES = 67
ALLOWED = {"REMOVABLE": {"DELETED", "RETAINED"}, "UPDATE-BEHAVIOR": {"REWRITTEN", "DELETED"},
           "UPDATE-FIXTURE": {"MIGRATED", "DELETED"}}
SIGNED_RETENTIONS = 2
FLEET = ".harness/factory/fleet.yaml"
SMOKE, KAYA = "mruangutai/harness-factory-smoke", "mruangutai/kaya"
ROW = re.compile(r"^\s*(?:-\s+)?`?(?P<path>[\w./-]+):(?P<span>[\d,–-]+)\s*\|\s*"
                 r"(?P<cls>REMOVABLE|UPDATE-BEHAVIOR|UPDATE-FIXTURE|UNAFFECTED)\s*\|.*\|\s*[~\d]+`?\s*$")
TEST_LIKE = re.compile(r"(^|/)(test[-_][^/]*|[^/]*_test\.\w+|[^/]*\.test\.ts|[^/]*_support\.py"
                       r"|conftest\.py)$|(^|/)fixtures/[^/]*$")
CODE = (".py", ".ts", ".js", ".json", ".yaml", ".yml", ".sh")
COVERS = re.compile(r"\b(SC-\d\d|D-0\d)\b")
BEGIN, END = "<!-- measured:begin -->", "<!-- measured:end -->"


def measured(path):
    return path.startswith("tests/") or path == CHECKER


def parse_inventory(text):
    return [m.groupdict() for line in text.splitlines() if (m := ROW.match(line))]


def tables(text):
    """`## Heading` -> rows of stripped cells, header and separator rows dropped."""
    out, heading = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            out.setdefault(heading, [])
        elif heading and line.startswith("|") and not re.match(r"^\|[\s|:-]+\|$", line):
            out[heading].append([c.strip().strip("`") for c in line.strip().strip("|").split("|")])
    return {k: rows[1:] for k, rows in out.items()}


def row_lines(text, span):
    lines = text.splitlines()
    picked = []
    for part in span.replace("–", "-").split(","):
        lo, _, hi = part.partition("-")
        picked += lines[int(lo) - 1:int(hi or lo)]
    return [line.strip() for line in picked if line.strip()]


def disposition_findings(rows, table, file_table):
    findings, seen, retained = [], collections.Counter(), 0
    keyed = collections.Counter((r["path"] + ":" + r["span"], r["cls"]) for r in rows if r["cls"] != "UNAFFECTED")
    for cells in table:
        if len(cells) < 5:
            findings.append(f"disposition row has fewer than five cells: {cells}")
            continue
        ident, cls, verdict, coverage, reason = cells[:5]
        if (ident, cls) not in keyed:
            findings.append(f"disposition names no inventory row: {ident} {cls}")
        elif seen[(ident, cls)] >= keyed[(ident, cls)]:
            findings.append(f"inventory row disposed more often than it is listed: {ident} {cls}")
        elif verdict not in ALLOWED[cls] or not coverage:
            findings.append(f"{ident} {cls}: disposition {verdict!r} needs one of "
                            f"{sorted(ALLOWED[cls])} and a named replacement coverage")
        retained += verdict == "RETAINED"
        if verdict == "RETAINED" and "signed" not in reason.lower():
            findings.append(f"{ident}: a retention must name its signed reason")
        seen[(ident, cls)] += 1
    findings += [f"inventory row not disposed: {i} {c}" for (i, c), n in sorted(keyed.items()) if seen[(i, c)] < n]
    if retained > SIGNED_RETENTIONS:
        findings.append(f"{retained} REMOVABLE retentions; only {SIGNED_RETENTIONS} were signed")
    assessed = {cells[0] for cells in file_table if len(cells) > 1 and cells[1]}
    findings += [f"inventory file not assessed: {p}" for p in sorted({r["path"] for r in rows} - assessed)]
    return findings


def stale_findings(rows, table, span_text, review_text):
    """A deleted or rewritten row whose inventoried text still stands verbatim at the review ref."""
    verdicts = {(c[0], c[1]): c[2] for c in table if len(c) >= 3}
    findings = []
    for r in rows:
        ident, cls = r["path"] + ":" + r["span"], r["cls"]
        if not (cls == "UPDATE-BEHAVIOR" or verdicts.get((ident, cls)) == "DELETED"):
            continue
        before, after = span_text(r["path"], r["span"]), review_text(r["path"])
        if after is None or len(before) < 2:
            continue
        now = [line.strip() for line in after.splitlines() if line.strip()]
        if any(now[i:i + len(before)] == before for i in range(len(now) - len(before) + 1)):
            findings.append(f"stale assertion: {ident} ({cls}) still stands verbatim at the review ref")
    return findings


def delta_findings(changes, enumerated):
    """changes: path -> (base_lines | None, review_lines | None) for every changed path."""
    findings = [f"test/helper escaped the measured roots: {p}" for p, (b, a) in sorted(changes.items())
                if not measured(p) and b is None and a is not None and p.endswith(CODE) and TEST_LIKE.search(p)]
    inside = {p: v for p, v in changes.items() if measured(p)}
    gate_a = sum((a or 0) - b for b, a in inside.values() if b is not None)
    if gate_a >= 0:
        findings.append(f"Gate A: pre-existing affected test/helper files net {gate_a:+d}; must be negative")
    for path, (base, review) in sorted(inside.items()):
        if base is not None or review is None:
            continue
        lines, covers = enumerated.get(path, (None, ""))
        if lines != review or not COVERS.search(covers):
            findings.append(f"Gate B: new {path} ({review} lines) is not enumerated with its exact "
                            f"line count and the SC/D it covers")
    return findings, gate_a


def fleet_findings(base_text, review_text):
    base, review = yaml.safe_load(base_text), yaml.safe_load(review_text)
    names = [m.get("name") for m in review.get("repos", [])]
    expected = dict(base, repos=[m for m in base.get("repos", []) if m.get("name") != SMOKE])
    kaya = [[m for m in doc.get("repos", []) if m.get("name") == KAYA] for doc in (base, review)]
    return ([f"fleet still lists {SMOKE}"] if SMOKE in names else []) + \
           ([f"{KAYA} changed or is missing"] if not kaya[1] or kaya[0] != kaya[1] else []) + \
           (["fleet differs from the base by more than the smoke entry"] if review != expected else [])


def self_control_failures():
    rows = [{"path": "tests/a.py", "span": "1-2", "cls": "REMOVABLE"},
            {"path": "tests/a.py", "span": "4-5", "cls": "UPDATE-BEHAVIOR"}]
    good = [["tests/a.py:1-2", "REMOVABLE", "DELETED", "T-07 tests/b.py::x", ""],
            ["tests/a.py:4-5", "UPDATE-BEHAVIOR", "REWRITTEN", "T-07 tests/a.py::y", ""]]
    files = [["tests/a.py", "assessed"]]
    old = "x = 1\nassert ok\n\nif missing:\n    allow()\n"
    fleet = f"repos:\n  - name: {SMOKE}\n  - name: {KAYA}\n"
    gone = f"repos:\n  - name: {KAYA}\n"
    span = lambda p, s: row_lines(old, s)
    shrunk = {"tests/a.py": (5, 2), "tests/new.py": (None, 3)}
    probes = {
        "positive: a complete, fresh receipt": not (
            disposition_findings(rows, good, files) + stale_findings(rows, good, span, lambda p: "y()\n")
            + delta_findings(shrunk, {"tests/new.py": (3, "D-06")})[0] + fleet_findings(fleet, gone)),
        "negative: an undisposed inventory row": disposition_findings(rows, good[:1], files),
        "negative: a stale fail-open assertion": stale_findings(rows, good, span, lambda p: old),
        "negative: a zero pre-existing delta": delta_findings({"tests/a.py": (5, 5)}, {})[0],
        "negative: a positive pre-existing delta": delta_findings({"tests/a.py": (5, 6)}, {})[0],
        "negative: an unenumerated new file": delta_findings(shrunk, {})[0],
        "negative: a test moved out of the roots": delta_findings(
            {"tests/a.py": (5, 0), "lib/test-a.py": (None, 5)}, {})[0],
        "negative: the fleet lost Kaya too": fleet_findings(fleet, "repos: []\n"),
    }
    return [name for name, ok in probes.items() if not ok]


def git(*args):
    done = subprocess.run(["git", *args], capture_output=True, text=True)
    if done.returncode:
        raise SystemExit(f"check-config-reduction: git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def show(ref, path):
    """The blob's text at ref, or None when the path is absent there (a missing ref still fails)."""
    listed = git("ls-tree", "--name-only", ref, "--", path).strip()
    return git("show", f"{ref}:{path}") if listed == path else None


def line_count(text):
    return None if text is None else len(text.splitlines())


def measurement(base, review, command, changes, gate_a):
    out = [BEGIN, f"- base `{base}` (`{command}`)", f"- review `{review}`", "",
           "| File | Base | Review | Delta |", "|---|---|---|---|"]
    inside = sorted(p for p in changes if measured(p))
    for p in inside:
        b, a = changes[p]
        out.append(f"| `{p}` | {b if b is not None else 'new'} | {a if a is not None else 'deleted'} "
                   f"| {(a or 0) - (b or 0):+d} |")
    new = sum(a for b, a in (changes[p] for p in inside) if b is None and a)
    out += ["", f"- Gate A, pre-existing affected files: {gate_a:+d}",
            f"- Gate B, new files enumerated below: {new:+d}",
            f"- Reported total, both populations: {gate_a + new:+d}", END]
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--review-ref", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--base")
    args = parser.parse_args(argv)
    broken = self_control_failures()
    if broken:
        print("\n".join(f"SELF-CONTROL FAILED  {name}" for name in broken))
        return 1
    review = git("rev-parse", "--verify", f"{args.review_ref}^{{commit}}").strip()
    command = f"git merge-base {args.review_ref} origin/main"
    base = git("rev-parse", "--verify", f"{args.base or git('merge-base', review, 'origin/main').strip()}^{{commit}}").strip()
    command = "--base" if args.base else command
    inventory = show(review, INVENTORY)
    if inventory is None or hashlib.sha256(inventory.encode()).hexdigest() != INVENTORY_SHA256:
        raise SystemExit(f"check-config-reduction: {INVENTORY} is missing or not the signed inventory")
    rows = parse_inventory(inventory)
    counts = {c: sum(r["cls"] == c for r in rows) for c in SIGNED_ROWS}
    if counts != SIGNED_ROWS or len({r["path"] for r in rows}) != SIGNED_FILES:
        raise SystemExit(f"check-config-reduction: inventory parses to {counts}, not the signed rows")
    with open(args.receipt, encoding="utf-8") as handle:
        receipt = handle.read()
    found = tables(receipt)
    table, files = found.get("Dispositions", []), found.get("Files", [])
    enumerated = {c[0]: (int(c[1]) if c[1].isdigit() else None, c[2])
                  for c in found.get("New coverage", []) if len(c) >= 3}
    base_spans = {}
    span = lambda p, s: row_lines(base_spans.setdefault(p, show(INVENTORY_REF, p) or ""), s)
    paths = git("diff", "--no-renames", "--name-only", base, review).split()
    changes = {p: (line_count(show(base, p)), line_count(show(review, p))) for p in paths}
    gated, gate_a = delta_findings(changes, enumerated)
    findings = (disposition_findings(rows, table, files)
                + stale_findings(rows, table, span, lambda p: show(review, p)) + gated
                + fleet_findings(show(base, FLEET), show(review, FLEET)))
    if BEGIN not in receipt or END not in receipt:
        findings.append(f"{args.receipt} has no {BEGIN} … {END} measurement block")
    else:
        head, rest = receipt.split(BEGIN, 1)
        with open(args.receipt, "w", encoding="utf-8") as handle:
            handle.write(head + measurement(base, review, command, changes, gate_a) + rest.split(END, 1)[1])
    print("\n".join(f"FAIL  {f}" for f in findings) or f"OK  base {base[:12]} review {review[:12]} "
          f"Gate A {gate_a:+d}; {sum(counts.values())} rows disposed; {SIGNED_FILES} files assessed")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
