#!/usr/bin/env python3
"""Refuse captured artifacts containing credentials or absolute home paths.

Every forbidden-pattern absence check first proves its own positive control, so
an invalid detector fails closed rather than reporting a false-clean fixture
(DEC-169, issue #981).

WAS A .sh ENTRY POINT (issue #1674). The native implementation retains the
shell command's argv, exit codes, diagnostics, byte-oriented matching, and
positive-control behavior.
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

import os
import re
import sys

USAGE = "usage: check-fixture-secrets.py <file> [<file> ...]"
SECRET_PATTERN_TEXT = r'credential_pin|-----BEGIN|AKIA[0-9A-Z]{16}|(^|[^A-Za-z0-9])sk-ant-|(^|[^A-Za-z0-9])sk-[A-Za-z0-9-]{16,}|(ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}'
HOME_PATH_PATTERN_TEXT = r'/Users/[^/\s"\']+/|/home/[^/\s"\']+/'
SECRET_PATTERN = re.compile(SECRET_PATTERN_TEXT.encode())
HOME_PATH_PATTERN = re.compile(HOME_PATH_PATTERN_TEXT.encode())


def _control_cases():
    guidance = "The sweep cannot be trusted; fix the pattern before checking any file with it."
    return (
        ("sk-ant- key", SECRET_PATTERN,
         "sk-ant-api03-THIS-IS-A-SYNTHETIC-CONTROL-VALUE-NOT-A-REAL-KEY", guidance),
        ("hyphenated sk- key", SECRET_PATTERN,
         "sk-proj-AbCdEfGh-1234-5678-XyZ9", guidance),
        ("AWS access key id", SECRET_PATTERN, "AKIA" + "A" * 16,
         "The AWS branch cannot be trusted; fix the pattern before checking any file with it."),
        ("PEM private key header", SECRET_PATTERN, "-----BEGIN PRIVATE KEY-----",
         "The PEM branch cannot be trusted; fix the pattern before checking any file with it."),
        ("GitHub token", SECRET_PATTERN, "ghp_ABCDEFGH12345678",
         "The GitHub-token branch cannot be trusted; fix the pattern before checking any file with it."),
        ("credential_pin literal", SECRET_PATTERN, "credential_pin=xyz",
         "The credential_pin branch cannot be trusted; fix the pattern before checking any file with it."),
        ("home-directory", HOME_PATH_PATTERN,
         "/Users/example-synthetic-control-user/scratch.txt",
         "The identity check cannot be trusted; fix the pattern before checking any file with it."),
    )


def _check_controls():
    failed = False
    for label, pattern, value, guidance in _control_cases():
        if pattern.search(value.encode()):
            continue
        print(
            f"check-fixture-secrets: POSITIVE CONTROL FAILED — the {label} pattern does not",
            file=sys.stderr)
        print(
            f"  match its own synthetic control value ({value}). {guidance}",
            file=sys.stderr)
        failed = True
    return not failed


def _read_file(path):
    if not os.access(path, os.R_OK):
        return None
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except OSError:
        return None


def _check_file(path):
    content = _read_file(path)
    if content is None:
        print(
            f"check-fixture-secrets: BLOCKED — {path} is not a readable file.",
            file=sys.stderr)
        return 1
    failures = 0
    if SECRET_PATTERN.search(content):
        print(
            f"check-fixture-secrets: BLOCKED — {path} matches the secret pattern. Do not",
            file=sys.stderr)
        print(
            "  commit it. Re-scrub or regenerate the fixture from a clean capture.",
            file=sys.stderr)
        failures += 1
    if HOME_PATH_PATTERN.search(content):
        print(
            f"check-fixture-secrets: BLOCKED — {path} contains an absolute home-directory",
            file=sys.stderr)
        print(
            "  path (/Users/<name>/... or /home/<name>/...). Redact it before committing.",
            file=sys.stderr)
        failures += 1
    return failures


def main(argv=None):
    paths = sys.argv[1:] if argv is None else argv
    if not paths:
        print(USAGE, file=sys.stderr)
        return 2
    if not _check_controls():
        return 2
    failures = sum(_check_file(path) for path in paths)
    if failures:
        return 1
    print(
        f"check-fixture-secrets: clean — {len(paths)} file(s) checked, all positive controls fired.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
