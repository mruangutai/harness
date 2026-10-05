#!/usr/bin/env python3
"""digest_record.py — the durable digest.md reader (FEAT-1928 SC-07).

Historical digest files are read, never judged: the last fenced YAML block that loads to a
mapping wins, keys outside today's live schemas survive, a file with no such block fails
with an actionable message, and every read leaves the file byte-identical (sha256 before
and after). The module must not reach for the live persona schemas at all.
"""
from pathlib import Path
import ast
import hashlib
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(BIN))
import digest_record  # noqa: E402

HISTORICAL = """# Build digest

Prose the lead wrote. A VERDICT: FAIL mention in prose must not pick a block.

```yaml
VERDICT: FAIL
DIGEST:
  headline: first attempt
```

```yaml
VERDICT: PASS
DIGEST:
  headline: corrected
  team: build
  members: [{ step: s1, persona: harness-qa, verdict: PASS }]
  cost_usd: 1.25
  retired_field: kept
artifact: notes/run/digest.md
```

Trailing prose after the last block.

```text
VERDICT: BLOCKED — a non-mapping block after the real one
```
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DurableRecord(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="digest-record-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fixture(self, text):
        path = self.tmp / "digest.md"
        path.write_bytes(text.encode("utf-8"))
        return path

    def read(self, path):
        before = sha(path)
        try:
            return digest_record.load_record(path)
        finally:
            self.assertEqual(sha(path), before, "a read changed the file's bytes")

    def test_last_fenced_mapping_wins_and_keeps_historical_keys(self):
        path = self.fixture(HISTORICAL)
        record = self.read(path)
        self.assertEqual(record["VERDICT"], "PASS")
        self.assertEqual(record["DIGEST"]["headline"], "corrected")
        self.assertEqual(record["DIGEST"]["cost_usd"], 1.25)
        self.assertEqual(record["DIGEST"]["retired_field"], "kept")
        self.assertEqual(record["DIGEST"]["members"][0]["verdict"], "PASS")

    def test_text_api_matches_file_api(self):
        self.assertEqual(digest_record.last_fenced_mapping(HISTORICAL),
                         self.read(self.fixture(HISTORICAL)))

    def test_structured_keys(self):
        record = self.read(self.fixture(HISTORICAL))
        self.assertEqual(digest_record.structured_keys(record),
                         ["DIGEST", "DIGEST.cost_usd", "DIGEST.headline", "DIGEST.members",
                          "DIGEST.retired_field", "DIGEST.team", "VERDICT", "artifact"])

    def test_malformed_last_block_falls_back_to_previous_mapping(self):
        text = HISTORICAL + "\n```yaml\nDIGEST: [unclosed\n```\n"
        self.assertEqual(self.read(self.fixture(text))["DIGEST"]["headline"], "corrected")

    def test_duplicate_key_block_is_not_a_mapping(self):
        text = "```yaml\nVERDICT: PASS\n```\n\n```yaml\nVERDICT: PASS\nVERDICT: FAIL\n```\n"
        self.assertEqual(self.read(self.fixture(text)), {"VERDICT": "PASS"})

    def test_absent_mapping_fails_actionably(self):
        for text in ("# only prose\nVERDICT: PASS\nDIGEST:\n  headline: x\n",
                     "```yaml\n- a list\n```\n", "```yaml\nkey: [broken\n```\n", ""):
            path = self.fixture(text)
            with self.assertRaises(digest_record.DigestRecordError) as caught:
                self.read(path)
            message = str(caught.exception)
            self.assertIn("fenced", message)
            self.assertIn(str(path), message)

    def test_unreadable_file_fails_actionably(self):
        with self.assertRaisesRegex(digest_record.DigestRecordError, "missing.md"):
            digest_record.load_record(self.tmp / "missing.md")

    def test_does_not_import_live_schema(self):
        tree = ast.parse((BIN / "digest_record.py").read_text(encoding="utf-8"))
        imported = {alias.name for node in ast.walk(tree)
                    if isinstance(node, (ast.Import, ast.ImportFrom))
                    for alias in node.names} | {
            node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertNotIn("digest_schema", imported)
        self.assertNotIn("jsonschema", imported)


if __name__ == "__main__":
    unittest.main()
