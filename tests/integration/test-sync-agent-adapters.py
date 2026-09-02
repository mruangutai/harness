#!/usr/bin/env python3
"""Behavior tests for provider-neutral OMP agents and Claude adapters."""

from __future__ import annotations
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

SCRIPT = Path(_anchor_bin) / "sync-agent-adapters.py"

SOURCE = """---
name: harness-backend-dev
description: Backend engineer: owns server behavior.
tools: [Read, Glob, Grep, Edit, Write, Bash]
color: cyan
model: sonnet
effort: medium
skills:
  - harness-handoff
  - harness-expertise
---

# Backend

Do the bounded backend task.
"""


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    _, raw, body = text.split("---", 2)
    return yaml.safe_load(raw), body.lstrip("\n")


def main() -> int:
    failures = 0

    def check(label: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        if ok:
            print(f"ok    {label}")
        else:
            failures += 1
            print(f"FAIL  {label}" + (f" — {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        source = root / ".claude" / "agents" / "harness-backend-dev.md"
        source.parent.mkdir(parents=True)
        source.write_text(SOURCE, encoding="utf-8")

        boot = run(root, "--bootstrap-from-claude")
        check("bootstrap exits 0", boot.returncode == 0, boot.stderr)

        canonical = root / ".omp" / "agents" / source.name
        check("bootstrap creates OMP canonical agent", canonical.is_file())
        meta, body = frontmatter(canonical)
        check("name preserved", meta.get("name") == "harness-backend-dev")
        check("colon-bearing description preserved", meta.get("description") == "Backend engineer: owns server behavior.")
        check("tools normalize to OMP names", meta.get("tools") == ["read", "glob", "grep", "edit", "write", "bash"])
        check("model becomes provider-neutral alias", meta.get("model") == "@standard")
        check("thinking level preserved", meta.get("thinking-level") == "medium")
        check("skills become autoloadSkills", meta.get("autoloadSkills") == ["harness-handoff", "harness-expertise"])
        check("leaf spawn policy is explicit", meta.get("spawns") == [])
        check("body gains a stable identity marker",
              body == "HARNESS_AGENT_ID: harness-backend-dev\n\n"
                      "# Backend\n\nDo the bounded backend task.\n")

        apply = run(root, "--apply")
        check("Claude adapter apply exits 0", apply.returncode == 0, apply.stderr)
        cmeta, cbody = frontmatter(source)
        check("Claude model mapping restored", cmeta.get("model") == "sonnet")
        check("Claude effort restored", cmeta.get("effort") == "medium")
        check("Claude tools restored", cmeta.get("tools") == ["Read", "Glob", "Grep", "Edit", "Write", "Bash"])
        check("Claude skills restored", cmeta.get("skills") == ["harness-handoff", "harness-expertise"])
        check("Claude body matches canonical", cbody == body)

        clean = run(root, "--check")
        check("check accepts synchronized adapters", clean.returncode == 0, clean.stderr)

        source.write_text(source.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
        drift = run(root, "--check")
        check("check rejects drift", drift.returncode == 1)
        check("drift output names adapter", "harness-backend-dev.md" in drift.stderr)

    print(f"\n{18 - failures}/18 cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
