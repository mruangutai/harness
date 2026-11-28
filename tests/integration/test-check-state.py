#!/usr/bin/env python3
"""FEAT-104: check-state sweep for closed version-2 run steps."""
from integration_support import TESTS  # noqa: F401  puts tests/ and bin/ on sys.path
import os
import subprocess
import sys
import tempfile

from check_state_support import SCRIPT, _root_env
from check_support import Checks
from harness_config_support import write_config

C = Checks()
check = C.check


def _run_state(content):
    """Run check-state.py on a fresh fixture holding one run whose state.yaml is `content`.
    _root_env writes the .harness/team-config.yaml marker the root override needs."""
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = os.path.join(
            tmp, ".harness", "harness", "features", "FEAT-STEP", "runs", "r1")
        os.makedirs(run_dir, exist_ok=True)
        write_config(os.path.join(tmp, ".harness", "harness.json"))
        with open(os.path.join(run_dir, "state.yaml"), "w") as handle:
            handle.write(content)
        result = subprocess.run(
            [SCRIPT], cwd=tmp, capture_output=True, text=True, env=_root_env(tmp))
        return result.returncode, result.stdout + result.stderr


def _check_case(name, passed, code, output):
    check(name, passed, f"exit {code}: {output[:500]}")


def run_t07_cases():
    v1_code, v1 = _run_state("""schema_version: 1
run_id: r1
steps:
  - id: old-step
    status: complete
    rogue_step_key: historical
""")
    _check_case("version 1 produces no undeclared step key report",
                "undeclared step key" not in v1, v1_code, v1)

    v2_code, v2 = _run_state("""schema_version: 2
run_id: r1
steps:
  - id: strict-step
    status: complete
    rogue_step_key: denied
""")
    strict_lines = [line for line in v2.splitlines()
                    if "undeclared step key" in line]
    _check_case("version 2 reports one undeclared step key with run, step and key",
                len(strict_lines) == 1 and all(token in strict_lines[0]
                    for token in ("r1", "strict-step", "rogue_step_key")),
                v2_code, v2)

    valid_code, valid = _run_state("""schema_version: 2
run_id: r1
steps:
  - id: valid-step
    status: complete
    evidence:
      test_exit: 0
      paths: [a, b]
""")
    _check_case("version 2 declared keys plus evidence produce no report",
                "undeclared step key" not in valid, valid_code, valid)


if __name__ == "__main__":
    run_t07_cases()
    sys.exit(C.report())
