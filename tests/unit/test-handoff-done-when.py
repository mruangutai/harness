#!/usr/bin/env python3
from pathlib import Path
import os
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

for name, malformed_note in [
    ("nested heading cannot truncate validation",
     note("Scope: done\nAuthority: plan-task:T-03.verify\n"
          "### hidden\nstray prose\nAuthority: plan-task:T-99.verify")),
    ("duplicate heading cannot truncate validation",
     note("Scope: done\nAuthority: plan-task:T-03.verify\n"
          "## Done when\nScope: hidden\nAuthority: plan-task:T-99.verify")),
]:
    td, root, rel = fixture()
    try:
        got = handoff_done_when.problems(rel, malformed_note, root, True)
        check(name, bool(got), repr(got))
    finally:
        td.cleanup()

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

ordering_cases = [
    ("blank scope", "Scope:   \nAuthority: plan-task:T-03.verify", "non-empty"),
    ("scope after authority", "Authority: plan-task:T-03.verify\nScope: done", "before"),
]
for name, body, needle in ordering_cases:
    got = problems(body)
    check(name, any(needle in message for message in got), repr(got))

unsafe_pointers = [
    "finding:/tmp/review.md#F-02",
    "finding:../review.md#F-02",
    "finding:.harness/harness/features/FEAT-90-fixture/notes/\x00review.md#F-02",
    "approval:/tmp/review.md#Approval",
    "approval:../review.md#Approval",
    "approval:.harness/harness/features/FEAT-90-fixture/notes/\x01review.md#Approval",
]
for pointer in unsafe_pointers:
    for resolve in (True, False):
        got = problems(f"Scope: done\nAuthority: {pointer}", resolve)
        check(f"unsafe pointer rejected resolve={resolve} {pointer!r}",
              len(got) == 1 and "unsafe" in got[0].lower(), repr(got))

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

td, root, rel = fixture()
try:
    feat = root / ".harness/harness/features/FEAT-90-fixture"
    (feat / "bad-nospace.md").write_text("#Approval\n")
    (feat / "bad-seven.md").write_text("####### Approval\n")
    for name in ("bad-nospace.md", "bad-seven.md"):
        pointer = f"approval:.harness/harness/features/FEAT-90-fixture/{name}#Approval"
        got = handoff_done_when.problems(
            rel, note(f"Scope: done\nAuthority: {pointer}"), root, True)
        check(f"approval requires real ATX heading {name}", len(got) == 1, repr(got))
finally:
    td.cleanup()

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

# Resolution must stay inside the project root and read only regular files.
with tempfile.TemporaryDirectory() as td_name:
    root = Path(td_name)
    feat = root / ".harness/harness/features/FEAT-90-fixture"
    notes = feat / "notes"
    notes.mkdir(parents=True)
    outside = root.parent / f"{root.name}-outside.md"
    outside.write_text("F-02\n")
    link = notes / "escape.md"
    link.symlink_to(outside)
    fifo = notes / "special.md"
    os.mkfifo(fifo)
    rel = ".harness/harness/features/FEAT-90-fixture/notes/handoff-build.md"
    relative_link = link.relative_to(root).as_posix()
    relative_fifo = fifo.relative_to(root).as_posix()
    for name, pointer in [
        ("finding symlink escape", f"finding:{relative_link}#F-02"),
        ("finding special file", f"finding:{relative_fifo}#F-02"),
        ("approval symlink escape", f"approval:{relative_link}#Approval"),
        ("approval special file", f"approval:{relative_fifo}#Approval"),
    ]:
        got = handoff_done_when.problems(
            rel, note(f"Scope: done\nAuthority: {pointer}"), root, True)
        check(name, len(got) == 1 and "unsafe" in got[0].lower(), repr(got))
    outside.unlink()

# ---------------------------------------------------------------------------
# B-1: RESOLUTION IS NOT SATISFACTION (FEAT-54 c6 finding VL-F-01).
#
# The defect these cases defend against passed every earlier gate: a note citing an
# authority that was ALREADY satisfied resolved clean, so `problems` returned [] and a
# successor could read the section, find it green, and skip the work in `## Next`.
# Existence was the only question asked, which is why the F-11 closure rested on a
# hand-applied semantic test rather than on this module.


def satisfaction_fixture(task_status, approval_status):
    """A feature whose single task and single approval carry the given states."""
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    feat = root / ".harness/harness/features/FEAT-91-satisfaction"
    (feat / "notes").mkdir(parents=True)
    (feat / "plan.yaml").write_text(
        "tasks:\n  - id: T-03\n    verify: python3 test.py\n"
        f"    status: {task_status}\n")
    (feat / "BRIEF.md").write_text(
        f"# BRIEF\n\n- SC-04: observable\n\n## Approval\n\nstatus: {approval_status}\n")
    rel = ".harness/harness/features/FEAT-91-satisfaction/notes/handoff-build.md"
    return td, root, rel


APPROVAL_POINTER = ("approval:.harness/harness/features/FEAT-91-satisfaction/"
                    "BRIEF.md#Approval")

# Each row: name, task status, approval status, pointers, whether it must be refused.
for _name, _task, _appr, _pointers, _refuse in [
    ("done task alone binds nothing", "done", "pending",
     ["plan-task:T-03.verify"], True),
    ("abandoned task alone binds nothing", "abandoned", "pending",
     ["plan-task:T-03.verify"], True),
    ("approved approval alone binds nothing", "building", "approved",
     [APPROVAL_POINTER], True),
    ("every pointer satisfied binds nothing", "done", "approved",
     ["plan-task:T-03.verify", APPROVAL_POINTER], True),
    # AND semantics: one unsatisfied pointer keeps the whole section binding.
    ("open task still binds", "building", "approved",
     ["plan-task:T-03.verify"], False),
    ("pending approval still binds", "done", "pending",
     [APPROVAL_POINTER], False),
    ("satisfied plus open task still binds", "done", "pending",
     ["plan-task:T-03.verify", APPROVAL_POINTER], False),
    # Indeterminate is never satisfied: an SC is met by judgment, not by a field.
    ("criterion alone is indeterminate", "done", "approved",
     ["brief-sc:SC-04"], False),
    ("satisfied task plus criterion still binds", "done", "approved",
     ["plan-task:T-03.verify", "brief-sc:SC-04"], False),
]:
    _td, _root, _rel = satisfaction_fixture(_task, _appr)
    try:
        _body = "Scope: do the thing\n" + "\n".join(
            f"Authority: {_pointer}" for _pointer in _pointers)
        _got = handoff_done_when.problems(_rel, note(_body), _root, True)
        if _refuse:
            check(f"satisfaction: {_name}",
                  len(_got) == 1 and "binds nothing" in _got[0]
                  and "templates/HANDOFF.md" in _got[0], repr(_got))
        else:
            check(f"satisfaction: {_name}", _got == [], repr(_got))
    finally:
        _td.cleanup()

# A missing status field is INDETERMINATE, not satisfied — the pre-DEC-182 plans and any
# hand-written task carry no station, and refusing those would be a false positive.
_td, _root, _rel = satisfaction_fixture("done", "approved")
try:
    _feat = _root / ".harness/harness/features/FEAT-91-satisfaction"
    (_feat / "plan.yaml").write_text("tasks:\n  - id: T-03\n    verify: python3 test.py\n")
    _got = handoff_done_when.problems(
        _rel, note("Scope: do the thing\nAuthority: plan-task:T-03.verify"), _root, True)
    check("satisfaction: stationless task is indeterminate", _got == [], repr(_got))
finally:
    _td.cleanup()

# The check is WRITE-TIME ONLY, exactly like resolution: the persisted-corpus pass must
# never reopen targets, or every superseded note on disk turns the state gate red as its
# tasks land.
_td, _root, _rel = satisfaction_fixture("done", "approved")
try:
    _got = handoff_done_when.problems(
        _rel, note("Scope: do the thing\nAuthority: plan-task:T-03.verify"), _root, False)
    check("satisfaction: silent when resolve is false", _got == [], repr(_got))
finally:
    _td.cleanup()

# An unresolved pointer must report ITS OWN error and nothing else — stacking a
# "binds nothing" line on top would bury the line the author has to fix.
_td, _root, _rel = satisfaction_fixture("done", "approved")
try:
    _got = handoff_done_when.problems(
        _rel, note("Scope: do the thing\nAuthority: plan-task:T-99.verify"), _root, True)
    check("satisfaction: unresolved wins over vacuity",
          len(_got) == 1 and "unresolved" in _got[0] and "binds nothing" not in _got[0],
          repr(_got))
finally:
    _td.cleanup()

raise SystemExit(1 if failures else 0)
