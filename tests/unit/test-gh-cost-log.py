#!/usr/bin/env python3
"""Tests for gh_cost_log.py (FEAT-29 T-03) — in-process, no subprocess, no real gh, no writes to
the real .harness/logs (every case redirects harness_boundary.resolve_root() to a tmp root and
asserts the redirect took effect BEFORE asserting anything about file contents — a test that
skipped that check could silently pollute the real checkout's log directory instead of failing).

The recorder is OPT-IN, default OFF (approval amendment 5, 2026-08-19): every case below that
exercises recording sets HARNESS_GH_COST_LOG=1 explicitly through log_case(), which restores the
environment when the case ends so it never leaks between cases. The SC-05 cases near the end
assert the OFF state (variable unset) instead — those must NOT set it.

    ./test-gh-cost-log.py    -> exit 0 all pass, 1 otherwise
"""
from unit_support import BIN, TESTS

import importlib
import importlib.util as _ilu
import json
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from unittest.mock import patch

from check_support import Checks

import factory_gh as _fgh
import gh_cost_log
import harness_boundary

C = Checks()
check = C.check

_real_resolve_root = harness_boundary.resolve_root
# Every gh launch — the counter read through factory_gh.launch_gh included — goes through the
# one shared subprocess.run module attribute, so that is the one attribute every case patches.
_real_subprocess_run = subprocess.run
_VAR = "HARNESS_GH_COST_LOG"


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


@contextmanager
def log_case(value=None, run=None):
    """One case: a tmp root behind redirect(), HARNESS_GH_COST_LOG set to value (None means
    genuinely unset, not merely "0"), and subprocess.run replaced by run when given. Yields the
    expected log path; the environment, resolve_root and subprocess.run are restored on exit."""
    with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ):
        path = redirect(tmp)
        os.environ.pop(_VAR, None)
        if value is not None:
            os.environ[_VAR] = value
        if run is not None:
            subprocess.run = run
        try:
            yield path
        finally:
            restore()


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


def invocation_lines(path):
    """The recorded lines minus the one coverage line a fresh log file starts with."""
    return [l for l in read_lines(path) if "coverage" not in l]


def first_or_empty(lines):
    return lines[0] if lines else {}


def raising(exc):
    """A subprocess.run stand-in that raises exc on every call."""
    def run(*a, **k):
        raise exc
    return run


def completed(stdout, rc=0):
    """A subprocess.run stand-in that returns one fixed result on every call."""
    return lambda argv, **k: subprocess.CompletedProcess(argv, rc, stdout, "")


def raised(exc_type, fn, *args):
    """True when fn(*args) raises exc_type; any other exception propagates."""
    try:
        fn(*args)
    except exc_type:
        return True
    return False


# ---------------- record(): keys, cost, and the fresh-file coverage line ----------------

with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ):
    path = redirect(tmp)
    check("redirect took effect before any assertion about content",
          path.startswith(tmp + os.sep), path)

    os.environ[_VAR] = "1"
    gh_cost_log.record(["issue", "view", "1"], 100, 105, 0)
    lines = read_lines(path)
    first = first_or_empty(lines)
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
restore()


# ---------------- a failing invocation is STILL recorded ----------------

with log_case("1") as path:
    gh_cost_log.record(["issue", "create"], 200, 210, 1)
    non_cov = invocation_lines(path)
    rec = first_or_empty(non_cov)
    check("a failing invocation (rc=1) is still recorded",
          len(non_cov) == 1, f"lines={read_lines(path)}")
    check("the failing invocation's line carries rc 1",
          rec.get("rc") == 1, rec)
    check("the failing invocation's line carries its real cost",
          rec.get("cost") == 10, rec)


# ---------------- -f/-F value truncation ----------------

with log_case("1") as path:
    long_query = "query=" + ("x" * 200)
    gh_cost_log.record(["api", "graphql", "-f", long_query, "-F", "owner=short"], 1, 1, 0)
    argv = first_or_empty(invocation_lines(path)).get("argv") or []
    check("a -f value longer than 80 chars is truncated with an ellipsis",
          len(argv) > 3 and len(argv[3]) < len(long_query) and argv[3].endswith("..."), argv)
    check("a short -F value is left untouched",
          len(argv) > 5 and argv[5] == "owner=short", argv)


# ---------------- HARNESS_GH_COST_LOG=0 disables recording entirely ----------------

with log_case("0") as path:
    gh_cost_log.record(["issue", "view", "1"], 1, 1, 0)
    check("HARNESS_GH_COST_LOG=0 writes no line at all",
          not os.path.exists(path), f"exists={os.path.exists(path)}")


# ---------------- measured(): a counter read that raises never propagates ----------------
# FEAT-64: an unreachable binary is an OSError — the class the boundary really raises.

def _measure_issue_view():
    with gh_cost_log.measured(["issue", "view", "1"]) as m:
        m.returncode = 0


with log_case("1", run=raising(OSError("boom — the counter binary is unreachable"))) as path:
    check("a counter read that raises does not propagate out of measured()",
          not raised(Exception, _measure_issue_view))
    rec = first_or_empty(invocation_lines(path))
    check("a counter-read failure records null before/after/cost",
          rec.get("before") is None and rec.get("after") is None and rec.get("cost") is None,
          rec)
    check("a counter-read failure still records the real returncode",
          rec.get("rc") == 0, rec)


# ---------------- measured(): the counter's own call is never wrapped (recursion guard) ----
# HARNESS_GH_COST_LOG=1 set explicitly — proves the recursion guard itself excludes the
# counter's own argv, not just that recording happens to be off (amendment 5).

with log_case("1", run=completed("999")) as path:
    with gh_cost_log.measured(gh_cost_log._COUNTER_ARGV) as m:
        m.returncode = 0
    check("measured() never records a line for the counter's own argv",
          not os.path.exists(path) or read_lines(path) == [], f"exists={os.path.exists(path)}")


# ---------------- SC-05: opt-in default is OFF — variable UNSET writes nothing, both halves --

for _label, _argv, _before, _after, _rc in (("a successful", ["issue", "view", "1"], 100, 105, 0),
                                            ("a FAILING", ["issue", "create"], 200, 210, 1)):
    with log_case() as path:
        gh_cost_log.record(_argv, _before, _after, _rc)
        check(f"with HARNESS_GH_COST_LOG unset, {_label} invocation creates no log file",
              not os.path.exists(path), f"exists={os.path.exists(path)}")
        check(f"with HARNESS_GH_COST_LOG unset, {_label} invocation writes no line",
              read_lines(path) == [], f"lines={read_lines(path)}")


# ---------------- WRAP SITES: factory_gh.run_gh and gh-sync.py's gh() -------------------
# These cases drive the REAL wrappers (factory_gh.run_gh and gh-sync.py's gh()) through a fake
# gh — a counting subprocess.run double standing in for the gh binary — parameterised on
# recorder state (ON/OFF), and assert BOTH the write AND the subprocess call count. The call
# count pins measured()'s own guard (`if not _enabled() or is_counter_call(argv)`) short-
# circuiting OFF to one call; the record() cases above only reach record()'s separate guard.


def _load_gh_sync():
    """gh-sync.py's hyphen blocks a plain import. A fresh module each call, but `subprocess`,
    `gh_cost_log` and `harness_boundary` are all resolved through sys.modules's cache, so
    patches on those module objects apply here too without re-patching per module instance."""
    spec = _ilu.spec_from_file_location("_ghs_t03_wrap_site", str(BIN / "gh-sync.py"))
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
        if list(argv[1:]) == gh_cost_log._COUNTER_ARGV:
            return subprocess.CompletedProcess(argv, 0, str(1000 + len(calls)), "")
        return subprocess.CompletedProcess(argv, rc, stdout, "" if rc == 0 else "boom")

    return fake_run, calls


def _wrap_site_case(label, call, on):
    fake_run, calls = _counting_fake()
    with log_case("1" if on else None, run=fake_run) as path:
        call(["issue", "view", "1"])
        if on:
            check(f"{label} wrap site, ON: one line written for the wrapped invocation",
                  len(invocation_lines(path)) == 1, f"lines={read_lines(path)}")
            check(f"{label} wrap site, ON: three subprocess calls (counter, real, counter)",
                  len(calls) == 3, f"calls={calls}")
        else:
            check(f"{label} wrap site, OFF: no line written",
                  not os.path.exists(path) or read_lines(path) == [],
                  f"exists={os.path.exists(path)}")
            check(f"{label} wrap site, OFF: exactly one subprocess call (the real call only)",
                  len(calls) == 1, f"calls={calls}")


for _label, _call in (("factory_gh.run_gh", lambda a: _fgh.run_gh(a)),
                      ("gh-sync.py gh()", lambda a: _load_gh_sync().gh(a))):
    for _on in (True, False):
        _wrap_site_case(_label, _call, _on)


# --- factory_gh.run_gh wrap site, ON, FAILING invocation: the recorded rc is the real one ---
# run_gh always raises GhError on non-zero rc (forced, not a design choice); this asserts the
# LOGGED RECORD'S rc equals 1 — the line try_gh's `cost.returncode = ...` writes.
fake_run, calls = _counting_fake(rc=1)
with log_case("1", run=fake_run) as path:
    gh_raised = raised(_fgh.GhError, _fgh.run_gh, ["issue", "view", "1"])
    non_cov = invocation_lines(path)
    check("factory_gh.run_gh wrap site, FAILING: GhError was raised",
          gh_raised)
    check("factory_gh.run_gh wrap site, FAILING: one line written for the wrapped invocation",
          len(non_cov) == 1, f"lines={read_lines(path)}")
    check("factory_gh.run_gh wrap site, FAILING: the recorded rc equals the real exit code (1)",
          len(non_cov) == 1 and non_cov[0].get("rc") == 1,
          f"non_cov={non_cov}")

# --- factory_gh.run_gh wrap site, OFF, FAILING invocation ---
# record()'s own guard already forecloses a write for any rc once _enabled() is False; this pins
# measured()'s guard firing on the non-zero-rc path specifically (SC-05: "including for a
# failing invocation").
fake_run, calls = _counting_fake(rc=1)
with log_case(run=fake_run) as path:
    gh_raised = raised(_fgh.GhError, _fgh.run_gh, ["issue", "view", "1"])
    check("OFF, FAILING: GhError was still raised (the wrapper does not swallow the real error)",
          gh_raised)
    check("OFF, FAILING: no log file is created",
          not os.path.exists(path), f"exists={os.path.exists(path)}")
    check("OFF, FAILING: no line is written",
          read_lines(path) == [], f"lines={read_lines(path)}")
    check("OFF, FAILING: exactly one subprocess call (the real call only, neither counter read)",
          len(calls) == 1, f"calls={calls}")


# FEAT-64 (SC-03): the counter and the log are BEST-EFFORT at their real boundaries — a
# counter binary that is absent, fails, or prints junk is None; an unwritable log dir is a
# silent return — but an unrelated programming defect escapes rather than reading as "the
# counter could not be read".
with log_case():
    subprocess.run = raising(FileNotFoundError("no gh"))
    check("FEAT-64: an absent counter binary reads None", gh_cost_log._read_counter() is None)
    subprocess.run = completed("not-a-number")
    check("FEAT-64: a counter that prints junk reads None", gh_cost_log._read_counter() is None)
    subprocess.run = raising(RuntimeError("unrelated"))
    check("FEAT-64: an unrelated RuntimeError escapes _read_counter",
          raised(RuntimeError, gh_cost_log._read_counter))
with log_case("1"), patch.object(gh_cost_log.json, "dumps", side_effect=RuntimeError("unrelated")):
    check("FEAT-64: an unrelated RuntimeError escapes record",
          raised(RuntimeError, gh_cost_log.record, ["gh", "api"], 1, 2, 0))


# ---------------- FEAT-2452 T-01: the counter reads through factory_gh.launch_gh -------------
# The counter read shares the one launch and FACTORY_GH boundary but stays outside cost
# accounting: launch_gh is never measured, and only try_gh (which run_gh adapts) measures, once.
# Every case pins FACTORY_GH to one fake binary path and patches the shared subprocess.run, so
# no real gh can start even if a case's own patch were missed.
_T01_FAKE_GH = str(TESTS / "unit" / "t01-fake-gh-never-installed")
_T01_OPERATION = ["issue", "view", "1"]


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
    with patch.multiple(_fgh, launch_gh=fake_launch, run_gh=_launch_boom, try_gh=_launch_boom):
        value = gh_cost_log._read_counter()
    check("T-01 _read_counter: reads the counter through factory_gh.launch_gh only",
          value == 1234 and seen == [(gh_cost_log._COUNTER_ARGV, None)], f"value={value!r} seen={seen}")


def t01_counter_failures_read_none():
    def failed_launch(args, *, input=None):
        raise _fgh.GhError(list(args), None, "", "", "gh not found", "gh", "install gh")

    def nonzero_launch(args, *, input=None):
        return subprocess.CompletedProcess(args, 1, "", "HTTP 401")

    subprocess.run = _launch_boom
    with patch.object(_fgh, "launch_gh", failed_launch):
        typed = gh_cost_log._read_counter()
    with patch.object(_fgh, "launch_gh", nonzero_launch):
        nonzero = gh_cost_log._read_counter()
    check("T-01 _read_counter: a typed launch failure and a nonzero counter both read None",
          typed is None and nonzero is None, f"typed={typed!r} nonzero={nonzero!r}")


def _t01_measured_operation(fn, rc):
    """Drive fn over one operation with telemetry ON and the one fake binary; return the
    launches, the recorded lines and fn's result."""
    fake_run, calls = _counting_fake(rc=rc)
    with log_case("1", run=fake_run) as path:
        result = fn(_T01_OPERATION)
        lines = invocation_lines(path)
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


sys.exit(C.report())
