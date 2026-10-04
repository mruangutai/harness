"""FEAT-70 SC-02 measurements over ONE checkout, each executed exactly once. Usage:
    python3 feat70-baseline.py <checkout-root> <plan-list-file> <out.json>
Records, with raw stdout/stderr bytes and sha1s:
  suite          the checkout's own tests/integration/test-plan-merge.py, run plainly (real concurrency)
  cases          the CASES identities of that suite (for the 107-pre-existing-case identity check)
  ledger         every CLI subprocess the cases fork, via feat70-ledger-driver.py (the recording shim)
  scratch        feat70-scratch-plans.py over the plan corpus in <plan-list-file>
  code_grade     the checkout's own grader over plan-merge.py plus every plan_merge/*.py present"""
import datetime, glob, hashlib, importlib.util, json, os, subprocess, sys

root, plan_list, out = (os.path.abspath(a) for a in sys.argv[1:4])
HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(root, ".claude", "skills", "harness", "bin")
SUITE = os.path.join(root, "tests", "integration", "test-plan-merge.py")
tag = os.path.basename(root)
res = {"root": root, "started": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")}
sha = lambda s: hashlib.sha1(s.encode("utf-8", "surrogateescape")).hexdigest()
env = dict(os.environ)
env.pop("HARNESS_AGENT_TYPE", None)
env.pop("PLAN_MERGE_BIN", None)


def record(name, argv, cwd):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, env=env, timeout=3600)
    res[name] = {"argv": argv, "cwd": cwd, "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                 "stdout_sha": sha(p.stdout), "stderr_sha": sha(p.stderr)}
    print(f"{p.returncode:3} {name} out={len(p.stdout)}B err={len(p.stderr)}B", flush=True)
    return p


record("suite", [sys.executable, SUITE], root)
res["suite"]["fail_lines"] = [l for l in res["suite"]["stdout"].splitlines() if l.startswith("FAIL")]

cases = subprocess.run([sys.executable, "-c",
                        "import importlib.util,sys,os; os.environ.pop('HARNESS_AGENT_TYPE',None); "
                        f"sys.path.insert(0,{os.path.dirname(SUITE)!r}); "
                        f"s=importlib.util.spec_from_file_location('suite',{SUITE!r}); m=importlib.util.module_from_spec(s); "
                        "s.loader.exec_module(m); print('\\n'.join(c.__name__ for c in m.CASES))"],
                       capture_output=True, text=True, env=env, check=True)
res["cases"] = cases.stdout.split()
print(f"    cases: {len(res['cases'])}")

ledger, results = f"/tmp/feat70-ledger-{tag}.jsonl", f"/tmp/feat70-ledger-{tag}-results.json"
record("ledger_driver", [sys.executable, os.path.join(HERE, "feat70-ledger-driver.py"), root, ledger, results], root)
res["ledger"] = [json.loads(l) for l in open(ledger)]
res["ledger_case_results"] = json.load(open(results))
print(f"    ledger: {len(res['ledger'])} invocation(s)")

scratch_out = f"/tmp/feat70-scratch-{tag}.json"
record("scratch_driver", [sys.executable, os.path.join(HERE, "feat70-scratch-plans.py"), root, plan_list, scratch_out], root)
res["scratch"] = json.load(open(scratch_out))
print(f"    scratch: {len(res['scratch']['records'])} command(s) over {len(res['scratch']['plans'])} plan(s)")

spec = importlib.util.spec_from_file_location("code_grade", os.path.join(BIN, "code_grade.py"))
cg = importlib.util.module_from_spec(spec); sys.modules["code_grade"] = cg; spec.loader.exec_module(cg)
files = [os.path.join(BIN, "plan-merge.py")] + sorted(glob.glob(os.path.join(BIN, "plan_merge", "*.py")))
grades = []
for f in files:
    rel = os.path.relpath(f, root)
    grades += [{"path": rel, "qualname": r.qualname, "grade": r.grade, "cyclomatic": r.cyclomatic,
                "cognitive": r.cognitive, "abc": r.abc} for r in cg.grade_source(open(f, encoding="utf-8").read(), rel)]
res["code_grade"] = {"files": [os.path.relpath(f, root) for f in files], "functions": grades}
print(f"    code_grade: {len(grades)} function(s) over {len(files)} file(s); below bar 4: "
      f"{[(g['qualname'], g['grade']) for g in grades if g['grade'] < 4]}")
res["finished"] = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
json.dump(res, open(out, "w"))
