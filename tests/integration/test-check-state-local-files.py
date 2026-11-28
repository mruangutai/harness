#!/usr/bin/env python3
"""check-state.py grades a feature that carries no local working files (FEAT-2641, DEC-260).

A CI checkout never holds a feature's notes/, runs/ or observations/: they are local working
files. A feature at station review with a signed BRIEF, an approved plan and a feature.json
recording a PASS validate run must therefore pass check-state with none of them on disk, and
`--list` shows every row that read one as retired. The positive control proves the fixture is
graded at all: the same record with cycles_used -1 is INV-7's violation.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json
import os
import subprocess
import sys
import tempfile
from check_state.table import INVARIANTS
from check_state_support import SCRIPT, _root_env
from harness_config_support import write_config

FEAT = "FEAT-LOCAL"
RETIRED_NUMBERS = ("INV-8", "INV-12", "INV-15", "INV-16", "INV-17", "INV-18",
                   "INV-36", "INV-43", "INV-46", "INV-47", "INV-51")
REVIEW_SHA = "0123456789abcdef0123456789abcdef01234567"

BRIEF = """# FEAT-LOCAL: fixture

## Goal
A feature with no local working files.

## Success criteria
- SC-01: check-state passes. verify: test

## Approval
status: approved
by: operator
date: 2026-11-27
"""

failures = []


def check(ok, label, detail=""):
    print(("ok   " if ok else "FAIL ") + label + (f"\n     {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(label)


def _plan():
    return {
        "schema": "plan/1", "feature": FEAT, "status": "review",
        "approval": {"status": "approved", "approved_by": "operator", "date": "2026-11-27"},
        "lanes": {"resolved_at": "abc123", "rows": []}, "decisions": [],
        "panel": {"last_run": "panel-validator", "cycle": 0, "findings": [],
                  "readers": [{"reader": "should-not-exist", "status": "ran"},
                              {"reader": "scope", "status": "ran"},
                              {"reader": "goalcheck", "status": "ran"}]},
        "tasks": [{"id": "T-01", "title": "fixture", "traces": ["SC-01"],
                   "change_type": "logic", "execution_mode": "team",
                   "execution_reason": "fixture", "depends_on": [], "status": "done",
                   "files": ["fixture"], "verify": "true", "intent": "fixture"}],
    }


def _record(cycles_used):
    return {
        "feature_id": FEAT, "branch": "none", "pr": None,
        "review_sha": REVIEW_SHA, "cycles_used": cycles_used, "max_total_cycles": 10,
        "runs": [
            {"id": "build-eng", "lead": "harness-eng-lead", "verdict": "PASS"},
            {"id": "validate-validator", "lead": "harness-validator-lead", "verdict": "PASS"},
        ],
    }


def _fixture(tmp, cycles_used):
    """The review-station feature: signed BRIEF, approved plan with its panel record, and a
    feature.json recording an eng run and a validate run at PASS -- and nothing else."""
    fdir = os.path.join(tmp, ".harness", "harness", "features", FEAT)
    os.makedirs(fdir)
    write_config(os.path.join(tmp, ".harness", "harness.json"), {"github": {"sync": False}})
    with open(os.path.join(fdir, "BRIEF.md"), "w", encoding="utf-8") as f:
        f.write(BRIEF)
    with open(os.path.join(fdir, "plan.yaml"), "w", encoding="utf-8") as f:
        json.dump(_plan(), f)
    with open(os.path.join(fdir, "feature.json"), "w", encoding="utf-8") as f:
        json.dump(_record(cycles_used), f, indent=2)
    return fdir


def _run(tmp, *args):
    proc = subprocess.run([sys.executable, SCRIPT, *args], cwd=tmp, capture_output=True,
                          text=True, env=_root_env(tmp))
    return proc.returncode, proc.stdout + proc.stderr


def case_no_working_files_is_clean():
    with tempfile.TemporaryDirectory() as tmp:
        fdir = _fixture(tmp, 0)
        for name in ("notes", "runs", "observations"):
            check(not os.path.exists(os.path.join(fdir, name)), f"fixture has no {name}/")
        # Every feature-scoped row, read from the table: the repo-scoped rows grade the
        # checkout (worktrees, hook install, layout, fleet), which a temp fixture cannot be.
        feature_rows = ",".join(row.name for group in INVARIANTS for row in group.rows
                                if row.scope == "feature")
        code, out = _run(tmp, "--feature", FEAT, "--only", feature_rows)
        violations = [line for line in out.splitlines() if line.lstrip().startswith("VIOLATION")]
        check(code == 0, "check-state --feature exits 0 with no working files", out)
        check(not violations, "no line starts VIOLATION", "\n".join(violations))


def case_list_shows_retired():
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, 0)
        code, out = _run(tmp, "--list")
        check(code == 0, "check-state --list exits 0", out)
        lines = out.splitlines()
        for number in RETIRED_NUMBERS:
            hit = [line for line in lines if line.split()[:1] == [number]]
            check(len(hit) == 1 and "retired" in hit[0].lower(),
                  f"--list shows {number} as retired", "\n".join(hit) or out)


def case_positive_control_negative_cycles():
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, -1)
        # INV-7's finding text names the feature, not the row, so --only attributes the line.
        code, out = _run(tmp, "--feature", FEAT, "--only", "INV-7")
        hit = [line for line in out.splitlines()
               if line.lstrip().startswith("VIOLATION") and FEAT in line
               and "nonnegative integer total" in line]
        check(code == 1 and bool(hit), "cycles_used -1 prints an INV-7 VIOLATION", out)
        code, out = _run(tmp, "--feature", FEAT)
        check(code == 1 and any(FEAT in line and "nonnegative integer total" in line
                                for line in out.splitlines()
                                if line.lstrip().startswith("VIOLATION")),
              "the full run reports the same INV-7 VIOLATION", out)


def main():
    case_no_working_files_is_clean()
    case_list_shows_retired()
    case_positive_control_negative_cycles()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
