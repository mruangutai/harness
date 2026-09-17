#!/usr/bin/env python3
"""Hand-labelled contract tests for the KPI core."""
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
FIXTURE = BIN / "dashboard" / "fixtures" / "project-a"
sys.path.insert(0, str(BIN))
sys.path.insert(0, str(BIN / "dashboard"))

import defects  # noqa: E402
import grading  # noqa: E402
import kpi  # noqa: E402


class KpiCoreTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "project-a"
        shutil.copytree(FIXTURE, self.project)
        self.expected = json.loads((self.project / "expected.json").read_text())
        shutil.copy(ROOT / ".harness/harness.json", self.project / ".harness/harness.json")
        (self.project / "probe.py").write_text("def probe():\n    return 1\n", encoding="utf-8")
        _commit_scratch(self.project)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_hand_labelled_feature_and_aggregate_values(self):
        generated_at = datetime(2026, 9, 16, tzinfo=timezone.utc)
        with patch("kpi.subprocess.run", side_effect=_diff_result) as diff, patch(
            "kpi.grading.distribution", return_value=_grading_expected(self.expected["grading"])
        ):
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
        for key in ("touchpoints", "attribution"):
            self.assertIsNone(result["aggregate"][key]["value"])
            self.assertEqual("not yet implemented", result["aggregate"][key]["unavailable"]["value"])
        self.assertEqual(0, result["aggregate"]["escaped_defects"]["count"])
        self.assertEqual("all", result["aggregate"]["escaped_defects"]["window"])
        self.assertEqual(
            "BUG-NN feature units first added in the selected window and Revert commits are counted; "
            "subjects beginning with fix are excluded because they are usually within-feature repairs.",
            result["aggregate"]["escaped_defects"]["sourcing_rule"],
        )

    def test_grading_distribution_uses_grader_payload_and_live_file_mix(self):
        payload = self.expected["grading_payload"]
        with patch("grading.subprocess.run", side_effect=_grading_result(payload, _TRACKED_FILES)) as run:
            result = grading.distribution(self.project)
        grader_call = run.call_args_list[1]
        self.assertEqual(
            ["python3", str(BIN / "code-grade.py"), "--json",
             str(self.project.resolve() / "alpha.py"), str(self.project.resolve() / "broken.py")],
            grader_call.args[0],
        )
        self.assertEqual(self.project.resolve(), grader_call.kwargs["cwd"])
        self.assertEqual(_grading_expected(self.expected["grading"]), result)
        with patch("grading.subprocess.run", side_effect=_grading_result(payload, _TRACKED_FILES + ["new.ts"])):
            changed = grading.distribution(self.project)
        self.assertNotEqual(result["file_mix"]["ungraded_share"], changed["file_mix"]["ungraded_share"])

    def test_kpi_uses_grading_distribution(self):
        grading_result = _grading_expected(self.expected["grading"])
        with patch("kpi.grading.distribution", return_value=grading_result):
            result = kpi.compute(self.project, "all", generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc))
        self.assertEqual(grading_result, result["aggregate"]["grading"])

    def test_grading_payload_has_no_central_tendency(self):
        result = self.expected["grading"]
        self.assertFalse(_has_central_tendency(result))
        with self.assertRaises(AssertionError):
            self.assertFalse(_has_central_tendency({"median": 2}))

    def test_committed_dashboard_source_sweep_rejects_mix_literal(self):
        paths = _dashboard_paths(ROOT)
        self.assertTrue(paths)
        _assert_no_mix_literals(ROOT, paths)
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            seeded_path = scratch / ".claude/skills/harness/bin/dashboard/seed.py"
            seeded_path.parent.mkdir(parents=True)
            seeded_path.write_text("mix = 107\n", encoding="utf-8")
            _commit_scratch(scratch)
            with self.assertRaisesRegex(AssertionError, "107"):
                _assert_no_mix_literals(scratch, _dashboard_paths(scratch))

    def test_change_size_uses_project_default_branch_once(self):
        calls = []

        def git_run(command, **kwargs):
            calls.append((command, kwargs))
            if command[1:3] == ["symbolic-ref", "--short"]:
                return _git_result("origin/trunk\n")
            return _diff_result(command)

        with patch("kpi.subprocess.run", side_effect=git_run), patch(
            "kpi.grading.distribution", return_value={}
        ):
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

        with patch("kpi.subprocess.run", side_effect=git_run) as git, patch(
            "kpi.grading.distribution", return_value={}
        ):
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


    def test_escaped_defects_count_bug_units_and_reverts_not_fixes(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "seed.txt").write_text("seed\n", encoding="utf-8")
            _commit_scratch(project)
            _commit_history(project, "add BUG-101", {
                ".harness/demo/features/BUG-101/feature.json": "{}\n",
            })
            _commit_history(project, "fix BUG-101 repair", {"repair-1.txt": "one\n"})
            _commit_history(project, "add BUG-202", {
                ".harness/demo/features/BUG-202/feature.json": "{}\n",
            })
            _commit_history(project, "fix BUG-202 repair", {"repair-2.txt": "two\n"})
            revert_id = _commit_history(project, "Revert \"release regression\"", {
                "revert.txt": "reverted\n",
            })

            result = defects.escaped(project, "all")

        self.assertEqual(3, result["count"])
        self.assertEqual("all", result["window"])
        self.assertEqual(
            ["BUG-101", "BUG-202", revert_id],
            [item["id"] for item in result["items"]],
        )
        self.assertEqual(
            ["bug_unit", "bug_unit", "revert"],
            [item["kind"] for item in result["items"]],
        )
        self.assertTrue(all(not item["subject"].startswith("fix") for item in result["items"]))
        self.assertEqual(
            "BUG-NN feature units first added in the selected window and Revert commits are counted; "
            "subjects beginning with fix are excluded because they are usually within-feature repairs.",
            result["sourcing_rule"],
        )

    def test_escaped_defects_report_unavailable_when_git_history_cannot_be_read(self):
        with tempfile.TemporaryDirectory() as directory:
            result = defects.escaped(Path(directory), "all")

        self.assertIsNone(result["count"])
        self.assertEqual([], result["items"])
        self.assertIn("git history cannot be read", result["unavailable"]["count"])

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

_TRACKED_FILES = ["alpha.py", "broken.py", "script.sh", "README"]


def _grading_expected(value):
    expected = dict(value)
    expected["bins"] = {int(grade): count for grade, count in value["bins"].items()}
    return expected


def _grading_result(payload, paths):
    def run(command, **kwargs):
        if command[:2] == ["git", "-C"]:
            return _git_result("\n".join(paths) + "\n")
        return _git_result(json.dumps(payload), returncode=1)
    return run


def _dashboard_paths(root):
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", ".claude/skills/harness/bin/dashboard/"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.splitlines()


def _assert_no_mix_literals(root, paths):
    for path in paths:
        result = subprocess.run(
            ["git", "-C", str(root), "show", f"HEAD:{path}"],
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, path
        assert b"107" not in result.stdout, f"107 in {path}"
        assert b"122" not in result.stdout, f"122 in {path}"

def _commit_scratch(root):
    for command in (
        ["git", "init"],
        ["git", "add", "."],
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-m", "seed"],
    ):
        subprocess.run(command, cwd=root, check=True, capture_output=True)

def _commit_history(root, subject, files):
    for relative, contents in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-m", subject],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _has_central_tendency(value):
    if isinstance(value, dict):
        return any(key in {"mean", "median"} or _has_central_tendency(item)
                   for key, item in value.items())
    if isinstance(value, list):
        return any(_has_central_tendency(item) for item in value)
    return False

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
