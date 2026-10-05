#!/usr/bin/env python3
"""feature_corpus.py: landed-population discovery and on-demand branch claims (FEAT-1559 SC-04,
SC-05, SC-13).

Discovery runs against a tiny real git repository in a temporary directory — structure is read
from git, so a fake would test the fake. Branch claims are pure and take record mappings.
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

ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
           GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")


def record(fid, branch):
    return {"id": fid, "document": {"feature_id": fid, "branch": branch}}


class BranchClaims(unittest.TestCase):
    def test_one_new_duplicate_is_one_finding_naming_both(self):
        found = fc.branch_collisions([record("FEAT-7-a", "feat/x"), record("FEAT-8-b", "feat/x"),
                                      record("FEAT-9-c", "feat/y")])
        self.assertEqual(found, [("feat/x", ["FEAT-7-a", "FEAT-8-b"])])

    def test_sentinels_claim_nothing(self):
        entries = [record("A", "none"), record("B", "none"), record("C", ""), record("D", ""),
                   {"id": "E", "document": {"feature_id": "E"}}, {"id": "F", "document": None},
                   record("G", "  none  ")]
        self.assertEqual(fc.branch_collisions(entries), [])

    def test_exact_era_pair_is_exempt(self):
        pair = [record("FEAT-02", "feat/harness-native-foundation"),
                record("FEAT-03-subissue-mirror", "feat/harness-native-foundation")]
        self.assertEqual(fc.branch_collisions(pair), [])

    def test_a_third_claimant_defeats_the_exemption(self):
        trio = [record("FEAT-02", "feat/harness-native-foundation"),
                record("FEAT-03-subissue-mirror", "feat/harness-native-foundation"),
                record("FEAT-77-late", "feat/harness-native-foundation")]
        self.assertEqual(fc.branch_collisions(trio),
                         [("feat/harness-native-foundation",
                           ["FEAT-02", "FEAT-03-subissue-mirror", "FEAT-77-late"])])

    def test_an_empty_reason_defeats_the_exemption(self):
        pair = [record("FEAT-02", "feat/harness-native-foundation"),
                record("FEAT-03-subissue-mirror", "feat/harness-native-foundation")]
        emptied = {frozenset({"FEAT-02", "FEAT-03-subissue-mirror"}): "  "}
        self.assertEqual(len(fc.branch_collisions(pair, exempt=emptied)), 1)

    def test_the_shipped_exemption_carries_a_reason(self):
        reason = fc.BRANCH_ERA_EXEMPT[frozenset({"FEAT-02", "FEAT-03-subissue-mirror"})]
        self.assertTrue(reason.strip())
        self.assertEqual(len(fc.BRANCH_ERA_EXEMPT), 1)


class LandedDiscovery(unittest.TestCase):
    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="feature-corpus-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        files = {
            ".harness/team-config.yaml": "teams: {}\n",
            ".harness/harness/features/FEAT-1-a/feature.json":
                '{"feature_id": "FEAT-1-a", "branch": "feat/FEAT-1-a"}\n',
            ".harness/harness/features/BUG-2-b/notes/deep/n.md": "record-less\n",
            ".harness/kaya/features/FEAT-3-c/feature.json": "{not json\n",
        }
        for rel, text in files.items():
            path = os.path.join(self.root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            Path(path).write_text(text)
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "seed"]):
            subprocess.run(["git", *args], cwd=self.root, env=ENV, check=True,
                           capture_output=True)

    def test_population_is_every_tracked_directory_by_name(self):
        names = [f"{s}/{i}" for s, i, _p in fc.landed_dirs(self.root)]
        self.assertEqual(names, ["harness/BUG-2-b", "harness/FEAT-1-a", "kaya/FEAT-3-c"])

    def test_a_missing_tracked_directory_refuses_with_counts_and_name(self):
        shutil.rmtree(os.path.join(self.root, ".harness/harness/features/BUG-2-b"))
        with self.assertRaises(fc.CorpusError) as caught:
            fc.landed_dirs(self.root)
        self.assertIn("reaches 2 of 3", str(caught.exception))
        self.assertIn("harness/BUG-2-b", str(caught.exception))

    def test_untracked_directory_is_not_landed(self):
        os.makedirs(os.path.join(self.root, ".harness/harness/features/FEAT-9-wip"))
        names = [i for _s, i, _p in fc.landed_dirs(self.root)]
        self.assertNotIn("FEAT-9-wip", names)

    def test_records_keep_recordless_and_unparseable_directories(self):
        by_id = {e["id"]: e for e in fc.records(self.root)}
        self.assertEqual(by_id["FEAT-1-a"]["document"]["branch"], "feat/FEAT-1-a")
        self.assertIsNone(by_id["BUG-2-b"]["record"])
        self.assertIsNone(by_id["BUG-2-b"]["error"])
        self.assertIsNotNone(by_id["FEAT-3-c"]["error"])

    def test_owner_root_of_a_non_checkout_refuses(self):
        outside = os.path.realpath(tempfile.mkdtemp(prefix="feature-corpus-outside-"))
        self.addCleanup(shutil.rmtree, outside, True)
        with self.assertRaises(fc.CorpusError):
            fc.owner_root(outside)

    def test_owner_root_of_an_unparseable_pointer_refuses(self):
        broken = os.path.join(self.root, "broken")
        os.makedirs(broken)
        Path(broken, ".git").write_bytes(b"gitdir: \xff\n")
        with self.assertRaises(fc.CorpusError):
            fc.owner_root(broken)

    def test_an_unborn_head_has_landed_nothing(self):
        fresh = os.path.realpath(tempfile.mkdtemp(prefix="feature-corpus-unborn-"))
        self.addCleanup(shutil.rmtree, fresh, True)
        subprocess.run(["git", "init", "-q"], cwd=fresh, env=ENV, check=True)
        os.makedirs(os.path.join(fresh, ".harness/harness/features/FEAT-1-a"))
        self.assertEqual(fc.landed_dirs(fresh), [])

    def test_compare_names(self):
        self.assertEqual(fc.compare_names(["a/1", "a/2"], ["a/2", "a/3"]), (["a/1"], ["a/3"]))


if __name__ == "__main__":
    unittest.main()
