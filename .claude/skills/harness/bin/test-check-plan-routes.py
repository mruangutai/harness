#!/usr/bin/env python3
"""Tests for check-plan-routes.py (D-01, D-02, D-04, D-07, D-08).

Fixtures are written under tempfile.mkdtemp() so no repo state is touched.
Each case invokes the real script as a subprocess against a fixture PLAN.md,
and against the repo's own templates/PLAN.md, run-unit-tests.sh and source
for the static/textual checks (cases 8-13, 16).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("CHECK_PLAN_ROUTES_BIN") or os.path.join(
    BIN_DIR, "check-plan-routes.py")
REPO_ROOT = os.path.abspath(os.path.join(BIN_DIR, "..", "..", "..", ".."))

GRANTED_PATH = ".claude/skills/harness/bin/check-domain.sh"  # granted to two agents


def cpr():
    """The module UNDER TEST, loaded from SCRIPT — never from the repo copy.

    SCRIPT honours CHECK_PLAN_ROUTES_BIN, so during mutation testing the two are
    DIFFERENT FILES. An earlier case in this suite read the repo copy while the override
    pointed at a mutant and therefore reported ok against the broken build; anything here
    that needs a production constant must come through this function.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("_cpr_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
UNGRANTED_PATH = "some/totally/nonexistent/zzz-surface.md"  # granted to nobody
CASE17_PATH = ".harness/harness/features/FEAT-09-plan-time-route-check/runs/1-eng/notes.md"

failures = []


def run(*args, cwd=None, project_dir=None, script=None):
    """Invoke the checker. `project_dir` sets the root override; None UNSETS it.

    Unsetting is not cosmetic (case 19). Under a hook-invoked suite run the variable
    IS set to the repo, at which point a wrong-directory test would pass through the
    env var and prove nothing about the from-__file__ derivation it exists to check.

    BOTH NAMES, SET AND UNSET TOGETHER (FEAT-42 T-13). The checker now resolves through
    harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR and no other name, while
    the reverted sha-3952814 copy read HARNESS first and the host-owned name second. Clearing
    only one leaves the other set by whatever invoked this suite, and case 19's whole point is
    that NOTHING is set.
    """
    _OVERRIDES = ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR")
    env = {k: v for k, v in os.environ.items() if k not in _OVERRIDES}
    if project_dir is not None:
        for _k in _OVERRIDES:
            env[_k] = project_dir
    return subprocess.run(
        [sys.executable, script or SCRIPT, *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def write_plan(tmpdir, body, name="PLAN.md"):
    path = os.path.join(tmpdir, name)
    with open(path, "w") as f:
        f.write(body)
    return path


def task_block(tid, files, execution_mode):
    return (
        f"- {tid}: fixture task\n"
        f"  files: {files}\n"
        f"  change_type: logic\n"
        f"  execution_mode: {execution_mode}\n\n"
    )


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def case_01_02_03():
    """(1)(2)(3): ungranted-and-undeclared task exits non-zero, output has task id + path."""
    with tempfile.TemporaryDirectory() as td:
        plan = write_plan(td, "# PLAN\n\n" + task_block("T-01", UNGRANTED_PATH, "team"))
        r = run(plan)
        check("case_01_ungranted_undeclared_exits_nonzero", r.returncode != 0, r.stdout + r.stderr)
        check("case_02_output_has_task_id", "T-01" in r.stdout, r.stdout)
        check("case_03_output_has_offending_path", UNGRANTED_PATH in r.stdout, r.stdout)


def case_04():
    """(4): a plan whose every task resolves to a granting agent exits 0."""
    with tempfile.TemporaryDirectory() as td:
        plan = write_plan(td, "# PLAN\n\n" + task_block("T-01", GRANTED_PATH, "team"))
        r = run(plan)
        check("case_04_all_granted_exits_0", r.returncode == 0, r.stdout + r.stderr)


def case_05():
    """(5): a plan whose every ungranted task declares main-session-direct exits 0."""
    with tempfile.TemporaryDirectory() as td:
        plan = write_plan(td, "# PLAN\n\n" + task_block("T-01", UNGRANTED_PATH, "main-session-direct"))
        r = run(plan)
        check("case_05_ungranted_declared_main_session_exits_0", r.returncode == 0, r.stdout + r.stderr)


def case_06_07():
    """(6): a wildcard entry produces UNRESOLVED-GLOB. (7): exit status matches the wildcard task removed."""
    with tempfile.TemporaryDirectory() as td:
        wildcard_body = "# PLAN\n\n" + task_block("T-01", ".harness/harness/docs/*.md", "team")
        plan_wild = write_plan(td, wildcard_body, name="WILD.md")
        r_wild = run(plan_wild)
        check("case_06_wildcard_produces_unresolved_glob", "UNRESOLVED-GLOB" in r_wild.stdout, r_wild.stdout)

        plan_removed = write_plan(td, "# PLAN\n\n", name="REMOVED.md")
        r_removed = run(plan_removed)
        check(
            "case_07_wildcard_exit_status_matches_task_removed",
            r_wild.returncode == r_removed.returncode,
            f"wild={r_wild.returncode} removed={r_removed.returncode}",
        )


def case_08_09_16():
    """(8) source mentions check-domain.sh. (9) no fnmatch. (16) no glob_to_re — separate case from 9."""
    with open(SCRIPT) as f:
        src = f.read()
    check("case_08_source_mentions_check_domain_sh", "check-domain.sh" in src)
    check("case_09_source_has_no_fnmatch", "fnmatch" not in src)
    check("case_16_source_has_no_glob_to_re", "glob_to_re" not in src)


def case_10_11_12():
    """(10)(11)(12): templates/PLAN.md carries the ## Lanes section and both execution_mode tokens."""
    tpl = os.path.join(REPO_ROOT, ".claude", "skills", "harness", "templates", "PLAN.md")
    with open(tpl) as f:
        src = f.read()
    check("case_10_template_has_lanes_section", "## Lanes" in src)
    check("case_11_template_has_team_token", "execution_mode: team" in src)
    check("case_12_template_has_main_session_direct_token", "execution_mode: main-session-direct" in src)


def case_13():
    """(13): run-unit-tests.sh's SCRIPTS array lists test-check-plan-routes.py."""
    runner = os.path.join(BIN_DIR, "run-unit-tests.sh")
    with open(runner) as f:
        src = f.read()
    check("case_13_runner_lists_this_test", '"test-check-plan-routes.py"' in src)


def case_14_15():
    """(14): a task with granted paths declaring main-session-direct produces DEVIATION.
    (15): that same plan still exits 0."""
    with tempfile.TemporaryDirectory() as td:
        plan = write_plan(td, "# PLAN\n\n" + task_block("T-01", GRANTED_PATH, "main-session-direct"))
        r = run(plan)
        check("case_14_granted_but_main_session_produces_deviation", "DEVIATION" in r.stdout, r.stdout)
        check("case_15_deviation_plan_still_exits_0", r.returncode == 0, r.stdout + r.stderr)


def case_17():
    """(17): the mid-pattern-wildcard grant path must resolve OK, no VIOLATION naming its task.

    This is the exact bug check-domain.sh:190-197 records: a hand-rolled prefix
    comparison on the text before `/**` answers False for a pattern with an earlier
    wildcard segment. The path string below is granted ONLY through
    `.harness/*/features/*/runs/*-eng/**` (team-config.yaml) and must stay verbatim.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = write_plan(td, "# PLAN\n\n" + task_block("T-01", CASE17_PATH, "team"))
        r = run(plan)
        lines = r.stdout.splitlines()
        has_violation_for_t01 = any(
            line.startswith("VIOLATION") and "T-01" in line for line in lines
        )
        has_ok_for_t01 = any(
            line.startswith("OK") and "T-01" in line for line in lines
        )
        check("case_17_midpattern_wildcard_grant_no_violation", not has_violation_for_t01, r.stdout)
        check("case_17_midpattern_wildcard_grant_reports_ok", has_ok_for_t01, r.stdout)
        check("case_17_midpattern_wildcard_grant_exits_0", r.returncode == 0, r.stdout + r.stderr)

        # (17b) THE CLAUSE THAT CAN ACTUALLY FAIL. The three assertions above pass under a
        # hand-rolled prefix comparison too, because that comparison OVER-grants rather than
        # under-granting: `.harness/harness/features/` is a prefix of every feature file, so the path
        # still resolves to somebody, still reports OK and still exits 0. Measured, this path
        # resolves to exactly {harness-eng-lead, harness-orchestrator} through the mid-pattern
        # grant `.harness/*/features/*/runs/*-eng/**`, while a prefix implementation grants it to
        # most of the org. Asserting the EXACT set is what discriminates, and it fails on any
        # reimplementation regardless of how its variables are spelled.
        ok_line = next((l for l in lines if l.startswith("OK") and "T-01" in l), "")
        granted = ok_line.split("granted to", 1)[-1].strip() if "granted to" in ok_line else ""
        check("case_17b_ok_line_names_the_exact_granting_set",
              granted == "harness-eng-lead, harness-orchestrator",
              f"expected 'harness-eng-lead, harness-orchestrator', got {granted!r} "
              f"from line {ok_line!r}")


def case_18():
    """(18) issue #134: a BLOCK-FORM `files:` is parsed in full, dash stripped.

    The bug was `files:\\s*(.*)$` — `\\s` matches NEWLINES, so on a block-form list the
    regex swallowed the line break and captured the FIRST ITEM ONLY, dash included.
    That is a false positive AND a fail-open in one: the dash made a granted path look
    ungranted, while every LATER entry went unchecked.

    Three assertions, because a returncode-only test passes on either half alone:
      (a) the granted first entry is NOT reported ungranted (the dash is stripped),
      (b) a genuinely ungranted LATER entry IS reported (the fail-open half),
      (c) the same-line form still works, so the fix did not trade one shape for another.
    """
    results = []
    with tempfile.TemporaryDirectory() as td:
        block = write_plan(td, "# PLAN\n\n" + (
            "- T-01: block form\n"
            "  files:\n"
            "    - .harness/harness/docs/SPEC.md\n"
            "    - .gitignore\n"
            "  execution_mode: team\n"
            "  status: pending\n"))
        r = run(block)
        out = r.stdout
        results.append(("case_18a_block_form_first_entry_not_falsely_rejected",
                        "- .harness/harness/docs/SPEC.md ungranted" not in out, out))
        results.append(("case_18b_block_form_LATER_entry_is_checked_the_fail_open",
                        ".gitignore ungranted" in out, out))
    # (18d) THE POSITIVE ASSERTION. 18a is NEGATIVE — "SPEC.md is not reported
    # ungranted" is satisfied by never resolving SPEC.md at all, and a mutant returning
    # entries[-1:] passed 18a/18b/18c together. Two paths with DIFFERENT granted sets,
    # all granted, so the OK line must name the UNION; dropping either changes it.
    with tempfile.TemporaryDirectory() as td:
        allg = write_plan(td, "# PLAN\n\n" + (
            "- T-01: block form, every path granted\n"
            "  files:\n"
            "    - .harness/harness/docs/SPEC.md\n"
            "    - .claude/skills/harness/bin/check-domain.sh\n"
            "  execution_mode: team\n"
            "  status: pending\n"))
        r4 = run(allg)
        ok_line = next((l for l in r4.stdout.splitlines() if l.startswith("OK T-01")), "")
        results.append(("case_18d_block_form_OK_line_names_the_UNION_of_granted_sets",
                        "harness-documentor" in ok_line
                        and "harness-backend-dev" in ok_line
                        and "harness-dev-ops" in ok_line,
                        f"OK line was {ok_line!r}"))

    # (18e) The WRAPPED same-line shape — trailing comma, value continues on the next
    # line. Live in FEAT-08 (3 tasks), where T-01 declared two paths and the checker
    # resolved one: the continuation was dropped in silence. Same fail-open class.
    with tempfile.TemporaryDirectory() as td:
        wrapped = write_plan(td, "# PLAN\n\n" + (
            "- T-01: wrapped same-line\n"
            "  files: `.harness/harness/docs/SPEC.md`,\n"
            "    `.gitignore`\n"
            "  execution_mode: team\n"
            "  status: pending\n"))
        r5 = run(wrapped)
        results.append(("case_18e_wrapped_same_line_continuation_is_read",
                        ".gitignore ungranted" in r5.stdout, r5.stdout))

    # (18f) A files: value this parser cannot read must SAY SO, never return silently —
    # an empty entry list used to be indistinguishable from "every path granted".
    with tempfile.TemporaryDirectory() as td:
        empty = write_plan(td, "# PLAN\n\n" + (
            "- T-01: files: present but unreadable\n"
            "  files:\n"
            "  execution_mode: team\n"
            "  status: pending\n"))
        r6 = run(empty)
        results.append(("case_18f_unparseable_files_value_is_reported_not_silent",
                        "UNPARSED T-01" in r6.stdout, r6.stdout))

    with tempfile.TemporaryDirectory() as td:
        same = write_plan(td, "# PLAN\n\n" + (
            "- T-01: same-line form\n"
            "  files: `.harness/harness/docs/SPEC.md`, `.gitignore`\n"
            "  execution_mode: team\n"
            "  status: pending\n"))
        r2 = run(same)
        results.append(("case_18c_same_line_form_still_parsed",
                        ".gitignore ungranted" in r2.stdout, r2.stdout))
    ok = True
    for name, passed, detail in results:
        print(f"{'ok' if passed else 'FAIL'} {name}")
        if not passed:
            print(f"        {detail.strip()[:220]}")
            ok = False
    return ok


def case_19():
    """(19) issue #133 B-7: an ARGV-LESS run must never mistake 'wrong directory' for 'clean'.

    Measured on main at a5edb13, with CLAUDE_PROJECT_DIR unset:
      cd /tmp && python3 <repo>/.agents/skills/harness/bin/check-plan-routes.py
      -> `0 violation(s) across 0 plan(s)`, EXIT 0
    The glob was cwd-relative, so a checker that found nothing because it was looking
    in the wrong place was byte-identical to a clean tree — the VF-1/VF-2 failure class.

    Four assertions, because no one of them alone pins the behaviour:
      (a) cwd PARITY — argv-less from /tmp and from the repo root give identical output.
          Deliberately not a plan count: counts drift as features land, and
          `returncode != 0` cannot tell exit 1 (violations) from exit 2 (could not run).
      (b) an unresolvable root is LOUD (exit 2), not an empty scan.
      (c) a freshly-onboarded project with a manifest and ZERO features still exits 0 —
          zero plans is not itself an error, and turning it into one is a false alarm.
      (d) the explicit-path form is untouched by the root guard, even when
          CLAUDE_PROJECT_DIR points somewhere with no manifest at all.
    """
    r_root = run(cwd=REPO_ROOT)
    r_tmp = run(cwd="/tmp")
    check("case_19a_argvless_output_is_independent_of_cwd",
          r_tmp.stdout == r_root.stdout and r_tmp.returncode == r_root.returncode,
          f"root(exit {r_root.returncode}) last={r_root.stdout.strip().splitlines()[-1:]!r} "
          f"tmp(exit {r_tmp.returncode}) last={r_tmp.stdout.strip().splitlines()[-1:]!r}")
    # (a3) THE ASSERTION THE OTHER SIX DO NOT MAKE: discovery must actually FIND the
    # plans. Every case here was satisfiable by a discover_plans() that resolves the
    # right root and returns an EMPTY list — measured, `return root, []` printed
    # `scanning <correct root>` then `0 violation(s) across 0 plan(s)`, exited 0 on a
    # tree holding 8 plans and 36 violations, and the whole suite stayed green. That is
    # B-7 itself, moved from the glob's BASE to the glob's RESULT.
    #
    # THE LIVE-REPO NON-ZERO ASSERTION WAS REMOVED ON 2026-08-13 BECAUSE IT LOST ALL
    # POWER, and this comment is the record so nobody restores it. It read
    # `int(...) > 0` against the real tree on the stated grounds that "at least one does
    # not drift while this repo has any feature at all". That premise stopped being true
    # when `_is_shipped` began skipping delivered features: the moment FEAT-18 went
    # `status: Done`, EVERY feature on disk was shipped, discovery correctly reported
    # `0 plan(s)`, and the assertion failed on a healthy tree. Worse than the false
    # failure is what a green would have meant — with the true count at zero, the
    # `return root, []` mutant this case exists to catch reports zero too. The
    # assertion could not distinguish the defect from the truth in either direction.
    #
    # Its job moves to a3b below, which carries the same anti-fail-open power against a
    # FIXTURE and therefore does not depend on how many features this repo has shipped.
    _m = re.search(r"across (\d+) plan\(s\)", r_root.stdout)
    check("case_19a3_argvless_reports_a_count_at_all",
          bool(_m),
          f"argv-less from the repo root printed no `across N plan(s)` summary at all — "
          f"a checker that reports nothing cannot be read as clean. "
          f"stdout tail={r_root.stdout.strip().splitlines()[-1:]!r}")

    # (a3b) DISCOVERY MUST ACTUALLY FIND PLANS, AND MUST SKIP SHIPPED ONES — one fixture,
    # both halves, because either alone is satisfiable by a broken discoverer. A
    # `return root, []` reports 0 where 1 is expected; a discoverer that ignored
    # `_is_shipped` reports 2. The count is exact for that reason, never `> 0`.
    with tempfile.TemporaryDirectory() as _td3:
        _f3 = os.path.join(_td3, ".harness", "harness", "features")
        os.makedirs(_f3)
        with open(os.path.join(_td3, ".harness", "team-config.yaml"), "w") as f:
            f.write("agents: {}\n")
        for _n, _status in (("FEAT-LIVE", "Building"), ("FEAT-SHIPPED", "Done")):
            os.makedirs(os.path.join(_f3, _n))
            with open(os.path.join(_f3, _n, "PLAN.md"), "w") as f:
                f.write("# PLAN\n\n" + task_block("T-01", GRANTED_PATH, "team"))
            with open(os.path.join(_f3, _n, "feature.json"), "w") as f:
                json.dump({"feature_id": _n, "status": _status}, f)
        _r3 = run(project_dir=_td3)
        check("case_19a3b_discovery_finds_the_live_plan_and_skips_the_shipped_one",
              "across 1 plan(s)" in _r3.stdout,
              f"expected exactly 1 plan — FEAT-LIVE checked, FEAT-SHIPPED skipped. "
              f"0 means discovery found nothing (the fail-open this case exists to "
              f"catch); 2 means _is_shipped was not consulted. "
              f"stdout={_r3.stdout[:300]!r}")
        # (a3c) THE SECOND COUNT IS WHAT LETS CI TELL THE TWO ZEROES APART, so it is
        # asserted rather than left as unchecked output. The same fixture: 2 dirs entered,
        # 1 checked, 1 skipped as shipped. The CI step greps this exact wording.
        check("case_19a3c_the_examined_line_reports_dirs_entered_and_shipped_skipped",
              "examined 2 feature dir(s); 1 skipped as shipped" in _r3.stdout,
              f"the argv-less run must report how many feature directories it ENTERED, "
              f"which is the number that proves discovery ran — `0 plan(s)` alone cannot "
              f"separate broken discovery from an all-shipped tree. "
              f"stdout={_r3.stdout[:300]!r}")
        # (a3d) EXPLICIT PATHS DISCOVER NOTHING, so they must vouch for nothing. A count
        # printed here would be a claim about a walk that never happened.
        _r3e = run(os.path.join(_f3, "FEAT-LIVE", "PLAN.md"), project_dir=_td3)
        check("case_19a3d_explicit_paths_print_no_examined_line",
              "examined " not in _r3e.stdout,
              f"with paths named on argv there is no discovery to vouch for. "
              f"stdout={_r3e.stdout[:300]!r}")

    check("case_19a2_argvless_names_the_root_it_scanned",
          r_tmp.stdout.startswith("scanning ") and REPO_ROOT in r_tmp.stdout.splitlines()[0],
          r_tmp.stdout[:200])

    # (b) Neutralise BOTH root sources: a copy of the script four levels under a bare
    # tmpdir makes the from-__file__ derivation land on a directory with no manifest,
    # and CLAUDE_PROJECT_DIR points at another one. Copying honours
    # CHECK_PLAN_ROUTES_BIN, so a mutated implementation is what gets tested here too.
    with tempfile.TemporaryDirectory() as td:
        fake_bin = os.path.join(td, "root", "a", "b", "bin")
        os.makedirs(fake_bin)
        copy = os.path.join(fake_bin, "check-plan-routes.py")
        with open(SCRIPT) as src, open(copy, "w") as dst:
            dst.write(src.read())
        # THE RESOLVER GOES WITH IT (FEAT-42 T-13). This case neutralises both ROOT sources;
        # it is not about a missing module. Without harness_boundary.py beside the copy the
        # script dies on ImportError at exit 1 before it can refuse, and both assertions go
        # red for a reason that has nothing to do with an unresolvable root.
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "harness_boundary.py"),
                    os.path.join(fake_bin, "harness_boundary.py"))
        r = run(cwd=td, project_dir=td, script=copy)
        check("case_19b_unresolvable_root_exits_2_not_0", r.returncode == 2,
              f"exit {r.returncode} stdout={r.stdout[:200]!r} stderr={r.stderr[:200]!r}")
        check("case_19b2_unresolvable_root_says_why_on_stderr",
              "check-plan-routes:" in r.stderr and "0 violation(s)" not in r.stdout,
              f"stderr={r.stderr[:300]!r} stdout={r.stdout[:200]!r}")

    # (b3) A CLAUDE_PROJECT_DIR THAT CANNOT BE USED MUST SAY SO. The fallback to the
    # derived root is correct, but in silence it is the same family as B-7: the caller asks
    # about tree A and gets an answer about tree B, with real-looking violations and exit 1.
    # Measured before the warning: a nonexistent CLAUDE_PROJECT_DIR produced 36 violations
    # from a different checkout, and the only clue was a `scanning` line that reads as
    # confirmation rather than as a correction.
    with tempfile.TemporaryDirectory() as td:
        r = run(project_dir=os.path.join(td, "does-not-exist"))
        # THE WORDING IS harness_boundary's NOW, not this script's (FEAT-42 T-13). The
        # assertion still grades the same property — an override that cannot be used is
        # ANNOUNCED, never swapped in silence — and still names the discarded path, so a
        # message that stopped saying which root it dropped still fails here.
        check("case_19b3_unusable_project_dir_is_reported_not_silently_replaced",
              "discarding" in r.stderr and "does-not-exist" in r.stderr,
              f"stderr={r.stderr[:300]!r}")
        # ...and a VALID one is not warned about, or the message becomes noise on every run.
        os.makedirs(os.path.join(td, ".harness", "harness", "features"))
        with open(os.path.join(td, ".harness", "team-config.yaml"), "w") as f:
            f.write("agents: {}\n")
        r2 = run(project_dir=td)
        check("case_19b4_a_valid_project_dir_is_not_warned_about",
              "discarding" not in r2.stderr, f"stderr={r2.stderr[:300]!r}")
    # ...and neither is an UNSET one, which is the common case and the one a valid-dir
    # fixture cannot reach: with the env var unset the discard branch IS entered (there is
    # nothing to discard), so a warning keyed on entering the branch rather than on the
    # caller having asked for something fires on every ordinary run. A first draft of
    # 19b4 used only the valid-dir fixture and a `if asked:` -> `if True:` mutant walked
    # straight past it.
    # B-2 (FEAT-42 review panel). This asserted "IGNORING it", a string that occurs exactly
    # once in the whole .claude/skills tree — in this assertion. Nothing could produce it, so
    # the case was green and could not fail, while being counted in every zero-failure claim
    # on this feature. Its siblings 19b3/19b4 moved to the resolver's own wording when T-13
    # landed and this one was left behind. Now on "discarding", which harness_boundary
    # actually prints (harness_boundary.py:70), so the mutant named above is killed.
    check("case_19b5_an_unset_project_dir_is_not_warned_about",
          "discarding" not in r_root.stderr, f"stderr={r_root.stderr[:300]!r}")

    # (a4) THE PLAN SET, PINNED — "found the right things", not merely "found something".
    #
    # This is case_19a3's gap, and case_19a3 is itself the fix for an earlier gap. That one
    # asserted only NON-ZERO, so three mutants walked past it against the real repo, which
    # holds 8 plans and 36 violations:
    #     glob only `FEAT-02/PLAN.md`  -> `0 violation(s) across 1 plan(s)`, exit 0
    #     truncate the result `[:1]`   -> same
    #     glob `*/*.md`                -> `across 24 plan(s)`
    # 1 > 0, so the assertion was satisfied while discovery found an eighth of the tree.
    # The PR's own title, one layer inward.
    #
    # A COUNT AGAINST THE REAL REPO CANNOT FIX THIS — it drifts as features land, which is
    # why the earlier cases avoided one. A CONTROLLED FIXTURE can: two plans, and two
    # decoys that a sloppier glob would swallow — a sibling BRIEF.md, and a PLAN.md nested
    # under runs/ where `**` or `*/*.md` would reach it.
    with tempfile.TemporaryDirectory() as td:
        feats = os.path.join(td, ".harness", "harness", "features")
        os.makedirs(feats)
        with open(os.path.join(td, ".harness", "team-config.yaml"), "w") as f:
            f.write("agents: {}\n")
        for name in ("FEAT-A", "FEAT-B"):
            os.makedirs(os.path.join(feats, name))
            with open(os.path.join(feats, name, "PLAN.md"), "w") as f:
                f.write("# PLAN\n\n" + task_block("T-01", GRANTED_PATH, "team"))
            # decoy 1: a sibling markdown file that is not a plan
            with open(os.path.join(feats, name, "BRIEF.md"), "w") as f:
                f.write("# BRIEF\n\n" + task_block("T-99", GRANTED_PATH, "team"))
        # decoy 2: a PLAN.md one level deeper, which `**` or `*/*.md` would swallow
        os.makedirs(os.path.join(feats, "FEAT-A", "runs", "r1"))
        with open(os.path.join(feats, "FEAT-A", "runs", "r1", "PLAN.md"), "w") as f:
            f.write("# PLAN\n\n" + task_block("T-98", GRANTED_PATH, "team"))

        r = run(project_dir=td)
        check("case_19a4_discovery_finds_exactly_the_feature_plans",
              "across 2 plan(s)" in r.stdout,
              f"expected exactly 2 plans (2 features, 1 sibling BRIEF.md each, 1 nested "
              f"decoy). stdout={r.stdout[:300]!r}")
        # (a5) The scan line must describe the search that actually ran. DEC-182 widened it to
    # both filenames and this assertion caught the change on the first run — which is the
    # case working, not breaking: the line is the only way a reader tells "nothing here"
    # from "wrong place", so it must never describe a search that did not happen. Changing ONLY the
        # print to `.harness/plans/**/ANY.md` survived every other assertion: 19a2 checks
        # `startswith("scanning ")` and that the root appears, 19c2 only that the root
        # appears. The line is the entire mechanism for telling "nothing here" from "wrong
        # place", so a line that describes a different search is worse than none.
        check("case_19a5_the_scan_line_matches_the_glob_that_ran",
              r.stdout.splitlines()[0]
              == f"scanning {td}/.harness/*/features/*/{{plan.yaml,PLAN.md}}",
              f"first line={r.stdout.splitlines()[:1]!r}")

    # (c) The other direction. A manifest is present, so the root IS known; there simply
    # are no features yet. Must be exit 0 and must scan the FIXTURE, not the real repo —
    # which is also what fails if the env-var/derived precedence is ever flipped.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, ".harness", "harness", "features"))
        with open(os.path.join(td, ".harness", "team-config.yaml"), "w") as f:
            f.write("agents: {}\n")
        r = run(project_dir=td)
        check("case_19c_zero_feature_project_is_not_an_error", r.returncode == 0,
              f"exit {r.returncode} stdout={r.stdout[:300]!r} stderr={r.stderr[:200]!r}")
        check("case_19c2_zero_feature_project_scans_the_declared_root",
              td in r.stdout and "0 violation(s) across 0 plan(s)" in r.stdout,
              r.stdout[:300])

    # (d) The explicit-path form, from a cwd with no .harness and an env root with no
    # manifest. A guard applied outside the argv-less branch turns this into exit 2.
    with tempfile.TemporaryDirectory() as td:
        plan = write_plan(td, "# PLAN\n\n" + task_block("T-01", GRANTED_PATH, "team"))
        r = run(plan, cwd=td, project_dir=td)
        check("case_19d_explicit_path_unaffected_by_the_root_guard",
              r.returncode == 0 and "OK T-01 granted to" in r.stdout,
              f"exit {r.returncode} stdout={r.stdout[:300]!r} stderr={r.stderr[:200]!r}")
        empty = write_plan(td, "# PLAN\n\nno tasks here\n", name="EMPTY.md")
        r2 = run(empty, cwd=td, project_dir=td)
        check("case_19d2_explicit_path_with_no_tasks_still_exits_0",
              r2.returncode == 0 and "scanning " not in r2.stdout,
              f"exit {r2.returncode} stdout={r2.stdout[:300]!r}")


def case_22():
    """(22) THE READABILITY GUARD, which had zero assertions across two designs.

    Round 3 reported "the entire round-2 guard could be deleted with both suites green". I
    responded by REWRITING the guard — better code, and it closed three other findings —
    and added 124 test lines, NONE of them touching permissions. Round 4 ran the identical
    mutation and got the identical result, because a finding about COVERAGE is closed only
    by an assertion that fails when the code is removed. The guard's assertion count went
    from zero to zero.

    What made it feel done: I verified the new guard BY HAND in a shell — chmod 000, exit 2,
    right message — and never asked whether anything here would notice if it vanished.

    Four fixtures, one per branch of the guard, because a single one leaves the others as
    unbound as they were. Modes are restored in a `finally`: `git status` does not show
    directory modes, so a leaked chmod silently poisons every later run in the worktree.
    """
    def build(td):
        feats = os.path.join(td, ".harness", "harness", "features", "FEAT-A")
        os.makedirs(feats)
        with open(os.path.join(td, ".harness", "team-config.yaml"), "w") as f:
            f.write("agents: {}\n")
        plan = os.path.join(feats, "PLAN.md")
        with open(plan, "w") as f:
            f.write("# PLAN\n\n" + task_block("T-01", GRANTED_PATH, "team"))
        return feats, plan

    # (a) a feature directory that cannot be entered
    with tempfile.TemporaryDirectory() as td:
        feats, _ = build(td)
        try:
            os.chmod(feats, 0o000)
            r = run(project_dir=td)
            check("case_22a_unreadable_feature_dir_exits_2",
                  r.returncode == 2 and "FEAT-A" in r.stderr
                  and ".harness/*/features/" in r.stderr
                  and "0 violation(s)" not in r.stdout,
                  f"exit {r.returncode} stdout={r.stdout[:150]!r} stderr={r.stderr[:200]!r}")
        finally:
            os.chmod(feats, 0o755)

    # (b) a PLAN.md that exists and cannot be read
    with tempfile.TemporaryDirectory() as td:
        _, plan = build(td)
        try:
            os.chmod(plan, 0o000)
            r = run(project_dir=td)
            check("case_22b_unreadable_plan_file_exits_2",
                  r.returncode == 2 and "PLAN.md" in r.stderr,
                  f"exit {r.returncode} stderr={r.stderr[:200]!r}")
        finally:
            os.chmod(plan, 0o644)

    # (c) a PLAN.md that is present but will not resolve. `glob` used lexists; the
    # single-walk rewrite used os.path.isfile, which SWALLOWS OSError — measured as a
    # regression against the previous commit, exit 2 became exit 0 and silent.
    with tempfile.TemporaryDirectory() as td:
        feats, plan = build(td)
        os.remove(plan)
        os.symlink(os.path.join(td, "nowhere-at-all"), plan)
        r = run(project_dir=td)
        check("case_22c_broken_symlink_plan_is_reported_not_skipped",
              r.returncode == 2 and "PLAN.md" in r.stderr,
              f"exit {r.returncode} stdout={r.stdout[:150]!r} stderr={r.stderr[:200]!r}")

    # (d) THE DISCRIMINATOR. Every case above passes against a guard that exits 2 always.
    with tempfile.TemporaryDirectory() as td:
        build(td)
        r = run(project_dir=td)
        # NOT `returncode == 0`: the fixture manifest is a stub, so GRANTED_PATH resolves
        # to NOBODY and the run legitimately exits 1 with a routing VIOLATION. This case is
        # about the READABILITY guard staying silent, so assert exactly that — the plan was
        # processed and nothing was called unreadable. Asserting 0 failed on correct code.
        check("case_22d_a_readable_tree_is_not_flagged",
              r.returncode != 2 and "across 1 plan(s)" in r.stdout
              and "cannot be read" not in r.stderr,
              f"exit {r.returncode} stdout={r.stdout[:200]!r} stderr={r.stderr[:150]!r}")


def case_21():
    """(21) THE BEHAVIOURAL TEST, which is what case_20 kept failing to be.

    case_20 scans SOURCE TEXT and is now on its fourth draft; the first three were each
    defeated, and review defeated the fourth twice more — a probe assembled into a variable
    (`_marker = os.path.join(derived, ".harness")` then `os.path.isdir(_marker)`) matches no
    predicate, and a file whose probes all vanish emits no assertion at all, because the
    per-file check lives inside the loop. A source-text detector can always be walked around
    by writing the same thing differently. That is not a bug in the fourth draft; it is the
    ceiling of the technique.

    So test the PROPERTY instead: a directory holding `.harness/` but NO `team-config.yaml`
    must NOT be accepted as a project root. That is the whole reason the probe names the
    manifest file — a `.harness/` directory can exist under `$HOME` for reasons that have
    nothing to do with any project: `$HOME/.harness/` exists on this machine because it
    holds the 2026-08-10 backup archives, so `$HOME` has a `.harness/` on any machine with
    that kind of unrelated content sitting under it. Any implementation that probes the
    directory fails this, however it is spelled.
    """
    with tempfile.TemporaryDirectory() as td:
        # bin/ four levels down, so the from-__file__ derivation lands on `fake_root`.
        fake_bin = os.path.join(td, "fake_root", ".claude", "skills", "harness", "bin")
        os.makedirs(fake_bin)
        for name in os.listdir(os.path.dirname(SCRIPT)):
            src = os.path.join(os.path.dirname(SCRIPT), name)
            if os.path.isfile(src) and (name.endswith(".py") or name.endswith(".sh")):
                shutil.copy2(src, os.path.join(fake_bin, name))
        # The trap: a .harness/ DIRECTORY with no manifest in it — exactly $HOME's shape.
        os.makedirs(os.path.join(td, "fake_root", ".harness"))
        with open(os.path.join(td, "fake_root", ".harness", "registry.json"), "w") as f:
            f.write("{}\n")
        # THE OVERRIDE MUST WIN. The loop above copies every bin/ file BY NAME from the
        # real directory, so `check-plan-routes.py` in the fake tree was the real
        # implementation and this case reported ok about a file the mutant never touched —
        # the identical defect case_20's second draft had, reproduced here within minutes
        # of writing a case whose whole purpose was to be harder to fool. Copy SCRIPT last,
        # over the top, so CHECK_PLAN_ROUTES_BIN is what actually runs.
        copy = os.path.join(fake_bin, "check-plan-routes.py")
        shutil.copy2(SCRIPT, copy)
        r = run(cwd=td, script=copy)
        check("case_21_a_bare_harness_dir_is_not_a_project_root",
              r.returncode == 2 and "0 violation(s)" not in r.stdout,
              f"exit {r.returncode} (want 2) stdout={r.stdout[:200]!r} "
              f"stderr={r.stderr[:200]!r} — a .harness/ directory with no manifest was "
              f"accepted as a root, which is B-7 in the global install")


PLAN_YAML = """schema: plan/1
feature: FEAT-A
approval: {status: approved}
tasks:
  - id: T-01
    title: granted path
    traces: [REQ-01]
    change_type: logic
    execution_mode: team
    execution_agent: harness-dev-ops
    depends_on: []
    status: pending
    files: [%s]
    verify: |
      true
    intent: |
      do it
"""


def _yaml_project(td, files=".harness/harness.json", extra="", status="pending"):
    """A fixture project whose feature carries a plan.yaml, with the REAL manifest so
    resolution is against the same globs production uses.

    `status` overrides the template's fixed `status: pending`; `status=None` omits the
    field entirely (the absent-status shape). Default is the original template value, so
    every existing caller is unaffected.
    """
    fd = os.path.join(td, ".harness", "harness", "features", "FEAT-A")
    os.makedirs(fd, exist_ok=True)
    import shutil as _sh
    _sh.copy2(os.path.join(REPO_ROOT, ".harness", "team-config.yaml"),
              os.path.join(td, ".harness", "team-config.yaml"))
    text = PLAN_YAML % files
    if status is None:
        text = text.replace("    status: pending\n", "", 1)
    elif status != "pending":
        text = text.replace("status: pending", f"status: {status}", 1)
    with open(os.path.join(fd, "plan.yaml"), "w") as f:
        f.write(text + extra)
    return fd


def case_23():
    """(23) DEC-182: the plan.yaml path resolves routes through the loader, not regexes.

    The whole point of #147 is that PLAN.md's fields were read by hand-rolled regexes that
    each invented their own rule for what a value may contain. These cases assert the new
    path does the routing job at least as well, and that the three shapes #147 asked about
    are now decided by the type rather than by a cleanup heuristic.
    """
    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td)
        r = run(project_dir=td)
        check("case_23a_plan_yaml_granted_path_is_OK",
              r.returncode == 0 and "OK T-01 granted to harness-dev-ops" in r.stdout,
              f"exit {r.returncode}: {r.stdout[:200]!r}")

    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, files=".agents/skills/harness-spec-driven/SKILL.md")
        r = run(project_dir=td)
        check("case_23b_plan_yaml_ungranted_path_is_a_VIOLATION",
              r.returncode == 1 and "ungranted (NOBODY)" in r.stdout,
              f"exit {r.returncode}: {r.stdout[:200]!r}")

    # #147 Q2 — an annotation is NOT silently cleaned. The old _clean() stripped backticks
    # and a trailing comma but not a parenthetical, so `bin/x.py (delete)` resolved only
    # because a /** grant swallowed the suffix. Here the resolver gets what was written.
    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, files='".harness/harness.json (delete)"')
        r = run(project_dir=td)
        check("case_23c_an_annotated_path_resolves_to_NOBODY_not_silently_cleaned",
              r.returncode == 1 and "ungranted (NOBODY)" in r.stdout,
              f"exit {r.returncode}: {r.stdout[:200]!r}")

    # A malformed plan is exit 2 — the checker could not run — never a routing violation.
    with tempfile.TemporaryDirectory() as td:
        fd = _yaml_project(td)
        with open(os.path.join(fd, "plan.yaml"), "w") as f:
            f.write("tasks:\n  - id: T-01\n   bad: indent\n")
        r = run(project_dir=td)
        check("case_23d_a_malformed_plan_yaml_exits_2_not_1",
              r.returncode == 2 and "does not load" in r.stderr,
              f"exit {r.returncode}: {r.stderr[:200]!r}")

    # The per-task machine-field budget (DEC-182). READ THE CONSTANT rather than writing
    # 30 or 50 into three assertions: review caught the first number being wrong, and a
    # test that hard-codes it fails for the right reason and the wrong cause the next time
    # it moves. `cap` here is production's own value.
    cap = cpr().MACHINE_LINES_PER_TASK

    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, files=", ".join(f'"src/f{i}.py"' for i in range(cap + 40)))
        r = run(project_dir=td)
        check("case_23e_the_per_task_machine_budget_fires",
              f"machine-field lines — budget is {cap}" in r.stdout,
              f"exit {r.returncode}: {r.stdout[:240]!r}")

    # ...and does NOT fire on a normal task, or it is a cap on having tasks at all.
    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td)
        r = run(project_dir=td)
        check("case_23f_the_budget_stays_silent_on_a_normal_task",
              f"budget is {cap}" not in r.stdout, r.stdout[:200])

    # THE BUDGET MUST GATE, NOT MERELY PRINT. `violations += 1` could be deleted with the
    # suite green, because case_23e asserts on stdout alone and every sibling in this file
    # asserts on the exit code. A finding that does not change the exit status is a
    # comment: check-plan-routes.py's whole contract is that CI reads its exit code.
    #
    # The fixture's files are GRANTED, so a non-zero exit can only come from the budget.
    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, files=", ".join(f'"{GRANTED_PATH}"' for _ in range(cap + 40)))
        r = run(project_dir=td)
        check("case_23h_an_over_budget_task_sets_the_EXIT_CODE_not_just_stdout",
              r.returncode == 1 and "ungranted" not in r.stdout,
              f"exit {r.returncode}: {r.stdout[:240]!r}")

    # THE BOUNDARY, both sides, ONE LINE APART. `>` -> `>=` survived every earlier
    # assertion because they all crossed the cap by 40, and in the real corpus FEAT-06
    # T-01 measures exactly AT the cap — the one value where the two operators disagree.
    #
    # Tuned with `traces:`, not `files:`. Both count identically against the budget, but
    # every files entry costs a check-domain.sh subprocess: a search over `files:` ran 110
    # of them and this case timed out at two minutes. `traces:` is never resolved.
    #
    # THREE RUNS, NO SEARCH. Run 1 goes far over and REPORTS its own total, which gives
    # the fixture's fixed overhead exactly. Runs 2 and 3 then sit on the boundary. Reading
    # the overhead beats assuming it: the fixture gains a field and an assumed constant
    # silently stops testing the boundary while still passing.
    def _traces(n):
        with tempfile.TemporaryDirectory() as td:
            fd = _yaml_project(td)
            p = os.path.join(fd, "plan.yaml")
            src = re.sub(r"^    traces:.*$", "", open(p).read(), flags=re.M)
            with open(p, "w") as f:
                f.write(src.rstrip("\n") +
                        "\n    traces: [" + ", ".join(f"REQ-{i:02d}"
                                                      for i in range(n)) + "]\n")
            return run(project_dir=td).stdout

    probe = cap + 40
    m = re.search(r"(\d+) machine-field lines", _traces(probe))
    if not m:
        check("case_23i_the_budget_boundary_is_exact", False,
              "probe run did not report a total; boundary untested")
    else:
        overhead = int(m.group(1)) - probe          # everything that is not `traces:`
        at, over = cap - overhead, cap - overhead + 1
        silent, fires = _traces(at), _traces(over)
        check("case_23i_the_budget_boundary_is_exact",
              f"budget is {cap}" not in silent and f"budget is {cap}" in fires,
              f"overhead={overhead}; {at} traces (=={cap}) must be silent, "
              f"{over} (=={cap + 1}) must fire")

    # EVERY BUDGETED FIELD COUNTS -- and the first draft of this comment said that while
    # covering 3 of the 11. Review dropped `title`, `id`, `status`, `change_type`,
    # `execution_mode`, `execution_agent` and `execution_reason` from BUDGETED_FIELDS one
    # at a time and the suite stayed ALL PASS on every one. A comment claiming coverage it
    # does not have is worse than no comment: it tells the next reader not to look.
    #
    # So the loop is generated FROM BUDGETED_FIELDS itself. A field added to production and
    # not to this list can no longer go unexercised, because there is no list to forget.
    # THE EXACT TOTAL, so every budgeted field is pinned by one assertion.
    #
    # Present-vs-absent was the first design and it cannot work: six of the eleven fields
    # are REQUIRED, so removing one makes load_plan reject the plan and no total is printed
    # at all. Measured -- files, verify, change_type, execution_mode, title and id all came
    # back `without=None`. A per-field drop test can only ever reach the five optional ones.
    #
    # So the fixture carries a KNOWN size for every field and the reported total is asserted
    # exactly. Drop any field from BUDGETED_FIELDS, or break any arm of the accumulator, and
    # the number moves. `status: true` is a BOOL and `execution_reason: ""` is EMPTY on
    # purpose -- those are the `elif v is not None` and `or 1` arms, both of which survived
    # as mutants until this case existed.
    N_TRACES, N_FILES, N_DEPS, N_VERIFY = cap + 20, 3, 2, 4
    EXPECTED = (N_FILES + N_VERIFY + N_TRACES + N_DEPS   # the four sized fields
                + 7)                                     # id title change_type
    #                                                      execution_mode execution_agent
    #                                                      execution_reason status
    plan = (
        "schema: plan/1\nfeature: FEAT-A\ntasks:\n"
        "  - id: T-01\n"
        "    title: a title\n"
        "    change_type: logic\n"
        "    execution_mode: team\n"
        "    execution_agent: harness-backend-dev\n"
        '    execution_reason: ""\n'
        "    status: true\n"
        "    traces: [" + ", ".join(f"REQ-{i:03d}" for i in range(N_TRACES)) + "]\n"
        "    depends_on: [" + ", ".join(f"T-{i:02d}" for i in range(N_DEPS)) + "]\n"
        "    files:\n" + "".join(f'      - "{GRANTED_PATH}"\n' for _ in range(N_FILES)) +
        "    verify: |\n" + "".join(f"      echo {i}\n" for i in range(N_VERIFY)) +
        # REQUIRED by load_plan, and deliberately NOT in BUDGETED_FIELDS — it is the
        # dispatch prompt, which is READ. Its length must not move EXPECTED, so a long
        # one here doubles as the assertion that it stays excluded from the count.
        "    intent: |\n" + "".join(f"      line {i}\n" for i in range(12))
    )
    with tempfile.TemporaryDirectory() as td:
        fd = os.path.join(td, ".harness", "harness", "features", "FEAT-A")
        os.makedirs(fd)
        shutil.copy2(os.path.join(REPO_ROOT, ".harness", "team-config.yaml"),
                     os.path.join(td, ".harness", "team-config.yaml"))
        with open(os.path.join(fd, "plan.yaml"), "w") as f:
            f.write(plan)
        r = run(project_dir=td)
        m = re.search(r"(\d+) machine-field lines", r.stdout)
        got = int(m.group(1)) if m else None
        check("case_23j_every_budgeted_field_counts_exactly_once", got == EXPECTED,
              f"reported {got}, expected {EXPECTED} "
              f"({N_FILES} files + {N_VERIFY} verify + {N_TRACES} traces + {N_DEPS} "
              f"depends_on + 7 scalars): {r.stdout[:160]!r}")

    # ...and the field list the case is written against has not drifted from production.
    check("case_23j2_BUDGETED_FIELDS_is_still_the_eleven_this_case_pins",
          set(cpr().BUDGETED_FIELDS) == {"files", "verify", "traces", "depends_on",
                                         "change_type", "execution_mode", "execution_agent",
                                         "execution_reason", "status", "id", "title"},
          f"BUDGETED_FIELDS = {cpr().BUDGETED_FIELDS}")

    # A feature carrying BOTH files is a half-finished migration, refused rather than
    # silently preferred — "which is authoritative" is the ambiguity #147 is about.
    with tempfile.TemporaryDirectory() as td:
        fd = _yaml_project(td)
        with open(os.path.join(fd, "PLAN.md"), "w") as f:
            f.write("# PLAN\n\n" + task_block("T-09", GRANTED_PATH, "team"))
        r = run(project_dir=td)
        check("case_23g_both_plan_yaml_and_PLAN_md_is_refused",
              r.returncode == 2 and "BOTH" in r.stderr,
              f"exit {r.returncode}: {r.stderr[:200]!r}")


def case_24():
    """(24) A DONE feature is not route-checked. Its plan is a record, not a contract.

    This is a removal, not a trade-off. Checking shipped plans was the default behaviour of
    a glob and never a decision: the work shipped, the routes were taken, the plan will not
    be re-executed, so a finding on it is actionable by nobody. Measured on the real tree
    before this landed: 36 violations across 8 plans — 27 `no files: line`, 8 the
    pre-FEAT-06 prose shape, and 1 real routing defect. 35 of the 36 were format noise in
    SHIPPED plans; the one real finding is FEAT-08 T-04's `**SPLIT`, which was `awaiting_user`
    and therefore still checked. That noise is why issue #133's gate could never be
    switched on.

    FINISHED_STATUSES is now ("Done",) — every prior board column (D-09/D-10 collapsed
    "shipped" and "abandoned" into Done) is checked, and only Done skips. All six board
    columns are asserted by name below, so a value drops out only if this loop is edited to
    drop it, never silently by a count changing. The lowercase "done" case is the one that
    proves D-11's case sensitivity is actually load-bearing here, not just documented.

    Both directions, because a skip that skips everything would pass the first case alone.
    """
    results = []
    for status, want_checked in (("Backlog", True), ("Plan", True), ("Ready", True),
                                 ("Building", True), ("Review", True), ("Done", False),
                                 ("done", True)):
        with tempfile.TemporaryDirectory() as td:
            fd = _yaml_project(td, files=".agents/skills/harness-spec-driven/SKILL.md")
            with open(os.path.join(fd, "feature.json"), "w") as f:
                f.write(f"feature_id: FEAT-A\nstatus: {status}\n")
            r = run(project_dir=td)
            checked = "ungranted (NOBODY)" in r.stdout
            ok = checked == want_checked
            results.append(ok)
            check(f"case_24_{status}_is_{'checked' if want_checked else 'skipped'}",
                  ok, f"exit {r.returncode}, checked={checked}: {r.stdout[:160]!r}")

    # FINISHED_STATUSES is a SUBSET of the schema's status enum, never equality — a status
    # can legitimately be in the enum without being finished. Without this, the constant and
    # feature-schema.json are two copies of the same vocabulary with nothing tying them
    # together (D-04).
    import json
    schema_path = os.path.join(REPO_ROOT, ".claude", "skills", "harness", "bin",
                                "feature-schema.json")
    with open(schema_path) as f:
        schema_enum = set(json.load(f)["properties"]["status"]["enum"])
    finished = set(cpr().FINISHED_STATUSES)
    ok = finished.issubset(schema_enum)
    results.append(ok)
    check("case_24_FINISHED_STATUSES_is_a_subset_of_the_schema_status_enum",
          ok, f"FINISHED_STATUSES={finished}, schema enum={schema_enum}")

    # A feature we CANNOT classify is checked, never skipped. The failure that matters is a
    # live plan going unexamined; an old one examined twice costs nothing.
    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, files=".agents/skills/harness-spec-driven/SKILL.md")
        r = run(project_dir=td)              # no feature.json at all
        check("case_24_no_feature_yaml_is_checked_not_skipped",
              "ungranted (NOBODY)" in r.stdout, r.stdout[:200])

    # A feature.json THAT PARSES BUT IS NOT A MAPPING. This is the case the four statuses
    # above cannot reach, and it was a live crash: the first draft put `_is_shipped`'s
    # `return` outside its own `try:`, so `doc.get` ran on a list and raised
    # AttributeError out of discover_plans(). The process died with EXIT 1 — the code that
    # means "violations found" — having examined nothing and printed no summary.
    #
    # ASSERT ON ALL THREE, because each alone is satisfied by the bug:
    #   exit != 1 ......... no. The crash exits 1, and so does a real violation.
    #   stderr is clean ... no on its own. It only says "did not crash", not "did the work".
    #   the summary line ... this is the one that says the checker REACHED the feature.
    # A `try:` wrapped around the whole body would silence the traceback and still skip
    # the feature, so the summary line is the assertion that closes the fail-open half.
    for label, body in (("a_sequence", '["a", "b"]\n'),
                        ("a_bare_scalar", '"Done"\n'),
                        ("status_is_a_list", '{"status": ["Done"]}\n'),
                        # A MAPPING WITH NO `status:` KEY AT ALL. Two shapes REACH
                        # `bool(token)`; this is the only one for which the guard is
                        # LOAD-BEARING -- the distinction the whole case exists to draw.
                        # Here `"".split()` is `[]` -- `"".split()` is `[]`, so without the guard
                        # `token[0]` raises IndexError and the run dies with empty stdout
                        # and exit 1, the code a real violation uses.
                        #
                        # ONLY TWO of the shapes above stop at the isinstance check --
                        # `a_sequence` and `a_bare_scalar`. An earlier version of this
                        # comment said four, which libelled the one case that carries its
                        # own weight: `status_is_a_list` IS a dict, reaches `bool(token)`
                        # with a truthy `["['Done']"]`, and is the SOLE case that
                        # catches removal of the `str()` at check-plan-routes.py:433.
                        # A comment telling the next reader a live case is a duplicate is
                        # how a load-bearing assertion gets deleted as redundant.
                        ("a_mapping_with_no_status", '{"feature_id": "FEAT-A"}\n')):
        with tempfile.TemporaryDirectory() as td:
            fd = _yaml_project(td, files=".agents/skills/harness-spec-driven/SKILL.md")
            with open(os.path.join(fd, "feature.json"), "w") as f:
                f.write(body)
            r = run(project_dir=td)
            ok = ("Traceback" not in r.stderr
                  and "ungranted (NOBODY)" in r.stdout
                  and "1 violation(s) across 1 plan(s)" in r.stdout)
            results.append(ok)
            check(f"case_24_feature_yaml_{label}_is_checked_not_crashed",
                  ok, f"exit {r.returncode}, stderr={r.stderr[:120]!r}, "
                      f"stdout={r.stdout[-120:]!r}")

    # (T-05 item 5) THE ELEVEN-KEY END-TO-END CASE. Based on
    # templates/feature.json's eight required keys, plus the three optional
    # keys (max_total_runs, github, factory) so all eleven are present. status
    # is Done, so the feature must be SKIPPED — proving the real reader path
    # (harness_yaml.load_file -> json.dumps'd feature.json -> _is_shipped)
    # end to end, not just the four malformed-document guards above.
    #
    # A shipped feature is excluded from discover_plans()'s own count, not
    # merely from its violations (check-plan-routes.py:568-569, `continue`
    # before `processed` is incremented) — so "across 1 plan(s)" is the WRONG
    # assertion for the skipped run on its own; it would be satisfied just as
    # well by a checker that never found the plan at all (case_19a3's
    # fail-open). PAIRED, on the SAME eleven-key document with only `status`
    # changed, is what discriminates: Done -> excluded entirely (0 plans, no
    # violation), Building -> reached and checked (1 plan, 1 violation on the
    # fixture's ungranted path). Only the status flips the outcome, proving
    # the document was actually parsed and _is_shipped actually consulted.
    def _eleven_key_doc(status):
        return {
            "feature_id": "FEAT-A",
            "branch": "none",
            "pr": None,
            "status": status,
            "review_sha": "none",
            "cycles_used": 0,
            "max_total_cycles": 10,
            "runs": [],
            "max_total_runs": 5,
            "github": {},
            "factory": {},
        }

    with tempfile.TemporaryDirectory() as td:
        fd = _yaml_project(td, files=".agents/skills/harness-spec-driven/SKILL.md")
        with open(os.path.join(fd, "feature.json"), "w") as f:
            f.write(json.dumps(_eleven_key_doc("Done")))
        r_done = run(project_dir=td)
        with open(os.path.join(fd, "feature.json"), "w") as f:
            f.write(json.dumps(_eleven_key_doc("Building")))
        r_building = run(project_dir=td)

        ok_done = ("ungranted (NOBODY)" not in r_done.stdout
                   and "across 0 plan(s)" in r_done.stdout)
        ok_building = ("ungranted (NOBODY)" in r_building.stdout
                       and "across 1 plan(s)" in r_building.stdout)
        ok = ok_done and ok_building
        results.append(ok)
        check("case_24_eleven_key_feature_json_Done_is_skipped_end_to_end",
              ok,
              f"Done: exit {r_done.returncode}, stdout={r_done.stdout[:200]!r} | "
              f"Building: exit {r_building.returncode}, stdout={r_building.stdout[:200]!r}")
    return all(results)


def case_25():
    """(25) DEC-192 board truth: a task's status, when present, is one of exactly
    pending / building / done — case sensitive on purpose. "Building" (capital B) is the
    board's own spelling of the same idea and is the typo a person will actually make;
    today it would read as not-done forever and the card would silently never move. An
    absent status is legal (the live corpus predates the field).
    """
    # The CLEAN case the whole enum exists for — asserted first.
    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, status="building")
        r = run(project_dir=td)
        check("case_25a_status_building_is_CLEAN",
              r.returncode == 0 and "VIOLATION" not in r.stdout,
              f"exit {r.returncode}: {r.stdout[:200]!r}")

    # Capital B — the board's own spelling — is a VIOLATION naming the three legal values.
    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, status="Building")
        r = run(project_dir=td)
        legal = cpr().LEGAL_TASK_STATUSES
        ok = (r.returncode != 0
              and "VIOLATION T-01" in r.stdout
              and "Building" in r.stdout
              and all(v in r.stdout for v in legal))
        check("case_25b_status_Building_capital_B_is_a_VIOLATION_naming_the_three_legal_values",
              ok, f"exit {r.returncode}: {r.stdout[:300]!r}, legal={legal}")

    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, status="in-progress")
        r = run(project_dir=td)
        check("case_25c_status_in_progress_is_a_VIOLATION",
              r.returncode != 0 and "VIOLATION T-01" in r.stdout,
              f"exit {r.returncode}: {r.stdout[:200]!r}")

    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, status=None)
        r = run(project_dir=td)
        check("case_25d_no_status_at_all_is_CLEAN",
              r.returncode == 0 and "VIOLATION" not in r.stdout,
              f"exit {r.returncode}: {r.stdout[:200]!r}")

    # A second task carrying `status: done`, alongside T-01's default `status: pending`
    # (via _yaml_project's default), are both CLEAN in the same plan.
    with tempfile.TemporaryDirectory() as td:
        fd = _yaml_project(td)
        second_task = (
            "  - id: T-02\n"
            "    title: second task\n"
            "    traces: [REQ-01]\n"
            "    change_type: logic\n"
            "    execution_mode: team\n"
            "    execution_agent: harness-dev-ops\n"
            "    depends_on: []\n"
            "    status: done\n"
            f'    files: ["{GRANTED_PATH}"]\n'
            "    verify: |\n"
            "      true\n"
            "    intent: |\n"
            "      do it\n"
        )
        with open(os.path.join(fd, "plan.yaml"), "a") as f:
            f.write(second_task)
        r = run(project_dir=td)
        check("case_25e_status_done_and_status_pending_are_both_CLEAN",
              r.returncode == 0 and "VIOLATION" not in r.stdout,
              f"exit {r.returncode}: {r.stdout[:300]!r}")


def case_20():
    """(20) Root resolution is now the FOURTH copy in this tree. D-02 does not forbid
    duplication — it forbids SILENT DRIFT, and case (o) in test-check-state.py is this
    repo's pattern for catching it.

    Case (o)'s own comment, written about the fourth duplicated NUMBER, says the detector
    "joins the detector in the same commit that duplicates it — not in a later one nobody
    writes." This is that commit for root resolution.

    KEYED ON THE PROBE STRING, not on control flow. The two spellings inside
    check-domain.sh are already textually different (a ternary and an if/else) and both
    are correct, so asserting shared structure would fail on a difference nobody minds.
    What every copy MUST agree on is WHICH FILE proves a directory is a harness root: if
    one probes `.harness/team-config.yaml` and another probes something else, they resolve
    different roots on the same tree and no gate notices.

    check-state.sh is a NAMED EXCEPTION, not an oversight. Measured by review: it has no
    derived fallback at all — `cd "$root"` with an invalid CLAUDE_PROJECT_DIR fails and it
    silently reports on the cwd. That is a real defect, it is a DEC-174 carve-out file, and
    it is unrelated to #133, so it is filed separately rather than fixed here. Encoding it
    as an exception keeps this assertion honest instead of quietly passing.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    MANIFEST = "team-config.yaml"
    PREDICATES = ("os.access(", "os.path.isdir(", "os.path.isfile(", "os.path.exists(",
                  "os.stat(", "Path(")

    def logical_lines(text):
        """Physical lines joined until brackets balance.

        THE THIRD DRAFT OF THIS CASE WAS BLIND BECAUSE IT SKIPPED THIS. It filtered
        PHYSICAL lines containing both `os.access(` and `.harness`, and this PR's own
        derived-root probe is wrapped across two lines — so the detector saw one of the two
        probes, and the invisible one was the one it was written for. Measured: replacing
        that probe with `os.path.isdir(os.path.join(derived, ".harness"))` — the exact
        simplification the implementation comment forbids AND cites this case as
        preventing — passed the entire suite, and reproduced the global-install fail-open.
        A detector that cannot see its own target is worse than none, because the comment
        next to it tells the next reader they are covered.
        """
        out, buf, depth = [], "", 0
        for raw in text.splitlines():
            buf = (buf + " " + raw.strip()).strip() if buf else raw.strip()
            depth += raw.count("(") + raw.count("[") - raw.count(")") - raw.count("]")
            if depth <= 0:
                out.append(buf)
                buf, depth = "", 0
        if buf:
            out.append(buf)
        return out

    # EVERY bin/ SCRIPT THAT PROBES IN PYTHON, which is narrower than it sounds and is
    # stated rather than implied: a pure-shell probe (`[ -d "$root/.harness" ]`) matches
    # none of these predicates and is invisible here. THIS CASE IS A CHEAP SMOKE CHECK, NOT
    # THE GUARANTEE — case (21) is, because it tests the behaviour and cannot be walked
    # around by spelling the probe differently. Four drafts of this case were each defeated
    # by a rewrite; that is the ceiling of source-text scanning, not a bug in draft five. The previous draft listed two files, so a
    # fifth copy of root resolution was undetectable by construction. check-state.sh is a
    # CODED exception, not prose: it genuinely has no root probe (verified — 0 matches),
    # which is issue #156, and encoding it here keeps this assertion honest rather than
    # quietly passing on a file that has the very defect the case is about.
    # NO CODED EXCEPTIONS. There was one — wayfind.py, which probed the `.harness` DIRECTORY
    # while walking up from the cwd, so from anywhere under a $HOME holding its own `.harness`
    # it resolved $HOME as the project root. FEAT-42 T-02 moved wayfind onto the MARKER file,
    # which is what this case demands of every other reader, so the exemption became stale the
    # moment that landed. A stale allowlist is worse than no coverage: it reports green while
    # hiding exactly the regression it was written to tolerate.
    ok, seen_any = True, 0
    for fname in sorted(os.listdir(here)):
        if not (fname.endswith(".py") or fname.endswith(".sh")) or fname.startswith("test-"):
            continue
        path = SCRIPT if fname == "check-plan-routes.py" else os.path.join(here, fname)
        try:
            body = open(path, encoding="utf-8").read()
        except OSError:
            continue
        # A ROOT PROBE is a filesystem test naming `.harness` inline. The limit is stated
        # rather than hidden: a probe whose path was assembled into a variable on an
        # earlier line is invisible to any source-text check, this one included.
        probes = [l for l in logical_lines(body)
                  if ".harness" in l and any(pr in l for pr in PREDICATES)]
        if not probes:
            continue
        seen_any += 1
        disagree = [l.strip()[:90] for l in probes if MANIFEST not in l]
        good = not disagree
        ok &= good
        check(f"case_20_{fname.replace('.', '_').replace('-', '_')}_probes_the_manifest",
              good,
              f"{fname}: {len(disagree)} of {len(probes)} root probe(s) do not name "
              f"{MANIFEST} -> {disagree[:2]}. A copy probing the .harness DIRECTORY "
              f"resolves $HOME as a root in the global install, which is B-7 verbatim.")
    check("case_20_the_detector_is_not_blind",
          seen_any >= 2,
          f"only {seen_any} file(s) matched any root probe — the pattern went blind, which "
          f"is how the previous draft passed while missing its own target")
    ok &= seen_any >= 2
    return ok


def _inv_project(td, features):
    """A fixture project with N feature dirs and a stub check-state.sh.

    `features` is a list of (dir_name, status, brief_text, plan_text_or_None). A plan of
    None writes NO plan.yaml at all — that is the FEAT-34 shape, the one that actually got
    through: a signed BRIEF claiming an invariant number, with no plan yet in existence, so
    a plan-only scan never sees it.
    """
    import shutil as _sh
    os.makedirs(os.path.join(td, ".harness"), exist_ok=True)
    _sh.copy2(os.path.join(REPO_ROOT, ".harness", "team-config.yaml"),
              os.path.join(td, ".harness", "team-config.yaml"))
    binp = os.path.join(td, ".claude", "skills", "harness", "bin")
    os.makedirs(binp, exist_ok=True)
    # The LIVE set. Only these three exist in this fixture's gate script.
    with open(os.path.join(binp, "check-state.sh"), "w") as f:
        f.write("#!/bin/bash\n# INV-1 something\n# INV-2 another\n# INV-3 a third\n")
    for name, status, brief, plan in features:
        fd = os.path.join(td, ".harness", "harness", "features", name)
        os.makedirs(fd, exist_ok=True)
        with open(os.path.join(fd, "feature.json"), "w") as f:
            json.dump({"feature_id": name, "status": status}, f)
        with open(os.path.join(fd, "BRIEF.md"), "w") as f:
            f.write(brief)
        if plan is not None:
            with open(os.path.join(fd, "plan.yaml"), "w") as f:
                f.write(plan)
    return td


_INV_PLAN = ("approval:\n  status: approved\n\ntasks:\n"
             "  - id: T-01\n    title: t\n    traces: [REQ-01]\n"
             "    change_type: logic\n    execution_mode: main-session-direct\n"
             "    execution_reason: none\n    status: pending\n"
             "    files:\n      - .harness/harness.json\n"
             "    verify: |\n      true\n    intent: |\n      x\n")


def case_26():
    """(26) TWO UNBUILT FEATURES CANNOT CLAIM THE SAME INV NUMBER.

    MEASURED 2026-08-23, and this case exists because the main session shipped the gap it
    is closing. FEAT-26's plan.yaml used `INV-28` sixteen times and FEAT-34's BRIEF used it
    eight times. Both were unbuilt, both were signed or about to be, and NOTHING saw it —
    not check-state.sh, not this checker, not two review rounds. It was found by a human
    reading a task list.

    The instruction given to pm at the time was "do not infer the next free number from the
    highest in the file". Correct, and half a check: it names check-state.sh and says
    nothing about the signed-but-unbuilt plans of other in-flight features. A number is
    free only when BOTH halves agree, and only one half was mechanised.

    WHY THE FEATURE DIR AND NOT THE PLAN. FEAT-34 had no plan.yaml at all — a BRIEF and
    nothing else. A plan-only scan would have reproduced the exact miss, which is why
    case_26c writes a feature with no plan and expects it to still participate.
    """
    # (a) THE COLLISION. Two unshipped features, same unclaimed number, both named.
    with tempfile.TemporaryDirectory() as td:
        _inv_project(td, [
            ("FEAT-A", "Ready", "The new invariant is INV-9.\n", _INV_PLAN),
            ("FEAT-B", "Plan", "Add INV-9, which reports the thing.\n", _INV_PLAN),
        ])
        r = run(project_dir=td)
        out = r.stdout + r.stderr
        ok = (r.returncode != 0 and "INV-9" in out
              and "FEAT-A" in out and "FEAT-B" in out)
        check("case_26a_two_unbuilt_features_claiming_INV-9_is_a_VIOLATION_naming_both",
              ok, f"exit {r.returncode}: {out[:400]!r}")

    # (b) DIFFERENT numbers are clean — without this, "always violate" passes (a).
    with tempfile.TemporaryDirectory() as td:
        _inv_project(td, [
            ("FEAT-A", "Ready", "The new invariant is INV-9.\n", _INV_PLAN),
            ("FEAT-B", "Plan", "Add INV-10, which reports the thing.\n", _INV_PLAN),
        ])
        r = run(project_dir=td)
        out = r.stdout + r.stderr
        check("case_26b_distinct_INV_numbers_are_CLEAN",
              r.returncode == 0 and "INV-9" not in out and "INV-10" not in out,
              f"exit {r.returncode}: {out[:400]!r}")

    # (c) THE SHAPE THAT ACTUALLY GOT THROUGH: a feature with a BRIEF and NO plan.yaml.
    with tempfile.TemporaryDirectory() as td:
        _inv_project(td, [
            ("FEAT-A", "Ready", "Add INV-9 to the gate.\n", _INV_PLAN),
            ("FEAT-B", "Plan", "The new invariant is INV-9.\n", None),
        ])
        r = run(project_dir=td)
        out = r.stdout + r.stderr
        ok = (r.returncode != 0 and "INV-9" in out
              and "FEAT-A" in out and "FEAT-B" in out)
        check("case_26c_a_feature_with_a_BRIEF_and_NO_plan_still_collides",
              ok, f"exit {r.returncode}: {out[:400]!r}")

    # (d) A number ALREADY LIVE in check-state.sh is a REFERENCE, not a claim. Two features
    #     citing INV-2 are discussing an invariant that exists; that must stay clean or the
    #     check fires on every plan that mentions an existing rule.
    with tempfile.TemporaryDirectory() as td:
        _inv_project(td, [
            ("FEAT-A", "Ready", "This interacts with INV-2.\n", _INV_PLAN),
            ("FEAT-B", "Plan", "INV-2 already grades that card.\n", _INV_PLAN),
        ])
        r = run(project_dir=td)
        out = r.stdout + r.stderr
        check("case_26d_two_features_citing_a_LIVE_invariant_is_CLEAN",
              r.returncode == 0 and "VIOLATION" not in out,
              f"exit {r.returncode}: {out[:400]!r}")

    # (e) A SHIPPED feature's claim is a record, not a contract. Its number is spent, and a
    #     live feature reusing it is a different problem from two live features colliding.
    with tempfile.TemporaryDirectory() as td:
        _inv_project(td, [
            ("FEAT-A", "Done", "Added INV-9.\n", _INV_PLAN),
            ("FEAT-B", "Plan", "The new invariant is INV-9.\n", _INV_PLAN),
        ])
        r = run(project_dir=td)
        out = r.stdout + r.stderr
        check("case_26e_a_SHIPPED_feature_does_not_collide_with_a_live_one",
              r.returncode == 0 and "VIOLATION" not in out,
              f"exit {r.returncode}: {out[:400]!r}")

    # (f) A DECLARATION WINS OVER PROSE. FEAT-B declares 10 and merely CITES 9 while
    #     explaining why it moved. That is history, not a claim, and the check must not
    #     fire on a feature for documenting the collision it already resolved.
    with tempfile.TemporaryDirectory() as td:
        _inv_project(td, [
            ("FEAT-A", "Ready", "Add INV-9 to the gate.\n", _INV_PLAN),
            ("FEAT-B", "Plan",
             "<!-- invariants: 10 -->\nThe new invariant is INV-10, not INV-9, "
             "because FEAT-A holds INV-9 and builds first.\n", _INV_PLAN),
        ])
        r = run(project_dir=td)
        out = r.stdout + r.stderr
        check("case_26f_a_DECLARATION_beats_a_prose_citation",
              r.returncode == 0 and "VIOLATION INV-9" not in out,
              f"exit {r.returncode}: {out[:400]!r}")

    # (g) THE DECLARATION IS NOT AN ESCAPE HATCH. Two features DECLARING the same number
    #     still collide — without this, "declare anything and be excused" passes (f).
    with tempfile.TemporaryDirectory() as td:
        _inv_project(td, [
            # NEITHER BRIEF WRITES THE TOKEN `INV-9` IN PROSE. If it did, the prose scan
            # alone would catch the pair and this case would pass without the declaration
            # path existing at all — which is exactly how it passed before the feature
            # was implemented.
            ("FEAT-A", "Ready", "<!-- invariants: 9 -->\nAdds one invariant.\n", _INV_PLAN),
            ("FEAT-B", "Plan", "<!-- invariants: 9 -->\nAdds one invariant.\n", _INV_PLAN),
        ])
        r = run(project_dir=td)
        out = r.stdout + r.stderr
        ok = (r.returncode != 0 and "INV-9" in out
              and "FEAT-A" in out and "FEAT-B" in out)
        check("case_26g_two_features_DECLARING_the_same_number_still_collide",
              ok, f"exit {r.returncode}: {out[:400]!r}")


def case_27():
    """(27) Routes use the owner manifest that the write hook will consult."""
    with tempfile.TemporaryDirectory() as td:
        owner = os.path.join(td, "owner")
        branch = os.path.join(owner, ".claude", "worktrees", "feature")
        gitdir = os.path.join(owner, ".git", "worktrees", "feature")
        os.makedirs(gitdir, exist_ok=True)
        os.makedirs(branch, exist_ok=True)
        with open(os.path.join(branch, ".git"), "w") as f:
            f.write(f"gitdir: {gitdir}\n")
        _yaml_project(branch, files=GRANTED_PATH)
        os.makedirs(os.path.join(owner, ".harness"), exist_ok=True)
        owner_manifest = os.path.join(owner, ".harness", "team-config.yaml")
        with open(owner_manifest, "w") as f:
            f.write("agents: {}\n")
        owner_bin = os.path.join(owner, ".claude", "skills", "harness", "bin")
        os.makedirs(owner_bin)
        owner_resolver = os.path.join(owner_bin, "check-domain.sh")
        with open(owner_resolver, "w") as f:
            f.write("#!/bin/sh\nprintf '%s\\n' harness-frontend-dev\n")
        os.chmod(owner_resolver, 0o755)

        result = run(project_dir=branch)
        branch_manifest = os.path.join(branch, ".harness", "team-config.yaml")
        output = result.stdout + result.stderr
        check(
            "case_27a_owner_manifest_controls_routes",
            result.returncode != 0
            and f"MANIFEST {os.path.realpath(owner_manifest)}" in output
            and f"DEVIATION {branch_manifest}" in output
            and "OK T-01 granted to harness-frontend-dev" in output,
            f"exit {result.returncode}: {output[:500]!r}",
        )

        prior_bin = os.path.join(td, "prior-bin")
        os.makedirs(prior_bin)
        rel = ".claude/skills/harness/bin"
        for name in ("check-plan-routes.py", "harness_boundary.py", "harness_yaml.py"):
            source = subprocess.run(
                ["git", "-C", REPO_ROOT, "show", f"HEAD:{rel}/{name}"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            if name == "check-plan-routes.py":
                source = source.replace(
                    'CHECK_DOMAIN = os.path.join(BIN_DIR, "check-domain.sh")',
                    f"CHECK_DOMAIN = {os.path.join(BIN_DIR, 'check-domain.sh')!r}",
                )
            with open(os.path.join(prior_bin, name), "w") as f:
                f.write(source)
        prior = run(project_dir=branch,
                    script=os.path.join(prior_bin, "check-plan-routes.py"))
        check(
            "case_27b_prior_revision_false_ok",
            prior.returncode == 0 and "OK T-01" in prior.stdout,
            f"exit {prior.returncode}: {(prior.stdout + prior.stderr)[:500]!r}",
        )

    with tempfile.TemporaryDirectory() as td:
        owner = os.path.join(td, "owner")
        branch = os.path.join(owner, ".claude", "worktrees", "feature")
        gitdir = os.path.join(owner, ".git", "worktrees", "feature")
        os.makedirs(gitdir, exist_ok=True)
        os.makedirs(branch, exist_ok=True)
        with open(os.path.join(branch, ".git"), "w") as f:
            f.write(f"gitdir: {gitdir}\n")
        _yaml_project(branch, files=GRANTED_PATH)
        result = run(project_dir=branch)
        output = result.stdout + result.stderr
        check(
            "case_27c_unreadable_owner_manifest_refuses",
            result.returncode == 2 and "owner manifest" in output,
            f"exit {result.returncode}: {output[:500]!r}",
        )


def main():
    case_01_02_03()
    case_04()
    case_05()
    case_06_07()
    case_08_09_16()
    case_10_11_12()
    case_13()
    case_14_15()
    case_17()
    if not case_18():
        failures.append('case_18')
    case_19()
    case_20()
    case_21()
    case_22()
    case_23()
    case_24()
    case_25()
    case_26()
    case_27()

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print("\nALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
