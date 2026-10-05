#!/usr/bin/env python3
"""digest_record.py — the durable digest.md reader for historical artifact consumers.

FEAT-1928 SC-07: a run directory's digest.md is prose followed by one or more fenced YAML
blocks; a later block is a correction appended after an earlier one (DEC-208). Consumers of
that durable record (check-state INV-15/INV-46, plan-merge record-panel/record-amendments,
the append comparison) read the LAST fenced block that safely loads to a mapping and use its
structured keys.

Deliberately narrow: this module never validates against the live persona schemas (a
historical record may carry keys today's closed contract refuses), never treats historical
text as a live return, never picks a block by searching for a VERDICT token, never rewrites
bytes and never grandfathers by date. It does not import digest_schema.
"""
import os
import re
import sys

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)
import harness_yaml  # noqa: E402

# An opening fence and its info string; only YAML-labelled or unlabelled fences are records.
_FENCE_RE = re.compile(r"^```([^`\s]*)[^`]*$")
_YAML_LABELS = {"", "yaml", "yml"}


class DigestRecordError(Exception):
    """No fenced YAML mapping can be read from a durable digest record."""


def _fenced_blocks(text):
    """(info label, body) for every closed ``` fence, in document order."""
    blocks, label, body = [], None, []
    for line in text.splitlines():
        if label is None:
            match = _FENCE_RE.match(line)
            if match:
                label, body = match.group(1).lower(), []
        elif line.rstrip() == "```":
            blocks.append((label, "\n".join(body)))
            label = None
        else:
            body.append(line)
    return blocks


def last_fenced_mapping(text, where="digest record"):
    """The last fenced YAML block in `text` that loads to a mapping. Blocks that fail to
    parse (including duplicate keys) or load to a non-mapping are skipped, earlier ones are
    tried in turn; none at all raises DigestRecordError naming `where`."""
    for label, body in reversed(_fenced_blocks(text)):
        if label not in _YAML_LABELS:
            continue
        try:
            loaded = harness_yaml.load_str(body, where)
        except harness_yaml.MissingDependency as error:
            raise DigestRecordError(f"{where}: cannot read fenced YAML: {error}") from error
        except harness_yaml.YamlParseError:
            continue
        if isinstance(loaded, dict):
            return loaded
    raise DigestRecordError(
        f"{where}: no fenced YAML block loads to a mapping — the durable record needs a "
        f"```yaml block holding VERDICT, DIGEST and artifact after the prose.")


def load_record(path):
    """The last fenced mapping of the digest file at `path`, read-only."""
    try:
        with open(path, encoding="utf-8") as source:
            text = source.read()
    except (OSError, UnicodeDecodeError) as error:
        raise DigestRecordError(f"{path}: digest record cannot be read: {error}") from error
    return last_fenced_mapping(text, str(path))


def structured_keys(mapping, prefix=""):
    """Sorted dotted key paths of `mapping`, descending into nested mappings."""
    keys = []
    for key, value in mapping.items():
        name = f"{prefix}{key}"
        keys.append(name)
        if isinstance(value, dict):
            keys.extend(structured_keys(value, f"{name}."))
    return sorted(keys)
