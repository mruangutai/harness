"""runner_tree_support.py — a private copy of the test runner, for files that drive
run-unit-tests.py against a fixture tree instead of this checkout.

    from integration_support import ROOT                 # first: puts tests/ and bin/ on sys.path
    from runner_tree_support import RUNNER_BIN_FILES, run_runner, runner_tree, sentinel_tree

RUNNER_BIN_FILES
    The bin modules run-unit-tests.py needs to start: itself, harness_boundary, run_identity,
    artifact_accessors, suite_layout, run_pool.
runner_tree() -> pathlib.Path
    A fresh tempfile.mkdtemp() root holding exactly: the .harness/team-config.yaml marker
    (`teams: []`), RUNNER_BIN_FILES copied (shutil.copy2) into .claude/skills/harness/bin, empty
    tests/unit/ and tests/integration/ directories, and this checkout's
    tests/integration/integration-durations.json (the runner's sharding input, FEAT-2081). No
    test file and no git repository. A caller that writes its own durations document overwrites
    that copy; one that lays out its own test files writes into the existing directories
    (mkdir(exist_ok=True)), never recreates them.
sentinel_tree() -> pathlib.Path
    runner_tree() plus one sentinel per kind, tests/unit/test-unit.py and
    tests/integration/test-integration.py, each printing `PASS test-<kind>.py`.
run_runner(root, *args) -> CompletedProcess (text)
    root's copied run-unit-tests.py with args, cwd=root, HARNESS_PROJECT_DIR=root over
    os.environ, output captured, timeout=60. The exit code is not checked.

The caller owns the tree's lifetime: `shutil.rmtree(root)` in a finally. Anything particular to
one file (live probes that must not run, weights, a git commit through git_support) stays in it.
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from integration_support import ROOT

RUNNER_BIN_FILES = ("run-unit-tests.py", "harness_boundary.py", "run_identity.py",
                    "artifact_accessors.py", "suite_layout.py", "run_pool.py")
_BIN = ".claude/skills/harness/bin"
_DURATIONS = "tests/integration/integration-durations.json"


def runner_tree():
    root = Path(tempfile.mkdtemp())
    (root / ".harness").mkdir()
    (root / ".harness/team-config.yaml").write_text("teams: []\n")
    (root / _BIN).mkdir(parents=True)
    for name in RUNNER_BIN_FILES:
        shutil.copy2(ROOT / _BIN / name, root / _BIN / name)
    for kind in ("unit", "integration"):
        (root / "tests" / kind).mkdir(parents=True)
    shutil.copy2(ROOT / _DURATIONS, root / _DURATIONS)
    return root


def sentinel_tree():
    root = runner_tree()
    for kind in ("unit", "integration"):
        (root / "tests" / kind / f"test-{kind}.py").write_text(f'print("PASS test-{kind}.py")\n')
    return root


def run_runner(root, *args):
    env = dict(os.environ, HARNESS_PROJECT_DIR=str(root))
    return subprocess.run([str(root / _BIN / "run-unit-tests.py"), *args], cwd=root, env=env,
                          text=True, capture_output=True, timeout=60)
