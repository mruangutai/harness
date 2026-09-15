#!/usr/bin/env python3
"""Contract tests for the public artifact accessor seam."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
import artifact_accessors as accessors  # noqa: E402


class JsonContracts(unittest.TestCase):
    def test_nonfinite_json_constants_are_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "harness.json"
                path.write_text('{"value": ' + value + '}', encoding="utf-8")
                with self.assertRaises(accessors.ArtifactAccessError):
                    accessors.load_harness_json(path)

    def test_in_memory_json_retains_caller_context(self):
        with self.assertRaises(accessors.ArtifactAccessError) as caught:
            accessors.parse_gh_json('{"value": NaN}', "gh issue view acme/widget")
        self.assertIn("gh issue view acme/widget", str(caught.exception))



    def test_feature_json_rejects_malformed_recorded_blocks(self):
        invalid_blocks = (
            {"github": {"parent": True}},
            {"github": {"issues": []}},
            {"factory": {"parent": "not-a-number"}},
            {"factory": {"issues": []}},
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feature.json"
            for block in invalid_blocks:
                with self.subTest(block=block):
                    path.write_text(json.dumps(block), encoding="utf-8")
                    with self.assertRaisesRegex(Exception, "recorded issue number|issues"):
                        accessors.load_feature_json(path)

    def test_feature_json_preserves_absent_blocks_and_numeric_strings(self):
        document = {
            "feature_id": "F1",
            "github": {"parent": "7", "issues": {"T-01": "8"}},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feature.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            self.assertEqual(document, accessors.load_feature_json(path))
class YamlContracts(unittest.TestCase):
    def test_frontmatter_rejects_duplicate_yaml_keys(self):
        with self.assertRaises(accessors.ArtifactAccessError):
            accessors.load_frontmatter("---\nname: one\nname: two\n---\nbody", "agent.md")

    def test_omp_config_accepts_both_yaml_extensions(self):
        with tempfile.TemporaryDirectory() as directory:
            for suffix in (".yml", ".yaml"):
                path = Path(directory) / ("config" + suffix)
                path.write_text("name: omp\n", encoding="utf-8")
                self.assertEqual({"name": "omp"}, accessors.load_omp_config(path))


class WriterContract(unittest.TestCase):
    def test_writer_makes_backup_and_writes_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "harness.json"
            path.write_text('{"schema_version": 1}\n', encoding="utf-8")
            accessors.write_harness_json(path, {"schema_version": 2})
            self.assertEqual({"schema_version": 2}, json.loads(path.read_text(encoding="utf-8")))
            self.assertEqual('{"schema_version": 1}\n', path.with_name("harness.json.harness-bak").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
