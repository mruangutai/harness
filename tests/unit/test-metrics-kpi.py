#!/usr/bin/env python3
"""Hand-labelled contract tests for the KPI core."""
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
FIXTURE = BIN / "dashboard" / "fixtures" / "project-a"
sys.path.insert(0, str(BIN))
sys.path.insert(0, str(BIN / "dashboard"))

import kpi  # noqa: E402


class KpiCoreTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "project-a"
        shutil.copytree(FIXTURE, self.project)
        self.expected = json.loads((self.project / "expected.json").read_text())

    def tearDown(self):
        self.tempdir.cleanup()

    def test_hand_labelled_feature_and_aggregate_values(self):
        generated_at = datetime(2026, 9, 16, tzinfo=timezone.utc)
        with patch("kpi.subprocess.run", side_effect=_diff_result) as diff:
            result = kpi.compute(self.project, "all", generated_at=generated_at)
        self.assertEqual(self.expected["schema"], result["schema"])
        self.assertEqual(str(self.project.resolve()), result["project"]["root"])
        self.assertEqual("project-a", result["project"]["name"])
        self.assertEqual("2026-09-16T00:00:00Z", result["generated_at"])
        self.assertEqual(self.expected["feature_ids"], [item["feature_id"] for item in result["features"]])
        shipped = _feature(result, "FIX-SHIPPED")
        self.assertEqual(self.expected["shipped"], _selected(shipped))
        self.assertEqual(self.expected["throughput"], result["aggregate"]["throughput"])
        self.assertEqual(self.expected["rework"], result["aggregate"]["rework"])
        self.assertEqual(
            {"git diff --numstat main...feature/shipped"},
            {" ".join(call.args[0]) for call in diff.call_args_list
             if call.args[0][-1] == "main...feature/shipped"},
        )
        self.assertEqual(7, diff.call_count)
        for key in ("touchpoints", "escaped_defects", "grading", "attribution"):
            self.assertIsNone(result["aggregate"][key]["value"])
            self.assertEqual("not yet implemented", result["aggregate"][key]["unavailable"]["value"])

    def test_change_size_uses_project_default_branch_once(self):
        calls = []

        def git_run(command, **kwargs):
            calls.append((command, kwargs))
            if command[1:3] == ["symbolic-ref", "--short"]:
                return _git_result("origin/trunk\n")
            return _diff_result(command)

        with patch("kpi.subprocess.run", side_effect=git_run):
            kpi.compute(self.project, "all", generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc))

        diffs = [command for command, _kwargs in calls if command[1:3] == ["diff", "--numstat"]]
        self.assertEqual(
            [(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], {"cwd": self.project.resolve(),
              "capture_output": True, "text": True, "check": False})],
            [(command, kwargs) for command, kwargs in calls if command[1] == "symbolic-ref"],
        )
        self.assertEqual(6, len(diffs))
        self.assertTrue(all(command[-1].startswith("trunk...") for command in diffs))


    def test_missing_project_default_branch_does_not_use_feature_diffs(self):
        def git_run(command, **_kwargs):
            return _git_result("", returncode=1)

        with patch("kpi.subprocess.run", side_effect=git_run) as git:
            result = kpi.compute(self.project, "all", generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc))

        self.assertEqual(1, git.call_count)
        self.assertTrue(all(
            item["unavailable"]["insertions"] == "project default branch is unavailable"
            for item in result["features"]
        ))
    def test_four_gap_features_have_distinct_specific_reasons(self):
        result = kpi.compute(self.project, "all", generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc))
        reasons = []
        for feature_id, expected in self.expected["gaps"].items():
            feature = _feature(result, feature_id)
            self.assertIsNone(feature["approved_on"], feature_id)
            self.assertIsNone(feature["cycle_time_days"], feature_id)
            self.assertEqual(expected, feature["unavailable"]["approved_on"], feature_id)
            self.assertEqual(expected, feature["unavailable"]["cycle_time_days"], feature_id)
            reasons.append(expected)
        self.assertEqual(4, len(set(reasons)))
    def test_missing_ship_record_is_null_with_its_own_reason(self):
        result = kpi.compute(self.project, "all", generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc))
        feature = _feature(result, "FIX-NOSHIP")
        self.assertIsNone(feature["shipped_at"])
        self.assertIsNone(feature["cycle_time_days"])
        self.assertEqual("no ship record for this feature", feature["unavailable"]["shipped_at"])
        self.assertEqual("no ship record for this feature", feature["unavailable"]["cycle_time_days"])

    def test_window_boundaries_are_generated_at_relative(self):
        generated_at = datetime(2026, 9, 16, tzinfo=timezone.utc)
        self.assertEqual((datetime(2026, 8, 17, tzinfo=timezone.utc), generated_at), kpi.resolve_window("30d", generated_at))
        self.assertEqual((datetime(2026, 6, 18, tzinfo=timezone.utc), generated_at), kpi.resolve_window("90d", generated_at))
        self.assertEqual((None, generated_at), kpi.resolve_window("all", generated_at))
        self.assertEqual(["FIX-SHIPPED"], [f["feature_id"] for f in kpi.compute(self.project, "30d", generated_at=generated_at)["features"]])


    def test_plan_parse_failures_are_unavailable_not_crashes(self):
        import harness_yaml
        failures = (
            harness_yaml.YamlParseError("plan.yaml", "broken syntax"),
            harness_yaml.PlanSchemaError("plan.yaml", "wrong shape"),
        )
        for failure in failures:
            with self.subTest(error=type(failure).__name__), patch(
                "kpi.artifact_accessors.load_plan", side_effect=failure
            ):
                result = kpi.compute(
                    self.project, "all",
                    generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc),
                )
            self.assertEqual(6, len(result["features"]))
            self.assertTrue(all("plan" in item["unavailable"] for item in result["features"]))

def _diff_result(command, **_kwargs):
    if command[1:3] == ["symbolic-ref", "--short"]:
        return _git_result("origin/main\n")
    return _git_result("3\t2\talpha.py\n1\t0\tbeta.py\n")

def _git_result(stdout, returncode=0):
    class Result:
        pass
    result = Result()
    result.returncode = returncode
    result.stdout = stdout
    return result


def _feature(result, feature_id):
    return next(feature for feature in result["features"] if feature["feature_id"] == feature_id)


def _selected(feature):
    return {key: feature[key] for key in (
        "feature_id", "approved_on", "shipped_at", "cycle_time_days", "runs",
        "cycles_used", "max_total_cycles", "insertions", "deletions", "files_changed",
    )}


if __name__ == "__main__":
    unittest.main()
