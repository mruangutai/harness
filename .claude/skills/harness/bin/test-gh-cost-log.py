#!/usr/bin/env python3
"""Tests for gh_cost_log.py (FEAT-29 T-03) — in-process, no subprocess, no real gh, no writes to
the real .harness/logs (every case redirects factory_config.harness_root() to a tmp root and
asserts the redirect took effect BEFORE asserting anything about file contents — a test that
skipped that check could silently pollute the real checkout's log directory instead of failing).

The recorder is OPT-IN, default OFF (approval amendment 5, 2026-08-19): every case below that
exercises recording sets HARNESS_GH_COST_LOG=1 explicitly, and cleans it up in a finally so it
never leaks between cases. The SC-05 cases near the end assert the OFF state (variable unset)
instead — those must NOT set it.

    ./test-gh-cost-log.py    -> exit 0 all pass, 1 otherwise
"""
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gh_cost_log  # noqa: E402
import factory_config  # noqa: E402

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


_real_harness_root = factory_config.harness_root
_real_subprocess_run = gh_cost_log.subprocess.run


def restore():
    factory_config.harness_root = _real_harness_root
    gh_cost_log.subprocess.run = _real_subprocess_run


def redirect(tmp):
    """Point gh_cost_log's log resolution at tmp. Returns the expected log path for TODAY, and
    asserts the redirect actually took effect before the caller trusts it — the log-path trap."""
    factory_config.harness_root = lambda: tmp
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


if FAILURES:
    print(f"\n{len(FAILURES)} of {RAN} FAILING.")
    sys.exit(1)
print(f"\n{RAN}/{RAN} checks passed")
sys.exit(0)
