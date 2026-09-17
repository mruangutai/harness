#!/usr/bin/env python3
"""Hand-labelled integration contracts for append-only trend persistence."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
import tempfile
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
sys.path.insert(0, str(BIN / "dashboard"))

import kpi  # noqa: E402
import trend  # noqa: E402

NOW = datetime(2026, 9, 15, 12, tzinfo=timezone.utc)


def record(feature_id, shipped_at, **changes):
    value = {
        "schema": "trend/1", "feature_id": feature_id, "shipped_at": shipped_at,
        "approved_on": "2026-09-01", "cycle_time_days": 2.0, "runs": 1,
        "cycles_used": 2, "max_total_cycles": 5, "insertions": 3, "deletions": 1,
        "files_changed": 2, "touchpoints": 0,
        "grade": {"graded_functions": 1, "at_or_above_bar": 1, "bins": {"4": 1}, "grade_1": [], "grade_2": [], "ungraded_files": 0, "tracked_files": 1},
        "attribution": {"by_tier": {"backend": 1}, "unattributed": {}}, "unavailable": {},
    }
    value.update(changes)
    return value


class TrendTest(unittest.TestCase):
    def setUp(self):
        self.directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.directory)

    def test_append_preserves_prior_bytes_and_rejects_duplicate(self):
        first = record("FEAT-ONE", "2026-09-01T10:00:00Z")
        second = record("FEAT-TWO", "2026-09-08T10:00:00Z")
        trend.append(self.directory, first)
        path = self.directory / ".harness/metrics/trend.jsonl"
        before = path.read_bytes()
        trend.append(self.directory, second)
        self.assertEqual(path.read_bytes()[:len(before)], before)
        self.assertEqual(path.read_bytes().count(b"\n"), 2)
        with self.assertRaisesRegex(ValueError, "FEAT-ONE"):
            trend.append(self.directory, first)

    def test_reader_rejects_schema_and_resolves_merged_duplicates(self):
        path = self.directory / ".harness/metrics/trend.jsonl"
        path.parent.mkdir(parents=True)
        rows = [
            record("FEAT-DUP", "2026-09-01T10:00:00Z"),
            record("FEAT-DUP", "2026-09-02T10:00:00Z"),
            record("FEAT-FUTURE", "2026-09-03T10:00:00Z", schema="trend/2"),
        ]
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        result = trend.read(self.directory, "all", NOW)
        self.assertEqual(result["records"]["FEAT-DUP"]["shipped_at"], "2026-09-02T10:00:00Z")
        self.assertIn("2026-09-01T10:00:00Z", result["unavailable"]["FEAT-DUP"])
        self.assertIn("2026-09-02T10:00:00Z", result["unavailable"]["FEAT-DUP"])
        self.assertIn("trend/2", result["unavailable"]["line_3"])

    def test_weekly_series_is_windowed_segmented_and_counts_null_pr(self):
        path = self.directory / ".harness/metrics/trend.jsonl"
        path.parent.mkdir(parents=True)
        rows = [
            record("OUTSIDE", "2026-08-15T12:00:00Z"),
            record("EARLY", "2026-08-16T11:00:00Z"),
            record("FIRST", "2026-08-17T12:00:00Z", pr=None),
            record("LAST", "2026-09-14T00:00:00Z"),
        ]
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        result = trend.read(self.directory, "30d", NOW)
        weekly = result["weekly"]
        self.assertEqual([point["week"] for point in weekly["points"]], ["2026-08-10", "2026-08-17", "2026-08-24", "2026-08-31", "2026-09-07", "2026-09-14"])
        self.assertEqual([point["value"] for point in weekly["points"]], [None, 1, None, None, None, 1])
        self.assertEqual(weekly["week_count"], 6)
        self.assertEqual(weekly["empty_bucket_count"], 4)
        self.assertEqual(sum(point["value"] or 0 for point in weekly["points"]), 2)
        self.assertTrue(weekly["points"][0]["partial"])
        self.assertIn("between 2026-08-16T12:00:00Z and 2026-08-17T00:00:00Z", weekly["points"][0]["reason"])
        self.assertIn("2026-08-24", weekly["points"][2]["reason"])
        self.assertEqual([[point["week"] for point in run] for run in weekly["segments"]], [["2026-08-17"], ["2026-09-14"]])

    def test_all_anchor_and_monday_boundary(self):
        path = self.directory / ".harness/metrics/trend.jsonl"
        path.parent.mkdir(parents=True)
        rows = [
            record("OLD", "2026-08-02T23:59:00Z"),
            record("BEFORE", "2026-09-06T23:59:00Z"),
            record("AFTER", "2026-09-07T00:00:00Z"),
        ]
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        weekly = trend.read(self.directory, "all", NOW)["weekly"]
        self.assertEqual(weekly["points"][0]["week"], "2026-07-27")
        self.assertEqual(weekly["points"][-1]["week"], "2026-09-14")
        values = {point["week"]: point["value"] for point in weekly["points"]}
        self.assertEqual(values["2026-08-31"], 1)
        self.assertEqual(values["2026-09-07"], 1)

    def test_kpi_reports_missing_trend_as_unavailable_not_zero(self):
        fixture = ROOT / ".claude/skills/harness/bin/dashboard/fixtures/project-a"
        root = self.directory / "project"
        shutil.copytree(fixture, root)
        with patch.object(kpi, "_aggregate", return_value={}):
            result = kpi.compute(root, "all", NOW)
        missing = next(item for item in result["features"] if item["feature_id"] == "FIX-NOSHIP")
        self.assertIsNone(missing["trend"]["cycle_time_days"])
        self.assertEqual(missing["trend"]["unavailable"]["cycle_time_days"], "shipped before metrics existed")


if __name__ == "__main__":
    unittest.main()
