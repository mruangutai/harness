#!/usr/bin/env python3
"""check_state/corpus.py's pure diagnostics (FEAT-1559 SC-04, SC-09, SC-13).

The preflight's decisions are made by three small functions; each is handed the exact input a
caller produces and graded on what it decides. The case that matters most is the combined one:
a report whose own exit is dirty (8) while it also carries a structural finding must refuse,
because dirty outranks every structural code in worktree-state.py's exit.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude/skills/harness/bin"))
import feature_corpus as fc  # noqa: E402
from check_state import corpus  # noqa: E402


def report(*codes):
    labels = {8: "dirty", 3: "cone", 4: "skip-bits", 7: "materialisation"}
    return {"checkout": "/c", "noop": None, "findings": [
        {"code": c, "label": labels.get(c, "?"), "paths": [], "detail": f"d{c}"} for c in codes]}


class VerifyReport(unittest.TestCase):
    def test_structural_codes_are_kept(self):
        structural, dirty, error = fc.verify_report_findings(report(3, 4, 7))
        self.assertEqual(([f["code"] for f in structural], dirty, error), ([3, 4, 7], None, None))

    def test_dirty_alone_is_not_structural(self):
        structural, dirty, error = fc.verify_report_findings(report(8))
        self.assertEqual((structural, dirty["code"], error), ([], 8, None))

    def test_dirty_does_not_mask_a_structural_finding(self):
        structural, dirty, error = fc.verify_report_findings(report(8, 7))
        self.assertEqual(([f["code"] for f in structural], dirty["code"], error), ([7], 8, None))

    def test_clean_report(self):
        self.assertEqual(fc.verify_report_findings(report()), ([], None, None))

    def test_unusable_reports_are_errors_never_permission(self):
        for doc in (None, [], "text", {"checkout": "/c"}, {"findings": "x"},
                    {"findings": [1]}, {"error": "boom"}):
            _s, _d, error = fc.verify_report_findings(doc)
            self.assertIsNotNone(error, doc)

    def test_an_unknown_code_is_an_error(self):
        _s, _d, error = fc.verify_report_findings(report(5))
        self.assertIn("unknown finding code", error)


class NameSets(unittest.TestCase):
    def test_equal_sets_say_nothing(self):
        self.assertEqual(corpus.name_set_findings(["h/A", "h/B"], ["h/B", "h/A"], "R"), ([], []))

    def test_missing_refuses_with_counts_sorted_names_and_remedy(self):
        refusal, notes = corpus.name_set_findings(["h/C", "h/A", "k/B"], ["h/A", "x/Z"], "REMEDY")
        self.assertEqual(notes, [])
        self.assertEqual(len(refusal), 1)
        line = refusal[0]
        self.assertIn("reaches 1 of 3", line)
        self.assertIn("missing: h/C, k/B", line)
        self.assertIn("unexpected: x/Z", line)
        self.assertIn("No invariant ran", line)
        self.assertIn("REMEDY", line)

    def test_unexpected_only_is_a_note_not_a_refusal(self):
        refusal, notes = corpus.name_set_findings(["h/A"], ["h/A", "h/WIP"], "R")
        self.assertEqual(refusal, [])
        self.assertIn("h/WIP", notes[0])
        self.assertIn("not gating", notes[0])


class Subject(unittest.TestCase):
    def test_no_selector_is_no_refusal(self):
        self.assertIsNone(corpus.subject_refusal(None, []))

    def test_a_selector_naming_a_local_directory_passes(self):
        self.assertIsNone(corpus.subject_refusal("FEAT-1-a", ["harness/FEAT-1-a", "kaya/F-2"]))

    def test_a_selector_naming_nothing_here_refuses(self):
        line = corpus.subject_refusal("FEAT-9-gone", ["harness/FEAT-1-a"])
        self.assertIn("names no feature directory", line)
        self.assertIn("harness/FEAT-1-a", line)

    def test_a_selector_in_an_empty_checkout_refuses(self):
        self.assertIn("none", corpus.subject_refusal("FEAT-1-a", []))


if __name__ == "__main__":
    unittest.main()
