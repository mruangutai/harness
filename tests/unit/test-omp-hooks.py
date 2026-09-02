#!/usr/bin/env python3
"""Run the OMP extension's Bun tests from the Harness Python test registry."""

from __future__ import annotations
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)

import subprocess
from pathlib import Path

TEST = Path(__file__).with_name("omp-hooks.test.ts")

result = subprocess.run(["bun", "test", str(TEST)], check=False)
raise SystemExit(result.returncode)
