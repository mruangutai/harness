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
_real_subprocess_run = gh_cost_log.subprocess.run


def restore():
    harness_boundary.resolve_root = _real_resolve_root
    gh_cost_log.subprocess.run = _real_subprocess_run


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
    raise RuntimeError("boom — the counter binary is unreachable")


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
    gh_cost_log.subprocess.run = raising_run
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
    gh_cost_log.subprocess.run = counter_stub([999])
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
    `gh_cost_log.subprocess`, `factory_gh.subprocess` and the freshly-loaded gh-sync module's
    `subprocess` are the SAME imported module object (Python caches modules by name), so
    patching `.run` on any one of them patches all of them."""
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
    gh_cost_log.subprocess.run = fake_run
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
    gh_cost_log.subprocess.run = fake_run
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
    gh_cost_log.subprocess.run = fake_run
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
    gh_cost_log.subprocess.run = fake_run
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
    gh_cost_log.subprocess.run = fake_run
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
    gh_cost_log.subprocess.run = fake_run
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


if FAILURES:
    print(f"\n{len(FAILURES)} of {RAN} FAILING.")
    sys.exit(1)
print(f"\n{RAN}/{RAN} checks passed")
sys.exit(0)
