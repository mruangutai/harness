#!/usr/bin/env python3
"""Hand-labelled integration contracts for append-only trend persistence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
sys.path.insert(0, str(BIN / "dashboard"))

import kpi  # noqa: E402
import touchpoints  # noqa: E402
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
    @classmethod
    def setUpClass(cls):
        cls.fixture_digest = _digest(_fixtures_root())

    @classmethod
    def tearDownClass(cls):
        if _digest(_fixtures_root()) != cls.fixture_digest:
            raise AssertionError("committed dashboard fixtures changed during the test run")

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

    def test_touchpoints_post_instrumentation_absent_file_is_zero(self):
        with patch.object(kpi, "_aggregate", return_value={}):
            result = kpi.compute(_touchpoint_fixture(), "all", NOW)
        feature = _feature(result, "FIX-NOSHIP")
        self.assertEqual(0, feature["touchpoints"])
        self.assertNotIn("touchpoints", feature["unavailable"])
        print("ok touchpoints post-instrumentation absent file is zero")

    def test_touchpoints_pre_instrumentation_is_unavailable_not_zero(self):
        with patch.object(kpi, "_aggregate", return_value={}):
            result = kpi.compute(_touchpoint_fixture(), "all", NOW)
        feature = _feature(result, "FIX-PRE")
        self.assertIsNone(feature["touchpoints"])
        self.assertNotEqual(0, feature["touchpoints"])
        self.assertNotEqual("0", feature["touchpoints"])
        self.assertEqual(
            "this feature predates touchpoint instrumentation in this project - "
            "touchpoints were never tracked for it",
            feature["unavailable"]["touchpoints"],
        )
        print("ok touchpoints pre-instrumentation is unavailable not zero")

    def test_two_touchpoint_run_is_counted_and_shipped(self):
        with _fixture_copy() as project:
            touchpoints.record(project, "FIX-NOSHIP", "approval_request")
            touchpoints.record(project, "FIX-NOSHIP", "uat_request")
            self.assertEqual((2, None), touchpoints.count(project, "FIX-NOSHIP"))
            trend.append(project, record("FIX-NOSHIP", "2026-09-15T12:00:00Z", touchpoints=2))
            self.assertEqual(2, trend.read(project, "all", NOW)["records"]["FIX-NOSHIP"]["touchpoints"])

    def test_touchpoint_epoch_is_written_once_and_invalid_event_writes_nothing(self):
        with _fixture_copy() as project:
            epoch = project / ".harness/metrics/instrumented_at"
            epoch.unlink()
            touchpoints.record(project, "FIX-NOSHIP", "escalation")
            first = epoch.read_bytes()
            touchpoints.record(project, "FIX-NOSHIP", "uat_request")
            self.assertEqual(first, epoch.read_bytes())
            before = _digest(project)
            result = subprocess.run(
                [sys.executable, str(BIN / "touchpoints.py"), "record", "--root", str(project),
                 "--feature", "FIX-NOSHIP", "--event", "unknown"],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertTrue(all(event in result.stderr for event in ("approval_request", "escalation", "uat_request")))
            self.assertEqual(before, _digest(project))

    def test_touchpoint_unavailable_branches_and_same_day_boundary(self):
        uninstrumented = _fixtures_root() / "project-uninstrumented"
        for feature_dir in uninstrumented.glob(".harness/*/features/*"):
            feature_id = feature_dir.name
            self.assertEqual(
                (None, "touchpoints were not tracked in this project - no .harness/metrics/"
                 "instrumented_at epoch exists, so no count here is a measurement"),
                touchpoints.count(uninstrumented, feature_id),
            )
        fixture = _touchpoint_fixture()
        with patch("touchpoints._first_feature_commit", return_value=None):
            self.assertEqual(
                (None, "touchpoints cannot be dated for this feature - it has neither an approval "
                 "date in its BRIEF.md nor a commit that added its directory, so pre-instrumentation "
                 "and post-instrumentation cannot be told apart"),
                touchpoints.count(fixture, "FIX-NOBRIEF"),
            )
        self.assertEqual((0, None), touchpoints.count(fixture, "FIX-NOSHIP"))

    def test_touchpoint_transition_window_has_incomplete_reason(self):
        feature = _touchpoint_fixture() / ".harness/demo/features/FIX-SHIPPED"
        log = feature / "touchpoints.jsonl"
        self.assertEqual(2, len(log.read_text(encoding="utf-8").splitlines()))
        value, reason = touchpoints.count(_touchpoint_fixture(), "FIX-SHIPPED")
        self.assertIsNone(value)
        self.assertIn("2 touchpoints", reason)
        self.assertNotIn("never tracked", reason)


def _fixtures_root() -> Path:
    return ROOT / ".claude/skills/harness/bin/dashboard/fixtures"

def _touchpoint_fixture() -> Path:
    return ROOT / ".claude/skills/harness/bin/dashboard/fixtures/project-a"


def _fixture_copy():
    directory = tempfile.TemporaryDirectory()
    project = Path(directory.name) / "project-a"
    shutil.copytree(_touchpoint_fixture(), project)
    return _temporary_project(directory, project)


class _temporary_project:
    def __init__(self, directory, project):
        self.directory = directory
        self.project = project

    def __enter__(self):
        return self.project

    def __exit__(self, *_args):
        self.directory.cleanup()


def _digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest.update(str(path.relative_to(root)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _feature(payload: dict, feature_id: str) -> dict:
    return next(item for item in payload["features"] if item["feature_id"] == feature_id)


if __name__ == "__main__":
    unittest.main()
