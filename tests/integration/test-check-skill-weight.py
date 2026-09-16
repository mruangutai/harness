#!/usr/bin/env python3
"""Tests for check-skill-weight.py (FEAT-60 SC-08, SC-11).

Every case builds a synthetic tree: `.omp/agents/*.md` with autoloadSkills, the skills
they name, and a `.harness/harness.json` carrying (or not) the budget. The live tree is
touched by exactly one case, which pins the two SC-11 invariants the harness relies on:
no reference is preloaded and every preload resolves.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
MODULE = os.path.join(ROOT, ".claude", "skills", "harness", "bin", "check-skill-weight.py")
sys.path.insert(0, os.path.dirname(MODULE))
import artifact_accessors

_spec = importlib.util.spec_from_file_location("check_skill_weight", MODULE)
csw = importlib.util.module_from_spec(_spec)
sys.modules["check_skill_weight"] = csw
_spec.loader.exec_module(csw)


def _tree(agents: dict[str, list[str]], skills: dict[str, int], budget=None) -> Path:
    root = Path(tempfile.mkdtemp(prefix="skill-weight-"))
    for agent, names in agents.items():
        body = "---\nname: %s\nautoloadSkills:\n%s---\n" % (
            agent, "".join(f"- {n}\n" for n in names))
        (root / ".omp" / "agents").mkdir(parents=True, exist_ok=True)
        (root / ".omp" / "agents" / f"{agent}.md").write_text(body, encoding="utf-8")
    for name, words in skills.items():
        d = root / ".claude" / "skills" / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(" ".join(["w"] * words) + "\n", encoding="utf-8")
    cfg = root / ".harness"
    cfg.mkdir()
    doc = {"budgets": {}}
    if budget is not None:
        doc["budgets"]["preload_warn_words"] = budget
    (cfg / "harness.json").write_text(json.dumps(doc), encoding="utf-8")
    return root


class WeightTests(unittest.TestCase):
    def test_counts_and_universal_set(self):
        root = _tree({"a": ["u", "x"], "b": ["u", "y"]}, {"u": 100, "x": 50, "y": 70},
                     {"universal": 1000, "agent": 1000})
        r = csw.scan(root)
        self.assertEqual(r.universal, ["u"])
        self.assertEqual(r.universal_words, 100)
        self.assertEqual(r.agent_words("a"), 150)
        self.assertEqual(r.total_words, 320)
        self.assertEqual(r.notes(), [])
        self.assertEqual(r.errors, [])
        agent = root / ".omp" / "agents" / "a.md"
        agent.write_text(
            agent.read_text(encoding="utf-8").replace(
                "autoloadSkills:\n", "autoloadSkills: []\nautoloadSkills:\n", 1),
            encoding="utf-8",
        )
        with self.assertRaises(artifact_accessors.ArtifactAccessError):
            csw._frontmatter(agent)

    def test_over_budget_is_a_note_never_an_error(self):
        root = _tree({"a": ["u", "x"], "b": ["u"]}, {"u": 100, "x": 50},
                     {"universal": 99, "agent": 120})
        r = csw.scan(root)
        self.assertEqual(r.errors, [])
        notes = r.notes()
        self.assertEqual(len(notes), 2)
        self.assertIn("universal preload is 100 words (budget 99)", notes[0])
        self.assertIn("a preloads 150 words (budget 120)", notes[1])
        self.assertEqual(csw.main([str(root)]), 0)

    def test_budget_must_come_from_harness_json(self):
        for bad in (None, 1900, {"universal": 1900}, {"universal": 0, "agent": 5},
                    {"universal": "1900", "agent": 5500}):
            root = _tree({"a": ["u"]}, {"u": 10}, bad)
            r = csw.scan(root)
            self.assertIsNone(r.budget, bad)
            self.assertEqual(len(r.notes()), 1)
            self.assertIn("UNBUDGETED", r.notes()[0])
        root = _tree({"a": ["u"]}, {"u": 10}, None)
        (root / ".harness" / "harness.json").write_text(
            '{"budgets": {}, "budgets": {}}', encoding="utf-8")
        with self.assertRaises(artifact_accessors.ArtifactAccessError):
            csw._budget(root)

    def test_missing_skill_is_an_error(self):
        root = _tree({"a": ["u", "ghost"]}, {"u": 10}, {"universal": 1, "agent": 1})
        r = csw.scan(root)
        self.assertEqual(len(r.errors), 1)
        self.assertIn("ghost", r.errors[0])
        self.assertEqual(csw.main([str(root)]), 1)

    def test_reference_named_as_preload_is_an_error(self):
        root = _tree({"a": ["u", "harness/references/team-run-state"]}, {"u": 10},
                     {"universal": 1, "agent": 1})
        r = csw.scan(root)
        self.assertEqual(len(r.errors), 1)
        self.assertIn("references/", r.errors[0])

    def test_live_tree_preloads_resolve_and_no_reference_is_preloaded(self):
        r = csw.scan(Path(ROOT))
        self.assertEqual(r.errors, [])
        self.assertEqual(len(r.agents), 16)
        self.assertEqual(set(r.universal),
                         {"harness-handoff", "harness-expertise", "harness-principles"})


if __name__ == "__main__":
    unittest.main()
