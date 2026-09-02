#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / ".claude/skills/harness/bin/run-unit-tests.sh"
failures = []
def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition: failures.append(name)

def tree():
    r = Path(tempfile.mkdtemp())
    (r/".harness").mkdir(); (r/".harness/team-config.yaml").write_text("teams: []\n")
    b = r/".claude/skills/harness/bin"; b.mkdir(parents=True)
    for name in ("run-unit-tests.sh", "harness_boundary.py", "suite_layout.py", "run_pool.py"):
        shutil.copy2(ROOT/".claude/skills/harness/bin"/name, b/name)
    for kind in ("unit", "integration"):
        d=r/"tests"/kind; d.mkdir(parents=True); (d/f"test-{kind}.py").write_text(f'print("PASS test-{kind}.py")\n')
    return r

def run(r, *args):
    env=dict(os.environ, HARNESS_PROJECT_DIR=str(r))
    return subprocess.run([str(r/".claude/skills/harness/bin/run-unit-tests.sh"), *args], cwd=r, env=env, text=True, capture_output=True, timeout=60)

r=tree()
try:
    p=run(r,"--check-layout"); check("clean layout", p.returncode == 0 and "PASS" not in p.stdout, p.stderr)
    for kind in ("unit","integration"):
        p=run(r,"--kind",kind); check(f"runs {kind}", p.returncode == 0 and f"PASS test-{kind}.py" in p.stdout, p.stdout+p.stderr)
    p=run(r,"--bogus"); check("bogus refused", p.returncode == 2 and "--check-layout" in p.stderr, p.stderr)
    p=run(r,"--kind","nonsense"); check("unknown kind refused", p.returncode == 2, p.stderr)
finally: shutil.rmtree(r)

for label, mutate, needle in [
 ("empty unit", lambda r:(r/"tests/unit/test-unit.py").unlink(), "tests/unit"),
 ("empty integration", lambda r:(r/"tests/integration/test-integration.py").unlink(), "tests/integration"),
 ("duplicate", lambda r:(r/"tests/integration/test-unit.py").write_text("pass\n"), "test-unit.py"),
 ("planted", lambda r:(r/".claude/skills/harness/bin/test-planted.py").write_text("pass\n"), "test-planted.py")]:
    r=tree()
    try:
        mutate(r); p=run(r,"--check-layout"); check(label, p.returncode == 2 and needle in p.stderr, p.stderr)
    finally: shutil.rmtree(r)
raise SystemExit(1 if failures else 0)
