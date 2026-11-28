#!/usr/bin/env python3
"""Tests for check-skill-weight.py (FEAT-60 SC-08, SC-11).

Every case builds a synthetic tree: `.omp/agents/*.md` with autoloadSkills, the skills
they name, and a `.harness/harness.json` carrying (or not) the budget. The live tree is
touched by exactly one case, which pins the two SC-11 invariants the harness relies on:
no reference is preloaded and every preload resolves.
"""
from integration_support import ROOT, BIN

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import artifact_accessors
from harness_config_support import build_config, write_config

MODULE = str(BIN / "check-skill-weight.py")

_spec = importlib.util.spec_from_file_location("check_skill_weight", MODULE)
csw = importlib.util.module_from_spec(_spec)
sys.modules["check_skill_weight"] = csw
_spec.loader.exec_module(csw)


def _tree(agents: dict[str, list[str]], skills: dict[str, int], budget=None) -> Path:
    root = Path(tempfile.mkdtemp(prefix="skill-weight-"))
    agents_dir = root / ".omp" / "agents"
    agents_dir.mkdir(parents=True)
    for agent, names in agents.items():
        body = "---\nname: %s\nautoloadSkills:\n%s---\n" % (
            agent, "".join(f"- {n}\n" for n in names))
        (agents_dir / f"{agent}.md").write_text(body, encoding="utf-8")
    for name, words in skills.items():
        d = root / ".claude" / "skills" / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(" ".join(["w"] * words) + "\n", encoding="utf-8")
    write_config(root / ".harness" / "harness.json",
                 {} if budget is None else {"budgets": {"preload_warn_words": budget}})
    return root


def _two_agent_tree() -> Path:
    """Agents a (u, x) and b (u, y); u=100, x=50, y=70 words; 1000/1000 budget."""
    return _tree({"a": ["u", "x"], "b": ["u", "y"]}, {"u": 100, "x": 50, "y": 70},
                 {"universal": 1000, "agent": 1000})


class WeightTests(unittest.TestCase):
    def test_counts_and_universal_set(self):
        root = _two_agent_tree()
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

    def test_absent_budget_uses_the_documented_defaults(self):
        root = _tree({"a": ["u"]}, {"u": 10})
        self.assertEqual(csw.scan(root).budget, {"universal": 1900, "agent": 5500})

    def test_malformed_present_budget_refuses(self):
        for bad in (1900, {"universal": 0, "agent": 5}, {"universal": "1900", "agent": 5500}):
            root = _tree({"a": ["u"]}, {"u": 10})
            config = build_config()
            config["budgets"]["preload_warn_words"] = bad
            (root / ".harness" / "harness.json").write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaises(artifact_accessors.ArtifactAccessError, msg=repr(bad)):
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

    def test_feat64_unrelated_defect_in_frontmatter_escapes(self):
        """FEAT-64 (SC-03): an unreadable/invalid frontmatter is a per-agent error row; an
        unrelated RuntimeError inside the reader escapes scan()."""
        root = _tree({"harness-a": ["s1"]}, {"s1": 10})
        with mock.patch.object(csw.artifact_accessors, "load_frontmatter",
                               side_effect=RuntimeError("unrelated")):
            with self.assertRaises(RuntimeError):
                csw.scan(root)

    def test_live_tree_preloads_resolve_and_no_reference_is_preloaded(self):
        r = csw.scan(ROOT)
        self.assertEqual(r.errors, [])
        self.assertEqual(len(r.agents), 16)
        self.assertEqual(set(r.universal),
                         {"harness-handoff", "harness-expertise", "harness-principles"})

    def test_cli_json_and_plain_modes(self):
        """BUG-2239 fold: `--json` called json.dumps with no `import json` and crashed with
        NameError; plain mode worked. Both modes run as real subprocesses on one fixture."""
        root = _two_agent_tree()
        r = subprocess.run([sys.executable, MODULE, str(root), "--json"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        doc = json.loads(r.stdout)
        self.assertEqual(doc["skills"], {"u": 100, "x": 50, "y": 70})
        self.assertEqual(doc["agents"], {"a": 150, "b": 170})
        self.assertEqual(doc["universal"], ["u"])
        self.assertEqual(doc["universal_words"], 100)
        self.assertEqual(doc["total_words"], 320)
        self.assertEqual(doc["errors"], [])
        plain = subprocess.run([sys.executable, MODULE, str(root)], capture_output=True, text=True)
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertIn("   170  b", plain.stdout)
        self.assertIn("   100  universal: u", plain.stdout)
        self.assertIn("   320  total across 2 agents", plain.stdout)


if __name__ == "__main__":
    unittest.main()
