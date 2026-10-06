#!/usr/bin/env python3
"""Owner resolution, peer parity and the gates' population seam (FEAT-1559 SC-13, FEAT-58 D-02).

Each case builds a tiny real repository — the seam answers from git structure and pointer files,
so a fake would test the fake. No hook and no gate runs here; their payloads are graded in
tests/integration/test-feature-corpus.py.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude/skills/harness/bin"))
import feature_corpus as fc  # noqa: E402
import harness_boundary as hb  # noqa: E402

ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
           GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, env=ENV, check=True, capture_output=True)


def record(fid):
    return '{"feature_id": "%s", "branch": "feat/%s"}\n' % (fid, fid)


class Seam(unittest.TestCase):
    def setUp(self):
        self.base = os.path.realpath(tempfile.mkdtemp(prefix="corpus-gates-"))
        self.addCleanup(shutil.rmtree, self.base, True)
        self.owner = os.path.join(self.base, "owner")
        files = {".harness/team-config.yaml": "teams: {}\n",
                 ".harness/harness/features/FEAT-1-a/feature.json": record("FEAT-1-a"),
                 ".harness/harness/features/FEAT-2-b/feature.json": record("FEAT-2-b")}
        for rel, text in files.items():
            path = os.path.join(self.owner, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            Path(path).write_text(text)
        git(self.base, "init", "-q", "-b", "main", self.owner)
        git(self.owner, "add", "-A")
        git(self.owner, "commit", "-qm", "seed")

    def worktree(self, name):
        path = os.path.join(self.owner, ".claude", "worktrees", "harness", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        git(self.owner, "worktree", "add", "-q", "-b", f"feat/{name}", path)
        return path

    def test_linked_worktrees_is_the_same_from_the_owner_and_from_a_worktree(self):
        a, b = self.worktree("FEAT-3-c"), self.worktree("FEAT-4-d")
        from_owner = hb.linked_worktrees(self.owner)
        self.assertEqual(from_owner, sorted([a, b]))
        self.assertEqual(hb.linked_worktrees(a), from_owner)
        self.assertEqual(hb.linked_worktrees(b), from_owner)

    def test_an_unparseable_pointer_lists_nothing(self):
        broken = os.path.join(self.base, "broken")
        os.makedirs(broken)
        Path(broken, ".git").write_bytes(b"gitdir: \xff\n")
        self.assertEqual(hb.linked_worktrees(broken), [])

    def test_population_from_a_worktree_is_landed_plus_its_own(self):
        wt = self.worktree("FEAT-3-c")
        Path(wt, ".harness/harness/features/FEAT-3-c").mkdir(parents=True)
        Path(wt, ".harness/harness/features/FEAT-3-c/feature.json").write_text(record("FEAT-3-c"))
        sibling = self.worktree("FEAT-4-d")
        Path(sibling, ".harness/harness/features/FEAT-4-d").mkdir(parents=True)
        ids = [e["id"] for e in fc.population(wt)]
        self.assertEqual(ids, ["FEAT-1-a", "FEAT-2-b", "FEAT-3-c"])

    def test_this_checkouts_copy_replaces_the_landed_one(self):
        wt = self.worktree("FEAT-1-a")
        Path(wt, ".harness/harness/features/FEAT-1-a/feature.json").write_text(
            '{"feature_id": "FEAT-1-a", "branch": "feat/local-edit"}\n')
        by_id = {e["id"]: e for e in fc.population(wt)}
        self.assertEqual(by_id["FEAT-1-a"]["document"]["branch"], "feat/local-edit")
        self.assertTrue(by_id["FEAT-1-a"]["path"].startswith(wt))
        self.assertTrue(by_id["FEAT-2-b"]["path"].startswith(self.owner))

    def test_population_in_the_main_checkout_refuses_a_missing_tracked_directory(self):
        shutil.rmtree(os.path.join(self.owner, ".harness/harness/features/FEAT-2-b"))
        with self.assertRaises(fc.CorpusError) as caught:
            fc.population(self.owner)
        self.assertIn("harness/FEAT-2-b", str(caught.exception))

    def test_population_outside_git_is_whatever_is_on_disk(self):
        loose = os.path.join(self.base, "loose")
        Path(loose, ".harness/x/features/FEAT-9-z").mkdir(parents=True)
        self.assertEqual([e["id"] for e in fc.population(loose)], ["FEAT-9-z"])

    def test_layout_is_not_examined_outside_a_linked_worktree(self):
        self.assertIsNone(fc.layout_refusal(self.owner))
        self.assertIsNone(fc.layout_refusal(os.path.join(self.base)))

    def test_corpus_path_reads_another_feature_at_the_owner(self):
        wt = self.worktree("FEAT-3-c")
        rel = ".harness/harness/features/FEAT-2-b/feature.json"
        self.assertEqual(fc.corpus_path(wt, rel), os.path.join(wt, rel))     # present here
        shutil.rmtree(os.path.join(wt, ".harness/harness/features/FEAT-2-b"))  # as sparse
        self.assertEqual(fc.corpus_path(wt, rel), os.path.join(self.owner, rel))
        self.assertEqual(fc.corpus_path(self.owner, rel), os.path.join(self.owner, rel))

    def test_corpus_path_never_answers_this_checkouts_feature_from_the_owner(self):
        wt = self.worktree("FEAT-1-a")           # FEAT-1-a is materialised here
        rel = ".harness/harness/features/FEAT-1-a/feature.json"
        os.remove(os.path.join(wt, rel))
        self.assertEqual(fc.corpus_path(wt, rel), os.path.join(wt, rel))

    def test_corpus_path_leaves_non_feature_paths_local(self):
        wt = self.worktree("FEAT-3-c")
        self.assertEqual(fc.corpus_path(wt, ".harness/notes/absent.md"),
                         os.path.join(wt, ".harness/notes/absent.md"))

    def test_corpus_roots(self):
        wt = self.worktree("FEAT-3-c")
        self.assertEqual(fc.corpus_roots(wt), [wt, self.owner])
        self.assertEqual(fc.corpus_roots(self.owner), [self.owner])
        os.remove(os.path.join(self.owner, ".harness/team-config.yaml"))
        with self.assertRaises(fc.CorpusError):
            fc.corpus_roots(wt)


if __name__ == "__main__":
    unittest.main()
