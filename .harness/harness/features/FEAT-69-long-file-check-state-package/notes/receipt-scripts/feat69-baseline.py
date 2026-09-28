"""FEAT-69 SC-02 measurements over ONE checkout, each executed exactly once.
Usage: python3 feat69-baseline.py <checkout-root> <out.json>
Records exit status and the raw stdout/stderr bytes (plus sha1) of: the full-table check-state run,
`--list`, the nine owning suites, the clean-tree feat62_findings and consolidation_findings runs; and
the code_grade record over check-state.py plus every check_state/*.py present (the SC-01 surface)."""
import subprocess, json, sys, hashlib, os, glob, importlib.util

root, out = sys.argv[1], sys.argv[2]
BIN = ".claude/skills/harness/bin"
SUITES = ["tests/integration/test-check-state.py", "tests/integration/test-check-state-entry.py",
          "tests/integration/test-check-state-plans.py", "tests/integration/test-check-state-records.py",
          "tests/integration/test-check-state-handoff.py", "tests/integration/test-check-state-worktrees.py",
          "tests/integration/test-check-state-inv26.py", "tests/integration/test-check-state-feat59.py",
          "tests/integration/test-check-state-table.py"]
FEAT62 = ("import importlib.util,sys; sys.path.insert(0, %r); "
          "s=importlib.util.spec_from_file_location('cpr', %r); m=importlib.util.module_from_spec(s); "
          "s.loader.exec_module(m); f=m.feat62_findings('.'); print('\\n'.join(f)); print(len(f), 'feat62 finding(s)')"
          % (BIN, os.path.join(BIN, "check-plan-routes.py")))
MEASUREMENTS = [("full_table", [sys.executable, os.path.join(BIN, "check-state.py")]),
                ("list", [sys.executable, os.path.join(BIN, "check-state.py"), "--list"]),
                *[(s, [sys.executable, s]) for s in SUITES],
                ("feat62_findings", [sys.executable, "-c", FEAT62]),
                ("consolidation_findings", [sys.executable, os.path.join(BIN, "check-plan-routes.py"), "--consolidation-audit"])]

# The full-table run is measured over every feature EXCEPT this feature's own record (amendment 2):
# FEAT-69's directory exists only at the pin, and the checker reporting on it (INV-32 resolved notes,
# INV-8's gitignored run dir) is the checker working, not the split. Both checkouts are copied to a
# scratch tree with that one directory removed, so both sides grade the same feature set; the
# scratch root is what the checkout-root normalisation then replaces. Every other measurement runs
# in the checkout itself.
OWN_RECORD = os.path.join(".harness", "harness", "features", "FEAT-69-long-file-check-state-package")
import shutil, tempfile
scratch = os.path.join(tempfile.mkdtemp(prefix="feat69-fulltable-"), os.path.basename(os.path.abspath(root)))
shutil.copytree(root, scratch, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__", "worktrees"))
shutil.rmtree(os.path.join(scratch, OWN_RECORD), ignore_errors=True)

res = {"full_table_scratch_root": scratch, "full_table_excludes": OWN_RECORD}
for name, argv in MEASUREMENTS:
    cwd = scratch if name == "full_table" else root
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=1800)
    res[name] = {"argv": argv, "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                 "stdout_sha": hashlib.sha1(p.stdout.encode()).hexdigest(),
                 "stderr_sha": hashlib.sha1(p.stderr.encode()).hexdigest()}
    print(f"{p.returncode:3} {name} out={len(p.stdout)}B err={len(p.stderr)}B", flush=True)

# The code_grade record over the SC-01 surface, with THIS checkout's own grader.
spec = importlib.util.spec_from_file_location("code_grade", os.path.join(root, BIN, "code_grade.py"))
cg = importlib.util.module_from_spec(spec); sys.modules["code_grade"] = cg; spec.loader.exec_module(cg)
files = [os.path.join(BIN, "check-state.py")] + sorted(glob.glob(os.path.join(root, BIN, "check_state", "*.py")))
grades = []
for f in files:
    rel = os.path.relpath(f, root) if os.path.isabs(f) else f
    text = open(os.path.join(root, rel), encoding="utf-8").read()
    grades += [{"path": rel, "qualname": r.qualname, "grade": r.grade, "cyclomatic": r.cyclomatic,
                "cognitive": r.cognitive, "abc": r.abc} for r in cg.grade_source(text, rel)]
res["code_grade"] = {"files": [os.path.relpath(f, root) if os.path.isabs(f) else f for f in files], "functions": grades}
print(f"code_grade: {len(grades)} function(s) over {len(files)} file(s); below bar 4: "
      f"{[(g['qualname'], g['grade']) for g in grades if g['grade'] < 4]}")
shutil.rmtree(os.path.dirname(scratch), ignore_errors=True)
json.dump(res, open(out, "w"))
