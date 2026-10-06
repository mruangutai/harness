#!/usr/bin/env python3
"""Pure rules behind worktree-state.py (FEAT-1559 SC-01, SC-07, SC-13).

No git and no filesystem: each case hands the rule a list of tracked directories or a name and
checks what it derives. The cone derivation is the rule a wrong answer from which strips a
directory every dispatch needs while git reports success (FEAT-58 D-08), so every part of it has
a case that would catch that.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(BIN))
import feature_corpus as fc  # noqa: E402

_spec = importlib.util.spec_from_file_location("worktree_state", BIN / "worktree-state.py")
ws = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ws)

DIRS = [
    ".agents", ".agents/skills", ".claude", ".claude/skills", "src",
    ".harness", ".harness/expertise", ".harness/factory", ".harness/notes",
    ".harness/harness", ".harness/harness/docs", ".harness/harness/expertise",
    ".harness/harness/features", ".harness/harness/features/FEAT-1-alpha",
    ".harness/harness/features/FEAT-1-alpha/notes", ".harness/harness/features/FEAT-2-beta",
    ".harness/kaya", ".harness/kaya/expertise", ".harness/kaya/features",
    ".harness/kaya/features/FEAT-10-kaya-app",
]


class DeriveCone(unittest.TestCase):
    def cone(self, dirs=DIRS, active=(".harness/harness/features/FEAT-1-alpha",)):
        return fc.derive_cone(dirs, list(active))

    def test_top_level_directories_except_harness(self):
        cone = self.cone()
        for top in (".agents", ".claude", "src"):
            self.assertIn(top, cone)
        self.assertNotIn(".harness", cone)

    def test_new_tracked_top_level_directory_joins_without_an_edit(self):
        self.assertNotIn("newtop", self.cone())
        self.assertIn("newtop", self.cone(DIRS + ["newtop"]))

    def test_maximal_non_feature_harness_subtrees_only(self):
        cone = self.cone()
        for keep in (".harness/expertise", ".harness/factory", ".harness/notes",
                     ".harness/harness/docs", ".harness/harness/expertise",
                     ".harness/kaya/expertise"):
            self.assertIn(keep, cone)
        # Ancestors of a features root and anything beneath one are never listed whole.
        for never in (".harness/harness", ".harness/kaya", ".harness/harness/features",
                      ".harness/harness/features/FEAT-2-beta",
                      ".harness/kaya/features/FEAT-10-kaya-app"):
            self.assertNotIn(never, cone)
        self.assertNotIn(".agents/skills", cone)      # covered by .agents; not maximal

    def test_active_directory_added_exactly(self):
        cone = self.cone(active=[".harness/kaya/features/FEAT-10-kaya-app"])
        self.assertIn(".harness/kaya/features/FEAT-10-kaya-app", cone)
        self.assertNotIn(".harness/harness/features/FEAT-1-alpha", cone)


class InCone(unittest.TestCase):
    CONE = [".agents", ".harness/notes", ".harness/harness/features/FEAT-1-alpha"]

    def test_membership(self):
        cases = {
            "README.md": True,                                      # top-level file
            ".agents/skills/x/SKILL.md": True,                      # under a listed dir
            ".harness/team-config.yaml": True,                      # directly in an ancestor
            ".harness/harness/feature-index.md": True,              # directly in an ancestor
            ".harness/harness/features/FEAT-1-alpha/BRIEF.md": True,
            ".harness/harness/features/FEAT-2-beta/BRIEF.md": False,
            ".harness/harness/docs/DECISIONS.md": False,            # not listed here
            "src/app.py": False,
        }
        for path, expected in cases.items():
            self.assertEqual(fc.in_cone(path, self.CONE), expected, path)


class Identity(unittest.TestCase):
    def test_pin_name(self):
        self.assertEqual(fc.parse_pin("FEAT-2-beta--run1--qa"), "FEAT-2-beta")
        for bad in ("FEAT-2-beta--run1", "FEAT-2-beta--run1--qa--x", "notes--run1--qa",
                    "FEAT-2-beta----qa"):
            self.assertIsNone(fc.parse_pin(bad), bad)

    def test_pin_identity_refuses_an_underivable_name(self):
        fid, refusal = fc.identity(fc.PIN, "whatever", None)
        self.assertIsNone(fid)
        self.assertIn("cannot be derived", refusal)

    def test_planning_identity_from_name_or_branch(self):
        self.assertEqual(fc.identity(fc.PLANNING, "FEAT-9-x", "feat/FEAT-9-x"), ("FEAT-9-x", None))
        self.assertEqual(fc.identity(fc.PLANNING, "FEAT-9-x", None), ("FEAT-9-x", None))
        self.assertEqual(fc.identity(fc.PLANNING, "scratch", "feat/BUG-4-y"), ("BUG-4-y", None))

    def test_planning_identity_absent_is_not_a_refusal(self):
        self.assertEqual(fc.identity(fc.PLANNING, "test-speed", "chore/test-speed"), (None, None))

    def test_name_and_branch_disagreeing_refuses(self):
        fid, refusal = fc.identity(fc.PLANNING, "FEAT-9-x", "feat/FEAT-8-y")
        self.assertIsNone(fid)
        self.assertIn("ambiguous", refusal)


class ActivePaths(unittest.TestCase):
    def test_existing_record_selects_its_own_segment_not_the_worktree_segment(self):
        paths, segment, refusal, _every = fc.active_paths("FEAT-10-kaya-app", DIRS, [])
        self.assertEqual((paths, segment, refusal),
                         ([".harness/kaya/features/FEAT-10-kaya-app"], "kaya", None))

    def test_recordless_id_is_included_in_every_segment(self):
        paths, segment, refusal, every = fc.active_paths("FEAT-99-new", DIRS, [])
        expected = [".harness/harness/features/FEAT-99-new", ".harness/kaya/features/FEAT-99-new"]
        self.assertEqual((paths, segment, refusal), (expected, None, None))
        self.assertEqual(every, expected)

    def test_two_claiming_segments_refuse(self):
        dirs = DIRS + [".harness/kaya/features/FEAT-1-alpha"]
        paths, segment, refusal, _every = fc.active_paths("FEAT-1-alpha", dirs, [])
        self.assertEqual((paths, segment), ([], None))
        self.assertIn("harness, kaya", refusal)


class ExitPriority(unittest.TestCase):
    def test_dirty_then_cone_then_skip_bits_then_materialisation(self):
        def codes(*cs):
            return ws.exit_code([ws.finding(c, [], "x") for c in cs])
        self.assertEqual(codes(), 0)
        self.assertEqual(codes(7, 4, 3, 8), 8)
        self.assertEqual(codes(7, 4, 3), 3)
        self.assertEqual(codes(7, 4), 4)
        self.assertEqual(codes(7), 7)

    def test_labels_and_codes(self):
        self.assertEqual(ws.LABELS, {8: "dirty", 3: "cone", 4: "skip-bits", 7: "materialisation"})
        self.assertNotIn(5, ws.LABELS)          # FEAT-58's symlink exits do not exist here
        self.assertNotIn(6, ws.LABELS)


if __name__ == "__main__":
    unittest.main()
