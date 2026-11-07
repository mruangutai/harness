#!/usr/bin/env python3
"""The feature.json line budget counts the journal, not the run ledger (B-4).

The cap is DEC-150's "data a script parses, not a journal". `runs:` IS that data and its
length tracks how long a feature ran, so counting it fired the cap on the one part of the
file nobody should be asked to shorten. These cases pin both halves: the ledger is free,
and everything else is still capped exactly as before.
"""
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude/skills/harness/bin"))
import feature_schema


def record(runs, extra=None):
    doc = {"feature_id": "FEAT-90", "branch": "feat/FEAT-90", "pr": None,
           "review_sha": "none", "cycles_used": 0, "max_total_cycles": 10,
           "runs": [{"id": f"r{index}", "squad": "eng", "verdict": "PASS",
                     "agent": "harness-eng-lead"} for index in range(runs)]}
    doc.update(extra or {})
    return json.dumps(doc, indent=2)


class JournalLinesTest(unittest.TestCase):
    def test_ledger_length_does_not_move_the_count(self):
        """Two records differing only in run count must count identically."""
        self.assertEqual(feature_schema.journal_lines(record(0)),
                         feature_schema.journal_lines(record(200)))

    def test_long_ledger_stays_under_budget(self):
        text = record(200)
        self.assertGreater(len(text.splitlines()),
                           feature_schema.FEATURE_JSON_LINE_BUDGET)
        self.assertLess(feature_schema.journal_lines(text),
                        feature_schema.FEATURE_JSON_LINE_BUDGET)

    def test_narrative_outside_the_ledger_still_trips(self):
        """The cap keeps its teeth: prose keys are counted and still blow the budget."""
        prose = {f"_rationale_{index}": "why this happened, at length"
                 for index in range(feature_schema.FEATURE_JSON_LINE_BUDGET + 1)}
        self.assertGreater(feature_schema.journal_lines(record(3, prose)),
                           feature_schema.FEATURE_JSON_LINE_BUDGET)

    def test_long_heterogeneous_ledger_before_a_nested_block(self):
        """The shape that motivated this (FEAT-54): a 300+ line record, nearly all ledger, whose
        run entries vary in keys and which is followed by a nested `github` block that still
        counts. Synthetic, so the case never depends on a prior feature's folder (FEAT-71)."""
        tasks = [f"T-{index:02d}" for index in range(1, 13)]
        runs = []
        for index in range(50):
            run = {"id": f"2026-01-01-{index}-fixture", "agent": "harness-product-lead"}
            if index % 7:
                run.update(squad="product", verdict="PASS" if index % 3 else "FAIL")
            if index % 5 == 0:
                run["code_grade"] = "n_a"
            runs.append(run)
        doc = {"feature_id": "FEAT-90-fixture", "branch": "feat/FEAT-90-fixture", "pr": 9,
               "review_sha": "none", "cycles_used": 22, "max_total_cycles": 30, "runs": runs,
               "github": {"milestone": 9, "parent": 90, "attached": tasks,
                          "issues": {task: 900 + n for n, task in enumerate(tasks)},
                          "source_issues": []}}
        text = json.dumps(doc, indent=2)
        self.assertGreater(len(text.splitlines()), 300)
        self.assertLess(feature_schema.journal_lines(text), 100)
        self.assertGreater(feature_schema.journal_lines(text), 2 * len(tasks))

    def test_a_runs_lookalike_inside_a_string_is_not_the_key(self):
        """A value that spells the key must not be mistaken for it."""
        text = json.dumps({"note": '"runs": [ not the key', "runs": [1, 2, 3]}, indent=2)
        self.assertEqual(4, feature_schema.journal_lines(text))

    def test_no_runs_key_counts_whole(self):
        text = json.dumps({"feature_id": "FEAT-90", "cycles_used": 1}, indent=2)
        self.assertEqual(len(text.splitlines()), feature_schema.journal_lines(text))

    def test_unclosed_ledger_counts_whole(self):
        """A truncated file must never be LOOSENED by a parse that failed."""
        text = '{\n"runs": [\n{"id": "r0"}\n'
        self.assertEqual(len(text.splitlines()), feature_schema.journal_lines(text))

    def test_compact_record_counts_one_line(self):
        self.assertEqual(1, feature_schema.journal_lines(json.dumps(json.loads(record(9)))))


if __name__ == "__main__":
    unittest.main()
