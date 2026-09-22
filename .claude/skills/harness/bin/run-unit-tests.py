#!/usr/bin/env python3
"""Run Harness's directory-selected unit and integration suites.

The repository has exactly two runnable Python test kinds: tests/unit and
tests/integration. Layout validation always runs before selection reaches the
pool, so a misplaced test cannot disappear by choosing the other kind.

WAS A .sh ENTRY POINT (issue #1674). This native module preserves isolated root
resolution, shell-glob ordering, CLI compatibility and run_pool's mutation
check while eliminating the wrapper's interpreter launches.
"""
import contextlib as _bootstrap_contextlib
import io as _bootstrap_io
import os as _bootstrap_os
import site as _bootstrap_site
import sys as _bootstrap_sys

_bootstrap_bin = _bootstrap_os.path.dirname(
    _bootstrap_os.path.abspath(__file__))
_bootstrap_original_path = list(_bootstrap_sys.path)
_bootstrap_pythonpath = {
    _bootstrap_os.path.realpath(entry)
    for entry in (_bootstrap_os.environ.get("PYTHONPATH") or "").split(
        _bootstrap_os.pathsep)
    if entry
}
_bootstrap_user_sites = _bootstrap_site.getusersitepackages()
if isinstance(_bootstrap_user_sites, str):
    _bootstrap_user_sites = [_bootstrap_user_sites]
_bootstrap_unsafe = _bootstrap_pythonpath | {
    _bootstrap_os.path.realpath(_bootstrap_bin),
    _bootstrap_os.path.realpath(_bootstrap_os.getcwd()),
    *(_bootstrap_os.path.realpath(entry) for entry in _bootstrap_user_sites),
}
_bootstrap_sys.path[:] = [
    entry for entry in _bootstrap_sys.path
    if entry and _bootstrap_os.path.realpath(entry) not in _bootstrap_unsafe
]


# ACCEPTED DUPLICATION (FEAT-61 D-09, DEC-234). This prologue is copied, not shared, in
# branch-create-gate.py, gh-close-gate.py, merge-gate.py, plan-sign-gate.py: it runs BEFORE the
# trusted bin path is on sys.path, so no helper can be imported to hold it — the code below IS
# what creates the import seam. Change all five together; never replace one with an import.
def _resolve_root():
    """Resolve through the trusted sibling with isolated import semantics."""
    try:
        _bootstrap_sys.path.insert(0, _bootstrap_bin)
        with _bootstrap_contextlib.redirect_stderr(_bootstrap_io.StringIO()):
            import harness_boundary
            return harness_boundary.resolve_root(_bootstrap_bin)
    except Exception:
        return ""


ROOT = _resolve_root()
if not ROOT or not _bootstrap_os.path.isdir(ROOT):
    print(
        f"run-unit-tests.py: no harness root could be resolved from "
        f"{_bootstrap_bin} — refusing to run",
        file=_bootstrap_sys.stderr,
    )
    raise SystemExit(2)
_bootstrap_sys.path[:] = _bootstrap_original_path

import glob
import os
import sys
import traceback

BIN_DIR = ".claude/skills/harness/bin"
USAGE = "usage: run-unit-tests.py [--kind unit|integration|all] [--check-layout]"


def _selection(argv):
    """Return (kind, check_layout_only), or None for unsupported syntax."""
    if not argv:
        return "all", False
    if argv[0] == "--kind":
        return (argv[1] if len(argv) > 1 else "all"), False
    if argv[0] == "--check-layout":
        return "all", True
    return None


def _patterns(kind):
    if kind == "unit":
        return ("tests/unit/test-*.py",)
    if kind == "integration":
        return ("tests/integration/test-*.py",)
    if kind == "all":
        return ("tests/unit/test-*.py", "tests/integration/test-*.py")
    return None


def _shell_glob(pattern):
    """Match Bash's sorted glob and unmatched-literal behavior."""
    matches = sorted(glob.glob(pattern))
    return matches or [pattern]


def _scripts(patterns):
    return [path for pattern in patterns for path in _shell_glob(pattern)]


def _layout_output(suite_layout):
    """Render violations as the old command substitution observed them."""
    try:
        return "\n".join(
            str(finding) for finding in suite_layout.violations(ROOT)
        ).rstrip("\n"), None
    except Exception:
        return "", traceback.format_exc().rstrip("\n")


def _validate_layout(suite_layout):
    output, crash = _layout_output(suite_layout)
    if crash is not None:
        print(f"MISCONFIGURED: layout check crashed: {crash}", file=sys.stderr)
        return False
    if output:
        for line in output.split("\n"):
            print(f"MISCONFIGURED: {line}", file=sys.stderr)
        return False
    return True


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    selection = _selection(argv)
    if selection is None:
        print(USAGE, file=sys.stderr)
        return 2
    kind, check_layout_only = selection
    patterns = _patterns(kind)
    if patterns is None:
        print(
            f"run-unit-tests.py: unknown kind '{kind}' — use unit, integration or all",
            file=sys.stderr,
        )
        return 2

    os.chdir(ROOT)
    sys.path.insert(0, os.path.join(ROOT, BIN_DIR))
    import suite_layout
    import run_pool

    if not _validate_layout(suite_layout):
        return 2
    if check_layout_only:
        return 0
    return run_pool.main([
        "--mutation-check", BIN_DIR, "--", *_scripts(patterns)
    ])


if __name__ == "__main__":
    raise SystemExit(main())
