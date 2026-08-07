#!/usr/bin/env python3
"""Tests for check-plan-routes.py (D-01, D-02, D-04, D-07, D-08).

Fixtures are written under tempfile.mkdtemp() so no repo state is touched.
Each case invokes the real script as a subprocess against a fixture PLAN.md,
and against the repo's own templates/PLAN.md, run-unit-tests.sh and source
for the static/textual checks (cases 8-13, 16).
"""
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
CASE17_PATH = ".harness/features/FEAT-09-plan-time-route-check/runs/1-eng/notes.md"

failures = []


def run(*args, cwd=None, project_dir=None, script=None):
    """Invoke the checker. `project_dir` sets CLAUDE_PROJECT_DIR; None UNSETS it.

    Unsetting is not cosmetic (case 19). Under a hook-invoked suite run the variable
    IS set to the repo, at which point a wrong-directory test would pass through the
    env var and prove nothing about the from-__file__ derivation it exists to check.
    """
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    if project_dir is not None:
        env["CLAUDE_PROJECT_DIR"] = project_dir
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
        wildcard_body = "# PLAN\n\n" + task_block("T-01", "docs/harness/*.md", "team")
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
    `.harness/features/*/runs/*-eng/**` (team-config.yaml:278) and must stay verbatim.
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
        # under-granting: `.harness/features/` is a prefix of every feature file, so the path
        # still resolves to somebody, still reports OK and still exits 0. Measured, this path
        # resolves to exactly {harness-eng-lead, harness-orchestrator} through the mid-pattern
        # grant `.harness/features/*/runs/*-eng/**`, while a prefix implementation grants it to
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
            "    - docs/harness/SPEC.md\n"
            "    - .gitignore\n"
            "  execution_mode: team\n"
            "  status: pending\n"))
        r = run(block)
        out = r.stdout
        results.append(("case_18a_block_form_first_entry_not_falsely_rejected",
                        "- docs/harness/SPEC.md ungranted" not in out, out))
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
            "    - docs/harness/SPEC.md\n"
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
            "  files: `docs/harness/SPEC.md`,\n"
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
            "  files: `docs/harness/SPEC.md`, `.gitignore`\n"
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
      cd /tmp && python3 <repo>/.claude/skills/harness/bin/check-plan-routes.py
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
    # The other cases avoid a plan count on the stated grounds that counts drift. True,
    # and it is why this asserts NON-ZERO rather than a number: "at least one" does not
    # drift while this repo has any feature at all, and it is the whole difference
    # between looking and reporting.
    _m = re.search(r"across (\d+) plan\(s\)", r_root.stdout)
    check("case_19a3_argvless_actually_finds_the_plans",
          bool(_m) and int(_m.group(1)) > 0,
          f"argv-less from the repo root reported {_m.group(1) if _m else '??'} plans — "
          f"resolving the root and finding nothing is the same fail-open as scanning "
          f"the wrong directory. stdout tail={r_root.stdout.strip().splitlines()[-1:]!r}")

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
        check("case_19b3_unusable_project_dir_is_reported_not_silently_replaced",
              "IGNORING it" in r.stderr and "does-not-exist" in r.stderr,
              f"stderr={r.stderr[:300]!r}")
        # ...and a VALID one is not warned about, or the message becomes noise on every run.
        os.makedirs(os.path.join(td, ".harness", "features"))
        with open(os.path.join(td, ".harness", "team-config.yaml"), "w") as f:
            f.write("agents: {}\n")
        r2 = run(project_dir=td)
        check("case_19b4_a_valid_project_dir_is_not_warned_about",
              "IGNORING it" not in r2.stderr, f"stderr={r2.stderr[:300]!r}")
    # ...and neither is an UNSET one, which is the common case and the one a valid-dir
    # fixture cannot reach: with the env var unset the discard branch IS entered (there is
    # nothing to discard), so a warning keyed on entering the branch rather than on the
    # caller having asked for something fires on every ordinary run. A first draft of
    # 19b4 used only the valid-dir fixture and a `if asked:` -> `if True:` mutant walked
    # straight past it.
    check("case_19b5_an_unset_project_dir_is_not_warned_about",
          "IGNORING it" not in r_root.stderr, f"stderr={r_root.stderr[:300]!r}")

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
        feats = os.path.join(td, ".harness", "features")
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
              == f"scanning {td}/.harness/features/*/{{plan.yaml,PLAN.md}}",
              f"first line={r.stdout.splitlines()[:1]!r}")

    # (c) The other direction. A manifest is present, so the root IS known; there simply
    # are no features yet. Must be exit 0 and must scan the FIXTURE, not the real repo —
    # which is also what fails if the env-var/derived precedence is ever flipped.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, ".harness", "features"))
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
        feats = os.path.join(td, ".harness", "features", "FEAT-A")
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
                  r.returncode == 2 and "FEAT-A" in r.stderr and "0 violation(s)" not in r.stdout,
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
    manifest file, and it is the difference between working and B-7 in the real global
    install — `deploy.sh` writes `$HOME/.harness/registry.json`, so `$HOME` has a `.harness/`
    on every machine that has ever deployed. Any implementation that probes the directory
    fails this, however it is spelled.
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


def _yaml_project(td, files=".harness/harness.json", extra=""):
    """A fixture project whose feature carries a plan.yaml, with the REAL manifest so
    resolution is against the same globs production uses."""
    fd = os.path.join(td, ".harness", "features", "FEAT-A")
    os.makedirs(fd, exist_ok=True)
    import shutil as _sh
    _sh.copy2(os.path.join(REPO_ROOT, ".harness", "team-config.yaml"),
              os.path.join(td, ".harness", "team-config.yaml"))
    with open(os.path.join(fd, "plan.yaml"), "w") as f:
        f.write((PLAN_YAML % files) + extra)
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
        _yaml_project(td, files=".claude/skills/harness-spec-driven/SKILL.md")
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
        fd = os.path.join(td, ".harness", "features", "FEAT-A")
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
    """(24) A SHIPPED feature is not route-checked. Its plan is a record, not a contract.

    This is a removal, not a trade-off. Checking shipped plans was the default behaviour of
    a glob and never a decision: the work shipped, the routes were taken, the plan will not
    be re-executed, so a finding on it is actionable by nobody. Measured on the real tree
    before this landed: 36 violations across 8 plans — 27 `no files: line`, 8 the
    pre-FEAT-06 prose shape, 0 routing defects, every one in delivered work. That noise is
    why issue #133's gate could never be switched on.

    Both directions, because a skip that skips everything would pass the first case alone.
    """
    results = []
    for status, want_checked in (("shipped", False), ("abandoned", False),
                                 ("in_review", True), ("awaiting_user", True)):
        with tempfile.TemporaryDirectory() as td:
            fd = _yaml_project(td, files=".claude/skills/harness-spec-driven/SKILL.md")
            with open(os.path.join(fd, "feature.yaml"), "w") as f:
                f.write(f"feature_id: FEAT-A\nstatus: {status}\n")
            r = run(project_dir=td)
            checked = "ungranted (NOBODY)" in r.stdout
            ok = checked == want_checked
            results.append(ok)
            check(f"case_24_{status}_is_{'checked' if want_checked else 'skipped'}",
                  ok, f"exit {r.returncode}, checked={checked}: {r.stdout[:160]!r}")

    # A feature we CANNOT classify is checked, never skipped. The failure that matters is a
    # live plan going unexamined; an old one examined twice costs nothing.
    with tempfile.TemporaryDirectory() as td:
        _yaml_project(td, files=".claude/skills/harness-spec-driven/SKILL.md")
        r = run(project_dir=td)              # no feature.yaml at all
        check("case_24_no_feature_yaml_is_checked_not_skipped",
              "ungranted (NOBODY)" in r.stdout, r.stdout[:200])

    # A feature.yaml THAT PARSES BUT IS NOT A MAPPING. This is the case the four statuses
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
    for label, body in (("a_sequence", "- a\n- b\n"),
                        ("a_bare_scalar", "shipped\n"),
                        ("status_is_a_list", "status:\n  - shipped\n"),
                        # A MAPPING WITH NO `status:` KEY AT ALL. The only shape reaching
                        # `bool(token)` -- `"".split()` is `[]`, so without the guard
                        # `token[0]` raises IndexError and the run dies with empty stdout
                        # and exit 1, the code a real violation uses.
                        #
                        # ONLY TWO of the shapes above stop at the isinstance check --
                        # `a_sequence` and `a_bare_scalar`. An earlier version of this
                        # comment said four, which libelled the one case that carries its
                        # own weight: `status_is_a_list` IS a dict, reaches `bool(token)`
                        # with a truthy `["['shipped']"]`, and is the SOLE case that
                        # catches removal of the `str()` at check-plan-routes.py:422.
                        # A comment telling the next reader a live case is a duplicate is
                        # how a load-bearing assertion gets deleted as redundant.
                        ("a_mapping_with_no_status", "feature_id: FEAT-A\n")):
        with tempfile.TemporaryDirectory() as td:
            fd = _yaml_project(td, files=".claude/skills/harness-spec-driven/SKILL.md")
            with open(os.path.join(fd, "feature.yaml"), "w") as f:
                f.write(body)
            r = run(project_dir=td)
            ok = ("Traceback" not in r.stderr
                  and "ungranted (NOBODY)" in r.stdout
                  and "1 violation(s) across 1 plan(s)" in r.stdout)
            results.append(ok)
            check(f"case_24_feature_yaml_{label}_is_checked_not_crashed",
                  ok, f"exit {r.returncode}, stderr={r.stderr[:120]!r}, "
                      f"stdout={r.stdout[-120:]!r}")
    return all(results)


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
    # CODED EXCEPTIONS, each naming its issue — never a silent skip, and never prose.
    # wayfind.py:46-54 probes the `.harness` DIRECTORY on purpose: it walks UP from the cwd
    # so a session inside a feature dir still resolves. That upward walk is also why it is
    # exposed — `$HOME/.harness/` exists wherever deploy.sh has run (it holds
    # registry.json), so from anywhere under $HOME with no project of its own it resolves
    # $HOME as the project root. Found by THIS case on its first full-tree run, filed as
    # its own issue, and listed here rather than fixed inside PR #153, which is about a
    # different script.
    KNOWN_DIRECTORY_PROBE = {"wayfind.py"}
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
        if fname in KNOWN_DIRECTORY_PROBE:
            continue
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

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print("\nALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
