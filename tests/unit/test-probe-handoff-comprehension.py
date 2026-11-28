#!/usr/bin/env python3
"""Focused path-security tests for the manual handoff comprehension probe."""

from __future__ import annotations

from unit_support import TESTS

import contextlib
import importlib.util
import io
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = TESTS / "manual" / "probe-handoff-comprehension.py"
NOTE = "# Handoff\n\n## Done when\nScope: safe\n"


def load_probe():
    spec = importlib.util.spec_from_file_location("probe_handoff_comprehension", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def temp_dir(test: unittest.TestCase) -> Path:
    tmp = tempfile.TemporaryDirectory()
    test.addCleanup(tmp.cleanup)
    return Path(tmp.name)


class ProbePathSecurityTest(unittest.TestCase):
    def setUp(self):
        self.root = temp_dir(self)
        self.notes = self.root / ".harness/harness/features/FEAT-test/notes"
        self.notes.mkdir(parents=True)
        self.valid = self.notes / "handoff-valid.md"
        self.valid.write_text(NOTE, encoding="utf-8")
        self.probe = load_probe()
        self.probe.ROOT = self.root
        self.real_ask = self.probe.ask
        patcher = mock.patch.object(self.probe, "ask", return_value=("safe", ""))
        self.ask = patcher.start()
        self.addCleanup(patcher.stop)

    def exercise(self, requested):
        self.probe.run(self.probe.note_paths(requested), "test-model")

    def assert_refused_without_model_call(self, path):
        self.exercise([path])
        self.assertEqual(0, self.ask.call_count)

    def test_explicit_repository_outside_absolute_and_traversal_are_refused(self):
        repository_outside = self.root / "handoff-repository-outside.md"
        repository_outside.write_text(NOTE, encoding="utf-8")
        absolute_outside = temp_dir(self) / "handoff-absolute-outside.md"
        absolute_outside.write_text(NOTE, encoding="utf-8")
        traversal_target = self.root / "outside" / "handoff-traversal.md"
        traversal_target.parent.mkdir()
        traversal_target.write_text(NOTE, encoding="utf-8")
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
        self.ask.reset_mock()
        self.valid.unlink()
        self.exercise([])
        self.assertEqual(0, self.ask.call_count)

    def test_non_regular_input_is_refused(self):
        directory = self.notes / "handoff-directory.md"
        directory.mkdir()
        self.assert_refused_without_model_call(directory)

    def test_wrong_basename_and_oversized_note_are_refused(self):
        wrong_name = self.notes / "not-a-handoff.md"
        wrong_name.write_text(NOTE, encoding="utf-8")
        oversized = self.notes / "handoff-oversized.md"
        oversized.write_bytes(b"x" * (self.probe.MAX_NOTE_BYTES + 1))

        self.assert_refused_without_model_call(wrong_name)
        self.assert_refused_without_model_call(oversized)

    def test_valid_handoff_reaches_both_measurement_arms(self):
        self.exercise([self.valid])
        self.assertEqual(2, self.ask.call_count)

    def test_ask_disables_tools_without_auto_approval(self):
        completed = types.SimpleNamespace(returncode=0, stdout="answer\n", stderr="")
        with mock.patch.object(self.probe.subprocess, "run", return_value=completed) as run:
            self.assertEqual(("answer", ""), self.real_ask("/bin/omp", "test-model", "note"))

        argv = run.call_args.args[0]
        self.assertEqual(1, argv.count("--no-tools"))
        self.assertNotIn("--auto-approve", argv)

    def test_dry_run_makes_no_model_call(self):
        args = types.SimpleNamespace(notes=[self.valid], dry_run=True, model="test-model")
        with mock.patch.object(self.probe, "arguments", return_value=args):
            self.assertEqual(0, self.probe.main())
        self.assertEqual(0, self.ask.call_count)

    def test_control_bytes_are_escaped_before_printing(self):
        """SEC-F-08: neither producer's control bytes may reach the terminal raw."""
        crafted = "scope\x1b[2Jcleared\x1b]0;title\x07\x00\x7f"
        got = self.probe.safe(crafted)
        for byte in ("\x1b", "\x07", "\x00", "\x7f"):
            self.assertNotIn(byte, got)
        self.assertIn("\\x1b", got)

    def test_newline_and_tab_survive_scrubbing(self):
        """A model answer is multi-line; mangling it would defeat the measurement."""
        self.assertEqual("a\nb\tc", self.probe.safe("a\nb\tc"))

    def test_every_untrusted_sink_is_scrubbed(self):
        """A crafted fact and a crafted answer both reach the terminal escaped."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.probe.measure_arm("as-written", "note", ["fact\x1b[2J"],
                                   "/bin/omp", "test-model")
        self.assertIn("fact", out.getvalue())
        self.assertNotIn("\x1b", out.getvalue())


if __name__ == "__main__":
    unittest.main()
