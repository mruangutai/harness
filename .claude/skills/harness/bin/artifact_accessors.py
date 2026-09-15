#!/usr/bin/env python3
"""Public artifact readers: load_feature_json via feature_json_write; load_harness_json;
load_plan and manifest_domains via harness_yaml; load_fleet via factory_config; load_frontmatter;
load_omp_config; read_hook_payload; parse_gh_json; and write_harness_json.

Sanctioned routes are write_feature_json, write_harness_json, plan-merge.py verbs,
sync-agent-adapters.py, main-session-owned files, and the sole state.yaml reader trip-wire.
"""
import json
import os
import shutil
import tempfile


class ArtifactAccessError(Exception):
    """An artifact cannot be read safely; the message retains its caller context."""


def _reject_constant(value):
    raise ValueError(f"non-finite JSON constant: {value}")


def _reject_duplicate_keys(pairs):
    seen = set()
    result = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key: {key!r}")
        seen.add(key)
        result[key] = value
    return result


def _load_json_bytes(path, context):
    try:
        with open(path, "rb") as source:
            text = source.read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ArtifactAccessError(f"{context}: invalid JSON: {error}") from error
    return _parse_json_mapping(text, context)


def load_harness_json(path=None, *, text=None, context=None):
    """Read a strict harness JSON mapping from exactly one path or in-memory text source."""
    if path is None and text is None:
        raise ArtifactAccessError("harness.json: supply exactly one source")
    if path is not None and text is not None:
        raise ArtifactAccessError("harness.json: supply exactly one source")
    if text is not None:
        return _parse_json_mapping(text, context or "in-memory harness.json")
    return _load_json_bytes(path, str(path))


def load_feature_json(path=None, *, text=None, context=None):
    """Delegate feature.json parsing to its existing locked-writer implementation."""
    import feature_json_write
    return feature_json_write.load_feature_json(path, text=text, context=context)


def load_plan(path):
    """Delegate validated plan loading to harness_yaml."""
    import harness_yaml
    return harness_yaml.load_plan(path)


def load_fleet(path):
    """Delegate validated fleet loading to factory_config."""
    import factory_config
    return factory_config.load_fleet(path)


def manifest_domains(manifest_path, agent):
    """Delegate manifest domain walking to harness_yaml."""
    import harness_yaml
    return harness_yaml.manifest_domains(manifest_path, agent)


def load_frontmatter(text, context):
    """Return strict YAML frontmatter and body from an in-memory document."""
    import harness_yaml
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ArtifactAccessError(f"{context}: missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ArtifactAccessError(f"{context}: missing closing frontmatter delimiter") from error
    try:
        metadata = harness_yaml.load_str("\n".join(lines[1:end]), context)
    except harness_yaml.YamlParseError as error:
        raise ArtifactAccessError(f"{context}: invalid frontmatter: {error}") from error
    if not isinstance(metadata, dict):
        raise ArtifactAccessError(f"{context}: frontmatter is not a mapping")
    return metadata, "\n".join(lines[end + 1:]).lstrip("\n")


def load_omp_config(path):
    """Load a strict OMP YAML mapping from either .yml or .yaml."""
    import harness_yaml
    suffix = os.fspath(path).lower()
    if not suffix.endswith((".yml", ".yaml")):
        raise ArtifactAccessError(f"{path}: expected a .yml or .yaml config")
    try:
        document = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as error:
        raise ArtifactAccessError(f"{path}: invalid OMP config: {error}") from error
    if not isinstance(document, dict):
        raise ArtifactAccessError(f"{path}: OMP config is not a mapping")
    return document


def read_hook_payload(text, context):
    """Parse an in-memory hook JSON mapping without opening a file."""
    return _parse_json_mapping(text, context)


def parse_gh_json(text, context):
    """Parse an in-memory strict GitHub JSON value without enforcing its shape."""
    return _parse_json_text(text, context)


def _parse_json_text(text, context):
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicate_keys,
                          parse_constant=_reject_constant)
    except (TypeError, ValueError) as error:
        raise ArtifactAccessError(f"{context}: invalid JSON: {error}") from error


def _parse_json_mapping(text, context):
    document = _parse_json_text(text, context)
    if not isinstance(document, dict):
        raise ArtifactAccessError(f"{context}: JSON document is not a mapping")
    return document


def write_harness_json(path, document):
    """Back up then atomically replace a harness JSON mapping in its own directory."""
    if not isinstance(document, dict):
        raise ArtifactAccessError(f"{path}: harness JSON document is not a mapping")
    directory = os.path.dirname(os.path.abspath(path))
    try:
        shutil.copyfile(path, os.fspath(path) + ".harness-bak")
        descriptor, temporary = tempfile.mkstemp(prefix=".harness-", suffix=".tmp", dir=directory)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as target:
                json.dump(document, target, indent=2)
                target.write("\n")
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary, path)
        except BaseException:
            if os.path.exists(temporary):
                os.unlink(temporary)
            raise
    except OSError as error:
        raise ArtifactAccessError(f"{path}: cannot atomically write harness JSON: {error}") from error
