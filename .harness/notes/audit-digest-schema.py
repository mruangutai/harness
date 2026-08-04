#!/usr/bin/env python3
"""Audit: which required DIGEST fields have NO truthful value when nothing happened?

For each persona, build the return it would make in a legitimate did-nothing state
(blocked / scoped-out / self-executed) and ask the real validator whether the
truthful encoding is accepted. A field is DEFECTIVE when the honest value is
rejected and the only accepted values are assertions that are false.
"""
import subprocess, sys, pathlib

V = ".claude/skills/harness/bin/validate-digest.py"
UNIV = "  open_questions: []\n  files_touched: []\n  expertise_update: []\n"


def check(persona, fields, verdict="BLOCKED"):
    body = f"VERDICT: {verdict}\nDIGEST:\n  headline: nothing was done, and here is why\n"
    body += "".join(f"  {k}: {v}\n" for k, v in fields.items())
    body += UNIV + "artifact: none\n"
    p = subprocess.run([sys.executable, V, persona], input=body,
                       capture_output=True, text=True)
    return p.returncode == 0, p.stdout.strip()


# (persona, scenario, honest fields, the field under suspicion, the lie that IS accepted)
CASES = [
    ("dev", "refuses an under-specified task; no tests ran",
     {"tests_added": 0, "suite": "none", "blocked_on": '"T-01 has a placeholder"'},
     "suite", {"tests_added": 0, "suite": "pass", "blocked_on": '"T-01 has a placeholder"'}),

    ("qa", "cannot run the suite at all",
     {"suite": "none", "failures": 0, "coverage_gaps": "[]", "matrix_ok": "none"},
     "suite/matrix_ok", {"suite": "pass", "failures": 0, "coverage_gaps": "[]",
                         "matrix_ok": "true"}),

    ("reviewer", "ui-reviewer self-scopes OUT of a non-UI diff",
     {"severity_max": "none", "findings": 0, "must_fix": "[]"},
     "severity_max", {"severity_max": "info", "findings": 0, "must_fix": "[]"}),

    ("visual-designer", "decides the feature needs no DESIGN.md",
     {"contract": "none", "mockups": "[]", "direction_choices": "[]"},
     "contract", {"contract": "written", "mockups": "[]", "direction_choices": "[]"}),

    ("dev-ops", "no suite applicable (has the n/a value already)",
     {"change_type": "config", "applied": "[]", "suite": "n/a"},
     "suite (CONTROL — expected OK)", None),

    ("lead", "self-executed a step, spawned no members (B-13)",
     {"team": "build", "steps_run": 1, "cycles_used": 0, "members": "[]",
      "must_fix": "[]", "branch": "none", "escalations": "[]", "sc_status": "[]"},
     "members vs steps_run", None),

    ("pm", "blocked before it could size anything",
     {"feasibility": "blocked", "surface": "none", "recommend": "halt",
      "risk": "none", "tasks": 0, "decisions": 0, "needs_approval": "false",
      "flags": "[]", "sc_status": "[]"},
     "surface/risk", {"feasibility": "blocked", "surface": "S", "recommend": "halt",
                      "risk": "low", "tasks": 0, "decisions": 0,
                      "needs_approval": "false", "flags": "[]", "sc_status": "[]"}),
]

print(f"{'persona':<17}{'honest?':<9}{'lie accepted?':<15}suspect field")
print("-" * 86)
defects = []
for persona, scenario, honest, suspect, lie in CASES:
    ok_honest, out = check(persona, honest)
    if lie is not None:
        ok_lie, _ = check(persona, lie)
        lie_s = "YES" if ok_lie else "no"
    else:
        ok_lie, lie_s = None, "—"
    flag = "" if ok_honest else "  <-- DEFECT"
    print(f"{persona:<17}{'OK' if ok_honest else 'REJECTED':<9}{lie_s:<15}{suspect}{flag}")
    if not ok_honest:
        first = [l for l in out.split("\n") if l.strip().startswith("-")]
        defects.append((persona, scenario, suspect, first[:3], ok_lie))

print("\n" + "=" * 86)
for persona, scenario, suspect, errs, ok_lie in defects:
    print(f"\n{persona}  —  {scenario}")
    print(f"  suspect: {suspect}")
    for e in errs:
        print(f"  {e.strip()}")
    if ok_lie:
        print("  ** the FALSE version of this return is accepted **")
print(f"\n{len(defects)} of {len(CASES)} personas cannot encode 'nothing happened' truthfully.")
