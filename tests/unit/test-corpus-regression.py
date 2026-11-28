#!/usr/bin/env python3
"""Ruling B's prohibitions, locked by behaviour (FEAT-1559 SC-02, SC-13).

Ruling B (2026-10-04): another feature is read from the MAIN CORPUS only — the owner root's
ordinary files. Each case pins one way that could quietly stop being true:

  * no sibling provider  — a feature that exists only in an in-progress sibling worktree is never
                           answered from that sibling, by path or by population;
  * no git-content read  — a main-corpus read sees the owner's working file, so an uncommitted
                           owner edit is what a worktree reads, not the HEAD blob;
  * no symlink, no owner write — repairing a worktree creates no symlink and changes no byte of
                           the owner's tree, index or config;
  * landed means tracked — an untracked directory at the owner is not part of the population a
                           worktree's gates judge.

Each case builds a small real repository: the seam answers from git structure and pointer files,
so a fake would test the fake.
"""
from unit_support import BIN  # noqa: F401  (first: puts bin/ and tests/ on sys.path)
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import feature_corpus as fc
from git_support import ENV, add_worktree, checked_git, commit_files, git


def record(fid):
    return '{"feature_id": "%s", "branch": "feat/%s"}\n' % (fid, fid)


def put(root, rel, text):
    path = Path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def tree_digest(root, extra=()):
    """sha256 over every work-tree path, link target and file byte under `root` (not `.git`, not
    `.claude`, where the worktrees live), plus the bytes of each file in `extra`."""
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        if dirpath == root:
            dirnames[:] = [d for d in dirnames if d not in (".git", ".claude")]
        for name in sorted(filenames) + [d for d in dirnames if os.path.islink(os.path.join(dirpath, d))]:
            path = os.path.join(dirpath, name)
            h.update(os.path.relpath(path, root).encode())
            if os.path.islink(path):
                h.update(b"->" + os.readlink(path).encode())
            elif os.path.isfile(path):
                h.update(Path(path).read_bytes())
    for path in extra:
        h.update(Path(path).read_bytes())
    return h.hexdigest()


class Corpus(unittest.TestCase):
    def setUp(self):
        self.base = os.path.realpath(
            self.enterContext(tempfile.TemporaryDirectory(prefix="corpus-regression-")))
        self.owner = os.path.join(self.base, "owner")
        files = {".harness/team-config.yaml": "teams: {}\n",
                 ".harness/notes/n.md": "note\n",
                 ".harness/harness/features/FEAT-1-a/feature.json": record("FEAT-1-a"),
                 ".harness/harness/features/FEAT-2-b/feature.json": record("FEAT-2-b"),
                 ".harness/harness/features/FEAT-2-b/BRIEF.md": "# landed\n",
                 "src/app.py": "app\n"}
        git(self.base, "init", "-q", "-b", "main", self.owner)
        commit_files(self.owner, files, "seed", git=checked_git)

    def worktree(self, name):
        path = add_worktree(self.owner, name, "harness", f"feat/{name}", git=checked_git)
        proc = subprocess.run([sys.executable, str(BIN / "worktree-state.py"), "--repair",
                               "--checkout", path], env=ENV, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return path

    def test_no_sibling_provider(self):
        wt = self.worktree("FEAT-1-a")
        sibling = self.worktree("FEAT-9-wip")
        rel = ".harness/harness/features/FEAT-9-wip/feature.json"
        put(sibling, rel, record("FEAT-9-wip"))
        self.assertEqual(fc.corpus_path(wt, rel), os.path.join(self.owner, rel))
        self.assertFalse(os.path.exists(fc.corpus_path(wt, rel)))
        self.assertNotIn("FEAT-9-wip", [e["id"] for e in fc.population(wt)])

    def test_main_corpus_reads_see_the_owners_working_file(self):
        wt = self.worktree("FEAT-1-a")
        rel = ".harness/harness/features/FEAT-2-b/BRIEF.md"
        self.assertFalse(os.path.exists(os.path.join(wt, rel)))
        Path(self.owner, rel).write_text("# edited at the owner, not committed\n")
        self.assertEqual(Path(fc.corpus_path(wt, rel)).read_text(),
                         "# edited at the owner, not committed\n")

    def test_repair_makes_no_symlink_and_writes_nothing_at_the_owner(self):
        def snapshot():
            return tree_digest(self.owner, [os.path.join(self.owner, ".git", "index")])

        def config():
            return set(git(self.owner, "config", "--local", "--list").stdout.splitlines())

        before, config_before = snapshot(), config()
        wt = self.worktree("FEAT-1-a")
        self.assertEqual(snapshot(), before)
        # The one shared-config write is git's own: a per-worktree sparse checkout needs
        # extensions.worktreeConfig, set once for the repository. Nothing else changes.
        added = config() - config_before
        self.assertLessEqual(added, {"extensions.worktreeconfig=true"})
        self.assertEqual([str(p) for p in Path(wt).rglob("*") if p.is_symlink()], [])
        self.assertEqual(sorted(os.listdir(os.path.join(wt, ".harness/harness/features"))),
                         ["FEAT-1-a"])

    def test_an_untracked_owner_directory_is_not_landed(self):
        put(self.owner, ".harness/harness/features/FEAT-7-stale/feature.json",
            record("FEAT-7-stale"))
        wt = self.worktree("FEAT-1-a")
        self.assertEqual([e["id"] for e in fc.population(wt)], ["FEAT-1-a", "FEAT-2-b"])


if __name__ == "__main__":
    unittest.main()
