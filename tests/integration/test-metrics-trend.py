#!/usr/bin/env python3
"""Hand-labelled integration contracts for append-only trend persistence."""
import ast
from contextlib import redirect_stderr
from datetime import datetime, timezone
import hashlib
import json
import io
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

    def test_separate_worktrees_preserve_three_records_through_two_merges(self):
        (self.directory / "baseline").write_text("base", encoding="utf-8")
        _baseline_commit(self.directory)
        baseline = record("FEAT-BASE", "2026-09-01T10:00:00Z")
        trend.append(self.directory, baseline)
        _commit_trend(self.directory, "base trend")
        first, second = _trend_worktrees(self.directory, self.directory.parent)
        try:
            _append_and_commit(first, record("FEAT-FIRST", "2026-09-02T10:00:00Z"))
            _append_and_commit(second, record("FEAT-SECOND", "2026-09-03T10:00:00Z"))
            _merge_trend_worktree(self.directory, first, second)
            result = trend.read(self.directory, "all", NOW)
        finally:
            _remove_worktree(self.directory, first)
            _remove_worktree(self.directory, second)
        self.assertEqual(["FEAT-BASE", "FEAT-FIRST", "FEAT-SECOND"], list(result["records"]))
        self.assertEqual(["FEAT-BASE", "FEAT-FIRST", "FEAT-SECOND"],
                         [json.loads(line)["feature_id"] for line in
                          (self.directory / ".harness/metrics/trend.jsonl").read_text().splitlines()])

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

    def test_weekly_sourcing_rule_covers_available_and_no_record_states(self):
        path = self.directory / ".harness/metrics/trend.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(record("FEATURE", "2026-09-14T00:00:00Z", pr=None)) + "\n", encoding="utf-8")
        expected = "Weekly counts are shipped features read from the durable ship record; each shipped feature represents one merged PR under DEC-200; nullable pr fields do not affect the count."
        self.assertEqual(trend.read(self.directory, "all", NOW)["weekly"]["sourcing_rule"], expected)
        self.assertEqual(trend._weekly({}, {}, None, NOW)["sourcing_rule"], expected)
        self.assertEqual(trend.read(self.directory / "missing", "all", NOW)["weekly"]["sourcing_rule"], expected)

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

    def test_kpi_reports_every_missing_trend_field_unavailable_not_zero(self):
        fixture = ROOT / ".claude/skills/harness/bin/dashboard/fixtures/project-a"
        root = self.directory / "project"
        shutil.copytree(fixture, root)
        with patch.object(kpi, "_aggregate", return_value={}):
            result = kpi.compute(root, "all", NOW)
        missing = next(item for item in result["features"] if item["feature_id"] == "FIX-NOSHIP")
        for field in ("cycle_time_days", "runs", "cycles_used", "max_total_cycles", "insertions",
                      "deletions", "files_changed", "touchpoints", "grade", "attribution"):
            self.assertIsNone(missing["trend"][field], field)
            self.assertNotEqual(0, missing["trend"][field], field)
            self.assertEqual("shipped before metrics existed", missing["trend"]["unavailable"][field])

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


    def test_record_ship_duplicate_refusal_and_commit_success_branch(self):
        with _fixture_copy() as project:
            _baseline_commit(project)
            path = project / ".harness/metrics/trend.jsonl"
            before_count = len(path.read_text(encoding="utf-8").splitlines())
            feature_dir = project / ".harness/demo/features/FIX-NOSHIP"
            with patch.object(trend.kpi, "_feature", return_value=_ship_feature()), patch.object(
                trend.grading, "distribution", return_value={"graded_functions": 1}
            ), patch.object(trend.attribution, "by_tier", return_value={"by_tier": {}, "unattributed": {}}), patch.object(
                trend.touchpoints, "count", return_value=(0, None)
            ):
                trend.record_ship(project, feature_dir)
                trend.record_ship(project, feature_dir)
            rows = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(before_count + 1, len(rows))
            self.assertEqual("FIX-NOSHIP", json.loads(rows[-1])["feature_id"])
            self.assertEqual(0, json.loads(rows[-1])["touchpoints"])
            self.assertEqual("", _git(project, "status", "--porcelain"))
            self.assertEqual(
                ".harness/metrics/trend.jsonl",
                _git(project, "ls-files", "--error-unmatch", ".harness/metrics/trend.jsonl"),
            )
            print("ok record_ship succeeding commit branch is clean and tracked")

    def test_record_ship_failure_branch_appends_without_a_git_repository(self):
        with _fixture_copy() as project:
            feature_dir = project / ".harness/demo/features/FIX-NOSHIP"
            path = project / ".harness/metrics/trend.jsonl"
            before_count = len(path.read_text(encoding="utf-8").splitlines())
            stderr = io.StringIO()
            with patch.object(trend.kpi, "_feature", return_value=_ship_feature()), patch.object(
                trend.grading, "distribution", return_value={"graded_functions": 1}
            ), patch.object(trend.attribution, "by_tier", return_value={"by_tier": {}, "unattributed": {}}), patch.object(
                trend.touchpoints, "count", return_value=(0, None)
            ), redirect_stderr(stderr):
                trend.record_ship(project, feature_dir)
            self.assertEqual(before_count + 1, len(path.read_text(encoding="utf-8").splitlines()))
            self.assertIn("trend: ERROR - ship record commit failed", stderr.getvalue())
            print("ok record_ship FAILURE-BRANCH appends despite commit failure")

    def test_cmd_ship_records_trend_before_board_writes_and_handles_failure(self):
        cmd_ship = _cmd_ship()
        record_lines, board_lines = _call_lines(cmd_ship)
        self.assertEqual(1, len(record_lines))
        self.assertTrue(board_lines)
        self.assertLess(record_lines[0], min(board_lines))
        self.assertTrue(_record_ship_try(cmd_ship).handlers)


def _cmd_ship():
    source = (BIN / "gh-sync.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    return next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "cmd_ship")


def _call_lines(function):
    calls = [
        (node.lineno, getattr(node.func, "attr", getattr(node.func, "id", "")))
        for node in ast.walk(function) if isinstance(node, ast.Call)
    ]
    return ([line for line, name in calls if name == "record_ship"],
            [line for line, name in calls if name == "board_stations_for"])


def _record_ship_try(function):
    return next(
        node for node in ast.walk(function)
        if isinstance(node, ast.Try) and any(
            getattr(call.func, "attr", "") == "record_ship" for call in ast.walk(node)
            if isinstance(call, ast.Call)
        )
    )

def _commit_trend(project: Path, message: str):
    _git(project, "add", ".harness/metrics/trend.jsonl")
    _git(project, "commit", "-qm", message)


def _trend_worktrees(project: Path, parent: Path):
    first, second = parent / "first", parent / "second"
    _git(project, "worktree", "add", "-q", "-b", "trend-first", str(first))
    _git(project, "worktree", "add", "-q", "-b", "trend-second", str(second))
    return first, second


def _append_and_commit(project: Path, value: dict):
    trend.append(project, value)
    _commit_trend(project, value["feature_id"])


def _merge_trend_worktree(project: Path, first: Path, second: Path):
    _git(project, "merge", "--no-ff", "-m", "merge first", "trend-first")
    conflict = subprocess.run(["git", "-C", str(project), "merge", "--no-ff", "-m", "merge second",
                               "trend-second"], capture_output=True, text=True)
    if conflict.returncode == 0:
        return
    second_line = (second / ".harness/metrics/trend.jsonl").read_text(encoding="utf-8").splitlines()[-1]
    merged = _git(project, "show", "HEAD:.harness/metrics/trend.jsonl")
    path = project / ".harness/metrics/trend.jsonl"
    path.write_text(merged + "\n" + second_line + "\n", encoding="utf-8")
    _git(project, "add", ".harness/metrics/trend.jsonl")
    _git(project, "commit", "-qm", "merge second")


def _remove_worktree(project: Path, worktree: Path):
    subprocess.run(["git", "-C", str(project), "worktree", "remove", "--force", str(worktree)],
                   check=False, capture_output=True)


def _ship_feature():
    return {
        "feature_id": "FIX-NOSHIP",
        "approved_on": "2026-09-01",
        "cycle_time_days": None,
        "runs": 1,
        "cycles_used": 2,
        "max_total_cycles": 5,
        "insertions": 3,
        "deletions": 1,
        "files_changed": 2,
        "touchpoints": 0,
        "unavailable": {"cycle_time_days": "no ship record for this feature"},
    }


def _baseline_commit(project: Path):
    for command in (
        ("init", "-q"),
        ("config", "user.name", "Trend Test"),
        ("config", "user.email", "trend@example.test"),
        ("add", "-A"),
        ("commit", "-q", "-m", "baseline"),
    ):
        subprocess.run(["git", "-C", str(project), *command], check=True, capture_output=True)


def _git(project: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(project), *args], check=True, capture_output=True, text=True
    ).stdout.strip()

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
