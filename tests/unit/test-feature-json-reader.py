#!/usr/bin/env python3
"""Contract tests for the public feature.json accessor (BUG-285).

The load implementation remains inward in feature_json_write.py through T-07. These tests
exercise it only through artifact_accessors, covering absence-vs-corruption, strict JSON,
top-level shape, and recorded GitHub/factory issue fields.
"""
from pathlib import Path
import json
import os
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
import artifact_accessors as accessors  # noqa: E402
import feature_json_write  # noqa: E402


def _write(dirpath, data_bytes):
    path = os.path.join(dirpath, "feature.json")
    with open(path, "wb") as f:
        f.write(data_bytes)
    return path


class LoadFeatureJsonTest(unittest.TestCase):
    def test_absent_file_returns_none(self):
        """Row 1: a legitimate first sync/first publish -- never an error."""
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "feature.json")
            self.assertIsNone(accessors.load_feature_json(path))

    def test_empty_file_raises_not_returns_empty(self):
        """Row 2: a 0-byte file is the truncating-write window FEAT-14 was about -- it must
        raise, distinguishable from the absent-file None above, never silently collapse to
        the same answer."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"")
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(path)

    def test_unparseable_json_raises(self):
        """Row 3."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"{ not: valid json [[[")
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(path)

    def test_non_utf8_bytes_raise_not_traceback(self):
        """Row 4: gh-sync.py's OLD reader let this escape its `except OSError` as a bare
        UnicodeDecodeError traceback -- the read is inside THIS function's own try, so it
        cannot happen here."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"\xff\xfe\x00\x01")
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(path)

    def test_top_level_list_raises(self):
        """Row 5."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"[1, 2]")
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(path)

    def test_top_level_scalar_string_raises(self):
        """Row 6."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b'"x"')
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(path)

    def test_top_level_scalar_int_raises(self):
        """Row 7."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"3")
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(path)

    def test_block_key_absent_returns_the_mapping(self):
        """Row 8: a mapping present with nothing recorded yet is a legitimate document --
        load_feature_json returns it unchanged; deciding that no `github`/`factory` key
        means a first sync is each reader's own job, not this accessor's."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, json.dumps({"feature_id": "F1"}).encode())
            self.assertEqual({"feature_id": "F1"}, accessors.load_feature_json(path))

    def test_block_key_present_not_a_mapping_still_returns(self):
        """A present block without recorded parent or issues fields remains raw metadata."""
        with tempfile.TemporaryDirectory() as td:
            doc = {"github": "x", "factory": "x"}
            path = _write(td, json.dumps(doc).encode())
            self.assertEqual(doc, accessors.load_feature_json(path))

    def test_wrong_typed_members_raise(self):
        """Present recorded parent and issues fields are shared-boundary corruption."""
        with tempfile.TemporaryDirectory() as td:
            doc = {"github": {"parent": "7", "issues": "nope"}}
            path = _write(td, json.dumps(doc).encode())
            with self.assertRaises(Exception):
                accessors.load_feature_json(path)

    def test_duplicate_top_level_keys_raise(self):
        """Row 11: json.load's own default for a repeated key is silent last-wins --
        object_pairs_hook must reject it, or the migration WEAKENS strictness relative to
        harness_yaml's DuplicateKeyError while claiming to tighten it."""
        with tempfile.TemporaryDirectory() as td:
            text = ('{"github": {"parent": 1}, "feature_id": "F1", '
                    '"github": {"parent": 2}}').encode()
            path = _write(td, text)
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(path)

    def test_duplicate_nested_keys_raise(self):
        """A repeated key one level below the top -- DuplicateKeyError's own contract is
        "at any nesting depth", and this migration must match it there too."""
        with tempfile.TemporaryDirectory() as td:
            text = '{"github": {"parent": 1, "parent": 2}}'.encode()
            path = _write(td, text)
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(path)

    def test_yaml_only_document_raises(self):
        """Row 12: a document no JSON writer produces and no JSON reader accepts -- the
        parser-choice divergence this migration closes by accepting ONLY JSON. Was, under
        the old harness_yaml-based load_factory, RETURNED populated; must now raise."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"github:\n  parent: 40\n  milestone: 7\n")
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(path)

    def test_valid_well_formed_document_returns_it(self):
        """Row 13, the control: a normal write_feature_json/write_factory document loads
        cleanly, proving this accessor distinguishes a well-formed read from a broken one."""
        with tempfile.TemporaryDirectory() as td:
            doc = {"feature_id": "F1",
                   "github": {"parent": 40, "milestone": 7, "issues": {"T-01": 41}}}
            path = _write(td, json.dumps(doc).encode())
            self.assertEqual(doc, accessors.load_feature_json(path))

    def test_absent_and_malformed_are_distinguishable(self):
        """The core defect this migration closes (property 5): absent must never be
        indistinguishable from present-but-corrupt to a caller."""
        with tempfile.TemporaryDirectory() as td:
            absent_path = os.path.join(td, "feature.json")
            self.assertIsNone(accessors.load_feature_json(absent_path))
            corrupt_path = _write(td, b"")
            with self.assertRaises(accessors.FeatureJsonError):
                accessors.load_feature_json(corrupt_path)

    def test_nonfinite_constants_raise(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant), tempfile.TemporaryDirectory() as td:
                path = _write(td, f'{{"github": {{"parent": {constant}}}}}'.encode())
                with self.assertRaises(accessors.FeatureJsonError):
                    accessors.load_feature_json(path)

    def test_text_source_matches_path_validation(self):
        document = {"feature_id": "F1", "github": {"issues": {"T-01": "8"}}}
        self.assertEqual(
            document,
            accessors.load_feature_json(
                text=json.dumps(document), context="git show main:feature.json"
            ),
        )
        failures = (
            ('{"outer": {"inner": {"key": 1, "key": 2}}}', "duplicate key"),
            ("NaN", "non-finite JSON constant"),
            ("Infinity", "non-finite JSON constant"),
            ("-Infinity", "non-finite JSON constant"),
            ("[1, 2]", "not a JSON mapping"),
            ('{"github": {"issues": []}}', "issues"),
        )
        for text, expected in failures:
            with self.subTest(text=text):
                with self.assertRaisesRegex(
                    accessors.FeatureJsonError, expected
                ) as caught:
                    accessors.load_feature_json(
                        text=text, context="git show main:feature.json"
                    )
                self.assertIn("git show main:feature.json", str(caught.exception))

    def test_exactly_one_source_is_required(self):
        with self.assertRaises(accessors.FeatureJsonError):
            accessors.load_feature_json()
        with self.assertRaises(accessors.FeatureJsonError):
            accessors.load_feature_json(
                "feature.json", text='{"feature_id": "F1"}',
                context="git show main:feature.json",
            )


class OptIntTest(unittest.TestCase):
    """opt_int now lives in feature_json_write.py, the one shared copy gh-sync.py's three
    call sites use (BUG-285 property 7); factory_decompose.py's load_factory keeps its own
    strict isinstance guard on purpose, unaffected by this move."""

    def test_quoted_digit_string_coerces(self):
        self.assertEqual(7, feature_json_write.opt_int("7"))

    def test_bool_excluded_despite_int_subclass(self):
        self.assertIsNone(feature_json_write.opt_int(True))
        self.assertIsNone(feature_json_write.opt_int(False))

    def test_none_and_junk_are_none(self):
        self.assertIsNone(feature_json_write.opt_int(None))
        self.assertIsNone(feature_json_write.opt_int("nope"))

    def test_real_int_passes_through(self):
        self.assertEqual(41, feature_json_write.opt_int(41))




if __name__ == "__main__":
    unittest.main()
