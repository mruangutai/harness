#!/usr/bin/env python3
"""Deterministically verify the provider-neutral OMP Harness surface."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import artifact_accessors

EXPECTED_AGENTS = {
    "harness-ai-dev",
    "harness-backend-dev",
    "harness-code-reviewer",
    "harness-data-engineer",
    "harness-dev-ops",
    "harness-documentor",
    "harness-eng-lead",
    "harness-frontend-dev",
    "harness-orchestrator",
    "harness-pm",
    "harness-product-lead",
    "harness-qa",
    "harness-security-reviewer",
    "harness-ui-reviewer",
    "harness-validator-lead",
    "harness-visual-designer",
}
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

def runtime_pin_errors(root: Path) -> list[str]:
    runtime_pin = root / ".omp" / "runtime-pin.json"
    try:
        pin = json.loads(runtime_pin.read_text(encoding="utf-8"))
        if not isinstance(pin, dict):
            raise ValueError("root must be an object")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [f"cannot read .omp/runtime-pin.json: {exc}"]
    requirements = (
        (re.fullmatch(r"[0-9a-f]{40}", str(pin.get("commit") or "")) is not None,
         ".omp/runtime-pin.json commit must be a 40-character Git commit"),
        (str(pin.get("repository") or "").endswith("/oh-my-pi.git"),
         ".omp/runtime-pin.json repository must identify the downstream OMP fork"),
        (str(pin.get("ref") or "").startswith("harness-runtime-lineage-"),
         ".omp/runtime-pin.json ref must identify an immutable Harness lineage tag"),
        (pin.get("required_capability") == "extension-context-runtime-lineage",
         ".omp/runtime-pin.json must require extension-context-runtime-lineage"),
    )
    return [message for satisfied, message in requirements if not satisfied]


def runtime_probe_errors(root: Path) -> list[str]:
    probes = (
        root / "tests" / "manual" / "probe-omp-runtime-lineage.py",
        root / "tests" / "manual" / "probe-omp-runtime-lineage.ts",
    )
    return [f"{probe.relative_to(root)} is missing" for probe in probes if not probe.is_file()]



# BUG-1898 defect D: OMP emits task:subagent:lifecycle on the session EventBus that an
# extension reaches as `pi.events`; `pi.on` is the hook dispatcher and never delivers it.
# The marker string alone is present in both forms, so the registration shape is checked.
_LIFECYCLE_ON_EVENTS = re.compile(r"""\bpi\.events\.on\(\s*(["'])task:subagent:lifecycle\1""")
_LIFECYCLE_ON_HOOKS = re.compile(r"""\bpi\.on\(\s*(["'])task:subagent:lifecycle\1""")


def lifecycle_bus_errors(source: str) -> list[str]:
    errors = []
    if _LIFECYCLE_ON_HOOKS.search(source):
        errors.append(".omp/extensions/harness-hooks.ts registers task:subagent:lifecycle on "
                      "pi.on, which never delivers it; register it on pi.events")
    if not _LIFECYCLE_ON_EVENTS.search(source):
        errors.append(".omp/extensions/harness-hooks.ts has no task:subagent:lifecycle "
                      "listener on pi.events; terminal children are never released")
    return errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    agents_md = root / "AGENTS.md"
    if not agents_md.is_file():
        errors.append("AGENTS.md is missing; OMP has no provider-neutral project guidance")

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
        if config.get("modelRoles"):
            errors.append("concrete modelRoles belong in .omp/providers overlays, not .omp/config.yml")
    except artifact_accessors.ArtifactAccessError as exc:
        errors.append(f"cannot read .omp/config.yml: {exc}")

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
        if not isinstance(meta.get("tools"), list):
            errors.append(f"{path.relative_to(root)} tools must be a list")
        if not isinstance(meta.get("spawns"), list):
            errors.append(f"{path.relative_to(root)} spawns must be an explicit list")
        skills = meta.get("autoloadSkills")
        if not isinstance(skills, list):
            errors.append(f"{path.relative_to(root)} autoloadSkills must be a list")
        else:
            for skill in skills:
                if not (root / ".agents" / "skills" / str(skill) / "SKILL.md").is_file():
                    errors.append(f"{path.relative_to(root)} references missing skill {skill!r}")
        marker = f"HARNESS_AGENT_ID: {name}"
        if marker not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(root)} lacks its stable HARNESS_AGENT_ID marker")
    if actual_names != EXPECTED_AGENTS:
        errors.append(
            "OMP agent roster mismatch: missing=%s extra=%s"
            % (sorted(EXPECTED_AGENTS - actual_names), sorted(actual_names - EXPECTED_AGENTS))
        )

    for filename, prefix in PROVIDER_PREFIX.items():
        path = root / ".omp" / "providers" / filename
        try:
            roles = (artifact_accessors.load_omp_config(path).get("modelRoles") or {})
            if set(roles) != {capability[1:] for capability in CAPABILITIES}:
                errors.append(f"{path.relative_to(root)} must map deep, strong, standard, and review")
            for role, selector in roles.items():
                if not str(selector).startswith(prefix):
                    errors.append(f"{path.relative_to(root)} role {role} must select {prefix}*")
        except artifact_accessors.ArtifactAccessError as exc:
            errors.append(f"cannot read {path.relative_to(root)}: {exc}")

    claude_skills = root / ".claude" / "skills"
    agent_skills = root / ".agents" / "skills"
    try:
        if not agent_skills.is_symlink() or agent_skills.resolve() != claude_skills.resolve():
            errors.append(".agents/skills must be a symlink to the authored tree at .claude/skills")
    except OSError as exc:
        errors.append(f"cannot resolve .agents/skills link: {exc}")

    extension = root / ".omp" / "extensions" / "harness-hooks.ts"
    if not extension.is_file():
        errors.append(".omp/extensions/harness-hooks.ts is missing")
    else:
        source = extension.read_text(encoding="utf-8")
        required_wiring = {
            "dispatch-guard.py": "OMP task preflight",
            "gh-close-gate.py": "GitHub close preflight",
            "inflight_registry.py": "OMP claim attachment and release",
            # BUG-1132: absent here until this fix, so plan-sign-gate.py's own absence from
            # harness-hooks.ts's bash gate list — REQ-05/DEC-120's only enforcement — went
            # undetected. required_wiring is a spot-check, not an enumeration of every gate
            # script; this entry closes the one instance that was actually missing, not the
            # general class.
            "plan-sign-gate.py": "sign-approval identity preflight",
        }
        for marker, purpose in required_wiring.items():
            if marker not in source:
                errors.append(f".omp/extensions/harness-hooks.ts lacks {purpose} ({marker})")
        errors.extend(lifecycle_bus_errors(source))

    command_dir = root / ".omp" / "commands"
    for door in REQUIRED_DOORS:
        if not (command_dir / f"{door}.md").is_file():
            errors.append(f".omp/commands/{door}.md is missing; {door} has no provider-neutral door")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[4]).resolve()
    errors = check(root) + runtime_pin_errors(root) + runtime_probe_errors(root)
    if errors:
        for error in errors:
            print(f"OMP-PORT: {error}", file=sys.stderr)
        return 1
    print("OMP port surface: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
