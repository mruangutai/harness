#!/usr/bin/env python3
"""feature_schema.py — the schema-checking module for a feature's execution
state (feature.json), FEAT-14 D-03.

Imported IN PROCESS by check-domain.sh (T-06) and by validate-feature-json.py
(this directory's thin CLI wrapper) — never spawned as a subprocess on the
write-time path, so a schema violation can be attributed to the real file it
came from rather than a temporary one, and the missing-dependency case is an
ordinary `except ImportError` branch rather than a subprocess that failed to
launch.

`jsonschema` is imported at MODULE level, inside a try, with the result
cached in JSONSCHEMA_AVAILABLE. Never import it inside a per-file function:
check-domain.sh's post sweep calls the entry point once per candidate file,
and a per-call import would pay the (measured) +42.6ms cost, and print the
unavailability message, once per file instead of once per process.

THE JSON PATH — problems_for_text(), and problems_for_file() on a `.json`
path — DEPENDS ON STDLIB `json` AND `jsonschema` ONLY, NEVER PyYAML. This is
deliberate, not an oversight: check-domain.sh's neighbouring `state.yaml`
branch returns `[]` (a fail-open the operator ruled on, DEC-154) when PyYAML
is absent, because state.yaml genuinely has no other way to be read. This
module's JSON path has no PyYAML dependency to be absent in the first place,
so it must never be made to match that shape — a checker with a dependency it
does not need is a checker that can fail for someone else's reason. The YAML
path exists only in problems_for_file(), for a non-`.json` extension, and it
imports harness_yaml LAZILY, inside that one branch, so a JSON-only caller
never pulls PyYAML in at all (T-01 receipt records this placement).
"""
import json
import os
import sys

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    JSONSCHEMA_AVAILABLE = False

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)

SCHEMA_PATH = os.path.join(BIN_DIR, "feature-schema.json")

# Verbatim text, per T-01's intent — never return [] on this path and never
# emit the word "skip": [] means checked and clean, and a checker that
# cannot run must never be indistinguishable from one that passed.
UNAVAILABLE_MESSAGE = (
    "jsonschema is REQUIRED and is not importable, so this file CANNOT be checked.\n"
    "Install it with: python3 -m pip install jsonschema  (or python3 -m pip install "
    "--user --break-system-packages jsonschema)"
)

# The redirection sentence, printed verbatim on every undeclared-key
# rejection regardless of nesting level (REQ-03 / the "Where the prose goes
# instead" table) — the destination does not vary by where the key sits.
_REDIRECT = (
    "This file holds execution state only. An operator ruling goes in that feature's "
    "plan.yaml under approval.rulings; run narrative, findings and corrections go in "
    "that run's digest; current state and open questions go in STATE.md; "
    "measurements, research and receipts go in notes/."
)

_schema_cache = None


def load_schema():
    """Read feature-schema.json from beside this module. Cached after the
    first read — the schema file does not change within one process."""
    global _schema_cache
    if _schema_cache is None:
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            _schema_cache = json.load(f)
    return _schema_cache


def _missing_keys(error):
    """error.validator == 'required'. Recover exactly which keys are missing
    by diffing the schema's OWN `required` list against the instance, rather
    than parsing jsonschema's message text — the message wording is not a
    contract the schema author controls."""
    required = error.schema.get("required", [])
    instance = error.instance if isinstance(error.instance, dict) else {}
    return sorted(set(required) - set(instance))


def _undeclared_keys(error):
    """error.validator == 'additionalProperties'. Same technique: diff the
    schema's declared `properties` against the instance's actual keys."""
    allowed = set(error.schema.get("properties", {}))
    instance = error.instance if isinstance(error.instance, dict) else {}
    return sorted(set(instance) - allowed)


def _pointer(path):
    if not path:
        return "/"
    return "/" + "/".join(str(p) for p in path)


def _problems_for_doc(doc, display):
    schema = load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    problems = []
    for error in sorted(validator.iter_errors(doc), key=lambda e: [str(p) for p in e.absolute_path]):
        pointer = _pointer(error.absolute_path)
        if error.validator == "additionalProperties":
            for key in _undeclared_keys(error):
                problems.append(f"{display}: undeclared key {key!r} at {pointer}. {_REDIRECT}")
        elif error.validator == "required":
            for key in _missing_keys(error):
                problems.append(
                    f"{display}: missing required key {key!r} at {pointer} "
                    f"(required by SPEC 11.3)."
                )
        else:
            problems.append(f"{display}: {pointer}: {error.message}")
    return problems


def problems_for_text(text, display):
    """Validate JSON document TEXT against the schema. Returns a list of
    stderr LINES, [] when clean. Never exits, never writes a temporary file
    — this is the entry point check-domain.sh imports at T-06, and it is why
    the module exists: a subprocess cannot be handed the real path, and its
    launch failure would escape as a non-blocking exit 1. `display` is the
    path to name IN THE MESSAGE, not a hint for how to parse `text` — this
    function always parses `text` as JSON."""
    if not JSONSCHEMA_AVAILABLE:
        return [UNAVAILABLE_MESSAGE]
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as e:
        return [f"{display}: not valid JSON: {e}"]
    return _problems_for_doc(doc, display)


def problems_for_file(path):
    """Same as problems_for_text, reading from disk. LOAD BY EXTENSION, never
    one permissive loader: a `.json` path is read as text and validated
    through problems_for_text (stdlib json + jsonschema only, see module
    docstring); anything else is read with harness_yaml.load_file, imported
    LAZILY here so the `.json` path above never pulls PyYAML in at all. A
    `.json` file that is valid YAML but not valid JSON is REJECTED, naming
    the JSON decode error — without this a feature.json no `json.load`
    consumer can read would validate clean."""
    if not JSONSCHEMA_AVAILABLE:
        return [UNAVAILABLE_MESSAGE]

    if path.endswith(".json"):
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            return [f"{path}: cannot be read: {e}"]
        return problems_for_text(text, path)

    # Lazy import, deliberately confined to THIS branch — see module
    # docstring and T-01's receipt: this is what makes "the .json path never
    # imports PyYAML" empirically checkable rather than merely asserted.
    import harness_yaml
    try:
        doc = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as e:
        return [f"{path}: not valid YAML: {e}"]
    return _problems_for_doc(doc, path)
