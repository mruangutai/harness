#!/usr/bin/env python3
"""Tests for factory_cli.py, the shared CLI contract (D-08).

WHY: every factory tool's entry point goes through run(), and the one behaviour that
matters most is the trap in BOTH directions — an unhandled exception must exit 2 (never
the silent-looking exit 1 for "nothing to do"), while a deliberate sys.exit(1) or
sys.exit(3) must pass through unchanged. A wrapper that got either direction wrong would
still look plausible in isolation, so both are asserted here, in-process, with no
subprocess spawned (run-unit-tests.py classifies this as UNIT for exactly that reason).
"""
from unit_support import BIN  # noqa: F401  (puts bin/ on sys.path)
import contextlib
import io
import json
import os
import sys
import unicodedata
from unittest import mock

from check_support import Checks
import factory_cli as cli

C = Checks()
check = C.check


def capture(fn, *args, **kw):
    """Call fn(*args, **kw), capturing stdout/stderr and any SystemExit code (None if none)."""
    out, err = io.StringIO(), io.StringIO()
    code = None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            fn(*args, **kw)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


def run_capturing(fn):
    """Call fn under run(), capturing stdout/stderr and the resulting exit code."""
    return capture(cli.run, "t", fn)


# ---------------- run(): success path ----------------
def _ok():
    return None


code, out, err = run_capturing(_ok)
check("run(): fn returning normally leaves exit 0", code in (0, None),
      f"code={code!r}")
check("run(): success writes nothing to stdout", out == "", f"out={out!r}")
check("run(): success writes nothing to stderr", err == "", f"err={err!r}")


# ---------------- run(): the trap in the failure direction ----------------
def _raises_keyerror():
    raise KeyError("missing")


code, out, err = run_capturing(_raises_keyerror)
check("run(): unhandled KeyError exits 2, not 1", code == cli.EXIT_REFUSED,
      f"code={code!r}")
check("run(): unhandled KeyError leaves stdout empty", out == "", f"out={out!r}")
check("run(): unhandled KeyError stderr mentions FACTORY_DEBUG", "FACTORY_DEBUG" in err,
      f"err={err!r}")


# ---------------- run(): the trap in the OTHER direction ----------------
def _exit1():
    sys.exit(1)


def _exit3():
    sys.exit(3)


code, out, err = run_capturing(_exit1)
check("run(): fn calling sys.exit(1) still exits 1", code == 1, f"code={code!r}")

code, out, err = run_capturing(_exit3)
check("run(): fn calling sys.exit(3) still exits 3", code == 3, f"code={code!r}")


# ---------------- run(): an expected exception ----------------
class MyError(Exception):
    pass


def _raises_expected():
    raise MyError("bad config at /x/y")


code, out, err = capture(cli.run, "t", _raises_expected, expected=(MyError,))
want = "factory: t: bad config at /x/y\n"
check("run(): expected exception produces the preformed line, no prefix duplication",
      err == want, f"err={err!r}")
check("run(): expected exception has no 'unexpected failure' text",
      "unexpected failure" not in err)
check("run(): expected exception exits 2", code == cli.EXIT_REFUSED, f"code={code!r}")


# ---------------- run(): FACTORY_DEBUG controls the traceback, not the hint text ----------------
# The hint text mentions "FACTORY_DEBUG" on EVERY unexpected failure regardless of the env
# var (asserted above) — that alone does not prove the env var actually gates a traceback.
# Deleting the `if os.environ.get("FACTORY_DEBUG")` branch in factory_cli.py would still pass
# every other check in this file, so this pair is the one that would catch it.
with mock.patch.dict(os.environ, {"FACTORY_DEBUG": "1"}):
    code, out, err = run_capturing(_raises_keyerror)
    check("run(): FACTORY_DEBUG=1 prints a traceback after the hint line",
          "Traceback" in err and err.index("FACTORY_DEBUG") < err.index("Traceback"),
          f"err={err!r}")

    del os.environ["FACTORY_DEBUG"]
    code, out, err = run_capturing(_raises_keyerror)
    check("run(): without FACTORY_DEBUG set, no traceback is printed",
          "Traceback" not in err, f"err={err!r}")


# ---------------- message(): exact grammar and ordering ----------------
got = cli.message("mytool", "bad path", "/a/b", "fix it")
want = "factory: mytool: bad path: /a/b — fix it"
check("message(): renders the five parts in order with the em dash", got == want,
      f"got={got!r}")


# ---------------- body(): the one place the failure body is built ----------------
got = cli.body("bad path", "/a/b", "fix it")
want = "bad path: /a/b — fix it"
check("body(): builds 'what: value — next_step'", got == want, f"got={got!r}")

# The dash codepoint matters on its own: an en dash or a hyphen would make body() and
# `want` above equally wrong if authored the same way in the same sitting. Cross-check
# against the Unicode character database as an independent source of truth for which
# codepoint "em dash" (D-08) means here, rather than trusting this file's own literal.
_EM_DASH = unicodedata.lookup("EM DASH")
check("the Unicode database names U+2014 EM DASH (source of truth for 'em dash')",
      _EM_DASH == "\u2014", f"found={_EM_DASH!r}")
check("body(): the dash emitted is U+2014, not a hyphen or en dash",
      _EM_DASH in got and unicodedata.lookup("EN DASH") not in got and got.count("-") == 0,
      f"got={got!r}")


# ---------------- payload(): the sole stdout shape ----------------
_, out, err = capture(cli.payload, {"a": 1})
lines = out.splitlines()
check("payload(): writes exactly one stdout line", len(lines) == 1, f"lines={lines!r}")
check("payload(): that line parses as json.loads",
      len(lines) == 1 and json.loads(lines[0]) == {"a": 1})
check("payload(): writes nothing to stderr", err == "", f"err={err!r}")

try:
    cli.payload("a string")
    raised = False
except TypeError:
    raised = True
check("payload(): a plain string raises TypeError", raised)


# ---------------- nothing_to_do(): stderr only, exit 1 ----------------
code, out, err = capture(cli.nothing_to_do, "t", "no issues claimable")
check("nothing_to_do(): writes nothing to stdout", out == "", f"out={out!r}")
check("nothing_to_do(): writes to stderr", "no issues claimable" in err, f"err={err!r}")
check("nothing_to_do(): exits 1 (EXIT_NOTHING), not an error", code == cli.EXIT_NOTHING,
      f"code={code!r}")


# ---------------- exit code constants ----------------
check("EXIT_OK == 0", cli.EXIT_OK == 0)
check("EXIT_NOTHING == 1", cli.EXIT_NOTHING == 1)
check("EXIT_REFUSED == 2", cli.EXIT_REFUSED == 2)
check("EXIT_RACE == 3", cli.EXIT_RACE == 3)


# ---------------- refuse() / lost_race(): fail() plus the right exit ----------------
code, out, err = capture(cli.refuse, "t", "bad config", "/x", "fix it")
check("refuse(): exits EXIT_REFUSED", code == cli.EXIT_REFUSED, f"code={code!r}")
check("refuse(): stdout stays empty", out == "")
check("refuse(): stderr carries message()",
      err == cli.message("t", "bad config", "/x", "fix it") + "\n")

code, out, err = capture(cli.lost_race, "t", "issue owned", "#12", "pick another")
check("lost_race(): exits EXIT_RACE", code == cli.EXIT_RACE, f"code={code!r}")
check("lost_race(): stdout stays empty", out == "")


sys.exit(C.report())
