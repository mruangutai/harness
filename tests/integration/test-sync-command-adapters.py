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
CANONICAL_PLAN = "# /harness-plan — plan a feature\n\nDoor body three.\n"
CANONICAL_GRILLING = "# /harness-grilling — grill the operator\n\nDoor body four.\n"
CANONICAL_SHIP = "# /harness-ship — ship a feature\n\nDoor body two.\n"

# seed() lays down all four of sync-command-adapters.py's REQUIRED_DOORS, plus their adapters —
# once --check enforces the full required set (F3), a fixture missing any one of them fails every
# other case for a reason unrelated to what that case actually tests.
REQUIRED_DOORS = {
    "harness.md": CANONICAL_HARNESS,
    "harness-plan.md": CANONICAL_PLAN,
    "harness-ship.md": CANONICAL_SHIP,
    "harness-grilling.md": CANONICAL_GRILLING,
}


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def banner(name: str) -> str:
    return (
        f"<!-- Generated from .omp/commands/{name}; do not edit. "
        "Run .claude/skills/harness/bin/sync-command-adapters.py --apply. -->\n"
    )


def seed(root: Path) -> None:
    canonical_dir = root / ".omp" / "commands"
    canonical_dir.mkdir(parents=True)
    adapter_dir = root / ".claude" / "commands"
    adapter_dir.mkdir(parents=True)
    for name, body in REQUIRED_DOORS.items():
        (canonical_dir / name).write_text(body, encoding="utf-8")
        (adapter_dir / name).write_text(banner(name) + body, encoding="utf-8")


def case_well_formed_tree_passes_check():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)

        clean = run(root, "--check")
        return [("well-formed tree passes --check", clean.returncode == 0, clean.stderr)]


def case_edited_adapter_body_fails():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)
        adapter = root / ".claude" / "commands" / "harness-ship.md"
        adapter.write_text(banner("harness-ship.md") + CANONICAL_SHIP + "drift\n", encoding="utf-8")

        result = run(root, "--check")
        return [
            ("edited adapter body fails --check", result.returncode != 0, result.stderr),
            ("edited-body failure names the file", "harness-ship.md" in result.stderr, result.stderr),
        ]


def case_missing_banner_fails():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)
        adapter = root / ".claude" / "commands" / "harness.md"
        adapter.write_text(CANONICAL_HARNESS, encoding="utf-8")

        result = run(root, "--check")
        return [
            ("missing banner line fails --check", result.returncode != 0, result.stderr),
            ("missing-banner failure names the file", "harness.md" in result.stderr, result.stderr),
        ]


def case_orphan_door_fails():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)
        orphan = root / ".claude" / "commands" / "harness-orphan.md"
        orphan.write_text("# orphan door\n\nNo canonical counterpart.\n", encoding="utf-8")

        result = run(root, "--check")
        return [
            ("orphan Claude-only door fails --check", result.returncode != 0, result.stderr),
            ("orphan failure names the file", "harness-orphan.md" in result.stderr, result.stderr),
        ]


def case_missing_adapter_apply_workflow():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)
        (root / ".claude" / "commands" / "harness-ship.md").unlink()

        missing = run(root, "--check")
        results = [("missing adapter fails --check", missing.returncode != 0, missing.stderr)]

        applied = run(root, "--apply")
        results.append(("apply exits 0", applied.returncode == 0, applied.stderr))
        adapter = root / ".claude" / "commands" / "harness-ship.md"
        results.append(("apply creates the missing adapter", adapter.is_file(), ""))
        results.append((
            "created adapter matches banner + canonical bytes",
            adapter.is_file() and adapter.read_text(encoding="utf-8") == banner("harness-ship.md") + CANONICAL_SHIP,
            "",
        ))

        followup = run(root, "--check")
        results.append(("check now passes after apply", followup.returncode == 0, followup.stderr))
        return results


def case_missing_required_door_fails():
    """F3: canonical_paths()/expected_adapters() only ever describe files that EXIST, so deleting
    a required door together with its adapter used to be invisible to --check. This pins the fix:
    a missing required door is a hard, named failure in both --check and --apply."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed(root)
        (root / ".omp" / "commands" / "harness-ship.md").unlink()
        (root / ".claude" / "commands" / "harness-ship.md").unlink()

        checked = run(root, "--check")
        results = [
            ("missing required door fails --check", checked.returncode != 0, checked.stderr),
            ("missing-required-door failure names the door", "harness-ship.md" in checked.stderr, checked.stderr),
        ]

        applied = run(root, "--apply")
        results.append(("missing required door also fails --apply", applied.returncode != 0, applied.stderr))
        return results


CASES = (
    case_well_formed_tree_passes_check,
    case_edited_adapter_body_fails,
    case_missing_banner_fails,
    case_orphan_door_fails,
    case_missing_adapter_apply_workflow,
    case_missing_required_door_fails,
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
