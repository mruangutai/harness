#!/usr/bin/env python3
"""Canonical artifact readers and their public read errors.

This module owns feature.json, plan.yaml, manifest-domain, fleet.yaml, frontmatter,
OMP-config, hook-payload, GitHub-JSON, and harness.json reads.

Sanctioned routes are write_feature_json, write_harness_json, plan-merge.py verbs,
main-session-owned files, and the sole state.yaml reader trip-wire.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass


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


class FeatureJsonError(Exception):
    """A feature.json read failed with an actionable next step."""

    def __init__(self, what, value, next_step):
        import factory_cli
        self.next_step = next_step
        super().__init__(factory_cli.body(what, value, next_step))


def _feature_json_source(path, text, context):
    label = context or ("feature.json" if path is None else str(path))
    if (path is None) == (text is None):
        raise FeatureJsonError(
            "feature.json invalid", label, "supply exactly one source")
    source_context = context or (
        "in-memory feature.json" if text is not None else str(path))
    if text is not None:
        return text, source_context
    if not os.path.exists(path):
        return None, source_context
    return _read_feature_json_text(path, source_context), source_context


def load_feature_json(path=None, *, text=None, context=None):
    """Load a feature mapping from exactly one path or in-memory JSON text source."""
    source_text, source_context = _feature_json_source(path, text, context)
    if source_text is None:
        return None
    doc = _parse_feature_json_text(source_text, source_context)
    _validate_recorded_blocks(doc, source_context)
    return doc


def _read_feature_json_text(path, context):
    try:
        with open(path, "rb") as source:
            return source.read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise FeatureJsonError(
            "feature.json unreadable", context, f"could not be read: {error}"
        ) from error


def _parse_feature_json_text(text, context):
    try:
        doc = json.loads(text, object_pairs_hook=_reject_duplicate_keys,
                         parse_constant=_reject_constant)
    except (TypeError, ValueError) as error:
        raise FeatureJsonError(
            "feature.json invalid", context, f"does not parse: {error}"
        ) from error
    if not isinstance(doc, dict):
        raise FeatureJsonError(
            "feature.json invalid", context,
            f"parsed but is not a JSON mapping (got {type(doc).__name__})",
        )
    return doc


def _positive_issue_number(value):
    import feature_json_write
    number = feature_json_write.opt_int(value)
    return number if number is not None and number >= 1 else None


def _validate_recorded_parent(block, path, block_name):
    if "parent" not in block or block["parent"] is None:
        return
    if _positive_issue_number(block["parent"]) is not None:
        return
    raise FeatureJsonError(
        "feature.json invalid", path,
        f"has a {block_name}.parent that is not a recorded issue number",
    )


def _validate_recorded_issues(block, path, block_name):
    if "issues" not in block:
        return
    issues = block["issues"]
    if not isinstance(issues, dict):
        raise FeatureJsonError(
            "feature.json invalid", path,
            f"has a {block_name}.issues key that is not a JSON object",
        )
    for key, value in issues.items():
        if _positive_issue_number(value) is None:
            raise FeatureJsonError(
                "feature.json invalid", path,
                f"has a {block_name}.issues[{key!r}] value that is not a recorded issue number",
            )


def _validate_recorded_block(doc, path, block_name):
    """Refuse malformed recorded issue fields in a present GitHub-style block."""
    block = doc.get(block_name)
    if not isinstance(block, dict):
        return
    _validate_recorded_parent(block, path, block_name)
    _validate_recorded_issues(block, path, block_name)


def _validate_recorded_blocks(doc, path):
    """Validate recorded GitHub and factory issue fields at the shared read boundary."""
    for block_name in ("github", "factory"):
        _validate_recorded_block(doc, path, block_name)


def load_plan(path):
    """Load a plan through strict YAML parsing and the canonical plan validator."""
    import harness_yaml
    return harness_yaml.validate_plan_doc(harness_yaml.load_file(path), path)


class FleetError(Exception):
    """A fleet declaration or fleet-derived value is unusable."""

    def __init__(self, what, value, next_step):
        import factory_cli
        super().__init__(factory_cli.body(what, value, next_step))


def _require_fleet_mapping(data, path):
    if not isinstance(data, dict):
        raise FleetError(
            "fleet file invalid", path, "the file must parse to a YAML mapping"
        )




def _validate_fleet_header(data, path):
    if data.get("schema") != "factory-fleet/1":
        raise FleetError(
            "fleet schema invalid", "schema", f"set schema: factory-fleet/1 in {path}"
        )
    if "board" in data:
        raise FleetError(
            "fleet key invalid", "board",
            f"a whole-fleet board key is no longer read from here — each repository declares "
            f"its own board remotely, in its own .harness/harness.json under github.board; "
            f"remove board from {path}",
        )


def _validate_fleet_repo(entry, path):
    name = entry.get("name") if isinstance(entry, dict) else None
    if not isinstance(name, str) or "/" not in name:
        raise FleetError(
            "fleet repo entry invalid", "repos[].name",
            f"each repo needs a name containing a slash (owner/repo) in {path}",
        )
    if not entry.get("default_branch"):
        raise FleetError(
            "fleet repo entry invalid", f"repos[{name}].default_branch",
            f"set a non-empty default_branch for {name} in {path}",
        )
    if "board" in entry:
        raise FleetError(
            "fleet key invalid", f"repos[{name}].board",
            f"the board is no longer declared in fleet.yaml — {name} declares its own board "
            f"remotely, in its own .harness/harness.json under github.board. Remove "
            f"repos[{name}].board from {path}",
        )


def _validate_fleet_repos(data, path):
    repos = data.get("repos")
    if not isinstance(repos, list) or not repos:
        raise FleetError(
            "fleet key invalid", "repos", f"set a non-empty list of repo entries in {path}"
        )
    for entry in repos:
        _validate_fleet_repo(entry, path)


def _validate_workspace_root(data, path):
    workspace_root = data.get("workspace_root")
    if not isinstance(workspace_root, str) or not os.path.isabs(workspace_root):
        raise FleetError(
            "fleet key invalid", "workspace_root",
            f"set it to an absolute path in {path}",
        )
    if os.path.dirname(os.path.normpath(workspace_root)) == os.path.normpath(workspace_root):
        raise FleetError(
            "fleet key invalid", "workspace_root",
            f"it is a filesystem root ({workspace_root!r}) in {path} — every path on "
            f"the machine would resolve inside the factory workspace, so the write "
            f"guard would refuse scratch paths it must ignore. Set it to a real "
            f"directory that holds the checkouts.",
        )


def load_fleet(path=None):
    """Load and validate a fleet declaration."""
    import harness_yaml
    if path is None:
        import factory_config
        path = factory_config.FLEET_PATH
    try:
        data = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as error:
        raise FleetError("fleet file invalid", path, f"does not load: {error}")
    _require_fleet_mapping(data, path)
    _validate_fleet_header(data, path)
    _validate_fleet_repos(data, path)
    _validate_workspace_root(data, path)
    return data


@dataclass(frozen=True)
class ManifestRoleDomains:
    """One named manifest role's writable domain globs."""

    name: str
    write_globs: tuple[str, ...]


@dataclass(frozen=True)
class ManifestDomainsView:
    """Immutable all-role manifest view returned by ``manifest_domains(view=True)``."""

    roles: tuple[ManifestRoleDomains, ...]
    shared_write_globs: tuple[str, ...]
    main_session_present: bool
    main_session_writes: tuple[str, ...] | None


def _require_manifest_mapping(parsed, manifest_path):
    import harness_yaml
    if isinstance(parsed, dict):
        return parsed
    raise harness_yaml.YamlParseError(
        manifest_path,
        f"manifest is not a YAML mapping (parsed as {type(parsed).__name__}); "
        "an empty or malformed file cannot declare any domain")


def _manifest_nodes(root):
    pending = [root]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            yield node
            pending.extend(reversed(tuple(node.values())))
        elif isinstance(node, list):
            pending.extend(reversed(node))


def _domain_paths(entries, *, include_read):
    if not isinstance(entries, list):
        return []
    return [
        str(entry["path"])
        for entry in entries
        if isinstance(entry, dict)
        and "path" in entry
        and (include_read or not entry.get("read"))
    ]


def _manifest_roles(parsed):
    names = []
    globs_by_name = {}
    for node in _manifest_nodes(parsed):
        raw_name = node.get("name")
        if raw_name is None:
            continue
        name = str(raw_name)
        if name not in globs_by_name:
            names.append(name)
            globs_by_name[name] = []
        globs_by_name[name].extend(
            _domain_paths(node.get("domain"), include_read=False))
    return tuple(
        ManifestRoleDomains(name, tuple(globs_by_name[name])) for name in names)


def _matching_manifest_paths(parsed, agent):
    paths = []
    for node in _manifest_nodes(parsed):
        name = node.get("name")
        if name is None or (agent is not None and name != agent):
            continue
        paths.extend(_domain_paths(node.get("domain"), include_read=False))
    return paths


def _main_session_writes(parsed):
    main_session = parsed.get("main_session")
    writes = main_session.get("writes") if isinstance(main_session, dict) else None
    if not isinstance(writes, list) or not writes:
        return None
    return tuple(entry for entry in writes if isinstance(entry, str) and entry.strip())


def _manifest_domains_view(parsed):
    return ManifestDomainsView(
        _manifest_roles(parsed),
        tuple(_domain_paths(parsed.get("shared"), include_read=False)),
        "main_session" in parsed,
        _main_session_writes(parsed),
    )


def manifest_domains(manifest_path, agent=None, *, view=False):
    """Return one agent's domains, all role domains, or an immutable all-role view."""
    import harness_yaml
    if view and agent is not None:
        raise TypeError("manifest_domains(view=True) requires agent=None")
    parsed = _require_manifest_mapping(
        harness_yaml.load_file(manifest_path), manifest_path)
    if view:
        return _manifest_domains_view(parsed)
    mine = _matching_manifest_paths(parsed, agent)
    shared = _domain_paths(parsed.get("shared"), include_read=agent is not None)
    return mine, shared


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
