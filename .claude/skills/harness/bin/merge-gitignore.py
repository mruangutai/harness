#!/usr/bin/env python3
"""Append Harness's canonical ignore rules without overwriting project rules.

The command is deliberately idempotent. ``--check`` reports every absent rule
without modifying the target; normal mode appends only missing rules under a
marker block (DEC-112).

WAS A .sh ENTRY POINT (issue #1674). The native implementation retains the
shell command's argv, byte-preservation, diagnostics, and even its historical
success-diagnostic glob expansion so the cutover is behavior-neutral.
"""
import os as _bootstrap_os
import site as _bootstrap_site
import sys as _bootstrap_sys

_bootstrap_bin = _bootstrap_os.path.dirname(
    _bootstrap_os.path.abspath(__file__))
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

import glob
import os
import sys

USAGE = "usage: merge-gitignore.py <project-root> [--check]"
HEADER = (
    "# --- harness ---\n"
    "# Run dirs are ephemeral; a dirty tree halts a team with BLOCKED, so these\n"
    "# must be ignored or the harness deadlocks itself. Everything else under\n"
    "# .harness/ is committed on purpose — it is the record of what shipped.\n"
).encode("utf-8")
FOOTER = b"# --- end harness ---\n"


def _snippet_path():
    return os.path.join(_bootstrap_bin, "..", "templates", "gitignore.snippet")


def _rules(snippet):
    with open(snippet, "rb") as handle:
        lines = handle.read().split(b"\n")
    return [
        line for line in lines
        if line.strip() and not line.lstrip().startswith(b"#")
    ]


def _target_lines(target):
    if not os.path.isfile(target):
        return set()
    with open(target, "rb") as handle:
        return set(handle.read().split(b"\n"))


def _missing_rules(target, rules):
    present = _target_lines(target)
    return [rule for rule in rules if rule not in present]


def _append_rules(target, missing):
    separator = b"\n" if os.path.isfile(target) and os.path.getsize(target) else b""
    block = separator + HEADER + b"".join(rule + b"\n" for rule in missing) + FOOTER
    with open(target, "ab") as handle:
        handle.write(block)


def _success_words(missing):
    words = b"\n".join(missing).decode("utf-8").split()
    expanded = []
    for word in words:
        matches = glob.glob(word)
        expanded.extend(sorted(matches) if matches else [word])
    return expanded


def _report_missing(target, missing):
    print(f"merge-gitignore: MISSING from {target}:", file=sys.stderr)
    for rule in missing:
        print(f"  - {rule.decode('utf-8')}", file=sys.stderr)


def _report_appended(target, missing):
    print(f"merge-gitignore: appended to {target}")
    for word in _success_words(missing):
        print(f"  + {word}")


def _merge(root_arg, mode):
    root = os.path.abspath(root_arg)
    snippet = _snippet_path()
    if not os.access(snippet, os.R_OK):
        print(f"merge-gitignore: no snippet at {snippet}", file=sys.stderr)
        return 1
    target = os.path.join(root, ".gitignore")
    missing = _missing_rules(target, _rules(snippet))
    if not missing:
        print(f"merge-gitignore: all harness rules already present in {target}")
        return 0
    if mode == "--check":
        _report_missing(target, missing)
        return 1
    _append_rules(target, missing)
    _report_appended(target, missing)
    return 0


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    root_arg = args[0] if args else ""
    mode = args[1] if len(args) > 1 else ""
    if not root_arg or not os.path.isdir(root_arg):
        print(USAGE, file=sys.stderr)
        return 1
    return _merge(root_arg, mode)


if __name__ == "__main__":
    raise SystemExit(main())
