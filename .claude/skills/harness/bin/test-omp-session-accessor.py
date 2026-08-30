#!/usr/bin/env python3
"""FEAT-44 / issue #923 — the ONE check that reaches the real OMP binary.

Every case in omp-hooks.test.ts stubs `getSessionFile`, so a green unit suite proves only that
the stub works. That is issue #923's own failure shape one layer out: the feature exists because
an assumed host API silently returned nothing, and a suite of stubs would never notice it
happening again.

WHY THIS IS NOT A UNIT TEST, measured 2026-08-29. The plan first specified asserting the shipped
`session-manager.d.ts` from inside `bun test`. That cannot work, for two independent reasons:

  1. `Bun.resolveSync("@oh-my-pi/pi-coding-agent/package.json", ...)` succeeds under `bun run`
     and FAILS under `bun test` — different resolution modes. The plan's feasibility measurement
     was taken in the wrong one.
  2. Three copies disagree on this machine: the RUNNING binary reports 18.0.5, the bun install
     cache holds 18.0.10, and the only stably resolvable copy — global node_modules — is 17.3.8.
     Asserting any of their type declarations says nothing about the binary executing the hooks.

So this drives the binary itself: it dispatches a real subagent under the committed probe
extension and asserts that, in the subagent session, `ctx.sessionManager.getSessionFile()`
returns that subagent's OWN nested transcript path.

FAILS, NEVER SKIPS. If omp is absent, if the probe produces nothing, or if the accessor stops
resolving, this exits non-zero. That is the whole point: it converts the version-floor risk
recorded in the feature's evidence/README.md from an unwatched assumption into something CI
reports. A soft skip here would be the gate-that-looks-real-and-does-nothing shape DEC-163
forbids, and would recreate exactly the defect this feature was written to remove.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parent
# The probe is committed with the feature so this test and the recorded evidence run the same code.
PROBE = (BIN_DIR.parent.parent.parent.parent
         / ".harness/harness/features/FEAT-44-omp-context-advisory/evidence"
         / "probe-session-accessors.ts")

TASK = ("Use the task tool exactly once: spawn a subagent of type 'sonic' whose entire task "
        "is to reply with the single word pong.")

RESULTS: list[tuple[str, bool, object]] = []


def check(name: str, ok: bool, detail: object = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} - {name}" + ("" if ok else f" ({detail!r})"))


def main() -> int:
    omp = shutil.which("omp")
    check("case1: the omp binary is on PATH", omp is not None, omp)
    check("case1: the committed probe extension exists", PROBE.is_file(), str(PROBE))
    if not omp or not PROBE.is_file():
        return finish()

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
    check("case2: the probe produced at least one observation",
          bool(rows), (proc.returncode, proc.stderr[-400:]))
    if not rows:
        return finish()

    def session_file(row: dict) -> str:
        return str((row.get("probed") or {}).get("getSessionFile") or "")

    # The subagent is the session where getContextUsage() is undefined. That is the whole
    # premise: the two accessors do not share the broken wiring.
    subagents = [r for r in rows if r.get("usageDefined") is False]
    check("case3: a subagent session was observed with getContextUsage undefined",
          bool(subagents), [r.get("session") for r in rows])
    if not subagents:
        return finish()

    resolved = [r for r in subagents if session_file(r)]
    check("case4: getSessionFile resolves inside that subagent session",
          bool(resolved), [session_file(r) for r in subagents])
    if not resolved:
        return finish()

    # Nested shape: <ts>_<parent-id>/<DispatchLabel>.jsonl, never a flat
    # <ts>_<session-id>.jsonl. The orchestrator always runs as a dispatched subagent, so the
    # nesting is the property the reader depends on.
    nested = re.compile(r"/\d{4}-\d{2}-\d{2}T[\d-]+Z_[0-9a-f-]+/[^/]+\.jsonl$")
    path = session_file(resolved[0])
    check("case5: the resolved path is the subagent's OWN nested transcript",
          bool(nested.search(path)), path)

    mains = [r for r in rows if r.get("usageDefined") is True and session_file(r)]
    if mains:
        check("case6: the main session resolves to a FLAT transcript, so the two differ",
              not nested.search(session_file(mains[0])), session_file(mains[0]))
    return finish()


def finish() -> int:
    failed = [name for name, ok, _ in RESULTS if not ok]
    print(f"{'FAIL' if failed else 'PASS'} - {len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
