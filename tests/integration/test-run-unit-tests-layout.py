#!/usr/bin/env python3
from integration_support import ROOT  # noqa: F401  (first: puts tests/ and bin/ on sys.path)

import contextlib
import shutil
import sys

from check_support import Checks
from git_support import MAINTENANCE_OFF, checked_git, commit_all, commit_files, init_repo
from runner_tree_support import run_runner as run, sentinel_tree as tree

C = Checks()
check = C.check


@contextlib.contextmanager
def fixture(git=False):
    """A sentinel tree, committed to a fresh main-branch repo when `git`, removed on exit."""
    r = tree()
    try:
        if git:
            # MAINTENANCE_OFF: background maintenance can race the rmtree of a short-lived .git.
            init_repo(r, "main", config=MAINTENANCE_OFF, git=checked_git)
            commit_all(r, "fixture", git=checked_git)
        yield r
    finally:
        shutil.rmtree(r)


def both_ran(p):
    return p.returncode == 0 and "PASS test-unit.py" in p.stdout and "PASS test-integration.py" in p.stdout


def misconfigured(p):
    return [line for line in p.stderr.splitlines() if line.startswith("MISCONFIGURED:")]


def patched_violations(r, body):
    """Replace suite_layout.violations in r's copy with one whose body is `body`; run --check-layout."""
    sl = r/".claude/skills/harness/bin/suite_layout.py"
    sl.write_text(sl.read_text() + f"\n\ndef violations(root):\n    {body}\n")
    return run(r, "--check-layout")


with fixture() as r:
    p=run(r,"--check-layout"); check("clean layout", p.returncode == 0 and "PASS" not in p.stdout, p.stderr)
    for kind in ("unit","integration"):
        p=run(r,"--kind",kind); check(f"runs {kind}", p.returncode == 0 and f"PASS test-{kind}.py" in p.stdout, p.stdout+p.stderr)
    p=run(r,"--bogus"); check("bogus refused", p.returncode == 2 and "--check-layout" in p.stderr, p.stderr)
    p=run(r,"--kind","nonsense"); check("unknown kind refused", p.returncode == 2, p.stderr)

for label, mutate, needle in [
 ("empty unit", lambda r:(r/"tests/unit/test-unit.py").unlink(), "tests/unit"),
 ("empty integration", lambda r:(r/"tests/integration/test-integration.py").unlink(), "tests/integration"),
 ("duplicate", lambda r:(r/"tests/integration/test-unit.py").write_text("pass\n"), "test-unit.py"),
 ("planted", lambda r:(r/".claude/skills/harness/bin/test-planted.py").write_text("pass\n"), "test-planted.py")]:
    with fixture() as r:
        mutate(r); p=run(r,"--check-layout"); check(label, p.returncode == 2 and needle in p.stderr, p.stderr)

# Repository-wide clause: the runner must present the refusal before any test
# sentinel runs. Cases below drive run-unit-tests.py through a real Git checkout
# so tracked_paths()'s self-ownership condition (suite_layout.py tracked at its
# real relative path) is satisfied.

# Case 1: clean git tree costs nothing — both sentinels run.
with fixture(git=True) as r:
    p = run(r, "--kind", "all")
    check("git clean tree runs both sentinels", both_ran(p), p.stdout + p.stderr)

# Case 2: one tracked rogue file is refused, and refused BEFORE any sentinel runs.
with fixture(git=True) as r:
    commit_files(r, {".harness/tools/test_rogue.py": "pass\n"}, "rogue", git=checked_git)
    p = run(r, "--kind", "all")
    check("git tracked rogue refused before sentinels",
          p.returncode == 2
          and any(".harness/tools/test_rogue.py" in line for line in misconfigured(p))
          and "PASS test-" not in p.stdout,
          p.stdout + p.stderr)

# Case 3: three tracked rogues in different directories are all reported, in
# sorted path order.
with fixture(git=True) as r:
    rogue_paths = [".harness/a/test_one.py", ".harness/b/test_two.py", ".harness/c/test_three.py"]
    commit_files(r, {rel: "pass\n" for rel in rogue_paths}, "rogues", git=checked_git)
    p = run(r, "--kind", "all")
    lines = misconfigured(p)
    ordered = [rel for line in lines for rel in rogue_paths if rel in line]
    check("git three tracked rogues reported in sorted path order",
          p.returncode == 2 and all(any(rel in line for line in lines) for rel in rogue_paths)
          and ordered == sorted(rogue_paths),
          p.stderr)

# Case 4: .git is an empty directory (no repository behind it); the runner fails closed too.
with fixture() as r:
    (r/".git").mkdir()
    p = run(r, "--kind", "all")
    check("git enumeration failure refused before sentinels",
          p.returncode == 2 and "cannot enumerate tracked files under" in p.stderr and "PASS test-" not in p.stdout,
          p.stdout + p.stderr)

# Case 5: untracked control — the same rogue shape, never added, is invisible.
with fixture(git=True) as r:
    (r/".harness/tools").mkdir(parents=True, exist_ok=True)
    (r/".harness/tools/test_rogue.py").write_text("pass\n")
    p = run(r, "--kind", "all")
    check("git untracked rogue is not reported and both sentinels run", both_ran(p), p.stdout + p.stderr)

# FEAT-64 (SC-03): _layout_output renders the documented layout-shape/rendering failures as a
# traceback string and the runner exits 2 on them; an unrelated RuntimeError inside
# suite_layout.violations propagates out of the runner as itself.
with fixture() as r:
    p = patched_violations(r, "raise RuntimeError('unrelated defect')")
    check("FEAT-64: an unrelated RuntimeError in suite_layout.violations escapes the runner as "
          "itself, not as 'MISCONFIGURED: layout check crashed'",
          p.returncode != 0 and "RuntimeError: unrelated defect" in p.stderr
          and "layout check crashed" not in p.stderr,
          f"rc={p.returncode} stdout={p.stdout!r} stderr={p.stderr[-300:]!r}")
with fixture() as r:
    p = patched_violations(r, "raise ValueError('a documented layout-data shape failure')")
    check("FEAT-64: a documented layout data-shape failure keeps the 'layout check crashed' rendering at exit 2",
          p.returncode == 2 and "MISCONFIGURED: layout check crashed" in p.stderr
          and "ValueError: a documented layout-data shape failure" in p.stderr,
          f"rc={p.returncode} stderr={p.stderr[-300:]!r}")

sys.exit(C.report())
