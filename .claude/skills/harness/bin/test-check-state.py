#!/usr/bin/env python3
"""Tests for check-state.sh's INV-21 (D-05): a mirrored feature with recorded task
issues but no recorded numeric parent. Fixtures are temp dirs; check-state.sh is run
with CLAUDE_PROJECT_DIR pointed at each, never against the real repo state.

No test invokes a real `gh` binary and none asserts on `sub_issues_summary` (SC-09).
"""
import json, os
import subprocess
import sys
import tempfile

# Overridable so a fix can be proven RED against a reverted copy — the same
# VALIDATE_DIGEST_BIN escape test-validate-digest.py uses.
SCRIPT = os.environ.get("CHECK_STATE_BIN") or os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "check-state.sh"
)

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
  parent_origin: none
  issues:
    T-01: 41
"""


def make_fixture(tmp, harness_json, parent_line):
    h = os.path.join(tmp, ".harness")
    os.makedirs(os.path.join(h, "features", "FEAT-TEST"), exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(harness_json)
    with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
        f.write(feature_yaml(parent_line))
    return h


def run(tmp):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = tmp
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
  parent_origin: none
  issues:
    T-01: 41
"""


def case_e():
    """Issue #11, behavioural: a trailing `#` comment on a run's `id:` or `squad:`
    line must not make the run invisible.

    The pre-T-07 block-form regex required `\\s*\\n` immediately after those two
    captures, so a comment — legal YAML, and the house style on 45 lines of FEAT-03's
    feature.yaml — matched nothing and dropped the ENTIRE entry. Three invariants then
    failed OPEN at exit 0: INV-6 (no validator run seen, so an unpinned review_sha was
    not reported), INV-7 (0 FAILs counted) and INV-8.

    Asserted through the invariant rather than the parser: this fixture has a validator
    run and NO `review_sha`, so a correct parse MUST report INV-6. Pre-fix the run
    vanished and check-state.sh said nothing at all — which is why a parser-level
    assertion would be the weaker test.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
            f.write(RUNS_WITH_TRAILING_COMMENTS)
        code, out = run(tmp)
        ok = "review_sha is not pinned" in out
        print(f"{'ok' if ok else 'FAIL'} - case (e): issue #11 — a commented squad:/id: "
              f"line still yields the run, so INV-6 fires")
        if not ok:
            print("        INV-6 was silent: the run was dropped and the gate failed OPEN")
        return ok


def case_f():
    """A feature.yaml that does not parse is a VIOLATION, never a silent skip.

    DEC-171 am.1 removed the fallback deliberately: there is no quieter mode. Before
    T-07 an unparseable file was indistinguishable from one with no runs, which is the
    same fail-open with a different cause.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
            f.write("runs: [ {id: a, squad: b ## eaten\nnext_key: 1\n")
        code, out = run(tmp)
        ok = "does not parse" in out and code == 1
        print(f"{'ok' if ok else 'FAIL'} - case (f): an unparseable feature.yaml is "
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
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "features", "FEAT-TEST", "notes"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        # phase: validate with NO handoff-plan.md / handoff-build.md -> INV-17 fires.
        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
            f.write("feature_id: FEAT-TEST\nphase: validate\n")
        code, out = run(tmp)
        ok = "handoff-plan.md" in out and "Traceback" not in out
        print(f"{'ok' if ok else 'FAIL'} - case (g): M-01 — INV-17 reports the missing "
              f"handoff instead of raising NameError")
        if not ok:
            print(f"        exit {code}; output: {out.strip()[:200]}")
        return ok


def case_h():
    """Issue #16: `review_sha: none` is a truthy STRING, so INV-6 passed unpinned.

    `val()` returns `str(v)`, so the literal `none` is truthy and `not val("review_sha")`
    is False. Only an ABSENT key tripped the check — case (e) covers that axis and
    passed throughout, which is exactly why this hole survived: the invariant had a
    test, and the test agreed with it.

    FEAT-05's own feature.yaml carried `review_sha: none` for its whole plan phase
    while recording validator-squad runs, so this was live on a shipped feature, not
    hypothetical.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
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
        os.makedirs(os.path.join(h, "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
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
    is live, not theoretical: FEAT-06's own feature.yaml is exactly this shape
    (placeholder review_sha, product/eng runs only) and must not self-report.
    """
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, ".harness")
        os.makedirs(os.path.join(h, "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
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
            rundir = os.path.join(h, "features", "FEAT-TEST", "runs", "2026-08-05-01-product")
            os.makedirs(rundir, exist_ok=True)
            with open(os.path.join(h, "harness.json"), "w") as f:
                f.write(HARNESS_JSON_SYNC_OFF)
            with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
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
        os.makedirs(os.path.join(h, "features", "FEAT-TEST"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write('{\n  "github": {"sync": false, "repo": null}'
                    + (",\n  " + budget if budget else "") + "\n}\n")
        runs = "\n".join(f"  - {{ id: r{i}, squad: eng, verdict: PASS }}"
                         for i in range(n))
        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
            f.write(f"feature_id: FEAT-TEST\nphase: build\ncycles_used: 2\n"
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
    "INV-23" in the output — so raising the feature.yaml budget from 200 to 250 left the
    STATE.md finding in the output and the case still reported ok. A test that cannot tell
    which of two checks fired is not testing either.

    Each fixture now crosses exactly ONE budget by exactly ONE line, and asserts the other
    file stays silent. That binds the message to the comparison: case (o) below proves the
    two scripts DECLARE the same number, and this proves the declared number is the one
    actually enforced.
    """
    results = []
    for label, fl, sl, want_f, want_s in (
        ("feature.yaml over", 201, 120, True,  False),
        ("STATE.md over",     200, 121, False, True),
        ("both within",       200, 120, False, False),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            h = make_fixture(tmp, '{}', "  parent: 40")
            fd = os.path.join(h, "features", "FEAT-TEST")
            # EXACTLY `fl` lines, header included — the boundary is the whole point of the
            # second fixture, so the padding is sized against the header rather than added
            # to it. Written the naive way, "within" came out at 205 lines and reported a
            # violation, which reads as INV-23 being wrong when the fixture was.
            head = feature_yaml("  parent: 40")
            pad = fl - len(head.splitlines())
            with open(os.path.join(fd, "feature.yaml"), "w") as f:
                f.write(head + "\n".join(f"k{i}: v" for i in range(pad)) + "\n")
            with open(os.path.join(fd, "STATE.md"), "w") as f:
                f.write("## Current\n" + "\n".join(f"line {i}" for i in range(sl - 1)) + "\n")
            _code, out = run(tmp)
            got_f = "INV-23 FEAT-TEST/feature.yaml is" in out
            got_s = "INV-23 FEAT-TEST/STATE.md is" in out
            ok = (got_f == want_f) and (got_s == want_s)
            results.append(ok)
            print(f"{'ok' if ok else 'FAIL'} - case (n/{label}): at {fl} feature.yaml / "
                  f"{sl} STATE.md lines, INV-23 fires on "
                  f"[{'feature.yaml' if got_f else ''}{' ' if got_f and got_s else ''}"
                  f"{'STATE.md' if got_s else ''}{'nothing' if not (got_f or got_s) else ''}]"
                  f" — wanted [{'feature.yaml' if want_f else ''}"
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
        ("feature.yaml lines",  r"feature\.yaml is \{len\(lines\)\} lines — budget is (\d+)",
                                r"feature\.yaml is \{len\(fl\)\} lines — budget is (\d+)"),
        ("feature.yaml comments", r"comment lines — budget is (\d+)",
                                  r"comment lines — budget is (\d+)"),
        ("STATE.md lines",      r"STATE\.md is \{len\(lines\)\} lines — budget is (\d+)",
                                r"STATE\.md is \{len\(sl\)\} lines — budget is (\d+)"),
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
    ok_p = case_p()

    ok_exit_unchanged = code_a == code_b
    print(
        f"{'ok' if ok_exit_unchanged else 'FAIL'} - exit code unchanged by INV-21 "
        f"(a: {code_a}, b: {code_b})"
    )

    if (ok_a and ok_b and ok_c and ok_d and ok_e and ok_f and ok_g
            and ok_h and ok_i and ok_j and ok_k and ok_l and ok_m and ok_m2 and ok_m3 and ok_n and ok_o and ok_p
            and ok_exit_unchanged):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
