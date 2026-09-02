#!/usr/bin/env python3
"""Filesystem invariant for Harness's directory-driven test layout."""
from pathlib import Path


def violations(root):
    root = Path(root)
    unit = root / "tests" / "unit"
    integration = root / "tests" / "integration"
    bin_dir = root / ".claude" / "skills" / "harness" / "bin"
    unit_tests = {p.name for p in unit.glob("test-*.py")}
    integration_tests = {p.name for p in integration.glob("test-*.py")}
    out = []
    if not unit_tests:
        out.append(f"{unit} contains no test-*.py")
    if not integration_tests:
        out.append(f"{integration} contains no test-*.py")
    for name in sorted(unit_tests & integration_tests):
        out.append(f"{name} appears in both {unit} and {integration}")
    test_shapes = ("test-*.py", "test_*.py", "*_test.py")
    shaped_tests = {
        path
        for pattern in test_shapes
        for path in (root / "tests").rglob(pattern)
    }
    for path in sorted(shaped_tests):
        if path.parent not in (unit, integration) or not path.match("test-*.py"):
            out.append(f"test file is not selected by the runner: {path}")
    planted = []
    for pattern in ("test-*.py", "*.test.*", "probe-*"):
        planted.extend(bin_dir.glob(pattern))
    for path in sorted(set(planted)):
        out.append(f"test-shaped file remains under bin: {path}")
    return out
