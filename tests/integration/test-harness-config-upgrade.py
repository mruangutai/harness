#!/usr/bin/env python3
"""FEAT-2297 D-05: upgrade-config.py migrates harness.json 2 -> 3 through the real CLI.

Every project starts as a valid built config and is then explicitly aged: schema_version set to 2
and kind statuses removed, which is the version-2 shape. Templates are the shipped ones.
"""
from integration_support import BIN
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness_config_support import EXCLUDED_KIND as EXCLUDED, build_config
import artifact_accessors as accessors

SCRIPT = BIN / "upgrade-config.py"
TEMPLATES = BIN.parent / "templates"


def version_two(overrides=None):
    """A valid config aged to the version-2 shape: no kind carries a status."""
    document = build_config(overrides)
    document["schema_version"] = 2
    for kind in document["test_kinds"].values():
        if kind["status"] != "excluded":
            del kind["status"]
    return document


class Upgrade(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / ".harness").mkdir()
        self.config = self.root / ".harness" / "harness.json"
        self.backup = self.root / ".harness" / "harness.json.harness-bak"

    def write(self, document):
        self.config.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        return self.config.read_bytes()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.root), "--templates", str(TEMPLATES),
                               *args], capture_output=True, text=True)

    def assert_refused(self, result, needle, original):
        """Exit 1 without a traceback, needle reported, the source left as it was, and no backup."""
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn(needle, result.stdout)
        self.assertEqual(original, self.config.read_bytes() if self.config.exists() else None)
        self.assertFalse(self.backup.exists())

    def product(self):
        return version_two({
            "panel_era_start": "2026-01-02",
            "test_kinds": {"unit": {"detect": "t/**", "exclude": "", "cmd": "make test", "status": "active"},
                           "integration": {"detect": "i/**", "exclude": "", "cmd": None,
                                           "status": "active"},
                           "eval": EXCLUDED}})

    def test_config_only_migrates_a_product_without_touching_a_manifest(self):
        original = self.write(self.product())
        result = self.run_cli("--config-only")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        upgraded = accessors.load_harness_json(self.config)
        kinds = upgraded["test_kinds"]
        self.assertEqual(3, upgraded["schema_version"])
        self.assertEqual(("make test", "active"), (kinds["unit"]["cmd"], kinds["unit"]["status"]))
        self.assertEqual("unresolved", kinds["integration"]["status"])
        self.assertEqual(EXCLUDED, kinds["eval"])
        self.assertEqual("2026-01-02", upgraded["panel_era_start"])
        self.assertEqual(original, self.backup.read_bytes())
        self.assertFalse((self.root / ".harness" / "team-config.yaml").exists())
        self.assertNotIn("team-config", result.stdout)

    def test_repeat_is_idempotent(self):
        self.write(self.product())
        self.run_cli("--config-only")
        upgraded, backup = self.config.read_bytes(), self.backup.read_bytes()
        again = self.run_cli("--config-only")
        self.assertEqual(0, again.returncode, again.stdout + again.stderr)
        self.assertIn("up to date (schema_version 3)", again.stdout)
        self.assertEqual((upgraded, backup), (self.config.read_bytes(), self.backup.read_bytes()))

    def test_check_reports_the_gap_and_writes_nothing(self):
        original = self.write(self.product())
        result = self.run_cli("--check", "--config-only")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("schema_version 2 -> 3", result.stdout)
        self.assertIn("test_kinds.unit.status = active", result.stdout)
        self.assertEqual(original, self.config.read_bytes())
        self.assertFalse(self.backup.exists())

    def test_an_invalid_candidate_is_never_written(self):
        for name, corrupt, needle in (
                ("wrong present value", lambda d: d["gates"].update(review="strict"), "gates.review"),
                ("newer version", lambda d: d.update(schema_version=4), "schema_version")):
            with self.subTest(name):
                document = self.product()
                corrupt(document)
                original = self.write(document)
                self.assert_refused(self.run_cli("--config-only"), needle, original)

    def test_a_missing_or_unparseable_source_is_diagnosed_and_nothing_is_written(self):
        for name, source, needle in (("missing", None, "harness.json"),
                                     ("unparseable", '{"schema_version": 2,', "cannot read config")):
            with self.subTest(name):
                self.config.unlink(missing_ok=True)
                if source is not None:
                    self.config.write_text(source, encoding="utf-8")
                original = None if source is None else source.encode("utf-8")
                self.assert_refused(self.run_cli("--config-only"), needle, original)

    def test_control_plane_upgrade_still_reports_its_manifest(self):
        self.write(self.product())
        (self.root / ".harness" / "team-config.yaml").write_text("schema_version: 1\nteams: []\n")
        result = self.run_cli()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("team-config.yaml: schema_version 1 ->", result.stdout)
        self.assertIn("MANUAL STEP REQUIRED", result.stdout)
        self.assertEqual(3, accessors.load_harness_json(self.config)["schema_version"])


if __name__ == "__main__":
    unittest.main()
