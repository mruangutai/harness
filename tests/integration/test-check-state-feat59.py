#!/usr/bin/env python3
"""check-state.py INV-38..41: the FEAT-59 proportional-flow invariants.

INV-38 brief-perspectives (SC-10): a by-perspective BRIEF has every perspective discharged by
a tagged SC and every SC tagged with a declared perspective; the old shape is untouched.
INV-39 cycles-budget (SC-15): cycles_used <= max_total_cycles, and a raise above the
harness.json default is a recorded budget_decisions entry (DEC-157).
INV-40 judgement-ledger (SC-21): mission, re-gate and succession each leave a judgements[]
entry; a record that predates the ledger is NOTED, never failed.
INV-41 sc-repo-wide (SC-16): an SC that invokes check-state.py / check-domain.py with no
feature-scoped argument is refused.
INV-43 succession-seam (BUG-1723 SC-03): the succession judgement for a handoff at seq-N is
recorded no later than run N+1 started; one recorded AFTER that run is a retrospective
correction, which means one context crossed the seam DEC-159 draws; an unreadable timestamp
is CANNOT VERIFY, never a silent pass.

Every case is a fixture tree under tmp; nothing reads the live corpus. Each rule carries a
positive (fires) and a negative (silent) case, filtered on its own INV tag so a sibling
invariant's noise (INV-34 on a plan-less directory, INV-17 on a fixture note) cannot decide
a case.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import io
import json
import os
import sys
import tempfile
from check_state_support import run

FEAT = "FEAT-TEST"

HARNESS_JSON = ('{\n  "github": {"sync": false, "repo": null},\n  "seam_era_start": null,\n'
                '  "budgets": {"max_total_cycles": 10, "max_total_runs": 20}\n}\n')

# The new shape (C5): the heading, perspectives as `**name**` lines under it, SCs tagged
# `(name)`. No `## Requirements`, no REQ-NN, no `## Goal` — the template drops them (SC-10).
BRIEF_NEW = """# BRIEF — FEAT-TEST

## Problem

A fixture.

## Done when — by perspective

**operator** — I trust the record.

**code maintainer** — One statement of done.

## Success criteria

- SC-01 (operator): the ledger exists and reads back.
  verify: automated  evidence: python
- SC-02 (code maintainer): the template carries the block.
  verify: inspection

## Approval

status: approved
date: 2026-09-11
"""

# The old shape: `## Requirements`, REQ-NN, untagged SCs. Never graded by INV-38/41.
BRIEF_OLD = """# BRIEF — FEAT-TEST

## Goal

A fixture.

## Requirements

- REQ-01: something holds.

## Success criteria

- SC-01: `python3 .claude/skills/harness/bin/check-state.py` exits 0.

## Approval

status: approved
date: 2026-09-11
"""

HANDOFF_SEQ = ("# Handoff — FEAT-TEST, build → review — written at abc1234, seq-{n}\n\n"
               "## Next\nbody\n## Trust\nbody\n## Dead ends\nbody\n## Working set\nbody\n"
               "## Done when\nPointer: brief-sc:SC-01\n")


def _fixture(tmp, feature, brief=None, notes=None, harness_json=HARNESS_JSON, station=None):
    """One feature at .harness/harness/features/FEAT-TEST with the given feature.json
    mapping, an optional BRIEF.md text, optional notes/{name: text}, and — when `station` is
    given — a minimal plan.yaml carrying that top-level status."""
    h = os.path.join(tmp, ".harness")
    fdir = os.path.join(h, "harness", "features", FEAT)
    os.makedirs(fdir, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(harness_json)
    with open(os.path.join(fdir, "feature.json"), "w") as f:
        f.write(json.dumps(feature, indent=1) + "\n")
    if brief is not None:
        with open(os.path.join(fdir, "BRIEF.md"), "w") as f:
            f.write(brief)
    for name, text in (notes or {}).items():
        os.makedirs(os.path.join(fdir, "notes"), exist_ok=True)
        with open(os.path.join(fdir, "notes", name), "w") as f:
            f.write(text)
    if station is not None:
        with open(os.path.join(fdir, "plan.yaml"), "w") as f:
            f.write(f"schema: plan/1\nfeature: {FEAT}\napproval:\n  status: approved\n"
                    f"status: {station}\nstation_only: true\ntasks: []\n")
    return fdir


def _lines(out, tag):
    return [l for l in out.splitlines() if tag in l]


def _violations(out, tag):
    return [l for l in _lines(out, tag) if l.startswith("  VIOLATION")]


def _notes(out, tag):
    return [l for l in _lines(out, tag) if l.startswith("  note")]


def _check(feature, brief=None, notes=None, harness_json=HARNESS_JSON, station=None):
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, feature, brief, notes, harness_json, station)
        return run(tmp)


def _run(rid, verdict="PASS", squad="eng"):
    return {"id": rid, "squad": squad, "verdict": verdict}


def _j(kind, decision=None):
    return {"at": "2026-09-11T10:00:00Z", "by": "harness-orchestrator", "kind": kind,
            "decision": kind if decision is None else decision, "reason": "fixture"}


# THE MINIMAL IN-ERA RECORD: `judgements: []` marks the feature as written under the FEAT-59
# contract, so INV-39/40 grade it rather than noting it as legacy.
def _in_era(**extra):
    doc = {"feature_id": FEAT, "cycles_used": 0, "max_total_cycles": 10,
           "review_sha": "abc1234", "judgements": [], "runs": []}
    doc.update(extra)
    return doc


def _legacy(**extra):
    doc = {"feature_id": FEAT, "cycles_used": 0, "max_total_cycles": 10,
           "review_sha": "abc1234", "runs": []}
    doc.update(extra)
    return doc


# ----------------------------------------------------------------------------- INV-38 ---
def case_inv38():
    """SC-10: perspectives and SC tags must close over each other, in a by-perspective BRIEF
    only."""
    results = []

    _, out = _check(_in_era(), BRIEF_NEW)
    results.append(("(38.a) a well-formed by-perspective BRIEF is silent",
                    not _lines(out, "INV-38"), out[:400]))
    results.append(("(38.a2) a by-perspective BRIEF is NOT graded for `## Requirements`/REQ-NN",
                    not [l for l in out.splitlines()
                         if l.startswith("  VIOLATION") and ("Requirements" in l or "REQ-" in l)],
                    out[:400]))

    orphan = BRIEF_NEW.replace("**code maintainer** — One statement of done.\n",
                               "**code maintainer** — One statement of done.\n\n"
                               "**orchestrator** — My budget is one I can exhaust.\n")
    _, out = _check(_in_era(), orphan)
    v = _violations(out, "INV-38")
    results.append(("(38.b) a perspective no SC discharges is a VIOLATION naming it",
                    len(v) == 1 and "orchestrator" in v[0] and FEAT in v[0], out[:400]))

    _, out = _check(_in_era(), BRIEF_NEW.replace("- SC-02 (code maintainer):",
                                                  "- SC-02 (tester):"))
    v = _violations(out, "INV-38")
    results.append(("(38.c) an SC tagged with an undeclared perspective names the SC and the tag",
                    any("SC-02" in l and "tester" in l for l in v)
                    and any("code maintainer" in l for l in v),
                    out[:400]))

    _, out = _check(_in_era(), BRIEF_NEW.replace("- SC-02 (code maintainer):", "- SC-02:"))
    v = _violations(out, "INV-38")
    results.append(("(38.d) an SC with no perspective tag is a VIOLATION naming the SC",
                    any("SC-02" in l and "no perspective" in l for l in v), out[:400]))

    _, out = _check(_legacy(), BRIEF_OLD)
    results.append(("(38.e) an old-shape BRIEF (REQ-NN, untagged SCs) is not graded",
                    not _lines(out, "INV-38"), out[:400]))

    qualified = BRIEF_NEW.replace("**code maintainer** — One statement of done.",
                                  "**code maintainer** — One statement of done.\n\n"
                                  "**reader (reviewer / qa / panel)** — I see the tree once.") \
                         .replace("  verify: inspection\n",
                                  "  verify: inspection\n"
                                  "- SC-03 (reader): findings carry a kind.\n  verify: unit\n")
    _, out = _check(_in_era(), qualified)
    results.append(("(38.f) a perspective with a parenthetical qualifier matches its bare tag",
                    not _lines(out, "INV-38"), out[:400]))

    empty = BRIEF_NEW.replace("**operator** — I trust the record.\n\n"
                              "**code maintainer** — One statement of done.\n", "")
    _, out = _check(_in_era(), empty)
    v = _violations(out, "INV-38")
    results.append(("(38.g) the heading with no perspective under it is a VIOLATION",
                    bool(v) and any("no perspective" in l or "declares no" in l for l in v),
                    out[:400]))
    return results


# ----------------------------------------------------------------------------- INV-39 ---

def case_inv39():
    """SC-15 / DEC-157: the cycle budget is enforced, and a raise is a recorded decision."""
    results = []

    _, out = _check(_in_era(cycles_used=11, max_total_cycles=10))
    v = _violations(out, "INV-39")
    results.append(("(39.a) cycles_used 11 > max_total_cycles 10 is a VIOLATION naming both",
                    len(v) == 1 and "cycles_used=11" in v[0] and "max_total_cycles=10" in v[0]
                    and FEAT in v[0], out[:400]))

    _, out = _check(_in_era(cycles_used=10, max_total_cycles=10))
    results.append(("(39.b) cycles_used == max_total_cycles is silent — the boundary is >",
                    not _lines(out, "INV-39"), out[:400]))

    _, out = _check(_in_era(max_total_cycles=14, budget_decisions=[]))
    v = _violations(out, "INV-39")
    results.append(("(39.c) a raise above the harness.json default with no decision names DEC-157",
                    len(v) == 1 and "DEC-157" in v[0] and "14" in v[0], out[:400]))

    dec = {"at": "2026-09-11T10:00:00Z", "max_total_cycles": 14,
           "decision": ".harness/harness/features/FEAT-TEST/notes/answers.md#raise"}
    _, out = _check(_in_era(max_total_cycles=14, budget_decisions=[dec]))
    results.append(("(39.d) the same raise with a matching budget_decisions entry is silent",
                    not _lines(out, "INV-39"), out[:400]))

    stale = dict(dec, max_total_cycles=12)
    _, out = _check(_in_era(max_total_cycles=14, budget_decisions=[stale]))
    results.append(("(39.e) a decision recording a DIFFERENT value does not cover the current one",
                    len(_violations(out, "INV-39")) == 1, out[:400]))

    _, out = _check(_in_era(max_total_cycles=10))
    results.append(("(39.f) max_total_cycles equal to the default needs no decision",
                    not _lines(out, "INV-39"), out[:400]))

    code, out = _check(_legacy(cycles_used=18, max_total_cycles=17), BRIEF_OLD)
    results.append(("(39.g) a record predating the FEAT-59 keys is NOTED, not failed",
                    not _violations(out, "INV-39") and len(_notes(out, "INV-39")) == 1
                    and "not graded" in _notes(out, "INV-39")[0], out[:400]))

    _, out = _check(_legacy(cycles_used=18, max_total_cycles=17), BRIEF_NEW)
    results.append(("(39.h) a by-perspective BRIEF puts a key-less record in era — graded",
                    len(_violations(out, "INV-39")) >= 1, out[:400]))

    # The schema lets a feature OMIT max_total_cycles to inherit the harness.json default;
    # the bound must then be the default, not nothing (review F9).
    inherited = _in_era(cycles_used=12)
    del inherited["max_total_cycles"]
    _, out = _check(inherited)
    v = _violations(out, "INV-39")
    results.append(("(39.i) cycles_used 12 with max_total_cycles inherited from the default 10 is a VIOLATION",
                    len(v) == 1 and "cycles_used=12" in v[0] and "10" in v[0], out[:400]))

    inherited = _in_era(cycles_used=10)
    del inherited["max_total_cycles"]
    _, out = _check(inherited)
    results.append(("(39.j) cycles_used at the inherited default is silent",
                    not _lines(out, "INV-39"), out[:400]))
    return results


# ----------------------------------------------------------------------------- INV-40 ---

def case_inv40():
    """SC-21: every autonomous judgement leaves a ledger entry; the three checks are
    independent; a record predating the ledger is noted."""
    results = []

    _, out = _check(_in_era(mission="patch"))
    v = _violations(out, "INV-40")
    results.append(("(40.a) mission with no judgement of kind mission is a VIOLATION",
                    len(v) == 1 and "mission" in v[0] and FEAT in v[0], out[:400]))

    _, out = _check(_in_era(mission="patch", judgements=[_j("mission", "patch")]))
    results.append(("(40.b) mission with its matching judgement is silent",
                    not _lines(out, "INV-40"), out[:400]))

    # SC-21 is about a mission CHANGE: a second set-mission with no new judgement leaves the
    # last mission entry disagreeing with the top-level key (review F2).
    _, out = _check(_in_era(mission="plan", judgements=[_j("mission", "patch")]))
    v = _violations(out, "INV-40")
    results.append(("(40.b2) mission plan whose LAST mission judgement decided patch is a VIOLATION naming both",
                    len(v) == 1 and "'plan'" in v[0] and "'patch'" in v[0], out[:400]))

    _, out = _check(_in_era(mission="patch", judgements=[_j("mission", "plan"),
                                                          _j("regate"), _j("mission", "patch")]))
    results.append(("(40.b3) two mission judgements, the last matching the current mission, is silent",
                    not _lines(out, "INV-40"), out[:400]))

    _, out = _check(_in_era(runs=[_run("r1", "FAIL"), _run("r2")]))
    v = _violations(out, "INV-40")
    results.append(("(40.c) a FAIL run followed by another run with no regate names the run",
                    len(v) == 1 and "r1" in v[0] and "regate" in v[0], out[:400]))

    _, out = _check(_in_era(runs=[_run("r1", "FAIL"), _run("r2")], judgements=[_j("regate")]))
    results.append(("(40.d) the same with a regate judgement is silent",
                    not _lines(out, "INV-40"), out[:400]))

    _, out = _check(_in_era(runs=[_run("r1"), _run("r2", "FAIL")]))
    results.append(("(40.e) a FAIL run that nothing follows needs no regate yet",
                    not _lines(out, "INV-40"), out[:400]))

    _, out = _check(_in_era(runs=[_run("r1", "FAIL"), _run("r2", "FAIL"), _run("r3")],
                            judgements=[_j("regate")]))
    v = _violations(out, "INV-40")
    results.append(("(40.f) two re-gates against one regate judgement names the uncovered run",
                    len(v) == 1 and "r2" in v[0] and "r1" not in v[0], out[:400]))

    _, out = _check(_in_era(runs=[_run("r1"), _run("r2")]),
                    notes={"handoff-build.md": HANDOFF_SEQ.format(n=1)})
    v = _violations(out, "INV-40")
    results.append(("(40.g) a handoff at seq-1 with a run after it and no succession names the note",
                    len(v) == 1 and "handoff-build.md" in v[0] and "succession" in v[0],
                    out[:400]))

    _, out = _check(_in_era(runs=[_run("r1"), _run("r2")], judgements=[_j("succession")]),
                    notes={"handoff-build.md": HANDOFF_SEQ.format(n=1)})
    results.append(("(40.h) the same with a succession judgement is silent",
                    not _lines(out, "INV-40"), out[:400]))

    _, out = _check(_in_era(runs=[_run("r1"), _run("r2")]),
                    notes={"handoff-build.md": HANDOFF_SEQ.format(n=2)})
    results.append(("(40.i) a handoff at seq-2 with exactly two runs has no successor run yet",
                    not _lines(out, "INV-40"), out[:400]))

    _, out = _check(_in_era(runs=[_run("r1"), _run("r2")]),
                    notes={"handoff-build.md": HANDOFF_SEQ.replace(", seq-{n}", "")})
    v = _violations(out, "INV-40")
    results.append(("(40.j) an in-era handoff with no seq-N on line one is refused, not skipped",
                    len(v) == 1 and "seq-N" in v[0], out[:400]))

    _, out = _check(_in_era(mission="plan", runs=[_run("r1", "FAIL"), _run("r2")]),
                    notes={"handoff-build.md": HANDOFF_SEQ.format(n=1)})
    v = _violations(out, "INV-40")
    results.append(("(40.k) the three checks are independent — all three fire on one record",
                    len(v) == 3 and any("mission" in l for l in v)
                    and any("regate" in l for l in v) and any("succession" in l for l in v),
                    out[:600]))

    _, out = _check(_legacy(runs=[_run("r1", "FAIL"), _run("r2")]), BRIEF_OLD,
                    notes={"handoff-build.md": HANDOFF_SEQ.format(n=1)})
    results.append(("(40.l) a record predating the ledger is NOTED once, never failed",
                    not _violations(out, "INV-40") and len(_notes(out, "INV-40")) == 1
                    and "not graded" in _notes(out, "INV-40")[0], out[:400]))

    _, out = _check(_legacy(runs=[_run("r1"), _run("r2")]), BRIEF_OLD)
    results.append(("(40.m) a legacy record with nothing to grade emits no note at all",
                    not _lines(out, "INV-40"), out[:400]))
    return results


# ------------------------------------------------------------------ INV-40 (d), BUG-1716 ---

_SIGNED_PLAN = ("schema: plan/1\nfeature: FEAT-TEST\n"
                "approval:\n  status: approved\n  approved_by: X\n  date: 2026-09-15\n"
                "status: building\n"
                "tasks:\n"
                "  - id: T-01\n    title: a\n    traces: [SC-01]\n    change_type: logic\n"
                "    execution_mode: main-session-direct\n    depends_on: []\n    status: building\n"
                "    intent: one\n    files: [a.py]\n    verify: python3 a.py\n"
                "  - id: T-02\n    title: b\n    traces: [SC-01]\n    change_type: logic\n"
                "    execution_mode: main-session-direct\n    depends_on: []\n    status: ready\n"
                "    intent: two\n    files: [b.py#f]\n    verify: python3 b.py\n")
_PLAN_MERGE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           ".claude", "skills", "harness", "bin", "plan-merge.py")


def _amend_j(decision, **extra):
    entry = {"at": "2026-09-15T12:00:00+00:00", "by": "harness-orchestrator", "kind": "amendment",
             "decision": decision, "reason": "fixture"}
    entry.update(extra)
    return entry


def _sign_through_plan_merge(plan):
    """Sign `plan` THROUGH plan-merge.py sign-approval so the hashes are the real ones."""
    import subprocess
    env = dict(os.environ)
    env.pop("HARNESS_AGENT_TYPE", None)
    r = subprocess.run([sys.executable, _PLAN_MERGE, "sign-approval", "--file", plan,
                        "--by", "X", "--date", "2026-09-15"],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr


def _rewrite(path, transform):
    with open(path) as f:
        text = f.read()
    with open(path, "w") as f:
        f.write(transform(text))


def _signed(plan_text=_SIGNED_PLAN, mutate=None, judgements=(), sign=True):
    """A feature signed through sign-approval, then `mutate(plan_text) -> plan_text` applied
    and `judgements` appended; returns check-state's (code, out)."""
    with tempfile.TemporaryDirectory() as tmp:
        fdir = _fixture(tmp, _in_era(), BRIEF_NEW)
        plan = os.path.join(fdir, "plan.yaml")
        with open(plan, "w") as f:
            f.write(plan_text.replace("status: approved", "status: pending") if sign else plan_text)
        if sign:
            _sign_through_plan_merge(plan)
        if mutate is not None:
            _rewrite(plan, mutate)
        _rewrite(os.path.join(fdir, "feature.json"),
                 lambda text: json.dumps(dict(json.load(io.StringIO(text)),
                                              judgements=list(judgements)), indent=1) + "\n")
        return run(tmp)


def _change_intent(t):
    return t.replace("intent: one", "intent: one, revised")


def _inv40_after(mutate=None, judgements=(), sign=True):
    """INV-40 violation lines after a signed fixture is mutated, plus the raw output."""
    _, out = _signed(mutate=mutate, judgements=judgements, sign=sign)
    return _violations(out, "INV-40"), out


def _one_naming(v, task):
    return len(v) == 1 and task in v[0]


def _tasks_named(v):
    return {tid for tid in ("T-01", "T-02") if any(tid in x for x in v)}


def case_inv40_signed_text_detects_unledgered_edits():
    """BUG-1716 T-05: an edit to a signed task's intent with no amendment judgement naming
    that task is ONE INV-40 violation naming the task and the remedy; a fresh plan is silent."""
    _, out = _signed()
    fresh = ("(40d.a) a freshly signed plan is silent — the hashes agree with sign-approval",
             not _lines(out, "INV-40") and "plan.yaml does not load" not in out, out[:400])
    v, out = _inv40_after(_change_intent)
    intent = ("(40d.b) an unledgered intent change is ONE violation naming the task and the remedy",
              _one_naming(v, "T-01") and "record-amendments" in v[0] and "T-02" not in v[0], out[:500])
    return [fresh, intent]


def case_inv40_signed_text_grades_every_signed_field():
    """files and verify changes are caught on the task they belong to; two independently
    changed tasks are two violations."""
    v, out = _inv40_after(lambda t: t.replace("files: [a.py]", "files: [a.py, c.py]"))
    files = ("(40d.g) a files change is caught", len(v) == 1, out[:400])
    v, out = _inv40_after(lambda t: t.replace("verify: python3 b.py", "verify: python3 b.py -v"))
    verify = ("(40d.h) a verify change is caught, on the task it belongs to", _one_naming(v, "T-02"), out[:400])
    v, out = _inv40_after(lambda t: _change_intent(t).replace("intent: two", "intent: two, revised"))
    both = ("(40d.i) two independently changed tasks are two violations",
            len(v) == 2 and _tasks_named(v) == {"T-01", "T-02"}, out[:500])
    return [files, verify, both]


def case_inv40_signed_text_amendment_coverage():
    """Only an `amendment` judgement whose decision names THAT task covers the edit —
    overruled or not; another task's, or another kind's, does not."""
    v, out = _inv40_after(_change_intent, [_amend_j("T-01.intent")])
    matching = ("(40d.c) the matching amendment judgement silences it", not v, out[:400])
    v, out = _inv40_after(_change_intent, [_amend_j("T-01.intent", overruled=True)])
    overruled = ("(40d.d) an OVERRULED matching amendment still covers — the ledger is the record",
                 not v, out[:400])
    v, out = _inv40_after(_change_intent, [_amend_j("T-02.intent")])
    other_task = ("(40d.e) an amendment for ANOTHER task does not cover", _one_naming(v, "T-01"), out[:400])
    v, out = _inv40_after(_change_intent, [dict(_amend_j("T-01.intent"), kind="regate")])
    other_kind = ("(40d.f) another judgement kind naming the task does not cover",
                  _one_naming(v, "T-01"), out[:400])
    return [matching, overruled, other_task, other_kind]


def case_inv40_signed_text_scope():
    """Presentation-only rewrites hash the same; plans without hashes or with pending approval
    are not graded; the text trigger reports beside the other INV-40 triggers."""
    v, out = _inv40_after(lambda t: t.replace("intent: one\n", "intent: 'one'\n")
                          .replace("files: [a.py]", "files:\n      - a.py"))
    reflow = ("(40d.j) a presentation-only rewrite (quoting, list form) hashes the same — silent",
              not v, out[:400])
    v, out = _inv40_after(_change_intent, sign=False)
    unsigned = ("(40d.k) a plan with no signed_task_hashes (signed before BUG-1716) is not graded",
                not v, out[:400])
    v, out = _inv40_after(lambda t: _change_intent(t).replace("status: approved", "status: pending"))
    pending = ("(40d.l) a pending approval is not graded by this trigger", not v, out[:400])
    v, out = _inv40_after(_change_intent)
    beside = ("(40d.m) the text trigger reports beside, not instead of, the other triggers",
              len(v) == 1, out[:400])
    return [reflow, unsigned, pending, beside]


def case_inv40_signed_text():
    return (case_inv40_signed_text_detects_unledgered_edits()
            + case_inv40_signed_text_grades_every_signed_field()
            + case_inv40_signed_text_amendment_coverage()
            + case_inv40_signed_text_scope())




# ----------------------------------------------------------------------------- INV-43 ---

def _timed(rid, started, verdict="PASS"):
    return {"id": rid, "squad": "eng", "verdict": verdict, "started_at": started,
            "ended_at": started}


def _succ_at(at):
    return {"at": at, "by": "harness-orchestrator", "kind": "succession",
            "decision": "continue", "reason": "fixture"}


# BUG-1723 SC-03 / D-02: a succession judgement whose `at` postdates the first run after its
# handoff is a retrospective seam correction — the trace #1713 measured twice on
# BUG-285-canonical-reader. INV-40 already demands the judgement EXIST; INV-43 grades WHEN.
_SEQ1 = {"handoff-build.md": HANDOFF_SEQ.format(n=1)}
_RUNS43 = [_timed("r1", "2026-09-11T10:00:00+00:00"), _timed("r2", "2026-09-11T12:00:00+00:00")]


def _seam(succession_at, runs=_RUNS43, notes=_SEQ1, **extra):
    """One INV-43 fixture: an in-era record with `runs`, one succession at `succession_at`."""
    judgements = [] if succession_at is None else [_succ_at(succession_at)]
    return _check(_in_era(runs=runs, judgements=judgements), notes=notes, **extra)


def case_inv43_chronology():
    """Later than the successor's first run fires; earlier or equal is silent."""
    results = []
    _, out = _seam("2026-09-11T13:00:00+00:00")
    v = _violations(out, "INV-43")
    results.append(("(43.a) succession recorded AFTER run 2 started is a VIOLATION naming both",
                    len(v) == 1 and "handoff-build.md" in v[0] and "r2" in v[0]
                    and "retrospective" in v[0], out[:500]))
    _, out = _seam("2026-09-11T11:00:00+00:00")
    results.append(("(43.b) succession recorded before run 2 started is silent",
                    not _lines(out, "INV-43"), out[:400]))
    _, out = _seam("2026-09-11T12:00:00+00:00")
    results.append(("(43.c) succession at exactly run 2's start is silent (no later than)",
                    not _lines(out, "INV-43"), out[:400]))
    return results


def case_inv43_matching():
    """Matching is INV-40's own: the k-th handoff by seq takes the k-th succession by ledger
    order, so only the retrospective one is named."""
    three = _RUNS43 + [_timed("r3", "2026-09-11T15:00:00+00:00")]
    _, out = _check(_in_era(runs=three, judgements=[_succ_at("2026-09-11T11:00:00+00:00"),
                                                     _succ_at("2026-09-11T16:00:00+00:00")]),
                    notes={"handoff-build.md": HANDOFF_SEQ.format(n=1),
                           "handoff-validate.md": HANDOFF_SEQ.format(n=2)})
    v = _violations(out, "INV-43")
    return [("(43.h) two handoffs match two successions in order; only the second is retrospective",
             len(v) == 1 and "handoff-validate.md" in v[0] and "r3" in v[0], out[:500])]


def case_inv43_unreadable():
    """A present-but-unreadable timestamp is CANNOT VERIFY naming the field, never silence."""
    results = []
    _, out = _seam("not-a-time")
    v = _violations(out, "INV-43")
    results.append(("(43.d) an unparseable succession `at` is CANNOT VERIFY naming the field",
                    len(v) == 1 and "CANNOT VERIFY" in v[0] and "at" in v[0], out[:500]))
    _, out = _seam("2026-09-11T11:00:00+00:00",
                   runs=[_timed("r1", "2026-09-11T10:00:00+00:00"), _run("r2")])
    v = _violations(out, "INV-43")
    results.append(("(43.e) a successor run with no started_at is CANNOT VERIFY naming started_at",
                    len(v) == 1 and "CANNOT VERIFY" in v[0] and "started_at" in v[0]
                    and "r2" in v[0], out[:500]))
    return results


def case_inv43_scope():
    """What INV-43 leaves alone: a missing succession (INV-40's), no successor run yet, a
    legacy record. What it does NOT leave alone: a terminal station — a retrospective
    succession is graded the same at done as at review (SC-03/D-02; validate c0 struck the
    terminal downgrade)."""
    results = []
    _, out = _seam(None)
    results.append(("(43.f) a MISSING succession is INV-40's finding, not INV-43's",
                    not _lines(out, "INV-43") and _violations(out, "INV-40"), out[:400]))
    _, out = _seam(None, runs=_RUNS43[:1])
    results.append(("(43.g) a handoff with no successor run yet has nothing to grade",
                    not _lines(out, "INV-43"), out[:400]))
    _, out = _check(_legacy(runs=_RUNS43, judgements=None), BRIEF_OLD, notes=_SEQ1)
    results.append(("(43.i) a legacy record is never graded by INV-43",
                    not _violations(out, "INV-43"), out[:400]))
    for station in ("done", "review"):
        _, out = _seam("2026-09-11T13:00:00+00:00", station=station)
        v = _violations(out, "INV-43")
        results.append((f"(43.j) at station {station} the retrospective succession is a VIOLATION",
                        len(v) == 1 and "retrospective" in v[0] and not _notes(out, "INV-43"),
                        out[:500]))
    return results


def _seam_era_json(value):
    return HARNESS_JSON.replace('"seam_era_start": null', '"seam_era_start": ' + value)


_LATE43 = "2026-09-11T13:00:00+00:00"


def _seam_era(era, **extra):
    """INV-43 (violations, notes) for a retrospective succession under `seam_era_start: era`."""
    _, out = _seam(_LATE43, harness_json=_seam_era_json(era), **extra)
    return _violations(out, "INV-43"), _notes(out, "INV-43"), out


def case_inv43_era_boundary():
    """The boundary is by DATE, never by station (BUG-1071's rule for INV-32): a retrospective
    succession recorded before `seam_era_start` is a note that says what it would fail; on or
    after it is a violation; at a terminal station the same date rule applies."""
    v, n, out = _seam_era('"2026-09-12"')
    before = ("(43.k) before seam_era_start the retrospective succession is a NOTE naming would-fail",
              not v and len(n) == 1 and "would fail" in n[0] and "retrospective" in n[0], out[:600])
    v, n, out = _seam_era('"2026-09-11"')
    on = ("(43.l) on the seam_era_start date it is graded — a VIOLATION", len(v) == 1 and not n, out[:500])
    v, n, out = _seam_era('"2026-09-12"', station="done")
    terminal = ("(43.m) the boundary is by date at a terminal station too", not v and len(n) == 1, out[:500])
    return [before, on, terminal]


def case_inv43_era_config():
    """A config without the key names the key and the upgrade; an unreadable value exempts
    nothing and is named."""
    _, out = _seam(_LATE43, harness_json=HARNESS_JSON.replace('  "seam_era_start": null,\n', ""))
    v = [x for x in _violations(out, "INV-43") if "seam_era_start" in x]
    missing = ("(43.n) a config without seam_era_start is a VIOLATION naming the key and the upgrade",
               len(v) == 1 and "upgrade-config.py" in v[0], out[:600])
    v, _, out = _seam_era('"yesterday"')
    unreadable = ("(43.o) an unreadable seam_era_start exempts nothing and is named",
                  len(v) == 2 and any("yesterday" in x for x in v), out[:600])
    return [missing, unreadable]


# ----------------------------------------------------------------------------- INV-41 ---

def _brief_with_sc02(text):
    return BRIEF_NEW.replace("- SC-02 (code maintainer): the template carries the block.",
                             "- SC-02 (code maintainer): " + text)


def case_inv41():
    """SC-16: repository-wide state is a merge-time check, not a feature criterion."""
    results = []
    MSG = "repository-wide state is a merge-time check, not a feature criterion (SC-16)"

    _, out = _check(_in_era(), _brief_with_sc02(
        "`python3 .claude/skills/harness/bin/check-state.py` exits 0."))
    v = _violations(out, "INV-41")
    results.append(("(41.a) an unscoped check-state.py invocation is a VIOLATION naming the SC",
                    len(v) == 1 and "SC-02" in v[0] and MSG in v[0], out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`python3 .claude/skills/harness/bin/check-state.py --feature FEAT-TEST` exits 0."))
    results.append(("(41.b) `--feature` scopes it — silent",
                    not _lines(out, "INV-41"), out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`python3 .claude/skills/harness/bin/check-state.py` reports no row naming "
        ".harness/harness/features/FEAT-TEST."))
    results.append(("(41.c) the feature directory path scopes it — silent",
                    not _lines(out, "INV-41"), out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`check-state.py` refuses a new BRIEF with an untagged SC."))
    results.append(("(41.d) naming the script as a subject is a mention, not an invocation",
                    not _lines(out, "INV-41"), out[:400]))

    _, out = _check(_legacy(), BRIEF_OLD)
    results.append(("(41.e) an old-shape BRIEF is not graded",
                    not _lines(out, "INV-41"), out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`.claude/skills/harness/bin/check-domain.py --check-plan` exits 0."))
    v = _violations(out, "INV-41")
    results.append(("(41.f) check-domain.py is covered too",
                    len(v) == 1 and "check-domain.py" in v[0], out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "the reviewer runs `check-state.py` and it exits 0."))
    results.append(("(41.g) a bare span the SC RUNS is an invocation",
                    len(_violations(out, "INV-41")) == 1, out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`python3 .claude/skills/harness/bin/check-state.py` has no VIOLATION row naming FEAT-TEST."))
    results.append(("(41.h) the feature id in the SC text scopes it — silent",
                    not _lines(out, "INV-41"), out[:400]))
    return results


def _report(results):
    ok = True
    for name, passed, detail in results:
        print(f"{'ok' if passed else 'FAIL'} - case {name}")
        if not passed:
            ok = False
            print(f"        {str(detail).strip()[:300]}")
    return ok


# ----------------------------------------------------------------------------- INV-44 ---

# The honest record of a rejection is station-only: the ticket was refused before any task
# was planned, so the plan carries a station and no tasks (harness_yaml's marker rule).
_REJECTED_PLAN = "schema: plan/1\nfeature: FEAT-TEST\nstation_only: true\nstatus: rejected\ntasks: []\n"
_BRIEF_DRAFT = BRIEF_NEW.replace("status: approved", "status: pending")


def _rejected_doc(**extra):
    doc = _in_era(runs=[{"id": "plan-product", "squad": "product", "verdict": "PASS",
                         "agent": "harness-orchestrator"}],
                  judgements=[{"at": "2026-09-16T05:00:00Z", "by": "harness-orchestrator",
                               "kind": "reject", "decision": "1594",
                               "reason": "#285 superseded by #1594"}])
    doc.update(extra)
    return doc


def _rejected(feature, plan=_REJECTED_PLAN, brief=_BRIEF_DRAFT):
    with tempfile.TemporaryDirectory() as tmp:
        fdir = _fixture(tmp, feature, brief)
        with open(os.path.join(fdir, "plan.yaml"), "w") as f:
            f.write(plan)
        return run(tmp)


def _inv44(feature, plan=_REJECTED_PLAN, brief=_BRIEF_DRAFT):
    """INV-44 violation lines for a rejected fixture, plus the raw output."""
    _, out = _rejected(feature, plan=plan, brief=brief)
    return _violations(out, "INV-44"), out


def _one_saying(v, needle):
    return len(v) == 1 and needle in v[0]


def case_inv44_run_shape():
    """FEAT-1714 T-03: a rejected record is one orchestrator run at zero cycles — each
    dimension its own violation; a conforming record is silent AND exempt from the approval
    demand only by being at this station."""
    _, out = _rejected(_rejected_doc())
    silent = ("(44.a) a conforming rejected record is silent on INV-44 and on the approval gate",
              not _lines(out, "INV-44") and not _lines(out, "is NOT approved"), out[:600])
    v, out = _inv44(_rejected_doc(cycles_used=1))
    cycles = ("(44.b) cycles_used other than integer 0 is a VIOLATION naming cycles",
              _one_saying(v, "cycles_used=1"), out[:400])
    v, out = _inv44(_rejected_doc(runs=[]))
    none = ("(44.c) zero runs is a VIOLATION naming the count", _one_saying(v, "0 run(s)"), out[:400])
    two = _rejected_doc()["runs"] + [{"id": "build-eng", "squad": "eng", "verdict": "PASS",
                                       "agent": "harness-eng-lead"}]
    v, out = _inv44(_rejected_doc(runs=two))
    pair = ("(44.d) two runs is a VIOLATION naming the count", _one_saying(v, "2 run(s)"), out[:400])
    lead = [dict(_rejected_doc()["runs"][0], agent="harness-product-lead")]
    v, out = _inv44(_rejected_doc(runs=lead))
    owner = ("(44.e) the one run owned by a lead is a VIOLATION naming the agent",
             _one_saying(v, "harness-product-lead"), out[:400])
    return [silent, cycles, none, pair, owner]


def case_inv44_ledger_and_signatures():
    """A rejected record carries a reject judgement and nothing signed — no approved plan,
    no signed BRIEF, no panel."""
    v, out = _inv44(_rejected_doc(judgements=[_j("mission", "plan")]))
    judgement = ("(44.f) no reject judgement is a VIOLATION naming the kind and remedy",
                 _one_saying(v, "kind reject") and "feature-record.py" in v[0], out[:400])
    approved = _REJECTED_PLAN.replace(
        "status: rejected\n",
        "approval:\n  status: approved\n  approved_by: X\n  date: 2026-09-16\nstatus: rejected\n")
    v, out = _inv44(_rejected_doc(), plan=approved)
    plan = ("(44.g) an approved plan under a rejected station is a VIOLATION",
            _one_saying(v, "approval is approved"), out[:400])
    v, out = _inv44(_rejected_doc(), brief=BRIEF_NEW)
    brief = ("(44.h) a signed BRIEF under a rejected station is a VIOLATION",
             _one_saying(v, "BRIEF.md"), out[:400])
    panel = _REJECTED_PLAN + "panel:\n  last_run: x\n  cycle: 0\n  readers: []\n  findings: []\n"
    v, out = _inv44(_rejected_doc(), plan=panel)
    paneled = ("(44.i) a panel mapping under a rejected station is a VIOLATION",
               _one_saying(v, "panel"), out[:400])
    return [judgement, plan, brief, paneled]


def case_inv44_scope():
    """Every bad dimension reports separately; the same record at another station is not
    INV-44's to grade."""
    v, out = _inv44(_rejected_doc(cycles_used=2, runs=[], judgements=[]))
    separate = ("(44.j) every bad dimension is reported separately", len(v) == 3, out[:600])
    _, out = _check(_rejected_doc(cycles_used=2), BRIEF_NEW)
    elsewhere = ("(44.k) the same record at any other station is not INV-44's to grade",
                 not _lines(out, "INV-44"), out[:400])
    return [separate, elsewhere]


def case_inv44():
    return case_inv44_run_shape() + case_inv44_ledger_and_signatures() + case_inv44_scope()


def main():
    return 0 if _report(case_inv38() + case_inv39() + case_inv40() + case_inv40_signed_text()
                        + case_inv41() + case_inv43_chronology() + case_inv43_unreadable()
                        + case_inv43_matching() + case_inv43_scope() + case_inv43_era_boundary()
                        + case_inv43_era_config() + case_inv44()) else 1


if __name__ == "__main__":
    sys.exit(main())
