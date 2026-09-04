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
failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition:
        failures.append(name)


def registration_problems(config):
    problems = []
    kinds = config.get("test_kinds", {}) if isinstance(config, dict) else {}
    entry = kinds.get("handoff_comprehension") if isinstance(kinds, dict) else None
    if not isinstance(entry, dict):
        return [f"{PROBE}: handoff_comprehension registration is missing"]
    expected = {
        "status": "locally_run",
        "detect": PROBE,
        "cmd": PROBE,
        "exclude": ".claude/worktrees/**",
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            problems.append(f"{PROBE}: handoff_comprehension.{key} must equal {value!r}")
    if "handoff_comprehension" in json.dumps(config.get("test_matrix", {}), sort_keys=True):
        problems.append(f"{PROBE}: handoff_comprehension must not appear in test_matrix")
    if not (ROOT / PROBE).is_file():
        problems.append(f"{PROBE}: registered path does not exist")
    return problems


def tree():
    root = Path(tempfile.mkdtemp())
    (root / ".harness").mkdir()
    (root / ".harness/team-config.yaml").write_text("teams: []\n")
    bin_dir = root / ".claude/skills/harness/bin"
    bin_dir.mkdir(parents=True)
    for name in ("run-unit-tests.sh", "harness_boundary.py", "suite_layout.py", "run_pool.py"):
        shutil.copy2(ROOT / ".claude/skills/harness/bin" / name, bin_dir / name)
    for kind in ("unit", "integration"):
        directory = root / "tests" / kind
        directory.mkdir(parents=True)
        (directory / f"test-{kind}.py").write_text(f'print("PASS test-{kind}.py")\n')
    manual = root / PROBE
    manual.parent.mkdir(parents=True)
    manual.write_text('#!/usr/bin/env python3\nprint("HANDOFF-PROBE-MUST-NOT-RUN")\nraise SystemExit(1)\n')
    manual.chmod(0o755)
    return root


def run(root, *args):
    env = dict(os.environ, HARNESS_PROJECT_DIR=str(root))
    return subprocess.run(
        [str(root / ".claude/skills/harness/bin/run-unit-tests.sh"), *args],
        cwd=root, env=env, text=True, capture_output=True, timeout=60)


config = json.loads((ROOT / ".harness/harness.json").read_text())
problems = registration_problems(config)
check(f"registered real probe {PROBE}", problems == [], repr(problems))

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
    check("--kind all excludes comprehension probe",
          all_run.returncode == 0
          and "PASS test-unit.py" in all_run.stdout
          and "PASS test-integration.py" in all_run.stdout
          and "HANDOFF-PROBE-MUST-NOT-RUN" not in all_run.stdout + all_run.stderr,
          all_run.stdout + all_run.stderr)
    layout = run(fixture, "--check-layout")
    check("manual comprehension probe is layout-valid", layout.returncode == 0,
          layout.stdout + layout.stderr)
finally:
    shutil.rmtree(fixture)

raise SystemExit(1 if failures else 0)
