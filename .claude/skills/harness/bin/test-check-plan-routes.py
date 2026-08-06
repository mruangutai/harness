#!/usr/bin/env python3
"""Tests for check-plan-routes.py (D-01, D-02, D-04, D-07, D-08).

Fixtures are written under tempfile.mkdtemp() so no repo state is touched.
Each case invokes the real script as a subprocess against a fixture PLAN.md,
and against the repo's own templates/PLAN.md, run-unit-tests.sh and source
for the static/textual checks (cases 8-13, 16).
"""
import os
import re
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("CHECK_PLAN_ROUTES_BIN") or os.path.join(
    BIN_DIR, "check-plan-routes.py")
REPO_ROOT = os.path.abspath(os.path.join(BIN_DIR, "..", "..", "..", ".."))

GRANTED_PATH = ".claude/skills/harness/bin/check-domain.sh"  # granted to two agents
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

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print("\nALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
