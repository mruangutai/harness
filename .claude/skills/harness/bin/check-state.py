#!/usr/bin/env python3
"""check-state.py — deterministic state-invariant checker. Run at every /harness entry.

Exit 0 = clean. Exit 1 = violations (listed). Exit 2 = cannot run (no harness root).

WAS A .sh (issue #1674). 2,969 lines of Python lived in a `<<'PY'` heredoc where
ast, linters, coverage and #1594's reader audit could not see any of it -- this is
the largest such file in the repository and the reason that audit had to declare a
quarter of its own target surface out of scope.

THE BOOTSTRAP IS PRESERVED EXACTLY, and it is the part worth reading before editing:

  * `sys.argv[1]` is the resolved harness root and `sys.argv[2]` is this script's
    directory. The body reads both at roughly ten sites. Rather than rewrite those
    references -- ten chances to introduce a defect in a gate -- argv is rebuilt
    below to the exact shape the heredoc received. Stray user arguments are still
    ignored, because the wrapper never forwarded "$@" either.
  * The old wrapper ran `python3 -c '... sys.path.pop(0) ...'`, popping the empty
    string that `-c` puts on sys.path so the CWD could not shadow a sibling module.
    Running as a real script needs no such trick: sys.path[0] is already this file's
    directory, and the CWD is never added. The pop is gone because its cause is.
  * The `cd "$root"` and the exported PYTHONPATH are NOT cosmetic. Subprocesses
    spawned by the body inherit both, and several resolve paths relative to the
    working directory. They are reproduced verbatim.
"""
import contextlib as _contextlib
import io as _io
import os as _os
import subprocess as _subprocess
import sys as _sys

_selfdir = _os.path.dirname(_os.path.abspath(__file__))
_sys.path.insert(0, _selfdir)


_ROOT_PROBE = (
    "import sys; sys.path.insert(0, sys.argv[1]); import harness_boundary; "
    "print(harness_boundary.resolve_root(sys.argv[1]))"
)


def _resolve_root():
    captured = _io.StringIO()
    try:
        with _contextlib.redirect_stderr(captured):
            import harness_boundary as _hb
            return _hb.resolve_root(_selfdir), captured.getvalue()
    except (ModuleNotFoundError, ValueError):
        # The module did not import (a first-party sibling -- ModuleNotFoundError, the only
        # shape a missing file takes), or resolve_root refused (strict: no MARKER anywhere).
        # Either way the clean-interpreter probe below produces the operator-facing stderr.
        probe = _subprocess.run(
            [_sys.executable, "-I", "-c", _ROOT_PROBE, _selfdir],
            capture_output=True, text=True)
        return "", probe.stderr


_root, _root_stderr = _resolve_root()
if not _root or not _os.path.isdir(_root):
    print(f"check-state.py: no harness root could be resolved from {_selfdir}"
          " — refusing to run.", file=_sys.stderr)
    _sys.stderr.write(_root_stderr)
    raise SystemExit(2)
_sys.stderr.write(_root_stderr)

_os.environ["PYTHONPATH"] = (
    _selfdir + (_os.pathsep + _os.environ["PYTHONPATH"] if _os.environ.get("PYTHONPATH") else "")
)
_os.chdir(_root)

# The exact argv the heredoc was handed: argv[1] = root, argv[2] = this bin dir.
_USER_ARGV = _sys.argv[1:]
_sys.argv = [_sys.argv[0], _root, _selfdir]

import sys, os, re, glob, json, subprocess

sys.path.insert(0, sys.argv[2])
import harness_yaml
import artifact_accessors
import handoff_policy
import run_identity
import harness_boundary

# Review finding 1: `require_or_die` is the module's documented gate for exactly
# this script and had ZERO production callers, so a missing PyYAML surfaced as
# every file "does not parse" and exit 1 — /harness entry reporting "violations
# found" for an absent dependency. It gates the ORCHESTRATOR, not a write, so a
# hard block here costs no recovery path (D-06); the bootstrap escape is for the
# two hooks only.
harness_yaml.require_or_die()

root = sys.argv[1]

from check_state import runner

if __name__ == "__main__":
    sys.exit(runner.main(root, _USER_ARGV))
