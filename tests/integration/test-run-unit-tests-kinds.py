#!/usr/bin/env python3
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROBE = "tests/manual/probe-handoff-comprehension.py"
# BUG-1898 T-04: the live OMP merge gate is a locally-run, credentialled kind, never a matrix
# (CI) claim, declared the same way as the other live probes.
LIFECYCLE_PROBE = "tests/manual/probe-inflight-claim-lifecycle.py"
LIVE_KINDS = {
    "handoff_comprehension": PROBE,
    "inflight_claim_lifecycle_live": LIFECYCLE_PROBE,
}
failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition:
        failures.append(name)


def registration_problems(config, kind="handoff_comprehension"):
    probe = LIVE_KINDS[kind]
    problems = []
    kinds = config.get("test_kinds", {}) if isinstance(config, dict) else {}
    entry = kinds.get(kind) if isinstance(kinds, dict) else None
    if not isinstance(entry, dict):
        return [f"{probe}: {kind} registration is missing"]
    expected = {
        "status": "locally_run",
        "detect": probe,
        "cmd": probe,
        "exclude": ".claude/worktrees/**",
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            problems.append(f"{probe}: {kind}.{key} must equal {value!r}")
    if not str(entry.get("runner_note") or "").strip():
        problems.append(f"{probe}: {kind} must say how it is run (runner_note)")
    if kind in json.dumps(config.get("test_matrix", {}), sort_keys=True):
        problems.append(f"{probe}: {kind} must not appear in test_matrix")
    if not (ROOT / probe).is_file():
        problems.append(f"{probe}: registered path does not exist")
    return problems


def tree():
    root = Path(tempfile.mkdtemp())
    (root / ".harness").mkdir()
    (root / ".harness/team-config.yaml").write_text("teams: []\n")
    bin_dir = root / ".claude/skills/harness/bin"
    bin_dir.mkdir(parents=True)
    for name in (
            "run-unit-tests.py", "harness_boundary.py", "run_identity.py",
            "artifact_accessors.py", "suite_layout.py", "run_pool.py"):
        shutil.copy2(ROOT / ".claude/skills/harness/bin" / name, bin_dir / name)
    for kind in ("unit", "integration"):
        directory = root / "tests" / kind
        directory.mkdir(parents=True)
        (directory / f"test-{kind}.py").write_text(f'print("PASS test-{kind}.py")\n')
    for probe in LIVE_KINDS.values():
        manual = root / probe
        manual.parent.mkdir(parents=True, exist_ok=True)
        manual.write_text('#!/usr/bin/env python3\nprint("LIVE-PROBE-MUST-NOT-RUN")\n'
                          'raise SystemExit(1)\n')
        manual.chmod(0o755)
    return root


def run(root, *args):
    env = dict(os.environ, HARNESS_PROJECT_DIR=str(root))
    return subprocess.run(
        [str(root / ".claude/skills/harness/bin/run-unit-tests.py"), *args],
        cwd=root, env=env, text=True, capture_output=True, timeout=60)


config = json.loads((ROOT / ".harness/harness.json").read_text())
problems = registration_problems(config)
check(f"registered real probe {PROBE}", problems == [], repr(problems))
lifecycle_problems = registration_problems(config, "inflight_claim_lifecycle_live")
check(f"registered live merge-gate probe {LIFECYCLE_PROBE}", lifecycle_problems == [],
      repr(lifecycle_problems))

in_matrix = copy.deepcopy(config)
in_matrix.setdefault("test_matrix", {})["bugfix"] = ["inflight_claim_lifecycle_live"]
matrix_problems = registration_problems(in_matrix, "inflight_claim_lifecycle_live")
check("claiming the live merge gate in the automated matrix is loud",
      any("test_matrix" in problem for problem in matrix_problems), repr(matrix_problems))

missing_lifecycle = copy.deepcopy(config)
del missing_lifecycle["test_kinds"]["inflight_claim_lifecycle_live"]
check("dropping the live merge-gate kind is loud",
      any(LIFECYCLE_PROBE in problem for problem in
          registration_problems(missing_lifecycle, "inflight_claim_lifecycle_live")))

empty_detect = copy.deepcopy(config)
empty_detect["test_kinds"]["handoff_comprehension"]["detect"] = ""
empty_problems = registration_problems(empty_detect)
check("dropping probe detect is loud",
      bool(empty_problems) and all(PROBE in problem for problem in empty_problems),
      repr(empty_problems))

missing_kind = copy.deepcopy(config)
del missing_kind["test_kinds"]["handoff_comprehension"]
missing_problems = registration_problems(missing_kind)
check("dropping probe kind is loud",
      bool(missing_problems) and all(PROBE in problem for problem in missing_problems),
      repr(missing_problems))

fixture = tree()
try:
    all_run = run(fixture, "--kind", "all")
    check("--kind all excludes both live probes",
          all_run.returncode == 0
          and "PASS test-unit.py" in all_run.stdout
          and "PASS test-integration.py" in all_run.stdout
          and "LIVE-PROBE-MUST-NOT-RUN" not in all_run.stdout + all_run.stderr,
          all_run.stdout + all_run.stderr)
    layout = run(fixture, "--check-layout")
    check("manual comprehension probe is layout-valid", layout.returncode == 0,
          layout.stdout + layout.stderr)
finally:
    shutil.rmtree(fixture)

raise SystemExit(1 if failures else 0)
