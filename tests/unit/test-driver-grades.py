#!/usr/bin/env python3
"""FEAT-66 SC-01: the three rule evaluators that graded 1 — `check-domain.shape_problems`,
`validate-digest.validate`, `plan-merge.apply_merge` — are drivers over per-rule functions and
grade at the production bar (4) or exactly 2, the one grade the grader itself excepts
(`code_grade._blocks`). Measured with the fleet grader's own `grade_source`, so the number
this locks is the number a review would see.

Why only the three names: every function the refactor EXTRACTS is new, has no pre-image, and
`code_grade` already gates it at bar 4 in review (DEC-209 recomputes the enum). The retained
drivers keep their names and so keep their grade-1 pre-images, which the ratchet tolerates
forever — this suite is what holds them at the bar. Not a file-wide lock: `approval_guard`,
`parse_digest`, `hook_mode` and the grade-3 helpers around them are out of scope (SC-03) and
the second wave's (ledger: notes/grilling-complex-function-three-drivers-2026-09-26.md).

Runnable directly with python3, no pytest. Loaded from FEAT66_BIN when set, else the sibling
bin/ — the red-first receipt runs this file against the pre-refactor tree that way.
"""
import os
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.environ.get("FEAT66_BIN") or os.path.join(ROOT, ".claude", "skills", "harness", "bin")
sys.path.insert(0, BIN_DIR)

from code_grade import grade_source  # noqa: E402

BAR = 4
DRIVERS = (("check-domain.py", "shape_problems"), ("validate-digest.py", "validate"),
           ("plan-merge.py", "apply_merge"))

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {'' if cond else detail}".rstrip())
    if not cond:
        failures.append(name)


for name, driver in DRIVERS:
    with open(os.path.join(BIN_DIR, name), encoding="utf-8") as stream:
        found = [g for g in grade_source(stream.read(), name) if g.qualname == driver]
    check(f"{name}: {driver} exists under its name", len(found) == 1,
          "renamed or deleted — the pre-image ratchet and every caller key on the name")
    if found:
        g = found[0]
        check(f"{name}: {driver} grades >= {BAR} or exactly 2", g.grade >= BAR or g.grade == 2,
              f"grade {g.grade} ({g.driver} cyc={g.cyclomatic} cog={g.cognitive} abc={g.abc})")

print(f"{len(failures)} failure(s)" if failures else "ALL PASS")
sys.exit(1 if failures else 0)
