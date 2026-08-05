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
    blocked /harness entry on a correctly configured project. Fixture: base has all
    five hook events registered; local adds ONE unrelated PreToolUse entry. INV-9
    must stay silent about the hooks it can still see.
    """
    with tempfile.TemporaryDirectory() as tmp:
        make_fixture(tmp, '{}', "  parent: 40")
        cl = os.path.join(tmp, ".claude")
        os.makedirs(cl, exist_ok=True)
        base = {"env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"},
                "hooks": {
                    "SubagentStart": [{"hooks": [{"command": "x/inject-expertise.sh"}]}],
                    "SubagentStop": [{"hooks": [{"command": "x/validate-digest.py --hook"}]}],
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

    ok_exit_unchanged = code_a == code_b
    print(
        f"{'ok' if ok_exit_unchanged else 'FAIL'} - exit code unchanged by INV-21 "
        f"(a: {code_a}, b: {code_b})"
    )

    if (ok_a and ok_b and ok_c and ok_d and ok_e and ok_f and ok_g
            and ok_h and ok_i and ok_j and ok_k and ok_exit_unchanged):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
