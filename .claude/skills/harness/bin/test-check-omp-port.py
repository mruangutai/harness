#!/usr/bin/env python3
"""Behavior tests for check-omp-port.py."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECK = Path(__file__).with_name("check-omp-port.py")


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


def main() -> int:
    failures = 0

    def check(label: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        if ok:
            print(f"ok    {label}")
        else:
            failures += 1
            print(f"FAIL  {label}" + (f" — {detail}" if detail else ""))

    claude_skills = ROOT / ".claude" / "skills"
    canonical_link = ROOT / ".agents" / "skills"
    check(
        "Claude skills remain a real directory",
        claude_skills.is_dir() and not claude_skills.is_symlink(),
    )
    check(
        "Agent Skills path links to Claude skills",
        canonical_link.is_symlink() and canonical_link.resolve() == claude_skills.resolve(),
    )

    clean = run(ROOT)
    check("live provider-neutral tree passes", clean.returncode == 0, clean.stderr)

    td, root = fixture()
    try:
        (root / "AGENTS.md").unlink()
        result = run(root)
        check("missing AGENTS.md fails", result.returncode == 1)
        check("missing guidance is named", "AGENTS.md" in result.stderr)
    finally:
        td.cleanup()

    td, root = fixture()
    try:
        agent = root / ".omp" / "agents" / "harness-backend-dev.md"
        agent.write_text(agent.read_text().replace("model: '@standard'", "model: anthropic/claude-sonnet-5"))
        result = run(root)
        check("concrete model in canonical agent fails", result.returncode == 1)
        check("provider coupling is named", "provider-neutral model alias" in result.stderr)
    finally:
        td.cleanup()

    td, root = fixture()
    try:
        adapter = root / ".claude" / "agents" / "harness-backend-dev.md"
        adapter.write_text(adapter.read_text() + "drift\n")
        result = run(root)
        check("stale Claude adapter fails", result.returncode == 1)
        check("adapter drift is named", "adapters are stale" in result.stderr)
    finally:
        td.cleanup()
    td, root = fixture()
    try:
        config = root / ".omp" / "config.yml"
        config.write_text(config.read_text().replace("async:\n  enabled: true\n", ""))
        result = run(root)
        check("missing explicit async enablement fails", result.returncode == 1)
        check("async liveness contract is named", "async.enabled" in result.stderr)
    finally:
        td.cleanup()

    td, root = fixture()
    try:
        config = root / ".omp" / "config.yml"
        config.write_text(config.read_text().replace("maxRuntimeMs: 0", "maxRuntimeMs: 60000"))
        result = run(root)
        check("task wall clock limit fails", result.returncode == 1)
        check("wall-clock contract is named", "task.maxRuntimeMs" in result.stderr)
    finally:
        td.cleanup()

    td, root = fixture()
    try:
        extension = root / ".omp" / "extensions" / "harness-hooks.ts"
        extension.write_text(extension.read_text().replace("task:subagent:lifecycle", "task:lifecycle"))
        result = run(root)
        check("missing OMP child lifecycle wiring fails", result.returncode == 1)
        check("lifecycle wiring gap is named", "task:subagent:lifecycle" in result.stderr)
    finally:
        td.cleanup()


    td, root = fixture()
    try:
        agent = root / ".omp" / "agents" / "harness-backend-dev.md"
        agent.write_text(agent.read_text().replace("blocking: true\n", ""))
        result = run(root)
        check("nonblocking nested Harness agent fails", result.returncode == 1)
        check("nested supervision contract is named", "blocking: true" in result.stderr)
    finally:
        td.cleanup()



    print(f"\n{17 - failures}/17 cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
