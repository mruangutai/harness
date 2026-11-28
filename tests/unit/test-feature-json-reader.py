#!/usr/bin/env python3
"""Contract tests for the public feature.json accessor (BUG-285).

The load implementation lives in feature_record/read.py. These tests exercise it through
feature_record.read, covering absence-vs-corruption, strict JSON,
top-level shape, and recorded GitHub/factory issue fields.
"""
import json
import os
import tempfile
import unittest

import unit_support  # noqa: F401  (puts bin/ on sys.path)
import harness_merge
from feature_record import read as record_read
import harness_yaml


def _write(dirpath, data_bytes):
    path = os.path.join(dirpath, "feature.json")
    with open(path, "wb") as f:
        f.write(data_bytes)
    return path


class LoadFeatureJsonTest(unittest.TestCase):
    def setUp(self):
        self.td = self.enterContext(tempfile.TemporaryDirectory())

    def _load(self, data_bytes):
        """Write data_bytes to feature.json (truncating) and load it by path."""
        return record_read.load_feature_json(_write(self.td, data_bytes))

    def _assert_load_raises(self, data_bytes, exc=record_read.FeatureJsonError):
        with self.assertRaises(exc):
            self._load(data_bytes)

    def test_absent_file_returns_none(self):
        """Row 1: a legitimate first sync/first publish -- never an error."""
        path = os.path.join(self.td, "feature.json")
        self.assertIsNone(record_read.load_feature_json(path))

    def test_empty_file_raises_not_returns_empty(self):
        """Row 2: a 0-byte file is the truncating-write window FEAT-14 was about -- it must
        raise, distinguishable from the absent-file None above, never silently collapse to
        the same answer."""
        self._assert_load_raises(b"")

    def test_unparseable_json_raises(self):
        """Row 3."""
        self._assert_load_raises(b"{ not: valid json [[[")

    def test_non_utf8_bytes_raise_not_traceback(self):
        """Row 4: gh-sync.py's OLD reader let this escape its `except OSError` as a bare
        UnicodeDecodeError traceback -- the read is inside THIS function's own try, so it
        cannot happen here."""
        self._assert_load_raises(b"\xff\xfe\x00\x01")

    def test_top_level_list_raises(self):
        """Row 5."""
        self._assert_load_raises(b"[1, 2]")

    def test_top_level_scalar_string_raises(self):
        """Row 6."""
        self._assert_load_raises(b'"x"')

    def test_top_level_scalar_int_raises(self):
        """Row 7."""
        self._assert_load_raises(b"3")

    def test_block_key_absent_returns_the_mapping(self):
        """Row 8: a mapping present with nothing recorded yet is a legitimate document --
        load_feature_json returns it unchanged; deciding that no `github`/`factory` key
        means a first sync is each reader's own job, not this accessor's."""
        doc = {"feature_id": "F1"}
        self.assertEqual(doc, self._load(json.dumps(doc).encode()))

    def test_block_key_present_not_a_mapping_still_returns(self):
        """A present block without recorded parent or issues fields remains raw metadata."""
        doc = {"github": "x", "factory": "x"}
        self.assertEqual(doc, self._load(json.dumps(doc).encode()))

    def test_wrong_typed_members_raise(self):
        """Present recorded parent and issues fields are shared-boundary corruption."""
        doc = {"github": {"parent": "7", "issues": "nope"}}
        self._assert_load_raises(json.dumps(doc).encode(), Exception)

    def test_duplicate_top_level_keys_raise(self):
        """Row 11: json.load's own default for a repeated key is silent last-wins --
        object_pairs_hook must reject it, or the migration WEAKENS strictness relative to
        harness_yaml's DuplicateKeyError while claiming to tighten it."""
        self._assert_load_raises(('{"github": {"parent": 1}, "feature_id": "F1", '
                                  '"github": {"parent": 2}}').encode())

    def test_duplicate_nested_keys_raise(self):
        """A repeated key one level below the top -- DuplicateKeyError's own contract is
        "at any nesting depth", and this migration must match it there too."""
        self._assert_load_raises(b'{"github": {"parent": 1, "parent": 2}}')

    def test_issue_285_comment_bearing_yaml_document_is_rejected(self):
        """Issue 285's prior feature document remains valid YAML, never feature JSON."""
        text = (
            b"feature_id: F1\n"
            b"github:\n"
            b"  parent: 40        # the container issue, adopted\n"
            b'  milestone: "7"    # quoted on purpose\n'
            b"  parent_origin: adopted\n"
            b"  attached: [T-01]\n"
            b"  issues:\n"
            b"    T-01: 41   # trailing comment here too\n"
        )
        expected = {
            "feature_id": "F1",
            "github": {
                "parent": 40,
                "milestone": "7",
                "parent_origin": "adopted",
                "attached": ["T-01"],
                "issues": {"T-01": 41},
            },
        }
        path = _write(self.td, text)
        self.assertEqual(expected, harness_yaml.load_file(path))
        with self.assertRaises(record_read.FeatureJsonError):
            record_read.load_feature_json(path)

    def test_valid_well_formed_document_returns_it(self):
        """Row 13, the control: a normal write_feature_json/write_factory document loads
        cleanly, proving this accessor distinguishes a well-formed read from a broken one."""
        doc = {"feature_id": "F1",
               "github": {"parent": 40, "milestone": 7, "issues": {"T-01": 41}}}
        self.assertEqual(doc, self._load(json.dumps(doc).encode()))

    def test_absent_and_malformed_are_distinguishable(self):
        """The core defect this migration closes (property 5): absent must never be
        indistinguishable from present-but-corrupt to a caller."""
        absent_path = os.path.join(self.td, "feature.json")
        self.assertIsNone(record_read.load_feature_json(absent_path))
        self._assert_load_raises(b"")

    def test_nonfinite_constants_raise(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                self._assert_load_raises(f'{{"github": {{"parent": {constant}}}}}'.encode())

    def test_text_source_matches_path_validation(self):
        document = {"feature_id": "F1", "github": {"issues": {"T-01": "8"}}}
        self.assertEqual(
            document,
            record_read.load_feature_json(
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
                    record_read.FeatureJsonError, expected
                ) as caught:
                    record_read.load_feature_json(
                        text=text, context="git show main:feature.json"
                    )
                self.assertIn("git show main:feature.json", str(caught.exception))

    def test_exactly_one_source_is_required(self):
        with self.assertRaises(record_read.FeatureJsonError):
            record_read.load_feature_json()
        with self.assertRaises(record_read.FeatureJsonError):
            record_read.load_feature_json(
                "feature.json", text='{"feature_id": "F1"}',
                context="git show main:feature.json",
            )


class ParseDocTest(unittest.TestCase):
    """FEAT-61 T-01: parse_doc decodes through artifact_accessors.strict_json_loads and keeps its
    own refusal contract byte for byte — code 11 and the exact line shapes gh-sync and the
    merge tools already match on. The two private hook copies it carried are gone; a reader
    still reaching for them fails loudly rather than silently using a stale twin."""

    def _refusal(self, base):
        with self.assertRaises(harness_merge.MergeRefusal) as caught:
            record_read.parse_doc(base, "X/feature.json")
        return caught.exception

    def test_none_passes_through_and_a_mapping_round_trips(self):
        self.assertIsNone(record_read.parse_doc(None, "X"))
        self.assertEqual({"a": 1}, record_read.parse_doc(b'{"a": 1}', "X"))

    def test_decode_failures_keep_code_11_and_the_not_valid_json_line(self):
        for base in (
            b"{ not json",
            b'{"outer": {"k": 1, "k": 2}}',
            b'{"v": NaN}',
            b"\xff\xfe",
        ):
            with self.subTest(base=base):
                refusal = self._refusal(base)
                self.assertEqual(record_read.SCHEMA_REFUSAL_CODE, refusal.code)
                self.assertEqual(1, len(refusal.lines))
                self.assertTrue(refusal.lines[0].startswith("X/feature.json: not valid JSON: "),
                                refusal.lines[0])

    def test_non_mapping_keeps_code_11_and_names_the_type(self):
        refusal = self._refusal(b"[1, 2]")
        self.assertEqual(record_read.SCHEMA_REFUSAL_CODE, refusal.code)
        self.assertEqual(
            ["X/feature.json: parsed but is not a JSON mapping (got list)"], refusal.lines)

    def test_private_hook_twins_are_gone(self):
        self.assertFalse(hasattr(record_read, "_reject_duplicate_keys"))
        self.assertFalse(hasattr(record_read, "_reject_nonfinite_constant"))


class OptIntTest(unittest.TestCase):
    """opt_int now lives in feature_record/read.py, the one shared copy gh-sync.py's three
    call sites use (BUG-285 property 7); factory_decompose.py's load_factory keeps its own
    strict isinstance guard on purpose, unaffected by this move."""

    def test_quoted_digit_string_coerces(self):
        self.assertEqual(7, record_read.opt_int("7"))

    def test_bool_excluded_despite_int_subclass(self):
        self.assertIsNone(record_read.opt_int(True))
        self.assertIsNone(record_read.opt_int(False))

    def test_none_and_junk_are_none(self):
        self.assertIsNone(record_read.opt_int(None))
        self.assertIsNone(record_read.opt_int("nope"))

    def test_real_int_passes_through(self):
        self.assertEqual(41, record_read.opt_int(41))


if __name__ == "__main__":
    unittest.main()
