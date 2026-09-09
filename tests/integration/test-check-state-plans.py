#!/usr/bin/env python3
"""check-state.sh INV-3/4/5, INV-6, INV-22, INV-23, INV-34 and INV-35: file content.

Sliced out of tests/integration/test-check-state.py (issue #1527). What a feature's own
files must contain — the plan read through the loader (INV-3/4/5), the review_sha pin and
BUG-1080's plan-phase exemption (INV-6), the run count (INV-22), the DEC-150 document
budgets (INV-23), a feature directory with no plan.yaml (INV-34) and a plain scalar whose
unquoted ` #NN` truncates silently (INV-35).

CARRIES THE INV-6 FIXTURE STRINGS `review_sha: none` and `review_sha: 1ce886a` that
tests/unit/test-team-catalog.py asserts on by path.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import os
import re
import sys
import tempfile
from check_state_support import (HARNESS_JSON_SYNC_OFF, SCRIPT, feature_yaml, make_fixture,
    run)


def case_h():
    """Issue #16: `review_sha: none` is a truthy STRING, so INV-6 passed unpinned.

    `val()` returns `str(v)`, so the literal `none` is truthy and `not val("review_sha")`
    is False. Only an ABSENT key tripped the check — case (e) covers that axis and
    passed throughout, which is exactly why this hole survived: the invariant had a
    test, and the test agreed with it.

    FEAT-05's own feature.json carried `review_sha: none` for its whole plan phase
    while recording validator-squad runs, so this was live on a shipped feature, not
    hypothetical.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
            f.write("feature_id: FEAT-TEST\n"
                    "review_sha: none\n"
                    "runs:\n"
                    "  - id: 2026-08-04-01-validator\n"
                    "    squad: validator\n"
                    "    verdict: PASS\n")
        code, out = run(tmp)
        ok = "review_sha is not pinned" in out
        print(f"{'ok' if ok else 'FAIL'} - case (h): issue #16 — `review_sha: none` is a "
              f"placeholder, not a pin, so INV-6 fires")
        if not ok:
            print("        INV-6 was silent: the string 'none' read as truthy and the "
                  "gate failed OPEN on an unpinned feature")
        return ok


def case_i():
    """The VALUE axis: a real SHA must NOT trip INV-6.

    Guards the over-broad fix — a rewrite that fires whenever `review_sha` is a string
    would turn every correctly pinned feature into a violation. `1ce886a` is a real
    short SHA shape, not a placeholder.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
            f.write("feature_id: FEAT-TEST\n"
                    "review_sha: 1ce886a\n"
                    "runs:\n"
                    "  - id: 2026-08-04-01-validator\n"
                    "    squad: validator\n"
                    "    verdict: PASS\n")
        code, out = run(tmp)
        ok = "review_sha is not pinned" not in out
        print(f"{'ok' if ok else 'FAIL'} - case (i): a pinned SHA does not trip INV-6")
        if not ok:
            print("        INV-6 fired on a correctly pinned feature — the fix is "
                  "over-scoped and every pinned feature is now a violation")
        return ok


def case_j():
    """The PRECONDITION axis: no validator run means no INV-6, placeholder or not.

    INV-6 exists to stop a REVIEWER diffing a moving HEAD (DEC-50). A feature with no
    validator run has nothing to pin for yet. This guards the `any(sq == "validator")`
    conjunct against being dropped by a rewrite that only looks at the value — and it
    is live, not theoretical: FEAT-06's own feature.json is exactly this shape
    (placeholder review_sha, product/eng runs only) and must not self-report.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
            f.write("feature_id: FEAT-TEST\n"
                    "review_sha: none\n"
                    "runs:\n"
                    "  - id: 2026-08-04-01-product\n"
                    "    squad: product\n"
                    "    verdict: PASS\n")
        code, out = run(tmp)
        ok = "review_sha is not pinned" not in out
        print(f"{'ok' if ok else 'FAIL'} - case (j): no validator run, so INV-6 stays "
              f"silent even on a placeholder")
        if not ok:
            print("        INV-6 fired with no validator run — the "
                  "any(squad == 'validator') conjunct was dropped")
        return ok


def case_l():
    """INV-22 (issue #79): runs are counted, the budget is INFORMATIONAL, and a
    per-feature raise outranks the default.

    Three assertions, because a one-sided test would pass on a check that always fires
    or never does:
      (1) 21 runs against a 20 budget NOTES,
      (2) exactly 20 does NOT — the boundary is `>`, not `>=`,
      (3) a feature declaring max_total_runs: 30 silences it,
      (4) and the exit code is UNCHANGED, because this must never gate.
    """
    def build(tmp, n, declared="", budget='"budgets": {"max_total_runs": 20}'):
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write('{\n  "github": {"sync": false, "repo": null}'
                    + (",\n  " + budget if budget else "") + "\n}\n")
        runs = "\n".join(f"  - {{ id: r{i}, squad: eng, verdict: PASS }}"
                         for i in range(n))
        with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
            f.write(f"feature_id: FEAT-TEST\ncycles_used: 2\n"
                    f"review_sha: abc1234\n{declared}runs:\n{runs}\n")
        return run(tmp)

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        code_over, out_over = build(tmp, 21)
    with tempfile.TemporaryDirectory() as tmp:
        code_at, out_at = build(tmp, 20)
    with tempfile.TemporaryDirectory() as tmp:
        _code_raised, out_raised = build(tmp, 21, "max_total_runs: 30\n")
    # (l5-l8) THE CONFIGURED VALUE MUST ACTUALLY BE READ, and a budget this check
    # cannot resolve must SAY SO. The first version of case (l) asserted neither:
    # a mutant hardcoding `_budget = 20` and never opening harness.json passed all
    # four assertions, exit 0 (PR #142 review, HIGH 2). Reproduced before fixing.
    # (l5) uses a DIFFERENT budget so a hardcoded 20 gives the wrong number in the
    # message; (l6)-(l8) cover the shapes that used to disable the check in silence,
    # including the one shipped in templates/examples/harness.kaya-ai.json.
    with tempfile.TemporaryDirectory() as tmp:
        _c, out_b5 = build(tmp, 7, budget='"budgets": {"max_total_runs": 5}')
    with tempfile.TemporaryDirectory() as tmp:
        _c, out_nokey = build(tmp, 21, budget='"budgets": {}')
    with tempfile.TemporaryDirectory() as tmp:
        _c, out_noblock = build(tmp, 21, budget="")
    with tempfile.TemporaryDirectory() as tmp:
        _c, out_bool = build(tmp, 21, budget='"budgets": {"max_total_runs": true}')

    for name, ok, detail in (
        ("(l1) 21 runs against a 20 budget is NOTED",
         "21 runs recorded against a 20-run budget" in out_over, out_over),
        ("(l2) exactly 20 does NOT fire — the boundary is >, not >=",
         "runs recorded against" not in out_at, out_at),
        ("(l3) a per-feature max_total_runs: 30 silences it",
         "runs recorded against" not in out_raised, out_raised),
        ("(l4) INV-22 NEVER gates — exit code identical over and under budget",
         code_over == code_at, f"over={code_over} at={code_at}"),
        ("(l5) the CONFIGURED value is read — budget 5 with 7 runs names 5, not 20",
         "7 runs recorded against a 5-run budget" in out_b5, out_b5),
        ("(l6) budgets present but key missing is REPORTED INACTIVE, never silent",
         "run counting is INACTIVE" in out_nokey, out_nokey),
        ("(l7) no budgets block at all (the shipped kaya example) is REPORTED INACTIVE",
         "run counting is INACTIVE" in out_noblock, out_noblock),
        ("(l8) a boolean budget is REJECTED, not treated as an int (bool subclasses int)",
         "run counting is INACTIVE" in out_bool, out_bool),
    ):
        print(f"{'ok' if ok else 'FAIL'} - case {name}")
        if not ok:
            print(f"        {detail.strip()[:200]}")
        results.append(ok)
    return all(results)


def case_n():
    """INV-23 sweeps the DEC-150 budgets from DISK, and stays quiet when they are met.

    THREE fixtures and PER-FILE assertions, and the per-file part was itself a defect
    found by mutation. The first draft crossed both budgets at once and asserted only
    "INV-23" in the output — so raising the feature.json budget from 200 to 250 left the
    STATE.md finding in the output and the case still reported ok. A test that cannot tell
    which of two checks fired is not testing either.

    Each fixture now crosses exactly ONE budget by exactly ONE line, and asserts the other
    file stays silent. That binds the message to the comparison: case (o) below proves the
    two scripts DECLARE the same number, and this proves the declared number is the one
    actually enforced.
    """
    results = []
    for label, fl, sl, want_f, want_s in (
        # 310/290, not 201/200: T-06 raised the feature budget from 200 to 300. Each
        # fixture still crosses exactly ONE budget by exactly ONE line, which is what
        # binds the message to the comparison.
        ("feature.json over", 301, 120, True,  False),
        ("STATE.md over",     300, 121, False, True),
        ("both within",       300, 120, False, False),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            h = make_fixture(tmp, '{}', "  parent: 40")
            fd = os.path.join(h, "harness", "features", "FEAT-TEST")
            # EXACTLY `fl` lines, header included — the boundary is the whole point of the
            # second fixture, so the padding is sized against the header rather than added
            # to it. Written the naive way, "within" came out at 205 lines and reported a
            # violation, which reads as INV-23 being wrong when the fixture was.
            head = feature_yaml("  parent: 40")
            pad = fl - len(head.splitlines())
            with open(os.path.join(fd, "feature.json"), "w") as f:
                f.write(head + "\n".join(f"k{i}: v" for i in range(pad)) + "\n")
            with open(os.path.join(fd, "STATE.md"), "w") as f:
                f.write("## Current\n" + "\n".join(f"line {i}" for i in range(sl - 1)) + "\n")
            _code, out = run(tmp)
            got_f = "INV-23 " in out and "FEAT-TEST" in out and "feature.json is" in out
            got_s = "INV-23 " in out and "FEAT-TEST" in out and "STATE.md is" in out
            ok = (got_f == want_f) and (got_s == want_s)
            results.append(ok)
            print(f"{'ok' if ok else 'FAIL'} - case (n/{label}): at {fl} feature.json / "
                  f"{sl} STATE.md lines, INV-23 fires on "
                  f"[{'feature.json' if got_f else ''}{' ' if got_f and got_s else ''}"
                  f"{'STATE.md' if got_s else ''}{'nothing' if not (got_f or got_s) else ''}]"
                  f" — wanted [{'feature.json' if want_f else ''}"
                  f"{' ' if want_f and want_s else ''}{'STATE.md' if want_s else ''}"
                  f"{'nothing' if not (want_f or want_s) else ''}]")
    return all(results)


def case_p():
    """INV-23's CLAUDE.md budget, bound BEHAVIOURALLY at its boundary — and at warn level.

    Review of PR #152, and it is case (n)'s lesson repeating one file over. Case (o)
    compares SOURCE TEXT, so mutating the comparison `len(_cml) > 80` -> `> 999` while
    leaving the `budget is 80` message alone survived all three suites with case (o)
    printing ok. The PR body listed "CLAUDE.md budget drifted between the two files" under
    mutants caught, which was true of the mutation actually run — one that changed the
    MESSAGE — and overstated what the case covers. Case (o) binds the two files to each
    other; only a boundary fixture binds either of them to reality.

    WARN LEVEL IS ASSERTED TOO. INV-23 must report and NOT change the exit code, exactly as
    for the four state files: an over-budget CLAUDE.md predating the gate must not halt
    /harness entry, which is the same reasoning that kept FEAT-05/STATE.md from doing so.
    """
    results, codes, outs = [], {}, {}
    for label, n, want in (("over", 81, True), ("at the budget", 80, False)):
        with tempfile.TemporaryDirectory() as tmp:
            make_fixture(tmp, '{}', "  parent: 40")
            with open(os.path.join(tmp, "CLAUDE.md"), "w") as f:
                f.write("\n".join(f"line {i}" for i in range(n)) + "\n")
            code, out = run(tmp)
            codes[label] = code
            outs[label] = out
            got = "INV-23 CLAUDE.md is" in out
            ok = got == want
            results.append(ok)
            print(f"{'ok' if ok else 'FAIL'} - case (p/{label}): CLAUDE.md at {n} lines -> "
                  f"INV-23 {'fires' if got else 'silent'} (want "
                  f"{'fires' if want else 'silent'})")
    # WARN LEVEL, ASSERTED ON THE LINE PREFIX — not on the exit code, which SATURATES.
    #
    # Two earlier drafts of this assertion were both wrong, and the second looked right.
    # Draft 1 compared the exit code to a literal 0 and failed on correct code: the fixture
    # is a bare .harness with no BRIEF, so check-state legitimately exits 1 for unrelated
    # reasons. Draft 2 compared the two fixtures' exit codes to each other — and a reviewer
    # showed that proves nothing, because `sys.exit(1 if bad else 0)` is already pinned at 1
    # by an unrelated violation before CLAUDE.md is ever consulted. Changing INV-23's
    # `warn.append` to `bad.append` left the ENTIRE SUITE GREEN with this case printing
    # `ok ... (1 -> 1)`. It was comparing two constants.
    #
    # check-state.sh prints `  VIOLATION  ` for bad and `  note       ` for warn. That
    # prefix flips under the mutation, on the fixture this case already has, and it cannot
    # saturate. One line, no second fixture — and notably NOT the "build a clean fixture"
    # fix, which would duplicate case (d)'s settings blob that case (d)'s own docstring
    # records as having gone stale once already.
    over_out = outs["over"]
    warn_shaped = any(l.strip().startswith("note") and "INV-23 CLAUDE.md" in l
                      for l in over_out.splitlines())
    halting = any("VIOLATION" in l and "INV-23 CLAUDE.md" in l for l in over_out.splitlines())
    ok_warn = warn_shaped and not halting
    results.append(ok_warn)
    print(f"{'ok' if ok_warn else 'FAIL'} - case (p/warn): the CLAUDE.md finding is a `note`, "
          f"not a `VIOLATION` — warn level, so it cannot halt /harness entry"
          + ("" if ok_warn else f" | got: {[l for l in over_out.splitlines() if 'INV-23 CLAUDE' in l]}"))
    return all(results)


PLAN_YAML_OK = """schema: plan/1
feature: FEAT-TEST
approval: {status: approved}
tasks:
  - id: T-01
    title: a task
    traces: [REQ-01]
    change_type: logic
    execution_mode: team
    execution_agent: harness-dev-ops
    depends_on: []
    status: pending
    files: [src/a.py]
    verify: |
      true
    intent: |
      do it
"""


def case_q():
    """(q) DEC-182: INV-3/4/5 read plan.yaml through the loader, not a regex over prose.

    INV-4's old "no change_type:" case cannot reach the yaml path at all — load_plan
    guarantees the field, so a missing one is a LOAD error, caught before the invariants
    run. What remains is what the loader does not police: the approval block, and STATE.md
    pointing at a task the plan does not contain.
    """
    results = []

    # approval: approved -> silent; pending -> a note, never a halt
    for status, want_note in (("approved", False), ("pending", True)):
        with tempfile.TemporaryDirectory() as tmp:
            h = make_fixture(tmp, '{}', "  parent: 40")
            fd = os.path.join(h, "harness", "features", "FEAT-TEST")
            os.remove(os.path.join(fd, "feature.json"))
            with open(os.path.join(fd, "feature.json"), "w") as f:
                f.write("feature_id: FEAT-TEST\nstatus: in_review\n")
            with open(os.path.join(fd, "plan.yaml"), "w") as f:
                f.write(PLAN_YAML_OK.replace("status: approved", f"status: {status}"))
            _code, out = run(tmp)
            got = "plan.yaml approval is pending" in out
            ok = got == want_note
            results.append(ok)
            print(f"{'ok' if ok else 'FAIL'} - case (q/{status}): INV-3 "
                  f"{'notes' if want_note else 'is silent'} on plan.yaml")

    # A plan.yaml that does not LOAD is a violation naming the file — never a silent skip.
    with tempfile.TemporaryDirectory() as tmp:
        h = make_fixture(tmp, '{}', "  parent: 40")
        fd = os.path.join(h, "harness", "features", "FEAT-TEST")
        with open(os.path.join(fd, "plan.yaml"), "w") as f:
            f.write("tasks:\n  - id: T-01\n   bad: indent\n")
        _code, out = run(tmp)
        ok = "plan.yaml does not load" in out
        results.append(ok)
        print(f"{'ok' if ok else 'FAIL'} - case (q/malformed): a plan.yaml that does not "
              f"load is reported, not skipped")

    # INV-5 across the yaml path: STATE.md naming a task the plan lacks.
    with tempfile.TemporaryDirectory() as tmp:
        h = make_fixture(tmp, '{}', "  parent: 40")
        fd = os.path.join(h, "harness", "features", "FEAT-TEST")
        with open(os.path.join(fd, "plan.yaml"), "w") as f:
            f.write(PLAN_YAML_OK)
        with open(os.path.join(fd, "STATE.md"), "w") as f:
            f.write("## Current\nworking T-99\n")
        _code, out = run(tmp)
        ok = "references T-99" in out and "plan.yaml" in out
        results.append(ok)
        print(f"{'ok' if ok else 'FAIL'} - case (q/inv5): STATE.md naming a task the "
              f"plan.yaml lacks is a violation")
    return all(results)


# --- BUG-1080: INV-6 must not forbid the plan-phase run DEC-207 legalises ------------
#
# INV-6 exists to stop a REVIEWER diffing a moving HEAD (DEC-50). A plan-phase panel
# grades a SPECIFICATION, so there is no commit to pin and the hazard cannot arise.
# DEC-207 legalises that run with `code_grade: n_a`; INV-6 predates DEC-207 and fired
# on it anyway, and validate-digest.py REFUSES a plan review when review_sha IS pinned.
# No value satisfied both rules, which is the defect (#1080).
#
# The exemption is keyed on the RUN, never on approval.status. Keying it on a pending
# approval would break the instant a plan is signed: the plan-phase runs stay in runs[]
# while review_sha is unpinned until the Building -> Review seam, so the gate would red
# through the whole build phase instead. case_inv6_exempt_survives_signature pins that.

_PIN_MSG = "review_sha is not pinned"


def _inv6_feature(runs_yaml, review_sha="none", approval=""):
    """Build a one-feature tree and return check-state's output."""
    tmp = tempfile.mkdtemp()
    h = os.path.join(tmp, ".harness")
    os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(HARNESS_JSON_SYNC_OFF)
    with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
        f.write(f"feature_id: FEAT-TEST\nreview_sha: {review_sha}\n{approval}runs:\n{runs_yaml}")
    _code, out = run(tmp)
    return out


_PLAN_RUN = ("  - id: 2026-08-31-01-validator\n"
             "    squad: validator\n"
             "    verdict: PASS\n"
             "    code_grade: n_a\n")


_CODE_RUN = ("  - id: 2026-08-31-02-validator\n"
             "    squad: validator\n"
             "    verdict: PASS\n")


def case_inv6_plan_run_is_exempt():
    """DEC-207's run: graded a plan, no code, so no SHA to pin. INV-6 must stay silent.

    This is the case that reddened the gate on FEAT-46 and had no honest resolution.
    """
    out = _inv6_feature(_PLAN_RUN)
    ok = _PIN_MSG not in out
    print(f"{'ok' if ok else 'FAIL'} - INV-6 exempts a plan-phase run (code_grade: n_a)")
    if not ok:
        print("        INV-6 fired on a run that graded no code — #1080 is not fixed")
    return ok


def case_inv6_code_run_still_fires():
    """The regression guard: a validator run that does NOT declare code_grade reviewed
    CODE, so an unpinned review_sha is still the GAP-7 failure. Absence is fail-CLOSED,
    the opposite default from the `agent` key, which FEAT-31 made deliberately benign."""
    out = _inv6_feature(_CODE_RUN)
    ok = _PIN_MSG in out
    print(f"{'ok' if ok else 'FAIL'} - INV-6 still fires on a code run with no pin")
    if not ok:
        print("        the exemption is over-scoped: absence of code_grade now exempts, "
              "so INV-6 no longer guards anything")
    return ok


def case_inv6_unknown_grade_fails_closed():
    """A value other than n_a is not an exemption. Guards the substring-match shortcut
    and any rewrite that treats the KEY's presence as the exemption."""
    out = _inv6_feature(_PLAN_RUN.replace("code_grade: n_a", "code_grade: graded"))
    ok = _PIN_MSG in out
    print(f"{'ok' if ok else 'FAIL'} - INV-6 fails closed on an unknown code_grade")
    if not ok:
        print("        any code_grade value exempted the run — presence of the key was "
              "read as the exemption instead of its value")
    return ok


def case_inv6_mixed_runs_still_fire():
    """The `any` axis, and the sharpest one: one exempt run must not silence a
    non-exempt sibling. A feature whose plan was panel-reviewed AND whose code was
    reviewed still needs a pin for the second run."""
    out = _inv6_feature(_PLAN_RUN + _CODE_RUN)
    ok = _PIN_MSG in out
    print(f"{'ok' if ok else 'FAIL'} - INV-6 fires when a code run sits beside an "
          f"exempt plan run")
    if not ok:
        print("        `any(non-exempt)` collapsed into `all(exempt)` — one plan run "
              "now silences every code run on the feature")
    return ok


def case_inv6_exempt_survives_signature():
    """WHY THE EXEMPTION IS NOT KEYED ON approval.status.

    An APPROVED plan whose only validator runs are plan-phase still has no pin until the
    Building -> Review seam. The rejected fix (exempt while approval.status is pending)
    turns green here the moment the operator signs and stays red for the whole build.
    """
    approval = "approval:\n  status: approved\n  date: 2026-08-31\n"
    out = _inv6_feature(_PLAN_RUN, approval=approval)
    ok = _PIN_MSG not in out
    print(f"{'ok' if ok else 'FAIL'} - INV-6 exemption survives signature (not keyed "
          f"on approval.status)")
    if not ok:
        print("        the exemption is keyed on a pending approval, so signing reds "
              "the gate for the entire build phase")
    return ok


def case_inv6_pinned_plan_run_silent():
    """A pinned feature carrying a plan-phase run must not newly fire. Guards against a
    rewrite that inverts the value test while adding the run test."""
    out = _inv6_feature(_PLAN_RUN + _CODE_RUN, review_sha="1ce886a")
    ok = _PIN_MSG not in out
    print(f"{'ok' if ok else 'FAIL'} - INV-6 silent on a pinned feature with both run "
          f"kinds")
    if not ok:
        print("        INV-6 fired on a correctly pinned feature")
    return ok


def case_inv6_case_variant_is_not_exempt():
    """Panel Q2: the gate's value test is EXACT, matching the schema's closed enum, so a
    document can never be schema-invalid and gate-exempt at once. `N_A` fails both."""
    out = _inv6_feature(_PLAN_RUN.replace("code_grade: n_a", "code_grade: N_A"))
    ok = _PIN_MSG in out
    print(f"{'ok' if ok else 'FAIL'} - INV-6 does not exempt a case-variant code_grade")
    if not ok:
        print("        the gate case-folds where the schema does not, so `N_A` is "
              "gate-exempt and schema-invalid at the same time")
    return ok


def case_inv6_message_names_the_remedy():
    """Panel Q3, and the BUG-1071 discoverability lesson: the violation must name the key
    that fixes it, at the point of failure, or the operator has to find this file."""
    out = _inv6_feature(_CODE_RUN)
    line = [l for l in out.splitlines() if _PIN_MSG in l]
    ok = bool(line) and "code_grade: n_a" in line[0]
    print(f"{'ok' if ok else 'FAIL'} - INV-6's violation names code_grade: n_a")
    if not ok:
        print("        the message states the defect without the remedy")
    return ok


def case_inv6_producer_is_documented():
    """THE CYCLE-0 BLOCKING FINDING. A legal exemption nothing writes is dead code, and the
    next plan-phase panel reproduces #1080 verbatim. SKILL.md step 6 is the only documented
    runs-writing instruction, so the key must be named THERE.

    This is the `check-decision-anchors.py` shape - a tool that ships and is invoked by
    nothing - which has recurred repeatedly in this repository.

    Cycle 1's panel showed the first cut bound too loosely: it asserted the string appeared
    ANYWHERE in the file, which three mutants evaded. It now binds the step-6 block, so
    moving the key into unrelated prose - or into a note about the key rather than an
    instruction to write it - turns this red.
    """
    # Anchored on __file__, never SCRIPT: CHECK_STATE_BIN may point SCRIPT at a mutant
    # copy in a temp dir, and this assertion is about the shipped skill, not the fixture.
    skill = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".claude", "skills", "harness", "SKILL.md")
    try:
        with open(skill, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"FAIL - INV-6's producer is documented: SKILL.md unreadable ({exc})")
        return False
    # Step 6 runs from its own numbered heading to the next top-level numbered step.
    step6 = re.search(r"^6\. \*\*Adjust and record\*\*(.*?)^7\. ", text, re.S | re.M)
    ok = bool(step6) and "code_grade: n_a" in step6.group(1)
    print(f"{'ok' if ok else 'FAIL'} - INV-6's exemption has a documented producer "
          f"(SKILL.md step 6 names code_grade: n_a)")
    if not ok:
        if not step6:
            print("        step 6 'Adjust and record' was not found: the runs-writing "
                  "instruction moved, so this test can no longer bind it")
        else:
            print("        the runs-writing step does not name the key, so every recorded "
                  "plan panel omits it and INV-6 deadlocks again")
    return ok


def _i34_fixture(tmp, with_plan):
    """A feature directory with a feature.json, and a plan.yaml only when asked for."""
    h = make_fixture(tmp, HARNESS_JSON_SYNC_OFF, "  parent: none")
    feat = os.path.join(h, "harness", "features", "FEAT-TEST")
    if with_plan:
        with open(os.path.join(feat, "plan.yaml"), "w") as f:
            f.write("schema: plan/1\nfeature: FEAT-TEST\nstatus: done\n"
                    "station_only: true\ntasks: []\n")
    return feat


def _i34_lines(out):
    return [l for l in out.splitlines() if "INV-34" in l]


def case_inv34_plan_required():
    """FEAT-41 T-19 — INV-34: a feature directory with NO plan.yaml is REPORTED.

    Operator-directed after cycle 2's C2-01. The one-record rule puts a feature's station in
    plan.yaml, so a feature WITHOUT one has nowhere to record it -- which is exactly how this
    feature destroyed BUG-1030's `Review` and then could not put it back: feature.json refuses
    the key (exit 11) and, before T-19, plan.yaml refused to exist without tasks.

    The invariant is what stops that recurring: the migration is a one-time repair, and without
    a check the next plan-less feature reintroduces the same hole silently.
    """
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        _i34_fixture(tmp, with_plan=False)
        code, out = run(tmp)
        ls = _i34_lines(out)
        ok = bool(ls) and any("FEAT-TEST" in l for l in ls) and any("plan.yaml" in l for l in ls)
        results.append(("(inv34.a) a feature with no plan.yaml is reported, naming the file",
                        ok, out[:400]))
    return results


def case_inv34_present_is_silent():
    """NEGATIVE CONTROL. A station-only plan.yaml satisfies it, so the invariant is about the
    RECORD existing and not about tasks -- the twelve directories this feature backfilled carry
    exactly this shape, and if they tripped it the migration would be self-defeating."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        _i34_fixture(tmp, with_plan=True)
        code, out = run(tmp)
        ls = _i34_lines(out)
        results.append(("(inv34.b) a station-only plan.yaml is enough — no INV-34 line",
                        not ls, out[:400]))
    return results


def _i34_station_only(tmp, tasks_block, state_md=None):
    """A feature whose plan is station-only, or carries tasks, plus an optional STATE.md."""
    h = make_fixture(tmp, HARNESS_JSON_SYNC_OFF, "  parent: none")
    feat = os.path.join(h, "harness", "features", "FEAT-TEST")
    with open(os.path.join(feat, "plan.yaml"), "w") as f:
        f.write("schema: plan/1\nfeature: FEAT-TEST\nstatus: done\n" + tasks_block)
    if state_md is not None:
        with open(os.path.join(feat, "STATE.md"), "w") as f:
            f.write(state_md)
    return feat


_I34_TASK = (
    "tasks:\n"
    "  - id: T-01\n"
    "    title: t\n"
    "    change_type: logic\n"
    "    execution_mode: main-session-direct\n"
    "    status: done\n"
    "    files: [a.py]\n"
    "    verify: run it\n"
    "    intent: do it\n"
)


def case_inv34_station_only_is_out_of_scope():
    """FEAT-41 T-19. A station-only record answers neither `is the goal signed` nor `does
    STATE.md name a real task`, because it HAS no goal and no tasks.

    THIS IS SCOPING, NOT A FAIL-OPEN, and the backfill is what forced the distinction: creating
    twelve station-only plans made two checks visible that had skipped those directories for as
    long as they had no plan at all. The alternative was to give each one an `approval:` block,
    which would have FABRICATED twelve signatures nobody gave.
    """
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        _i34_station_only(tmp, "station_only: true\ntasks: []\n",
                          state_md="## Current\nsee T-01 and T-99\n")
        code, out = run(tmp)
        quiet = ("no `approval:` block" not in out) and ("which is absent from its" not in out)
        results.append(("(inv34.c) a station-only plan is exempt from the approval and "
                        "STATE.md-task checks", quiet, out[:400]))
    return results


def case_inv34_a_real_plan_is_still_checked():
    """NEGATIVE CONTROL, and the one that stops the exemption widening. A plan WITH tasks is
    still held to both checks -- if this ever goes quiet, the exemption has swallowed the rule
    for every plan in the tree, which is the failure mode this whole feature keeps finding."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        _i34_station_only(tmp, _I34_TASK, state_md="## Current\nsee T-99\n")
        code, out = run(tmp)
        loud = ("no `approval:` block" in out) and ("T-99" in out)
        results.append(("(inv34.d) a plan WITH tasks is still checked for approval and for "
                        "STATE.md task ids", loud, out[:400]))
    return results


def case_inv34_an_emptied_plan_is_not_station_only():
    """FEAT-41 MF-3, high, proven END TO END by cycle 3's code reviewer.

    A Bash write emptied a SIGNED plan's `tasks:` while keeping its `approval:` and `status:`.
    The old exemption keyed on the ABSENCE of tasks, so the forged document inherited it and a
    real dangling-STATE.md-task violation went SILENT. Cycle 3 also showed the existing control
    was PARTLY VACUOUS -- deleting the exemption line left it green -- and that NO case covered
    this state. This is that case.

    THE FIX MAKES THE FORGED STATE LOUDER, not merely caught: an emptied plan carries no
    `station_only:` marker, so `load_plan` refuses it, and a plan that does not load is already a
    violation. The point is general -- AN ABSENCE CANNOT BE A CREDENTIAL. A checker must be told a
    fact, never infer one from a missing field.
    """
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        feat = _i34_station_only(tmp, _I34_TASK, state_md="## Current\nsee T-99\n")
        plan = os.path.join(feat, "plan.yaml")
        with open(plan, "w") as f:
            f.write("schema: plan/1\nfeature: FEAT-TEST\nstatus: done\n"
                    "approval:\n  status: approved\n  approved_by: X\n  date: 2026-01-01\n"
                    "tasks: []\n")
        code, out = run(tmp)
        # It must NOT go quiet. Either the load refusal or the dangling-task line is acceptable
        # evidence; what is unacceptable is silence, which is what the old keying produced.
        loud = ("does not load" in out) or ("T-99" in out)
        results.append(("(inv34.e) a SIGNED plan emptied to `tasks: []` does NOT inherit the "
                        "station-only exemption", loud, out[:500]))
    return results


def case_inv34_marker_cannot_be_minted_onto_a_real_plan():
    """FEAT-41 HIGH-1, cycle 4, found independently by two reviewers.

    MF-3 made `station_only: true` a credential and validated it in ONE direction only, so the
    marker could be MINTED onto a task-bearing SIGNED plan -- via the ungated `apply` verb or a
    raw Bash write -- durably silencing the approval and STATE.md-task checks for that feature.

    THIS CASE EXISTS BECAUSE A COMMENT CLAIMED IT ALREADY DID. `check-state.sh` cited case
    (inv34.d) as asserting this guarantee; two reviewers checked at source and (inv34.d)'s fixture
    carries NO marker, so the cited test never tested it. A false citation in a comment is worse
    than a missing test, because it stops the next reader looking.
    """
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        feat = _i34_station_only(tmp, _I34_TASK, state_md="## Current\nsee T-99\n")
        plan = os.path.join(feat, "plan.yaml")
        body = open(plan).read()
        # Mint the credential onto the signed, task-bearing plan, exactly as a Bash write would.
        with open(plan, "w") as f:
            f.write("station_only: true\n" + body)
        code, out = run(tmp)
        # It must not go quiet. The load refusal is the expected outcome and is LOUDER than the
        # checks the marker was being used to escape.
        loud = ("does not load" in out) or ("T-99" in out) or ("station_only" in out)
        results.append(("(inv34.f) the station_only marker CANNOT be minted onto a task-bearing "
                        "plan to exempt it", loud, out[:500]))
    return results


def _i35_fixture(tmp, notes_block):
    """A station-only plan.yaml, valid enough that no OTHER invariant fires, carrying
    `notes_block` verbatim as the tail of the file so INV-35's raw-source scan sees exactly
    the line under test."""
    h = make_fixture(tmp, HARNESS_JSON_SYNC_OFF, "  parent: none")
    feat = os.path.join(h, "harness", "features", "FEAT-TEST")
    with open(os.path.join(feat, "plan.yaml"), "w") as f:
        f.write("schema: plan/1\nfeature: FEAT-TEST\nstatus: done\n"
                 "station_only: true\ntasks: []\n" + notes_block)
    return feat


def _i35_lines(out):
    return [l for l in out.splitlines() if "INV-35" in l]


def case_inv35_unquoted_hash_digit_is_reported():
    """issue #251 (inv35.a). THE REPORT. An unquoted scalar mentioning an issue number the
    way a human writes one -- ` #217` -- is exactly the shape YAML's plain-scalar comment
    rule truncates, and this is the case that must not go quiet."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, "notes: close out the fix for #217\n")
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = bool(ls) and any("#217" in l for l in ls) and any(":6" in l for l in ls)
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.a) an unquoted ` #217` is reported, "
              f"naming the line and the number")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def case_inv35_matches_real_truncation():
    """(inv35.b) THE PROOF THIS IS NOT HYPOTHETICAL. The exact fixture (inv35.a) flags,
    loaded through the same harness_yaml module check-state.sh and every other reader use,
    silently drops everything from the `#` onward. If this case ever goes green while
    (inv35.a) still fires, the invariant has drifted from the defect it exists to catch."""
    with tempfile.TemporaryDirectory() as tmp:
        feat = _i35_fixture(tmp, "notes: close out the fix for #217\n")
        sys.path.insert(0, os.path.dirname(SCRIPT))
        import importlib
        harness_yaml_mod = importlib.import_module("harness_yaml")
        doc = harness_yaml_mod.load_file(os.path.join(feat, "plan.yaml"))
        truncated = doc.get("notes") == "close out the fix for"
        print(f"{'ok' if truncated else 'FAIL'} - case (inv35.b) the flagged fixture actually "
              f"loses `#217` when parsed (real={doc.get('notes')!r})")
        return truncated


def case_inv35_quoted_is_silent():
    """(inv35.c) NEGATIVE CONTROL. Quoting the value is the fix the finding tells the operator
    to make, and it must actually satisfy the invariant."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, 'notes: "close out the fix for #217"\n')
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = not ls
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.c) a quoted ` #217` is silent")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def case_inv35_full_line_comment_is_silent():
    """(inv35.d) A line that is ENTIRELY a comment carries no data to lose -- flagging it
    would tell an operator to quote a comment, which YAML has no syntax for."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, "# tracked by #217\n")
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = not ls
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.d) a whole-line comment is silent")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def case_inv35_block_scalar_is_exempt():
    """(inv35.e) A `|` block's content is literal by the YAML spec itself -- a `#` inside it
    is data, never a comment start, so it cannot lose anything and must not be flagged."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, "notes: |\n  close out the fix for #217\n  and nothing else\n")
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = not ls
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.e) a `#` inside a block scalar is silent")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def case_inv35_hash_without_digit_is_silent():
    """(inv35.f) NEGATIVE CONTROL on the narrow trigger. A real trailing comment with a space
    after the `#` -- the ordinary human way to write one -- is not this defect's shape and
    must not be flagged."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, "notes: close out the fix  # see the tracker\n")
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = not ls
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.f) `# text` with no digit is silent")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def case_inv35_digit_inside_an_already_started_comment_is_silent():
    """(inv35.g) REGRESSION. The first unquoted `#` is where YAML's comment actually starts --
    everything after it, including a coincidental `#217` deeper in ordinary commentary, is
    already comment text and loses nothing. An earlier draft of the scanner kept looking past
    the first hash and flagged the second one; this pins the fix."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, "notes: fix the thing # see issue #217 for details\n")
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = not ls
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.g) a digit inside an already-started "
              f"comment is silent")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def case_inv35_apostrophe_before_truncation_still_fires():
    """(inv35.h) REGRESSION -- validator panel finding (harness-code-reviewer, PR #1145).
    A plain scalar's own apostrophes have NO YAML significance once the value has already
    opened unquoted -- only the value's FIRST character can open a quoted scalar. An earlier
    draft toggled `in_quote` on every `'`/`"` anywhere on the line, so an odd count of
    apostrophes before the real truncation point flipped the scanner into treating the actual
    ` #<digit>` as quoted and reporting nothing. Reproduced live against this repo's own
    FEAT-34-worktree-act3-enforced/plan.yaml D-03 at review time -- this fixture is that
    exact shape."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, "notes: the operator's design note for #806 - status Done\n")
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = bool(ls) and any("#806" in l for l in ls)
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.h) an apostrophe before the "
              f"truncation point does not suppress the report")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def case_inv35_coincidental_block_indicator_substring_still_fires():
    """(inv35.i) REGRESSION -- validator panel finding (harness-security-reviewer, PR #1145).
    An earlier draft matched the block-scalar-open pattern with `.search()` over the RAW
    LINE, so a coincidental `key:>value` substring anywhere in ordinary prose (unrelated to
    the line's own `key:` position) was misread as opening a block scalar, and the real
    unquoted truncation earlier on the same line was skipped entirely. The check must be
    anchored to the isolated value, never a substring search over the whole line."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, "notes: fix #217 for the ratio:>5\n")
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = bool(ls) and any("#217" in l for l in ls)
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.i) a coincidental block-indicator "
              f"substring does not suppress a real truncation earlier on the line")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def case_inv35_quoted_key_still_fires():
    """(inv35.j) REGRESSION -- validator panel finding, cycle 2 (harness-code-reviewer, PR
    #1145). `_KEY_PREFIX` originally recognised only a bare-identifier key, so a QUOTED key
    (`"my-key": value #217`) fell through the optional key group untouched, and
    `_unquoted_hash_digit` then read the key's own opening quote as the value's first
    character, tracked to the key's own closing quote, and returned None -- silently
    swallowing the real truncation that followed. `_KEY_PREFIX` now recognises a
    double-quoted, single-quoted, or hyphenated-identifier key as well as a bare one."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, '"my-key": value for the record #217\n')
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = bool(ls) and any("#217" in l for l in ls)
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.j) a quoted key does not suppress a "
              f"real truncation in its value")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def case_inv35_hyphenated_key_block_scalar_is_exempt():
    """(inv35.k) SIBLING of (inv35.j), same root cause. An unquoted key containing a hyphen
    (`my-key: |`) was not recognised by `_KEY_PREFIX` either, which left the whole line
    un-stripped and made the block-scalar-open check miss it -- a false POSITIVE risk on the
    block's own content lines rather than a silence, but the identical seam."""
    with tempfile.TemporaryDirectory() as tmp:
        _i35_fixture(tmp, "my-key: |\n  close out the fix for #217\n  and nothing else\n")
        code, out = run(tmp)
        ls = _i35_lines(out)
        ok = not ls
        print(f"{'ok' if ok else 'FAIL'} - case (inv35.k) a hyphenated key's block scalar is "
              f"recognised and exempt")
        if not ok:
            print(f"        {out[:400]}")
        return ok


def _report(results):
    """The original main()'s printer for the cases that return a results LIST."""
    ok = True
    for name, passed, detail in results:
        print(f"{'ok' if passed else 'FAIL'} - case {name}")
        if not passed:
            ok = False
            print(f"        {str(detail).strip()[:300]}")
    return ok


def main():
    results = []
    results.append(case_h())
    results.append(case_i())
    results.append(case_j())
    results.append(case_l())
    results.append(case_n())
    results.append(case_inv35_unquoted_hash_digit_is_reported())
    results.append(case_inv35_matches_real_truncation())
    results.append(case_inv35_quoted_is_silent())
    results.append(case_inv35_full_line_comment_is_silent())
    results.append(case_inv35_block_scalar_is_exempt())
    results.append(case_inv35_hash_without_digit_is_silent())
    results.append(case_inv35_digit_inside_an_already_started_comment_is_silent())
    results.append(case_inv35_apostrophe_before_truncation_still_fires())
    results.append(case_inv35_coincidental_block_indicator_substring_still_fires())
    results.append(case_inv35_quoted_key_still_fires())
    results.append(case_inv35_hyphenated_key_block_scalar_is_exempt())
    results.append(case_p())
    results.append(case_q())
    results.append(case_inv6_plan_run_is_exempt())
    results.append(case_inv6_code_run_still_fires())
    results.append(case_inv6_unknown_grade_fails_closed())
    results.append(case_inv6_mixed_runs_still_fire())
    results.append(case_inv6_exempt_survives_signature())
    results.append(case_inv6_pinned_plan_run_silent())
    results.append(case_inv6_case_variant_is_not_exempt())
    results.append(case_inv6_message_names_the_remedy())
    results.append(case_inv6_producer_is_documented())
    results.append(_report(
        case_inv34_plan_required()
            + case_inv34_present_is_silent()
            + case_inv34_station_only_is_out_of_scope()
            + case_inv34_a_real_plan_is_still_checked()
            + case_inv34_an_emptied_plan_is_not_station_only()
            + case_inv34_marker_cannot_be_minted_onto_a_real_plan()
    ))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
