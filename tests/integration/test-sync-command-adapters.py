#!/usr/bin/env python3
"""Behavior tests for sync-command-adapters.py."""

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

SCRIPT = Path(_anchor_bin) / "sync-command-adapters.py"

CANONICAL_HARNESS = "# /harness — run a feature flow\n\nDoor body one.\n"
CANONICAL_SHIP = "# /harness-ship — ship a feature\n\nDoor body two.\n"


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def banner(name: str) -> str:
    return f"<!-- Generated from .omp/commands/{name}; do not edit. Run bin/sync-command-adapters.py --apply. -->\n"


def seed(root: Path) -> None:
    canonical_dir = root / ".omp" / "commands"
    canonical_dir.mkdir(parents=True)
    (canonical_dir / "harness.md").write_text(CANONICAL_HARNESS, encoding="utf-8")
    (canonical_dir / "harness-ship.md").write_text(CANONICAL_SHIP, encoding="utf-8")
    adapter_dir = root / ".claude" / "commands"
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "harness.md").write_text(banner("harness.md") + CANONICAL_HARNESS, encoding="utf-8")
    (adapter_dir / "harness-ship.md").write_text(banner("harness-ship.md") + CANONICAL_SHIP, encoding="utf-8")


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
        seed(root)

        clean = run(root, "--check")
        check("well-formed tree passes --check", clean.returncode == 0, clean.stderr)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)
        adapter = root / ".claude" / "commands" / "harness-ship.md"
        adapter.write_text(banner("harness-ship.md") + CANONICAL_SHIP + "drift\n", encoding="utf-8")

        result = run(root, "--check")
        check("edited adapter body fails --check", result.returncode != 0)
        check("edited-body failure names the file", "harness-ship.md" in result.stderr)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)
        adapter = root / ".claude" / "commands" / "harness.md"
        adapter.write_text(CANONICAL_HARNESS, encoding="utf-8")

        result = run(root, "--check")
        check("missing banner line fails --check", result.returncode != 0)
        check("missing-banner failure names the file", "harness.md" in result.stderr)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)
        orphan = root / ".claude" / "commands" / "harness-orphan.md"
        orphan.write_text("# orphan door\n\nNo canonical counterpart.\n", encoding="utf-8")

        result = run(root, "--check")
        check("orphan Claude-only door fails --check", result.returncode != 0)
        check("orphan failure names the file", "harness-orphan.md" in result.stderr)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)
        (root / ".claude" / "commands" / "harness-ship.md").unlink()

        missing = run(root, "--check")
        check("missing adapter fails --check", missing.returncode != 0)

        applied = run(root, "--apply")
        check("apply exits 0", applied.returncode == 0, applied.stderr)
        adapter = root / ".claude" / "commands" / "harness-ship.md"
        check("apply creates the missing adapter", adapter.is_file())
        check(
            "created adapter matches banner + canonical bytes",
            adapter.read_text(encoding="utf-8") == banner("harness-ship.md") + CANONICAL_SHIP,
        )

        followup = run(root, "--check")
        check("check now passes after apply", followup.returncode == 0, followup.stderr)

    print(f"\n{12 - failures}/12 cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
