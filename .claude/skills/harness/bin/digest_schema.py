#!/usr/bin/env python3
"""digest_schema.py — the live persona digest contract, read from bin/digest-schemas/.

FEAT-1928: every harness agent returns its digest as an object `{VERDICT, DIGEST, artifact}`
validated against ONE closed JSON Schema per persona. The schema files are the single copy of
the structural contract (required fields, types, enums, nested and list-entry shapes, the
nullable `none`/`n/a` spelling, the closed key set); shared parts live in common.json and are
reached by external `$ref`. Semantic and cross-file rules — the VERDICT-bound gates, git range
binding, receipts, the matrix floor, the lead roll-up — stay in validate-digest.py.

This module reads LIVE returns only. Durable digest.md files are digest_record.py's, and are
never validated against these schemas.
"""
import os
import sys

import jsonschema
import referencing
import referencing.exceptions
from referencing.jsonschema import DRAFT202012

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)
import artifact_accessors  # noqa: E402

SCHEMA_DIR = os.path.join(BIN_DIR, "digest-schemas")
COMMON = "common"

# The 16 runtime personas; one schema file each, named `<persona>.json`.
PERSONAS = (
    "harness-ai-dev", "harness-backend-dev", "harness-code-reviewer",
    "harness-data-engineer", "harness-dev-ops", "harness-documentor", "harness-eng-lead",
    "harness-frontend-dev", "harness-orchestrator", "harness-pm", "harness-product-lead",
    "harness-qa", "harness-security-reviewer", "harness-ui-reviewer",
    "harness-validator-lead", "harness-visual-designer",
)

# Names that are not a persona file but resolve to one. The main session building directly
# (DEC-174, #1895) carries the dev contract; the generic short names validate-digest.py's CLI
# has always accepted resolve to the persona whose contract is the superset for that family.
ALIASES = {
    "main-session": "harness-backend-dev",
    "dev": "harness-backend-dev",
    "reviewer": "harness-code-reviewer",
    "lead": "harness-eng-lead",
}


class DigestSchemaError(Exception):
    """A persona cannot be resolved, a schema file cannot be loaded, or object input is not
    a JSON object. The message names the file or input at fault."""


def canonical_persona(name):
    """The persona schema `name` is validated against: a persona itself, `harness-<name>`,
    or an ALIASES entry. Anything else is refused, never guessed."""
    if name in PERSONAS:
        return name
    if name in ALIASES:
        return ALIASES[name]
    prefixed = f"harness-{name}"
    if prefixed in PERSONAS:
        return prefixed
    raise DigestSchemaError(
        f"unknown persona {name!r} — no digest schema resolves it; expected one of "
        f"{list(PERSONAS)} or an alias in {sorted(ALIASES)}.")


class SchemaStore:
    """Strict, cached loads of one digest-schemas directory. Every file is decoded strictly
    (duplicate keys and NaN refused), checked as a Draft 2020-12 schema, and registered by its
    `$id`; a duplicate `$id` or a missing persona file is refused."""

    def __init__(self, directory=SCHEMA_DIR):
        self.directory = os.fspath(directory)
        self._documents = None
        self._registry = None
        self._validators = {}

    def _path(self, stem):
        return os.path.join(self.directory, f"{stem}.json")

    def _load_one(self, stem):
        path = self._path(stem)
        try:
            document = artifact_accessors.load_harness_json(path)
        except artifact_accessors.ArtifactAccessError as error:
            raise DigestSchemaError(f"{path}: digest schema cannot be loaded: {error}") from error
        try:
            jsonschema.Draft202012Validator.check_schema(document)
        except jsonschema.exceptions.SchemaError as error:
            raise DigestSchemaError(f"{path}: not a valid JSON Schema: {error.message}") from error
        if not isinstance(document.get("$id"), str):
            raise DigestSchemaError(f"{path}: digest schema has no string $id.")
        return document

    def _load_all(self):
        if self._documents is not None:
            return
        documents, ids = {}, {}
        for stem in (COMMON,) + PERSONAS:
            document = self._load_one(stem)
            if document["$id"] in ids:
                raise DigestSchemaError(
                    f"{self._path(stem)}: duplicate $id {document['$id']!r} (also "
                    f"{self._path(ids[document['$id']])}).")
            ids[document["$id"]] = stem
            documents[stem] = document
        self._registry = referencing.Registry().with_resources(
            (doc["$id"], DRAFT202012.create_resource(doc)) for doc in documents.values())
        self._documents = documents

    def schema(self, persona):
        """The parsed schema document for `persona` (aliases resolved)."""
        self._load_all()
        return self._documents[canonical_persona(persona)]

    def common_defs(self):
        """The shared `$defs` of common.json, from the same strict load as the personas."""
        self._load_all()
        return self._documents[COMMON].get("$defs") or {}

    def validator(self, persona):
        persona = canonical_persona(persona)
        if persona not in self._validators:
            self._validators[persona] = jsonschema.Draft202012Validator(
                self.schema(persona), registry=self._registry)
        return self._validators[persona]

    def validate(self, persona, mapping):
        """jsonschema error strings for `mapping`, `path: message`, empty when valid."""
        validator = self.validator(persona)
        try:
            found = sorted(validator.iter_errors(mapping), key=lambda e: list(e.absolute_path))
        except referencing.exceptions.Unresolvable as error:
            raise DigestSchemaError(
                f"{self._path(canonical_persona(persona))}: unresolved $ref {error}") from error
        return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
                for e in found]


_STORE = SchemaStore()


def load_schema(persona):
    """The live schema document for `persona`, loaded strictly once per process."""
    return _STORE.schema(persona)


def common_defs():
    """common.json's `$defs`, for callers that word errors from the schema's shared parts."""
    return _STORE.common_defs()


def validate_object(persona, mapping):
    """Structural errors for a returned object against its persona schema; [] is valid."""
    return _STORE.validate(persona, mapping)


def decode_object_json(text, context="digest object input"):
    """Strictly decode the validator CLI's object input; it must be one JSON object."""
    try:
        return artifact_accessors.read_hook_payload(text, context)
    except artifact_accessors.ArtifactAccessError as error:
        raise DigestSchemaError(
            f"{error} — return the digest as one JSON object "
            f"{{VERDICT, DIGEST: {{...}}, artifact}}.") from error
