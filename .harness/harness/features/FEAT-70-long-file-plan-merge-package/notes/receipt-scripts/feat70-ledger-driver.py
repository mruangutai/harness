"""FEAT-70 SC-02 behavioural ledger driver. Usage:
    python3 feat70-ledger-driver.py <checkout-root> <ledger.jsonl> <case-results.json>

Runs the checkout's OWN tests/integration/test-plan-merge.py case by case, in CASES order, with
PLAN_MERGE_BIN pointed at a recording shim that stands in for the checkout's plan-merge.py. Every
CLI subprocess the cases fork is executed by the shim IN-PROCESS over the checkout's real entry
(monolith or entry+package) and appended to the ledger: case identity, per-case ordinal, argv, cwd,
exit status, stdout, stderr, the `--file` plan's bytes before and after, and sha1s of each. The
suite's own PASS/FAIL results per case are written to <case-results.json> for the exclusion rule
(source-text reads of the CLI and private in-process imports see the shim, not the tool).

Three things are made deterministic ON BOTH SIDES BY THE SAME DRIVER so that the only byte differing
between two executions is the checkout root: fixture directories (tempfile.mkdtemp is replaced by a
counter under one fixed root, cleared first); the wall clock inside the tool (the shim binds every
`datetime` name in the tool's own modules to a class whose now() is fixed); and the lock race in
case_concurrency_real (consecutive subprocess.Popen calls are serialised — the second writer starts
after the first exits — so the trial records the tool's union, not which process the scheduler let
win; the plain suite run, the separate receipt, still races for real). None touches the tool's
bytes or its behaviour; all three are named in the receipt."""
import importlib.util, json, os, shutil, sys, tempfile

root, ledger, results_path = (os.path.abspath(a) for a in sys.argv[1:4])
BIN = os.path.join(root, ".claude", "skills", "harness", "bin")
REAL = os.path.join(BIN, "plan-merge.py")
FIXTURES = "/tmp/feat70-fixtures"          # identical path on both sides, cleared per execution
CASE_FILE = ledger + ".case"
shutil.rmtree(FIXTURES, ignore_errors=True)
os.makedirs(FIXTURES)
for p in (ledger, CASE_FILE, results_path):
    if os.path.exists(p):
        os.remove(p)

# --- the shim: a directory holding plan-merge.py (the shim) and plan_merge -> the real package ---
shim_dir = "/tmp/feat70-shim"                        # one path on both sides: its frame appears in tracebacks
shutil.rmtree(shim_dir, ignore_errors=True)
os.makedirs(shim_dir)
pkg = os.path.join(BIN, "plan_merge")
if os.path.isdir(pkg):
    os.symlink(pkg, os.path.join(shim_dir, "plan_merge"))
SHIM = os.path.join(shim_dir, "plan-merge.py")
open(SHIM, "w").write(f'''#!/usr/bin/env python3
"""FEAT-70 recording shim (generated). Stands in for plan-merge.py under PLAN_MERGE_BIN."""
import datetime as _dt, hashlib, importlib.util, io, json, os, sys
REAL = {REAL!r}; BIN = {BIN!r}; LEDGER = {ledger!r}; CASE_FILE = {CASE_FILE!r}

def _load_real():
    if BIN not in sys.path:
        sys.path.insert(0, BIN)
    spec = importlib.util.spec_from_file_location("feat70_real_entry", REAL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

if __name__ != "__main__":
    # Imported as a module (the baseline suite's _load_pm): expose the real tool's names.
    globals().update(vars(_load_real()))
else:
    class _Frozen(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 1, 1, 0, 0, 0, tzinfo=tz)
    argv = sys.argv[1:]
    plan = os.path.abspath(argv[argv.index("--file") + 1]) if "--file" in argv else None
    def _bytes(p):
        try:
            return open(p, "rb").read().decode("utf-8", "surrogateescape")
        except (OSError, TypeError):
            return None
    before = _bytes(plan)
    class _Tee(io.TextIOBase):
        def __init__(self, real):
            self.real, self.buf = real, []
        def write(self, s):
            self.buf.append(s); return self.real.write(s)
        def flush(self):
            self.real.flush()
    out, err = _Tee(sys.stdout), _Tee(sys.stderr)
    sys.stdout, sys.stderr = out, err
    code = 0
    try:
        mod = _load_real()
        for m in [mod] + list(sys.modules.values()):   # the entry itself is not in sys.modules
            f = getattr(m, "__file__", None) or ""
            if f.startswith(BIN) and getattr(m, "datetime", None) is _dt.datetime:
                m.datetime = _Frozen
        sys.argv = [REAL] + argv
        mod.main()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    except BaseException:
        import traceback; traceback.print_exc(); code = 1
    finally:
        sys.stdout, sys.stderr = out.real, err.real
    try:
        case = open(CASE_FILE).read().strip()
    except OSError:
        case = None
    o, e, after = "".join(out.buf), "".join(err.buf), _bytes(plan)
    sha = lambda s: None if s is None else hashlib.sha1(s.encode("utf-8", "surrogateescape")).hexdigest()
    with open(LEDGER, "a") as fh:
        fh.write(json.dumps({{"case": case, "argv": argv, "cwd": os.getcwd(), "exit": code,
                             "stdout": o, "stderr": e, "plan": plan, "plan_before": before, "plan_after": after,
                             "stdout_sha": sha(o), "stderr_sha": sha(e), "before_sha": sha(before), "after_sha": sha(after)}}) + "\\n")
    sys.exit(code)
''')
os.chmod(SHIM, 0o755)

# --- the suite, case by case ---
os.environ["PLAN_MERGE_BIN"] = SHIM
os.environ.pop("HARNESS_AGENT_TYPE", None)
counter = [0]
def deterministic_mkdtemp(suffix=None, prefix=None, dir=None):
    counter[0] += 1
    path = os.path.join(FIXTURES, f"{counter[0]:04d}")
    os.makedirs(path)
    return path
tempfile.mkdtemp = deterministic_mkdtemp
import subprocess
_RealPopen, _last = subprocess.Popen, [None]
class SerialPopen(_RealPopen):
    def __init__(self, *args, **kwargs):
        if _last[0] is not None:
            _last[0].wait()
        super().__init__(*args, **kwargs)
        _last[0] = self
subprocess.Popen = SerialPopen
suite_path = os.path.join(root, "tests", "integration", "test-plan-merge.py")
sys.path.insert(0, os.path.dirname(suite_path))
spec = importlib.util.spec_from_file_location("feat70_suite", suite_path)
suite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suite)
results = {"cases": [], "checks": {}}
for case in suite.CASES:
    open(CASE_FILE, "w").write(case.__name__)
    n = len(suite.RESULTS)
    error = None
    try:
        case()
    except BaseException as exc:  # a case aborting is recorded, not hidden
        error = repr(exc)
    mine = suite.RESULTS[n:]
    results["cases"].append(case.__name__)
    results["checks"][case.__name__] = {"error": error,
                                        "results": [(name, bool(ok), (detail or "")[:400]) for name, ok, detail in mine]}
    print(f"{'ok ' if error is None and all(r[1] for r in mine) else 'FAIL'} {case.__name__} ({len(mine)} checks)", flush=True)
json.dump(results, open(results_path, "w"), indent=1)
shutil.rmtree(shim_dir, ignore_errors=True)
shutil.rmtree(FIXTURES, ignore_errors=True)
