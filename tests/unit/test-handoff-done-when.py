#!/usr/bin/env python3
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(BIN))
import handoff_done_when

failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition:
        failures.append(name)


def fixture():
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    feat = root / ".harness/harness/features/FEAT-90-fixture"
    notes = feat / "notes"
    notes.mkdir(parents=True)
    (feat / "plan.yaml").write_text("tasks:\n  - id: T-03\n    verify: python3 test.py\n")
    (feat / "BRIEF.md").write_text("# BRIEF\n\n- SC-04: observable\n\n## Approval\n")
    (notes / "review-fixture.md").write_text("Finding F-02 remains.\n")
    rel = ".harness/harness/features/FEAT-90-fixture/notes/handoff-build.md"
    return td, root, rel


def note(body):
    return "## Next\nnext\n\n## Trust\ntrust\n\n## Dead ends\nnone\n\n## Working set\nset\n\n## Done when\n" + body + "\n"


def problems(body, resolve=True):
    td, root, rel = fixture()
    try:
        return handoff_done_when.problems(rel, note(body), root, resolve)
    finally:
        td.cleanup()


td, root, rel = fixture()
try:
    missing = handoff_done_when.problems(rel, "## Next\nnext\n", root, True)
    check("missing section", len(missing) == 1 and "## Done when" in missing[0]
          and "templates/HANDOFF.md" in missing[0], repr(missing))
finally:
    td.cleanup()

valid = "Scope: build complete\nAuthority: plan-task:T-03.verify"
check("well formed", problems(valid) == [], repr(problems(valid)))

shape_cases = [
    ("zero scope", "Authority: plan-task:T-03.verify", "Scope", "0"),
    ("two scope", "Scope: one\nScope: two\nAuthority: plan-task:T-03.verify", "Scope", "2"),
    ("zero authority", "Scope: only", "Authority", "0"),
    ("five authority", "Scope: only\n" + "\n".join(["Authority: plan-task:T-03.verify"] * 5), "Authority", "5"),
    ("stray line", valid + "\nstray prose", "stray prose", None),
]
for name, body, first, second in shape_cases:
    got = problems(body)
    check(name, any(first in message and (second is None or second in message) for message in got), repr(got))

pointers = [
    ("plan", "plan-task:T-03.verify", "plan-task:T-99.verify"),
    ("brief", "brief-sc:SC-04", "brief-sc:SC-99"),
    ("finding", "finding:.harness/harness/features/FEAT-90-fixture/notes/review-fixture.md#F-02",
     "finding:.harness/harness/features/FEAT-90-fixture/notes/review-fixture.md#F-99"),
    ("approval", "approval:.harness/harness/features/FEAT-90-fixture/BRIEF.md#Approval",
     "approval:.harness/harness/features/FEAT-90-fixture/BRIEF.md#Missing"),
]
for name, good, bad in pointers:
    check(f"{name} resolves", problems(f"Scope: done\nAuthority: {good}") == [])
    got = problems(f"Scope: done\nAuthority: {bad}")
    check(f"{name} unresolved", len(got) == 1 and bad in got[0], repr(got))
    check(f"{name} unresolved ignored without resolution",
          problems(f"Scope: done\nAuthority: {bad}", False) == [])

for value in ("docs:whatever", "check-domain.sh:1523"):
    for resolve in (True, False):
        got = problems(f"Scope: done\nAuthority: {value}", resolve)
        check(f"unknown authority {value} resolve={resolve}",
              len(got) == 1 and all(prefix in got[0] for prefix in
                  ("plan-task:", "brief-sc:", "finding:", "approval:")), repr(got))

all_good = "Scope: done\n" + "\n".join(f"Authority: {good}" for _, good, _ in pointers)
check("four authorities accepted", problems(all_good) == [], repr(problems(all_good)))
one_bad = "Scope: done\n" + "\n".join(
    f"Authority: {bad if index == 2 else good}" for index, (_, good, bad) in enumerate(pointers))
got = problems(one_bad)
check("all authorities required", len(got) == 1 and pointers[2][2] in got[0], repr(got))

# resolve=False still enforces section, shape, and grammar.
td, root, rel = fixture()
try:
    got = handoff_done_when.problems(rel, "## Next\n", root, False)
    check("missing section without resolution", len(got) == 1 and "## Done when" in got[0], repr(got))
finally:
    td.cleanup()
for name, body, first, second in shape_cases:
    got = problems(body, False)
    check(f"{name} without resolution",
          any(first in message and (second is None or second in message) for message in got), repr(got))

# A grammar-only pass must not open any absent target.
with tempfile.TemporaryDirectory() as td_name:
    root = Path(td_name)
    rel = ".harness/harness/features/FEAT-90-fixture/notes/handoff-build.md"
    grammar_only = "Scope: done\n" + "\n".join(
        ["Authority: plan-task:T-03.verify", "Authority: brief-sc:SC-04",
         "Authority: finding:missing.md#F-02", "Authority: approval:missing.md#Approval"])
    got = handoff_done_when.problems(rel, note(grammar_only), root, False)
    check("resolve false opens no target", got == [], repr(got))

raise SystemExit(1 if failures else 0)
