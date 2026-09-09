#!/usr/bin/env python3
"""Keep Claude Code's command doors in sync with the canonical OMP command doors.

Commands carry no frontmatter, so an adapter is a banner line plus the canonical file's
bytes verbatim — a copy, not a transformation, mirroring sync-agent-adapters.py's
--check/--apply interface for the .omp/agents <-> .claude/agents pair.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BANNER = "<!-- Generated from .omp/commands/{name}; do not edit. Run bin/sync-command-adapters.py --apply. -->\n"


def canonical_paths(canonical_dir: Path) -> list[Path]:
    paths = {canonical_dir / "harness.md"}
    paths.update(canonical_dir.glob("harness-*.md"))
    return sorted(p for p in paths if p.is_file())


def expected_adapters(canonical_dir: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in canonical_paths(canonical_dir):
        result[path.name] = BANNER.format(name=path.name) + path.read_text(encoding="utf-8")
    return result


def sync(root: Path, check: bool) -> int:
    canonical_dir = root / ".omp" / "commands"
    adapter_dir = root / ".claude" / "commands"
    expected = expected_adapters(canonical_dir)
    actual_names = {path.name for path in adapter_dir.glob("harness*.md")} if adapter_dir.exists() else set()
    drift: list[str] = []

    for name, content in expected.items():
        target = adapter_dir / name
        if not target.is_file() or target.read_text(encoding="utf-8") != content:
            drift.append(name)
            if not check:
                adapter_dir.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
    for name in sorted(actual_names - set(expected)):
        drift.append(name)
        if not check:
            (adapter_dir / name).unlink()

    if not drift:
        return 0
    if check:
        print("Claude command adapters are stale: " + ", ".join(sorted(set(drift))), file=sys.stderr)
        return 1
    print("Updated Claude command adapters: " + ", ".join(sorted(set(drift))))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--apply", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        return sync(root, check=args.check)
    except OSError as exc:
        print(f"sync-command-adapters: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
