#!/usr/bin/env python3
"""Focused path-security tests for the manual handoff comprehension probe."""

from __future__ import annotations

import importlib.util
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "manual" / "probe-handoff-comprehension.py"


def load_probe():
    spec = importlib.util.spec_from_file_location("probe_handoff_comprehension", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProbePathSecurityTest(unittest.TestCase):
    def setUp(self):
        self.root_tmp = tempfile.TemporaryDirectory()
        self.outside_tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.root_tmp.name)
        self.notes = self.root / ".harness/harness/features/FEAT-test/notes"
        self.notes.mkdir(parents=True)
        self.valid = self.notes / "handoff-valid.md"
        self.valid.write_text("# Handoff\n\n## Done when\nScope: safe\n", encoding="utf-8")
        self.probe = load_probe()
        self.probe.ROOT = self.root
        self.calls = []
        self.probe.ask = self.record_call

    def tearDown(self):
        self.root_tmp.cleanup()
        self.outside_tmp.cleanup()

    def record_call(self, omp, model, note):
        self.calls.append((omp, model, note))
        return "safe", ""

    def exercise(self, requested):
        with mock.patch.object(self.probe.shutil, "which", return_value="/bin/omp"):
            self.probe.run(self.probe.note_paths(requested), "test-model")

    def assert_refused_without_model_call(self, path):
        self.exercise([path])
        self.assertEqual([], self.calls)

    def test_explicit_repository_outside_absolute_and_traversal_are_refused(self):
        repository_outside = self.root / "handoff-repository-outside.md"
        repository_outside.write_text(self.valid.read_text(encoding="utf-8"), encoding="utf-8")
        absolute_outside = Path(self.outside_tmp.name) / "handoff-absolute-outside.md"
        absolute_outside.write_text(self.valid.read_text(encoding="utf-8"), encoding="utf-8")
        traversal_target = self.root / "outside" / "handoff-traversal.md"
        traversal_target.parent.mkdir()
        traversal_target.write_text(self.valid.read_text(encoding="utf-8"), encoding="utf-8")
        traversal = Path(
            ".harness/harness/features/FEAT-test/notes/../../../../../outside/handoff-traversal.md"
        )

        self.assert_refused_without_model_call(repository_outside)
        self.assert_refused_without_model_call(absolute_outside)
        self.assert_refused_without_model_call(traversal)

    def test_repository_contained_symlink_is_refused_for_explicit_and_default_selection(self):
        link = self.notes / "handoff-link.md"
        link.symlink_to(self.valid.name)

        self.assert_refused_without_model_call(link)
        self.calls.clear()
        self.valid.unlink()
        self.exercise([])
        self.assertEqual([], self.calls)

    def test_non_regular_input_is_refused(self):
        directory = self.notes / "handoff-directory.md"
        directory.mkdir()
        self.assert_refused_without_model_call(directory)

    def test_wrong_basename_and_oversized_note_are_refused(self):
        wrong_name = self.notes / "not-a-handoff.md"
        wrong_name.write_text(self.valid.read_text(encoding="utf-8"), encoding="utf-8")
        oversized = self.notes / "handoff-oversized.md"
        oversized.write_bytes(b"x" * (self.probe.MAX_NOTE_BYTES + 1))

        self.assert_refused_without_model_call(wrong_name)
        self.assert_refused_without_model_call(oversized)

    def test_valid_handoff_reaches_both_measurement_arms(self):
        self.exercise([self.valid])
        self.assertEqual(2, len(self.calls))

    def test_ask_disables_tools_without_auto_approval(self):
        probe = load_probe()
        probe.ROOT = self.root
        completed = types.SimpleNamespace(returncode=0, stdout="answer\n", stderr="")
        with mock.patch.object(probe.subprocess, "run", return_value=completed) as run:
            self.assertEqual(("answer", ""), probe.ask("/bin/omp", "test-model", "note"))

        argv = run.call_args.args[0]
        self.assertEqual(1, argv.count("--no-tools"))
        self.assertNotIn("--auto-approve", argv)

    def test_dry_run_makes_no_model_call(self):
        args = types.SimpleNamespace(notes=[self.valid], dry_run=True, model="test-model")
        with mock.patch.object(self.probe, "arguments", return_value=args):
            self.assertEqual(0, self.probe.main())
        self.assertEqual([], self.calls)


if __name__ == "__main__":
    unittest.main()
