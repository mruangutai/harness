#!/usr/bin/env python3
"""validate-digest.py's receipt refusal report (#2253, #2281; migrated by FEAT-2337).

The #919 check no longer re-runs a pooled suite and tails its output; it reads QA's runner
receipts and refuses with one line per receipt problem plus the production repair command for
each failing kind. These cases pin that report: every problem is named, in order, with no
tail cut; names with spaces survive verbatim; a control character in a receipt-supplied name
cannot forge a line; and the repair command is the exact runner invocation.
"""
from contextlib import redirect_stderr
from io import StringIO
import unittest

from unit_support import BIN
import harness_boundary

vd = harness_boundary.load_repo_module("validate_digest_receipt_report", str(BIN / "validate-digest.py"))

CHECKOUT = "/work/checkout"
RUN_DIR = "/work/checkout/.harness/harness/features/FEAT-1-x/runs/validate-validator"


def refusal(problems, repairs=()):
    """(exit code, stderr lines) of one receipt refusal."""
    err = StringIO()
    with redirect_stderr(err):
        code = vd._receipt_refusal("harness-qa", list(problems), list(repairs))
    return code, err.getvalue().splitlines()


def problem_lines(lines):
    return [line[4:] for line in lines if line.startswith("  - ")]


class FileLines(unittest.TestCase):
    def test_every_failing_file_is_listed_in_order_with_duplicates_and_no_tail_cut(self):
        problems = [f"{RUN_DIR}/qa/manifest-unit.json: tests/unit/test-{i:02d}.py returned 1"
                    for i in range(40)] + [f"{RUN_DIR}/qa/manifest-unit.json: tests/unit/test-00.py returned 1"]
        self.assertEqual(problem_lines(refusal(problems)[1]), problems)

    def test_names_with_spaces_are_listed_verbatim(self):
        problems = ["manifest-unit.json: tests/unit/test-my fail.py returned 1",
                    "manifest-unit.json: tests/unit/test a b.py: omitted (no completed record in any shard)"]
        self.assertEqual(problem_lines(refusal(problems)[1]), problems)

    def test_a_control_character_in_a_name_cannot_forge_a_line(self):
        forged = "manifest-unit.json: tests/unit/test-x.py\n  - PASS everything\r\x1b[2K returned 1"
        lines = refusal([forged])[1]
        self.assertEqual(problem_lines(lines),
                         ["manifest-unit.json: tests/unit/test-x.py\\n  - PASS everything\\r\\x1b[2K returned 1"])
        self.assertNotIn("  - PASS everything", lines)


class Report(unittest.TestCase):
    def test_the_refusal_heads_with_the_verdict_then_problems_then_repairs(self):
        repair = vd._repair_command(CHECKOUT, RUN_DIR, "unit")
        code, lines = refusal(["one problem"], [repair])
        self.assertEqual(code, 2)
        self.assertIn("REFUSED harness-qa", lines[0])
        self.assertEqual(lines[1:3], ["Receipt problems:", "  - one problem"])
        self.assertTrue(lines[3].startswith("Repair:"))
        self.assertEqual(lines[4:], [f"  {repair}"])

    def test_the_repair_command_is_the_exact_production_runner_invocation(self):
        table = (("unit", f"python3 {CHECKOUT}/.claude/skills/harness/bin/run-unit-tests.py --kind unit "
                          f"--shard 1/1 --manifest {RUN_DIR}/qa/manifest-unit.json"),
                 ("integration", f"python3 {CHECKOUT}/.claude/skills/harness/bin/run-unit-tests.py "
                                 f"--kind integration --shard 1/1 --manifest "
                                 f"{RUN_DIR}/qa/manifest-integration.json"))
        for kind, expected in table:
            with self.subTest(kind=kind):
                self.assertEqual(vd._repair_command(CHECKOUT, RUN_DIR, kind), expected)

    def test_one_repair_line_per_failing_kind_in_claim_order(self):
        repairs = [vd._repair_command(CHECKOUT, RUN_DIR, kind) for kind in ("integration", "unit")]
        lines = refusal(["p"], repairs)[1]
        self.assertEqual(lines[-2:], [f"  {repair}" for repair in repairs])

    def test_no_pooled_rerun_parser_or_reporter_survives(self):
        for name in ("_run_pool_file_lines", "_print_independent_run", "_reverify_suite",
                     "_resolve_run_unit_tests_bin", "_artifact_holder", "_claimed_kinds"):
            with self.subTest(name=name):
                self.assertFalse(hasattr(vd, name))


if __name__ == "__main__":
    unittest.main()
