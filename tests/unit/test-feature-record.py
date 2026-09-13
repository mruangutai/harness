#!/usr/bin/env python3
"""feature-record.py and the FEAT-59 feature.json ledger keys (SC-15, SC-18, SC-19, SC-21).

Every verb is exercised through the CLI as a subprocess, the way the orchestrator and the
main session call it, and every written document is re-validated with feature_schema so a
verb that writes a shape the schema rejects cannot pass here. The refusal cases assert the
file is byte-identical afterwards: a refused write that still moved bytes is the incident
feature_json_write exists to close.
"""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(BIN))
import feature_schema  # noqa: E402
import feature_json_write  # noqa: E402

CLI = BIN / "feature-record.py"
# datetime.now(timezone.utc).isoformat(timespec="seconds") — the one shape this tool writes.
ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$")


def base_doc(**overrides):
    doc = {"feature_id": "FEAT-77-record", "branch": "none", "pr": None,
           "review_sha": "none", "cycles_used": 0, "max_total_cycles": 5, "runs": []}
    doc.update(overrides)
    return doc


class FeatureRecordCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="feature-record-test-"))
        feat_dir = self.tmp / ".harness" / "features" / "FEAT-77-record"
        feat_dir.mkdir(parents=True)
        self.path = feat_dir / "feature.json"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, doc):
        self.path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        return self.path.read_bytes()

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def assert_ok(self, result):
        self.assertEqual(0, result.returncode, f"stdout={result.stdout!r} stderr={result.stderr!r}")

    def assert_clean(self):
        problems = feature_schema.problems_for_text(
            self.path.read_text(encoding="utf-8"), str(self.path))
        self.assertEqual([], problems)


class RunStartEndTest(FeatureRecordCase):
    def test_run_start_appends_a_pending_entry_stamped_started_at(self):
        self.write(base_doc())
        self.assert_ok(self.run_cli("run-start", "--file", str(self.path), "--id", "r1",
                                    "--squad", "product", "--agent", "harness-product-lead"))
        runs = self.load()["runs"]
        self.assertEqual(1, len(runs))
        entry = runs[0]
        self.assertEqual({"id": "r1", "squad": "product", "agent": "harness-product-lead",
                          "verdict": "PENDING"},
                         {k: entry[k] for k in ("id", "squad", "agent", "verdict")})
        self.assertRegex(entry["started_at"], ISO_UTC)
        self.assertNotIn("ended_at", entry)
        self.assertNotIn("tokens", entry)
        self.assert_clean()

    def test_run_start_refuses_a_duplicate_id_and_leaves_bytes_untouched(self):
        before = self.write(base_doc(runs=[{"id": "r1", "squad": "product", "verdict": "PASS",
                                            "agent": "harness-product-lead"}]))
        result = self.run_cli("run-start", "--file", str(self.path), "--id", "r1",
                              "--squad", "product", "--agent", "harness-product-lead")
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("r1", result.stderr)
        self.assertEqual(before, self.path.read_bytes())

    def test_run_end_stamps_verdict_ended_at_tokens_and_code_grade(self):
        self.write(base_doc(runs=[{"id": "r1", "squad": "product", "verdict": "PENDING",
                                   "agent": "harness-product-lead",
                                   "started_at": "2026-09-11T10:00:00+00:00"}]))
        self.assert_ok(self.run_cli("run-end", "--file", str(self.path), "--id", "r1",
                                    "--verdict", "PASS", "--tokens", "48213",
                                    "--code-grade", "n_a"))
        entry = self.load()["runs"][0]
        self.assertEqual("PASS", entry["verdict"])
        self.assertEqual(48213, entry["tokens"])
        self.assertEqual("n_a", entry["code_grade"])
        self.assertEqual("2026-09-11T10:00:00+00:00", entry["started_at"])
        self.assertRegex(entry["ended_at"], ISO_UTC)
        self.assert_clean()

    def test_run_end_without_tokens_records_null_never_a_guess(self):
        """SC-18: tokens is measured by the caller or null. A run-end that carries no
        figure must write null, so a reader can tell "unmeasured" from "zero"."""
        self.write(base_doc(runs=[{"id": "r1", "squad": "eng", "verdict": "PENDING",
                                   "agent": "harness-eng-lead",
                                   "started_at": "2026-09-11T10:00:00+00:00"}]))
        self.assert_ok(self.run_cli("run-end", "--file", str(self.path), "--id", "r1",
                                    "--verdict", "FAIL"))
        entry = self.load()["runs"][0]
        self.assertIn("tokens", entry)
        self.assertIsNone(entry["tokens"])
        self.assertNotIn("code_grade", entry)
        self.assert_clean()

    def test_run_end_refuses_an_unknown_id(self):
        before = self.write(base_doc(runs=[{"id": "r1", "squad": "eng", "verdict": "PENDING",
                                            "agent": "harness-eng-lead"}]))
        result = self.run_cli("run-end", "--file", str(self.path), "--id", "r9",
                              "--verdict", "PASS")
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("r9", result.stderr)
        self.assertEqual(before, self.path.read_bytes())

    def test_missing_file_is_refused_not_created(self):
        result = self.run_cli("run-start", "--file", str(self.path), "--id", "r1",
                              "--squad", "eng", "--agent", "harness-eng-lead")
        self.assertEqual(feature_json_write.SCHEMA_REFUSAL_CODE, result.returncode, result.stderr)
        self.assertFalse(self.path.exists())


class JudgementTest(FeatureRecordCase):
    def test_judgement_appends_in_order_with_all_five_keys(self):
        self.write(base_doc())
        self.assert_ok(self.run_cli("judgement", "--file", str(self.path),
                                    "--by", "harness-orchestrator", "--kind", "mission",
                                    "--decision", "patch",
                                    "--reason", "known-cause bug, ~130 lines"))
        self.assert_ok(self.run_cli("judgement", "--file", str(self.path),
                                    "--by", "harness-validator-lead", "--kind", "finding_kind",
                                    "--decision", "form", "--reason", "wording only"))
        ledger = self.load()["judgements"]
        self.assertEqual(["mission", "finding_kind"], [j["kind"] for j in ledger])
        first = ledger[0]
        self.assertEqual({"at", "by", "kind", "decision", "reason"}, set(first))
        self.assertRegex(first["at"], ISO_UTC)
        self.assertEqual("harness-orchestrator", first["by"])
        self.assertEqual("patch", first["decision"])
        self.assert_clean()

    def test_judgement_refuses_an_unknown_kind(self):
        before = self.write(base_doc())
        result = self.run_cli("judgement", "--file", str(self.path), "--by", "x",
                              "--kind", "vibe", "--decision", "d", "--reason", "r")
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("vibe", result.stderr)
        self.assertEqual(before, self.path.read_bytes())

    def test_judgement_refuses_a_reason_over_240_characters(self):
        """The ledger holds one-line reasons (SC-21); the cap is the schema's, and the
        refusal must propagate the schema code rather than be swallowed."""
        before = self.write(base_doc())
        result = self.run_cli("judgement", "--file", str(self.path), "--by", "x",
                              "--kind", "regate", "--decision", "d", "--reason", "r" * 241)
        self.assertEqual(feature_json_write.SCHEMA_REFUSAL_CODE, result.returncode, result.stderr)
        self.assertIn("reason", result.stderr)
        self.assertEqual(before, self.path.read_bytes())


class RulingsTest(FeatureRecordCase):
    """set-rework and raise-cycles are the OPERATOR'S rulings (SC-15, DEC-157). `--decision`
    names where the ruling is recorded, and this CLI refuses a record that is not a file
    under the feature's own directory — a bare `DEC-300` or a path elsewhere in the tree is
    a claim INV-39 would then accept on the strength of its own syntax."""

    def setUp(self):
        super().setUp()
        (self.path.parent / "plan.yaml").write_text("approval:\n  status: approved\n",
                                                    encoding="utf-8")
        (self.path.parent / "notes").mkdir()
        (self.path.parent / "notes" / "raise.md").write_text("raise to 8\n", encoding="utf-8")

    def test_set_rework_writes_the_ruling(self):
        self.write(base_doc())
        self.assert_ok(self.run_cli("set-rework", "--file", str(self.path), "--rounds", "3",
                                    "--minutes", "120",
                                    "--decision", "plan.yaml#approval.rulings[0]"))
        self.assertEqual({"rounds": 3, "wall_clock_minutes": 120,
                          "decision": "plan.yaml#approval.rulings[0]"},
                         self.load()["rework"])
        self.assert_clean()

    def test_raise_cycles_moves_the_budget_and_appends_the_decision(self):
        self.write(base_doc(max_total_cycles=5))
        self.assert_ok(self.run_cli("raise-cycles", "--file", str(self.path), "--to", "8",
                                    "--decision", "notes/raise.md"))
        doc = self.load()
        self.assertEqual(8, doc["max_total_cycles"])
        self.assertEqual(1, len(doc["budget_decisions"]))
        record = doc["budget_decisions"][0]
        self.assertEqual({"at", "max_total_cycles", "decision"}, set(record))
        self.assertEqual(8, record["max_total_cycles"])
        self.assertEqual("notes/raise.md", record["decision"])
        self.assertRegex(record["at"], ISO_UTC)
        self.assert_clean()

    def test_raise_cycles_accepts_an_absolute_decision_path_inside_the_feature_dir(self):
        """The main session runs from the repo root, so a path it can copy-paste is absolute
        or cwd-relative; either resolves, as long as the file is the feature's own."""
        self.write(base_doc(max_total_cycles=5))
        self.assert_ok(self.run_cli("raise-cycles", "--file", str(self.path), "--to", "8",
                                    "--decision", str(self.path.parent / "notes" / "raise.md")))
        self.assertEqual(8, self.load()["max_total_cycles"])

    def test_raise_cycles_refuses_a_value_that_does_not_raise(self):
        before = self.write(base_doc(max_total_cycles=5))
        for to in ("5", "4"):
            result = self.run_cli("raise-cycles", "--file", str(self.path), "--to", to,
                                  "--decision", "notes/raise.md")
            self.assertEqual(2, result.returncode, result.stderr)
            self.assertIn("max_total_cycles", result.stderr)
            self.assertIn("5", result.stderr)
        self.assertEqual(before, self.path.read_bytes())

    def test_rulings_refuse_a_decision_that_is_not_a_file_under_the_feature_dir(self):
        """Refused at exit 2, file untouched: a record that does not exist (`DEC-300`,
        `notes/none.md`), one outside the feature directory (the checkout's own
        harness.json, an absolute path elsewhere), and a directory rather than a file."""
        outside = self.tmp / "elsewhere.md"
        outside.write_text("not this feature's\n", encoding="utf-8")
        (self.tmp / ".harness" / "harness.json").write_text("{}\n", encoding="utf-8")
        before = self.write(base_doc(max_total_cycles=5))
        for decision in ("DEC-300", "notes/none.md", "../../harness.json",
                         str(outside), "notes"):
            for verb, extra in (("raise-cycles", ["--to", "8"]),
                                ("set-rework", ["--rounds", "2", "--minutes", "60"])):
                result = self.run_cli(verb, "--file", str(self.path), *extra,
                                      "--decision", decision)
                self.assertEqual(2, result.returncode, (verb, decision, result.stderr))
                self.assertIn("--decision", result.stderr, (verb, decision))
                self.assertIn(str(self.path.parent), result.stderr, (verb, decision))
        self.assertEqual(before, self.path.read_bytes())


class SetMissionTest(FeatureRecordCase):
    """set-mission writes `mission` AND its `kind: mission` judgement in one locked write
    (SC-01, SC-21), so the ledger can never show a mission with no entry deciding it —
    which is the state check-state.sh INV-40 refuses."""

    MISSION = ["--by", "harness-orchestrator", "--reason", "known-cause bug, ~130 lines"]

    def test_set_mission_accepts_each_lane_and_refuses_others(self):
        self.write(base_doc())
        for mission in ("patch", "plan"):
            self.assert_ok(self.run_cli("set-mission", "--file", str(self.path),
                                        "--mission", mission, *self.MISSION))
            self.assertEqual(mission, self.load()["mission"])
            self.assert_clean()
        before = self.path.read_bytes()
        result = self.run_cli("set-mission", "--file", str(self.path), "--mission", "epic",
                              *self.MISSION)
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertEqual(before, self.path.read_bytes())

    def test_set_mission_appends_the_mission_judgement_deciding_the_new_mission(self):
        self.write(base_doc(judgements=[
            {"at": "2026-09-11T10:00:00+00:00", "by": "harness-pm", "kind": "mission",
             "decision": "plan", "reason": "intake"}]))
        self.assert_ok(self.run_cli("set-mission", "--file", str(self.path),
                                    "--mission", "patch", *self.MISSION))
        doc = self.load()
        self.assertEqual("patch", doc["mission"])
        self.assertEqual(2, len(doc["judgements"]))
        last = doc["judgements"][-1]
        self.assertEqual({"at", "by", "kind", "decision", "reason"}, set(last))
        self.assertEqual(("mission", "patch", "harness-orchestrator",
                          "known-cause bug, ~130 lines"),
                         (last["kind"], last["decision"], last["by"], last["reason"]))
        self.assertRegex(last["at"], ISO_UTC)
        self.assert_clean()

    def test_set_mission_refuses_without_by_or_reason(self):
        before = self.write(base_doc())
        for argv in (["--mission", "patch"],
                     ["--mission", "patch", "--by", "harness-orchestrator"],
                     ["--mission", "patch", "--reason", "r"]):
            result = self.run_cli("set-mission", "--file", str(self.path), *argv)
            self.assertEqual(2, result.returncode, (argv, result.stderr))
        self.assertEqual(before, self.path.read_bytes())

    def test_set_mission_refuses_a_reason_over_240_characters_unchanged(self):
        """The judgement is written under the same schema as `judgement`, so its cap
        holds here too and the mission is not written without its entry."""
        before = self.write(base_doc())
        result = self.run_cli("set-mission", "--file", str(self.path), "--mission", "patch",
                              "--by", "harness-orchestrator", "--reason", "r" * 241)
        self.assertEqual(feature_json_write.SCHEMA_REFUSAL_CODE, result.returncode, result.stderr)
        self.assertEqual(before, self.path.read_bytes())


class SpendTest(FeatureRecordCase):
    RUNS = [
        {"id": "r1", "squad": "product", "verdict": "PASS", "agent": "harness-product-lead",
         "started_at": "2026-09-11T10:00:00+00:00", "ended_at": "2026-09-11T10:45:30+00:00",
         "tokens": 1000},
        {"id": "r2", "squad": "eng", "verdict": "PASS", "agent": "harness-eng-lead",
         "started_at": "2026-09-11T11:00:00+00:00", "ended_at": "2026-09-11T12:30:00+00:00",
         "tokens": 2500},
        # Still running: contributes a run, no minutes, no tokens.
        {"id": "r3", "squad": "eng", "verdict": "PENDING", "agent": "harness-eng-lead",
         "started_at": "2026-09-11T12:31:00+00:00"},
    ]

    def spend(self):
        result = self.run_cli("spend", "--file", str(self.path))
        self.assert_ok(result)
        return json.loads(result.stdout)

    def test_spend_sums_whole_minutes_and_measured_tokens(self):
        self.write(base_doc(runs=self.RUNS))
        self.assertEqual({"runs": 3, "wall_clock_minutes": 135, "tokens": 3500, "phase": "plan",
                          "rework_minutes": 0, "rework_rounds": 0},
                         self.spend())

    def test_spend_reports_build_once_build_entry_is_recorded(self):
        self.write(base_doc(runs=self.RUNS, github={"build_entry": "opened"}))
        self.assertEqual("build", self.spend()["phase"])

    def test_spend_tokens_is_null_when_no_run_was_measured(self):
        """Null, not 0: an unmeasured feature has no token figure, and printing 0 would be
        the estimate SC-18 forbids."""
        self.write(base_doc(runs=[{"id": "r1", "squad": "eng", "verdict": "PASS",
                                   "agent": "harness-eng-lead"}]))
        self.assertEqual({"runs": 1, "wall_clock_minutes": 0, "tokens": None, "phase": "plan",
                          "rework_minutes": 0, "rework_rounds": 0},
                         self.spend())

    def test_spend_on_a_pre_feat59_ledger_is_all_zero_and_null(self):
        self.write(base_doc())
        self.assertEqual({"runs": 0, "wall_clock_minutes": 0, "tokens": None, "phase": "plan",
                          "rework_minutes": 0, "rework_rounds": 0},
                         self.spend())

    # The rework window: the operator's `rework.wall_clock_minutes` is a budget for REWORK,
    # so what is measured against it must start where rework can start — the first
    # `validate-*` run — and never carry the plan and build phases in. Before this window
    # existed, `wall_clock_minutes` (whole feature) stood in for it, and a 60-minute plan
    # plus a 40-minute build ate 100 of a 120-minute ruling before the first fix round.
    #
    # THE IDS ARE THE CORPUS'S SHAPE, DATE-PREFIXED (`2026-09-11-05-validate-validator`: 181
    # such against 1 bare `validate-validator` on disk). The first draft keyed the window on
    # `startswith("validate-")`, so on every real ledger the window stayed shut and the
    # build-phase SPEND advisory (SC-19) never fired. The `validate-` / `fix-` token is
    # matched at the start or after a `-`, never inside a word: `postfix-eng` is not a fix.
    REWORK_RUNS = [
        {"id": "2026-09-11-01-plan-product", "squad": "product", "verdict": "PASS",
         "agent": "harness-product-lead", "started_at": "2026-09-11T10:00:00+00:00",
         "ended_at": "2026-09-11T11:00:00+00:00", "tokens": 1000},
        {"id": "2026-09-11-02-t01-eng", "squad": "eng", "verdict": "PASS",
         "agent": "harness-eng-lead", "started_at": "2026-09-11T11:00:00+00:00",
         "ended_at": "2026-09-11T11:40:00+00:00"},
        {"id": "2026-09-11-05-validate-validator", "squad": "validator", "verdict": "FAIL",
         "agent": "harness-validator-lead", "started_at": "2026-09-11T12:00:00+00:00",
         "ended_at": "2026-09-11T12:30:00+00:00", "tokens": 4000},
        {"id": "2026-09-11-06-fix-c1-validator", "squad": "validator", "verdict": "FAIL",
         "agent": "harness-validator-lead", "started_at": "2026-09-11T12:30:00+00:00",
         "ended_at": "2026-09-11T13:15:00+00:00"},
        {"id": "2026-09-11-07-postfix-eng", "squad": "eng", "verdict": "PASS",
         "agent": "harness-eng-lead", "started_at": "2026-09-11T13:15:00+00:00",
         "ended_at": "2026-09-11T13:25:00+00:00"},
        {"id": "2026-09-11-08-fix-c2-validator", "squad": "validator", "verdict": "PASS",
         "agent": "harness-validator-lead", "started_at": "2026-09-11T13:25:00+00:00",
         "ended_at": "2026-09-11T13:45:00+00:00"},
    ]

    def test_rework_minutes_start_at_the_first_validate_run_and_count_fix_rounds(self):
        self.write(base_doc(runs=self.REWORK_RUNS, github={"build_entry": "opened"}))
        spend = self.spend()
        self.assertEqual(205, spend["wall_clock_minutes"])   # 60+40+30+45+10+20, for the briefing
        self.assertEqual(105, spend["rework_minutes"])       # validate 30 + fix 45 + 10 + fix 20
        self.assertEqual(2, spend["rework_rounds"])          # the two fix-* runs, not postfix

    def test_rework_window_opens_on_a_bare_validate_id_too(self):
        """The one pre-date-prefix ledger shape on disk still counts: the token is matched
        at the start of the id as well as after a `-`."""
        runs = [dict(entry) for entry in self.REWORK_RUNS]
        runs[2]["id"] = "validate-validator"
        runs[3]["id"] = "fix-c1-validator"
        self.write(base_doc(runs=runs, github={"build_entry": "opened"}))
        spend = self.spend()
        self.assertEqual(105, spend["rework_minutes"])
        self.assertEqual(2, spend["rework_rounds"])

    def test_rework_window_is_zero_before_any_validate_run(self):
        self.write(base_doc(runs=self.REWORK_RUNS[:2], github={"build_entry": "opened"}))
        spend = self.spend()
        self.assertEqual(100, spend["wall_clock_minutes"])
        self.assertEqual(0, spend["rework_minutes"])
        self.assertEqual(0, spend["rework_rounds"])



class ProposeReworkTest(FeatureRecordCase):
    """`propose-rework`: the baseline the main session shows the operator at signature.
    Deterministic from disk — the mission, the task count, and two harness.json budgets — so
    the operator confirms or changes a number rather than inventing one (SC-15, SC-22)."""

    def setUp(self):
        super().setUp()
        (self.tmp / ".harness").mkdir(exist_ok=True)
        (self.tmp / ".harness" / "harness.json").write_text(json.dumps(
            {"budgets": {"max_total_cycles": 4, "rework_round_minutes": 45}}), encoding="utf-8")

    def plan(self, tasks):
        body = "schema: plan/1\nfeature: FEAT-77-record\napproval:\n  status: pending\ntasks:\n"
        for i in range(1, tasks + 1):
            body += (f"  - id: T-{i:02d}\n    title: t{i}\n    traces: [SC-01]\n"
                     f"    change_type: logic\n    execution_mode: main-session-direct\n"
                     f"    execution_reason: fixture\n    depends_on: []\n    status: pending\n"
                     f"    files: [fixture]\n    verify: 'true'\n    intent: fixture\n")
        (self.path.parent / "plan.yaml").write_text(body, encoding="utf-8")

    def propose(self):
        result = self.run_cli("propose-rework", "--file", str(self.path))
        self.assert_ok(result)
        return json.loads(result.stdout)

    def test_patch_is_one_round(self):
        self.write(base_doc(mission="patch"))
        self.plan(1)
        self.assertEqual({"rounds": 1, "minutes": 45}, {k: self.propose()[k] for k in ("rounds", "minutes")})

    def test_plan_rounds_scale_with_tasks_floor_two(self):
        self.write(base_doc(mission="plan"))
        for tasks, rounds in ((1, 2), (3, 2), (4, 2), (7, 3), (9, 3), (10, 4)):
            self.plan(tasks)
            self.assertEqual(rounds, self.propose()["rounds"], tasks)
            self.assertEqual(rounds * 45, self.propose()["minutes"], tasks)

    def test_rounds_never_exceed_max_total_cycles(self):
        self.write(base_doc(mission="plan"))
        self.plan(30)   # ceil(30/3) = 10, but harness.json caps cycles at 4
        self.assertEqual(4, self.propose()["rounds"])

    def test_basis_names_every_input(self):
        self.write(base_doc(mission="plan"))
        self.plan(7)
        basis = self.propose()["basis"]
        for token in ("7 tasks", "rework_round_minutes", "45", "plan"):
            self.assertIn(token, basis)

    def test_refuses_without_a_mission(self):
        self.write(base_doc())
        self.plan(3)
        result = self.run_cli("propose-rework", "--file", str(self.path))
        self.assertEqual(2, result.returncode)
        self.assertIn("mission", result.stderr)

class SchemaTest(unittest.TestCase):
    """The schema half of the ledger: what feature_json_write refuses at every verb."""

    def problems(self, doc):
        return feature_schema.problems_for_text(json.dumps(doc), "sample.json")

    def judgement(self, **overrides):
        entry = {"at": "2026-09-11T10:00:00+00:00", "by": "harness-orchestrator",
                 "kind": "mission", "decision": "patch", "reason": "small"}
        entry.update(overrides)
        return entry

    def test_old_shape_without_any_new_key_is_still_valid(self):
        self.assertEqual([], self.problems(base_doc(
            runs=[{"id": "r1", "squad": "eng", "verdict": "PASS", "agent": "harness-eng-lead"}])))

    def test_full_new_shape_is_valid(self):
        doc = base_doc(mission="plan", judgements=[self.judgement()],
                       rework={"rounds": 2, "wall_clock_minutes": 60, "decision": "ruling-1"},
                       budget_decisions=[{"at": "2026-09-11T10:00:00+00:00",
                                          "max_total_cycles": 6, "decision": "DEC-1"}],
                       runs=[{"id": "r1", "squad": "eng", "verdict": "PASS",
                              "agent": "harness-eng-lead",
                              "started_at": "2026-09-11T10:00:00+00:00",
                              "ended_at": "2026-09-11T10:10:00+00:00", "tokens": None}])
        self.assertEqual([], self.problems(doc))

    def test_judgement_missing_any_of_the_five_keys_is_rejected(self):
        for key in ("at", "by", "kind", "decision", "reason"):
            entry = self.judgement()
            del entry[key]
            problems = self.problems(base_doc(judgements=[entry]))
            self.assertTrue(problems and any(repr(key) in p for p in problems), (key, problems))

    def test_judgement_unknown_kind_is_rejected(self):
        problems = self.problems(base_doc(judgements=[self.judgement(kind="hunch")]))
        self.assertTrue(problems and any("/judgements/0/kind" in p for p in problems), problems)

    def test_judgement_extra_key_is_rejected(self):
        problems = self.problems(base_doc(judgements=[self.judgement(note="why")]))
        self.assertTrue(problems and any("'note'" in p for p in problems), problems)

    def test_judgement_at_must_be_an_iso_timestamp(self):
        problems = self.problems(base_doc(judgements=[self.judgement(at="yesterday")]))
        self.assertTrue(problems and any("/judgements/0/at" in p for p in problems), problems)

    def test_mission_outside_the_two_lanes_is_rejected(self):
        problems = self.problems(base_doc(mission="epic"))
        self.assertTrue(problems and any("/mission" in p for p in problems), problems)

    def test_rework_requires_all_three_keys(self):
        for key in ("rounds", "wall_clock_minutes", "decision"):
            rework = {"rounds": 1, "wall_clock_minutes": 30, "decision": "d"}
            del rework[key]
            problems = self.problems(base_doc(rework=rework))
            self.assertTrue(problems and any(repr(key) in p for p in problems), (key, problems))

    def test_budget_decision_below_one_cycle_is_rejected(self):
        problems = self.problems(base_doc(budget_decisions=[
            {"at": "2026-09-11T10:00:00+00:00", "max_total_cycles": 0, "decision": "d"}]))
        self.assertTrue(problems and any("max_total_cycles" in p for p in problems), problems)

    def test_run_tokens_negative_or_string_is_rejected_null_is_not(self):
        def run(tokens):
            return base_doc(runs=[{"id": "r1", "squad": "eng", "verdict": "PASS",
                                   "agent": "harness-eng-lead", "tokens": tokens}])
        self.assertEqual([], self.problems(run(None)))
        self.assertEqual([], self.problems(run(0)))
        for bad in (-1, "1200", 12.5):
            problems = self.problems(run(bad))
            self.assertTrue(problems and any("/runs/0/tokens" in p for p in problems),
                            (bad, problems))


if __name__ == "__main__":
    unittest.main()
