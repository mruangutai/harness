#!/usr/bin/env python3
"""check-state.sh at session entry: INV-9, INV-21, INV-24, INV-28, INV-30.

Sliced out of tests/integration/test-check-state.py (issue #1527). The hook registration
INV-9 requires, the mirrored feature with no recorded parent (INV-21), factory claims
against the fleet (INV-24), a Done feature with no recorded pull request (INV-28), an
open milestone behind a Done feature (INV-30), the cost-log silence, the two enforcement
scripts' agreement on every duplicated number, and the crash shapes a malformed tree must
report instead of dying on. No test invokes a real `gh` binary.
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
from check_state_support import (HARNESS_JSON_SYNC_OFF, HARNESS_JSON_SYNC_ON, SCRIPT,
    make_fixture, run, _run_with_gh, _run_with_gh_streams)


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
    here = _anchor_bin
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
        # The feature.json pair is GONE because the DUPLICATE is gone: FEAT-54's B-4 moved
        # the number and the counting rule into feature_schema.FEATURE_JSON_LINE_BUDGET, and
        # both gates now import it. That pair is policed by its own block below, which
        # asserts the single source AND that neither gate's fallback literal disagrees with
        # it — a fallback that drifts is the same defect this case exists to catch, just
        # hidden one branch deeper.
        #
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

    # THE feature.json BUDGET, NOW SINGLE-SOURCED (FEAT-54 B-4). Three things must hold or
    # the de-duplication is worse than the duplication it replaced: the constant exists, both
    # gates read it BY NAME, and every fallback literal they carry for an unimportable helper
    # equals it. The third is the one a reader would miss — a fallback saying 250 would
    # silently enforce a different budget on exactly the path nobody tests.
    schema_src = open(os.path.join(here, "feature_schema.py"), encoding="utf-8").read()
    declared = _re.search(r"^FEATURE_JSON_LINE_BUDGET = (\d+)$", schema_src, _re.M)
    fallbacks = sorted({int(x) for x in
                        _re.findall(r"_(?:inv23_)?budget = (\d+)", dom + sta)})
    reads_constant = ("FEATURE_JSON_LINE_BUDGET" in dom
                      and "FEATURE_JSON_LINE_BUDGET" in sta)
    fgood = (declared is not None and reads_constant
             and fallbacks in ([], [int(declared.group(1))]))
    ok_all &= fgood
    checks.append(
        f"feature.json budget: declared "
        f"{declared.group(1) if declared else 'NOT FOUND'}, both gates read the constant "
        f"{reads_constant}, fallback literals {fallbacks or 'none'}")

    # AND THE COUNTING RULE ITSELF IS SHARED, not merely the number. Either gate counting
    # whole-file lines while the other excludes the ledger would enforce two budgets under
    # one name, which is exactly the drift class above with the numbers still matching.
    counts_journal = ("journal_lines" in dom and "journal_lines" in sta
                      and "def journal_lines" in schema_src)
    ok_all &= counts_journal
    checks.append(f"feature.json counting rule shared: {counts_journal}")

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
    hb_ordered = [h.lower() for h in _re.findall(r'"(## [^"]+)"',
                  _re.search(r"HANDOFF_SECTIONS = \[(.*?)\]", sta, _re.S).group(1))]
    hb = set(hb_ordered)
    narrative_is_prefix = bool(_re.search(
        r"HANDOFF_NARRATIVE_HEADINGS\s*=\s*HANDOFF_SECTIONS\[:4\]", sta))
    hc = {h.strip().lower() for h in _re.findall(r"^(## .+)$", tpl, _re.M)}
    hgood = (bool(ha) and ha == hb and ha <= hc and narrative_is_prefix
             and hb_ordered[-1:] == ["## done when"])
    ok_all &= hgood
    checks.append(f"handoff headings: check-domain {sorted(ha)}, check-state {sorted(hb)}, "
                  f"narrative-prefix {narrative_is_prefix}, template {sorted(hc)}")

    print(f"{'ok' if ok_all else 'FAIL'} - case (o): check-domain.sh, check-state.sh and "
          f"HANDOFF.md agree on every duplicated budget, key and heading")
    if not ok_all:
        for c in checks:
            print(f"       | {c}")
    return ok_all


# --- T-05 (FEAT-26): INV-28 — a Done feature whose pull request number was never
# recorded. Warn level, gated on github.sync, one line per offending feature.
#
# WHY SIX CASES AND NOT ONE. The four silence cases are what stop an always-warn
# implementation passing the first: `pr` recorded, `Abandoned`, non-terminal, and sync off
# are each a separate reason to say nothing, and an implementation can get one right and
# the rest wrong. The per-feature naming case exists because a single aggregate count
# cannot tell the operator WHICH feature to run the remedy on.

def _inv28_fixture(tmp, sync_on, features):
    """features: list of (feat_id, status, pr_literal_or_None[, plan_station]).

    `pr` None omits the key. `status` None omits the status key entirely — the shape FEAT-41
    T-07's migration leaves on disk — and a fourth element writes a sibling plan.yaml carrying
    that lowercase top-level station, which is where the station is read from afterwards.
    """
    h = os.path.join(tmp, ".harness")
    os.makedirs(h, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(HARNESS_JSON_SYNC_ON if sync_on else HARNESS_JSON_SYNC_OFF)
    for entry in features:
        feat, status, pr = entry[:3]
        plan_station = entry[3] if len(entry) > 3 else None
        d = os.path.join(h, "harness", "features", feat)
        os.makedirs(d, exist_ok=True)
        body = '{\n  "feature_id": "%s"' % feat
        if status is not None:
            body += ',\n  "status": "%s"' % status
        if pr is not None:
            body += ',\n  "pr": %s' % pr
        body += "\n}\n"
        with open(os.path.join(d, "feature.json"), "w") as f:
            f.write(body)
        if plan_station is not None:
            with open(os.path.join(d, "plan.yaml"), "w") as f:
                f.write(f"schema: plan/1\nfeature: {feat}\nstatus: {plan_station}\ntasks: []\n")
    return h


def case_inv28_warns():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28", None, None, "done")])
        _code, out = run(tmp)
        ok = "INV-28" in out and "FEAT-T28" in out and "record-pr" in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 warns on a Done feature whose pr is null")
        return ok


def case_inv28_silent_on_integer():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28", None, "543", "done")])
        _code, out = run(tmp)
        ok = "INV-28" not in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 is silent on a Done feature whose pr is an integer")
        return ok


def case_inv28_silent_on_abandoned():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28", None, None, "abandoned")])
        _code, out = run(tmp)
        ok = "INV-28" not in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 is silent on an Abandoned feature whose pr is null")
        return ok


def case_inv28_silent_on_nonterminal():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28", None, None, "building")])
        _code, out = run(tmp)
        ok = "INV-28" not in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 is silent on a feature that is not terminal")
        return ok


def case_inv28_names_each():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T28A", None, None, "done"), ("FEAT-T28B", None, None, "done")])
        _code, out = run(tmp)
        lines = [l for l in out.splitlines() if "INV-28" in l]
        ok = (len(lines) == 2
              and any("FEAT-T28A" in l for l in lines)
              and any("FEAT-T28B" in l for l in lines))
        print(f"{'ok' if ok else 'FAIL'} - INV-28 names each offending feature on its own line")
        return ok


def case_41_t07_inv28_station_from_plan():
    """FEAT-41 T-07: INV-28's terminal gate reads the station from plan.yaml.

    THE POSITIVE SIDE OF THE MIGRATION, and INV-28 is the sharpest place to prove it because
    its half-applied direction is SILENT AND GREEN: with the status key gone and the gate
    un-repointed, `pdoc.get("status")` is empty, every feature fails the `!= ["Done"]` test,
    the loop `continue`s, and the invariant warns about nothing at all. The gate keeps exiting
    0 while checking zero features — the same vacuous-pass shape as board_lifecycle's STATUS
    class, in the project's own state gate.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T07", None, None, "done")])
        _code, out = run(tmp)
        ok = "INV-28" in out and "FEAT-T07" in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 warns from plan.yaml's `done` station with "
              f"NO feature.json status present")
        return ok


def case_41_t07_inv28_negative_control_live_station():
    """NEGATIVE CONTROL for the case above, and it is load-bearing: without it an always-warn
    repointing passes, and INV-28 would name every feature in the tree."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, True, [("FEAT-T07", None, None, "building")])
        _code, out = run(tmp)
        ok = "INV-28" not in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 is silent on a plan.yaml station of "
              f"`building` — the terminal gate still discriminates")
        return ok


def case_inv28_silent_sync_off():
    with tempfile.TemporaryDirectory() as tmp:
        _inv28_fixture(tmp, False, [("FEAT-T28", None, None, "done")])
        _code, out = run(tmp)
        ok = "INV-28" not in out
        print(f"{'ok' if ok else 'FAIL'} - INV-28 is silent when github.sync is off")
        return ok


def _inv30_fixture(tmp, features):
    """features: list of (feat_id, status, milestone_or_None). milestone None writes
    `"milestone": null`, which is the shape eight real features carry at 9165162."""
    h = os.path.join(tmp, ".harness")
    os.makedirs(h, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(HARNESS_JSON_SYNC_ON)
    for feat, station, ms in features:
        d = os.path.join(h, "harness", "features", feat)
        os.makedirs(d, exist_ok=True)
        body = ('{\n  "feature_id": "%s",\n'
                '  "github": {"milestone": %s}\n}\n'
                % (feat, "null" if ms is None else int(ms)))
        with open(os.path.join(d, "feature.json"), "w") as f:
            f.write(body)
        # The station lands in plan.yaml, lowercase (FEAT-41 T-07). feature.json keeps the
        # milestone, which is what this invariant is actually about.
        with open(os.path.join(d, "plan.yaml"), "w") as f:
            f.write(f"feature: {feat}\nstatus: {str(station).lower()}\ntasks: []\n")
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
        _inv30_fixture(tmp, [("FEAT-T30", "done", 77)])
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
        _inv30_fixture(tmp, [("FEAT-T30", "done", 77)])
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
        _inv30_fixture(tmp, [("FEAT-T30", "done", 77)])
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
        _inv30_fixture(tmp, [("FEAT-T30", "done", None)])
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
        _inv30_fixture(tmp, [("FEAT-T30", "review", 77)])
        gh = _inv30_gh_stub(tmp, [77])
        _code, out = _run_with_gh(tmp, gh)
        ok = not _inv30_lines(out)
        print(f"{'ok' if ok else 'FAIL'} - INV-30 is silent on a non-terminal feature whose "
              f"milestone is open")
        return ok


def main():
    results = []
    ok, code_a = case_a()
    results.append(ok)
    ok, code_b = case_b()
    results.append(ok)
    ok, _code_c = case_c()
    results.append(ok)
    results.append(case_d())
    results.append(case_e())
    results.append(case_f())
    results.append(case_k())
    results.append(case_m())
    results.append(case_m2())
    results.append(case_m3())
    results.append(case_o())
    results.append(case_inv28_warns())
    results.append(case_inv28_silent_on_integer())
    results.append(case_inv28_silent_on_abandoned())
    results.append(case_inv28_silent_on_nonterminal())
    results.append(case_inv28_names_each())
    results.append(case_inv28_silent_sync_off())
    results.append(case_41_t07_inv28_station_from_plan())
    results.append(case_41_t07_inv28_negative_control_live_station())
    results.append(case_r())
    results.append(case_s())
    results.append(case_t())
    results.append(case_inv30_fires_on_open_milestone())
    results.append(case_inv30_silent_on_closed_milestone())
    results.append(case_inv30_silent_offline())
    results.append(case_inv30_silent_on_null_milestone())
    results.append(case_inv30_silent_on_nonterminal())
    ok_exit_unchanged = code_a == code_b
    print(
        f"{'ok' if ok_exit_unchanged else 'FAIL'} - exit code unchanged by INV-21 "
        f"(a: {code_a}, b: {code_b})"
    )
    results.append(ok_exit_unchanged)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
