"""harness.json schema_version 3: defaults, then validation against config-schemas/harness.json.

artifact_accessors.load_harness_json is the only caller: it decodes strictly and hands the mapping
here (FEAT-2297 D-01/D-04). A default fills a key only where it is ABSENT: an explicit null or a
wrong present value is never repaired, and records with required fields carry no defaults inside,
so a default can never hide a missing one. The checked validator is cached; config data never is.
"""
from __future__ import annotations

import copy
import datetime
import functools
import os
import re

from artifact_accessors import ArtifactAccessError, load_json_mapping

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config-schemas", "harness.json")
VERSION = 3
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_INSTANT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}(:[0-9]{2}(\.[0-9]{1,6})?)?(Z|[+-][0-9]{2}:[0-9]{2})")


def _is_date(value):
    if not isinstance(value, str) or not _DATE.fullmatch(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _is_instant(value):
    """An ISO-8601 extended instant that names its zone, with a real date, time and offset. The
    form is fixed by pattern and `Z` is normalised first, so validity never depends on which
    Python reads it (fromisoformat takes `Z` only from 3.11); on 3.11+ anything accepted here
    also passes plan_merge.check._instant, the gate that reads this era."""
    if not isinstance(value, str) or not _INSTANT.fullmatch(value):
        return False
    try:
        datetime.datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return False
    return True


def _refuse_remote(uri):
    import referencing.exceptions
    raise referencing.exceptions.NoSuchResource(ref=uri)


def _jsonschema():
    """jsonschema through its ONE guard in feature_schema (D-12's one-guard rule), loaded lazily so
    an artifact_accessors importer that never validates pays nothing for it. A sibling that fails
    while executing is RepoModuleError (the loader's one typed failure), refused as an unreadable
    config rather than escaping as whatever it raised."""
    import harness_boundary
    try:
        feature_schema = harness_boundary.load_repo_module("feature_schema")
    except harness_boundary.RepoModuleError as error:
        raise ArtifactAccessError(f"harness.json cannot be validated: {error}") from error
    if feature_schema.jsonschema is None:
        raise ArtifactAccessError(f"harness.json: {feature_schema.UNAVAILABLE_MESSAGE}")
    return feature_schema.jsonschema


def _format_checker(jsonschema):
    formats = jsonschema.FormatChecker(formats=())
    formats.checks("harness-date")(lambda value: not isinstance(value, str) or _is_date(value))
    formats.checks("harness-instant")(lambda value: not isinstance(value, str) or _is_instant(value))
    return formats


@functools.cache
def _schema_and_validator():
    """(schema, validator), built once the schema has loaded and checked; a failure is not cached."""
    jsonschema = _jsonschema()
    import referencing
    import referencing.jsonschema
    schema = load_json_mapping(SCHEMA_PATH)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as error:
        raise ArtifactAccessError(f"{SCHEMA_PATH}: invalid schema: {error.message}") from error
    registry = referencing.Registry(retrieve=_refuse_remote).with_resource(
        schema["$id"], referencing.Resource(schema, referencing.jsonschema.DRAFT202012))
    return schema, jsonschema.Draft202012Validator(
        schema, registry=registry, format_checker=_format_checker(jsonschema))


def _resolve(node, schema):
    while isinstance(node, dict) and "$ref" in node:
        node = schema["$defs"][node["$ref"].rsplit("/", 1)[-1]]
    return node


def _children(value, node):
    """(item, schema) for every key of `value` the schema describes: a named property, or an
    entry of a map whose entries share one schema (underscore prose excepted)."""
    properties = node.get("properties", {})
    entries = node.get("additionalProperties")
    for key, item in value.items():
        if key in properties:
            yield item, properties[key]
        elif isinstance(entries, dict) and not key.startswith("_"):
            yield item, entries


def _set_absent(value, properties):
    for key, child in properties.items():
        if key not in value and "default" in child:
            value[key] = copy.deepcopy(child["default"])


def _fill_defaults(value, node, schema):
    node = _resolve(node, schema)
    if isinstance(value, dict) and isinstance(node, dict):
        _set_absent(value, node.get("properties", {}))
        for item, child in _children(value, node):
            _fill_defaults(item, child, schema)


def _key_path(error):
    """The offending key's dotted path: an unexpected, missing or misnamed key is named itself."""
    parts = [str(part) for part in error.absolute_path]
    if "propertyNames" in error.absolute_schema_path:
        parts.append(str(error.instance))
    elif error.validator == "additionalProperties":
        known = error.schema.get("properties", {})
        parts += sorted(k for k in error.instance if k not in known and not k.startswith("_"))[:1]
    elif error.validator == "required":
        parts += sorted(set(error.validator_value) - set(error.instance))[:1]
    return tuple(parts)


def _rank(error):
    return _key_path(error), error.validator


def _typed_branch(error):
    """The errors of the one `anyOf` branch whose type the value matched, or None if not one."""
    branches = {}
    for sub in error.context:
        branches.setdefault(sub.relative_schema_path[0], []).append(sub)
    matched = [subs for subs in branches.values() if not any(
        sub.validator == "type" and sub.absolute_path == error.absolute_path for sub in subs)]
    return matched[0] if len(matched) == 1 else None


def _specific(error):
    """An `anyOf` failure, narrowed to the one branch whose type the value matched — so a bad
    board names its broken field, not the whole object. Ambiguous or untyped: left as is."""
    while error.validator == "anyOf" and error.context:
        branch = _typed_branch(error)
        if branch is None:
            break
        error = min(branch, key=_rank)
    return error


def validated(document, context):
    """`document` with schema defaults applied where absent, or ArtifactAccessError naming the
    source, the first failing key path (by path, then rule) and the schema keyword."""
    version = document.get("schema_version", VERSION)
    if version == 2 and not isinstance(version, bool):
        raise ArtifactAccessError(
            f"{context}: schema_version: 2 is the previous harness.json shape; run "
            f"upgrade-config.py <project-root> to migrate it to {VERSION} [const]")
    schema, validator = _schema_and_validator()
    _fill_defaults(document, schema, schema)
    errors = sorted((_specific(e) for e in validator.iter_errors(document)), key=_rank)
    if errors:
        first = errors[0]
        path = ".".join(_key_path(first)) or "(root)"
        raise ArtifactAccessError(f"{context}: {path}: {first.message} [{first.validator}]")
    return document
