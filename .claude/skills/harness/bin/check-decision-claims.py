#!/usr/bin/env python3
"""Executable-claims checker for .harness/harness/docs/DECISIONS.md.

A CLAIM MARKER is an HTML comment on its own line inside a decision body:

    <!-- claim: git grep -c "budget is 80" .claude/skills/harness/bin/check-domain.sh :: 1 -->

Everything between "claim:" and the " :: " separator is the COMMAND. Everything
after it is the expected stdout SUBSTRING, stripped of surrounding whitespace. This
checker runs the command and asserts the substring appears in its stdout — a
decision that STATES a fact a command can check gets that fact re-verified on every
run, instead of aging silently the way `## DEC-N` prose already does (that is what
the anchor checker's docstring calls "this tool's job").

THE SAFETY BOUNDARY. The command is split with shlex.split and run with
subprocess.run as an argv list, never through a shell. Any command whose first
token is not exactly
`git` or `grep` is REFUSED — reported and counted as a failure, never silently
skipped, because a skip that looks like a pass is the same hole as no check at all.
A documentation file must not become an arbitrary code execution surface. Each
command gets a 10-second timeout; a timeout counts as a failure.

Usage:
    check-decision-claims.py            check .harness/harness/docs/DECISIONS.md,
                                         resolved the same way gen-decisions-index.py
                                         resolves its default target
    check-decision-claims.py --file P   check P instead

Exit codes: 0 only when every marker ran and passed (including the zero-marker
case). 1 when any claim failed or was refused. 2 for a usage error or an unreadable
target. The count of markers examined is always printed on success, so a zero-marker
run is visibly distinct from one that actually exercised something.
"""
import argparse
import os
import re
import shlex
import subprocess
import sys

import harness_boundary

_BIN_DIR = os.path.dirname(os.path.abspath(__file__))

# Mirrors gen-decisions-index.py's own DOCS_DIR/DECISIONS_PATH constants exactly —
# the default target is the same file, resolved the same way, never a second guess.
DOCS_DIR = os.path.join(".harness", "harness", "docs")
DECISIONS_REL_PATH = os.path.join(DOCS_DIR, "DECISIONS.md")

HEADING_RE = re.compile(r"^##\s+(DEC-\d+.*)$")

# `<!-- claim: <command> :: <expected substring> -->` on its own line. The command
# and the expected substring are separated by " :: " with a single space on each
# side, matching the row grammar's own separator convention.
CLAIM_RE = re.compile(r"^<!--\s*claim:\s*(.*?)\s*::\s*(.*?)\s*-->\s*$")

ALLOWED_FIRST_TOKENS = {"git", "grep"}

TIMEOUT_SECONDS = 10


def default_target():
    """The default --file value, resolved at CALL time (never at import time) so
    a caller that hasn't chdir'd yet still gets the right answer."""
    project_dir = harness_boundary.resolve_root(_BIN_DIR)
    return os.path.join(project_dir, DECISIONS_REL_PATH)


def extract_claims(text):
    """[(heading, command, expected), ...] in document order.

    `heading` is the text of the nearest preceding `## DEC-N ...` line, or None if
    a marker appears before any heading — which should not happen in a well-formed
    document but must still be reported rather than crash.
    """
    claims = []
    current_heading = None
    for line in text.splitlines():
        h = HEADING_RE.match(line)
        if h:
            current_heading = h.group(1)
            continue
        m = CLAIM_RE.match(line)
        if m:
            claims.append((current_heading, m.group(1), m.group(2)))
    return claims


def run_claim(command):
    """Run `command` (already validated) and return (ok, output_or_reason).

    `ok` is False for a nonzero exit, a timeout, or an OS-level failure to launch
    — none of those are treated as a skip; each is a failure the caller reports.
    """
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        return False, f"could not parse command: {exc}"
    if not tokens:
        return False, "empty command"
    if tokens[0] not in ALLOWED_FIRST_TOKENS:
        return False, (
            f"REFUSED: first token {tokens[0]!r} is not git or grep — a decisions "
            "document must not become an arbitrary code execution surface"
        )
    try:
        result = subprocess.run(
            tokens, capture_output=True, text=True, timeout=TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired:
        return False, f"timed out after {TIMEOUT_SECONDS}s"
    except OSError as exc:
        return False, f"could not run: {exc}"
    return True, result.stdout


def check_claim(heading, command, expected):
    """None if the claim's expected substring is present in the command's stdout,
    else a short reason string. `heading` is unused for the check itself but is
    threaded through by the caller for reporting."""
    ok, output = run_claim(command)
    if not ok:
        return output
    if expected not in output:
        return f"expected substring {expected!r} not found in stdout: {output!r}"
    return None


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="check-decision-claims.py",
        description="Run every executable claim marker in a decisions document "
        "and assert its expected stdout substring appears.",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="document to check (default: .harness/harness/docs/DECISIONS.md, "
        "resolved via harness_boundary)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.file is not None:
        target = args.file
    else:
        try:
            target = default_target()
        except ValueError as exc:
            print(f"check-decision-claims: {exc}", file=sys.stderr)
            sys.exit(2)

    try:
        with open(target, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print(f"check-decision-claims: cannot read {target!r}: {exc}", file=sys.stderr)
        sys.exit(2)

    claims = extract_claims(text)

    failed = 0
    for heading, command, expected in claims:
        heading_label = heading if heading is not None else "(no preceding DEC heading)"
        reason = check_claim(heading, command, expected)
        if reason is not None:
            print(f"{heading_label}: `{command}` :: {expected!r}: {reason}")
            failed += 1

    print(f"examined {len(claims)} claim(s), {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
