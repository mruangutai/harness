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
    except (ModuleNotFoundError, ValueError):
        # FEAT-64: the module did not import (a missing first-party sibling), or resolve_root
        # refused (strict: no MARKER anywhere) -- the two shapes "no root" takes, matching
        # check-state.py's copy. The four gate copies narrow the same way in FEAT-65.
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
import json
import math
import os
import re
import subprocess
import sys
import traceback

BIN_DIR = ".claude/skills/harness/bin"
DURATIONS = "tests/integration/integration-durations.json"
USAGE = ("usage: run-unit-tests.py [--kind unit|integration|all] "
         "[--shard i/n [--manifest PATH]] | --check-layout")
_VALUE_OPTIONS = {"--kind": "kind", "--shard": "shard", "--manifest": "manifest"}


class UsageError(ValueError):
    """An unusable invocation; reported before any test runs (exit 2)."""


def _take_value(argv, index, option):
    if index + 1 < len(argv):
        return argv[index + 1]
    if option == "--kind":
        return "all"
    raise UsageError(f"{option} requires a value")


def _tokens(argv):
    """Return the raw option dict; options may appear in any order, each at most once."""
    opts = {"kind": None, "shard": None, "manifest": None, "check_layout": False}
    index = 0
    while index < len(argv):
        option = argv[index]
        if option == "--check-layout" and not opts["check_layout"]:
            opts["check_layout"] = True
            index += 1
            continue
        key = _VALUE_OPTIONS.get(option)
        if key is None or opts[key] is not None:
            raise UsageError(f"unsupported or repeated option '{option}'\n{USAGE}")
        opts[key] = _take_value(argv, index, option)
        index += 2
    return opts


def _parse_shard(raw):
    """Two unsigned decimal positive integers i/n with 1 <= i <= n."""
    match = re.fullmatch(r"([0-9]+)/([0-9]+)", raw, re.ASCII)
    if match is None:
        raise UsageError(f"--shard must be i/n with unsigned decimal integers, got '{raw}'")
    index, count = int(match.group(1)), int(match.group(2))
    if not 1 <= index <= count:
        raise UsageError(f"--shard {raw}: need 1 <= i <= n")
    return index, count


def _parse(argv):
    """Return validated options or raise UsageError."""
    opts = _tokens(argv)
    if opts["manifest"] is not None and opts["shard"] is None:
        raise UsageError("--manifest requires --shard")
    if opts["check_layout"] and (opts["shard"] or opts["manifest"]):
        raise UsageError("--check-layout cannot be combined with --shard or --manifest")
    if opts["shard"] is not None:
        opts["shard"] = _parse_shard(opts["shard"])
    opts["kind"] = opts["kind"] or "all"
    return opts


def _manifest_target(raw):
    """Absolute manifest path, refused inside the watched bin tree."""
    if raw is None:
        return None
    target = os.path.realpath(os.path.abspath(raw))
    watched = os.path.realpath(os.path.join(ROOT, BIN_DIR))
    if target == watched or target.startswith(watched + os.sep):
        raise UsageError(f"--manifest {raw} is inside the watched bin tree {watched}")
    return target


def _positive(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value > 0)


def _load_weights(path):
    """Validated (default_seconds, weights) from the versioned duration document."""
    with open(path, encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict) or doc.get("schema") != 1:
        raise ValueError(f"{path}: expected an object with schema 1")
    if not all(isinstance(doc.get(k), str) for k in ("source_run_url", "source_commit")):
        raise ValueError(f"{path}: source_run_url and source_commit must be strings")
    weights = doc.get("weights")
    if not _positive(doc.get("default_seconds")) or not isinstance(weights, dict):
        raise ValueError(f"{path}: default_seconds must be positive and weights an object")
    if not all(isinstance(k, str) and _positive(v) for k, v in weights.items()):
        raise ValueError(f"{path}: every weight must be a positive finite number")
    return doc["default_seconds"], weights


def _partition(paths, default, weights, count):
    """Longest-processing-time: heaviest first (path tie break) onto the least loaded shard."""
    loads = [0.0] * count
    shards = [[] for _ in range(count)]
    for path in sorted(paths, key=lambda p: (-weights.get(p, default), p)):
        target = min(range(count), key=lambda k: (loads[k], k))
        loads[target] += weights.get(path, default)
        shards[target].append(path)
    return [sorted(shard) for shard in shards]


def _tested_commit():
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True, check=False)
    if proc.returncode != 0:
        raise UsageError(f"--manifest needs a git HEAD: {proc.stderr.strip()}")
    return proc.stdout.strip()


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
    except (LookupError, OSError, UnicodeError, ValueError):
        # FEAT-64: suite_layout's own typed shapes -- LookupError for its git probes, OSError
        # and UnicodeError for the tree walk, ValueError for malformed layout data. Anything
        # else is a defect in the checker and propagates as itself.
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


def _write_manifest(target, identity, chosen, completed, runner_exit):
    """Written only after every started script terminated and mutation checking finished."""
    if target is None:
        return
    doc = dict(identity, schema=1, selected_files=chosen, runner_exit=runner_exit,
               completed_files=[{"path": os.path.normpath(path).replace(os.sep, "/"),
                                 "returncode": rc} for path, rc in completed])
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target + ".tmp", "w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=2)
        handle.write("\n")
    os.replace(target + ".tmp", target)


def _run_shard(run_pool, opts, target, scripts):
    index, count = opts["shard"]
    identity = {"tested_commit": _tested_commit() if target else None,
                "kind": opts["kind"], "shard_index": index, "shard_count": count}
    try:
        default, weights = _load_weights(os.path.join(ROOT, DURATIONS))
    except (OSError, ValueError) as exc:
        print(f"run-unit-tests.py: unusable duration document: {exc}", file=sys.stderr)
        return 2
    chosen = _partition(scripts, default, weights, count)[index - 1]
    print(f"shard {index}/{count}: {len(chosen)} selected files")
    for path in chosen:
        print(f"selected {path}")
    completed = []
    runner_exit = run_pool.main([
        "--mutation-check", BIN_DIR, "--", *chosen], completed=completed) if chosen else 0
    _write_manifest(target, identity, chosen, completed, runner_exit)
    return runner_exit


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        opts = _parse(argv)
        target = _manifest_target(opts["manifest"])
    except UsageError as exc:
        print(f"run-unit-tests.py: {exc}", file=sys.stderr)
        return 2
    patterns = _patterns(opts["kind"])
    if patterns is None:
        print(
            f"run-unit-tests.py: unknown kind '{opts['kind']}' — use unit, integration or all",
            file=sys.stderr,
        )
        return 2

    os.chdir(ROOT)
    sys.path.insert(0, os.path.join(ROOT, BIN_DIR))
    import suite_layout
    import run_pool

    if not _validate_layout(suite_layout):
        return 2
    if opts["check_layout"]:
        return 0
    if opts["shard"] is None:
        return run_pool.main([
            "--mutation-check", BIN_DIR, "--", *_scripts(patterns)
        ])
    try:
        return _run_shard(run_pool, opts, target, _scripts(patterns))
    except UsageError as exc:
        print(f"run-unit-tests.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
