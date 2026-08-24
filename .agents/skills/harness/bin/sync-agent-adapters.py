#!/usr/bin/env python3
"""Bootstrap OMP-native Harness agents and generate Claude Code adapters.

Canonical role policy lives in `.omp/agents`. Claude files are generated
compatibility adapters; edit the OMP source, then run `--apply`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

TO_OMP_TOOL = {
    "Read": "read",
    "Glob": "glob",
    "Grep": "grep",
    "Edit": "edit",
    "Write": "write",
    "Bash": "bash",
    "WebSearch": "web_search",
    "WebFetch": "web_fetch",
    "Agent": "task",
    "Task": "task",
    "Skill": "skill",
}
TO_CLAUDE_TOOL = {value: key for key, value in TO_OMP_TOOL.items()}
TO_CLAUDE_TOOL["task"] = "Agent"

CAPABILITY_FROM_CLAUDE = {
    ("opus", "high"): "@deep",
    ("opus", "medium"): "@strong",
    ("sonnet", "medium"): "@standard",
    ("sonnet", "high"): "@review",
}
CLAUDE_FROM_CAPABILITY = {
    "@deep": ("opus", "high"),
    "@strong": ("opus", "medium"),
    "@standard": ("sonnet", "medium"),
    "@review": ("sonnet", "high"),
}

SPAWNS = {
    "harness-orchestrator": [
        "harness-product-lead",
        "harness-eng-lead",
        "harness-validator-lead",
    ],
    "harness-product-lead": [
        "harness-pm",
        "harness-visual-designer",
        "harness-documentor",
    ],
    "harness-eng-lead": [
        "harness-frontend-dev",
        "harness-backend-dev",
        "harness-ai-dev",
        "harness-data-engineer",
        "harness-dev-ops",
    ],
    "harness-validator-lead": [
        "harness-qa",
        "harness-code-reviewer",
        "harness-security-reviewer",
        "harness-ui-reviewer",
    ],
}

COLORS = {
    "harness-orchestrator": "blue",
    "harness-product-lead": "purple",
    "harness-pm": "purple",
    "harness-visual-designer": "purple",
    "harness-documentor": "purple",
    "harness-validator-lead": "orange",
    "harness-qa": "orange",
    "harness-code-reviewer": "orange",
    "harness-security-reviewer": "orange",
    "harness-ui-reviewer": "orange",
}


def split_document(text: str, path: Path) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: missing closing frontmatter delimiter") from exc
    body = "\n".join(lines[end + 1 :]).lstrip("\n") + "\n"
    return "\n".join(lines[1:end]), body


def parse_legacy_frontmatter(raw: str, path: Path) -> dict:
    """Parse Claude's permissive frontmatter, including unquoted colons."""
    result: dict[str, object] = {}
    current: str | None = None
    for line in raw.splitlines():
        if line.startswith("  - ") and current:
            value = line[4:].split(" #", 1)[0].strip()
            bucket = result.setdefault(current, [])
            if not isinstance(bucket, list):
                raise ValueError(f"{path}: {current} mixes scalar and list values")
            bucket.append(value)
            continue
        if line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        current = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            result[current] = [part.strip() for part in value[1:-1].split(",") if part.strip()]
        elif not value:
            result[current] = []
        else:
            result[current] = value
    return result


def parse_canonical(path: Path) -> tuple[dict, str]:
    raw, body = split_document(path.read_text(encoding="utf-8"), path)
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return data, body


def render(meta: dict, body: str) -> str:
    frontmatter = yaml.safe_dump(
        meta,
        sort_keys=False,
        allow_unicode=True,
        width=1000,
        default_flow_style=False,
    ).rstrip()
    return f"---\n{frontmatter}\n---\n\n{body}"


def bootstrap_one(path: Path) -> str:
    raw, body = split_document(path.read_text(encoding="utf-8"), path)
    source = parse_legacy_frontmatter(raw, path)
    name = str(source.get("name") or "")
    description = str(source.get("description") or "")
    model = str(source.get("model") or "")
    effort = str(source.get("effort") or "")
    if not name or not description:
        raise ValueError(f"{path}: name and description are required")
    try:
        capability = CAPABILITY_FROM_CLAUDE[(model, effort)]
    except KeyError as exc:
        raise ValueError(f"{path}: unsupported Claude model/effort pair {model!r}/{effort!r}") from exc

    source_tools = source.get("tools") or []
    source_skills = source.get("skills") or []
    if not isinstance(source_tools, list) or not isinstance(source_skills, list):
        raise ValueError(f"{path}: tools and skills must be lists")
    try:
        tools = [TO_OMP_TOOL[str(tool)] for tool in source_tools]
    except KeyError as exc:
        raise ValueError(f"{path}: unsupported Claude tool {exc.args[0]!r}") from exc

    spawns = list(SPAWNS.get(name, []))
    if spawns and "task" not in tools:
        raise ValueError(f"{path}: spawning agent {name} lacks Agent/task tool")
    if not spawns and "task" in tools:
        raise ValueError(f"{path}: leaf agent {name} unexpectedly has Agent/task tool")

    canonical = {
        "name": name,
        "description": description,
        "tools": tools,
        "spawns": spawns,
        "model": capability,
        "thinking-level": effort,
        "autoloadSkills": [str(skill) for skill in source_skills],
    }
    marker = f"HARNESS_AGENT_ID: {name}\n\n"
    return render(canonical, body if body.startswith(marker) else marker + body)


def claude_adapter(path: Path) -> str:
    canonical, body = parse_canonical(path)
    name = str(canonical.get("name") or "")
    description = str(canonical.get("description") or "")
    capability = str(canonical.get("model") or "")
    thinking = str(canonical.get("thinking-level") or "")
    if not name or not description:
        raise ValueError(f"{path}: name and description are required")
    try:
        model, expected_effort = CLAUDE_FROM_CAPABILITY[capability]
    except KeyError as exc:
        raise ValueError(f"{path}: unsupported provider-neutral capability {capability!r}") from exc
    if thinking != expected_effort:
        raise ValueError(
            f"{path}: {capability} requires thinking-level {expected_effort!r}, got {thinking!r}"
        )

    raw_tools = canonical.get("tools") or []
    raw_skills = canonical.get("autoloadSkills") or []
    if not isinstance(raw_tools, list) or not isinstance(raw_skills, list):
        raise ValueError(f"{path}: tools and autoloadSkills must be lists")
    try:
        tools = [TO_CLAUDE_TOOL[str(tool)] for tool in raw_tools]
    except KeyError as exc:
        raise ValueError(f"{path}: no Claude adapter for OMP tool {exc.args[0]!r}") from exc

    adapter = {
        "name": name,
        "description": description,
        "tools": tools,
        "color": COLORS.get(name, "cyan"),
        "model": model,
        "effort": thinking,
        "skills": [str(skill) for skill in raw_skills],
    }
    return render(adapter, body)


def expected_adapters(canonical_dir: Path) -> dict[str, str]:
    paths = sorted(canonical_dir.glob("harness-*.md"))
    if not paths:
        raise ValueError(f"{canonical_dir}: no Harness agents found")
    result: dict[str, str] = {}
    names: set[str] = set()
    for path in paths:
        data, _ = parse_canonical(path)
        name = str(data.get("name") or "")
        if name in names:
            raise ValueError(f"{path}: duplicate agent name {name!r}")
        names.add(name)
        result[path.name] = claude_adapter(path)
    return result


def bootstrap(root: Path) -> None:
    source_dir = root / ".claude" / "agents"
    target_dir = root / ".omp" / "agents"
    sources = sorted(source_dir.glob("harness-*.md"))
    if not sources:
        raise ValueError(f"{source_dir}: no Claude Harness agents found")
    if target_dir.exists() and any(target_dir.glob("harness-*.md")):
        raise ValueError(f"{target_dir}: canonical agents already exist; refusing to overwrite")
    target_dir.mkdir(parents=True, exist_ok=True)
    for source in sources:
        (target_dir / source.name).write_text(bootstrap_one(source), encoding="utf-8")


def sync(root: Path, check: bool) -> int:
    canonical_dir = root / ".omp" / "agents"
    adapter_dir = root / ".claude" / "agents"
    expected = expected_adapters(canonical_dir)
    actual_names = {path.name for path in adapter_dir.glob("harness-*.md")} if adapter_dir.exists() else set()
    expected_names = set(expected)
    drift: list[str] = []

    for name, content in expected.items():
        target = adapter_dir / name
        if not target.is_file() or target.read_text(encoding="utf-8") != content:
            drift.append(name)
            if not check:
                adapter_dir.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
    for name in sorted(actual_names - expected_names):
        drift.append(name)
        if not check:
            (adapter_dir / name).unlink()

    if check and drift:
        print("Claude agent adapters are stale: " + ", ".join(sorted(set(drift))), file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--bootstrap-from-claude", action="store_true")
    action.add_argument("--apply", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.bootstrap_from_claude:
            bootstrap(root)
            return 0
        return sync(root, check=args.check)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"sync-agent-adapters: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
