#!/usr/bin/env python3
"""Run the OMP extension's Bun tests from the Harness Python test registry."""

from __future__ import annotations

import subprocess
from pathlib import Path

TEST = Path(__file__).with_name("omp-hooks.test.ts")

result = subprocess.run(["bun", "test", str(TEST)], check=False)
raise SystemExit(result.returncode)
