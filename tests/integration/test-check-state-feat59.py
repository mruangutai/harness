#!/usr/bin/env python3
"""check-state.sh INV-38..41: the FEAT-59 proportional-flow invariants.

INV-38 brief-perspectives (SC-10): a by-perspective BRIEF has every perspective discharged by
a tagged SC and every SC tagged with a declared perspective; the old shape is untouched.
INV-39 cycles-budget (SC-15): cycles_used <= max_total_cycles, and a raise above the
harness.json default is a recorded budget_decisions entry (DEC-157).
INV-40 judgement-ledger (SC-21): mission, re-gate and succession each leave a judgements[]
entry; a record that predates the ledger is NOTED, never failed.
INV-41 sc-repo-wide (SC-16): an SC that invokes check-state.sh / check-domain.sh with no
feature-scoped argument is refused.

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
import json
import os
import sys
import tempfile
from check_state_support import run

FEAT = "FEAT-TEST"

HARNESS_JSON = ('{\n  "github": {"sync": false, "repo": null},\n'
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

- SC-01: `bash .claude/skills/harness/bin/check-state.sh` exits 0.

## Approval

status: approved
date: 2026-09-11
"""

HANDOFF_SEQ = ("# Handoff — FEAT-TEST, build → review — written at abc1234, seq-{n}\n\n"
               "## Next\nbody\n## Trust\nbody\n## Dead ends\nbody\n## Working set\nbody\n"
               "## Done when\nPointer: brief-sc:SC-01\n")


def _fixture(tmp, feature, brief=None, notes=None, harness_json=HARNESS_JSON):
    """One feature at .harness/harness/features/FEAT-TEST with the given feature.json
    mapping, an optional BRIEF.md text and optional notes/{name: text}."""
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
    return fdir


def _lines(out, tag):
    return [l for l in out.splitlines() if tag in l]


def _violations(out, tag):
    return [l for l in _lines(out, tag) if l.startswith("  VIOLATION")]


def _notes(out, tag):
    return [l for l in _lines(out, tag) if l.startswith("  note")]


def _check(feature, brief=None, notes=None, harness_json=HARNESS_JSON):
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, feature, brief, notes, harness_json)
        return run(tmp)


def _run(rid, verdict="PASS", squad="eng"):
    return {"id": rid, "squad": squad, "verdict": verdict}


def _j(kind):
    return {"at": "2026-09-11T10:00:00Z", "by": "harness-orchestrator", "kind": kind,
            "decision": kind, "reason": "fixture"}


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

    _, out = _check(_in_era(mission="patch", judgements=[_j("mission")]))
    results.append(("(40.b) mission with its judgement is silent",
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


# ----------------------------------------------------------------------------- INV-41 ---

def _brief_with_sc02(text):
    return BRIEF_NEW.replace("- SC-02 (code maintainer): the template carries the block.",
                             "- SC-02 (code maintainer): " + text)


def case_inv41():
    """SC-16: repository-wide state is a merge-time check, not a feature criterion."""
    results = []
    MSG = "repository-wide state is a merge-time check, not a feature criterion (SC-16)"

    _, out = _check(_in_era(), _brief_with_sc02(
        "`bash .claude/skills/harness/bin/check-state.sh` exits 0."))
    v = _violations(out, "INV-41")
    results.append(("(41.a) an unscoped check-state.sh invocation is a VIOLATION naming the SC",
                    len(v) == 1 and "SC-02" in v[0] and MSG in v[0], out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`bash .claude/skills/harness/bin/check-state.sh --feature FEAT-TEST` exits 0."))
    results.append(("(41.b) `--feature` scopes it — silent",
                    not _lines(out, "INV-41"), out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`bash .claude/skills/harness/bin/check-state.sh` reports no row naming "
        ".harness/harness/features/FEAT-TEST."))
    results.append(("(41.c) the feature directory path scopes it — silent",
                    not _lines(out, "INV-41"), out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`check-state.sh` refuses a new BRIEF with an untagged SC."))
    results.append(("(41.d) naming the script as a subject is a mention, not an invocation",
                    not _lines(out, "INV-41"), out[:400]))

    _, out = _check(_legacy(), BRIEF_OLD)
    results.append(("(41.e) an old-shape BRIEF is not graded",
                    not _lines(out, "INV-41"), out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`.claude/skills/harness/bin/check-domain.sh --check-plan` exits 0."))
    v = _violations(out, "INV-41")
    results.append(("(41.f) check-domain.sh is covered too",
                    len(v) == 1 and "check-domain.sh" in v[0], out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "the reviewer runs `check-state.sh` and it exits 0."))
    results.append(("(41.g) a bare span the SC RUNS is an invocation",
                    len(_violations(out, "INV-41")) == 1, out[:400]))

    _, out = _check(_in_era(), _brief_with_sc02(
        "`bash .claude/skills/harness/bin/check-state.sh` has no VIOLATION row naming FEAT-TEST."))
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


def main():
    return 0 if _report(case_inv38() + case_inv39() + case_inv40() + case_inv41()) else 1


if __name__ == "__main__":
    sys.exit(main())
