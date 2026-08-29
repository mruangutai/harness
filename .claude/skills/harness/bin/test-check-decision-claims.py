#!/usr/bin/env python3
"""Tests for check-decision-claims.py, the executable-claims checker.

Most cases run against a SYNTHETIC fixture written into this test's own temp
directory, never against the live document — a test that reads live state passes
or fails for reasons that have nothing to do with the code under test. The
fixture path is passed explicitly (`--file`) on every invocation, so a checker
that resolved its default at import time rather than call time would still be
caught reading the wrong thing. Those cases test the checker's LOGIC and stay
hermetic.

One case, `test_live_authority_claims_all_hold`, is different by design: it runs
the checker against the LIVE `.harness/harness/docs/DECISIONS.md` and guards the
AUTHORITY itself, not the checker's logic. It is expected to move with the tree
— a claim marker whose command's output no longer matches its expected
substring must redden it — and it resolves the live path through the checker's
own `DECISIONS_REL_PATH` constant rather than a second, hand-rolled resolution.

Commands under `git`/`grep` are used exclusively for the passing/failing cases so
the fixtures exercise the real allow-listed path, not a stand-in for it.
"""
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import time

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BIN_DIR, "..", "..", "..", ".."))
CHECKER = os.environ.get("CHECK_DECISION_CLAIMS_BIN") or os.path.join(
    BIN_DIR, "check-decision-claims.py"
)

_spec = importlib.util.spec_from_file_location("check_decision_claims", CHECKER)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LIVE_DECISIONS = os.path.join(REPO_ROOT, _mod.DECISIONS_REL_PATH)


def run_checker(fixture_path):
    return subprocess.run(
        [sys.executable, CHECKER, "--file", fixture_path],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )


def write_fixture(tmp, name, text):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def test_matching_claim_exits_zero():
    name = "test_matching_claim_exits_zero"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-01 — A heading\n\n"
                "Body text.\n\n"
                '<!-- claim: grep -c "DEC-01" ' + fixture_self(tmp) + " :: 1 -->\n",
            )
            r = run_checker(fixture)
            if r.returncode != 0:
                print(f"FAIL - {name}: expected exit 0, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "examined 1 claim" not in r.stdout:
                print(f"FAIL - {name}: did not report examining 1 claim: {r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def fixture_self(tmp):
    """A stable path, inside `tmp`, that the fixture itself can grep for its own
    heading text — written first so the claim's command has something real to
    check against, independent of the checker under test."""
    path = os.path.join(tmp, "self.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("DEC-01\n")
    return path


def test_mismatching_claim_reports_heading_and_exits_one():
    name = "test_mismatching_claim_reports_heading_and_exits_one"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            grepped = os.path.join(tmp, "target.md")
            with open(grepped, "w", encoding="utf-8") as f:
                f.write("nothing matching here\n")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-42 — The mismatching heading\n\n"
                f'<!-- claim: grep -c "needle" {grepped} :: 7 -->\n',
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "DEC-42" not in r.stdout:
                print(f"FAIL - {name}: failing claim was not reported by its DEC "
                      f"heading: {r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_disallowed_first_token_is_refused_and_exits_one():
    name = "test_disallowed_first_token_is_refused_and_exits_one"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-07 — An unsafe heading\n\n"
                '<!-- claim: python3 -c "print(1)" :: 1 -->\n',
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout:
                print(f"FAIL - {name}: did not report the claim as REFUSED "
                      f"(only a nonzero exit is not enough): {r.stdout!r}")
                return False
            if "python3" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the disallowed "
                      f"command: {r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_git_c_core_fsmonitor_quoted_is_refused_and_payload_does_not_run():
    """FEAT-38 F-3: `git -c "core.fsmonitor=<cmd>" status` reproduced live —
    the quoted-value form. Refusal alone is not enough; the payload's own
    side effect (a touched file) must be provably absent."""
    name = "test_git_c_core_fsmonitor_quoted_is_refused_and_payload_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            payload = os.path.join(tmp, "touched")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-10 — core.fsmonitor via -c, quoted\n\n"
                f'<!-- claim: git -c "core.fsmonitor=touch {payload}" status '
                ":: nothing -->\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout or "'-c'" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the -c option: "
                      f"{r.stdout!r}")
                return False
            if os.path.exists(payload):
                print(f"FAIL - {name}: the payload RAN — {payload} was created")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_git_c_core_fsmonitor_unquoted_is_refused_and_payload_does_not_run():
    """Same vector, written with a backslash-escaped space instead of quote
    characters — refusal must not depend on how the marker text is quoted."""
    name = "test_git_c_core_fsmonitor_unquoted_is_refused_and_payload_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            payload = os.path.join(tmp, "touched")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-10b — core.fsmonitor via -c, unquoted\n\n"
                f"<!-- claim: git -c core.fsmonitor=touch\\ {payload} status "
                ":: nothing -->\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout or "'-c'" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the -c option: "
                      f"{r.stdout!r}")
                return False
            if os.path.exists(payload):
                print(f"FAIL - {name}: the payload RAN — {payload} was created")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_git_c_diff_external_quoted_is_refused_and_payload_does_not_run():
    """FEAT-38 F-3: `git -c "diff.external=<cmd>" diff --ext-diff` reproduced
    live — the quoted-value form."""
    name = "test_git_c_diff_external_quoted_is_refused_and_payload_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            payload = os.path.join(tmp, "touched")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-11 — diff.external via -c, quoted\n\n"
                f'<!-- claim: git -c "diff.external=touch {payload}" diff '
                "--ext-diff :: nothing -->\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout or "'-c'" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the -c option: "
                      f"{r.stdout!r}")
                return False
            if os.path.exists(payload):
                print(f"FAIL - {name}: the payload RAN — {payload} was created")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_git_c_diff_external_unquoted_is_refused_and_payload_does_not_run():
    """Same vector, backslash-escaped instead of quoted."""
    name = "test_git_c_diff_external_unquoted_is_refused_and_payload_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            payload = os.path.join(tmp, "touched")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-11b — diff.external via -c, unquoted\n\n"
                f"<!-- claim: git -c diff.external=touch\\ {payload} diff "
                "--ext-diff :: nothing -->\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout or "'-c'" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the -c option: "
                      f"{r.stdout!r}")
                return False
            if os.path.exists(payload):
                print(f"FAIL - {name}: the payload RAN — {payload} was created")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_git_c_alias_quoted_is_refused_and_payload_does_not_run():
    """FEAT-38 F-3: `git -c alias.zz='!<cmd>' zz`, and the checker's own
    exemplar marker `git -c "alias.zz=!touch /tmp/p_f" zz` — reproduced live,
    quoted-value form."""
    name = "test_git_c_alias_quoted_is_refused_and_payload_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            payload = os.path.join(tmp, "touched")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-12 — alias.zz via -c, quoted\n\n"
                f'<!-- claim: git -c "alias.zz=!touch {payload}" zz '
                ":: nothing -->\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout or "'-c'" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the -c option: "
                      f"{r.stdout!r}")
                return False
            if os.path.exists(payload):
                print(f"FAIL - {name}: the payload RAN — {payload} was created")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_git_c_alias_unquoted_is_refused_and_payload_does_not_run():
    """Same vector, backslash-escaped instead of quoted."""
    name = "test_git_c_alias_unquoted_is_refused_and_payload_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            payload = os.path.join(tmp, "touched")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-12b — alias.zz via -c, unquoted\n\n"
                f"<!-- claim: git -c alias.zz=!touch\\ {payload} zz "
                ":: nothing -->\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout or "'-c'" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the -c option: "
                      f"{r.stdout!r}")
                return False
            if os.path.exists(payload):
                print(f"FAIL - {name}: the payload RAN — {payload} was created")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_git_disallowed_subcommand_is_refused_and_init_does_not_run():
    """Rejected-subcommand case: `git init <dir>` clears rule 2 (no option
    before the subcommand) but must be refused by rule 3 (subcommand
    allowlist). `init`'s own side effect — creating a directory — stands in
    for a touched file: it must never be created."""
    name = "test_git_disallowed_subcommand_is_refused_and_init_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = os.path.join(tmp, "should-not-be-created")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-13 — a disallowed subcommand\n\n"
                f'<!-- claim: git init {target_dir} :: nothing -->\n',
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if ("REFUSED" not in r.stdout or "subcommand" not in r.stdout
                    or "'init'" not in r.stdout):
                print(f"FAIL - {name}: refusal did not name the disallowed "
                      f"subcommand: {r.stdout!r}")
                return False
            if os.path.isdir(target_dir):
                print(f"FAIL - {name}: the payload RAN — {target_dir} was "
                      f"created by git init")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_git_global_option_before_subcommand_is_refused_and_payload_does_not_run():
    """Rejected-global-option case: `git -C /tmp ...` must be refused by rule
    2 same as -c, and an embedded -c payload after it must never run either
    — refusal fires on the FIRST leading option, before any of it is read."""
    name = "test_git_global_option_before_subcommand_is_refused_and_payload_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            payload = os.path.join(tmp, "touched")
            target = os.path.join(tmp, "target.md")
            with open(target, "w", encoding="utf-8") as f:
                f.write("nothing\n")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-14 — a global option before the subcommand\n\n"
                f'<!-- claim: git -C /tmp -c "core.fsmonitor=touch {payload}" '
                f"grep -c x {target} :: nothing -->\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout or "'-C'" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the -C global "
                      f"option: {r.stdout!r}")
                return False
            if os.path.exists(payload):
                print(f"FAIL - {name}: the payload RAN — {payload} was created")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_grep_dash_f_argument_file_is_refused_and_never_blocks_on_fifo():
    """`-f` reads patterns from a file instead of argv; pointed at a FIFO
    with no writer, an actually-executed grep would block for the full 10s
    timeout waiting for data. A fast refusal is itself proof the subprocess
    was never launched — a slow one would mean it was."""
    name = "test_grep_dash_f_argument_file_is_refused_and_never_blocks_on_fifo"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fifo = os.path.join(tmp, "patterns.fifo")
            os.mkfifo(fifo)
            target = os.path.join(tmp, "target.md")
            with open(target, "w", encoding="utf-8") as f:
                f.write("nothing\n")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-15 — grep -f reading an argument file\n\n"
                f'<!-- claim: grep -f {fifo} {target} :: nothing -->\n',
            )
            started = time.monotonic()
            r = run_checker(fixture)
            elapsed = time.monotonic() - started
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout or "'-f'" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the -f option: "
                      f"{r.stdout!r}")
                return False
            if elapsed >= 5:
                print(f"FAIL - {name}: took {elapsed:.1f}s — grep appears to "
                      f"have actually blocked reading the fifo instead of "
                      f"being refused before it ran: {r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_git_grep_open_pager_option_is_refused_and_payload_does_not_run():
    """`git grep -O<cmd>` invokes <cmd> directly, quite apart from -c — the
    bundled short-option form reproduced live."""
    name = "test_git_grep_open_pager_option_is_refused_and_payload_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            payload = os.path.join(tmp, "touched")
            target = os.path.join(tmp, "target.md")
            with open(target, "w", encoding="utf-8") as f:
                f.write("needle\n")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-16 — git grep -O opens a pager directly\n\n"
                f"<!-- claim: git grep -Otouch\\ {payload} needle {target} "
                ":: nothing -->\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "REFUSED" not in r.stdout or "-O" not in r.stdout:
                print(f"FAIL - {name}: refusal did not name the -O option: "
                      f"{r.stdout!r}")
                return False
            if os.path.exists(payload):
                print(f"FAIL - {name}: the payload RAN — {payload} was created")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_ambient_git_config_env_is_neutralized_and_payload_does_not_run():
    """FEAT-38 rule 5: the checker's own PROCESS environment can carry an
    ambient GIT_CONFIG_GLOBAL pointing at a hostile config — set by a CI
    runner or a developer's shell, never named in the marker or argv at all —
    this pins that rule 5 neutralizes it at the ONE subprocess.run call site
    regardless of what the checker inherited. No rule 1/2/3/4/6 token is
    involved: `git diff --ext-diff` is a bare allowlisted subcommand with no
    options, so this exercises rule 5 in isolation. `diff.external` is the
    config key: a real diff of a modified tracked file routes through it, so
    a neutralized config falls back to git's internal diff (the expected
    substring below) and an un-neutralized one runs the external command
    directly — same mechanism as the F-3 `-c diff.external=` vectors, but
    reached ambiently instead of through an argv option."""
    name = "test_ambient_git_config_env_is_neutralized_and_payload_does_not_run"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            repo = os.path.join(tmp, "repo")
            os.makedirs(repo)
            git_env = dict(os.environ)
            git_env.update({
                "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
            })
            subprocess.run(["git", "init", "-q"], cwd=repo, env=git_env, check=True)
            tracked = os.path.join(repo, "tracked.txt")
            with open(tracked, "w", encoding="utf-8") as f:
                f.write("hello\n")
            subprocess.run(["git", "add", "tracked.txt"], cwd=repo, env=git_env,
                            check=True)
            subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo,
                            env=git_env, check=True)
            with open(tracked, "a", encoding="utf-8") as f:
                f.write("world\n")

            payload = os.path.join(tmp, "touched")
            hostile_config = os.path.join(tmp, "hostile_gitconfig")
            with open(hostile_config, "w", encoding="utf-8") as f:
                f.write(f"[diff]\n\texternal = touch {payload}\n")

            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-16b — ambient diff.external must not be reachable\n\n"
                "<!-- claim: git diff --ext-diff -- tracked.txt "
                ":: diff --git -->\n",
            )

            checker_env = dict(os.environ)
            checker_env["GIT_CONFIG_GLOBAL"] = hostile_config
            checker_env["HOME"] = tmp
            r = subprocess.run(
                [sys.executable, CHECKER, "--file", fixture],
                cwd=repo, capture_output=True, text=True, env=checker_env,
            )
            if "REFUSED" in r.stdout:
                print(f"FAIL - {name}: rule 1-4/6 refused an allowlisted bare "
                      f"subcommand — this test no longer exercises rule 5: "
                      f"{r.stdout!r}")
                return False
            if os.path.exists(payload):
                print(f"FAIL - {name}: the ambient diff.external payload "
                      f"RAN — {payload} was created; rule 5's env override "
                      f"did not reach the subprocess.run call: {r.stdout!r}")
                return False
            if r.returncode != 0:
                print(f"FAIL - {name}: expected exit 0 (real diff output "
                      f"matches the expected substring once diff.external is "
                      f"neutralized), got {r.returncode}: {r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_malformed_claim_marker_single_colon_reports_line_and_exits_one():
    """FEAT-38 F-4: a single `:` where `::` belongs must not silently vanish
    — it must be reported by line number and counted as a failure."""
    name = "test_malformed_claim_marker_single_colon_reports_line_and_exits_one"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-17 — a malformed marker\n\n"
                '<!-- claim: grep -c "x" file.md : 1 -->\n',
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "decisions.md:3" not in r.stdout:
                print(f"FAIL - {name}: did not report the malformed line's "
                      f"number: {r.stdout!r}")
                return False
            if "malformed" not in r.stdout:
                print(f"FAIL - {name}: did not name the failure as malformed: "
                      f"{r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_malformed_claim_marker_trailing_text_reports_line_and_exits_one():
    """FEAT-38 F-4: trailing text after `-->` must not silently vanish either
    — same treatment, same report."""
    name = "test_malformed_claim_marker_trailing_text_reports_line_and_exits_one"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-18 — a malformed marker with trailing text\n\n"
                '<!-- claim: grep -c "x" file.md :: 1 --> trailing junk\n',
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "decisions.md:3" not in r.stdout:
                print(f"FAIL - {name}: did not report the malformed line's "
                      f"number: {r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_zero_markers_exits_zero_and_says_so():
    """A silent zero-claim pass must be distinguishable from a working one: the
    checker must SAY it examined zero claims, not just exit 0 with no output."""
    name = "test_zero_markers_exits_zero_and_says_so"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-01 — A heading with no claim markers at all\n\n"
                "Just prose.\n",
            )
            r = run_checker(fixture)
            if r.returncode != 0:
                print(f"FAIL - {name}: expected exit 0, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "examined 0 claim" not in r.stdout:
                print(f"FAIL - {name}: did not state it examined zero claims: "
                      f"{r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_nonexistent_path_in_command_is_a_failure_not_a_crash():
    name = "test_nonexistent_path_in_command_is_a_failure_not_a_crash"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, "does-not-exist-xyz123.md")
            fixture = write_fixture(
                tmp, "decisions.md",
                "## DEC-99 — A heading whose claim names a missing path\n\n"
                f'<!-- claim: grep -c "anything" {missing} :: 1 -->\n',
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1 (failure, not a crash or "
                      f"skip), got {r.returncode}: {r.stdout!r} {r.stderr!r}")
                return False
            if "DEC-99" not in r.stdout:
                print(f"FAIL - {name}: failing claim was not reported by its DEC "
                      f"heading: {r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_unreadable_target_exits_two_not_zero():
    name = "test_unreadable_target_exits_two_not_zero"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, "no-such-file.md")
            r = run_checker(missing)
            if r.returncode != 2:
                print(f"FAIL - {name}: expected exit 2 for an unreadable target, "
                      f"got {r.returncode}: {r.stdout!r} {r.stderr!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_checker_source_never_uses_shell_true():
    """The safety boundary is not optional: assert it directly against the
    checker's own source, not just indirectly through behavior."""
    name = "test_checker_source_never_uses_shell_true"
    try:
        with open(CHECKER, encoding="utf-8") as f:
            src = f.read()
        if "shell=True" in src:
            print(f"FAIL - {name}: checker source contains shell=True")
            return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_live_authority_claims_all_hold():
    """FEAT-38 T-1x: guards the AUTHORITY itself, not the checker's logic — a
    claim marker whose command's stdout no longer contains its expected
    substring anywhere in the live DECISIONS.md must redden this case. The live
    path is resolved through the checker's own DECISIONS_REL_PATH constant
    (never a second, hand-rolled join), so this traverses the identical code
    path a mutation-copy run traverses, differing only in the path string."""
    name = "test_live_authority_claims_all_hold"
    try:
        r = run_checker(LIVE_DECISIONS)
        if r.returncode != 0:
            print(f"FAIL - {name}: expected exit 0 against the live authority, "
                  f"got {r.returncode}: stdout={r.stdout!r} stderr={r.stderr!r}")
            return False
        if "REFUSED" in r.stdout:
            print(f"FAIL - {name}: a claim marker was REFUSED (disallowed first "
                  f"token) in the live authority: {r.stdout!r}")
            return False
        m = re.search(r"examined (\d+) claim\(s\), (\d+) failed", r.stdout)
        if m is None:
            print(f"FAIL - {name}: no summary line found in stdout: {r.stdout!r}")
            return False
        examined, failed = int(m.group(1)), int(m.group(2))
        if examined == 0:
            print(f"FAIL - {name}: examined 0 claims — the checker or its path "
                  f"resolution is broken, not proven clean: {r.stdout!r}")
            return False
        if failed != 0:
            print(f"FAIL - {name}: {failed} claim(s) failed in the live "
                  f"authority: {r.stdout!r}")
            return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


TESTS = [
    test_matching_claim_exits_zero,
    test_mismatching_claim_reports_heading_and_exits_one,
    test_disallowed_first_token_is_refused_and_exits_one,
    test_git_c_core_fsmonitor_quoted_is_refused_and_payload_does_not_run,
    test_git_c_core_fsmonitor_unquoted_is_refused_and_payload_does_not_run,
    test_git_c_diff_external_quoted_is_refused_and_payload_does_not_run,
    test_git_c_diff_external_unquoted_is_refused_and_payload_does_not_run,
    test_git_c_alias_quoted_is_refused_and_payload_does_not_run,
    test_git_c_alias_unquoted_is_refused_and_payload_does_not_run,
    test_git_disallowed_subcommand_is_refused_and_init_does_not_run,
    test_git_global_option_before_subcommand_is_refused_and_payload_does_not_run,
    test_grep_dash_f_argument_file_is_refused_and_never_blocks_on_fifo,
    test_git_grep_open_pager_option_is_refused_and_payload_does_not_run,
    test_ambient_git_config_env_is_neutralized_and_payload_does_not_run,
    test_malformed_claim_marker_single_colon_reports_line_and_exits_one,
    test_malformed_claim_marker_trailing_text_reports_line_and_exits_one,
    test_zero_markers_exits_zero_and_says_so,
    test_nonexistent_path_in_command_is_a_failure_not_a_crash,
    test_unreadable_target_exits_two_not_zero,
    test_checker_source_never_uses_shell_true,
    test_live_authority_claims_all_hold,
]


def main():
    results = []
    for t in TESTS:
        try:
            results.append(t())
        except Exception as e:
            print(f"FAIL - {t.__name__}: {type(e).__name__}: {e}")
            results.append(False)

    if all(results):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
