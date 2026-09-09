#!/usr/bin/env python3
"""Behavior tests for check-omp-port.py."""

from __future__ import annotations
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)

import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / ".claude/skills/harness/bin/check-omp-port.py"
SYNC_COMMAND_ADAPTERS = ROOT / ".claude/skills/harness/bin/sync-command-adapters.py"


def _sync_command_adapters_module():
    """Load sync-command-adapters.py's own REQUIRED_DOORS list at runtime — pins this file's
    door names to that module's list behaviourally, never by grepping either source's text."""
    spec = importlib.util.spec_from_file_location("_sync_command_adapters_under_test", SYNC_COMMAND_ADAPTERS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CHECK), str(root)], text=True, capture_output=True)


def fixture() -> tuple[tempfile.TemporaryDirectory, Path]:
    td = tempfile.TemporaryDirectory()
    dst = Path(td.name)
    for rel in (".omp", ".agents", ".claude"):
        src = ROOT / rel
        shutil.copytree(src, dst / rel, symlinks=True)
    shutil.copy2(ROOT / "AGENTS.md", dst / "AGENTS.md")
    shutil.copy2(ROOT / "CLAUDE.md", dst / "CLAUDE.md")
    return td, dst


def case_symlink_topology():
    claude_skills = ROOT / ".claude" / "skills"
    canonical_link = ROOT / ".agents" / "skills"
    return [
        (
            "Claude skills remain a real directory",
            claude_skills.is_dir() and not claude_skills.is_symlink(),
            "",
        ),
        (
            "Agent Skills path links to Claude skills",
            canonical_link.is_symlink() and canonical_link.resolve() == claude_skills.resolve(),
            "",
        ),
    ]


def case_live_tree_passes():
    clean = run(ROOT)
    # FEAT-56 T-14 (F4): EXPECTED TO FAIL until the main session regenerates
    # .claude/commands/** via sync-command-adapters.py --apply (new banner text).
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


def case_stale_claude_adapter_fails():
    td, root = fixture()
    try:
        adapter = root / ".claude" / "agents" / "harness-backend-dev.md"
        adapter.write_text(adapter.read_text() + "drift\n")
        result = run(root)
        return [
            ("stale Claude adapter fails", result.returncode == 1, ""),
            ("adapter drift is named", "adapters are stale" in result.stderr, ""),
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
    """BUG-1132: plan-sign-gate.sh (REQ-05/DEC-120) is wired into `.claude/settings.json` for
    native Claude Code, and was silently absent from harness-hooks.ts's own bash gate list
    until this fix — invisible to this checker because the script was never in
    `required_wiring`. This proves the checker would now catch that class of gap recurring
    for ANY gate script, not just this one instance."""
    td, root = fixture()
    try:
        extension = root / ".omp" / "extensions" / "harness-hooks.ts"
        extension.write_text(extension.read_text().replace("plan-sign-gate.sh", "plan-sign-gate-REMOVED.sh"))
        result = run(root)
        return [
            ("missing plan-sign-gate.sh wiring fails", result.returncode == 1, ""),
            ("sign-gate wiring gap is named", "plan-sign-gate.sh" in result.stderr, ""),
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


def case_required_doors_pinned_to_sync_command_adapters():
    """F3/T-14: sync-command-adapters.py's REQUIRED_DOORS is a second copy of this file's own
    door tuple (check-omp-port.py:169). Load it at runtime and prove, one door at a time, that
    deleting any single required door is still caught here — pins the two lists together
    behaviourally instead of trusting them to stay hand-synchronized."""
    results = []
    for door in _sync_command_adapters_module().REQUIRED_DOORS:
        td, root = fixture()
        try:
            (root / ".omp" / "commands" / door).unlink()
            result = run(root)
            results.append((f"check-omp-port also reports {door} missing", result.returncode == 1, ""))
            results.append((f"{door} missing is named in check-omp-port output", door in result.stderr, ""))
        finally:
            td.cleanup()
    return results


CASES = (
    case_symlink_topology,
    case_live_tree_passes,
    case_missing_agents_md_fails,
    case_concrete_model_in_canonical_fails,
    case_stale_claude_adapter_fails,
    case_missing_async_enablement_fails,
    case_task_wall_clock_limit_fails,
    case_missing_lifecycle_wiring_fails,
    case_missing_sign_gate_wiring_fails,
    case_nonblocking_nested_agent_fails,
    case_missing_command_door_fails,
    case_absent_canonical_command_root_fails,
    case_required_doors_pinned_to_sync_command_adapters,
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
