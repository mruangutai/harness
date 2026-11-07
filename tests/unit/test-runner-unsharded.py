#!/usr/bin/env python3
"""FEAT-2081 SC-07/SC-08: unsharded run-unit-tests.py keeps discovery, attribution, failures.

Runs the real runner in a private copied tree (no git, no weight document needed) so a
runner mutation that drops a discovered file, destroys attributed output blocks, or masks a
child failure is caught for --kind unit, --kind integration, and the no-argument form.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BIN = ".claude/skills/harness/bin"
BIN_FILES = ("run-unit-tests.py", "harness_boundary.py", "run_identity.py",
             "artifact_accessors.py", "suite_layout.py", "run_pool.py")
FILES = {"unit": ("test-ua.py", "test-ub.py", "test-uc.py"),
         "integration": ("test-ia.py", "test-ib.py", "test-ic.py")}
failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition:
        failures.append(name)


def tree(failing=None):
    root = Path(tempfile.mkdtemp())
    (root / ".harness").mkdir()
    (root / ".harness/team-config.yaml").write_text("teams: []\n")
    (root / BIN).mkdir(parents=True)
    for name in BIN_FILES:
        shutil.copy2(ROOT / BIN / name, root / BIN / name)
    for kind, names in FILES.items():
        (root / "tests" / kind).mkdir(parents=True)
        for name in names:
            code = "raise SystemExit(4)" if name == failing else "pass"
            (root / "tests" / kind / name).write_text(f'print("TOKEN-{name}")\n{code}\n')
    return root


def run(root, *args):
    env = dict(os.environ, HARNESS_PROJECT_DIR=str(root))
    return subprocess.run([str(root / BIN / "run-unit-tests.py"), *args], cwd=root, env=env,
                          text=True, capture_output=True, timeout=60)


def attributed(stdout, name):
    """The child's output sits inside its own header ... PASS/FAIL block."""
    pattern = (rf"^----- {re.escape(name)} \(exit -?\d+, [\d.]+s\) -----\n"
               rf"TOKEN-{re.escape(name)}\n(PASS|FAIL) {re.escape(name)}$")
    return re.search(pattern, stdout, re.MULTILINE) is not None


def case_discovery(args, names):
    root = tree()
    try:
        proc = run(root, *args)
        check(f"{args or 'no-arg'}: exit 0 and every discovered file attributed",
              proc.returncode == 0 and all(attributed(proc.stdout, n) for n in names),
              proc.stdout + proc.stderr)
        check(f"{args or 'no-arg'}: pool reports exactly the discovered count",
              f", {len(names)} files," in proc.stdout, proc.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_failure(args, failing):
    root = tree(failing=failing)
    try:
        proc = run(root, *args)
        check(f"{args or 'no-arg'}: child failure propagates as exit 1",
              proc.returncode == 1 and f"FAIL {failing}" in proc.stdout
              and "(exit 4," in proc.stdout, proc.stdout + proc.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    case_discovery(["--kind", "unit"], FILES["unit"])
    case_discovery(["--kind", "integration"], FILES["integration"])
    case_discovery([], FILES["unit"] + FILES["integration"])
    case_failure(["--kind", "unit"], "test-ub.py")
    case_failure(["--kind", "integration"], "test-ic.py")
    case_failure([], "test-ia.py")
    print(f"\n{len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
