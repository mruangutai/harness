#!/usr/bin/env python3
"""Unit floor for feature_schema.recovery_command_for and BUILD_ENTRY_ERA_EXEMPT (T-11,
BUG-1309, DEC-217's Over clause). Seven cases, each aimed at a state or observable that no
integration bed reaches (see tests/integration/test-check-state.py:4622-4699's fixture, which
always writes exactly one task with os.path.join'd paths — see this task's plan.yaml intent for
the case-by-case cross-check). Mutation-based discrimination proof for these cases lives outside
this file (throwaway scripts against a mutated copy, never the real feature_schema.py) and is
recorded in this task's receipt.

python3 stdlib only. gh-sync.py's own BIN-dir resolution convention
(tests/unit/test-handoff-done-when.py:7-10); reporting convention
(tests/unit/test-handoff-done-when.py:15-18).

    ./test-feature-schema-build-entry.py    -> exit 0 all pass, 1 otherwise
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
import feature_schema  # noqa: E402

failures = []


def check(name, ok, detail=""):
    print("PASS" if ok else "FAIL", name, detail if not ok else "")
    if not ok:
        failures.append(name)


def feat_dir(tmp, name, trailing_slash=False):
    d = os.path.join(tmp, ".harness", "harness", "features", name)
    os.makedirs(d, exist_ok=True)
    return d + "/" if trailing_slash else d


def write_plan(d, status, tasks):
    """A minimal plan.yaml recovery_command_for can read: `status:` plus `tasks:`, each
    task rendered as a JSON object (valid YAML flow mapping)."""
    lines = ["schema: plan/1", f"status: {status}"]
    if tasks:
        lines.append("tasks:")
        for t in tasks:
            lines.append(f"  - {json.dumps(t)}")
    else:
        lines.append("tasks: []")
    with open(os.path.join(d, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# BE-02: an era-set member with a trailing slash on feat_dir still returns recover-terminal.
# The plan underneath is a real "would return open" plan (building, no task done), so the era
# short-circuit is what is actually proven, not an absent-plan except leg (that would be BE-01's
# now-struck vacuous shape).
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "BUG-1030-stale-anchor-write-hazard", trailing_slash=True)
    write_plan(d, "building", [{"id": "T-01"}])
    got = feature_schema.recovery_command_for(d)
    check("BE-02 an era-set member with a trailing slash still returns recover-terminal",
          got == "recover-terminal", repr(got))

# BE-03: a non-era feature with no plan.yaml returns recover-terminal.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9002-fixture-no-plan")
    got = feature_schema.recovery_command_for(d)
    check("BE-03 a non-era feature with no plan.yaml returns recover-terminal",
          got == "recover-terminal", repr(got))

# BE-04: a non-era feature whose plan.yaml does not parse returns recover-terminal.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9003-fixture-bad-yaml")
    with open(os.path.join(d, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write("status: building\ntasks: [\n  - unterminated flow sequence\n")
    got = feature_schema.recovery_command_for(d)
    check("BE-04 a non-era feature whose plan.yaml does not parse returns recover-terminal",
          got == "recover-terminal", repr(got))

# BE-06: plan status done returns recover-terminal, isolated from the any()-task-done trigger
# by giving the one task a non-done status.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9004-fixture-non-era")
    write_plan(d, "done", [{"id": "T-01", "status": "building"}])
    got = feature_schema.recovery_command_for(d)
    check("BE-06 plan status done returns recover-terminal", got == "recover-terminal", repr(got))

# BE-08: a plan at status building with THREE tasks, none carrying a status of done, returns
# open; and the SAME three-task plan with only the LAST task carrying status done returns
# recover-terminal, so the any() scans every task rather than the first.
with tempfile.TemporaryDirectory() as tmp:
    d1 = feat_dir(tmp, "FEAT-9005-fixture-three-open")
    write_plan(d1, "building", [{"id": "T-01"}, {"id": "T-02"}, {"id": "T-03"}])
    leg1 = feature_schema.recovery_command_for(d1)
    d2 = feat_dir(tmp, "FEAT-9006-fixture-last-done")
    write_plan(d2, "building",
               [{"id": "T-01"}, {"id": "T-02"}, {"id": "T-03", "status": "done"}])
    leg2 = feature_schema.recovery_command_for(d2)
    check("BE-08 building with three tasks none done is open, and only-last-done is "
          "recover-terminal",
          leg1 == "open" and leg2 == "recover-terminal",
          f"leg1={leg1!r} leg2={leg2!r}")

# BE-09: plan status building with an empty tasks list returns open.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9007-fixture-empty-tasks")
    write_plan(d, "building", [])
    got = feature_schema.recovery_command_for(d)
    check("BE-09 plan status building with an empty tasks list returns open",
          got == "open", repr(got))

# BE-10: membership is exact, never a prefix and never case-insensitive.
check("BE-10 membership is exact, never a prefix and never case-insensitive",
      "FEAT-01" in feature_schema.BUILD_ENTRY_ERA_EXEMPT
      and "FEAT-01-suffix" not in feature_schema.BUILD_ENTRY_ERA_EXEMPT
      and "feat-01" not in feature_schema.BUILD_ENTRY_ERA_EXEMPT
      and "FEAT-90-e-green-thing" not in feature_schema.BUILD_ENTRY_ERA_EXEMPT,
      repr(sorted(x for x in feature_schema.BUILD_ENTRY_ERA_EXEMPT if x.startswith("FEAT-01"))))

sys.exit(1 if failures else 0)
