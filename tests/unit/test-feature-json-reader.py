#!/usr/bin/env python3
"""Tests for feature_json_write.load_feature_json (BUG-285) -- the one canonical reader for
feature.json, replacing the two independent parsers gh-sync.py's load_recorded and
factory_decompose.py's load_factory used to run for themselves. Exercises the accessor
directly against all 13 input classes measured in
`.harness/harness/features/BUG-285-yaml-loader-pin/notes/research-BUG-285-parity-survey.md`,
plus a structural check that neither reader parses feature.json independently any more --
that is what keeps this ONE implementation rather than two that happen to agree today.

Rows about a specific FIELD inside the parsed document (a `github`/`factory` block present
but wrong-typed, or a member coerced) are each reader's own business, not this accessor's --
those stay covered by gh-sync.py's and factory_decompose.py's own suites. This file tests
only the raw read/parse/shape layer load_feature_json owns: absent-vs-malformed, JSON
validity, duplicate keys, and top-level mapping shape.
"""
from pathlib import Path
import ast
import json
import os
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
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
            self.assertIsNone(feature_json_write.load_feature_json(path))

    def test_empty_file_raises_not_returns_empty(self):
        """Row 2: a 0-byte file is the truncating-write window FEAT-14 was about -- it must
        raise, distinguishable from the absent-file None above, never silently collapse to
        the same answer."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"")
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(path)

    def test_unparseable_json_raises(self):
        """Row 3."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"{ not: valid json [[[")
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(path)

    def test_non_utf8_bytes_raise_not_traceback(self):
        """Row 4: gh-sync.py's OLD reader let this escape its `except OSError` as a bare
        UnicodeDecodeError traceback -- the read is inside THIS function's own try, so it
        cannot happen here."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"\xff\xfe\x00\x01")
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(path)

    def test_top_level_list_raises(self):
        """Row 5."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"[1, 2]")
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(path)

    def test_top_level_scalar_string_raises(self):
        """Row 6."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b'"x"')
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(path)

    def test_top_level_scalar_int_raises(self):
        """Row 7."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"3")
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(path)

    def test_block_key_absent_returns_the_mapping(self):
        """Row 8: a mapping present with nothing recorded yet is a legitimate document --
        load_feature_json returns it unchanged; deciding that no `github`/`factory` key
        means a first sync is each reader's own job, not this accessor's."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, json.dumps({"feature_id": "F1"}).encode())
            self.assertEqual({"feature_id": "F1"}, feature_json_write.load_feature_json(path))

    def test_block_key_present_not_a_mapping_still_returns(self):
        """Row 9: load_feature_json does not inspect nested field types -- a `github` value
        that is a plain string is still sitting inside a valid top-level JSON mapping, and
        catching THAT shape is each reader's own guard, not this accessor's."""
        with tempfile.TemporaryDirectory() as td:
            doc = {"github": "x", "factory": "x"}
            path = _write(td, json.dumps(doc).encode())
            self.assertEqual(doc, feature_json_write.load_feature_json(path))

    def test_wrong_typed_members_still_returns(self):
        """Row 10: coercion policy (a quoted "7" reads as 7, or not) is each reader's own
        decision, made after load_feature_json hands back the raw mapping -- unaffected
        here."""
        with tempfile.TemporaryDirectory() as td:
            doc = {"github": {"parent": "7", "issues": "nope"}}
            path = _write(td, json.dumps(doc).encode())
            self.assertEqual(doc, feature_json_write.load_feature_json(path))

    def test_duplicate_top_level_keys_raise(self):
        """Row 11: json.load's own default for a repeated key is silent last-wins --
        object_pairs_hook must reject it, or the migration WEAKENS strictness relative to
        harness_yaml's DuplicateKeyError while claiming to tighten it."""
        with tempfile.TemporaryDirectory() as td:
            text = ('{"github": {"parent": 1}, "feature_id": "F1", '
                    '"github": {"parent": 2}}').encode()
            path = _write(td, text)
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(path)

    def test_duplicate_nested_keys_raise(self):
        """A repeated key one level below the top -- DuplicateKeyError's own contract is
        "at any nesting depth", and this migration must match it there too."""
        with tempfile.TemporaryDirectory() as td:
            text = '{"github": {"parent": 1, "parent": 2}}'.encode()
            path = _write(td, text)
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(path)

    def test_yaml_only_document_raises(self):
        """Row 12: a document no JSON writer produces and no JSON reader accepts -- the
        parser-choice divergence this migration closes by accepting ONLY JSON. Was, under
        the old harness_yaml-based load_factory, RETURNED populated; must now raise."""
        with tempfile.TemporaryDirectory() as td:
            path = _write(td, b"github:\n  parent: 40\n  milestone: 7\n")
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(path)

    def test_valid_well_formed_document_returns_it(self):
        """Row 13, the control: a normal write_feature_json/write_factory document loads
        cleanly, proving this accessor distinguishes a well-formed read from a broken one."""
        with tempfile.TemporaryDirectory() as td:
            doc = {"feature_id": "F1",
                   "github": {"parent": 40, "milestone": 7, "issues": {"T-01": 41}}}
            path = _write(td, json.dumps(doc).encode())
            self.assertEqual(doc, feature_json_write.load_feature_json(path))

    def test_absent_and_malformed_are_distinguishable(self):
        """The core defect this migration closes (property 5): absent must never be
        indistinguishable from present-but-corrupt to a caller."""
        with tempfile.TemporaryDirectory() as td:
            absent_path = os.path.join(td, "feature.json")
            self.assertIsNone(feature_json_write.load_feature_json(absent_path))
            corrupt_path = _write(td, b"")
            with self.assertRaises(feature_json_write.FeatureJsonError):
                feature_json_write.load_feature_json(corrupt_path)


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


def _function_source(path, name):
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))
    node = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, node)


class SingleReaderStructuralTest(unittest.TestCase):
    """BUG-285's whole point: only ONE implementation parses feature.json now. A reader
    that reimplements even one call it delegates today would silently reopen the fork this
    feature closes."""

    def test_load_recorded_does_not_parse_independently(self):
        source = _function_source(BIN / "gh-sync.py", "load_recorded")
        for banned in ("json.load(", "json.loads(", "harness_yaml.load_file("):
            self.assertNotIn(banned, source, f"{banned!r} found in load_recorded")

    def test_load_factory_does_not_parse_independently(self):
        source = _function_source(BIN / "factory_decompose.py", "load_factory")
        for banned in ("json.load(", "json.loads(", "harness_yaml.load_file("):
            self.assertNotIn(banned, source, f"{banned!r} found in load_factory")


if __name__ == "__main__":
    unittest.main()
