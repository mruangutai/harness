#!/usr/bin/env python3
"""check-state retires every row that read a local working file (FEAT-2641, DEC-260).

notes/, runs/ and observations/ are local working files no CI checkout carries, so a row that
read one would be red in CI by construction. The eleven numbers below are RETIRED -- named in
the catalogue, never run and never reused (DEC-205) -- INV-7 and INV-40 stay as rows, and no
surviving row declares a read of a notes, runs or handoff path.
"""
import os
import sys

_TESTS = os.path.dirname(os.path.abspath(__file__))
_BIN = os.path.join(_TESTS, "..", "..", ".claude", "skills", "harness", "bin")
sys.path.insert(0, os.path.abspath(_BIN))

from check_state import table  # noqa: E402

RETIRED_NUMBERS = ("INV-8", "INV-12", "INV-15", "INV-16", "INV-17", "INV-18",
                   "INV-36", "INV-43", "INV-46", "INV-47", "INV-51")
SURVIVING = ("INV-7", "INV-40")
WORKING_FILE_MARKERS = ("notes/", "runs/", "/runs", "handoff")

failures = []


def check(ok, label):
    print(("ok   " if ok else "FAIL ") + label)
    if not ok:
        failures.append(label)


def main():
    rows = [row for group in table.INVARIANTS for row in group.rows]
    names = {row.name for row in rows}
    for number in RETIRED_NUMBERS:
        check(number in table.RETIRED, f"{number} is a RETIRED key")
        check(number not in names, f"{number} names no INVARIANTS row")
    for number in SURVIVING:
        check(number in names, f"{number} is still a row")
    for row in rows:
        hits = [read for read in row.reads if any(m in read for m in WORKING_FILE_MARKERS)]
        check(not hits, f"{row.name} reads no notes, runs or handoff path {hits or ''}".rstrip())
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
