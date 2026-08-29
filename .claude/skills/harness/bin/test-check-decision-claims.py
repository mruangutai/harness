#!/usr/bin/env python3
"""Tests for check-decision-claims.py, the executable-claims checker.

Every case runs against a SYNTHETIC fixture written into this test's own temp
directory, never against the live document — a test that reads live state passes
or fails for reasons that have nothing to do with the code. The fixture path is
passed explicitly (`--file`) on every invocation, so a checker that resolved its
default at import time rather than call time would still be caught reading the
wrong thing.

Commands under `git`/`grep` are used exclusively for the passing/failing cases so
the fixtures exercise the real allow-listed path, not a stand-in for it.
"""
import os
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BIN_DIR, "..", "..", "..", ".."))
CHECKER = os.environ.get("CHECK_DECISION_CLAIMS_BIN") or os.path.join(
    BIN_DIR, "check-decision-claims.py"
)


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


TESTS = [
    test_matching_claim_exits_zero,
    test_mismatching_claim_reports_heading_and_exits_one,
    test_disallowed_first_token_is_refused_and_exits_one,
    test_zero_markers_exits_zero_and_says_so,
    test_nonexistent_path_in_command_is_a_failure_not_a_crash,
    test_unreadable_target_exits_two_not_zero,
    test_checker_source_never_uses_shell_true,
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
