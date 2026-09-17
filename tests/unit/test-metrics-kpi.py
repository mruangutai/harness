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

import attribution  # noqa: E402
import defects  # noqa: E402
import grading  # noqa: E402
import kpi  # noqa: E402
import trend  # noqa: E402


class KpiCoreTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "project-a"
        shutil.copytree(FIXTURE, self.project)
        self.expected = json.loads((self.project / "expected.json").read_text())
        shutil.copy(ROOT / ".harness/harness.json", self.project / ".harness/harness.json")
        (self.project / "probe.py").write_text("def probe():\n    return 1\n", encoding="utf-8")
        _commit_scratch(self.project)
        self.attribution = patch("kpi.attribution.by_tier", return_value=_unimplemented_attribution())
        self.attribution.start()

    def tearDown(self):
        self.attribution.stop()
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
        self.assertEqual(
            self.expected["touchpoints"]["value"],
            _feature(result, self.expected["touchpoints"]["feature"])["touchpoints"],
        )
        self.assertEqual(
            {
                key: self.expected["touchpoints"][key]
                for key in ("mean", "zero_count", "not_tracked_count")
            },
            result["aggregate"]["touchpoints"],
        )
        self.assertIsNone(result["aggregate"]["attribution"]["value"])
        self.assertEqual("not yet implemented", result["aggregate"]["attribution"]["unavailable"]["value"])
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
        self.assertEqual(7, len(diffs))
        self.assertTrue(all(command[-1].startswith("trunk...") for command in diffs))


    def test_change_size_counts_binary_file_without_inventing_lines(self):
        def git_run(command, **_kwargs):
            if command[1:3] == ["symbolic-ref", "--short"]:
                return _git_result("origin/main\n")
            return _git_result("3\t2\talpha.py\n-\t-\timage.png\n")

        with patch("kpi.subprocess.run", side_effect=git_run), patch(
            "kpi.grading.distribution", return_value={}
        ):
            result = kpi.compute(self.project, "all", generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc))

        for feature in result["features"]:
            self.assertEqual(3, feature["insertions"])
            self.assertEqual(2, feature["deletions"])
            self.assertEqual(2, feature["files_changed"])

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


    def test_attribution_resolves_model_tiers_and_accounts_for_every_commit(self):
        self.attribution.stop()
        _attribution_plan(self.project, "FEAT-101", "T-01", "alpha-agent")
        _attribution_plan(self.project, "FEAT-202", "T-02", "beta-agent")
        _attribution_plan(self.project, "FEAT-404", "T-03", "missing-model-agent")
        agents = self.project / ".claude" / "agents"
        agents.mkdir(parents=True)
        (agents / "alpha-agent.md").write_text("---\nmodel: opus\n---\n", encoding="utf-8")
        (agents / "beta-agent.md").write_text("---\nmodel: haiku\n---\n", encoding="utf-8")
        (agents / "missing-model-agent.md").write_text("---\nname: missing\n---\n", encoding="utf-8")
        history = "\n".join((
            "a1\t2026-09-16T00:00:00+00:00\t[harness:t-01] alpha",
            "a2\t2026-09-16T00:00:00+00:00\t[harness:t-01] alpha again",
            "b1\t2026-09-16T00:00:00+00:00\t[harness:t-02] beta",
            "b2\t2026-09-16T00:00:00+00:00\t[harness:unknown,t-02] beta fallback",
            "x1\t2026-09-16T00:00:00+00:00\t[harness:t-99] absent",
            "m1\t2026-09-16T00:00:00+00:00\t[harness:t-03] missing model",
            "h1\t2026-09-16T00:00:00+00:00\t[harness:human] human",
            "f1\t2026-09-16T00:00:00+00:00\t[harness:FEAT-303] feature",
            "n1\t2026-09-16T00:00:00+00:00\tunprefixed",
        ))
        branches = {
            "a1": "feat/FEAT-101\n",
            "a2": "feat/FEAT-101\n",
            "b1": "feat/FEAT-202\n",
            "b2": "feat/FEAT-202\n",
            "x1": "feat/FEAT-101\n",
            "m1": "feat/FEAT-404\n",
        }

        def git_history(_root, arguments):
            if arguments[0] == "log":
                return history
            return branches.get(arguments[2], "")

        with patch("attribution._git", side_effect=git_history), patch(
            "attribution.artifact_accessors.load_plan",
            wraps=attribution.artifact_accessors.load_plan,
        ) as load_plan:
            result = attribution.by_tier(self.project, "all")

        self.assertEqual({"opus": 2, "haiku": 2}, result["by_tier"])
        self.assertEqual(
            {"no_prefix": 1, "human": 1, "feature_only": 1, "unresolvable_step_id": 2},
            result["unattributed"],
        )
        self.assertEqual(4 / 9, result["attributable_share"])
        self.assertEqual(9, result["total_commits"])
        self.assertEqual(3, load_plan.call_count)
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
            self.assertEqual(7, len(result["features"]))
            self.assertTrue(all("plan" in item["unavailable"] for item in result["features"]))

    def test_record_ship_copies_each_feature_measurement_and_marks_unavailable_values(self):
        feature = {
            "feature_id": "FIX-NOSHIP",
            "approved_on": "2026-09-01",
            "cycle_time_days": 15.5,
            "runs": 3,
            "cycles_used": 2,
            "max_total_cycles": 5,
            "insertions": 7,
            "deletions": 4,
            "files_changed": 2,
            "touchpoints": 0,
            "unavailable": {},
        }
        grade = {"graded_functions": 3}
        attribution_result = {"by_tier": {"backend": 2}, "unattributed": {}}
        with patch.object(trend.kpi, "_feature", return_value=feature), patch.object(
            trend.kpi, "_cycle_time", return_value=15.5
        ), patch.object(trend.grading, "distribution", return_value=grade), patch.object(
            trend.attribution, "by_tier", return_value=attribution_result
        ), patch.object(trend.touchpoints, "count", return_value=(0, None)), patch.object(
            trend, "append"
        ) as append, patch.object(trend, "_commit"):
            trend.record_ship(self.project, self.project / ".harness/demo/features/FIX-NOSHIP")
        record = append.call_args.args[1]
        self.assertEqual("trend/1", record["schema"])
        self.assertEqual("FIX-NOSHIP", record["feature_id"])
        self.assertEqual("2026-09-01", record["approved_on"])
        self.assertEqual(15.5, record["cycle_time_days"])
        self.assertEqual(3, record["runs"])
        self.assertEqual(2, record["cycles_used"])
        self.assertEqual(5, record["max_total_cycles"])
        self.assertEqual(7, record["insertions"])
        self.assertEqual(4, record["deletions"])
        self.assertEqual(2, record["files_changed"])
        self.assertEqual(0, record["touchpoints"])
        self.assertEqual(grade, record["grade"])
        self.assertEqual(attribution_result, record["attribution"])
        self.assertEqual({}, record["unavailable"])

    def test_record_ship_marks_missing_approval_and_cycle_time_unavailable(self):
        feature = {
            "feature_id": "FIX-NOAPPROVAL",
            "approved_on": None,
            "cycle_time_days": None,
            "runs": 0,
            "cycles_used": 0,
            "max_total_cycles": 1,
            "insertions": None,
            "deletions": None,
            "files_changed": None,
            "touchpoints": None,
            "unavailable": {
                "approved_on": "BRIEF.md has no Approval section",
                "cycle_time_days": "BRIEF.md has no Approval section",
                "insertions": "git default branch is unavailable",
                "deletions": "git default branch is unavailable",
                "files_changed": "git default branch is unavailable",
                "touchpoints": "touchpoints were not tracked in this project",
            },
        }
        with patch.object(trend.kpi, "_feature", return_value=feature), patch.object(
            trend.grading, "distribution", return_value={"graded_functions": 0}
        ), patch.object(trend.attribution, "by_tier", return_value={}), patch.object(
            trend.touchpoints, "count", return_value=(None, "touchpoints were not tracked in this project")
        ), patch.object(trend, "append") as append, patch.object(trend, "_commit"):
            trend.record_ship(self.project, self.project / ".harness/demo/features/FIX-NOAPPROVAL")
        record = append.call_args.args[1]
        self.assertIsNone(record["approved_on"])
        self.assertIsNone(record["cycle_time_days"])
        self.assertNotEqual(0, record["approved_on"])
        self.assertNotEqual(0, record["cycle_time_days"])
        self.assertEqual("BRIEF.md has no Approval section", record["unavailable"]["approved_on"])
        self.assertEqual("BRIEF.md has no Approval section", record["unavailable"]["cycle_time_days"])

_TRACKED_FILES = ["alpha.py", "broken.py", "script.sh", "README"]
def _attribution_plan(root, feature_id, task_id, agent):
    plan = root / ".harness" / "demo" / "features" / feature_id / "plan.yaml"
    plan.parent.mkdir(parents=True)
    plan.write_text(
        f"""tasks:
  - id: {task_id}
    title: attribution fixture
    change_type: logic
    execution_mode: team
    files: [fixture.py]
    verify: python3 fixture.py
    intent: fixture
    execution_agent: {agent}
""",
        encoding="utf-8",
    )


def _unimplemented_attribution():
    return {"value": None, "unavailable": {"value": "not yet implemented"}}




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
