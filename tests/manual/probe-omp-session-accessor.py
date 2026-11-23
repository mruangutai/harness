#!/usr/bin/env python3
"""FEAT-44 / issue #923, repaired by FEAT-2397 / issue #2194 — a MANUAL host check. Not a CI gate.

The orchestrator context advisory in `.omp/extensions/harness-hooks.ts` reads the host's own
session accounting, `ctx.getContextUsage().tokens`, inside a dispatched task child.
Every case in omp-hooks.test.ts stubs that accessor, so a green unit suite proves only that the
stub works. That is issue #923's own failure shape one layer out. This is the one check that
reaches the real binary. It dispatches a real task subagent under the committed probe extension
and asserts four things:

  case3  a nested task child session was observed. Its `getSessionFile()` path decides that,
         through `is_nested`, and never its usage;
  case4  that child's `getContextUsage()` returned finite numbers for tokens, contextWindow and
         percent. bool, absent, null, NaN and infinities are rejected;
  case5  a flat main session was observed: a valid, nonempty `.jsonl` path that is not nested.
         A missing main is a failure, not an optional pass;
  case6  the measured child and the main are distinct probe sessions.

Identity and measurement are independent: no usage value moves a session between child and main.
`usageDefined` is recorded as a diagnostic only. tests/unit/test-session-accessor-probe.py drives
these helpers offline; that proves the probe's logic, not the host's wiring.

WHY IT IS MANUAL AND NOT A GATE — corrected after it reddened CI, and stated plainly because an
earlier version of this docstring claimed the opposite.

It was first registered in INTEGRATION_SCRIPTS with the reasoning that a soft skip would be the
gate-that-looks-real-and-does-nothing shape DEC-163 forbids. That reasoning collapsed two
different absences:

  - "the accessor moved"      -> real evidence, and this check must fail loudly on it;
  - "the host is not installed here" -> no evidence about the accessor at all.

Measured on the CI run for PR #982: `FAIL - case1: the omp binary is on PATH (None)`. And the
deeper reason it can never be a gate is that this check makes a LIVE MODEL CALL — it dispatches a
real subagent with `--model anthropic/claude-sonnet-5`. The tests workflow installs bun and
python and references no `secrets.*` at all, so it holds no model credentials. Installing omp in
CI would not fix this; the check would still have nothing to authenticate with.

So the honest arrangement is that the check is registered only as the `locally_run` test kind
`omp_session_accessor`, never a CI gate. A human (or a release step) runs it on a machine that has
omp and credentials. It is named `probe-` rather than `test-` so the unit glob does not sweep it
back into the suite.

WHAT THIS COSTS, RECORDED RATHER THAN GLOSSED. The version-floor risk recorded below — that a
later OMP drops or breaks the accessor in task children — is therefore watched by a check
someone must REMEMBER TO RUN, not by CI. That is weaker than an automated gate and is not dressed
up as one. Nothing available in this repository's CI can verify a property of a binary that CI
does not have.

WHERE IT DOES RUN, IT FAILS RATHER THAN SKIPS: if omp is present and a task child's usage is not
numeric, or the probe yields no child or no main, this exits non-zero.

THE PROBE EXTENSION. `tests/manual/probe-session-accessors.ts` registers one `turn_end` handler.
It calls `getContextUsage()` once and saves the returned object, numbers unchanged, with
`usageDefined` beside it as a diagnostic. It also enumerates `ctx.sessionManager`'s read-only
getters and calls each. It appends one JSON line per session to `$CTXPROBE_OUT` (default
`/tmp/ctxprobe/out2.jsonl`). Reproduce the measurement by hand from the repository root:

    omp -p "Use the task tool once: spawn a subagent of type 'sonic' whose entire task is to reply with the single word pong." \\
        -e tests/manual/probe-session-accessors.ts \\
        --no-extensions --no-skills --no-rules --auto-approve \\
        --model anthropic/claude-sonnet-5 \\
        --session-dir /tmp/ctxprobe/sessions

`--no-extensions --no-skills --no-rules` isolates it from harness machinery.

HISTORICAL OBSERVATION, BOUNDED — 2026-08-28, reproduced 2026-08-29, one pre-18.0.11 OMP build on
one machine:

    session              getContextUsage()                          getSessionFile()
    main                 defined ({tokens, contextWindow, percent})  <dir>/<ts>_<session-id>.jsonl
    subagent (depth 1)   undefined                                  <dir>/<ts>_<parent-id>/<DispatchLabel>.jsonl

The undefined subagent usage was upstream can1357/oh-my-pi#10097, closed by #10098 and released
in omp 18.0.11. It describes those builds only. The earlier probe used it as the child's identity,
which #2194 reported false on OMP 18.18.0. The path shape in that table is what still identifies
a child: a nested transcript keyed by dispatch label under the parent's directory, against the
main's flat one.

API FLOOR AND ACCEPTANCE. The native accessor needs omp >= 18.0.11. FEAT-2397 accepts omp 19.1.0
on this check: a nested task child must report numeric usage, and a distinct flat main must be
observed. That a later OMP behaves the same is NOT established; it is the version-floor risk
this check watches.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
# The extension lives beside this check so the check and a hand reproduction run the same code.
PROBE = ROOT / "tests/manual/probe-session-accessors.ts"

TASK = ("Use the task tool exactly once: spawn a subagent of type 'sonic' whose entire task "
        "is to reply with the single word pong.")

# A task child's transcript is nested: <ts>_<parent-id>/<DispatchLabel>.jsonl. A main's is a flat
# <ts>_<session-id>.jsonl. This is the one session-identity pattern; is_nested is its only reader.
NESTED_SESSION_FILE = re.compile(r"/\d{4}-\d{2}-\d{2}T[\d-]+Z_[0-9a-f-]+/[^/]+\.jsonl$")
SESSION_FILE_SUFFIX = ".jsonl"
USAGE_FIELDS = ("tokens", "contextWindow", "percent")

RESULTS: list[tuple[str, bool, object]] = []


def check(name: str, ok: bool, detail: object = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} - {name}" + ("" if ok else f" ({detail!r})"))


def session_file(row: dict) -> str:
    """The row's getSessionFile() result when the probe saw a string, else ''."""
    value = (row.get("probed") or {}).get("getSessionFile")
    return value if isinstance(value, str) else ""


def _is_session_file(path: object) -> bool:
    """An absolute path to a nonempty-named .jsonl file. Rejects tryCall's 'undefined'/'THREW'."""
    if not isinstance(path, str) or not path.endswith(SESSION_FILE_SUFFIX):
        return False
    return PurePosixPath(path).is_absolute() and len(PurePosixPath(path).name) > len(SESSION_FILE_SUFFIX)


def is_nested(path: object) -> bool:
    """Identity: True for a task child's own nested transcript. Usage never enters into it."""
    return _is_session_file(path) and NESTED_SESSION_FILE.search(path) is not None


def is_flat_main(path: object) -> bool:
    """A flat main candidate: a valid session file that is not nested."""
    return _is_session_file(path) and not is_nested(path)


def _finite_number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def usage_numbers(row: dict) -> dict | None:
    """The saved getContextUsage() numbers when all three are finite, else None. Never invented."""
    usage = row.get("usage")
    if not isinstance(usage, dict):
        return None
    numbers = {field: usage.get(field) for field in USAGE_FIELDS}
    return numbers if all(_finite_number(value) for value in numbers.values()) else None


def _distinct(children: list[dict], mains: list[dict]) -> bool:
    child_ids = {r.get("session") for r in children}
    main_ids = {r.get("session") for r in mains}
    named = None not in child_ids | main_ids
    return bool(children and mains) and named and child_ids.isdisjoint(main_ids)


def _by_path(rows: list[dict], identity) -> list[dict]:
    """The rows whose session-file path satisfies identity (is_nested or is_flat_main)."""
    return [r for r in rows if identity(session_file(r))]


def _field(rows: list[dict], key: str) -> list[object]:
    return [r.get(key) for r in rows]


def observation_checks(rows: list[dict]) -> list[tuple[str, bool, object]]:
    """case3..case6 over the probe's rows. Pure, so the offline tests drive it directly."""
    paths = [session_file(r) for r in rows]
    children = _by_path(rows, is_nested)
    mains = _by_path(rows, is_flat_main)
    measured = [r for r in children if usage_numbers(r) is not None]
    return [
        ("case3: a nested task child session was observed, identified by its session path",
         bool(children), paths),
        ("case4: that child's getContextUsage returned finite tokens, contextWindow and percent",
         bool(measured), _field(children, "usage")),
        ("case5: a flat main session was observed", bool(mains), paths),
        ("case6: the measured child and the main are distinct sessions",
         _distinct(measured, mains), _field(rows, "session")),
    ]


def _observe(omp: str) -> tuple[list[dict], subprocess.CompletedProcess]:
    workdir = tempfile.mkdtemp(prefix="feat44-accessor-")
    out = Path(workdir) / "out.jsonl"
    out.write_text("", encoding="utf-8")
    env = {**os.environ, "CTXPROBE_OUT": str(out)}
    proc = subprocess.run(
        [omp, "-p", TASK, "-e", str(PROBE),
         "--no-extensions", "--no-skills", "--no-rules", "--auto-approve",
         "--model", "anthropic/claude-sonnet-5",
         "--session-dir", str(Path(workdir) / "sessions")],
        capture_output=True, text=True, timeout=600, env=env, cwd=workdir,
    )
    rows = []
    for line in out.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return [r for r in rows if isinstance(r, dict)], proc


def main() -> int:
    omp = shutil.which("omp")
    check("case1: the omp binary is on PATH", omp is not None, omp)
    check("case1: the committed probe extension exists", PROBE.is_file(), str(PROBE))
    if not omp or not PROBE.is_file():
        return finish()

    rows, proc = _observe(omp)
    check("case2: the probe produced at least one observation",
          bool(rows), (proc.returncode, proc.stderr[-400:]))
    if rows:
        for name, ok, detail in observation_checks(rows):
            check(name, ok, detail)
    return finish()


def finish() -> int:
    failed = [name for name, ok, _ in RESULTS if not ok]
    print(f"{'FAIL' if failed else 'PASS'} - {len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
