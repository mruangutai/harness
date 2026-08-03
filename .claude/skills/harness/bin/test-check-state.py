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
  "github": {"sync": true, "repo": "org/repo"},
  "cost_model": {"rates": {"sonnet": 1}}
}
"""

HARNESS_JSON_SYNC_OFF = """{
  "github": {"sync": false, "repo": null},
  "cost_model": {"rates": {"sonnet": 1}}
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
        make_fixture(tmp, '{"cost_model": {"rates": {}}}', "  parent: 40")
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


def main():
    ok_a, code_a = case_a()
    ok_b, code_b = case_b()
    ok_c, _code_c = case_c()
    ok_d = case_d()
    ok_e = case_e()
    ok_f = case_f()

    ok_exit_unchanged = code_a == code_b
    print(
        f"{'ok' if ok_exit_unchanged else 'FAIL'} - exit code unchanged by INV-21 "
        f"(a: {code_a}, b: {code_b})"
    )

    if ok_a and ok_b and ok_c and ok_d and ok_e and ok_f and ok_exit_unchanged:
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
