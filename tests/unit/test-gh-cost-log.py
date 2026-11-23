#!/usr/bin/env python3
"""Tests for gh_cost_log.py (FEAT-29 T-03) — in-process, no subprocess, no real gh, no writes to
the real .harness/logs (every case redirects harness_boundary.resolve_root() to a tmp root and
asserts the redirect took effect BEFORE asserting anything about file contents — a test that
skipped that check could silently pollute the real checkout's log directory instead of failing).

The recorder is OPT-IN, default OFF (approval amendment 5, 2026-08-19): every case below that
exercises recording sets HARNESS_GH_COST_LOG=1 explicitly, and cleans it up in a finally so it
never leaks between cases. The SC-05 cases near the end assert the OFF state (variable unset)
instead — those must NOT set it.

    ./test-gh-cost-log.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import io
import json
import os
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
sys.path.insert(0, HERE)

import gh_cost_log  # noqa: E402
import harness_boundary  # noqa: E402

FAILURES = []
RAN = 0


def check(name, cond, detail=""):
    global RAN
    RAN += 1
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}{(' — ' + detail) if detail else ''}")
        FAILURES.append(name)


_real_resolve_root = harness_boundary.resolve_root
# Every gh launch — the counter read through factory_gh.launch_gh included — goes through the
# one shared subprocess.run module attribute, so that is the one attribute every case patches.
_real_subprocess_run = subprocess.run


def restore():
    harness_boundary.resolve_root = _real_resolve_root
    subprocess.run = _real_subprocess_run


def redirect(tmp):
    """Point gh_cost_log's log resolution at tmp. Returns the expected log path for TODAY, and
    asserts the redirect actually took effect before the caller trusts it — the log-path trap."""
    harness_boundary.resolve_root = lambda *a, **k: tmp
    resolved = gh_cost_log._log_path()
    assert resolved.startswith(tmp + os.sep), (
        f"redirect did not take effect: resolved {resolved!r} is not under tmp root {tmp!r}"
    )
    return resolved


def read_lines(path):
    """Never raises — a mutation that drops the write on some path must redden the NAMED
    check that asserts on the returned (possibly empty) list, not crash the whole suite before
    that check is even reached (P-04: an unguarded raise here would hide every later check's
    redness behind an abort, and an abort is not evidence of anything)."""
    try:
        with open(path, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except (OSError, json.JSONDecodeError):
        return []


def counter_stub(values):
    """A fake subprocess.run standing in for the counter's own `gh api rate_limit --jq ...`
    call. `values` is an iterator of ints to return, one per call, via stdout."""
    it = iter(values)

    class R:
        def __init__(self, out):
            self.returncode = 0
            self.stdout = str(out)
            self.stderr = ""

    def fake_run(argv, **kwargs):
        return R(next(it))

    return fake_run


def raising_run(argv, **kwargs):
    # FEAT-64: an unreachable binary is an OSError — the class the boundary really raises.
    # (Was RuntimeError, which pinned the over-broad catch rather than the contract.)
    raise OSError("boom — the counter binary is unreachable")


# ---------------- record(): keys, cost, and the fresh-file coverage line ----------------
# HARNESS_GH_COST_LOG=1 set explicitly — the recorder is opt-in, default OFF (amendment 5).

with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    check("redirect took effect before any assertion about content",
          path.startswith(tmp + os.sep), path)

    os.environ["HARNESS_GH_COST_LOG"] = "1"
    try:
        gh_cost_log.record(["issue", "view", "1"], 100, 105, 0)
        lines = read_lines(path)
        first = lines[0] if lines else {}
        check("fresh log file's FIRST line is JSON carrying a coverage key",
              len(lines) == 2 and "coverage" in first, f"lines={lines}")
        check("coverage value mentions run_gh",
              "run_gh" in first.get("coverage", ""), first)
        check("coverage value mentions gh typed directly into Bash",
              "Bash" in first.get("coverage", ""), first)
        check("a successful invocation writes exactly one invocation line",
              len(lines) == 2, f"lines={lines}")
        rec = lines[1] if len(lines) > 1 else {}
        check("recorded line has all six required keys",
              set(rec.keys()) == {"ts", "argv", "before", "after", "cost", "rc"}, rec)
        check("cost equals after minus before",
              rec.get("cost") == 5, rec)
        check("before/after/rc are recorded verbatim",
              rec.get("before") == 100 and rec.get("after") == 105 and rec.get("rc") == 0, rec)

        # appending a second invocation must NOT repeat the coverage line
        gh_cost_log.record(["issue", "view", "2"], 105, 106, 0)
        lines2 = read_lines(path)
        check("appending a second invocation does not rewrite the coverage line",
              sum(1 for l in lines2 if "coverage" in l) == 1, f"lines={lines2}")
        check("appending a second invocation adds exactly one more line",
              len(lines2) == 3, f"lines={lines2}")
    finally:
        del os.environ["HARNESS_GH_COST_LOG"]
restore()


# ---------------- a failing invocation is STILL recorded ----------------
# HARNESS_GH_COST_LOG=1 set explicitly — the recorder is opt-in, default OFF (amendment 5).

with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    os.environ["HARNESS_GH_COST_LOG"] = "1"
    try:
        gh_cost_log.record(["issue", "create"], 200, 210, 1)
        lines = read_lines(path)
        non_cov = [l for l in lines if "coverage" not in l]
        rec = non_cov[0] if non_cov else {}
        check("a failing invocation (rc=1) is still recorded",
              len(non_cov) == 1, f"lines={lines}")
        check("the failing invocation's line carries rc 1",
              rec.get("rc") == 1, rec)
        check("the failing invocation's line carries its real cost",
              rec.get("cost") == 10, rec)
    finally:
        del os.environ["HARNESS_GH_COST_LOG"]
restore()


# ---------------- -f/-F value truncation ----------------
# HARNESS_GH_COST_LOG=1 set explicitly — the recorder is opt-in, default OFF (amendment 5).

with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    os.environ["HARNESS_GH_COST_LOG"] = "1"
    try:
        long_query = "query=" + ("x" * 200)
        gh_cost_log.record(["api", "graphql", "-f", long_query, "-F", "owner=short"], 1, 1, 0)
        lines = read_lines(path)
        non_cov = [l for l in lines if "coverage" not in l]
        rec = non_cov[0] if non_cov else {}
        argv = rec.get("argv") or []
        check("a -f value longer than 80 chars is truncated with an ellipsis",
              len(argv) > 3 and len(argv[3]) < len(long_query) and argv[3].endswith("..."), argv)
        check("a short -F value is left untouched",
              len(argv) > 5 and argv[5] == "owner=short", argv)
    finally:
        del os.environ["HARNESS_GH_COST_LOG"]
restore()


# ---------------- HARNESS_GH_COST_LOG=0 disables recording entirely ----------------

with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    os.environ["HARNESS_GH_COST_LOG"] = "0"
    try:
        gh_cost_log.record(["issue", "view", "1"], 1, 1, 0)
    finally:
        del os.environ["HARNESS_GH_COST_LOG"]
    check("HARNESS_GH_COST_LOG=0 writes no line at all",
          not os.path.exists(path), f"exists={os.path.exists(path)}")
restore()


# ---------------- measured(): a counter read that raises never propagates ----------------
# HARNESS_GH_COST_LOG=1 set explicitly — the recorder is opt-in, default OFF (amendment 5).

with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    subprocess.run = raising_run
    os.environ["HARNESS_GH_COST_LOG"] = "1"
    try:
        raised = False
        try:
            with gh_cost_log.measured(["issue", "view", "1"]) as m:
                m.returncode = 0
        except Exception:
            raised = True
        check("a counter read that raises does not propagate out of measured()",
              not raised)
        lines = read_lines(path)
        non_cov = [l for l in lines if "coverage" not in l]
        rec = non_cov[0] if non_cov else {}
        check("a counter-read failure records null before/after/cost",
              rec.get("before") is None and rec.get("after") is None and rec.get("cost") is None,
              rec)
        check("a counter-read failure still records the real returncode",
              rec.get("rc") == 0, rec)
    finally:
        del os.environ["HARNESS_GH_COST_LOG"]
restore()


# ---------------- measured(): the counter's own call is never wrapped (recursion guard) ----
# HARNESS_GH_COST_LOG=1 set explicitly — proves the recursion guard itself excludes the
# counter's own argv, not just that recording happens to be off (amendment 5).

with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    subprocess.run = counter_stub([999])
    os.environ["HARNESS_GH_COST_LOG"] = "1"
    try:
        with gh_cost_log.measured(gh_cost_log._COUNTER_ARGV) as m:
            m.returncode = 0
        check("measured() never records a line for the counter's own argv",
              not os.path.exists(path) or read_lines(path) == [], f"exists={os.path.exists(path)}")
    finally:
        del os.environ["HARNESS_GH_COST_LOG"]
restore()


# ---------------- SC-05: opt-in default is OFF — variable UNSET writes nothing, both halves --

with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    os.environ.pop("HARNESS_GH_COST_LOG", None)  # ensure genuinely unset, not merely "0"
    gh_cost_log.record(["issue", "view", "1"], 100, 105, 0)
    check("with HARNESS_GH_COST_LOG unset, a successful invocation creates no log file",
          not os.path.exists(path), f"exists={os.path.exists(path)}")
    check("with HARNESS_GH_COST_LOG unset, a successful invocation writes no line",
          read_lines(path) == [], f"lines={read_lines(path)}")
restore()

with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    os.environ.pop("HARNESS_GH_COST_LOG", None)  # ensure genuinely unset
    gh_cost_log.record(["issue", "create"], 200, 210, 1)  # a FAILING invocation, rc != 0
    check("with HARNESS_GH_COST_LOG unset, a FAILING invocation creates no log file",
          not os.path.exists(path), f"exists={os.path.exists(path)}")
    check("with HARNESS_GH_COST_LOG unset, a FAILING invocation writes no line",
          read_lines(path) == [], f"lines={read_lines(path)}")
restore()


# ---------------- WRAP SITES: factory_gh.run_gh and gh-sync.py's gh() -------------------
# QA fix cycle 3 (T-03): `with gh_cost_log.measured(args)` at each wrap site was asserted by
# NOTHING via the real wrapper — every case above calls record()/measured() directly, which
# bypasses the interface. These four cases drive the REAL wrappers (factory_gh.run_gh and
# gh-sync.py's gh()) through a fake gh — a counting subprocess.run double standing in for the
# gh binary — parameterised on recorder state (ON/OFF), and assert BOTH the write AND the
# subprocess call count. The call count is what proves the guard at gh_cost_log.py:157
# (`if not _enabled() or is_counter_call(argv)`) actually short-circuits OFF to one call; every
# existing OFF case above calls record() directly and only exercises record()'s OWN, separate
# guard at :112.

import contextlib  # noqa: E402
import importlib  # noqa: E402
import importlib.util as _ilu  # noqa: E402

import factory_gh as _fgh  # noqa: E402


def _load_gh_sync():
    """gh-sync.py's hyphen blocks a plain import; loaded the same way test-gh-sync.py:890-891
    already does for load_recorded. A fresh module each call, but `subprocess`, `gh_cost_log`
    and `harness_boundary` are all resolved through sys.modules's cache, so patches on those
    module objects apply here too without re-patching per module instance."""
    spec = _ilu.spec_from_file_location("_ghs_t03_wrap_site", os.path.join(HERE, "gh-sync.py"))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _counting_fake(rc=0, stdout="ok"):
    """Stands in for the gh binary itself. Every subprocess.run call this drives — the
    counter's own rate_limit read AND the 'real' invocation — lands here, because
    factory_gh and the freshly-loaded gh-sync module launch through the SAME imported
    `subprocess` module object (Python caches modules by name), so patching its `.run` patches
    every launch."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))

        class R:
            pass

        r = R()
        if len(argv) >= 1 and list(argv[1:]) == gh_cost_log._COUNTER_ARGV:
            r.returncode = 0
            r.stdout = str(1000 + len(calls))
            r.stderr = ""
        else:
            r.returncode = rc
            r.stdout = stdout
            r.stderr = "" if rc == 0 else "boom"
        return r

    return fake_run, calls


# --- factory_gh.run_gh wrap site, ON ---
with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    fake_run, calls = _counting_fake()
    subprocess.run = fake_run
    os.environ["HARNESS_GH_COST_LOG"] = "1"
    try:
        _fgh.run_gh(["issue", "view", "1"])
    finally:
        del os.environ["HARNESS_GH_COST_LOG"]
    lines = read_lines(path)
    non_cov = [l for l in lines if "coverage" not in l]
    check("factory_gh.run_gh wrap site, ON: one line written for the wrapped invocation",
          len(non_cov) == 1, f"lines={lines}")
    check("factory_gh.run_gh wrap site, ON: three subprocess calls (counter, real, counter)",
          len(calls) == 3, f"calls={calls}")
restore()

# --- factory_gh.run_gh wrap site, OFF (genuinely unset, not merely "0") ---
with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    fake_run, calls = _counting_fake()
    subprocess.run = fake_run
    os.environ.pop("HARNESS_GH_COST_LOG", None)
    _fgh.run_gh(["issue", "view", "1"])
    check("factory_gh.run_gh wrap site, OFF: no line written",
          not os.path.exists(path) or read_lines(path) == [], f"exists={os.path.exists(path)}")
    check("factory_gh.run_gh wrap site, OFF: exactly one subprocess call (the real call only)",
          len(calls) == 1, f"calls={calls}")
restore()

# --- gh-sync.py's gh() wrap site, ON ---
with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    fake_run, calls = _counting_fake()
    subprocess.run = fake_run
    os.environ["HARNESS_GH_COST_LOG"] = "1"
    try:
        _ghs = _load_gh_sync()
        _ghs.gh(["issue", "view", "1"])
    finally:
        del os.environ["HARNESS_GH_COST_LOG"]
    lines = read_lines(path)
    non_cov = [l for l in lines if "coverage" not in l]
    check("gh-sync.py gh() wrap site, ON: one line written for the wrapped invocation",
          len(non_cov) == 1, f"lines={lines}")
    check("gh-sync.py gh() wrap site, ON: three subprocess calls (counter, real, counter)",
          len(calls) == 3, f"calls={calls}")
restore()

# --- gh-sync.py's gh() wrap site, OFF (genuinely unset, not merely "0") ---
with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    fake_run, calls = _counting_fake()
    subprocess.run = fake_run
    os.environ.pop("HARNESS_GH_COST_LOG", None)
    _ghs = _load_gh_sync()
    _ghs.gh(["issue", "view", "1"])
    check("gh-sync.py gh() wrap site, OFF: no line written",
          not os.path.exists(path) or read_lines(path) == [], f"exists={os.path.exists(path)}")
    check("gh-sync.py gh() wrap site, OFF: exactly one subprocess call (the real call only)",
          len(calls) == 1, f"calls={calls}")
restore()

# --- factory_gh.run_gh wrap site, ON, FAILING invocation: the recorded rc is the real one ---
# T-03 cycle 4 (approval amendment 6): the four ON/OFF cases above all drive rc=0 via
# _counting_fake()'s default, and none inspects the recorded "rc" value — only presence/count.
# `_cost.returncode = r.returncode` at factory_gh.py:162 is asserted by NOTHING. This drives a
# FAILING call (rc=1) through the real run_gh, catches the raised GhError (run_gh always raises
# on non-zero rc — that is forced, not a design choice), and asserts the LOGGED RECORD'S rc
# equals 1 — not that a record exists, not that GhError was raised.
with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    fake_run, calls = _counting_fake(rc=1)
    subprocess.run = fake_run
    os.environ["HARNESS_GH_COST_LOG"] = "1"
    try:
        try:
            _fgh.run_gh(["issue", "view", "1"])
            raised = False
        except _fgh.GhError:
            raised = True
    finally:
        del os.environ["HARNESS_GH_COST_LOG"]
    lines = read_lines(path)
    non_cov = [l for l in lines if "coverage" not in l]
    check("factory_gh.run_gh wrap site, FAILING: GhError was raised",
          raised)
    check("factory_gh.run_gh wrap site, FAILING: one line written for the wrapped invocation",
          len(non_cov) == 1, f"lines={lines}")
    check("factory_gh.run_gh wrap site, FAILING: the recorded rc equals the real exit code (1)",
          len(non_cov) == 1 and non_cov[0].get("rc") == 1,
          f"non_cov={non_cov}")
restore()

# --- factory_gh.run_gh wrap site, OFF, FAILING invocation: the recorder stays fully out of the
# way of a non-zero-rc call too, not just the rc=0 case already covered above ---
# QA fix cycle (SC-05): every existing OFF case that drives the real wrapper (lines 335-346,
# 367-379) uses _counting_fake()'s default rc=0. record()'s own guard at gh_cost_log.py:112
# already forecloses a write for ANY rc once _enabled() is False, so this case cannot discover a
# defect record() doesn't already prevent — what it DOES pin is measured()'s guard at :157 firing
# on the non-zero-rc path specifically, closing the grading ambiguity SC-05's amended sentence
# ("including for a failing invocation") named.
with tempfile.TemporaryDirectory() as tmp:
    path = redirect(tmp)
    fake_run, calls = _counting_fake(rc=1)
    subprocess.run = fake_run
    os.environ.pop("HARNESS_GH_COST_LOG", None)  # ensure genuinely unset
    try:
        _fgh.run_gh(["issue", "view", "1"])
        raised = False
    except _fgh.GhError:
        raised = True
    check("OFF, FAILING: GhError was still raised (the wrapper does not swallow the real error)",
          raised)
    check("OFF, FAILING: no log file is created",
          not os.path.exists(path), f"exists={os.path.exists(path)}")
    check("OFF, FAILING: no line is written",
          read_lines(path) == [], f"lines={read_lines(path)}")
    check("OFF, FAILING: exactly one subprocess call (the real call only, neither counter read)",
          len(calls) == 1, f"calls={calls}")
restore()


# FEAT-64 (SC-03): the counter and the log are BEST-EFFORT at their real boundaries — a
# counter binary that is absent, fails, or prints junk is None; an unwritable log dir is a
# silent return — but an unrelated programming defect escapes rather than reading as "the
# counter could not be read".
with tempfile.TemporaryDirectory() as tmp:
    redirect(tmp)
    subprocess.run = lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("no gh"))
    check("FEAT-64: an absent counter binary reads None", gh_cost_log._read_counter() is None)
    class _R:
        returncode = 0
        stdout = "not-a-number"
    subprocess.run = lambda *a, **k: _R()
    check("FEAT-64: a counter that prints junk reads None", gh_cost_log._read_counter() is None)
    subprocess.run = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("unrelated"))
    try:
        gh_cost_log._read_counter()
        escaped = False
    except RuntimeError:
        escaped = True
    check("FEAT-64: an unrelated RuntimeError escapes _read_counter", escaped)
    restore()
    redirect(tmp)
    _real_dumps = gh_cost_log.json.dumps
    gh_cost_log.json.dumps = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("unrelated"))
    os.environ["HARNESS_GH_COST_LOG"] = "1"
    try:
        try:
            gh_cost_log.record(["gh", "api"], 1, 2, 0)
            escaped = False
        except RuntimeError:
            escaped = True
    finally:
        gh_cost_log.json.dumps = _real_dumps
        del os.environ["HARNESS_GH_COST_LOG"]
    check("FEAT-64: an unrelated RuntimeError escapes record", escaped)
restore()


# ---------------- FEAT-2452 T-01: the counter reads through factory_gh.launch_gh -------------
# The counter read shares the one launch and FACTORY_GH boundary but stays outside cost
# accounting: launch_gh is never measured, and only try_gh (which run_gh adapts) measures, once.
# Every case pins FACTORY_GH to one fake binary path and patches the shared subprocess.run, so
# no real gh can start even if a case's own patch were missed.
_T01_FAKE_GH = os.path.join(TESTS_DIR, "t01-fake-gh-never-installed")
_T01_OPERATION = ["issue", "view", "1"]
_MISSING = object()


@contextlib.contextmanager
def _patched(module, **attrs):
    saved = {name: vars(module).get(name, _MISSING) for name in attrs}
    for name, value in attrs.items():
        setattr(module, name, value)
    try:
        yield
    finally:
        for name, value in saved.items():
            if value is _MISSING:
                delattr(module, name)
            else:
                setattr(module, name, value)


def _launch_boom(*a, **k):
    raise AssertionError(f"unexpected launch: {a!r}")


def t01_case(name, fn):
    os.environ["FACTORY_GH"] = _T01_FAKE_GH
    try:
        fn()
    except Exception as exc:
        check(f"T-01 {name}: ran to its checks", False, f"{type(exc).__name__}: {exc}")
    finally:
        os.environ.pop("FACTORY_GH", None)
        os.environ.pop("HARNESS_GH_COST_LOG", None)
        restore()


def t01_counter_uses_launch_gh():
    seen = []

    def fake_launch(args, *, input=None):
        seen.append((list(args), input))
        return subprocess.CompletedProcess(args, 0, "1234\n", "")

    subprocess.run = _launch_boom
    with _patched(_fgh, launch_gh=fake_launch, run_gh=_launch_boom, try_gh=_launch_boom):
        value = gh_cost_log._read_counter()
    check("T-01 _read_counter: reads the counter through factory_gh.launch_gh only",
          value == 1234 and seen == [(gh_cost_log._COUNTER_ARGV, None)], f"value={value!r} seen={seen}")


def t01_counter_failures_read_none():
    def failed_launch(args, *, input=None):
        raise _fgh.GhError(list(args), None, "", "", "gh not found", "gh", "install gh")

    def nonzero_launch(args, *, input=None):
        return subprocess.CompletedProcess(args, 1, "", "HTTP 401")

    subprocess.run = _launch_boom
    with _patched(_fgh, launch_gh=failed_launch):
        typed = gh_cost_log._read_counter()
    with _patched(_fgh, launch_gh=nonzero_launch):
        nonzero = gh_cost_log._read_counter()
    check("T-01 _read_counter: a typed launch failure and a nonzero counter both read None",
          typed is None and nonzero is None, f"typed={typed!r} nonzero={nonzero!r}")


def _t01_measured_operation(fn, rc):
    """Drive fn over one operation with telemetry ON and the one fake binary; return the
    launches, the recorded lines and fn's result."""
    with tempfile.TemporaryDirectory() as tmp:
        path = redirect(tmp)
        fake_run, calls = _counting_fake(rc=rc)
        subprocess.run = fake_run
        os.environ["HARNESS_GH_COST_LOG"] = "1"
        result = fn(_T01_OPERATION)
        os.environ.pop("HARNESS_GH_COST_LOG", None)
        lines = [l for l in read_lines(path) if "coverage" not in l]
    return calls, lines, result


def t01_telemetry_one_fake_binary():
    counter = [_T01_FAKE_GH] + gh_cost_log._COUNTER_ARGV
    expected = [counter, [_T01_FAKE_GH] + _T01_OPERATION, counter]
    for rc in (0, 1):
        calls, lines, result = _t01_measured_operation(_fgh.try_gh, rc)
        check(f"T-01 telemetry rc={rc}: before-counter, operation, after-counter, nothing else",
              calls == expected, f"calls={calls}")
        check(f"T-01 telemetry rc={rc}: one recorded line with the real return code",
              len(lines) == 1 and lines[0].get("rc") == rc and lines[0].get("argv") == _T01_OPERATION
              and isinstance(lines[0].get("before"), int), f"lines={lines}")
        check(f"T-01 telemetry rc={rc}: the result keeps the real process status",
              result.status == rc and result.ok == (rc == 0), repr(result))


def t01_run_gh_measures_once():
    counter = [_T01_FAKE_GH] + gh_cost_log._COUNTER_ARGV
    calls, lines, _ = _t01_measured_operation(_fgh.run_gh, 0)
    check("T-01 telemetry run_gh: the adapter adds no second measurement",
          calls == [counter, [_T01_FAKE_GH] + _T01_OPERATION, counter] and len(lines) == 1,
          f"calls={calls} lines={lines}")


def t01_launch_gh_is_not_measured():
    calls, lines, result = _t01_measured_operation(_fgh.launch_gh, 0)
    check("T-01 launch_gh: telemetry ON still launches exactly once and records nothing",
          calls == [[_T01_FAKE_GH] + _T01_OPERATION] and lines == [] and result.returncode == 0,
          f"calls={calls} lines={lines}")


def _t01_fresh_modules(order):
    """Import order's modules afresh with every launch failing loudly, then hand them back;
    the caller restores the originals."""
    launches = []
    subprocess.run = lambda argv, **k: launches.append(list(argv))
    for name in ("factory_gh", "gh_cost_log"):
        sys.modules.pop(name, None)
    fresh = {name: importlib.import_module(name) for name in order}
    return fresh, launches


def t01_import_orders():
    originals = {name: sys.modules[name] for name in ("factory_gh", "gh_cost_log")}
    for order in (("gh_cost_log", "factory_gh"), ("factory_gh", "gh_cost_log")):
        try:
            fresh, launches = _t01_fresh_modules(order)
            fgh, cost = fresh["factory_gh"], fresh["gh_cost_log"]
            fgh.launch_gh = lambda args, *, input=None: subprocess.CompletedProcess(args, 0, "77", "")
            subprocess.run = _launch_boom
            value = cost._read_counter()
        finally:
            sys.modules.update(originals)
        check(f"T-01 import {' then '.join(order)}: no gh launch at import",
              launches == [], f"launches={launches}")
        check(f"T-01 import {' then '.join(order)}: factory_gh wires the same gh_cost_log",
              fgh.gh_cost_log is cost, f"{fgh.gh_cost_log!r} vs {cost!r}")
        check(f"T-01 import {' then '.join(order)}: the counter resolves factory_gh at call time",
              value == 77, f"value={value!r}")


for _name, _fn in (
    ("counter uses launch_gh", t01_counter_uses_launch_gh),
    ("counter failures read None", t01_counter_failures_read_none),
    ("telemetry one fake binary", t01_telemetry_one_fake_binary),
    ("run_gh measures once", t01_run_gh_measures_once),
    ("launch_gh is not measured", t01_launch_gh_is_not_measured),
    ("import orders", t01_import_orders),
):
    t01_case(_name, _fn)


if FAILURES:
    print(f"\n{len(FAILURES)} of {RAN} FAILING.")
    sys.exit(1)
print(f"\n{RAN}/{RAN} checks passed")
sys.exit(0)
