#!/usr/bin/env python3
"""Tests for check-decision-anchors.py, the anchor-rot checker.

Most cases run against a SYNTHETIC fixture written into this test's own temp
directory, never against the live document — a test that reads live state passes
or fails for reasons that have nothing to do with the code under test. The
fixture path is passed explicitly (`--file`) on every invocation, so a checker
that resolved its default at import time rather than call time would still be
caught reading the wrong thing. Those cases test the checker's LOGIC and stay
hermetic.

One case, `test_live_authority_anchors_all_resolve`, is different by design: it
runs the checker against the LIVE `.harness/harness/docs/DECISIONS.md` and guards
the AUTHORITY itself, not the checker's logic. It is expected to move with the
tree — a rotted anchor added anywhere in the real document must redden it — and
it resolves the live path through the checker's own `DECISIONS_REL_PATH`
constant rather than a second, hand-rolled resolution.

The cited FILE inside each synthetic fixture anchor is a real path tracked in
this repo (picked for stability — CLAUDE.md at the repo root), because the check
under test is "does this basename resolve in `git ls-files`", which is
inherently a question about the real tree the checker is invoked from, not
about the fixture.
"""
import importlib.util
import os
import re
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BIN_DIR, "..", "..", "..", ".."))
CHECKER = os.environ.get("CHECK_DECISION_ANCHORS_BIN") or os.path.join(
    BIN_DIR, "check-decision-anchors.py"
)

_spec = importlib.util.spec_from_file_location("check_decision_anchors", CHECKER)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LIVE_DECISIONS = os.path.join(REPO_ROOT, _mod.DECISIONS_REL_PATH)

# A file guaranteed tracked at REPO_ROOT and stable across runs. Line 1 of a
# non-empty tracked file is always in range regardless of later edits to the file.
REAL_TRACKED_FILE = "CLAUDE.md"
NONEXISTENT_FILE = "does-not-exist-anywhere-xyz123.py"


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


def test_in_range_anchor_reports_nothing_and_exits_zero():
    name = "test_in_range_anchor_reports_nothing_and_exits_zero"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                f"See `{REAL_TRACKED_FILE}:1` for the rule.\n",
            )
            r = run_checker(fixture)
            if r.returncode != 0:
                print(f"FAIL - {name}: expected exit 0, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if REAL_TRACKED_FILE in r.stdout.split("examined")[0]:
                print(f"FAIL - {name}: a clean anchor was reported: {r.stdout!r}")
                return False
            if "examined 1 anchor" not in r.stdout:
                print(f"FAIL - {name}: did not report examining the one anchor: "
                      f"{r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_missing_file_is_reported_and_exits_one():
    name = "test_missing_file_is_reported_and_exits_one"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                f"See `{NONEXISTENT_FILE}:1` for the rule.\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if NONEXISTENT_FILE not in r.stdout:
                print(f"FAIL - {name}: failing anchor was not named: {r.stdout!r}")
                return False
            if "not found" not in r.stdout:
                print(f"FAIL - {name}: did not report the EXISTENCE check as the "
                      f"failure (expected 'not found'): {r.stdout!r}")
                return False
            if "past end" in r.stdout:
                print(f"FAIL - {name}: reported the wrong check (range, not "
                      f"existence): {r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_out_of_range_line_is_reported_and_exits_one():
    name = "test_out_of_range_line_is_reported_and_exits_one"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                f"See `{REAL_TRACKED_FILE}:999999999` for the rule.\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if REAL_TRACKED_FILE not in r.stdout:
                print(f"FAIL - {name}: failing anchor was not named: {r.stdout!r}")
                return False
            if "past end" not in r.stdout:
                print(f"FAIL - {name}: did not report the RANGE check as the "
                      f"failure (expected 'past end'): {r.stdout!r}")
                return False
            if "not found" in r.stdout:
                print(f"FAIL - {name}: reported the wrong check (existence, not "
                      f"range) for a file that does exist: {r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_malformed_anchor_extension_reports_line_and_exits_one():
    """FEAT-38 F-4: a citation shaped like `<file>:<line>` whose extension
    falls outside ANCHOR_RE's strict allowlist must not silently vanish — it
    must be reported by line number and counted as a failure, mirroring
    gen-decisions-index.py's ROW_LOOKALIKE_RE / MalformedRow treatment."""
    name = "test_malformed_anchor_extension_reports_line_and_exits_one"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                "See `some_script.rb:12` for the rule.\n",
            )
            r = run_checker(fixture)
            if r.returncode != 1:
                print(f"FAIL - {name}: expected exit 1, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "decisions.md:1" not in r.stdout:
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


def test_zero_anchors_exits_zero_and_says_so():
    """A silent zero-anchor pass must be distinguishable from a working one: the
    checker must SAY it examined zero anchors, not just exit 0 with no output."""
    name = "test_zero_anchors_exits_zero_and_says_so"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = write_fixture(
                tmp, "decisions.md",
                "Nothing here cites a file or a line at all.\n",
            )
            r = run_checker(fixture)
            if r.returncode != 0:
                print(f"FAIL - {name}: expected exit 0, got {r.returncode}: "
                      f"{r.stdout!r} {r.stderr!r}")
                return False
            if "examined 0 anchor" not in r.stdout:
                print(f"FAIL - {name}: did not state it examined zero anchors: "
                      f"{r.stdout!r}")
                return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_unreadable_target_exits_two_not_zero():
    """An empty result (0 anchors, exit 0) and a target the checker could not even
    read must never look the same — that is what exit 2 is for."""
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


def test_default_file_is_dev_null_readable_zero_anchors():
    """--file /dev/null is readable and holds zero anchors: exit 0, never 2 — the
    exact case the plan's own verify block exercises."""
    name = "test_default_file_is_dev_null_readable_zero_anchors"
    try:
        r = run_checker("/dev/null")
        if r.returncode != 0:
            print(f"FAIL - {name}: expected exit 0 for /dev/null, got "
                  f"{r.returncode}: {r.stdout!r} {r.stderr!r}")
            return False
        if "examined 0 anchor" not in r.stdout:
            print(f"FAIL - {name}: did not state it examined zero anchors: "
                  f"{r.stdout!r}")
            return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


def test_live_authority_anchors_all_resolve():
    """FEAT-38 T-1x: guards the AUTHORITY itself, not the checker's logic — a
    rotted anchor anywhere in the live DECISIONS.md must redden this case. The
    live path is resolved through the checker's own DECISIONS_REL_PATH constant
    (never a second, hand-rolled join), so this traverses the identical code
    path a mutation-copy run traverses, differing only in the path string."""
    name = "test_live_authority_anchors_all_resolve"
    try:
        r = run_checker(LIVE_DECISIONS)
        if r.returncode != 0:
            print(f"FAIL - {name}: expected exit 0 against the live authority, "
                  f"got {r.returncode}: stdout={r.stdout!r} stderr={r.stderr!r}")
            return False
        m = re.search(r"examined (\d+) anchor\(s\), (\d+) failed", r.stdout)
        if m is None:
            print(f"FAIL - {name}: no summary line found in stdout: {r.stdout!r}")
            return False
        examined, failed = int(m.group(1)), int(m.group(2))
        if examined == 0:
            print(f"FAIL - {name}: examined 0 anchors — the checker or its path "
                  f"resolution is broken, not proven clean: {r.stdout!r}")
            return False
        if failed != 0:
            print(f"FAIL - {name}: {failed} anchor(s) failed in the live "
                  f"authority: {r.stdout!r}")
            return False
        print(f"ok - {name}")
        return True
    except Exception as e:
        print(f"FAIL - {name}: {type(e).__name__}: {e}")
        return False


TESTS = [
    test_in_range_anchor_reports_nothing_and_exits_zero,
    test_missing_file_is_reported_and_exits_one,
    test_out_of_range_line_is_reported_and_exits_one,
    test_malformed_anchor_extension_reports_line_and_exits_one,
    test_zero_anchors_exits_zero_and_says_so,
    test_unreadable_target_exits_two_not_zero,
    test_default_file_is_dev_null_readable_zero_anchors,
    test_live_authority_anchors_all_resolve,
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
