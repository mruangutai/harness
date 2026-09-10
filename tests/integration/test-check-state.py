#!/usr/bin/env python3
"""FEAT-104: check-state sweep for closed version-2 run steps."""
import os
import subprocess
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS, "..", ".."))
sys.path.insert(0, TESTS)

from check_state_support import SCRIPT, _root_env


def _run_state(content):
    with tempfile.TemporaryDirectory() as tmp:
        feature = os.path.join(
            tmp, ".harness", "harness", "features", "FEAT-STEP")
        run_dir = os.path.join(feature, "runs", "r1")
        os.makedirs(run_dir, exist_ok=True)
        with open(os.path.join(tmp, ".harness", "team-config.yaml"), "w") as handle:
            handle.write("agents: {}\n")
        with open(os.path.join(run_dir, "state.yaml"), "w") as handle:
            handle.write(content)
        result = subprocess.run(
            [SCRIPT], cwd=tmp, capture_output=True, text=True, env=_root_env(tmp))
        return result.returncode, result.stdout + result.stderr


def run_t07_cases():
    cases = []
    v1_code, v1 = _run_state("""schema_version: 1
run_id: r1
steps:
  - id: old-step
    status: complete
    rogue_step_key: historical
""")
    cases.append(("version 1 produces no undeclared step key report",
                  "undeclared step key" not in v1, v1_code, v1))

    v2_code, v2 = _run_state("""schema_version: 2
run_id: r1
steps:
  - id: strict-step
    status: complete
    rogue_step_key: denied
""")
    strict_lines = [line for line in v2.splitlines()
                    if "undeclared step key" in line]
    cases.append(("version 2 reports one undeclared step key with run, step and key",
                  len(strict_lines) == 1 and all(token in strict_lines[0]
                      for token in ("r1", "strict-step", "rogue_step_key")),
                  v2_code, v2))

    valid_code, valid = _run_state("""schema_version: 2
run_id: r1
steps:
  - id: valid-step
    status: complete
    evidence:
      test_exit: 0
      paths: [a, b]
""")
    cases.append(("version 2 declared keys plus evidence produce no report",
                  "undeclared step key" not in valid, valid_code, valid))

    failures = 0
    for name, passed, code, output in cases:
        if passed:
            print("ok   ", name)
        else:
            failures += 1
            print("FAIL ", name)
            print(f"      exit {code}: {output[:500]}")
    print(f"\n{len(cases) - failures}/{len(cases)} T-07 undeclared step key cases passed.")
    print("ALL PASSED" if not failures else f"{failures} FAILING")
    return failures


if __name__ == "__main__":
    raise SystemExit(1 if run_t07_cases() else 0)
