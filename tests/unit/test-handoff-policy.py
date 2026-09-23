#!/usr/bin/env python3
"""handoff_policy.exempt_reason — the one DEC-174 predicate INV-17 (check-state.py) and
`gh-sync ship` (BUG-1129) share. Every shape that is NOT a non-empty plan whose every task is
explicitly main-session-direct grants no exemption; the cases below are the ones a regression
would most plausibly open (an empty list is vacuously "all direct"; a mixed plan has SOME direct
tasks; an unreadable plan has no tasks to disagree)."""
from pathlib import Path
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(BIN))
import handoff_policy

failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition:
        failures.append(name)


def task(tid, mode):
    mode_line = f"    execution_mode: {mode}\n" if mode is not None else ""
    return (f"  - id: {tid}\n    title: t\n    change_type: logic\n{mode_line}"
            f"    files: [x.py]\n    verify: true\n    intent: i\n")


def reason_for(plan_text, mode=0o644):
    with tempfile.TemporaryDirectory() as td:
        feat = Path(td) / "FEAT-90"
        feat.mkdir()
        if plan_text is not None:
            p = feat / "plan.yaml"
            p.write_text(plan_text)
            os.chmod(p, mode)
        return handoff_policy.exempt_reason(str(feat))


# The one exempt shape, so the negatives below are discriminating and not vacuous.
why, detail = reason_for("schema: plan/1\ntasks:\n" + task("T-01", "main-session-direct")
                         + task("T-02", "main-session-direct"))
check("every task main-session-direct -> exempt, naming DEC-174",
      "main-session-direct" in why and "DEC-174" in why and detail == "", repr((why, detail)))

NOT_EXEMPT = [
    ("absent plan.yaml", None, ""),
    ("unparsable plan.yaml", "tasks: [\n  - id: T-01\n", "does not parse"),
    ("plan.yaml that is not a mapping", "- just\n- a list\n", "not a mapping"),
    # The three shapes artifact_accessors.load_plan itself refuses arrive as a parse failure;
    # the contract here is "no exemption", and the detail names the loader's reason.
    ("empty tasks list (vacuous truth is refused)", "schema: plan/1\ntasks: []\n",
     "does not parse"),
    ("tasks key that is not a list", "schema: plan/1\ntasks: nope\n", "does not parse"),
    ("a task that is not a mapping", "schema: plan/1\ntasks:\n  - T-01\n", "not a mapping"),
    ("a task with no execution_mode", "schema: plan/1\ntasks:\n" + task("T-01", None),
     "does not parse"),
    ("a team task", "schema: plan/1\ntasks:\n" + task("T-01", "team"), ""),
    ("a mixed plan (one direct, one team)",
     "schema: plan/1\ntasks:\n" + task("T-01", "main-session-direct") + task("T-02", "team"), ""),
]
for label, text, detail_needle in NOT_EXEMPT:
    why, detail = reason_for(text)
    check(f"{label} -> no exemption", why == "", repr((why, detail)))
    if detail_needle:
        check(f"{label} -> the detail says why it could not be evaluated",
              detail_needle in detail, repr(detail))
    else:
        check(f"{label} -> no detail (nothing was unreadable, it simply is not exempt)",
              detail == "", repr(detail))

# Unreadable (mode 000): a read error is a "does not parse" refusal, never an exemption.
if os.geteuid() != 0:
    why, detail = reason_for("schema: plan/1\ntasks:\n" + task("T-01", "main-session-direct"),
                             mode=0o000)
    check("unreadable plan.yaml -> no exemption, detail names the read failure",
          why == "" and "does not parse" in detail, repr((why, detail)))


# FEAT-64 (SC-03): "does not parse" is the loader's YamlParseError; an unrelated
# RuntimeError raised inside the loader escapes rather than becoming a parenthetical.
import artifact_accessors  # noqa: E402
_real = artifact_accessors.load_plan
def _boom(path):
    raise RuntimeError("unrelated defect")
artifact_accessors.load_plan = _boom
try:
    try:
        reason_for("schema: plan/1\ntasks:\n" + task("T-01", "main-session-direct"))
        escaped = False
    except RuntimeError:
        escaped = True
finally:
    artifact_accessors.load_plan = _real
check("FEAT-64: an unrelated RuntimeError in the plan loader escapes _plan_mapping", escaped)

print(f"{len(NOT_EXEMPT) * 2 + 3 - len(failures)} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
