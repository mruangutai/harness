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

def git_tree():
    r = tree()
    # suite_layout.py's own DOCUMENTED_EXCEPTIONS registry (D-05) polices itself
    # against the tracked set: without this fixture file present at its exact
    # real-repo relative path, the registry would report it "no longer tracked"
    # in every git checkout fixture, independent of any rogue file under test.
    exc_dir = r/".harness/harness/features/FEAT-44-omp-context-advisory/evidence"
    exc_dir.mkdir(parents=True)
    (exc_dir/"probe-session-accessors.ts").write_text("// fixture stand-in for D-05 documented exception\n")
    subprocess.run(["git", "init", "-b", "main", "-q"], cwd=r, check=True, capture_output=True)
    git_commit(r)
    return r

def git_commit(r, message="fixture"):
    subprocess.run(["git", "add", "-A"], cwd=r, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=t",
         "commit", "-q", "-m", message],
        cwd=r, check=True, capture_output=True)

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

# Repository-wide clause: the runner must present the refusal before any test
# sentinel runs. Cases below drive run-unit-tests.sh through a real Git checkout
# so tracked_paths()'s self-ownership condition (suite_layout.py tracked at its
# real relative path) is satisfied.

# Case 1: clean git_tree() costs nothing — both sentinels run.
r = git_tree()
try:
    p = run(r, "--kind", "all")
    check("git clean tree runs both sentinels",
          p.returncode == 0 and "PASS test-unit.py" in p.stdout and "PASS test-integration.py" in p.stdout,
          p.stdout + p.stderr)
finally: shutil.rmtree(r)

# Case 2: one tracked rogue file is refused, and refused BEFORE any sentinel runs.
r = git_tree()
try:
    (r/".harness/tools").mkdir(parents=True, exist_ok=True)
    (r/".harness/tools/test_rogue.py").write_text("pass\n")
    git_commit(r, "rogue")
    p = run(r, "--kind", "all")
    misconfigured = [line for line in p.stderr.splitlines() if line.startswith("MISCONFIGURED:")]
    check("git tracked rogue refused before sentinels",
          p.returncode == 2
          and any(".harness/tools/test_rogue.py" in line for line in misconfigured)
          and "PASS test-unit.py" not in p.stdout,
          p.stdout + p.stderr)
finally: shutil.rmtree(r)

# Case 3: three tracked rogues in different directories are all reported, in
# sorted path order.
r = git_tree()
try:
    rogue_paths = [".harness/a/test_one.py", ".harness/b/test_two.py", ".harness/c/test_three.py"]
    for rel in rogue_paths:
        p_ = r/rel; p_.parent.mkdir(parents=True, exist_ok=True); p_.write_text("pass\n")
    git_commit(r, "rogues")
    p = run(r, "--kind", "all")
    misconfigured = [line for line in p.stderr.splitlines() if line.startswith("MISCONFIGURED:")]
    ordered = [rel for rel in rogue_paths for line in misconfigured if rel in line]
    check("git three tracked rogues reported in sorted path order",
          p.returncode == 2 and all(any(rel in line for line in misconfigured) for rel in rogue_paths)
          and ordered == sorted(rogue_paths),
          p.stderr)
finally: shutil.rmtree(r)

# Case 4: .git replaced by an empty directory fails closed at the runner too.
r = git_tree()
try:
    shutil.rmtree(r/".git")
    (r/".git").mkdir()
    p = run(r, "--kind", "all")
    check("git enumeration failure refused before sentinels",
          p.returncode == 2 and "cannot enumerate tracked files under" in p.stderr and "PASS test-" not in p.stdout,
          p.stdout + p.stderr)
finally: shutil.rmtree(r)

# Case 5: untracked control — the same rogue shape, never added, is invisible.
r = git_tree()
try:
    (r/".harness/tools").mkdir(parents=True, exist_ok=True)
    (r/".harness/tools/test_rogue.py").write_text("pass\n")
    p = run(r, "--kind", "all")
    check("git untracked rogue is not reported and both sentinels run",
          p.returncode == 0 and "PASS test-unit.py" in p.stdout and "PASS test-integration.py" in p.stdout,
          p.stdout + p.stderr)
finally: shutil.rmtree(r)

raise SystemExit(1 if failures else 0)
