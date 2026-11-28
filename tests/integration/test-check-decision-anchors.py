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
from integration_support import ROOT, BIN  # noqa: F401  (puts bin/ on sys.path for the checker's imports)
import importlib.util  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402

from check_support import Checks  # noqa: E402

C = Checks()
check = C.check

REPO_ROOT = str(ROOT)
CHECKER = os.environ.get("CHECK_DECISION_ANCHORS_BIN") or str(BIN / "check-decision-anchors.py")

_spec = importlib.util.spec_from_file_location("check_decision_anchors", CHECKER)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LIVE_DECISIONS = os.path.join(REPO_ROOT, _mod.DECISIONS_REL_PATH)

# A file guaranteed tracked at REPO_ROOT and stable across runs. Line 1 of a
# non-empty tracked file is always in range regardless of later edits to the file.
REAL_TRACKED_FILE = "CLAUDE.md"
NONEXISTENT_FILE = "does-not-exist-anywhere-xyz123.py"

# One synthetic fixture per row: (check name, fixture text, expected exit,
# substrings stdout must contain, substrings stdout must not contain).
FIXTURE_CASES = [
    # A clean anchor is examined and not reported (the head-of-stdout check
    # for this row lives in fixture_problems).
    ("test_in_range_anchor_reports_nothing_and_exits_zero",
     f"See `{REAL_TRACKED_FILE}:1` for the rule.\n", 0,
     ["examined 1 anchor"], []),
    # The EXISTENCE check fails, not the range check.
    ("test_missing_file_is_reported_and_exits_one",
     f"See `{NONEXISTENT_FILE}:1` for the rule.\n", 1,
     [NONEXISTENT_FILE, "not found"], ["past end"]),
    # The RANGE check fails, not the existence check, for a file that exists.
    ("test_out_of_range_line_is_reported_and_exits_one",
     f"See `{REAL_TRACKED_FILE}:999999999` for the rule.\n", 1,
     [REAL_TRACKED_FILE, "past end"], ["not found"]),
    # FEAT-38 F-4: a citation shaped like `<file>:<line>` whose extension falls
    # outside ANCHOR_RE's strict allowlist must not silently vanish — it must be
    # reported by line number and counted as a failure, mirroring
    # gen-decisions-index.py's ROW_LOOKALIKE_RE / MalformedRow treatment.
    ("test_malformed_anchor_extension_reports_line_and_exits_one",
     "See `some_script.rb:12` for the rule.\n", 1,
     ["decisions.md:1", "malformed"], []),
    # A silent zero-anchor pass must be distinguishable from a working one: the
    # checker must SAY it examined zero anchors, not just exit 0 with no output.
    ("test_zero_anchors_exits_zero_and_says_so",
     "Nothing here cites a file or a line at all.\n", 0,
     ["examined 0 anchor"], []),
]


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


def output_problems(r, expected_exit, must_contain=(), must_not_contain=()):
    """Every way r departs from the expected exit and stdout substrings."""
    problems = []
    if r.returncode != expected_exit:
        problems.append(f"expected exit {expected_exit}, got {r.returncode}")
    problems += [f"stdout lacks {s!r}" for s in must_contain if s not in r.stdout]
    problems += [f"stdout has {s!r}" for s in must_not_contain if s in r.stdout]
    return problems


def check_output(name, r, problems):
    check(name, not problems,
          "\n".join(problems + [f"stdout={r.stdout!r}", f"stderr={r.stderr!r}"]))


def check_fixture_cases(tmp):
    for i, (name, text, expected_exit, present, absent) in enumerate(FIXTURE_CASES):
        case_dir = os.path.join(tmp, str(i))
        os.mkdir(case_dir)
        r = run_checker(write_fixture(case_dir, "decisions.md", text))
        problems = output_problems(r, expected_exit, present, absent)
        if expected_exit == 0 and REAL_TRACKED_FILE in text \
                and REAL_TRACKED_FILE in r.stdout.split("examined")[0]:
            problems.append("a clean anchor was reported")
        check_output(name, r, problems)


def check_unreadable_target(tmp):
    """An empty result (0 anchors, exit 0) and a target the checker could not even
    read must never look the same — that is what exit 2 is for."""
    r = run_checker(os.path.join(tmp, "no-such-file.md"))
    check_output("test_unreadable_target_exits_two_not_zero", r, output_problems(r, 2))


def check_dev_null():
    """--file /dev/null is readable and holds zero anchors: exit 0, never 2 — the
    exact case the plan's own verify block exercises."""
    r = run_checker("/dev/null")
    check_output("test_default_file_is_dev_null_readable_zero_anchors", r,
                 output_problems(r, 0, ["examined 0 anchor"]))


def live_summary_problems(stdout):
    m = re.search(r"examined (\d+) anchor\(s\), (\d+) failed", stdout)
    if m is None:
        return ["no summary line found in stdout"]
    examined, failed = int(m.group(1)), int(m.group(2))
    problems = []
    if examined == 0:
        problems.append("examined 0 anchors — the checker or its path "
                        "resolution is broken, not proven clean")
    if failed != 0:
        problems.append(f"{failed} anchor(s) failed in the live authority")
    return problems


def check_live_authority():
    """FEAT-38 T-1x: guards the AUTHORITY itself, not the checker's logic — a
    rotted anchor anywhere in the live DECISIONS.md must redden this case. The
    live path is resolved through the checker's own DECISIONS_REL_PATH constant
    (never a second, hand-rolled join), so this traverses the identical code
    path a mutation-copy run traverses, differing only in the path string."""
    r = run_checker(LIVE_DECISIONS)
    check_output("test_live_authority_anchors_all_resolve", r,
                 output_problems(r, 0) + live_summary_problems(r.stdout))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        check_fixture_cases(tmp)
        check_unreadable_target(tmp)
    check_dev_null()
    check_live_authority()
    sys.exit(C.report())


if __name__ == "__main__":
    main()
