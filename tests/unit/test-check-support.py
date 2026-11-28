#!/usr/bin/env python3
"""tests/check_support.py's Checks: report() is the exit code a unit file hands to sys.exit.

The runner reads only a child's exit code, so the contract under test is the integer report()
returns: 1 when any check failed, 1 when no check ran at all, 0 only when at least one check ran
and every one passed. Each case drives a fresh Checks in-process with stdout captured.
"""
import contextlib
import io
import unittest

import unit_support  # noqa: F401  (puts tests/ on sys.path)
from check_support import Checks


def _run(results):
    """Record one check per bool in results; return (report() value, captured stdout)."""
    checks = Checks()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        for index, ok in enumerate(results):
            checks.check(f"case-{index}", ok, f"detail-{index}")
        code = checks.report()
    return code, out.getvalue()


class ReportTests(unittest.TestCase):
    def test_a_failing_check_makes_report_return_1(self):
        code, out = _run([True, False, True])
        self.assertEqual(code, 1)
        self.assertIn("FAIL case-1", out)

    def test_zero_checks_makes_report_return_1(self):
        code, out = _run([])
        self.assertEqual(code, 1)
        self.assertIn("no checks ran", out)

    def test_all_passing_checks_make_report_return_0(self):
        code, _out = _run([True, True])
        self.assertEqual(code, 0)


class CheckTests(unittest.TestCase):
    def test_check_returns_the_truth_of_cond(self):
        checks = Checks()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertIs(checks.check("yes", 1), True)
            self.assertIs(checks.check("no", []), False)

    def test_detail_prints_only_on_failure(self):
        _code, out = _run([True, False])
        self.assertNotIn("detail-0", out)
        self.assertIn("detail-1", out)


if __name__ == "__main__":
    unittest.main()
