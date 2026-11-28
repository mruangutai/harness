#!/usr/bin/env python3
"""Deterministically verify the provider-neutral OMP Harness surface."""

from __future__ import annotations

import sys
from pathlib import Path

import artifact_accessors
import digest_projection

# The one place a role's reasoning effort is bound to its capability alias (DEC-233).
THINKING_FOR_CAPABILITY = {
    "@deep": "high",
    "@strong": "medium",
    "@standard": "medium",
    "@review": "high",
}
CAPABILITIES = set(THINKING_FOR_CAPABILITY)
REQUIRED_DOORS = ("harness", "harness-plan", "harness-patch", "harness-ship", "harness-grilling")
PROVIDER_PREFIX = {
    "openai.yml": "openai-codex/",
    "anthropic.yml": "anthropic/",
}


def frontmatter(path: Path) -> dict:
    metadata, _body = artifact_accessors.load_frontmatter(
        path.read_text(encoding="utf-8"), str(path))
    return metadata

def check(root: Path) -> list[str]:
    # FEAT-67: order is part of the contract — errors come out in CHECKS order.
    errors: list[str] = []
    for check_fn in CHECKS:
        errors.extend(check_fn(root))
    return errors


def agents_md_errors(root: Path) -> list[str]:
    agents_md = root / "AGENTS.md"
    if not agents_md.is_file():
        return ["AGENTS.md is missing; OMP has no provider-neutral project guidance"]
    return []


def config_errors(root: Path) -> list[str]:
    errors: list[str] = []
    config_path = root / ".omp" / "config.yml"
    try:
        config = artifact_accessors.load_omp_config(config_path)
        if "claude" not in (config.get("disabledProviders") or []):
            errors.append(".omp/config.yml does not disable Claude discovery")
        if ((config.get("task") or {}).get("maxRecursionDepth")) != 3:
            errors.append(".omp/config.yml task.maxRecursionDepth must be 3")
        if ((config.get("async") or {}).get("enabled")) is not True:
            errors.append(".omp/config.yml async.enabled must be true")
        if ((config.get("task") or {}).get("maxRuntimeMs")) != 0:
            errors.append(".omp/config.yml task.maxRuntimeMs must be 0")
        if ((config.get("task") or {}).get("structured", False)) is not False:
            errors.append(".omp/config.yml task.structured must stay unset or false: each harness "
                          "agent's frontmatter carries its digest schema")
        if config.get("modelRoles"):
            errors.append("concrete modelRoles belong in .omp/providers overlays, not .omp/config.yml")
    except artifact_accessors.ArtifactAccessError as exc:
        errors.append(f"cannot read .omp/config.yml: {exc}")
    return errors


def agent_files_errors(root: Path) -> list[str]:
    errors: list[str] = []
    agent_dir = root / ".omp" / "agents"
    actual_names: set[str] = set()
    for path in sorted(agent_dir.glob("harness-*.md")):
        try:
            meta = frontmatter(path)
        except (artifact_accessors.ArtifactAccessError, OSError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        name = str(meta.get("name") or "")
        actual_names.add(name)
        errors.extend(agent_file_errors(root, path, meta, name))
    # The roster itself is graded by the suites that load every agent (#2696); this guard only
    # keeps the per-agent checks above from passing vacuously when no agent file is found.
    if not actual_names:
        errors.append(f"no harness-*.md agent files under {agent_dir.relative_to(root)}")
    return errors


def agent_file_errors(root: Path, path: Path, meta: dict, name: str) -> list[str]:
    errors: list[str] = []
    model = meta.get("model")
    if model not in CAPABILITIES:
        errors.append(f"{path.relative_to(root)} must use a provider-neutral model alias")
    elif meta.get("thinking-level") != THINKING_FOR_CAPABILITY[model]:
        errors.append(
            f"{path.relative_to(root)}: {model} requires thinking-level "
            f"{THINKING_FOR_CAPABILITY[model]!r}, got {meta.get('thinking-level')!r}"
        )
    if name == "harness-orchestrator":
        if meta.get("blocking"):
            errors.append(f"{path.relative_to(root)} must remain background-dispatched from main")
    elif meta.get("blocking") is not True:
        errors.append(
            f"{path.relative_to(root)} must set blocking: true for nested OMP supervision"
        )
    # Kept by the #2698 review: OMP reads a `tools` mapping as an empty allowlist and only logs
    # a warning, and no suite catches that shape on an agent without bash.
    if not isinstance(meta.get("tools"), list):
        errors.append(f"{path.relative_to(root)} tools must be a list")
    if not isinstance(meta.get("spawns"), list):
        errors.append(f"{path.relative_to(root)} spawns must be an explicit list")
    marker = f"HARNESS_AGENT_ID: {name}"
    if marker not in path.read_text(encoding="utf-8"):
        errors.append(f"{path.relative_to(root)} lacks its stable HARNESS_AGENT_ID marker")
    errors.extend(agent_output_errors(root, path, meta, name))
    return errors


def typed_equal(a, b) -> bool:
    """Structural equality that never lets a bool stand in for an int (or either for a float):
    Python's own `{"a": False} == {"a": 0}` is True, so plain equality would pass a
    hand-edited `additionalProperties: 0`."""
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[key], b[key]) for key in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


def agent_output_errors(root: Path, path: Path, meta: dict, name: str) -> list[str]:
    """BUG-2565: an agent's yield is bound to its digest schema only through its frontmatter,
    so `structured: true` and an `output:` equal to the persona's projection are required."""
    rel = path.relative_to(root)
    errors = []
    if meta.get("structured") is not True:
        errors.append(f"{rel} must set structured: true so its yield is bound to its digest schema")
    try:
        bundle = digest_projection.provider_bundle(name, root / digest_projection.SCHEMA_RELPATH)
    except digest_projection.ProjectionError as exc:
        return [*errors, f"{rel}: digest schema for {name} cannot be projected: {exc}"]
    if not typed_equal(meta.get("output"), bundle):
        errors.append(f"{rel} output differs from schemas/digest/{name}.json; "
                      "run .claude/skills/harness/bin/gen-agent-output.py")
    return errors


def provider_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for filename, prefix in PROVIDER_PREFIX.items():
        errors.extend(provider_file_errors(root, root / ".omp" / "providers" / filename, prefix))
    return errors


def provider_file_errors(root: Path, path: Path, prefix: str) -> list[str]:
    try:
        roles = (artifact_accessors.load_omp_config(path).get("modelRoles") or {})
    except artifact_accessors.ArtifactAccessError as exc:
        return [f"cannot read {path.relative_to(root)}: {exc}"]
    errors: list[str] = []
    if set(roles) != {capability[1:] for capability in CAPABILITIES}:
        errors.append(f"{path.relative_to(root)} must map deep, strong, standard, and review")
    for role, selector in roles.items():
        if not str(selector).startswith(prefix):
            errors.append(f"{path.relative_to(root)} role {role} must select {prefix}*")
    return errors


def door_errors(root: Path) -> list[str]:
    command_dir = root / ".omp" / "commands"
    return [f".omp/commands/{door}.md is missing; {door} has no provider-neutral door"
            for door in REQUIRED_DOORS if not (command_dir / f"{door}.md").is_file()]


CHECKS = (
    agents_md_errors,
    config_errors,
    agent_files_errors,
    provider_errors,
    door_errors,
)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[4]).resolve()
    errors = check(root)
    if errors:
        for error in errors:
            print(f"OMP-PORT: {error}", file=sys.stderr)
        return 1
    print("OMP port surface: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
