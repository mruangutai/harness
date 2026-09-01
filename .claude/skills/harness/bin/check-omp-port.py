#!/usr/bin/env python3
"""Deterministically verify the provider-neutral OMP Harness surface."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

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
CAPABILITIES = {"@deep", "@strong", "@standard", "@review"}
PROVIDER_PREFIX = {
    "openai.yml": "openai-codex/",
    "anthropic.yml": "anthropic/",
}


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError("missing frontmatter delimiters")
    end = lines.index("---", 1)
    data = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def check(root: Path) -> list[str]:
    errors: list[str] = []
    agents_md = root / "AGENTS.md"
    claude_md = root / "CLAUDE.md"
    if not agents_md.is_file():
        errors.append("AGENTS.md is missing; OMP has no provider-neutral project guidance")
    if not claude_md.is_file() or "@AGENTS.md" not in claude_md.read_text(encoding="utf-8"):
        errors.append("CLAUDE.md does not import AGENTS.md")

    config_path = root / ".omp" / "config.yml"
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
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
    except Exception as exc:
        errors.append(f"cannot read .omp/config.yml: {exc}")

    agent_dir = root / ".omp" / "agents"
    actual_names: set[str] = set()
    for path in sorted(agent_dir.glob("harness-*.md")):
        try:
            meta = frontmatter(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        name = str(meta.get("name") or "")
        actual_names.add(name)
        if meta.get("model") not in CAPABILITIES:
            errors.append(f"{path.relative_to(root)} must use a provider-neutral model alias")
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
            roles = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("modelRoles") or {}
            if set(roles) != {capability[1:] for capability in CAPABILITIES}:
                errors.append(f"{path.relative_to(root)} must map deep, strong, standard, and review")
            for role, selector in roles.items():
                if not str(selector).startswith(prefix):
                    errors.append(f"{path.relative_to(root)} role {role} must select {prefix}*")
        except Exception as exc:
            errors.append(f"cannot read {path.relative_to(root)}: {exc}")

    claude_skills = root / ".claude" / "skills"
    agent_skills = root / ".agents" / "skills"
    if not claude_skills.is_dir() or claude_skills.is_symlink():
        errors.append(".claude/skills must be the real authored skill directory")
    try:
        if not agent_skills.is_symlink() or agent_skills.resolve() != claude_skills.resolve():
            errors.append(".agents/skills must be a symlink to .claude/skills")
    except OSError as exc:
        errors.append(f"cannot resolve .agents/skills compatibility link: {exc}")

    extension = root / ".omp" / "extensions" / "harness-hooks.ts"
    if not extension.is_file():
        errors.append(".omp/extensions/harness-hooks.ts is missing")
    else:
        source = extension.read_text(encoding="utf-8")
        required_wiring = {
            "dispatch-guard.sh": "OMP task preflight",
            "task:subagent:lifecycle": "OMP task terminal lifecycle",
            "gh-close-gate.sh": "GitHub close preflight",
            "inflight_registry.py": "OMP claim attachment and release",
            # BUG-1132: absent here until this fix, so plan-sign-gate.sh's own absence from
            # harness-hooks.ts's bash gate list — REQ-05/DEC-120's only enforcement — went
            # undetected. required_wiring is a spot-check, not an enumeration of every gate
            # script; this entry closes the one instance that was actually missing, not the
            # general class.
            "plan-sign-gate.sh": "sign-approval identity preflight",
        }
        for marker, purpose in required_wiring.items():
            if marker not in source:
                errors.append(f".omp/extensions/harness-hooks.ts lacks {purpose} ({marker})")

    sync = root / ".agents" / "skills" / "harness" / "bin" / "sync-agent-adapters.py"
    if sync.is_file():
        result = subprocess.run(
            [sys.executable, str(sync), "--root", str(root), "--check"],
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            errors.append(result.stderr.strip() or "Claude agent adapters are stale")
    else:
        errors.append("sync-agent-adapters.py is missing")
    return errors


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
