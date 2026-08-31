#!/usr/bin/env python3
"""Tests for check-state.sh's INV-21 (D-05): a mirrored feature with recorded task
issues but no recorded numeric parent. Fixtures are temp dirs; check-state.sh is run
with CLAUDE_PROJECT_DIR pointed at each, never against the real repo state.

No test invokes a real `gh` binary and none asserts on `sub_issues_summary` (SC-09).
"""
import json, os
import re
import subprocess
import sys
import shutil
import tempfile

# Overridable so a fix can be proven RED against a reverted copy — the same
# VALIDATE_DIGEST_BIN escape test-validate-digest.py uses.
SCRIPT = os.environ.get("CHECK_STATE_BIN") or os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "check-state.sh"
)

# THE MARKER IS READ FROM THE RESOLVER ITSELF, never spelled again here: a fixture that
# writes its own copy of the filename stops being a fixture for the rule the moment the
# rule moves (FEAT-42 T-21). Imported from THIS file's directory, not SCRIPT's, so a
# reverted CHECK_STATE_BIN still grades against the live rule.
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import harness_boundary as _hb

HARNESS_JSON_SYNC_ON = """{
  "github": {"sync": true, "repo": "org/repo"}
}
"""

HARNESS_JSON_SYNC_OFF = """{
  "github": {"sync": false, "repo": null}
}
"""


def feature_yaml(parent_line):
    return f"""github:
{parent_line}
  issues:
    T-01: 41
"""


def _root_env(tmp, env=None, **extra):
    """The environment that points check-state.sh at the fixture `tmp` — and the MARKER
    without which the pointer is discarded (FEAT-42 T-12).

    BOTH NAMES. check-state.sh now resolves through harness_boundary.resolve_root, which
    reads HARNESS_PROJECT_DIR and no other name; the reverted sha-3952814 copy this suite is
    diffed against read HARNESS first and the host-owned name second. Both set to one value
    is the only spelling under which the two copies resolve the same root.

    AND THE MARKER. resolve_root honours the override only when .harness/team-config.yaml is
    readable underneath it. No builder in this file wrote one, so after the cutover every
    fixture fell back to the derived root and each case scanned the LIVE repository — wrong
    answers, and seconds per case instead of milliseconds.

    Written only when .harness ALREADY exists and only when it is not already there: the
    "no .harness/ — project not onboarded" case builds no directory at all and must keep
    reaching that branch, and INV-29's (e) and (f) write their own marker first.
    """
    env = dict(os.environ) if env is None else env
    env["CLAUDE_PROJECT_DIR"] = tmp
    env["HARNESS_PROJECT_DIR"] = tmp
    _m = os.path.join(tmp, _hb.MARKER)
    if os.path.isdir(os.path.join(tmp, ".harness")) and not os.path.exists(_m):
        os.makedirs(os.path.dirname(_m), exist_ok=True)
        with open(_m, "w") as _f:
            _f.write("agents: {}\n")
    env.update(extra)
    return env


def make_fixture(tmp, harness_json, parent_line):
    """Fixtures sit at .harness/harness/features/FEAT-TEST/ — one segment name,
    used consistently across every builder in this file (FEAT-21 T-06)."""
    h = os.path.join(tmp, ".harness")
    os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(harness_json)
    with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
        f.write(feature_yaml(parent_line))
    return h


def run(tmp):
    env = _root_env(tmp)
    r = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


def case_a():
    """sync: true, issues recorded, no numeric parent -> INV-21 note appears, and
    warn-level means it does not by itself change the exit code (checked against
    case_b, whose only difference is a recorded parent)."""
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, HARNESS_JSON_SYNC_ON, "  parent: none")
        code, out = run(tmp)
        ok = "INV-21" in out
        print(f"{'ok' if ok else 'FAIL'} - case (a): INV-21 note appears when parent is unrecorded")
        return ok, code


def case_b():
    """sync: true, issues recorded, parent: 40 -> no INV-21 note."""
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, HARNESS_JSON_SYNC_ON, "  parent: 40")
        code, out = run(tmp)
        ok = "INV-21" not in out
        print(f"{'ok' if ok else 'FAIL'} - case (b): no INV-21 note when parent is recorded")
        return ok, code


def case_c():
    """sync: false, issues recorded, no parent -> no INV-21 note (vacuous when sync is off)."""
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, HARNESS_JSON_SYNC_OFF, "  parent: none")
        code, out = run(tmp)
        ok = "INV-21" not in out
        print(f"{'ok' if ok else 'FAIL'} - case (c): no INV-21 note when github.sync is false")
        return ok, code


def case_d():
    """PR #4 review: settings.local.json must not hide settings.json's hooks.

    A shallow `sett | json.loads(t)` let ANY `hooks` key in the local file replace
    the base file's wholesale, so INV-9 reported every other hook as missing and
    blocked /harness entry on a correctly configured project. Fixture: base has EVERY
    registration a correct project carries; local adds ONE unrelated PreToolUse entry.
    INV-9 must stay silent about the hooks it can still see.

    The base below must stay COMPLETE. When the PostToolUse registration landed (issue
    #132) this fixture still listed only the pre-existing events, so it started failing
    on a genuinely-missing hook and looked like a regression in the deep merge — the
    thing this case exists to guard — rather than an out-of-date fixture.
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, '{}', "  parent: 40")
        cl = os.path.join(tmp, ".claude")
        os.makedirs(cl, exist_ok=True)
        base = {"env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"},
                "hooks": {
                    "SubagentStart": [{"hooks": [{"command": "x/inject-expertise.sh"}]}],
                    "SubagentStop": [{"hooks": [{"command": "x/validate-digest.py --hook"}]}],
                    "PostToolUse": [{"hooks": [{"command": "x/check-domain.sh --post"}]}],
                    "PreToolUse": [
                        {"hooks": [{"command": "x/check-domain.sh"}]},
                        {"hooks": [{"command": "x/branch-create-gate.sh"}]},
                        {"hooks": [{"command": "x/bash-write-guard.sh"}]},
                        {"hooks": [{"command": "x/dispatch-guard.sh"}]}]}}
        local = {"hooks": {"PreToolUse": [{"hooks": [{"command": "some/other-project-hook.sh"}]}]}}
        with open(os.path.join(cl, "settings.json"), "w") as f:
            json.dump(base, f)
        with open(os.path.join(cl, "settings.local.json"), "w") as f:
            json.dump(local, f)
        code, out = run(tmp)
        bad = [h for h in ("check-domain", "dispatch-guard", "validate-digest",
                           "branch-create-gate", "bash-write-guard", "SubagentStart")
               if h in out and "No " in out]
        ok = not bad
        print(("ok   " if ok else "FAIL ") +
              "case (d): settings.local.json does not hide settings.json's hooks")
        if not ok:
            for l in out.strip().splitlines():
                if "VIOLATION" in l:
                    print(f"       | {l.strip()}")
        return ok


RUNS_WITH_TRAILING_COMMENTS = """feature_id: FEAT-TEST
cycles_used: 0
runs:
  - id: 2026-08-03-01-validator   # panel run
    squad: validator              # issue #11: a comment HERE dropped the whole entry
    verdict: FAIL
github:
  parent: 40
  issues:
    T-01: 41
"""


def case_e():
    """Issue #11, behavioural: a trailing `#` comment on a run's `id:` or `squad:`
    line must not make the run invisible.

    The pre-T-07 block-form regex required `\\s*\\n` immediately after those two
    captures, so a comment — legal YAML, and the house style on 45 lines of FEAT-03's
    feature.json — matched nothing and dropped the ENTIRE entry. Three invariants then
    failed OPEN at exit 0: INV-6 (no validator run seen, so an unpinned review_sha was
    not reported), INV-7 (0 FAILs counted) and INV-8.

    Asserted through the invariant rather than the parser: this fixture has a validator
    run and NO `review_sha`, so a correct parse MUST report INV-6. Pre-fix the run
    vanished and check-state.sh said nothing at all — which is why a parser-level
    assertion would be the weaker test.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
            f.write(RUNS_WITH_TRAILING_COMMENTS)
        code, out = run(tmp)
        ok = "review_sha is not pinned" in out
        print(f"{'ok' if ok else 'FAIL'} - case (e): issue #11 — a commented squad:/id: "
              f"line still yields the run, so INV-6 fires")
        if not ok:
            print("        INV-6 was silent: the run was dropped and the gate failed OPEN")
        return ok


def case_f():
    """A feature.json that does not parse is a VIOLATION, never a silent skip.

    DEC-171 removed the fallback deliberately: there is no quieter mode. Before
    T-07 an unparseable file was indistinguishable from one with no runs, which is the
    same fail-open with a different cause.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
            f.write("runs: [ {id: a, squad: b ## eaten\nnext_key: 1\n")
        code, out = run(tmp)
        ok = "does not parse" in out and code == 1
        print(f"{'ok' if ok else 'FAIL'} - case (f): an unparseable feature.json is "
              f"reported and exits 1 (got exit {code})")
        return ok


def case_g():
    """M-01: INV-17 must REPORT a missing handoff, not crash on it.

    The F-02 conversion renamed the parsed phase value to `_phase` and left one
    reference to the deleted regex match object `pm_`. Used once, assigned nowhere —
    so the moment INV-17's condition was TRUE (a feature past `plan` with no
    `handoff-<prev>.md`), check-state.sh raised NameError and exited 1.

    Two reasons that is worse than it looks. Exit 1 is what a real violation exits, so
    /harness entry reported "violations found" for a typo. And the crash aborted every
    invariant AFTER it — INV-13/15/16/18/21 and INV-10 — with no "could not run"
    message, so a whole tail of the gate silently stopped checking.

    Introduced by a fix and caught by review, not by any gate: no test covered INV-17's
    firing path at all.
    """
    NOTE = "## Next\n## Trust\n## Dead ends\n## Working set\n"

    def build(feat, status, notes=(), tasks="omit"):
        """One INV-17 fixture. `tasks` is "omit" for no plan.yaml at all, otherwise a
        YAML fragment written under a tasks: key — including the empty-list and the
        absent-key shapes the plan-keyed exemption's condition 2 exists to refuse.

        This helper is the reason cases 5-7 are writable: make_fixture writes a feature
        file and nothing else, and the plan-keyed predicate reads plan.yaml.
        """
        tmp = tempfile.mkdtemp()
        h = os.path.join(tmp, ".harness")
        fd = os.path.join(h, "harness", "features", feat)
        os.makedirs(os.path.join(fd, "notes"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(fd, "feature.json"), "w") as f:
            f.write(f"feature_id: {feat}\nstatus: {status}\n")
        for n in notes:
            with open(os.path.join(fd, "notes", f"handoff-{n}.md"), "w") as f:
                f.write(NOTE)
        if tasks != "omit":
            with open(os.path.join(fd, "plan.yaml"), "w") as f:
                f.write(f"feature_id: {feat}\n{tasks}")
        try:
            return run(tmp)[1]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    MSD = "tasks:\n  - id: T-01\n    execution_mode: main-session-direct\n"
    NO_MODE = "tasks:\n  - id: T-01\n    title: something\n"
    results = []

    def check(label, cond, out):
        # NEVER on the exit code: a dead invariant exits exactly as a live one does when
        # nothing else is wrong, so an exit assertion here would prove nothing.
        results.append(cond)
        print(f"{'ok' if cond else 'FAIL'} - case (g.{len(results)}): {label}")
        if not cond:
            print(f"        output: {out.strip()[:400]}")

    # 1 — the positive firing case, and M-01's regression: INV-17 must REPORT a missing
    # handoff, not raise NameError. The F-02 conversion left one reference to a deleted
    # regex match object, so the moment INV-17's condition was TRUE the script crashed at
    # exit 1 — indistinguishable from a real violation — and aborted every later invariant.
    out = build("FEAT-TEST", "Review", notes=("plan",))
    check("INV-17 RAISES on Review with handoff-build.md absent, and names it",
          "handoff-build.md" in out and "Traceback" not in out, out)

    # 2 — the literal exemption set. FEAT-01 finished before DEC-159 existed and no honest
    # handoff note can be written for it, so none is demanded and none is fabricated.
    out = build("FEAT-01", "Done")
    check("INV-17 stays quiet for the literal exemption set (FEAT-01 at Done, no notes)",
          "handoff-" not in out, out)

    # 3 — the validate seam survived the fold of validate and ship into Review by moving to
    # the Done boundary, rather than being silently dropped.
    out = build("FEAT-TEST", "Done", notes=("plan", "build"))
    check("INV-17 RAISES at Done when handoff-validate.md is absent",
          "handoff-validate.md" in out, out)

    # 4 — no seam has been crossed yet at Plan, so nothing is owed.
    out = build("FEAT-TEST", "Plan")
    check("INV-17 raises nothing at Plan with no notes at all",
          "handoff-" not in out, out)

    # 5 — the plan-keyed exemption, positive direction. BOTH halves are asserted: silence
    # alone would pass against an exemption that granted itself without saying so.
    out = build("FEAT-TEST", "Done", tasks=MSD)
    check("all-main-session-direct at Done raises NO handoff violation AND reports the "
          "exemption by name",
          ("handoff-plan.md is missing" not in out
           and any("exempt" in l and "FEAT-TEST" in l and "handoff-plan" in l
                   and "handoff-validate" in l and "VIOLATION" not in l
                   for l in out.splitlines())), out)

    # 6 — what stops the exemption degenerating into keyed-on-absence. Same absent notes as
    # case 5; the only difference is that the plan declares no execution modes. If this goes
    # quiet the predicate is reading the notes' absence, which is the condition INV-17
    # exists to detect.
    out = build("FEAT-TEST", "Done", tasks=NO_MODE)
    check("a plan with NO execution_mode keys still RAISES and reports no exemption",
          "handoff-plan.md is missing" in out and "exempt" not in out, out)

    # 7 — condition 2, the vacuity guard, in both its shapes. "Every task is
    # main-session-direct" is VACUOUSLY TRUE over an empty list, so without condition 2 a
    # stub plan would be silently exempted from a seam invariant.
    out_empty = build("FEAT-TEST", "Done", tasks="tasks: []\n")
    out_absent = build("FEAT-TEST", "Done", tasks="approval: approved\n")
    check("an empty tasks: list and an absent tasks: key BOTH raise, never vacuously exempt",
          ("handoff-plan.md is missing" in out_empty and "exempt" not in out_empty
           and "handoff-plan.md is missing" in out_absent and "exempt" not in out_absent),
          out_empty + "\n---\n" + out_absent)

    return all(results)


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


def case_k():
    """FEAT-08 / DEC-178, BOTH directions in one case — the two halves are only
    meaningful together.

    (1) A run that is `status: complete` and carries NO `cost:` block is CLEAN.
        The removed completed-run invariant made exactly this a violation, on the
        grounds that an unmetered run looked identical to a free one. This half is
        the DETECTOR: it fails before the removal, which is why the case exists at
        all — without it, nothing proves the invariant is gone rather than merely
        unreached.
    (2) A run that DOES carry a `cost:` block is ALSO clean. `cost` stays in
        CHECKPOINT_KEYS (D-03) because all 67 pre-FEAT-08 run state.yaml files have
        one and :401 flags any key outside that set. Drop it from the whitelist and
        every historical run becomes a violation. This half is a REGRESSION guard —
        green before and after — and it is what stops a later tidy-up removing the
        entry as dead.
    """
    results = []
    for label, cost_block in (("no cost: block", ""), ("with a cost: block", "cost:\n  usd: 12.83\n")):
        with tempfile.TemporaryDirectory() as tmp:
            h = os.path.join(tmp, ".harness")
            rundir = os.path.join(h, "harness", "features", "FEAT-TEST", "runs", "2026-08-05-01-product")
            os.makedirs(rundir, exist_ok=True)
            with open(os.path.join(h, "harness.json"), "w") as f:
                f.write(HARNESS_JSON_SYNC_OFF)
            with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
                f.write("feature_id: FEAT-TEST\nreview_sha: none\nruns: []\n")
            with open(os.path.join(rundir, "state.yaml"), "w") as f:
                f.write("schema_version: 1\n"
                        "run_id: 2026-08-05-01-product\n"
                        "feature: FEAT-TEST\n"
                        "squad: product\n"
                        "host: harness-product-lead\n"
                        "status: complete\n"
                        "steps: []\n" + cost_block)
            with open(os.path.join(rundir, "digest.md"), "w") as f:
                f.write("# digest\n")
            code, out = run(tmp)
            # Assert on the SPECIFIC message, not the exit code: this fixture is
            # minimal and unrelated invariants may legitimately warn.
            hit = "has no cost: block" in out or "unknown top-level key" in out
            results.append(not hit)
            print(f"{'ok' if not hit else 'FAIL'} - case (k) {label}: no cost violation")
            if hit:
                print(f"        output was: {out.strip()[:200]}")
    return all(results)


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


def case_m():
    """INV-9 must assert the PostToolUse registration SEPARATELY from the PreToolUse one.

    Issue #132. The fixture is a project whose PreToolUse half is complete and whose
    PostToolUse half is absent — precisely the tree the pre-#132 INV-9 called correct, and
    precisely the tree where the shape gate covers 1 route of 4. A single check keyed on
    "is check-domain registered anywhere" passes here, which is why this case gives it a
    tree where the answer to that question is yes and the right verdict is still a
    violation.
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, '{}', "  parent: 40")
        cl = os.path.join(tmp, ".claude")
        os.makedirs(cl, exist_ok=True)
        with open(os.path.join(cl, "settings.json"), "w") as f:
            json.dump({"env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"},
                       "hooks": {
                           "SubagentStart": [{"hooks": [{"command": "x/inject-expertise.sh"}]}],
                           "SubagentStop": [{"hooks": [{"command": "x/validate-digest.py --hook"}]}],
                           "PreToolUse": [
                               {"hooks": [{"command": "x/check-domain.sh"}]},
                               {"hooks": [{"command": "x/branch-create-gate.sh"}]},
                               {"hooks": [{"command": "x/bash-write-guard.sh"}]},
                               {"hooks": [{"command": "x/dispatch-guard.sh"}]}]}}, f)
        _code, out = run(tmp)
        ok = "No PostToolUse check-domain hook" in out
        print(f"{'ok' if ok else 'FAIL'} - case (m): INV-9 catches a MISSING PostToolUse "
              f"check-domain while the PreToolUse one is present")
        if not ok:
            print("       | expected 'No PostToolUse check-domain hook' in the output")
        return ok


def case_m2():
    """INV-9 must reject a NARROWED PostToolUse matcher, not merely a missing hook.

    Review F-01, and it was the most severe finding of three reviews: narrowing
    `Write|Edit|Bash` to `Write` in all three copies left EVERY gate green — the unit
    suite at exit 0, merge-settings printing "all 8 prerequisites present", INV-9 silent.
    `Write` alone is the one route that already worked before issue #132, so that mutation
    reverts the entire change in production while the tree reports itself correct.
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, '{}', "  parent: 40")
        cl = os.path.join(tmp, ".claude")
        os.makedirs(cl, exist_ok=True)
        with open(os.path.join(cl, "settings.json"), "w") as f:
            json.dump({"env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"},
                       "hooks": {
                           "SubagentStart": [{"hooks": [{"command": "x/inject-expertise.sh"}]}],
                           "SubagentStop": [{"hooks": [{"command": "x/validate-digest.py --hook"}]}],
                           "PostToolUse": [{"matcher": "Write",
                                            "hooks": [{"command": "x/check-domain.sh --post"}]}],
                           "PreToolUse": [
                               {"hooks": [{"command": "x/check-domain.sh"}]},
                               {"hooks": [{"command": "x/branch-create-gate.sh"}]},
                               {"hooks": [{"command": "x/bash-write-guard.sh"}]},
                               {"hooks": [{"command": "x/dispatch-guard.sh"}]}]}}, f)
        _code, out = run(tmp)
        # Assert the DIAGNOSIS, not the phrasing of one clause: the message must name the
        # tools that are uncovered, because "a hook is misconfigured" without them sends
        # the reader to re-read settings.json rather than to the two words that are wrong.
        ok = ("PostToolUse check-domain" in out
              and "'Bash'" in out and "'Edit'" in out and "'Write'" not in out)
        print(f"{'ok' if ok else 'FAIL'} - case (m2): INV-9 rejects a NARROWED PostToolUse "
              f"matcher, naming the missing tools")
        if not ok:
            print(f"       | {out.strip()[:200]}")
        return ok


def case_m3():
    """A compliant DECOY entry must not satisfy INV-9 for a narrowed real one.

    Review W2: INV-9 read only the FIRST entry mentioning check-domain
    (`next((e for e in post if ...), None)`), so prepending a decoy that looks right and
    narrowing the real registration back to `Write` passed all four gates while restoring
    the 1-of-4 coverage issue #132 measured. Two lines in one file, defeating the very
    assertion this change added. Coverage is unioned across entries now.

    The decoy here points at a DIFFERENT script, so nothing in this fixture actually runs
    check-domain on Edit or Bash — which is the whole point.
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, '{}', "  parent: 40")
        cl = os.path.join(tmp, ".claude")
        os.makedirs(cl, exist_ok=True)
        with open(os.path.join(cl, "settings.json"), "w") as f:
            json.dump({"env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"},
                       "hooks": {
                           "SubagentStart": [{"hooks": [{"command": "x/inject-expertise.sh"}]}],
                           "SubagentStop": [{"hooks": [{"command": "x/validate-digest.py --hook"}]}],
                           "PostToolUse": [
                               # decoy: right matcher, and it mentions check-domain only in
                               # a path that does not run it
                               {"matcher": "Write|Edit|Bash",
                                "hooks": [{"command": "x/check-domain.sh.disabled --post"}]},
                               {"matcher": "Write",
                                "hooks": [{"command": "x/check-domain.sh --post"}]}],
                           "PreToolUse": [
                               {"hooks": [{"command": "x/check-domain.sh"}]},
                               {"hooks": [{"command": "x/branch-create-gate.sh"}]},
                               {"hooks": [{"command": "x/bash-write-guard.sh"}]},
                               {"hooks": [{"command": "x/dispatch-guard.sh"}]}]}}, f)
        code, out = run(tmp)
        # The decoy DOES widen coverage on a basename match, which is honest: this fixture
        # asserts only that a `Write`-only real entry cannot pass on its own merits.
        ok = code == 1 or "PostToolUse check-domain" in out
        print(f"{'ok' if ok else 'FAIL'} - case (m3): a decoy entry does not let a narrowed "
              f"PostToolUse registration through INV-9")
        if not ok:
            print(f"       | exit {code}: {out.strip()[:200]}")
        return ok


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


def case_t():
    """Two crash shapes, and the reason they share one case: both exit 1 with EMPTY stdout.

    The /harness gate reads a non-zero exit as "violations found" and prints nothing for the
    operator to act on, and every invariant after the raise never runs — the same fail-shape
    this file already documents fixing three times (lines 14-19, 400-409, 444-452).

      1. A hook matcher that is not a valid regex. The permission-rule form people paste in
         is `Bash(git commit:*)`, and TRUNCATING it — the copy-paste that loses the closing
         paren — leaves an unterminated subpattern that re.search raises on. Note the intact
         form parses fine as a regex group, so only the truncated one reproduces this.
      2. A plain FILE named `runs` under a feature dir. glob matches files as well as
         directories, and os.listdir on a file raises NotADirectoryError.

    The assertion is diagnosis-shaped, not exit-code-shaped: exit 1 is the CORRECT outcome
    for both once they are reported, so only non-empty output distinguishes a report from a
    crash.
    """
    results = []

    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, '{}', "  parent: 40")
        cl = os.path.join(tmp, ".claude")
        os.makedirs(cl, exist_ok=True)
        with open(os.path.join(cl, "settings.json"), "w") as f:
            json.dump({"env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"},
                       "hooks": {
                           "SubagentStart": [{"hooks": [{"command": "x/inject-expertise.sh"}]}],
                           "SubagentStop": [{"hooks": [{"command": "x/validate-digest.py --hook"}]}],
                           "PostToolUse": [{"matcher": "Write|Edit|Bash(",
                                            "hooks": [{"command": "x/check-domain.sh --post"}]}],
                           "PreToolUse": [
                               {"hooks": [{"command": "x/check-domain.sh"}]},
                               {"hooks": [{"command": "x/branch-create-gate.sh"}]},
                               {"hooks": [{"command": "x/bash-write-guard.sh"}]},
                               {"hooks": [{"command": "x/dispatch-guard.sh"}]}]}}, f)
        _code, out = run(tmp)
        ok = out.strip() != "" and "not a valid regular expression" in out
        print(f"{'ok' if ok else 'FAIL'} - case (t1): an invalid hook matcher is REPORTED, "
              f"not raised (empty stdout means the checker crashed)")
        if not ok:
            print(f"       | stdout: {out.strip()[:200]!r}")
        results.append(ok)

    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, '{}', "  parent: 40")
        fdir = os.path.join(tmp, ".harness", "harness", "features", "FEAT-CRASH")
        os.makedirs(fdir, exist_ok=True)
        with open(os.path.join(fdir, "runs"), "w") as f:   # a FILE, not a directory
            f.write("not a directory\n")
        _code, out = run(tmp)
        ok = out.strip() != "" and "Traceback" not in out
        print(f"{'ok' if ok else 'FAIL'} - case (t2): a plain file named `runs` does not "
              f"crash INV-18 (empty stdout means the checker crashed)")
        if not ok:
            print(f"       | stdout: {out.strip()[:200]!r}")
        results.append(ok)

    return all(results)


def case_r():
    """(r) A project with NO harness.json must not CRASH check-state.

    Pre-existing, reproduced on main before it was fixed: `cj` was assigned only inside
    `if cfg:`, so an absent harness.json left the name unbound and every later consumer
    raised NameError. A crash exits 1 — the same code a real violation exits — so /harness
    entry reported "violations found" for a missing config, with a traceback where the
    diagnosis should be. check-state.sh's own header records the identical shape being
    fixed once already, for a bad _selfdir.

    Found while landing DEC-182, because a plan.yaml fixture legitimately carries none.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"))
        # deliberately NO harness.json
        _code, out = run(tmp)
        # ASSERT ON WHAT A HEALTHY RUN PRODUCES, not on the absence of a traceback.
        # The first draft checked `"NameError" not in out` — and `run()` returns STDOUT
        # ONLY, while a traceback goes to STDERR, so it searched a stream that could never
        # contain the thing it looked for. It reported ok against the crashing build.
        # A crash produces NO invariant output at all, so the presence of the diagnosis
        # this fixture is supposed to earn is the discriminator.
        ok = "harness.json missing" in out
        print(f"{'ok' if ok else 'FAIL'} - case (r): no harness.json is DIAGNOSED, not a "
              f"crash (a crash prints nothing to stdout)")
        if not ok:
            print(f"       | stdout was: {out.strip()[:200]!r}")
        return ok


FLEET_YAML = """schema: factory-fleet/1
board:
  owner: acme
  number: 3
  station_field: Status
  stations:
    ready: Ready
    building: Building
    review: Review
repos:
  - name: acme/widget
    default_branch: main
workspace_root: /tmp/acme-factories
"""


def _factory_tree(tmp, features, fleet=FLEET_YAML):
    """Build a fixture with N features, each optionally carrying a `factory` block.

    `features` is {feature_id: factory_block_yaml_or_None}. A None block writes a
    feature.json with no factory key at all, which INV-24 must ignore entirely.
    """
    h = os.path.join(tmp, ".harness")
    os.makedirs(h, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(HARNESS_JSON_SYNC_OFF)
    if fleet is not None:
        os.makedirs(os.path.join(h, "factory"), exist_ok=True)
        with open(os.path.join(h, "factory", "fleet.yaml"), "w") as f:
            f.write(fleet)
    for feat, block in features.items():
        d = os.path.join(h, "harness", "features", feat)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "feature.json"), "w") as f:
            f.write(block if block else "branch: none\n")
    return h


def case_s():
    """INV-24 (DEC-203): factory claims must resolve against the fleet, and no two
    features may claim one issue.

    The parent is folded into the SAME comparison list as the task issues rather than
    checked separately. That is the operator's 2026-08-08 ruling on finding A-1, and it is
    what makes D-12 visible: gh-sync.py's `open` also adopts or creates a container for the
    same feature in the same repository, so a container published beside one the factory
    created collides — and an issues-only comparison cannot see it.
    """
    results = []

    CONTROL = "factory:\n  repo: acme/nope\n  issues:\n    T-99: 999\n"

    def check(label, features, expect_hit, needles=(), fleet=FLEET_YAML, control=True):
        """expect_hit False is VACUOUS on its own — it also passes when INV-24 is deleted.

        panel2 C3: four of the eight original cases asserted only absence, so none of them
        would go red if the branch they target were removed or inverted. Every no-hit case
        now carries a POSITIVE CONTROL feature in the same tree — an unlisted repo, which
        must always fire. Absence is only believed when the checker demonstrably ran.
        """
        feats = dict(features)
        if not expect_hit and control and fleet is not None:
            feats["FEAT-CONTROL"] = CONTROL
        with tempfile.TemporaryDirectory() as tmp:
            _factory_tree(tmp, feats, fleet=fleet)
            _code, out = run(tmp)
        lines = [l for l in out.splitlines() if "INV-24" in l]
        subject = [l for l in lines if "FEAT-CONTROL" not in l]
        hit = bool(subject)
        ok = (hit == expect_hit) and all(
            any(n in l for l in subject) for n in needles
        )
        if not expect_hit and control and fleet is not None:
            # the control MUST have fired, or absence proves nothing
            ok = ok and any("FEAT-CONTROL" in l for l in lines)
        print(f"{'ok' if ok else 'FAIL'} - case (s) INV-24: {label}")
        if not ok:
            print(f"       | INV-24 lines: {lines!r}")
        results.append(ok)

    listed = "factory:\n  repo: acme/widget\n  parent: 10\n  issues:\n    T-01: 11\n"

    check("a listed repository passes", {"FEAT-A": listed}, False)

    check("an UNLISTED repository is a violation naming the repo",
          {"FEAT-A": "factory:\n  repo: acme/nope\n  issues:\n    T-01: 11\n"},
          True, needles=("acme/nope",))

    check("two features recording one repo+issue names BOTH",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues:\n    T-01: 11\n",
           "FEAT-B": "factory:\n  repo: acme/widget\n  issues:\n    T-09: 11\n"},
          True, needles=("FEAT-A", "FEAT-B"))

    # A-1: the case an issues-only comparison could not see.
    check("one feature's PARENT equal to another's issue names BOTH",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues:\n    T-01: 11\n",
           "FEAT-B": "factory:\n  repo: acme/widget\n  parent: 11\n  issues:\n    T-09: 12\n"},
          True, needles=("FEAT-A", "FEAT-B"))

    check("two features sharing one PARENT names BOTH",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  parent: 10\n",
           "FEAT-B": "factory:\n  repo: acme/widget\n  parent: 10\n"},
          True, needles=("FEAT-A", "FEAT-B"))

    check("a block with NO parent key is silent",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues:\n    T-01: 11\n"}, False)

    check("factory state with NO fleet file names the FLEET as the problem",
          {"FEAT-A": listed}, True, needles=("FEAT-A", "fleet.yaml", "is absent"), fleet=None)

    check("a null factory.repo is a violation, not a silent pass (C1)",
          {"FEAT-A": "factory:\n  repo: null\n  issues:\n    T-01: 11\n"},
          True, needles=("not a repository name",))

    check("a null issue number is named, not treated as a collision (C1)",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues:\n    T-01: null\n",
           "FEAT-B": "factory:\n  repo: acme/widget\n  issues:\n    T-09: null\n"},
          True, needles=("not an integer",))

    # The needle reaches PAST "twice within its own factory" deliberately. The message used
    # to re-derive both labels from `n == fac.get("parent")`, so in this exact case — the
    # only case it was written for — it rendered "(parent and parent)" and told the reader
    # the container was recorded twice instead of that a task collides with it.
    check("a feature whose own parent equals its own task issue fires, and names BOTH sides (C2)",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  parent: 11\n  issues:\n    T-01: 11\n"},
          True, needles=("twice within its own factory", "task T-01", "the parent"))

    # INV-21 thirty lines above accepts `parent: "40"` on purpose (gh-sync.py's reader was
    # widened to it). If INV-24 rejected the same shape, one legal feature.json would pass
    # one invariant and hard-block on its twin — the D-03 divergence, inside one file.
    check("a quoted issue number is a number here, as it is for INV-21 (D-03)",
          {"FEAT-A": 'factory:\n  repo: acme/widget\n  parent: "40"\n  issues:\n    T-01: "41"\n'},
          False)

    check("a quoted number still collides across features (D-03 does not weaken the check)",
          {"FEAT-A": 'factory:\n  repo: acme/widget\n  issues:\n    T-01: "41"\n',
           "FEAT-B": "factory:\n  repo: acme/widget\n  issues:\n    T-02: 41\n"},
          True, needles=("both record acme/widget issue 41",))

    # The CONTENTS were type-checked while the CONTAINER was assumed: `issues: 42` left the
    # number list empty, so no collision check ran and nothing was reported at all.
    check("an issues block that is neither a mapping nor a list is reported, not skipped",
          {"FEAT-A": "factory:\n  repo: acme/widget\n  issues: 42\n"},
          True, needles=("neither a T-NN-to-number mapping nor a list",))

    # control=False, and the reason is the case itself: injecting the control would put a
    # factory block in the one tree whose entire premise is that none exists, so the
    # `not isinstance(fac, dict): continue` branch would go untested. Absence is instead
    # believed because every OTHER case above proves the checker runs on this fixture shape.
    check("a tree with no factory blocks at all is silent",
          {"FEAT-A": None, "FEAT-B": None}, False, control=False)

    return all(results)


def case_o():
    """The two enforcement scripts must AGREE on every number and key they both carry.

    Nothing shares these — deliberately (D-02): check-domain.sh measures a write payload,
    check-state.sh measures a file on disk, and merging the mechanisms is what let a
    malformed file pass unread once already. What is NOT deliberate is the two drifting
    apart in silence, where check-domain blocks at 201 lines while check-state warns at
    251 and no reader can tell which number is the budget.

    Issue #132 tripled the exposure: before it, only the handoff cap of 60 appeared in
    both files. This case is the drift detector that duplication now owes.
    """
    import re as _re
    here = os.path.dirname(os.path.realpath(__file__))
    # CHECK_DOMAIN_BIN, not a hard-coded name — the same override this case's own
    # comment demands one line below, and it was hard-coded here anyway. Review pointed
    # CHECK_DOMAIN_BIN at a mutant saying "budget is 999" and this case printed ok,
    # having opened the real file instead.
    dom = open(os.environ.get("CHECK_DOMAIN_BIN")
               or os.path.join(here, "check-domain.sh"), encoding="utf-8").read()
    # SCRIPT, not a hard-coded "check-state.sh". This case reads source rather than running
    # it, so a literal path here would keep reading the REAL file while CHECK_STATE_BIN
    # pointed the rest of the suite at a mutant — the case would report ok against a copy
    # it never opened, which is the failure mode the override exists to expose.
    sta = open(SCRIPT, encoding="utf-8").read()

    def budget(text, label, pat):
        m = _re.findall(pat, text)
        return sorted({int(x) for x in m}), label

    checks, ok_all = [], True
    for what, dpat, spat in (
        ("feature.json lines",  r"feature\.json is \{len\(lines\)\} lines — budget is (\d+)",
                                r"feature\.json'\)\} is \{len\(fl\)\} lines — budget is (\d+)"),
        # The comment-line budget pair is GONE, not relaxed. T-06 removed the check from
        # both files because JSON has no comments, so it could never fire — and a pair of
        # numbers that can never be printed is a duplicate this case cannot police.
        ("STATE.md lines",      r"STATE\.md is \{len\(lines\)\} lines — budget is (\d+)",
                                r"STATE\.md'\)\} is \{len\(sl\)\} lines — budget is (\d+)"),
        # Issue #139 made this the fourth number in both files, so it joins the detector in
        # the same commit that duplicates it — not in a later one nobody writes.
        ("CLAUDE.md lines",     r"CLAUDE\.md is \{len\(lines\)\} lines — budget is (\d+)",
                                r"CLAUDE\.md is \{len\(_cml\)\} lines — budget is (\d+)"),
    ):
        a, _ = budget(dom, what, dpat)
        b, _ = budget(sta, what, spat)
        good = bool(a) and a == b
        ok_all &= good
        checks.append(f"{what}: check-domain {a or 'NOT FOUND'} vs check-state {b or 'NOT FOUND'}")

    # The checkpoint vocabulary, the oldest deliberate duplicate in the pair.
    va = set(_re.findall(r'"([a-z_]+)"',
                         _re.search(r"ALLOWED = \{(.*?)\}", dom, _re.S).group(1)))
    vb = set(_re.findall(r'"([a-z_]+)"',
                         _re.search(r"CHECKPOINT_KEYS = \{(.*?)\n\}", sta, _re.S).group(1)))
    vgood = bool(va) and va == vb
    ok_all &= vgood
    checks.append(f"checkpoint keys: {len(va)} vs {len(vb)}, "
                  f"diff {sorted(va ^ vb) or 'none'}")

    # The handoff contract, in THREE copies — the two scripts plus the template a human
    # fills in. The template is the one that matters most and is the one no gate reads:
    # rename a heading there and every future handoff is written to a shape check-domain
    # rejects, with the rejection pointing at templates/HANDOFF.md as the authority.
    # Compared case-insensitively, because check-state lowercases and check-domain does not.
    tpl = open(os.path.join(here, "..", "templates", "HANDOFF.md"), encoding="utf-8").read()
    ha = {h.lower() for h in _re.findall(r'"(## [^"]+)"',
          _re.search(r'required = \[(.*?)\]', dom, _re.S).group(1))}
    hb = {h.lower() for h in _re.findall(r'"(## [^"]+)"',
          _re.search(r"HANDOFF_HEADINGS = \[(.*?)\]", sta, _re.S).group(1))}
    hc = {h.strip().lower() for h in _re.findall(r"^(## .+)$", tpl, _re.M)}
    hgood = bool(ha) and ha == hb and ha <= hc
    ok_all &= hgood
    checks.append(f"handoff headings: check-domain {sorted(ha)}, check-state {sorted(hb)}, "
                  f"template {sorted(hc)}")

    print(f"{'ok' if ok_all else 'FAIL'} - case (o): check-domain.sh, check-state.sh and "
          f"HANDOFF.md agree on every duplicated budget, key and heading")
    if not ok_all:
        for c in checks:
            print(f"       | {c}")
    return ok_all


def case_u():
    """INV-25 (issue #103): an out-of-place worktree red-gates session entry.

    Built with REAL git, deliberately. The test process is not the Bash tool route, so
    it may create the shapes T-04 now forbids there — and INV-25 reads
    `git worktree list --porcelain`, so a hand-built .git pointer would not appear in
    that output at all and the case would pass vacuously.

    EVERY DIRECTORY USED AS A RUN ROOT GETS make_fixture. check-state.sh exits 1 with
    "project not onboarded" before any invariant runs, so a bare worktree root would
    exit non-zero while printing no INV-25 line, and these assertions could never be
    satisfied by correct code.
    """
    results = []

    def _repo(path):
        os.makedirs(path, exist_ok=True)
        for cmd in (["git", "init", "-q"],
                    ["git", "config", "user.email", "t@example.com"],
                    ["git", "config", "user.name", "t"]):
            subprocess.run(cmd, cwd=path, capture_output=True)
        with open(os.path.join(path, "f.txt"), "w") as f:
            f.write("x\n")
        subprocess.run(["git", "add", "f.txt"], cwd=path, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=path, capture_output=True)
        return path

    def _add_wt(repo, dest):
        subprocess.run(["git", "worktree", "add", "-q", dest, "HEAD"],
                       cwd=repo, capture_output=True)
        return dest

    def _inv25_lines(out):
        return [l for l in out.splitlines() if "INV-25" in l]

    with tempfile.TemporaryDirectory() as tmp:
        # --- repo A: the PAIRED ALLOW. One worktree, in the legitimate location.
        # Without this the case cannot tell a working invariant from one that flags
        # every worktree it sees.
        a = _repo(os.path.join(tmp, "A"))
        _add_wt(a, os.path.join(a, ".claude", "worktrees", "wt"))
        make_fixture(a, '{}', "  parent: 40")
        _code_a, out_a = run(a)
        ok = not _inv25_lines(out_a)
        results.append(("(u.1) a worktree UNDER .claude/worktrees/ is silent", ok,
                        "\n".join(_inv25_lines(out_a))))

        # --- repo B: FORBIDDEN. A sibling outside the checkout, and the session is NOT
        # standing in it — so branch 3, which keeps the removal guidance.
        b = _repo(os.path.join(tmp, "B"))
        sib = _add_wt(b, os.path.join(tmp, "B-sib"))
        make_fixture(b, '{}', "  parent: 40")
        code_b, out_b = run(b)
        b_lines = [l for l in _inv25_lines(out_b) if os.path.realpath(sib) in l or sib in l]
        # SEVERITY IS ASSERTED ON THE LINE'S OWN PREFIX, not on the run's exit code. The
        # fixture is red for other reasons already, so `code != 0` passes with INV-25
        # demoted to a note — measured. VIOLATION vs note is the only thing that
        # discriminates, and the write guards now REFUSE writes in such a tree, so a
        # note would be the same silence in a quieter font.
        results.append(("(u.2) a sibling worktree is a VIOLATION, not a note",
                        bool(b_lines) and all("VIOLATION" in l for l in b_lines),
                        f"exit {code_b}; INV-25 lines: {_inv25_lines(out_b)}"))

        # THE PAIRED POSITIVE FOR THE BRANCH. Without it, the negative asserted on repo C
        # below is satisfiable by stripping removal guidance from EVERY branch — the
        # opposite defect, and nothing else in this suite would catch it. This is what
        # proves the branch actually branches.
        results.append(("(u.3) the not-my-root branch DOES carry `git worktree remove`",
                        bool(b_lines) and any("git worktree remove" in l for l in b_lines),
                        f"lines: {b_lines}"))

        # --- repo C: FORBIDDEN, own-root branch, plus the base-discriminating allow.
        # Two worktrees from the same mechanism: one out of place, which is ALSO the
        # session root, and one legitimate under the MAIN checkout.
        c = _repo(os.path.join(tmp, "C"))
        own = _add_wt(c, os.path.join(tmp, "C-own"))
        legit = _add_wt(c, os.path.join(c, ".claude", "worktrees", "legit"))
        make_fixture(own, '{}', "  parent: 40")
        code_c, out_c = run(own)
        c_lines = _inv25_lines(out_c)
        own_lines = [l for l in c_lines if os.path.realpath(own) in l or own in l]
        results.append(("(u.4) a session ROOTED in an out-of-place worktree is a "
                        "VIOLATION too — severity does not branch",
                        bool(own_lines) and all("VIOLATION" in l for l in own_lines),
                        f"exit {code_c}; INV-25 lines: {c_lines}"))

        # THE BASE-DISCRIMINATING PAIRED ALLOW, scoped BY PATH and not by the run — repo
        # C legitimately prints one INV-25 line for its own root, so asserting the run
        # prints none would contradict u.4.
        #
        # This is the assertion that pins the comparison base to the MAIN CHECKOUT. With
        # the base taken from the session root, `legit` sits outside
        # <root>/.claude/worktrees/, is not the session root and is not prunable — so it
        # falls to branch 3 and is handed `git worktree remove` on a correct tree. Repo
        # A's allow cannot detect this: there the run root and the main checkout are the
        # same directory and both bases agree.
        legit_lines = [l for l in c_lines if os.path.realpath(legit) in l or legit in l]
        results.append(("(u.5) the LEGITIMATE worktree under the main checkout is silent "
                        "even from an out-of-place root",
                        not legit_lines, f"lines: {legit_lines}"))

        # THE WORDING, both halves, on THAT LINE ONLY. Asserting over the whole run would
        # redden correct code the moment any other flagged entry printed the string.
        # Presence alone passes if the removal sentence is re-added beside the location
        # line; absence alone passes for a line that says nothing useful.
        results.append(("(u.6) the own-root line names .claude/worktrees and does NOT say "
                        "`git worktree remove`",
                        bool(own_lines)
                        and all(".claude/worktrees" in l for l in own_lines)
                        and all("git worktree remove" not in l for l in own_lines),
                        f"lines: {own_lines}"))

    # --- F-B: THE FOURTH IMPORT ROUTE. The three in the two write guards fail closed;
    # this one absorbed the ImportError, skipped every INV-25 branch, printed
    # "all state invariants hold" and exited 0. Found by the review panel, with zero
    # coverage: u.1-u.6 all have the module, and SC-10's module-absent fixture is a
    # different file. An isolated copy is required — a check-state running from the real
    # bin/ finds the real module whatever the fixture looks like.
    with tempfile.TemporaryDirectory() as tmp2:
        isobin = os.path.join(tmp2, ".agents", "skills", "harness", "bin")
        os.makedirs(isobin)
        _bin = os.path.dirname(os.path.abspath(SCRIPT))
        for fn in ("check-state.sh", "harness_yaml.py"):
            shutil.copy(os.path.join(_bin, fn), os.path.join(isobin, fn))
        os.chmod(os.path.join(isobin, "check-state.sh"), 0o755)
        b = _repo(os.path.join(tmp2, "B"))
        _add_wt(b, os.path.join(tmp2, "B-sib"))
        make_fixture(b, '{}', "  parent: 40")
        env = _root_env(b)
        r = subprocess.run([os.path.join(isobin, "check-state.sh")], cwd=b,
                           capture_output=True, text=True, env=env)
        # THE VERDICT MOVED FROM A FINDING TO A REFUSAL, and it moved LOUDER (FEAT-42
        # T-12). check-state.sh now resolves its own root through harness_boundary, so a
        # tree where that module cannot be imported is one this script cannot even locate
        # — it exits 2 before any invariant runs, naming the module on stderr, instead of
        # exiting 1 with an INV-25 CANNOT RUN line. The property this case exists to hold
        # is unchanged and is still asserted in full: an unimportable harness_boundary is
        # NEVER silent and NEVER reports a clean tree.
        results.append(("(u.7) F-B: an unimportable harness_boundary.py is a REFUSAL that "
                        "names it, not a silent skip of INV-25",
                        r.returncode == 2
                        and "harness_boundary" in r.stderr
                        and "all state invariants hold" not in r.stdout,
                        f"exit {r.returncode}: out={r.stdout.strip()[:200]} "
                        f"err={r.stderr.strip()[:200]}"))

    all_ok = True
    for name, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - case {name}")
        if not ok:
            all_ok = False
            print(f"        {str(detail).strip()[:300]}")
    return all_ok




_SENTINEL = object()


def _inv26_fixture(root, feat, task_status, card_status, parent_status,
                   issues=None, feature_status="Building", second_status=None,
                   second_card=None, factory=None, board_override=_SENTINEL):
    """One INV-26 fixture: harness.json with sync+repo+board, one feature with a plan,
    a feature.json recording issues, and a fake gh whose project item-list page puts
    each card wherever the caller says.

    THE FAKE IS POINTED AT WITH FACTORY_GH, the same variable factory_gh honours, so one
    fake serves both gh_board and the invariant. `gh auth status` must exit 0 through it
    or INV-26 gates out and every assertion below passes vacuously.
    """
    h = os.path.join(root, ".harness")
    fd = os.path.join(h, "harness", "features", feat)
    os.makedirs(fd, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        # THE FIVE STATIONS ARE REQUIRED NOW (FEAT-24 T-04/T-05). Before this feature the
        # board carried three keys and INV-26 spelled "Building"/"Done"/"Backlog" itself;
        # the names now come from the declaration, so a fixture without `stations` is not a
        # weaker fixture — it is an UNUSABLE board, and case v.13 asserts that it is
        # reported as one. `board_override` lets a case ship a deliberately broken board.
        # The ordered lowercase declaration (FEAT-41 T-01); INV-26 compares stations, not
        # columns, because gh_board.board_stations lowercases the board's answer on read.
        _board = {"owner": "org", "number": 3, "station_field": "status",
                  "stations": ["backlog", "plan", "ready", "building", "review", "done"]}
        if board_override is not _SENTINEL:
            _board = board_override
        json.dump({"github": {"sync": True, "repo": "org/repo",
                              "board": _board}}, f)
    with open(os.path.join(fd, "plan.yaml"), "w") as f:
        f.write("schema: plan/1\nfeature: %s\napproval:\n  status: approved\n"
                "tasks:\n  - id: T-01\n    title: t\n    change_type: logic\n"
                "    execution_mode: team\n    execution_agent: harness-backend-dev\n"
                "    depends_on: []\n"
                "    status: %s\n    files:\n      - a.py\n    verify: |\n      true\n"
                "    intent: |\n      x\n" % (feat, task_status))
        # A SECOND TASK, so a fixture can sit BETWEEN two statuses. Every case before
        # this parameter was single-task, which is exactly why the suite stayed green
        # while a mixed plan silenced the whole invariant.
        if second_status is not None:
            f.write("  - id: T-02\n    title: t2\n    change_type: logic\n"
                    "    execution_mode: team\n    execution_agent: harness-backend-dev\n"
                    "    depends_on: []\n"
                    "    status: %s\n    files:\n      - b.py\n    verify: |\n      true\n"
                    "    intent: |\n      x\n" % second_status)
    if issues is None:
        issues = {"T-01": 41} if second_status is None else {"T-01": 41, "T-02": 42}
    _doc = {"feature_id": feat, "branch": "b", "pr": None,
            "status": feature_status, "review_sha": "abc1234",
            "cycles_used": 0, "max_total_cycles": 10, "runs": [],
            "github": {"milestone": 1, "parent": 40, "issues": issues}}
    if factory is not None:
        # A factory-lane feature: published by factory_decompose, so its issues live
        # under `factory`, in a repository fleet.yaml must declare or INV-24 fires
        # instead of the clause under test.
        _doc["factory"] = factory
        os.makedirs(os.path.join(h, "factory"), exist_ok=True)
        with open(os.path.join(h, "factory", "fleet.yaml"), "w") as f:
            f.write("schema: factory-fleet/1\nrepos:\n  - name: %s\n"
                    "workspace_root: %s\n" % (factory["repo"], root))
    with open(os.path.join(fd, "feature.json"), "w") as f:
        json.dump(_doc, f)

    items = [{"content": {"repository": "org/repo", "number": 41}, "status": card_status},
             {"content": {"repository": "org/repo", "number": 40}, "status": parent_status}]
    if second_status is not None:
        items.append({"content": {"repository": "org/repo", "number": 42},
                      "status": second_card if second_card is not None else "Backlog"})
    page = json.dumps({"totalCount": len(items), "items": items})
    # TWO SHAPES, dispatched on the subcommand. FEAT-29 T-02 replaced INV-26's
    # `gh project item-list` read with ONE targeted `gh api graphql` query
    # (factory_gh.project_item_stations). A fake serving only the item-list shape makes that
    # call raise, check-state.sh's bare except swallows it, and INV-26 goes SILENT — every
    # assertion here then passes vacuously, which is issue #588's shape inside the one
    # invariant this fixture exists to test. Six named cases went red on exactly that.
    # The item-list shape is KEPT: it costs nothing and any caller still on the old read
    # keeps working rather than failing in a second, differently-confusing way.
    gql = json.dumps({"data": {"user": {"projectV2": {"items": {
        "totalCount": len(items),
        "nodes": [{"content": {"number": it["content"]["number"],
                               "repository": {"nameWithOwner": it["content"]["repository"]}},
                   "fieldValueByName": ({"name": it["status"]}
                                        if it.get("status") is not None else None)}
                  for it in items],
        "pageInfo": {"hasNextPage": False, "endCursor": None}}}}}})
    fake = os.path.join(root, "fake-gh")
    with open(fake, "w") as f:
        f.write("#!/bin/bash\ncase \"$1 $2\" in\n"
                "  \"auth status\") exit 0 ;;\n"
                "  \"api graphql\") cat <<'GQL'\n" + gql + "\nGQL\n    exit 0 ;;\n"
                "esac\n"
                "cat <<'EOF'\n" + page + "\nEOF\n")
    os.chmod(fake, 0o755)
    return fake


def _run_with_gh(tmp, fake):
    env = dict(os.environ)
    env = _root_env(tmp, env)
    env["FACTORY_GH"] = fake
    r = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


def _run_with_gh_streams(tmp, fake):
    """Both streams. A TRACEBACK GOES TO STDERR, so a case asserting the gate did not abort
    is blind if it reads stdout alone — measured: removing INV-26's try/except reddened the
    reports case and left the completes case green, because the traceback was never in the
    text it searched. The whole file being one python3 heredoc is what makes an abort total,
    and that is the property this second reader exists to see."""
    env = dict(os.environ)
    env = _root_env(tmp, env)
    env["FACTORY_GH"] = fake
    r = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout, r.stderr


def case_v():
    """INV-26 (issue #277): the board must agree with the plan.

    THE NON-VACUITY PAIR IS THE POINT. v.1 and v.2 differ in the fake page ONLY — one
    card's status and the parent's. If v.1 alone passed, it would be satisfied by an
    invariant that reports a violation for every feature it looks at, which is the same
    blindness facing the other way.
    """
    results = []

    def _lines(out):
        return [l for l in out.splitlines() if "INV-26" in l]

    # --- v.1 THE MIS-COLUMNED FIXTURE: T-01 done, its card in Backlog.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        # The fixture feeds the BOARD's capitalised "Backlog"; board_stations lowercases it on
        # read, so the reported value is lowercase (FEAT-41 T-02).
        ok = (any("FEAT-X" in l and "T-01" in l and "done" in l and "backlog" in l
                  for l in ls))
        results.append(("(v.1) a mis-columned card is a VIOLATION naming feature, task, "
                        "plan status and column found", ok, "\n".join(ls) or "(no INV-26 line)"))

    # --- v.2 THE CORRECTED TWIN: the SAME fixture, that one card reading Done.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.2) the corrected twin reports NOTHING", not ls,
                        "\n".join(ls)))

    # --- v.3 the terminal exemption: status Done, every card wrong, silence.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Backlog",
                              feature_status="Done")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.3) a feature whose status is Done is exempt even with every "
                        "card wrong", not ls, "\n".join(ls)))

    # --- v.4 the mirror-never-ran clause: a task building, sync on, empty issues map.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Building", "Building", issues={})
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("no mirrored issues" in l for l in ls)
        results.append(("(v.4) tasks in flight with an EMPTY issues map is a violation",
                        ok, "\n".join(ls) or "(no INV-26 line)"))

    # --- v.5 CANNOT VERIFY: the recorded issue is absent from the board page.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review",
                              issues={"T-01": 9999})
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("CANNOT VERIFY" in l and "9999" in l and "not on the board" in l
                 for l in ls)
        results.append(("(v.5) a recorded issue absent from the board is CANNOT VERIFY, "
                        "not a clean pass", ok, "\n".join(ls) or "(no INV-26 line)"))

    # --- v.6 the parent mismatch is its own finding.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Backlog")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("parent" in l and "#40" in l and "review" in l and "backlog" in l
                 for l in ls)
        results.append(("(v.6) the parent card disagreeing with the derivation is a "
                        "violation", ok, "\n".join(ls) or "(no INV-26 line)"))

    # --- v.7 gh absent contributes NOTHING. The environment is not the tree.
    with tempfile.TemporaryDirectory() as tmp:
        _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Backlog")
        _c, out = _run_with_gh(tmp, os.path.join(tmp, "no-such-gh-binary"))
        ls = _lines(out)
        results.append(("(v.7) a gh binary that does not exist records NO INV-26 finding",
                        not ls, "\n".join(ls)))

    # --- v.8 THE CASE THE INVARIANT WAS BUILT FOR AND COULD NOT SEE.
    # T-01 done with its card still in Backlog, T-02 pending and correctly in Backlog.
    # derive_station returns None for {done, pending}, and the old code skipped the whole
    # feature on None — so SC-05's own scenario went unreported in the ordinary window
    # between two tasks. The per-task comparison never needed the parent derivation.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Backlog",
                              second_status="pending", second_card="Backlog")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("T-01" in l and "done" in l and "backlog" in l for l in ls)
        results.append(("(v.8) a mis-columned done card is reported even when the plan "
                        "derives NO parent station", ok,
                        "\n".join(ls) or "(no INV-26 line)"))

    # --- v.9 THE NON-VACUITY TWIN FOR v.8, and the parent-silence proof in one fixture.
    # Same mixed plan, T-01's card corrected to Done. Nothing must be reported — in
    # particular NOT a parent finding, because a None derivation still has no station to
    # expect and the parent card sits in Backlog here.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Backlog",
                              second_status="pending", second_card="Backlog")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.9) the corrected twin of v.8 reports NOTHING, and a None "
                        "derivation raises no parent finding", not ls, "\n".join(ls)))

    # --- v.10 an all-pending plan still claims nothing. The silence that was correct
    # must survive the fix: no task has started, so no card can be wrong yet.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "pending", "Building", "Review",
                              second_status="pending", second_card="Done")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.10) an all-pending plan reports NOTHING even with every card "
                        "wrong", not ls, "\n".join(ls)))

    # --- v.11/v.12 THE LANE PAIR (issue #349's caveat). The mirror-never-ran clause read
    # only `github.issues`, so a feature published by factory_decompose — issues recorded
    # under `factory.issues`, nothing under `github.issues` — fired a FALSE violation
    # instructing the operator to mirror product work onto harness's board. The pair
    # differs in the factory block alone: v.11 must stay silent, v.12 keeps the teeth.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Building", "Building",
                              issues={},
                              factory={"repo": "org/prod", "issues": {"T-01": 7}})
        _c, out = _run_with_gh(tmp, fake)
        ls = [l for l in _lines(out) if "no mirrored issues" in l]
        results.append(("(v.11) a factory-published feature (factory.issues recorded, "
                        "github.issues empty) raises NO mirror-never-ran violation",
                        not ls, "\n".join(ls)))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Building", "Building",
                              issues={},
                              factory={"repo": "org/prod", "issues": {}})
        _c, out = _run_with_gh(tmp, fake)
        ls = [l for l in _lines(out) if "no mirrored issues" in l]
        results.append(("(v.12) the same fixture with an EMPTY factory.issues still "
                        "fires — the exemption keys on recorded issues, not the block",
                        bool(ls), "(no INV-26 line)"))

    # THE OK-LINE TEXT IS THE CONTRACT. T-05's approved verify matches these five with
    # `grep -qxF` — exact, whole line, after the `ok - ` prefix is stripped. Rewording one
    # breaks the gate silently, so the strings below are load-bearing and are not descriptions.

    # --- THE INVERSE OF THE OLD BEHAVIOUR (FEAT-24 T-05). A board present but broken used to
    # make load_board return None, which made INV-26 vacuous and left the gate GREEN. Two
    # SEPARATE properties, asserted separately because the verify wants them separately
    # visible: it is REPORTED, and the gate still COMPLETES. A crashed gate reports no
    # invariant at all, which is a worse silence than the one being fixed.
    _broken = {"owner": "org", "number": 3, "station_field": "status"}
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review",
                              board_override=_broken)
        c, out, err = _run_with_gh_streams(tmp, fake)
        ls = [l for l in _lines(out) if "CANNOT RUN" in l]
        results.append(("INV-26 reports a violation when the board declaration is unusable",
                        bool(ls) and "stations" in ls[0],
                        "lines=%r" % (ls[:1],)))
        # BOTH STREAMS, and the later invariants too. An abort is not merely a traceback: it
        # is every invariant after INV-26 going unreported, so the case checks that INV-13 —
        # which lives immediately below INV-26 — still ran.
        _tb = "Traceback" in out or "Traceback" in err
        _later_ran = "INV-13" in out or not _tb
        results.append(("INV-26 completes the gate rather than aborting on an unusable board",
                        not _tb and c == 1 and _later_ran,
                        "exit=%s traceback=%s stderr_tail=%r"
                        % (c, _tb, err[-200:])))

    # --- THE NULL TWIN. Not named by the verify, and load-bearing anyway: without it the two
    # cases above are satisfied by an invariant that reports every board it sees, including the
    # one shape that is a deliberate declaration rather than a defect.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review",
                              board_override=None)
        c, out = _run_with_gh(tmp, fake)
        results.append(("(v.14) an explicit null board records NOTHING — not a violation, "
                        "and no traceback",
                        not _lines(out) and "Traceback" not in out,
                        "\n".join(_lines(out)) or "(unexpected INV-26 line)"))

    # --- T-22 / D-24: THE REVIEW-PHASE WIDENING, AND THE BOUND ON IT.
    # Under D-23 a done task's sub-issue is deliberately left OPEN so it can hold its column
    # through Review. So a done task's card may read done, review OR building — but ONLY while
    # the feature's own feature.json status is Review. All four cases below exist because the
    # accept set has three members and the bound has two sides; three fixtures cannot see a
    # widening that leaked past its bound.
    #
    # THE PLAN ASKED FOR A CASE THAT CANNOT EXIST. Its wording was "the same feature at status
    # Done with the same card is still a VIOLATION". At status Done the TERMINAL EXEMPTION
    # `continue`s before the per-task comparison is ever reached (case v.3 asserts exactly that),
    # so no fixture at status Done can produce an INV-26 station finding at all. The honest test
    # of the bound is a NON-terminal status, so (v.T22b) uses Building.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Review", "Review",
                              feature_status="Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.T22a) at status Review, a done task's card reading Review is "
                        "ACCEPTED", not ls, "\n".join(ls)))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Building", "Review",
                              feature_status="Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.T22b) at status Review, a done task's card reading Building is "
                        "ACCEPTED", not ls, "\n".join(ls)))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Review", "Review",
                              feature_status="Building")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("FEAT-X" in l and "T-01" in l and "review" in l for l in ls)
        results.append(("(v.T22c) THE BOUND: at status Building, a done task's card reading "
                        "Review is still a VIOLATION", ok,
                        "\n".join(ls) or "(no INV-26 line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review",
                              feature_status="Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("FEAT-X" in l and "T-01" in l and "backlog" in l for l in ls)
        results.append(("(v.T22d) the widening does NOT reach Backlog: a done task's card "
                        "there is a VIOLATION even at status Review", ok,
                        "\n".join(ls) or "(no INV-26 line)"))

    # --- ONE CASE PER KEY, AND THAT IS THE POINT. _EXPECT quantifies over three statuses, so
    # a single fixture cannot see a lookup that was never migrated: a `done` case is blind to a
    # `backlog` literal left behind. This feature's own recurring defect is a clause over N
    # keys with fewer than N fixtures, and the verify demands one each because of it.
    #
    # Every column is RENAMED away from the DEC-203 spellings. A build that still spells
    # "Building"/"Done"/"Backlog" itself reports a violation against a correctly placed card.
    _renamed = {"owner": "org", "number": 3, "station_field": "status",
                "stations": {"backlog": "Icebox", "plan": "Drafted", "ready": "Primed",
                             "building": "WIP", "review": "Review", "done": "Shipped"}}

    def _no_finding(out):
        return not [l for l in _lines(out) if "CANNOT RUN" not in l]

    # backlog: a MIXED plan — an all-pending plan reports nothing whatever _EXPECT says, so
    # the pending card can only be judged beside a started one.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Shipped", "Review",
                              second_status="pending", second_card="Icebox",
                              board_override=_renamed)
        c, out = _run_with_gh(tmp, fake)
        results.append(("INV-26 expects the declared station for status: backlog",
                        _no_finding(out), "\n".join(_lines(out)) or "(unexpected line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "WIP", "WIP",
                              board_override=_renamed)
        c, out = _run_with_gh(tmp, fake)
        results.append(("INV-26 expects the declared station for status: building",
                        _no_finding(out), "\n".join(_lines(out)) or "(unexpected line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Shipped", "Review",
                              board_override=_renamed)
        c, out = _run_with_gh(tmp, fake)
        results.append(("INV-26 expects the declared station for status: done",
                        _no_finding(out), "\n".join(_lines(out)) or "(unexpected line)"))

    # --- FEAT-41 T-04: ONE CASE PER _EXPECT KEY, against the REAL declaration ------------
    # _EXPECT quantifies over three statuses, so a single fixture cannot see a key that was
    # never migrated — a `done` case is blind to a `pending` literal left behind in the `ready`
    # slot. Each key therefore gets a POSITIVE case (correctly placed card, no finding) AND a
    # NEGATIVE control (misplaced card, a finding naming the value), because a positive case
    # alone passes on a build where INV-26 reports nothing at all.
    #
    # These are separate from the renamed-board cases above, which pass VACUOUSLY now: a renamed
    # declaration is a mapping, validate_board refuses it, INV-26 emits CANNOT RUN, and
    # `_no_finding` filters exactly that line out. T-11 owns deleting them.
    _t04 = []

    # ready: a MIXED plan. An all-ready plan is skipped outright by the nothing-has-started
    # guard, so the ready card can only be judged beside a started one — which is also the
    # regression the guard rewrite in this task protects: were it still spelled against
    # `pending`, this fixture would stop being skipped and every all-ready feature with it.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review",
                              second_status="ready", second_card="Ready")
        c, out = _run_with_gh(tmp, fake)
        _t04.append(("(v.T04-ready) a ready task whose card reads Ready is CLEAN",
                     _no_finding(out), "\n".join(_lines(out)) or "(unexpected line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review",
                              second_status="ready", second_card="Building")
        c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        _t04.append(("(v.T04-ready-neg) a ready task whose card reads Building is a VIOLATION "
                     "naming ready",
                     any("T-02" in l and "ready" in l for l in ls),
                     "\n".join(ls) or "(no INV-26 line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Building", "Building")
        c, out = _run_with_gh(tmp, fake)
        _t04.append(("(v.T04-building) a building task whose card reads Building is CLEAN",
                     _no_finding(out), "\n".join(_lines(out)) or "(unexpected line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Ready", "Building")
        c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        _t04.append(("(v.T04-building-neg) a building task whose card reads Ready is a "
                     "VIOLATION naming building",
                     any("T-01" in l and "building" in l for l in ls),
                     "\n".join(ls) or "(no INV-26 line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review")
        c, out = _run_with_gh(tmp, fake)
        _t04.append(("(v.T04-done) a done task whose card reads Done is CLEAN",
                     _no_finding(out), "\n".join(_lines(out)) or "(unexpected line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review")
        c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        _t04.append(("(v.T04-done-neg) a done task whose card reads Backlog is a VIOLATION "
                     "naming done",
                     any("T-01" in l and "done" in l for l in ls),
                     "\n".join(ls) or "(no INV-26 line)"))

    # `pending` IS NOT A VALUE ANY MORE. A plan still carrying it must not be silently treated
    # as the not-started station: _EXPECT has no such key, so _want is None and the per-task
    # compare skips — which is the fail-open direction, and is why check-plan-routes.py refuses
    # the value outright at plan time. Asserted here so the two halves stay a pair.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "pending", "Backlog", "Review")
        c, out = _run_with_gh(tmp, fake)
        ls = [l for l in _lines(out) if "T-01" in l]
        _t04.append(("(v.T04-pending) a leftover pending task is NOT judged by INV-26 — "
                     "check-plan-routes refuses it at plan time instead",
                     not ls, "\n".join(ls) or "(no line, as expected)"))

    results.extend(_t04)

    allok = True
    for name, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - {name}")
        if not ok and detail:
            print("      " + detail.replace("\n", "\n      "))
        allok = allok and ok
    return allok


def case_w():
    """ABANDONED: the terminal state for a feature planned and never built (2026-08-14).

    THE NON-VACUITY PAIR IS THE POINT. w.1 and w.2 differ in ONE byte-range — the status
    value — and nothing else. An abandoned feature's BRIEF is never approved BY DESIGN, so
    the exemption must silence that violation; but an exemption that silenced it for every
    feature would be the same blindness facing the other way, which w.2 is here to catch.

    FEAT-19 was the first: planned, reviewed through three engineering passes, retired
    unsigned when map #336 superseded its scope. Before this, the enum had no terminal
    state for that, and every one of the 18 features on disk was Done.
    """
    results = []

    def build(status):
        tmp = tempfile.mkdtemp()
        h = os.path.join(tmp, ".harness")
        fd = os.path.join(h, "harness", "features", "FEAT-Z")
        os.makedirs(fd, exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "team-config.yaml"), "w") as f:
            f.write("agents: {}\n")
        json.dump({"feature_id": "FEAT-Z", "branch": "b", "pr": None,
                   "status": status, "review_sha": "abc1234",
                   "cycles_used": 0, "max_total_cycles": 10, "runs": []},
                  open(os.path.join(fd, "feature.json"), "w"))
        with open(os.path.join(fd, "BRIEF.md"), "w") as f:
            f.write("# BRIEF\n\n## Approval\n\nstatus: pending\n")
        return tmp

    def approval_lines(tmp):
        env = _root_env(tmp)
        r = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
        return [l for l in r.stdout.splitlines() if "NOT approved" in l]

    # w.1 ABANDONED: the unapproved brief must NOT be reported.
    ls = approval_lines(build("Abandoned"))
    results.append(("(w.1) an Abandoned feature's unapproved BRIEF raises NOTHING",
                    not ls, "\n".join(ls)))

    # w.2 THE TWIN: same fixture, status Plan. It MUST be reported, or w.1 proves nothing.
    ls = approval_lines(build("Plan"))
    results.append(("(w.2) the same fixture at status Plan IS reported",
                    any("FEAT-Z" in l for l in ls), "\n".join(ls) or "(no line)"))

    allok = True
    for name, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - {name}")
        if not ok and detail:
            print("      " + detail.replace("\n", "\n      "))
        allok = allok and ok
    return allok


def case_x():
    """INV-27 (FEAT-20 T-02): the layout invariant at the session-entry call site.

    Existing fixtures hold no coupled reader and no control-plane marker, so under
    D-04 they are NOT APPLICABLE and INV-27 appends nothing — which is exactly why
    every case above keeps passing. The applicable trees are built ONLY here, by
    writing the marker and reader stubs explicitly; the shared helper is untouched
    on purpose (a stub in it would put an INV-27 verdict inside every unrelated case).
    """
    results = []
    import layout_fixtures as lf
    import layout_migration as lm
    STUBS = {rel: forms["legacy"] for rel, forms in lf.STUB.items()}

    def build(tmp, marker=True, overrides=None, evidence=True):
        h = os.path.join(tmp, ".harness")
        os.makedirs(h, exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "team-config.yaml"), "w") as f:
            f.write(STUBS[".harness/team-config.yaml"])
        if evidence:
            # LEGACY on purpose: case_x's reader stubs are all legacy-form, so its
            # evidence must be legacy too — a legacy sandbox is a valid detector
            # input in every era, and segmenting only the evidence made x.3's
            # "clean" tree an undeclared-segment cannot-verify.
            fd = os.path.join(h, "features", "FEAT-Z")
            os.makedirs(fd, exist_ok=True)
            open(os.path.join(fd, "feature.json"), "w").write(
                json.dumps({"feature_id": "FEAT-Z", "branch": "b", "pr": None,
                            "status": "Done", "review_sha": "abc1234",
                            "cycles_used": 0, "max_total_cycles": 10, "runs": []}))
            dd = os.path.join(tmp, "docs", "harness")
            os.makedirs(dd, exist_ok=True)
            open(os.path.join(dd, "SPEC.md"), "w").write("# spec\n")
        if marker:
            mp = os.path.join(tmp, lm.MARKER)
            os.makedirs(os.path.dirname(mp), exist_ok=True)
            open(mp, "w").write(lf.FLEET_TEXT)
        overrides = overrides or {}
        for rel, text in STUBS.items():
            if rel == ".harness/team-config.yaml":
                continue
            p = os.path.join(tmp, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(overrides.get(rel, text))
        return tmp

    inv = lambda out: [l for l in out.splitlines() if "INV-27" in l]

    # x.1 a tree the detector REDDENS: legacy evidence, one reader migrated. Assert the
    # tag AND the remedy here, not only in the unit suite — this is the only automated
    # evidence the session-entry call site renders them at all.
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp, overrides={
            ".agents/skills/harness/bin/gen-decisions-index.py":
                'HEADER = "the authority is .harness/repoA/docs/DECISIONS.md"\n'})
        code, out = run(tmp)
        ls = inv(out)
        ok = (code == 1 and ls
              and any("gen-decisions-index.py" in l and "[migrated]" in l
                      and "atomic commit" in l for l in ls))
        results.append(("(x.1) a mixed tree -> exit 1, INV-27 names the reader, its "
                        "form-set tag and the remedy", ok, "\n".join(ls) or out[-400:]))

    # x.2 a tree it CANNOT JUDGE: one reader carries neither form.
    with tempfile.TemporaryDirectory() as tmp:
        # THE BLANKED FILE MUST STILL BE A READER. factory_config.py stood here until
        # FEAT-42 T-04 deleted its root resolution wholesale and its row left
        # layout_migration.READER_TABLE with it, so blanking it stopped producing
        # [neither] and produced silence. harness_boundary.py is a docs-surface reader
        # that survives, and layout_fixtures asserts STUB and READER_TABLE agree, so a
        # future row deletion breaks this at import rather than here.
        build(tmp, overrides={
            ".agents/skills/harness/bin/harness_boundary.py": "nothing relevant\n"})
        code, out = run(tmp)
        ls = inv(out)
        ok = code == 1 and any("CANNOT VERIFY" in l and "[neither]" in l for l in ls)
        results.append(("(x.2) an unjudgeable tree -> exit 1, INV-27 CANNOT VERIFY",
                        ok, "\n".join(ls) or out[-400:]))

    # x.3 an APPLICABLE clean tree: marker present, every reader legacy, legacy
    # evidence on both surfaces. Assert the ABSENCE of INV-27 specifically, not merely
    # exit 0 — a case that passes because the invariant never ran must be
    # distinguishable from one that passes because it ran clean.
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp)
        _code, out = run(tmp)
        ls = inv(out)
        results.append(("(x.3) an applicable clean tree -> NO INV-27 line",
                        not ls, "\n".join(ls)))

    # x.4 no marker: the product-repository and existing-fixture case, pinned
    # deliberately rather than left as an emergent property.
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp, marker=False)
        _code, out = run(tmp)
        ls = inv(out)
        results.append(("(x.4) no control-plane marker -> NO INV-27 line",
                        not ls, "\n".join(ls)))

    # x.5 layout_migration unimportable -> the CANNOT RUN wording, exit 1. The script
    # prepends ITS OWN dir to PYTHONPATH, so a shadow dir cannot outrank the real
    # module. Faithful route: run a COPY of check-state.sh from a bin dir holding its
    # one hard import (harness_yaml) and NO layout_migration.py — the same failure an
    # operator gets when the module is deleted from the tree.
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp)
        import shutil
        bindir = os.path.join(tmp, "binx")
        os.makedirs(bindir)
        shutil.copy(SCRIPT, os.path.join(bindir, "check-state.sh"))
        # harness_yaml is the script's one hard import; harness_boundary joined it in
        # FEAT-42 T-12, when check-state.sh started resolving its own root through it. Both
        # are copied so the ONLY thing missing from this bin is layout_migration.py, which
        # is what the case is about. Without the resolver the script refuses at exit 2
        # before any invariant runs, and the case would be red for the wrong module.
        for _mod in ("harness_yaml.py", "harness_boundary.py"):
            shutil.copy(os.path.join(os.path.dirname(SCRIPT), _mod),
                        os.path.join(bindir, _mod))
        env = dict(os.environ)
        env = _root_env(tmp, env)
        r = subprocess.run([os.path.join(bindir, "check-state.sh")],
                           cwd=tmp, capture_output=True, text=True, env=env)
        ls = inv(r.stdout)
        ok = r.returncode == 1 and any("CANNOT RUN" in l for l in ls)
        results.append(("(x.5) unimportable layout_migration -> INV-27 CANNOT RUN, "
                        "exit 1", ok, "\n".join(ls) or r.stdout[-400:]))

    allok = True
    for name, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - {name}")
        if not ok and detail:
            print("      " + detail.replace("\n", "\n      "))
        allok = allok and ok
    return allok



# ---------------------------------------------------------------------------
# FEAT-31 T-14 — INV-17's shape check reaches EVERY notes/handoff-*.md, not only
# the stems SEAM_NOTES names.
#
# ON THE ASSERTION TEXT, and this is a deliberate divergence from the task wording.
# The task says to assert "an INV-17 line". The shape message carries NO `INV-17`
# token — check-state.sh:1366 prints it as `  VIOLATION  <feat>: notes/<file> fails
# the shape (...)` — and the task ALSO says to report through the same bad.append
# path with the SAME message shape. Adding the token to make the word "INV-17"
# literally greppable would change the shape the task told me to preserve, so these
# cases assert on the VIOLATION prefix, the basename and `fails the shape`, which is
# the contract the verify block itself uses.
# ---------------------------------------------------------------------------

HANDOFF_GOOD = """# handoff — plan to build — FEAT-TEST

## Next
Do the thing.

## Trust
The measured figures.

## Dead ends
The one that did not work.

## Working set
one/file.py
"""


def _handoff_fixture(tmp, status, notes, feat="FEAT-TEST"):
    """A minimal tree INV-17 will walk: harness.json, one feature.json carrying a
    status in STATUS_ORDER, and whatever notes the case names.

    `notes` maps a BASENAME to its full text. Nothing here reads the real repo and
    nothing is written outside tmp."""
    h = os.path.join(tmp, ".harness")
    fdir = os.path.join(h, "harness", "features", feat)
    os.makedirs(os.path.join(fdir, "notes"), exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(HARNESS_JSON_SYNC_OFF)
    with open(os.path.join(fdir, "feature.json"), "w") as f:
        f.write(json.dumps({"status": status}))
    for name, text in notes.items():
        with open(os.path.join(fdir, "notes", name), "w") as f:
            f.write(text)
    return fdir


def _shape_lines(out, needle):
    """VIOLATION lines reporting a shape failure for `needle`. Counted, never
    just detected — case (t14-f) turns on the count being exactly 1."""
    return [l for l in out.splitlines()
            if l.startswith("  VIOLATION") and "fails the shape" in l and needle in l]


def case_t14_widening():
    """THE WIDENING. A note whose stem is in no SEAM_NOTES list, missing one of the
    four headings, is reported. Before T-14 the file was never opened at all, so
    this case is the one that fails against the pre-task tree."""
    with tempfile.TemporaryDirectory() as tmp:
        bad_note = HANDOFF_GOOD.replace("## Dead ends\n", "## Not A Heading\n")
        _handoff_fixture(tmp, "Plan", {"handoff-midphase.md": bad_note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-midphase.md")
        ok = len(hits) == 1 and "## dead ends" in hits[0]
        print(f"{'ok' if ok else 'FAIL'} - case (t14-d): a non-seam stem missing a heading "
              f"is reported by name ({len(hits)} line(s))")
        return ok


def case_t14_cap():
    """THE CAP REACHES IT TOO. Same non-seam stem, all four headings present, 61
    lines. The cap and the heading test are one check with two clauses, and a fix
    that wired only the headings into the new pass would pass (t14-d) and fail here."""
    with tempfile.TemporaryDirectory() as tmp:
        long_note = HANDOFF_GOOD + "\n".join(f"filler {i}" for i in range(1, 62))
        _handoff_fixture(tmp, "Plan", {"handoff-midphase.md": long_note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-midphase.md")
        ok = len(hits) == 1 and "cap 60" in hits[0]
        n = len(long_note.splitlines())
        print(f"{'ok' if ok else 'FAIL'} - case (t14-e): a non-seam stem over the cap is "
              f"reported ({n} lines, {len(hits)} line(s))")
        return ok


def case_t14_no_double():
    """NO DOUBLE REPORT, and this is the case the restructure exists to satisfy.
    Status Building REQUIRES handoff-plan.md, and the file is present but malformed.
    The seam loop and the glob pass both see it. EXACTLY ONE line, or the two passes
    are reporting the same file twice."""
    with tempfile.TemporaryDirectory() as tmp:
        bad_note = HANDOFF_GOOD.replace("## Trust\n", "## Nope\n")
        _handoff_fixture(tmp, "Building", {"handoff-plan.md": bad_note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-plan.md")
        ok = len(hits) == 1
        print(f"{'ok' if ok else 'FAIL'} - case (t14-f): a malformed seam-stem note is "
              f"reported EXACTLY once, not twice (count {len(hits)})")
        return ok


def case_t14_exempt_shape():
    """EXEMPTION DOES NOT SUPPRESS SHAPE. FEAT-01 is in HANDOFF_EXEMPT_LITERAL, so a
    MISSING required note is suppressed — but a note that EXISTS is shape-checked
    anyway. Both halves asserted in one fixture: status Done owes plan, build and
    validate; only a malformed handoff-plan.md is present."""
    with tempfile.TemporaryDirectory() as tmp:
        bad_note = HANDOFF_GOOD.replace("## Working set\n", "## Elsewhere\n")
        _handoff_fixture(tmp, "Done", {"handoff-plan.md": bad_note}, feat="FEAT-01-exempt")
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-plan.md")
        missing = [l for l in out.splitlines()
                   if l.startswith("  VIOLATION") and "is missing" in l and "handoff-" in l]
        ok = len(hits) == 1 and len(missing) == 0
        print(f"{'ok' if ok else 'FAIL'} - case (t14-g): a literal-exempt feature still has "
              f"its EXISTING note shape-checked ({len(hits)} shape) while missing notes stay "
              f"suppressed ({len(missing)} missing)")
        return ok


def case_t14_accepted():
    """ACCEPTED. Three well-formed notes, two seam stems and one non-seam stem. Zero
    shape lines. Without this the four cases above are satisfied by a pass that
    reports every note unconditionally."""
    with tempfile.TemporaryDirectory() as tmp:
        _handoff_fixture(tmp, "Review", {
            "handoff-plan.md": HANDOFF_GOOD,
            "handoff-build.md": HANDOFF_GOOD,
            "handoff-t04-rotation.md": HANDOFF_GOOD,
        })
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-")
        ok = len(hits) == 0
        print(f"{'ok' if ok else 'FAIL'} - case (t14-h): three well-formed notes, two seam "
              f"stems and one non-seam, raise ZERO shape lines ({len(hits)})")
        return ok


T14_MARKER = "# INV-17 handoff shape pass, all stems (FEAT-31 T-14)"


def case_t14_red():
    """RED PROOF. An exit status is never the proof (D-08). Strip the whole new pass
    from a copy, located by its marker comment, and compare COUNTS on case (t14-d)'s
    fixture: original 1, mutant 0.

    THE MUTANT LIVES BESIDE THE ORIGINAL, NOT IN THE FIXTURE, and that is not
    tidiness. check-state.sh imports harness_yaml from its own directory, so a copy
    placed in the tmpdir dies on import and exits non-zero — a code indistinguishable
    from a real finding, which is a green-looking proof that measured nothing. FEAT-30
    Q3 and the FEAT-31 behind-gate proof were both this trap."""
    src = open(SCRIPT).read()
    lines = src.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if T14_MARKER in l), None)
    if start is None:
        print("FAIL - case (t14-red): marker comment not found, nothing was mutated")
        return False
    end = next((i for i in range(start, len(lines))
                if lines[i].startswith("    if _ex_stems:")), None)
    if end is None:
        print("FAIL - case (t14-red): could not find the end of the pass")
        return False
    mutant_text = "".join(lines[:start] + lines[end:])
    if mutant_text == src:
        print("FAIL - case (t14-red): INCONCLUSIVE — the mutation did not change the source")
        return False

    mpath = os.path.join(os.path.dirname(os.path.realpath(SCRIPT)),
                         ".mutant-check-state-t14.sh")
    try:
        with open(mpath, "w") as f:
            f.write(mutant_text)
        shutil.copymode(SCRIPT, mpath)
        with tempfile.TemporaryDirectory() as tmp:
            bad_note = HANDOFF_GOOD.replace("## Dead ends\n", "## Not A Heading\n")
            _handoff_fixture(tmp, "Plan", {"handoff-midphase.md": bad_note})
            env = dict(os.environ)
            env = _root_env(tmp, env)
            real = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
            mut = subprocess.run([mpath], cwd=tmp, capture_output=True, text=True, env=env)
        n_real = len(_shape_lines(real.stdout, "handoff-midphase.md"))
        n_mut = len(_shape_lines(mut.stdout, "handoff-midphase.md"))
        if n_mut >= n_real:
            print(f"FAIL - case (t14-red): INCONCLUSIVE — original {n_real}, mutant "
                  f"{n_mut}; the mutant did not lose the finding")
            return False
        print(f"ok - case (t14-red): the pass is load-bearing — original reports {n_real}, "
              f"mutant reports {n_mut}")
        return True
    finally:
        if os.path.exists(mpath):
            os.remove(mpath)


# ---------------------------------------------------------------------------
# FEAT-31 T-10 — a required section with no BODY fails the shape. SC-15's
# automatable half: until this check existed, a handoff carrying all four headings
# and nothing under any of them passed the gate, so "the relay fails when ## Next is
# emptied" could not be shown.
#
# Assertion text as in the T-14 block above: the message carries no INV-17 token, so
# these cases assert the VIOLATION prefix, the basename and the named section.
# ---------------------------------------------------------------------------

T10_MARKER = "# INV-17 empty-body check (FEAT-31 T-10)"


def _empty_section(text, heading):
    """Return `text` with `heading`'s body blanked and the heading left in place.
    The heading must SURVIVE — otherwise the note fails on `miss` instead and the
    case would pass for the wrong reason."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].strip().lower() == heading:
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("##"):
                i += 1
            out.append("")
            continue
        i += 1
    return "\n".join(out) + "\n"


def case_t10_accepted():
    """ACCEPTED. All four headings, every body non-empty, "## Next" naming a concrete
    dispatch. Without this the four rejection cases below are satisfied by a check
    that reports every note."""
    with tempfile.TemporaryDirectory() as tmp:
        _handoff_fixture(tmp, "Building", {"handoff-plan.md": HANDOFF_GOOD})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-plan.md")
        ok = len(hits) == 0
        print(f"{'ok' if ok else 'FAIL'} - case (t10-a): a handoff with a body under every "
              f"heading raises no shape line ({len(hits)})")
        return ok


def _rejected(heading, label, tag):
    with tempfile.TemporaryDirectory() as tmp:
        note = _empty_section(HANDOFF_GOOD, heading)
        _handoff_fixture(tmp, "Building", {"handoff-plan.md": note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-plan.md")
        # The HEADING must still be present, or this passed on `miss` and proves nothing.
        heading_survived = heading in note.lower()
        named = hits and heading in hits[0] and "empty section" in hits[0]
        missed = hits and "missing section" in hits[0]
        ok = bool(heading_survived and named and not missed)
        print(f"{'ok' if ok else 'FAIL'} - case ({tag}): {label} emptied is reported as an "
              f"empty section, not a missing one ({len(hits)} line(s))")
        return ok


def case_t10_next_emptied():
    """REJECTED — the case SC-15 names. `## Next` heading present, body blank."""
    return _rejected("## next", "the Next section", "t10-b")


def case_t10_trust_emptied():
    return _rejected("## trust", "the Trust section", "t10-c1")


def case_t10_deadends_emptied():
    return _rejected("## dead ends", "the Dead ends section", "t10-c2")


def case_t10_workingset_emptied():
    """The other three emptied ONE AT A TIME, each its own case, so a check that
    inspects only "## Next" cannot pass all four."""
    return _rejected("## working set", "the Working set section", "t10-c3")


def case_t10_red():
    """RED PROOF. Strip the empty-body check by its marker comment and compare COUNTS
    on case (t10-b)'s fixture: original 1, mutant 0. Equal counts are INCONCLUSIVE and
    exit non-zero, never passed.

    The mutant lives BESIDE the original for the reason case (t14-red) records: a copy
    in the fixture dir cannot import harness_yaml and dies with a code that looks like
    a finding."""
    src = open(SCRIPT).read()
    lines = src.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if T10_MARKER in l), None)
    if start is None:
        print("FAIL - case (t10-red): marker comment not found, nothing was mutated")
        return False
    # The check ends at the `if miss or len(hl) > 60 or _empty:` line, which stays --
    # only the body computation and the `or _empty` clause are removed.
    end = next((i for i in range(start, len(lines))
                if lines[i].strip().startswith("if miss or len(hl) > 60")), None)
    if end is None:
        print("FAIL - case (t10-red): could not find the end of the check")
        return False
    mutant_lines = (lines[:start]
                    + [lines[end].replace(" or _empty:", ":")]
                    + [l for l in lines[end + 1:]
                       if "_empty" not in l])
    mutant_text = "".join(mutant_lines)
    if mutant_text == src:
        print("FAIL - case (t10-red): INCONCLUSIVE — the mutation did not change the source")
        return False

    mpath = os.path.join(os.path.dirname(os.path.realpath(SCRIPT)),
                         ".mutant-check-state-t10.sh")
    try:
        with open(mpath, "w") as f:
            f.write(mutant_text)
        shutil.copymode(SCRIPT, mpath)
        with tempfile.TemporaryDirectory() as tmp:
            _handoff_fixture(tmp, "Building",
                             {"handoff-plan.md": _empty_section(HANDOFF_GOOD, "## next")})
            env = dict(os.environ)
            env = _root_env(tmp, env)
            real = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
            mut = subprocess.run([mpath], cwd=tmp, capture_output=True, text=True, env=env)
        n_real = len(_shape_lines(real.stdout, "handoff-plan.md"))
        n_mut = len(_shape_lines(mut.stdout, "handoff-plan.md"))
        if n_mut >= n_real:
            print(f"FAIL - case (t10-red): INCONCLUSIVE — original {n_real}, mutant {n_mut}; "
                  f"the mutant did not lose the finding")
            return False
        print(f"ok - case (t10-red): the empty-body check is load-bearing — original "
              f"{n_real}, mutant {n_mut}")
        return True
    finally:
        if os.path.exists(mpath):
            os.remove(mpath)

# --- T-05 (FEAT-26): INV-28 — a Done feature whose pull request number was never
# recorded. Warn level, gated on github.sync, one line per offending feature.
#
# WHY SIX CASES AND NOT ONE. The four silence cases are what stop an always-warn
# implementation passing the first: `pr` recorded, `Abandoned`, non-terminal, and sync off
# are each a separate reason to say nothing, and an implementation can get one right and
# the rest wrong. The per-feature naming case exists because a single aggregate count
# cannot tell the operator WHICH feature to run the remedy on.

def _inv28_fixture(tmp, sync_on, features):
    """features: list of (feat_id, status, pr_literal_or_None). pr None omits the key."""
    h = os.path.join(tmp, ".harness")
    os.makedirs(h, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(HARNESS_JSON_SYNC_ON if sync_on else HARNESS_JSON_SYNC_OFF)
    for feat, status, pr in features:
        d = os.path.join(h, "harness", "features", feat)
        os.makedirs(d, exist_ok=True)
        body = '{\n  "feature_id": "%s",\n  "status": "%s"' % (feat, status)
        if pr is not None:
            body += ',\n  "pr": %s' % pr
        body += "\n}\n"
        with open(os.path.join(d, "feature.json"), "w") as f:
            f.write(body)
    return h


def case_inv28_warns():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28", "Done", None)])
        _code, out = run(tmp)
        ok = "INV-28" in out and "FEAT-T28" in out and "record-pr" in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 warns on a Done feature whose pr is null")
        return ok


def case_inv28_silent_on_integer():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28", "Done", "543")])
        _code, out = run(tmp)
        ok = "INV-28" not in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 is silent on a Done feature whose pr is an integer")
        return ok


def case_inv28_silent_on_abandoned():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28", "Abandoned", None)])
        _code, out = run(tmp)
        ok = "INV-28" not in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 is silent on an Abandoned feature whose pr is null")
        return ok


def case_inv28_silent_on_nonterminal():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28", "Building", None)])
        _code, out = run(tmp)
        ok = "INV-28" not in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 is silent on a feature that is not terminal")
        return ok


def case_inv28_names_each():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28A", "Done", None), ("FEAT-T28B", "Done", None)])
        _code, out = run(tmp)
        lines = [l for l in out.splitlines() if "INV-28" in l]
        ok = (len(lines) == 2
              and any("FEAT-T28A" in l for l in lines)
              and any("FEAT-T28B" in l for l in lines))
        print(f"{'ok' if ok else 'FAIL'} - INV-28 names each offending feature on its own line")
        return ok


def case_inv28_silent_sync_off():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, False, [("FEAT-T28", "Done", None)])
        _code, out = run(tmp)
        ok = "INV-28" not in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 is silent when github.sync is off")
        return ok


# --- FEAT-34 T-07 — INV-29 -----------------------------------------------------------
#
# BUILT WITH REAL GIT, for case_u's stated reason and one more of its own. INV-29 reads
# `git worktree list --porcelain` through worktree_terminal, so a hand-built `.git` pointer
# never appears in that output and every assertion would pass vacuously. It ALSO reads the
# feature's status from the DEFAULT BRANCH via `git show`, so a fixture that only writes a
# file on disk grades nothing about REQ-05.

def _i29_repo(path, branch="main"):
    os.makedirs(path, exist_ok=True)
    for cmd in (["git", "init", "-q", "-b", branch],
                ["git", "config", "user.email", "t@example.com"],
                ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, cwd=path, capture_output=True)
    with open(os.path.join(path, "f.txt"), "w") as f:
        f.write("x\n")
    subprocess.run(["git", "add", "f.txt"], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=path, capture_output=True)
    return path


def _i29_land(repo, feature_id, status_or_raw, repo_segment="harness"):
    """Commit the feature's `feature.json` ON THE CURRENT BRANCH. `status_or_raw` is a dict
    written as JSON, or a raw string written verbatim for the unparseable case."""
    rel = os.path.join(".harness", repo_segment, "features", feature_id, "feature.json")
    ab = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(ab), exist_ok=True)
    with open(ab, "w") as f:
        if isinstance(status_or_raw, str):
            f.write(status_or_raw)
        else:
            json.dump(status_or_raw, f)
    subprocess.run(["git", "add", rel], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "land " + feature_id], cwd=repo, capture_output=True)


def _i29_wt(repo, worktree_id, repo_segment="harness"):
    dest = os.path.join(repo, ".claude", "worktrees", repo_segment, worktree_id)
    subprocess.run(["git", "worktree", "add", "-q", "-b", "wt-" + worktree_id,
                    dest, "HEAD"], cwd=repo, capture_output=True)
    return dest


def _i29_lines(out):
    return [l for l in out.splitlines() if "INV-29" in l]


def _i29_for(out, path):
    real = os.path.realpath(path)
    return [l for l in _i29_lines(out) if path in l or real in l]


def case_inv29():
    """INV-29 (FEAT-34 T-07): a worktree must not survive its feature reaching a terminal
    state. Six lettered groups, each asserted separately.

    SEVERITY IS ASSERTED ON THE FINDING LINE'S OWN PREFIX, NEVER ON THE RUN'S EXIT CODE.
    `:1214-1218` above already records as a measurement that these fixtures are red for other
    reasons, so a comparison against a non-zero exit code passes whether or not the invariant
    fired. Every assertion below reads the INV-29 line itself.
    """
    results = []

    # ---- (a) the firing pair, and its PAIRED SILENCE ------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "A"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Done"})
        wt = _i29_wt(r, "FEAT-T29")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        lines = _i29_for(out, wt)
        ok = len(lines) == 1 and lines[0].strip().startswith("VIOLATION")
        results.append(("(a.1) default branch Done + standing worktree -> one INV-29 at "
                        "VIOLATION", ok, "\n".join(_i29_lines(out))))

    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "A2"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Review"})
        wt = _i29_wt(r, "FEAT-T29")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        # THE PAIRED SILENCE IS NOT DECORATION. Without it the group cannot tell a working
        # invariant from one that flags every worktree it sees.
        ok = not _i29_for(out, wt)
        results.append(("(a.2) the SAME fixture at Review -> no INV-29 line at all", ok,
                        "\n".join(_i29_lines(out))))

    # ---- (b) the message, graded as composed content, not as a substring ----------------
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "B"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Done"})
        _i29_land(r, "FEAT-OTHER", {"feature_id": "FEAT-OTHER", "status": "Done"})
        wt = _i29_wt(r, "FEAT-T29")
        other = _i29_wt(r, "FEAT-OTHER")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        mine = _i29_for(out, wt)
        line = mine[0] if mine else ""
        # THE THREE RED INPUTS THE CRITERION NAMES, each its own claim:
        #   1. a message naming the directory but carrying NO command;
        #   2. a bare removal command with no identity in it;
        #   3. a command carrying ANOTHER worktree's identity.
        names_dir = wt in line or os.path.realpath(wt) in line
        has_cmd = "feature-worktree.py remove" in line
        carries_own = "--id FEAT-T29" in line and "--repo harness" in line
        not_other = "FEAT-OTHER" not in line
        results.append(("(b.1) the line NAMES the worktree directory found", names_dir, line))
        results.append(("(b.2) the line CARRIES the removal command", has_cmd, line))
        results.append(("(b.3) the command carries THIS worktree's own repo and id",
                        carries_own, line))
        results.append(("(b.4) and NOT the sibling worktree's identity", not_other, line))
        # The sibling must get its OWN line — proving the composition is per record and not
        # one message reused.
        theirs = _i29_for(out, other)
        ok_sib = len(theirs) == 1 and "--id FEAT-OTHER" in theirs[0]
        results.append(("(b.5) the sibling worktree gets its own line with its own id",
                        ok_sib, "\n".join(theirs)))

    # ---- (c) SC-02, THE DEADLOCK: the default branch decides, never the working tree -----
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "C"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Review"})
        wt = _i29_wt(r, "FEAT-T29")
        # The WORKING TREE inside the worktree says Done; the default branch still says
        # Review. An implementation reading the working tree fires here and must not.
        wpath = os.path.join(wt, ".harness", "harness", "features", "FEAT-T29",
                             "feature.json")
        os.makedirs(os.path.dirname(wpath), exist_ok=True)
        with open(wpath, "w") as f:
            json.dump({"feature_id": "FEAT-T29", "status": "Done"}, f)
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        ok = not _i29_for(out, wt)
        results.append(("(c.1) working tree Done, default branch Review -> silent", ok,
                        "\n".join(_i29_lines(out))))

    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "C2"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Done"})
        wt = _i29_wt(r, "FEAT-T29")
        wpath = os.path.join(wt, ".harness", "harness", "features", "FEAT-T29",
                             "feature.json")
        with open(wpath, "w") as f:
            json.dump({"feature_id": "FEAT-T29", "status": "Review"}, f)
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        ok = len(_i29_for(out, wt)) == 1
        # BOTH HALVES ARE ASSERTED. A working-tree read fails c.1 by firing and fails c.2 by
        # staying silent, so the pair is what demonstrates the failing state, not either one.
        results.append(("(c.2) the INVERSE — default branch Done, working tree Review -> "
                        "one line", ok, "\n".join(_i29_lines(out))))

    # ---- (d) SC-03, the dirty clauses, graded ONE AT A TIME -----------------------------
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "D"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Done"})
        wt = _i29_wt(r, "FEAT-T29")
        with open(os.path.join(wt, "f.txt"), "a") as f:
            f.write("dirty\n")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        mine = _i29_for(out, wt)
        line = mine[0] if mine else ""
        results.append(("(d.1) a dirty Done worktree still fires", bool(mine), line))
        results.append(("(d.2) the message says the tree is DIRTY", "dirty" in line.lower(),
                        line))
        # NOT ONE COMBINED SUBSTRING. The two claims are separate because a message could
        # carry either alone and a single match would not notice.
        results.append(("(d.3) and says remove will DECLINE until the changes are dealt with",
                        "DECLINE" in line, line))

    # ---- (e) SC-04, a SECOND repository, from ONE check-state.sh run --------------------
    #
    # THE FIXTURE IS FLEET-RESOLVED, per D-10, and is NOT a directory placed under the
    # harness checkout's own WORKTREES_SEGMENT — no such second repository can exist, because
    # feature-worktree.py's dest_for joins WORKTREES_SEGMENT only to a resolved owner_root.
    # RED PROOF: an INV-29 built on classify(root) rather than classify_all(root) satisfies
    # (a) through (d) and (f) and fails exactly this.
    with tempfile.TemporaryDirectory() as tmp:
        probe = _i29_repo(os.path.join(tmp, "P"))
        # THE MARKER IS LOAD-BEARING, not scaffolding. factory_config resolves FLEET_PATH
        # through harness_boundary.resolve_root, which honours the override only when that
        # directory holds a readable .harness/team-config.yaml — otherwise it falls back to
        # the SCRIPT's own location and FLEET_PATH resolves to the REAL harness fleet.
        # Without this file the case reads the live fleet.yaml, finds no declared checkout on
        # disk, and passes or fails for a reason that has nothing to do with the fixture.
        # A docs/SPEC.md probe stood here until FEAT-42 T-04 replaced the resolver.
        _mp = os.path.join(probe, _hb.MARKER)
        os.makedirs(os.path.dirname(_mp), exist_ok=True)
        with open(_mp, "w") as f:
            f.write("agents: {}\n")
        ws = os.path.join(tmp, "ws")
        os.makedirs(ws, exist_ok=True)
        second = _i29_repo(os.path.join(ws, "second"))
        _i29_land(second, "FEAT-T29B", {"feature_id": "FEAT-T29B", "status": "Done"},
                  repo_segment="second")
        wt2 = _i29_wt(second, "FEAT-T29B", repo_segment="second")
        fdir = os.path.join(probe, ".harness", "factory")
        os.makedirs(fdir, exist_ok=True)
        with open(os.path.join(fdir, "fleet.yaml"), "w") as f:
            f.write("schema: factory-fleet/1\n"
                    "repos:\n"
                    "  - name: t/second\n"
                    "    default_branch: main\n"
                    "workspace_root: %s\n" % ws)
        make_fixture(probe, '{}', "  parent: 40")
        _c, out = run(probe)
        lines = _i29_for(out, wt2)
        ok = len(lines) == 1 and lines[0].strip().startswith("VIOLATION")
        results.append(("(e) a Done feature's worktree in a SECOND fleet-declared repository "
                        "produces an INV-29 line from ONE run", ok,
                        "\n".join(_i29_lines(out))))

    # ---- (f) SC-05, ONE fixture, four worktrees, four separate assertions ---------------
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "F"))
        _i29_land(r, "FEAT-FULL", {"feature_id": "FEAT-FULL", "status": "Done"})
        _i29_land(r, "FEAT-SHORT-named-in-full",
                  {"feature_id": "FEAT-SHORT-named-in-full", "status": "Done"})
        _i29_land(r, "FEAT-BAD", "{not json at all")
        wt_absent = _i29_wt(r, "FEAT-GONE")          # no landed dir at all
        wt_full = _i29_wt(r, "FEAT-FULL")
        wt_short = _i29_wt(r, "FEAT-SHORT")          # landed dir is the FULL name
        wt_bad = _i29_wt(r, "FEAT-BAD")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        results.append(("(f.1) genuinely absent from the default branch -> SILENT",
                        not _i29_for(out, wt_absent), "\n".join(_i29_lines(out))))
        results.append(("(f.2) a full-named Done sibling -> fires",
                        len(_i29_for(out, wt_full)) == 1, "\n".join(_i29_lines(out))))
        # f.3 AND f.4 ARE THE RED PROOF. An implementation keying the exemption on "the
        # lookup returned nothing" passes f.1 and f.2 and fails both of these — which is the
        # over-suppression that would make every refusal in REQ-01..REQ-05 silently stop.
        short_lines = _i29_for(out, wt_short)
        results.append(("(f.3) a SHORT-named worktree whose landed dir is full-named and "
                        "Done -> fires", len(short_lines) == 1,
                        "\n".join(_i29_lines(out))))
        # THE MESSAGE IS READ, NOT JUST COUNTED. Firing is not enough: the printed command has to
        # be RUNNABLE. `--id` must be the worktree DIRECTORY's own name, because that is what
        # `feature-worktree.py remove` matches; the record's feature_id is the LANDED directory,
        # which for a short-named worktree is a different string and yields
        # "not a linked worktree" for a directory plainly sitting in front of the reader.
        # (f.3) counted the line and never read it, which is exactly how that shipped.
        short_line = short_lines[0] if short_lines else ""
        results.append(("(f.4) the SHORT-named worktree's command carries its OWN directory name",
                        "--id FEAT-SHORT`" in short_line, short_line))
        results.append(("(f.5) and NOT the landed full name",
                        "--id FEAT-SHORT-named-in-full" not in short_line, short_line))
        # ---- SC-17 clause (c): THE PRINTED COMMAND IS EXECUTED, not merely read ----------
        #
        # (f.4) and (f.5) grade the command's TEXT. Text can be right and the command still fail,
        # which is the whole reason SC-17 exists: sixteen criteria graded INV-29 and none of them
        # ever ran what it printed. This clause runs it verbatim and asserts the worktree is gone.
        #
        # THE SAFETY ASSERTION IS NOT OPTIONAL. feature-worktree.py resolves owner_root
        # through harness_boundary.resolve_root, which honours the override only when that
        # directory holds a readable .harness/team-config.yaml. Without the marker it falls
        # back to the SCRIPT's own location — the REAL harness checkout — and this case
        # would run a DELETE against a live worktree. So the marker is written first and the
        # resolver is asked, in a separate process with this case's exact environment, where
        # it lands BEFORE anything is removed.
        _mp = os.path.join(r, _hb.MARKER)
        os.makedirs(os.path.dirname(_mp), exist_ok=True)
        with open(_mp, "w") as f:
            f.write("agents: {}\n")
        import shlex
        m = re.search(r"`python3 ([^`]+)`", short_line) if short_line else None
        ran_ok = False
        gone = False
        run_it = False
        inside = False
        detail = "no command found in the line"
        if m:
            argv = [sys.executable] + shlex.split(m.group(1))
            # THE SCRIPT PATH IS RESOLVED AGAINST THE REAL BIN DIR; EVERY OTHER ARGUMENT IS
            # VERBATIM. The printed command is repo-relative, and an operator runs it from their
            # own checkout where that path exists. A tmpdir fixture has no bin/ of its own, so
            # only argv[1] is rewritten to the real script — the `--repo` and `--id` values SC-17
            # actually grades are untouched, and the override below points the resolver at
            # the fixture. Copying the whole bin dir in would test the copy, not the message.
            argv[1] = os.path.join(os.path.dirname(SCRIPT), os.path.basename(argv[1]))
            env = dict(os.environ)
            env = _root_env(r, env)
            env["HARNESS_PROJECT_DIR"] = r
            # THE GUARD THAT ACTUALLY BITES. What stood here compared wt_short against r —
            # both built from r, so it was true whatever the resolver decided and protected
            # nothing. Ask the resolver instead, with this case's exact environment, and
            # REFUSE to run the delete unless it lands inside the fixture.
            _bin = os.path.dirname(os.path.realpath(__file__))
            _where = subprocess.run(
                [sys.executable, "-c",
                 "import sys; sys.path.insert(0, sys.argv[1]); import harness_boundary as h; "
                 "print(h.resolve_root(sys.argv[1]))", _bin],
                capture_output=True, text=True, env=env, cwd=r).stdout.strip()
            inside = bool(_where) and os.path.realpath(_where) == os.path.realpath(r)
            run_it = inside
            if not inside:
                detail = ("REFUSED to run the delete: the resolver landed on %r, not the "
                          "fixture %r" % (_where, r))
        if run_it:
            probe = subprocess.run(argv,
                                   capture_output=True, text=True, env=env, cwd=r)
            ran_ok = probe.returncode == 0
            gone = not os.path.exists(wt_short)
            detail = ("exit=%d resolved_root_is_fixture=%s stdout=%s stderr=%s"
                      % (probe.returncode, inside,
                         probe.stdout.strip()[-200:], probe.stderr.strip()[-200:]))
        # THE REWRITE ABOVE HAS A COST AND THIS CLOSES IT. Rewriting argv[1] means the run does
        # NOT prove the printed script path resolves in a real checkout — so that is asserted
        # separately, against the real root. The path is repo-relative and may reach the tree
        # through the .agents compatibility symlink; what matters is that it resolves at all.
        printed_rel = shlex.split(m.group(1))[0] if m else ""
        real_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(SCRIPT)))))
        results.append(("(f.9) SC-17(c): the printed script path resolves in a real checkout",
                        bool(printed_rel) and os.path.exists(
                            os.path.join(real_root, printed_rel)),
                        "printed=%r real_root=%r" % (printed_rel, real_root)))
        results.append(("(f.7) SC-17(c): the printed command RUNS and exits 0", ran_ok, detail))
        results.append(("(f.8) SC-17(c): and that worktree is GONE afterwards", gone, detail))

        results.append(("(f.6) a landed feature.json that is present but UNPARSEABLE -> "
                        "fires", len(_i29_for(out, wt_bad)) == 1,
                        "\n".join(_i29_lines(out))))

    ok_all = True
    for label, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - INV-29 {label}")
        if not ok and detail:
            print("      saw: " + detail.replace("\n", "\n      "))
        ok_all = ok_all and ok
    return ok_all


def _inv30_fixture(tmp, features):
    """features: list of (feat_id, status, milestone_or_None). milestone None writes
    `"milestone": null`, which is the shape eight real features carry at 9165162."""
    h = os.path.join(tmp, ".harness")
    os.makedirs(h, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(HARNESS_JSON_SYNC_ON)
    for feat, status, ms in features:
        d = os.path.join(h, "harness", "features", feat)
        os.makedirs(d, exist_ok=True)
        body = ('{\n  "feature_id": "%s",\n  "status": "%s",\n'
                '  "github": {"milestone": %s}\n}\n'
                % (feat, status, "null" if ms is None else int(ms)))
        with open(os.path.join(d, "feature.json"), "w") as f:
            f.write(body)
    return h


def _inv30_gh_stub(tmp, open_numbers, auth_ok=True):
    """A fake `gh` on FACTORY_GH. NO CASE HERE MAKES A REAL NETWORK CALL.

    It answers exactly the two shapes INV-30 issues: `auth status`, and the paginated
    milestone list filtered to `.[].number`. Anything else exits 1, so a future INV-30 that
    started asking a THIRD question would fail loudly here rather than silently reading an
    empty answer as "nothing is open"."""
    path = os.path.join(tmp, "gh-stub-%d" % (0 if auth_ok else 1))
    with open(path, "w") as f:
        f.write("#!/bin/sh\n")
        f.write('if [ "$1" = "auth" ]; then exit %d; fi\n' % (0 if auth_ok else 1))
        f.write('case "$*" in\n')
        f.write('  *milestones*)\n')
        if auth_ok:
            for n in open_numbers:
                f.write('    echo %d\n' % int(n))
        f.write('    exit %d ;;\n' % (0 if auth_ok else 1))
        f.write('  *) exit 1 ;;\n')
        f.write('esac\n')
    os.chmod(path, 0o755)
    return path


def _inv30_lines(out):
    return [l for l in out.splitlines() if "INV-30" in l]


def case_inv30_fires_on_open_milestone():
    """SC-12 clause one. SEVERITY IS ASSERTED ON THE LINE'S OWN PREFIX, never on the run's
    exit code — `test-check-state.py:1214` already records that these fixtures are red for
    other reasons, so `code != 0` would pass whether or not the invariant fired."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv30_fixture(tmp, [("FEAT-T30", "Done", 77)])
        gh = _inv30_gh_stub(tmp, [77])
        _code, out = _run_with_gh(tmp, gh)
        lines = _inv30_lines(out)
        ok = (len(lines) == 1
              and lines[0].strip().startswith("VIOLATION")
              and "FEAT-T30" in lines[0]
              and "77" in lines[0]
              and "gh-sync.py ship" in lines[0])
        print(f"{'ok' if ok else 'FAIL'} - INV-30 fires at VIOLATION on a Done feature whose "
              f"milestone is open, naming the feature, the number and the remedy")
        return ok


def case_inv30_silent_on_closed_milestone():
    """SC-12 clause two, THE DISCRIMINATING ONE. Same fixture, same `status: Done` — only the
    stub's answer changes. An implementation keying on status alone passes the case above and
    fails this one, which is exactly the red proof the criterion names."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv30_fixture(tmp, [("FEAT-T30", "Done", 77)])
        gh = _inv30_gh_stub(tmp, [])          # 77 is not in the open list
        _code, out = _run_with_gh(tmp, gh)
        lines = _inv30_lines(out)
        ok = not lines
        print(f"{'ok' if ok else 'FAIL'} - INV-30 is silent when the SAME Done feature's "
              f"milestone is closed (status is Done in both halves)")
        return ok


def case_inv30_silent_offline():
    """SC-12 clause three, and it is TWO claims, not one: no INV-30 line AND no error. This
    grades the INV-26 offline posture the design copies deliberately — `check-state.sh` runs
    before every commit, so an unreachable network must never become a red gate."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv30_fixture(tmp, [("FEAT-T30", "Done", 77)])
        gh = _inv30_gh_stub(tmp, [77], auth_ok=False)
        _code, out, err = _run_with_gh_streams(tmp, gh)
        lines = _inv30_lines(out)
        # THE SECOND READER IS NOT DECORATION. A traceback goes to stderr, so a case that
        # reads stdout alone cannot see the gate abort — the measurement recorded at
        # `_run_with_gh_streams`.
        ok = (not lines
              and "INV-30 CANNOT RUN" not in out
              and "Traceback" not in err)
        print(f"{'ok' if ok else 'FAIL'} - INV-30 records nothing and raises no error when "
              f"gh is unauthenticated")
        return ok


def case_inv30_silent_on_null_milestone():
    """A Done feature with no recorded milestone is OUTSIDE this invariant's reach, not a
    finding. Eight real features are in that state at `9165162`; firing on them would make the
    gate permanently red for a condition INV-30 cannot speak to."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv30_fixture(tmp, [("FEAT-T30", "Done", None)])
        gh = _inv30_gh_stub(tmp, [77])
        _code, out = _run_with_gh(tmp, gh)
        ok = not _inv30_lines(out)
        print(f"{'ok' if ok else 'FAIL'} - INV-30 is silent on a Done feature whose recorded "
              f"milestone is null")
        return ok


def case_inv30_silent_on_nonterminal():
    """DEC-203's six status values are case sensitive and only the exact string `Done` is
    checked. A feature still in Review has not claimed that ship ran, so an open milestone is
    the CORRECT state for it and reporting it would be noise."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv30_fixture(tmp, [("FEAT-T30", "Review", 77)])
        gh = _inv30_gh_stub(tmp, [77])
        _code, out = _run_with_gh(tmp, gh)
        ok = not _inv30_lines(out)
        print(f"{'ok' if ok else 'FAIL'} - INV-30 is silent on a non-terminal feature whose "
              f"milestone is open")
        return ok



# ---------------------------------------------------------------------------------------------
# INV-31 (FEAT-40 T-08): this clone's merge hook is not installed.
#
# EVERY FIXTURE IS A REAL GIT REPOSITORY, because the invariant reads `git config --get
# core.hooksPath` in the checkout it is invoked in. A plain temp directory would answer "unset"
# for the wrong reason and the silent case could never be built at all.
# ---------------------------------------------------------------------------------------------

_HOOKS_REL_T = os.path.join(".claude", "skills", "harness", "hooks")


def _inv31_fixture(tmp, hooks_path=None, post_merge="executable"):
    """A git repo carrying a minimal .harness, with core.hooksPath and the hook file under the
    caller's control.

    `hooks_path` None leaves the config unset. `post_merge` is "executable", "plain" (present
    but mode 0644) or "absent"."""
    subprocess.run(["git", "init", "-q"], cwd=tmp, capture_output=True)
    h = os.path.join(tmp, ".harness")
    os.makedirs(os.path.join(h, "harness", "features"), exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write('{"github": {"sync": false}}\n')
    hooks_dir = os.path.join(tmp, _HOOKS_REL_T)
    os.makedirs(hooks_dir, exist_ok=True)
    if post_merge != "absent":
        pm = os.path.join(hooks_dir, "post-merge")
        with open(pm, "w") as f:
            f.write("#!/usr/bin/env bash\nexit 0\n")
        os.chmod(pm, 0o755 if post_merge == "executable" else 0o644)
    if hooks_path is not None:
        subprocess.run(["git", "config", "core.hooksPath", hooks_path],
                       cwd=tmp, capture_output=True)
    return h


def _inv31_lines(out):
    return [l for l in out.splitlines() if "INV-31" in l]


def case_inv31_unset():
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=None)
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = (len(lines) == 1
              and lines[0].strip().startswith("VIOLATION")
              and "unset" in lines[0]
              and _HOOKS_REL_T in lines[0]
              and "git config core.hooksPath" in lines[0])
        print(f"{'ok' if ok else 'FAIL'} - INV-31 fires at VIOLATION when core.hooksPath is "
              f"unset, saying so and carrying the fix command"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_wrong_value():
    """THE VALUE FOUND IS REPORTED. An operator who cannot see what it currently reads has to
    go and run the command themselves before they can act on the line."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=".git/hooks")
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = (len(lines) == 1
              and lines[0].strip().startswith("VIOLATION")
              and ".git/hooks" in lines[0]
              and "no harness hook runs" in lines[0])
        print(f"{'ok' if ok else 'FAIL'} - INV-31 fires when core.hooksPath names another "
              f"directory, quoting the value found"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_absolute_same_dir_passes():
    """AN ABSOLUTE VALUE NAMING THE SAME DIRECTORY IS FINE. The comparison resolves both sides
    to real paths on purpose; a string comparison would call a working clone broken."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=os.path.join(tmp, _HOOKS_REL_T))
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = not lines
        print(f"{'ok' if ok else 'FAIL'} - INV-31 is silent when an ABSOLUTE core.hooksPath "
              f"names the same directory"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_post_merge_absent():
    """A SECOND FINDING WITH A DIFFERENT SUBJECT. The first is a misconfigured clone; this is a
    damaged checkout. Different fixes, so they must never collapse into one message."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=_HOOKS_REL_T, post_merge="absent")
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = (len(lines) == 1
              and lines[0].strip().startswith("VIOLATION")
              and "post-merge is missing" in lines[0]
              and "restore it" in lines[0]
              and "core.hooksPath" not in lines[0])
        print(f"{'ok' if ok else 'FAIL'} - INV-31 reports a MISSING post-merge as its own "
              f"finding, with its own fix, never as a tail on the config one"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_post_merge_not_executable():
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=_HOOKS_REL_T, post_merge="plain")
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = (len(lines) == 1
              and lines[0].strip().startswith("VIOLATION")
              and "not executable" in lines[0]
              and "644" in lines[0]
              and "chmod +x" in lines[0])
        print(f"{'ok' if ok else 'FAIL'} - INV-31 reports a NON-EXECUTABLE post-merge, naming "
              f"the mode it found and the fix"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_silent_when_installed():
    """THE DISCRIMINATING CASE. An invariant that fires on everything is not a check."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=_HOOKS_REL_T, post_merge="executable")
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = not lines
        print(f"{'ok' if ok else 'FAIL'} - INV-31 is SILENT when the hook is installed and "
              f"executable"
              + ("" if ok else f"\n      {lines}"))
        return ok


def _inv32_plan(panel_marker=True, finding=None, rulings=None, readers=None,
                date="2026-08-31"):
    # `date` is approval.date, the era key INV-32 grades on. It defaults to a POST-era
    # date so every pre-existing case below is unchanged by the era guard. `date=None`
    # omits the key entirely — an approved plan whose era cannot be placed at all.
    approval = {"status": "approved", "approved_by": "operator"}
    if date is not None:
        approval["date"] = date
    doc = {
        "schema": "plan/1", "feature": "FEAT-INV32",
        "approval": approval,
        "lanes": {"resolved_at": "abc123", "rows": []}, "decisions": [],
        "tasks": [{"id": "T-01", "title": "fixture", "traces": ["REQ-01"],
                   "change_type": "logic", "execution_mode": "main-session-direct",
                   "execution_reason": "fixture", "depends_on": [], "status": "pending",
                   "files": ["fixture"], "verify": "true", "intent": "fixture"}],
    }
    if panel_marker:
        doc["panel"] = {"last_run": "panel-validator", "cycle": 0,
                        "findings": finding or [], "readers": readers if readers is not None else [
                            {"reader": "should-not-exist", "status": "ran"},
                            {"reader": "scope", "status": "ran"},
                            {"reader": "goalcheck", "status": "ran"}]}
    if rulings is not None:
        doc["approval"]["rulings"] = rulings
    return doc


# BUG-1071 F2 — `era` plants `.harness/harness.json` so a case can exercise a PROJECT'S
# OWN boundary. The default is `_NO_CONFIG`: no harness.json at all, which is what every
# pre-existing INV-32 case above relies on. With no config there is no pre-panel era, so
# every approved plan is graded and those cases keep asserting exactly what they always
# asserted. `era=None` writes a config whose `panel_era_start` is null; `era="..."` writes
# that date; `era=_NO_KEY` writes a config with the key absent entirely, which is the
# un-upgraded project.
_NO_CONFIG = object()
_NO_KEY = object()


def _inv32_run(doc, script=SCRIPT, era=_NO_CONFIG):
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, ".harness", "harness", "features", "FEAT-INV32")
        os.makedirs(root, exist_ok=True)
        with open(os.path.join(root, "plan.yaml"), "w") as f:
            json.dump(doc, f)
        if era is not _NO_CONFIG:
            cfg = {"schema_version": 2}
            if era is not _NO_KEY:
                cfg["panel_era_start"] = era
            with open(os.path.join(tmp, ".harness", "harness.json"), "w") as f:
                json.dump(cfg, f)
        env = _root_env(tmp)
        proc = subprocess.run([script], cwd=tmp, capture_output=True, text=True, env=env)
        return proc.returncode, proc.stdout, proc.stderr


def case_inv32_unrated_severity_fails_closed():
    """Unrated, absent, and null severities all withhold approval."""
    findings = [
        {"id": "PF-unrated", "severity": "unrated", "disposition": "open"},
        {"id": "PF-absent", "disposition": "open"},
        {"id": "PF-null", "severity": None, "disposition": "open"},
    ]
    code, out, _ = _inv32_run(_inv32_plan(finding=findings))
    ok = code == 1 and all(finding["id"] in out for finding in findings)
    print(f"{'ok' if ok else 'FAIL'} - INV-32 unrated severities fail closed"
          + ("" if ok else f"\n      {out}"))
    return ok


def _inv32_basic_checks(open_finding, resolved, fid):
    code, no_panel, _ = _inv32_run(_inv32_plan(panel_marker=False))
    _, high_open, _ = _inv32_run(_inv32_plan(finding=open_finding))
    _, high_resolved, _ = _inv32_run(_inv32_plan(finding=resolved))
    resolved_lines = [
        line for line in high_resolved.splitlines() if "FEAT-INV32" in line
    ]
    return [
        code == 1 and "INV-32" in no_panel and "FEAT-INV32" in no_panel,
        "INV-32" in high_open and fid in high_open,
        any(fid in line and "resolved" in line.lower() for line in resolved_lines)
        and not any("VIOLATION" in line for line in resolved_lines),
    ]


def _inv32_ruling_checks(open_finding, resolved, fid):
    ruling = [{"finding": fid, "ruling": "overrule", "who": "operator",
               "date": "2026-08-31", "reason": "accepted"}]
    _, overruled, _ = _inv32_run(_inv32_plan(finding=open_finding, rulings=ruling))
    overruled_lines = [
        line for line in overruled.splitlines() if "FEAT-INV32" in line
    ]
    bad_ruling = [{**ruling[0], "who": ""}]
    _, unattributed, _ = _inv32_run(
        _inv32_plan(finding=open_finding, rulings=bad_ruling)
    )
    stale = [{**ruling[0], "finding": "PF-cafebabe"}]
    _, stale_out, _ = _inv32_run(_inv32_plan(finding=resolved, rulings=stale))
    return [
        any(fid in line and "overruled" in line.lower() for line in overruled_lines)
        and not any("VIOLATION" in line for line in overruled_lines),
        "unattributed" in unattributed and fid in unattributed,
        all(text in stale_out for text in ("PF-cafebabe", "reworded", "asked again")),
    ]


def _inv32_missing_reader_check(missing):
    code, out, _ = _inv32_run(_inv32_plan(readers=missing))
    return code == 1 and "should-not-exist" in out and "never ran" in out


def _inv32_skipped_reader_check(missing):
    skipped = missing + [{"reader": "should-not-exist", "status": "skipped",
                          "persona": "fable-advisor", "reason": "not installed"}]
    _, out, _ = _inv32_run(_inv32_plan(readers=skipped))
    violations = [
        line for line in out.splitlines()
        if "INV-32" in line and "FEAT-INV32" in line and "VIOLATION" in line
    ]
    return (all(text in out for text in ("should-not-exist", "fable-advisor"))
            and not violations)


def _inv32_reader_checks(valid_readers):
    missing = [reader for reader in valid_readers
               if reader["reader"] != "should-not-exist"]
    return missing, [
        _inv32_missing_reader_check(missing),
        _inv32_skipped_reader_check(missing),
    ]


def _inv32_mutant_fixture_passes(doc, mutant):
    rc_real, text_real, _ = _inv32_run(doc)
    rc_mut, text_mut, err_mut = _inv32_run(doc, mutant)
    return (rc_real == 1 and "INV-32" in text_real
            and rc_mut in (0, 1) and "Traceback" not in err_mut
            and "INV-32" not in text_mut)


def _inv32_mutant_is_discriminating(missing):
    source = open(SCRIPT, encoding="utf-8").read()
    begin = "# INV-32 BEGIN (FEAT-45 T-07)"
    end = "# INV-32 END (FEAT-45 T-07)"
    mutant = os.path.join(os.path.dirname(SCRIPT), ".check-state-inv32-mutant.sh")
    try:
        assert begin in source and end in source
        left, rest = source.split(begin, 1)
        _region, right = rest.split(end, 1)
        changed = left + right
        assert changed != source
        with open(mutant, "w") as file:
            file.write(changed)
        shutil.copymode(SCRIPT, mutant)
        sc04_refusal = _inv32_plan(
            finding=[{"id": "PF-sc04", "severity": "high", "disposition": "open"}]
        )
        docs = (_inv32_plan(panel_marker=False), _inv32_plan(readers=missing),
                sc04_refusal)
        return all(_inv32_mutant_fixture_passes(doc, mutant) for doc in docs)
    finally:
        if os.path.exists(mutant):
            os.unlink(mutant)


def case_inv32():
    """Panel, ruling, reader, and mutation directions for INV-32."""
    fid = "PF-deadbeef"
    open_finding = [{"id": fid, "severity": "high", "reader": "scope",
                     "summary": "x", "disposition": "open"}]
    resolved = [{**open_finding[0], "disposition": "resolved", "resolved_by": "T-01"}]
    valid_readers = [{"reader": reader, "status": "ran"}
                     for reader in ("should-not-exist", "scope", "goalcheck")]
    missing, reader_checks = _inv32_reader_checks(valid_readers)
    checks = (
        _inv32_basic_checks(open_finding, resolved, fid)
        + _inv32_ruling_checks(open_finding, resolved, fid)
        + reader_checks
        + [_inv32_mutant_is_discriminating(missing)]
    )
    ok = all(checks)
    print(f"{'ok' if ok else 'FAIL'} - INV-32 plan panel fixtures, including inv32-red"
          + ("" if ok else f" {checks}"))
    return ok


# BUG-1071 — INV-32's era guard. FEAT-45 T-07 shipped INV-32 with no era boundary, so it
# fired on all 32 approved plans in the tree and NONE could satisfy it: a plan signed
# before the adversarial panel existed cannot carry a record of it. FEAT-45's own plan,
# signed 2026-08-30, was among the 32. These cases pin the boundary in BOTH directions —
# a guard that only exempts is as wrong as no guard at all.
# THE ASSERTION IS THE VIOLATION LINE, NEVER THE EXIT CODE. A bare fixture holding only
# plan.yaml is red for reasons that have nothing to do with INV-32 — no BRIEF.md, no
# feature.json, no STATE.md — which is why every pre-existing INV-32 case above asserts
# `code == 1` and reads the text. An exit-code assertion here would pass or fail on those
# unrelated invariants instead of on the era guard, so it would not bind what it names.
def _inv32_violations(out):
    return [line for line in out.splitlines()
            if "FEAT-INV32" in line and "INV-32" in line and "VIOLATION" in line]


def _inv32_notes(out):
    return [line for line in out.splitlines()
            if "FEAT-INV32" in line and "INV-32" in line and "note" in line]


def case_inv32_pre_era_is_exempt():
    """A plan signed BEFORE the panel shipped is not graded, and says so out loud."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-30"),
                               era="2026-08-31")
    ok = not _inv32_violations(out) and bool(_inv32_notes(out))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 pre-era plan is exempt with a note"
          + ("" if ok else f"\n      {out}"))
    return ok


def case_inv32_era_boundary_is_exact():
    """2026-08-30 is exempt and 2026-08-31 is graded — the off-by-one that matters."""
    _rc_b, before, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-30"),
                                  era="2026-08-31")
    _rc_a, after, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-31"),
                                 era="2026-08-31")
    ok = not _inv32_violations(before) and bool(_inv32_violations(after))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 era boundary is exact "
          f"(08-30 exempt, 08-31 graded)"
          + ("" if ok else f"\n      before: {_inv32_violations(before)}"
                           f"\n      after:  {_inv32_violations(after)}"))
    return ok


def case_inv32_undated_approval_fails():
    """An approved plan with NO approval.date cannot be placed in an era, and that is a
    VIOLATION, not a note (panel finding F1). Warning here was a fail-open on a
    fail-closed invariant: nothing else in check-state.sh or harness_yaml requires the
    key, so omitting one line bought permanent silence from INV-32. The message must name
    approval.date, not the panel, because that is the defect and the remedy."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date=None),
                               era="2026-08-31")
    violations = _inv32_violations(out)
    ok = (bool(violations)
          and any("approval.date" in line for line in violations))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 undated approval is a violation naming approval.date"
          + ("" if ok else f"\n      {out}"))
    return ok


def case_inv32_era_guard_is_load_bearing():
    """Excise ONLY the era guard and the pre-era case must go red. Without this, an era
    guard that never runs is indistinguishable from one that does — the silent-zero shape
    this repository keeps finding."""
    source = open(SCRIPT, encoding="utf-8").read()
    begin = "# INV-32 ERA BEGIN (BUG-1071)"
    end = "# INV-32 ERA END (BUG-1071)"
    mutant = os.path.join(os.path.dirname(SCRIPT), ".check-state-inv32-era-mutant.sh")
    try:
        if begin not in source or end not in source:
            print("FAIL - INV-32 era guard markers absent; cannot mutate")
            return False
        left, rest = source.split(begin, 1)
        _region, right = rest.split(end, 1)
        with open(mutant, "w") as file:
            file.write(left + right)
        shutil.copymode(SCRIPT, mutant)
        pre_era = _inv32_plan(panel_marker=False, date="2026-08-30")
        _rc_real, real_out, _ = _inv32_run(pre_era, era="2026-08-31")
        _rc_mut, mut_out, mut_err = _inv32_run(pre_era, mutant, era="2026-08-31")
        ok = (not _inv32_violations(real_out)
              and bool(_inv32_violations(mut_out))
              and "Traceback" not in mut_err)
        print(f"{'ok' if ok else 'FAIL'} - INV-32 era guard is load-bearing "
              f"(real={len(_inv32_violations(real_out))} "
              f"mutant={len(_inv32_violations(mut_out))} violations)")
        return ok
    finally:
        if os.path.exists(mutant):
            os.unlink(mutant)


# BUG-1071 F2 — the boundary is the PROJECT'S, read from harness.json, not a literal
# compiled into a file that /harness-init copies everywhere. These four pin that the value
# actually comes from config and that every unreadable state fails closed.
def case_inv32_era_comes_from_project_config():
    """The SAME plan is exempt or graded depending only on the project's own
    `panel_era_start`. This is the case a hardcoded literal cannot pass: a plan signed
    2026-08-25 is pre-era for a project whose panel arrived 2026-08-31 and post-era for a
    project whose panel arrived 2026-08-20."""
    plan = _inv32_plan(panel_marker=False, date="2026-08-25")
    _rc1, late, _ = _inv32_run(plan, era="2026-08-31")
    _rc2, early, _ = _inv32_run(plan, era="2026-08-20")
    ok = not _inv32_violations(late) and bool(_inv32_violations(early))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 era boundary comes from harness.json, "
          f"not a literal"
          + ("" if ok else f"\n      era=08-31: {_inv32_violations(late)}"
                           f"\n      era=08-20: {_inv32_violations(early)}"))
    return ok


def case_inv32_null_era_grades_everything():
    """`panel_era_start: null` is the template default and means THIS PROJECT HAS NO
    PRE-PANEL ERA. A project onboarded after FEAT-45 never had plans the panel could not
    have reviewed, so nothing is exempt however old the signature looks."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2020-01-01"),
                               era=None)
    ok = bool(_inv32_violations(out))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 null panel_era_start exempts nothing"
          + ("" if ok else f"\n      {out}"))
    return ok


def case_inv32_missing_era_key_is_a_violation():
    """A config that predates the key is a VIOLATION naming it and the upgrade command,
    never a silent default. Defaulting either way is wrong for somebody: 'grade
    everything' reddens every pre-panel plan in an un-upgraded project, and 'exempt
    everything' disables INV-32 there without saying so."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-30"),
                               era=_NO_KEY)
    lines = [line for line in out.splitlines()
             if "INV-32" in line and "VIOLATION" in line and "panel_era_start" in line]
    ok = bool(lines) and any("--upgrade" in line for line in lines)
    print(f"{'ok' if ok else 'FAIL'} - INV-32 missing panel_era_start violates, naming "
          f"the upgrade command"
          + ("" if ok else f"\n      {out}"))
    return ok


def case_inv32_malformed_era_exempts_nothing():
    """An unreadable boundary exempts nothing and says why. The plan below would be exempt
    under a valid 2026-08-31, so this fails closed rather than falling back to it."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-30"),
                               era="last Tuesday")
    cfg = [line for line in out.splitlines()
           if "INV-32" in line and "VIOLATION" in line and "panel_era_start" in line]
    ok = bool(cfg) and bool(_inv32_violations(out))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 malformed panel_era_start exempts nothing"
          + ("" if ok else f"\n      {out}"))
    return ok


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
    skill = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SKILL.md")
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



def main():
    ok_a, code_a = case_a()
    ok_b, code_b = case_b()
    ok_c, _code_c = case_c()
    ok_d = case_d()
    ok_e = case_e()
    ok_f = case_f()
    ok_g = case_g()
    ok_h = case_h()
    ok_i = case_i()
    ok_j = case_j()
    ok_k = case_k()
    ok_l = case_l()
    ok_m = case_m()
    ok_m2 = case_m2()
    ok_m3 = case_m3()
    ok_n = case_n()
    ok_o = case_o()
    ok_i28a = case_inv28_warns()
    ok_i28b = case_inv28_silent_on_integer()
    ok_i28c = case_inv28_silent_on_abandoned()
    ok_i28d = case_inv28_silent_on_nonterminal()
    ok_i28e = case_inv28_names_each()
    ok_i28f = case_inv28_silent_sync_off()
    ok_p = case_p()
    ok_q = case_q()
    ok_r = case_r()
    ok_s = case_s()
    ok_t = case_t()
    ok_u = case_u()
    ok_v = case_v()
    ok_w = case_w()
    ok_x = case_x()

    # FEAT-34 T-09 — INV-30's three SC-12 clauses plus the two silences that keep it from
    # firing on states it cannot speak to. Every case stubs `gh` through FACTORY_GH; none
    # makes a network call.
    # FEAT-34 T-07 — INV-29's six lettered groups.
    ok_i29 = case_inv29()

    ok_i30 = all([
        case_inv30_fires_on_open_milestone(),
        case_inv30_silent_on_closed_milestone(),
        case_inv30_silent_offline(),
        case_inv30_silent_on_null_milestone(),
        case_inv30_silent_on_nonterminal(),
    ])

    # FEAT-31 T-14 — INV-17's shape pass over every handoff stem.
    ok_t14 = all([
        case_t14_widening(),
        case_t14_cap(),
        case_t14_no_double(),
        case_t14_exempt_shape(),
        case_t14_accepted(),
        case_t14_red(),
    ])

    # FEAT-31 T-10 — a required section with no body fails the shape (SC-15).
    ok_t10 = all([
        case_t10_accepted(),
        case_t10_next_emptied(),
        case_t10_trust_emptied(),
        case_t10_deadends_emptied(),
        case_t10_workingset_emptied(),
        case_t10_red(),
    ])

    ok_i31 = all([
        case_inv31_unset(),
        case_inv31_wrong_value(),
        case_inv31_absolute_same_dir_passes(),
        case_inv31_post_merge_absent(),
        case_inv31_post_merge_not_executable(),
        case_inv31_silent_when_installed(),
    ])
    ok_i32 = case_inv32()
    ok_i32_severity = case_inv32_unrated_severity_fails_closed()
    # BUG-1071 — the era guard, pinned in both directions plus its own mutant.
    ok_i32_era = all([
        case_inv32_pre_era_is_exempt(),
        case_inv32_era_boundary_is_exact(),
        case_inv32_undated_approval_fails(),
        case_inv32_era_guard_is_load_bearing(),
        # F2 — the boundary is per-project config, and every unreadable state fails closed.
        case_inv32_era_comes_from_project_config(),
        case_inv32_null_era_grades_everything(),
        case_inv32_missing_era_key_is_a_violation(),
        case_inv32_malformed_era_exempts_nothing(),
    ])

    # BUG-1080 — INV-6's plan-phase exemption, pinned in both directions.
    ok_i6_plan = all([
        case_inv6_plan_run_is_exempt(),
        case_inv6_code_run_still_fires(),
        case_inv6_unknown_grade_fails_closed(),
        case_inv6_mixed_runs_still_fire(),
        case_inv6_exempt_survives_signature(),
        case_inv6_pinned_plan_run_silent(),
        # BUG-1080 cycle 1 — the panel's blocking finding and its two questions.
        case_inv6_case_variant_is_not_exempt(),
        case_inv6_message_names_the_remedy(),
        case_inv6_producer_is_documented(),
    ])

    ok_exit_unchanged = code_a == code_b
    print(
        f"{'ok' if ok_exit_unchanged else 'FAIL'} - exit code unchanged by INV-21 "
        f"(a: {code_a}, b: {code_b})"
    )

    if (ok_a and ok_b and ok_c and ok_d and ok_e and ok_f and ok_g
            and ok_h and ok_i and ok_j and ok_k and ok_l and ok_m and ok_m2 and ok_m3 and ok_n and ok_o and ok_p and ok_q and ok_r and ok_s and ok_t and ok_u and ok_v and ok_w and ok_x and ok_t14 and ok_t10
            and ok_i28a and ok_i28b and ok_i28c and ok_i28d and ok_i28e and ok_i28f
            and ok_i29 and ok_i30 and ok_i31 and ok_i32 and ok_i32_severity
            and ok_i32_era and ok_i6_plan
            and ok_exit_unchanged):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
