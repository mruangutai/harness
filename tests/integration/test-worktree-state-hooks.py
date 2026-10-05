#!/usr/bin/env python3
"""Git operations converge the sparse layout through the hooks (FEAT-1559 T-04, SC-01/07/08/09).

Every subject is a checkout of the synthetic owner in f58_sparse_fixture. The owner gets its own
copy of the real hooks and bin under `<owner>/.claude/skills/harness/` (untracked, git-excluded),
and `core.hooksPath` names that directory ABSOLUTELY. So every hook runs from the owner's copy
while git runs it inside a linked worktree: the shim must repair git's checkout, not the one it
is installed in. The sweep, finding its root beside itself, can only ever reach the fixture. No
case touches this repository's own hooks configuration or worktree registrations.

What modern git does on its own, measured on git 2.54 before these cases were written:
  - an ordinary merge, rebase, reset or cherry-pick keeps a cone-mode layout intact, even with a
    merge or rebase that edits a hidden feature;
  - a merge or rebase that brings in a NEW top-level directory leaves the cone stale (cone 3,
    skip-bits 4): the directory stays hidden until something re-derives the cone;
  - an index rewrite (`git read-tree HEAD`) clears every skip bit, leaving the hidden paths as
    unstaged deletions (class A). The next merge re-applies them itself, so the class-A case is
    driven through `commit --amend`, which fires post-rewrite and does not.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BIN))
import f58_sparse_fixture as F  # noqa: E402

HOOK_NAMES = ("post-checkout", "post-merge", "post-rewrite")
SEGMENTS = ("harness", "kaya")


class Hooked(unittest.TestCase):
    def setUp(self):
        ctx = F.sparse_fixture()
        self.fx = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)
        owner = self.fx.owner
        # Into the fixture's own (tracked) bin directory: every script there derives the root
        # four levels above itself, so the sweep and the creators can only reach the fixture.
        self.bin = os.path.join(owner, ".claude", "skills", "harness", "bin")
        shutil.copytree(BIN, self.bin, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__"))
        self.hooks = os.path.join(owner, ".claude", "skills", "harness", "hooks")
        os.makedirs(self.hooks)
        for name in HOOK_NAMES:
            if (ROOT / ".claude/skills/harness/hooks" / name).exists():
                shutil.copy2(ROOT / ".claude/skills/harness/hooks" / name, self.hooks)
        with open(os.path.join(owner, ".git", "info", "exclude"), "a") as fh:
            fh.write("/.claude/skills/\n")
        F.git(owner, "config", "core.hooksPath", self.hooks)
        self.env = dict(F.ENV, HARNESS_PROJECT_DIR=owner, GH_BIN="/nonexistent-gh")

    def state(self, checkout, mode="--verify"):
        proc = subprocess.run([sys.executable, os.path.join(self.bin, "worktree-state.py"), mode,
                               "--json", "--checkout", checkout], env=F.ENV,
                              capture_output=True, text=True)
        doc = json.loads(proc.stdout)
        return proc.returncode, doc

    def assert_converged(self, checkout):
        code, doc = self.state(checkout)
        self.assertEqual(code, 0, doc["findings"])
        self.assertEqual(F.git(checkout, "status", "--porcelain").stdout, "")
        return doc

    def cone(self, checkout):
        return F.git(checkout, "sparse-checkout", "list").stdout.split()


class Creation(Hooked):
    """SC-08: a checkout converges whoever creates it, before and after its record exists."""

    def assert_recordless_cone(self, checkout, fid):
        cone = self.cone(checkout)
        for segment in SEGMENTS:
            self.assertIn(f".harness/{segment}/features/{fid}", cone)
        self.assertEqual(F.feature_dirs_on_disk(checkout), [])

    def record_converges(self, checkout, segment, fid):
        F.write_files(checkout, {f".harness/{segment}/features/{fid}/feature.json":
                                 F.feature_json(fid, f"feat/{fid}")})
        F.git(checkout, "add", "-A")
        F.git(checkout, "commit", "-qm", f"record {fid}")
        F.git(checkout, "commit", "-q", "--amend", "--no-edit")      # post-rewrite repairs
        doc = self.assert_converged(checkout)
        self.assertEqual((doc["active_feature"], doc["artifact_segment"]), (fid, segment))
        self.assertEqual(F.feature_dirs_on_disk(checkout), [f"{segment}/{fid}"])

    def test_bare_git_worktree_add(self):
        wt = self.fx.add_worktree("FEAT-8-fresh")
        self.assert_converged(wt)
        self.assert_recordless_cone(wt, "FEAT-8-fresh")
        self.record_converges(wt, "harness", "FEAT-8-fresh")

    def test_feature_worktree_create(self):
        proc = subprocess.run([sys.executable, os.path.join(self.bin, "feature-worktree.py"),
                               "create", "--repo", "harness", "--id", "FEAT-9-made"],
                              env=self.env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        wt = proc.stdout.strip().splitlines()[-1]
        self.assertEqual(wt, self.fx.worktree_path("FEAT-9-made"))
        self.assert_converged(wt)
        self.assert_recordless_cone(wt, "FEAT-9-made")
        self.record_converges(wt, "harness", "FEAT-9-made")

    def test_fleet_planning_worktree_uses_its_artifact_segment(self):
        workspace = os.path.join(self.fx.base, "workspace")
        product = os.path.join(workspace, "kaya")
        os.makedirs(product)
        F.git(product, "init", "-q", "-b", "main")
        F.write_files(product, {"README.md": "kaya\n"})
        F.git(product, "add", "-A")
        F.git(product, "commit", "-qm", "seed")
        self.fx.commit_owner({".harness/factory/fleet.yaml":
                              f"schema: factory-fleet/1\nworkspace_root: {workspace}\n"
                              f"repos:\n  - name: org/kaya\n    default_branch: main\n"}, "fleet")
        proc = subprocess.run([sys.executable, os.path.join(self.bin, "feature-worktree.py"),
                               "create", "--repo", "org/kaya", "--id", "FEAT-11-kplan"],
                              env=self.env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        planning = next(line.split(" ", 1)[1] for line in proc.stdout.splitlines()
                        if line.startswith("PLANNING "))
        self.assertEqual(planning, self.fx.worktree_path("FEAT-11-kplan"))   # harness segment
        self.assert_converged(planning)
        self.assert_recordless_cone(planning, "FEAT-11-kplan")
        self.record_converges(planning, "kaya", "FEAT-11-kplan")             # artifact segment

    def test_pinned_checkout_add(self):
        sha = F.git(self.fx.owner, "rev-parse", "HEAD").stdout.strip()
        proc = subprocess.run([sys.executable, os.path.join(self.bin, "pinned-checkout.py"),
                               "add", "--feature", "FEAT-2-beta", "--run-id", "r1",
                               "--persona", "qa", "--sha", sha],
                              env=self.env, cwd=self.fx.owner, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        pin = proc.stdout.strip().splitlines()[-1]
        self.assertEqual(os.path.basename(pin), "FEAT-2-beta--r1--qa")
        doc = self.assert_converged(pin)
        self.assertEqual(doc["checkout_class"], "pin")
        self.assertEqual(F.feature_dirs_on_disk(pin), ["harness/FEAT-2-beta"])


class Operations(Hooked):
    """SC-01/SC-07: merge, rebase and amend leave a clean, verified layout."""

    def setUp(self):
        super().setUp()
        self.wt = self.fx.add_worktree("FEAT-1-alpha")
        # Converged EXPLICITLY, not by post-checkout: each case here is red or green on the one
        # hook its operation fires, never on whether creation happened to converge first.
        self.assertEqual(self.state(self.wt, "--repair")[0], 0)
        F.write_files(self.wt, {".harness/harness/features/FEAT-1-alpha/notes/w.md": "work\n"})
        F.git(self.wt, "add", "-A")
        F.git(self.wt, "commit", "-qm", "worktree work")
        self.fx.commit_owner({"newtop/file.txt": "new\n",
                              ".harness/harness/features/FEAT-2-beta/BRIEF.md": "# v2\n"},
                             "main grows a top-level directory and edits a hidden feature")

    def test_merge(self):
        proc = F.git(self.wt, "merge", "--no-edit", "main")
        self.assert_converged(self.wt)
        self.assertTrue(os.path.isfile(os.path.join(self.wt, "newtop/file.txt")))
        self.assertEqual(F.feature_dirs_on_disk(self.wt), ["harness/FEAT-1-alpha"])
        self.assertIn(f"post-merge-sweep: resolved repository root: {self.fx.owner}",
                      proc.stdout + proc.stderr)

    def test_rebase(self):
        F.git(self.wt, "rebase", "main")
        self.assert_converged(self.wt)
        self.assertTrue(os.path.isfile(os.path.join(self.wt, "newtop/file.txt")))
        self.assertEqual(F.feature_dirs_on_disk(self.wt), ["harness/FEAT-1-alpha"])

    def test_class_a_after_an_index_rewrite_is_repaired_by_amend(self):
        F.git(self.wt, "read-tree", "HEAD")
        deleted = F.git(self.wt, "status", "--porcelain").stdout.splitlines()
        self.assertTrue(deleted and all(line.startswith(" D .harness/") for line in deleted),
                        deleted)
        F.git(self.wt, "commit", "-q", "--amend", "--no-edit")
        self.assert_converged(self.wt)
        self.assertEqual(F.feature_dirs_on_disk(self.wt), ["harness/FEAT-1-alpha"])

    def test_class_c_is_skipped_and_left_byte_identical(self):
        F.write_files(self.wt, {".harness/harness/features/FEAT-2-beta/stray.md": "mine\n"})
        before = F.snapshot(self.wt)
        head = F.git(self.wt, "rev-parse", "HEAD").stdout.strip()
        proc = subprocess.run([os.path.join(self.hooks, "post-checkout"), head, head, "1"],
                              cwd=self.wt, env=F.ENV, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn(f"layout repair SKIPPED in {self.wt}", proc.stderr)
        self.assertEqual(F.snapshot(self.wt), before)


if __name__ == "__main__":
    unittest.main()
