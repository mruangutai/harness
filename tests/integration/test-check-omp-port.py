#!/usr/bin/env python3
"""Behavior tests for check-omp-port.py."""

from __future__ import annotations
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / ".claude/skills/harness/bin/check-omp-port.py"

def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CHECK), str(root)], text=True, capture_output=True)


def fixture() -> tuple[tempfile.TemporaryDirectory, Path]:
    td = tempfile.TemporaryDirectory()
    dst = Path(td.name)
    # `.claude/worktrees/` holds every live feature checkout — ~1 GB here, growing with
    # concurrent feature work — and check-omp-port.py never reads it: its only traversal is
    # `agent_dir.glob("harness-*.md")`. Copying it made this file 239s of the integration
    # suite's 240s wall clock (issue #1525).
    skip_worktrees = shutil.ignore_patterns("worktrees")
    for rel in (".omp", ".agents", ".claude"):
        src = ROOT / rel
        shutil.copytree(src, dst / rel, symlinks=True, ignore=skip_worktrees)
    shutil.copy2(ROOT / "AGENTS.md", dst / "AGENTS.md")
    manual = dst / "tests" / "manual"
    manual.mkdir(parents=True)
    for suffix in ("py", "ts"):
        shutil.copy2(
            ROOT / "tests" / "manual" / f"probe-omp-runtime-lineage.{suffix}",
            manual / f"probe-omp-runtime-lineage.{suffix}",
        )
    return td, dst


def case_symlink_topology():
    claude_skills = ROOT / ".claude" / "skills"
    canonical_link = ROOT / ".agents" / "skills"
    return [
        (
            "Agent Skills path links to the authored skills tree",
            canonical_link.is_symlink() and canonical_link.resolve() == claude_skills.resolve(),
            "",
        ),
    ]


# GRADE-2 REASON: the strict-reader contract is one ordered integration scenario across
# config, agent frontmatter, and provider YAML; each mutation requires a fresh fixture.
def case_live_tree_passes():
    clean = run(ROOT)
    td, strict_root = fixture()
    try:
        config = strict_root / ".omp" / "config.yml"
        config.write_text(
            config.read_text(encoding="utf-8")
            + "\nasync:\n  enabled: true\n",
            encoding="utf-8",
        )
        duplicate_config = run(strict_root)
        assert duplicate_config.returncode == 1 and "duplicate key" in (
            duplicate_config.stderr), duplicate_config.stderr

        td.cleanup()
        td, strict_root = fixture()
        agent = strict_root / ".omp" / "agents" / "harness-backend-dev.md"
        text = agent.read_text(encoding="utf-8")
        agent.write_text(
            text.replace(
                "name: harness-backend-dev",
                "name: harness-backend-dev\nname: harness-backend-dev",
                1,
            ),
            encoding="utf-8",
        )
        duplicate_frontmatter = run(strict_root)
        assert duplicate_frontmatter.returncode == 1 and "duplicate key" in (
            duplicate_frontmatter.stderr), duplicate_frontmatter.stderr

        td.cleanup()
        td, strict_root = fixture()
        provider = strict_root / ".omp" / "providers" / "openai.yml"
        text = provider.read_text(encoding="utf-8")
        provider.write_text(text + "\n" + text, encoding="utf-8")
        duplicate_provider = run(strict_root)
        assert duplicate_provider.returncode == 1 and "duplicate key" in (
            duplicate_provider.stderr), duplicate_provider.stderr
    finally:
        td.cleanup()
    return [("live provider-neutral tree passes", clean.returncode == 0, clean.stderr)]


def case_missing_agents_md_fails():
    td, root = fixture()
    try:
        (root / "AGENTS.md").unlink()
        result = run(root)
        return [
            ("missing AGENTS.md fails", result.returncode == 1, ""),
            ("missing guidance is named", "AGENTS.md" in result.stderr, ""),
        ]
    finally:
        td.cleanup()


def case_concrete_model_in_canonical_fails():
    td, root = fixture()
    try:
        agent = root / ".omp" / "agents" / "harness-backend-dev.md"
        agent.write_text(agent.read_text().replace("model: '@standard'", "model: anthropic/claude-sonnet-5"))
        result = run(root)
        return [
            ("concrete model in canonical agent fails", result.returncode == 1, ""),
            ("provider coupling is named", "provider-neutral model alias" in result.stderr, ""),
        ]
    finally:
        td.cleanup()


def case_thinking_level_disagrees_with_alias_fails():
    """DEC-233: the alias↔thinking-level pairing was enforced only by the deleted
    sync-agent-adapters.py. A `@review` role at `medium` must be refused here, naming both."""
    td, root = fixture()
    try:
        agent = root / ".omp" / "agents" / "harness-code-reviewer.md"
        agent.write_text(agent.read_text().replace("thinking-level: high", "thinking-level: medium"))
        result = run(root)
        return [
            ("thinking-level disagreeing with alias fails", result.returncode == 1, result.stderr),
            ("both values are named", "@review" in result.stderr and "medium" in result.stderr, result.stderr),
        ]
    finally:
        td.cleanup()


def case_missing_async_enablement_fails():
    td, root = fixture()
    try:
        config = root / ".omp" / "config.yml"
        config.write_text(config.read_text().replace("async:\n  enabled: true\n", ""))
        result = run(root)
        return [
            ("missing explicit async enablement fails", result.returncode == 1, ""),
            ("async liveness contract is named", "async.enabled" in result.stderr, ""),
        ]
    finally:
        td.cleanup()


def case_task_wall_clock_limit_fails():
    td, root = fixture()
    try:
        config = root / ".omp" / "config.yml"
        config.write_text(config.read_text().replace("maxRuntimeMs: 0", "maxRuntimeMs: 60000"))
        result = run(root)
        return [
            ("task wall clock limit fails", result.returncode == 1, ""),
            ("wall-clock contract is named", "task.maxRuntimeMs" in result.stderr, ""),
        ]
    finally:
        td.cleanup()


def case_missing_lifecycle_wiring_fails():
    td, root = fixture()
    try:
        extension = root / ".omp" / "extensions" / "harness-hooks.ts"
        extension.write_text(extension.read_text().replace("task:subagent:lifecycle", "task:lifecycle"))
        result = run(root)
        return [
            ("missing OMP child lifecycle wiring fails", result.returncode == 1, ""),
            ("lifecycle wiring gap is named", "task:subagent:lifecycle" in result.stderr, ""),
        ]
    finally:
        td.cleanup()


def case_missing_sign_gate_wiring_fails():
    """BUG-1132: plan-sign-gate.py (REQ-05/DEC-120) was silently absent from
    harness-hooks.ts's own bash gate list until this fix — invisible to this checker because
    the script was never in `required_wiring`. This proves the checker would now catch that
    class of gap recurring for ANY gate script, not just this one instance."""
    td, root = fixture()
    try:
        extension = root / ".omp" / "extensions" / "harness-hooks.ts"
        extension.write_text(extension.read_text().replace("plan-sign-gate.py", "plan-sign-gate-REMOVED.sh"))
        result = run(root)
        return [
            ("missing plan-sign-gate.py wiring fails", result.returncode == 1, ""),
            ("sign-gate wiring gap is named", "plan-sign-gate.py" in result.stderr, ""),
        ]
    finally:
        td.cleanup()


def case_nonblocking_nested_agent_fails():
    td, root = fixture()
    try:
        agent = root / ".omp" / "agents" / "harness-backend-dev.md"
        agent.write_text(agent.read_text().replace("blocking: true\n", ""))
        result = run(root)
        return [
            ("nonblocking nested Harness agent fails", result.returncode == 1, ""),
            ("nested supervision contract is named", "blocking: true" in result.stderr, ""),
        ]
    finally:
        td.cleanup()

def case_missing_runtime_pin_fails():
    td, root = fixture()
    try:
        (root / ".omp" / "runtime-pin.json").unlink()
        result = run(root)
        return [
            ("missing OMP runtime pin fails", result.returncode == 1, ""),
            ("missing runtime pin is named", "runtime-pin.json" in result.stderr, result.stderr),
        ]
    finally:
        td.cleanup()


def case_malformed_runtime_pin_fails():
    td, root = fixture()
    try:
        pin = root / ".omp" / "runtime-pin.json"
        pin.write_text('{"repository":"https://example.invalid/repo.git","ref":"moving","commit":"main"}')
        result = run(root)
        return [
            ("malformed OMP runtime pin fails", result.returncode == 1, ""),
            ("immutable commit requirement is named", "40-character Git commit" in result.stderr,
             result.stderr),
        ]
    finally:
        td.cleanup()


def case_missing_command_door_fails():
    td, root = fixture()
    try:
        (root / ".omp" / "commands" / "harness-ship.md").unlink()
        result = run(root)
        return [
            ("missing command door fails", result.returncode == 1, ""),
            ("missing door is named", "harness-ship.md" in result.stderr, ""),
        ]
    finally:
        td.cleanup()


def case_absent_canonical_command_root_fails():
    td, root = fixture()
    try:
        shutil.rmtree(root / ".omp" / "commands")
        result = run(root)
        missing_doors = sum(
            1 for door in ("harness", "harness-plan", "harness-ship", "harness-grilling")
            if f".omp/commands/{door}.md is missing" in result.stderr
        )
        return [
            ("absent canonical command root fails", result.returncode == 1, ""),
            ("absent canonical root names all four doors", missing_doors == 4, result.stderr),
        ]
    finally:
        td.cleanup()



CASES = (
    case_symlink_topology,
    case_live_tree_passes,
    case_missing_agents_md_fails,
    case_concrete_model_in_canonical_fails,
    case_thinking_level_disagrees_with_alias_fails,
    case_missing_async_enablement_fails,
    case_task_wall_clock_limit_fails,
    case_missing_lifecycle_wiring_fails,
    case_missing_sign_gate_wiring_fails,
    case_nonblocking_nested_agent_fails,
    case_missing_runtime_pin_fails,
    case_malformed_runtime_pin_fails,
    case_missing_command_door_fails,
    case_absent_canonical_command_root_fails,
)


def main() -> int:
    results = []
    for case in CASES:
        results.extend(case())

    failures = 0
    for label, ok, detail in results:
        if ok:
            print(f"ok    {label}")
        else:
            failures += 1
            print(f"FAIL  {label}" + (f" — {detail}" if detail else ""))

    print(f"\n{len(results) - failures}/{len(results)} cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
