#!/usr/bin/env python3
"""worktree-state.py --verify / --repair over real linked worktrees (FEAT-1559 SC-01, SC-06,
SC-07).

Every subject is a real git worktree of the synthetic owner in f58_sparse_fixture — never this
checkout. The command runs as a subprocess, the way hooks and gates call it, and its decision is
read from the JSON report as well as the exit status.
"""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / ".claude/skills/harness/bin/worktree-state.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import f58_sparse_fixture as F  # noqa: E402

HIDDEN_BRIEF = ".harness/harness/features/FEAT-2-beta/BRIEF.md"
BETA_TEXT = "# BRIEF FEAT-2-beta\n"


def run(mode, checkout, *extra):
    proc = subprocess.run([sys.executable, str(CLI), f"--{mode}", "--checkout", checkout,
                           "--json", *extra], env=F.ENV, capture_output=True, text=True)
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise AssertionError(f"no JSON from {mode} (exit {proc.returncode}): "
                             f"{proc.stdout!r} {proc.stderr!r}")
    return proc.returncode, doc


def labels(doc):
    return [f["label"] for f in doc["findings"]]


class Case(unittest.TestCase):
    def setUp(self):
        ctx = F.sparse_fixture()
        self.fx = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)

    def converged(self, checkout):
        code, doc = run("repair", checkout)
        self.assertEqual(code, 0, doc)
        return doc

    def assert_required_paths(self, checkout):
        for rel in F.REQUIRED_PATHS:
            self.assertTrue(os.path.isdir(os.path.join(checkout, rel)), rel)


class RecordBearingClasses(Case):
    def test_harness_planning_worktree(self):
        wt = self.fx.add_worktree("FEAT-1-alpha")
        self.assertEqual(len(F.feature_dirs_on_disk(wt)), 4)        # cut full, as today
        code, doc = run("verify", wt)
        self.assertEqual(code, 3)
        self.assertEqual(labels(doc), ["cone", "skip-bits", "materialisation"])
        doc = self.converged(wt)
        self.assertTrue(doc["repaired"])
        self.assertEqual((doc["checkout_class"], doc["active_feature"], doc["artifact_segment"]),
                         ("planning-worktree", "FEAT-1-alpha", "harness"))
        self.assertEqual(F.feature_dirs_on_disk(wt), ["harness/FEAT-1-alpha"])
        self.assert_required_paths(wt)
        self.assertTrue(os.path.isfile(os.path.join(wt, ".harness/team-config.yaml")))
        self.assertEqual(run("verify", wt), (0, run("verify", wt)[1]))

    def test_fleet_planning_worktree_uses_the_record_segment(self):
        wt = self.fx.add_worktree("FEAT-10-kaya-app")          # under .claude/worktrees/harness
        doc = self.converged(wt)
        self.assertEqual(doc["artifact_segment"], "kaya")
        self.assertEqual(F.feature_dirs_on_disk(wt), ["kaya/FEAT-10-kaya-app"])
        self.assert_required_paths(wt)

    def test_validator_pin(self):
        pin = self.fx.add_pin("FEAT-2-beta")
        doc = self.converged(pin)
        self.assertEqual((doc["checkout_class"], doc["active_feature"]), ("pin", "FEAT-2-beta"))
        self.assertEqual(F.feature_dirs_on_disk(pin), ["harness/FEAT-2-beta"])

    def test_new_top_level_directory_survives_without_an_edit(self):
        self.fx.commit_owner({"newtop/x.txt": "x\n"}, "add a top-level tree")
        wt = self.fx.add_worktree("FEAT-1-alpha")
        self.converged(wt)
        self.assertTrue(os.path.isfile(os.path.join(wt, "newtop/x.txt")))

    def test_recordless_feature_converges_before_and_after_its_record(self):
        wt = self.fx.add_worktree("FEAT-99-new")
        doc = self.converged(wt)
        self.assertIsNone(doc["artifact_segment"])
        self.assertEqual(F.feature_dirs_on_disk(wt), [])
        cone = F.git(wt, "sparse-checkout", "list").stdout.split()
        self.assertIn(".harness/harness/features/FEAT-99-new", cone)
        self.assertIn(".harness/kaya/features/FEAT-99-new", cone)
        F.write_files(wt, {".harness/kaya/features/FEAT-99-new/BRIEF.md": "# new\n"})
        code, doc = run("verify", wt)
        self.assertEqual((code, doc["artifact_segment"], labels(doc)), (0, "kaya", []))


class NoOpSubjects(Case):
    def assert_noop(self, path, klass):
        before = F.snapshot(path)
        for mode in ("verify", "repair"):
            code, doc = run(mode, path)
            self.assertEqual((code, doc["checkout_class"], doc["findings"]), (0, klass, []))
            self.assertTrue(doc["noop"])
        self.assertEqual(F.snapshot(path), before)

    def test_plain_clone_keeps_everything(self):
        clone = self.fx.clone()
        self.assert_noop(clone, "plain-clone")
        self.assertEqual(len(F.feature_dirs_on_disk(clone)), 4)

    def test_worktree_outside_the_worktrees_segment(self):
        self.assert_noop(self.fx.add_probe("scratch"), "probe")

    def test_chore_worktree_without_a_feature_identity(self):
        self.assert_noop(self.fx.add_worktree("test-speed", branch="chore/test-speed"), "probe")


class Refusals(Case):
    def assert_refused_unchanged(self, path, needle):
        before = F.snapshot(path)
        for mode in ("verify", "repair"):
            code, doc = run(mode, path)
            self.assertEqual((code, labels(doc)), (3, ["cone"]))
            self.assertIn(needle, doc["findings"][0]["detail"])
        self.assertEqual(F.snapshot(path), before)

    def test_underivable_pin_name(self):
        path = self.fx.add_pin("FEAT-2-beta")
        moved = os.path.join(os.path.dirname(path), "not-a-pin")
        F.git(self.fx.owner, "worktree", "move", path, moved)
        self.assert_refused_unchanged(moved, "cannot be derived")

    def test_directory_and_branch_naming_different_features(self):
        path = self.fx.add_worktree("FEAT-1-alpha", branch="feat/FEAT-2-beta")
        self.assert_refused_unchanged(path, "ambiguous")

    def test_two_segments_claiming_the_active_id(self):
        self.fx.commit_owner({".harness/kaya/features/FEAT-1-alpha/BRIEF.md": "dup\n"}, "dup")
        self.assert_refused_unchanged(self.fx.add_worktree("FEAT-1-alpha"), "ambiguous")


class StructuralBreaks(Case):
    def setUp(self):
        super().setUp()
        self.wt = self.fx.add_worktree("FEAT-1-alpha")
        self.converged(self.wt)

    def assert_verify_reports_without_mutation(self, code, label):
        before = F.snapshot(self.wt)
        got, doc = run("verify", self.wt)
        self.assertEqual(got, code, doc)
        self.assertIn(label, labels(doc))
        self.assertEqual(F.snapshot(self.wt), before)

    def assert_repair_converges(self):
        self.converged(self.wt)
        self.assertEqual(run("verify", self.wt)[0], 0)
        self.assertEqual(F.feature_dirs_on_disk(self.wt), ["harness/FEAT-1-alpha"])
        self.assertEqual(F.git(self.wt, "status", "--porcelain").stdout, "")

    def test_wrong_cone(self):
        F.git(self.wt, "sparse-checkout", "set", "--cone", "src")
        self.assert_verify_reports_without_mutation(3, "cone")
        self.assert_repair_converges()

    def test_cleared_skip_bits_after_a_merge_are_class_a(self):
        hidden = [p for p in F.git(self.wt, "ls-files", "-t").stdout.splitlines()
                  if p.startswith("S ")]
        F.git(self.wt, "update-index", "--no-skip-worktree", *[p[2:] for p in hidden])
        status = F.git(self.wt, "status", "--porcelain").stdout
        self.assertIn(f" D {HIDDEN_BRIEF}", status)          # the measured shape: absent, no bit
        self.assert_verify_reports_without_mutation(4, "skip-bits")
        _code, doc = run("verify", self.wt)
        self.assertNotIn("dirty", labels(doc))
        self.assert_repair_converges()

    def test_merge_touching_a_hidden_feature(self):
        self.fx.commit_owner({HIDDEN_BRIEF: "# BRIEF FEAT-2-beta, revised\n"}, "revise beta")
        F.git(self.wt, "merge", "-q", "--no-edit", "main")
        self.assert_repair_converges()

    def test_class_b_identical_materialised_file(self):
        # git clears the skip bit of any file present on disk when it loads the index
        # (sparse.expectFilesOutsideOfPatterns), so skip-bits outranks materialisation here.
        F.write_files(self.wt, {HIDDEN_BRIEF: BETA_TEXT})
        self.assert_verify_reports_without_mutation(4, "materialisation")
        _code, doc = run("verify", self.wt)
        self.assertNotIn("dirty", labels(doc))
        self.assert_repair_converges()

    def test_second_repair_changes_nothing(self):
        before = F.snapshot(self.wt)
        code, doc = run("repair", self.wt)
        self.assertEqual((code, doc["repaired"]), (0, False))
        self.assertEqual(F.snapshot(self.wt), before)


class ClassC(Case):
    """Any class-C path anywhere refuses repair with exit 8 and leaves every byte in place."""

    def assert_refused(self, wt, path):
        before = F.snapshot(wt)
        for mode in ("verify", "repair"):
            code, doc = run(mode, wt)
            self.assertEqual(code, 8, doc)
            dirty = [f for f in doc["findings"] if f["label"] == "dirty"][0]
            self.assertIn(path, dirty["paths"])
        self.assertEqual(F.snapshot(wt), before)

    def converged_wt(self):
        wt = self.fx.add_worktree("FEAT-1-alpha")
        self.converged(wt)
        return wt

    def test_real_edit_in_the_active_feature(self):
        wt = self.converged_wt()
        rel = ".harness/harness/features/FEAT-1-alpha/BRIEF.md"
        F.write_files(wt, {rel: "edited\n"})
        self.assert_refused(wt, rel)

    def test_staged_deletion_of_a_hidden_file(self):
        wt = self.converged_wt()
        F.git(wt, "rm", "-q", "--cached", "--sparse", HIDDEN_BRIEF)
        self.assert_refused(wt, HIDDEN_BRIEF)

    def test_untracked_and_ignored_files_in_a_hidden_directory(self):
        wt = self.converged_wt()
        F.write_files(wt, {".harness/harness/features/FEAT-2-beta/notes/new.md": "work\n"})
        self.assert_refused(wt, ".harness/harness/features/FEAT-2-beta/notes/new.md")
        os.remove(os.path.join(wt, ".harness/harness/features/FEAT-2-beta/notes/new.md"))
        F.write_files(wt, {".harness/harness/features/FEAT-2-beta/plan.yaml.lock": ""})
        self.assert_refused(wt, ".harness/harness/features/FEAT-2-beta/plan.yaml.lock")

    def test_rewritten_skip_worktree_file(self):
        wt = self.converged_wt()
        F.write_files(wt, {HIDDEN_BRIEF: "someone wrote here\n"})
        self.assert_refused(wt, HIDDEN_BRIEF)

    def test_mixed_a_b_c_refuses_and_mutates_nothing(self):
        wt = self.fx.add_worktree("FEAT-1-alpha")               # full: every hidden file is B
        os.remove(os.path.join(wt, ".harness/harness/features/FEAT-2-beta/feature.json"))   # A
        F.write_files(wt, {".harness/kaya/features/FEAT-10-kaya-app/BRIEF.md": "edit\n"})    # C
        self.assert_refused(wt, ".harness/kaya/features/FEAT-10-kaya-app/BRIEF.md")
        self.assertEqual(len(F.feature_dirs_on_disk(wt)), 4)


class Report(Case):
    def test_json_shape_retains_every_category(self):
        wt = self.fx.add_worktree("FEAT-1-alpha")
        F.write_files(wt, {".harness/harness/features/FEAT-1-alpha/BRIEF.md": "edited\n"})
        code, doc = run("verify", wt)
        self.assertEqual(code, 8)
        self.assertEqual(set(doc), {"checkout", "checkout_class", "active_feature",
                                    "artifact_segment", "mode", "noop", "repaired", "findings"})
        self.assertEqual(labels(doc), ["dirty", "cone", "skip-bits", "materialisation"])
        for f in doc["findings"]:
            self.assertEqual(f["paths"], sorted(f["paths"]))
            self.assertEqual(set(f), {"code", "label", "paths", "detail"})

    def test_human_output_names_the_category_and_the_remedy(self):
        wt = self.fx.add_worktree("FEAT-1-alpha")
        proc = subprocess.run([sys.executable, str(CLI), "--verify", "--checkout", wt],
                              env=F.ENV, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 3)
        self.assertIn("cone (3)", proc.stdout)
        self.assertIn(f"--repair --checkout {wt}", proc.stdout)


if __name__ == "__main__":
    unittest.main()
