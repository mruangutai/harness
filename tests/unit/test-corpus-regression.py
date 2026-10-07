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
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(BIN))
import feature_corpus as fc  # noqa: E402

ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
           GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=ENV, check=True,
                          capture_output=True, text=True).stdout


def record(fid):
    return '{"feature_id": "%s", "branch": "feat/%s"}\n' % (fid, fid)


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
        self.base = os.path.realpath(tempfile.mkdtemp(prefix="corpus-regression-"))
        self.addCleanup(shutil.rmtree, self.base, True)
        self.owner = os.path.join(self.base, "owner")
        files = {".harness/team-config.yaml": "teams: {}\n",
                 ".harness/notes/n.md": "note\n",
                 ".harness/harness/features/FEAT-1-a/feature.json": record("FEAT-1-a"),
                 ".harness/harness/features/FEAT-2-b/feature.json": record("FEAT-2-b"),
                 ".harness/harness/features/FEAT-2-b/BRIEF.md": "# landed\n",
                 "src/app.py": "app\n"}
        for rel, text in files.items():
            os.makedirs(os.path.dirname(os.path.join(self.owner, rel)), exist_ok=True)
            Path(self.owner, rel).write_text(text)
        git(self.base, "init", "-q", "-b", "main", self.owner)
        git(self.owner, "add", "-A")
        git(self.owner, "commit", "-qm", "seed")

    def worktree(self, name, repair=True):
        path = os.path.join(self.owner, ".claude", "worktrees", "harness", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        git(self.owner, "worktree", "add", "-q", "-b", f"feat/{name}", path)
        if repair:
            proc = subprocess.run([sys.executable, str(BIN / "worktree-state.py"), "--repair",
                                   "--checkout", path], env=ENV, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return path

    def test_no_sibling_provider(self):
        wt = self.worktree("FEAT-1-a")
        sibling = self.worktree("FEAT-9-wip")
        Path(sibling, ".harness/harness/features/FEAT-9-wip").mkdir(parents=True)
        Path(sibling, ".harness/harness/features/FEAT-9-wip/feature.json").write_text(record("FEAT-9-wip"))
        rel = ".harness/harness/features/FEAT-9-wip/feature.json"
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
        before = tree_digest(self.owner, [os.path.join(self.owner, ".git", "index")])
        config_before = git(self.owner, "config", "--local", "--list").splitlines()
        wt = self.worktree("FEAT-1-a")
        self.assertEqual(tree_digest(self.owner, [os.path.join(self.owner, ".git", "index")]),
                         before)
        # The one shared-config write is git's own: a per-worktree sparse checkout needs
        # extensions.worktreeConfig, set once for the repository. Nothing else changes.
        added = set(git(self.owner, "config", "--local", "--list").splitlines()) - set(config_before)
        self.assertLessEqual(added, {"extensions.worktreeconfig=true"})
        links = [os.path.join(d, n) for d, dirs, files in os.walk(wt)
                 for n in dirs + files if os.path.islink(os.path.join(d, n))]
        self.assertEqual(links, [])
        self.assertEqual(sorted(os.listdir(os.path.join(wt, ".harness/harness/features"))),
                         ["FEAT-1-a"])

    def test_an_untracked_owner_directory_is_not_landed(self):
        Path(self.owner, ".harness/harness/features/FEAT-7-stale").mkdir(parents=True)
        Path(self.owner, ".harness/harness/features/FEAT-7-stale/feature.json").write_text(
            record("FEAT-7-stale"))
        wt = self.worktree("FEAT-1-a")
        self.assertEqual([e["id"] for e in fc.population(wt)], ["FEAT-1-a", "FEAT-2-b"])


if __name__ == "__main__":
    unittest.main()
