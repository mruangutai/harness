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
# Every live probe is a locally-run, credentialled kind, never a matrix (CI) claim, and each is
# declared the same way. This table is the complete set of locally_run kinds.
LIVE_KINDS = {
    "handoff_comprehension": PROBE,
    "issue_types_live": "tests/manual/probe-issue-types.py",
    "omp_session_accessor": "tests/manual/probe-omp-session-accessor.py",
}
ISSUE_TYPES_PROBE = LIVE_KINDS["issue_types_live"]
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
    # FEAT-2081: the runner's sharding data dependency travels with the copied tree.
    durations = "tests/integration/integration-durations.json"
    shutil.copy2(ROOT / durations, root / durations)
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
locally_run = sorted(name for name, entry in config.get("test_kinds", {}).items()
                     if isinstance(entry, dict) and entry.get("status") == "locally_run")
check("the locally_run kinds are exactly the declared live probes",
      locally_run == sorted(LIVE_KINDS), repr(locally_run))
for kind, probe in sorted(LIVE_KINDS.items()):
    problems = registration_problems(config, kind)
    check(f"registered live probe {probe}", problems == [], repr(problems))

in_matrix = copy.deepcopy(config)
in_matrix.setdefault("test_matrix", {})["bugfix"] = ["issue_types_live"]
matrix_problems = registration_problems(in_matrix, "issue_types_live")
check("claiming a live probe in the automated matrix is loud",
      any("test_matrix" in problem for problem in matrix_problems), repr(matrix_problems))

missing_issue_types = copy.deepcopy(config)
del missing_issue_types["test_kinds"]["issue_types_live"]
check("dropping a second live probe kind is loud",
      any(ISSUE_TYPES_PROBE in problem for problem in
          registration_problems(missing_issue_types, "issue_types_live")))

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
    check("--kind all excludes every live probe",
          all_run.returncode == 0
          and "PASS test-unit.py" in all_run.stdout
          and "PASS test-integration.py" in all_run.stdout
          and "LIVE-PROBE-MUST-NOT-RUN" not in all_run.stdout + all_run.stderr,
          all_run.stdout + all_run.stderr)
    layout = run(fixture, "--check-layout")
    check("manual live probes are layout-valid", layout.returncode == 0,
          layout.stdout + layout.stderr)
finally:
    shutil.rmtree(fixture)

raise SystemExit(1 if failures else 0)
