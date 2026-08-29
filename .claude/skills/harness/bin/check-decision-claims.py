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

A line that starts `<!-- claim:` but does not fully match the marker grammar — a
single `:` where `::` belongs, trailing text after `-->`, anything a human or
agent MEANT as a marker but mistyped — is a reported FAILURE, never a silent skip.
Treating a lookalike as "no marker here" is the exact fail-open this checker exists
to prevent applied to itself.

THE SAFETY BOUNDARY. The command is split with shlex.split and run with
subprocess.run as an argv list, never through a shell. A command is refused —
reported and counted as a failure, never silently skipped — unless it clears ALL
of:

  1. its first token is exactly `git` or `grep` (an allowlist, not a blacklist);
  2. for `git`, no token before the subcommand starts with `-` — this is what
     kills `-c`, `-C`, `--config-env`, `--exec-path`, `--git-dir`, `--work-tree`,
     and every other config/repo-redirecting global option in one rule, rather
     than chasing individual dangerous config KEYS (`core.fsmonitor`,
     `diff.external`, `alias.*`, ...) one at a time forever;
  3. the git subcommand itself is in a fixed read-only allowlist (`grep`, `log`,
     `show`, `ls-files`, `rev-parse`, `cat-file`, `diff`) — nothing that writes,
     nothing that spawns a process by name;
  4. no token anywhere in a git command is `-O`/`--open-files-in-pager` (or its
     bundled/`=value` forms) — `git grep -O<cmd>` runs `<cmd>` directly, entirely
     apart from `-c`, so rule 2 alone does not cover it;
  5. every subprocess this checker launches runs with `GIT_CONFIG_GLOBAL`,
     `GIT_CONFIG_SYSTEM` set to `/dev/null` and `GIT_CONFIG_NOSYSTEM=1`, so a
     hostile alias or command sitting in a developer's or a CI runner's own
     ambient git config is unreachable even though it was never named in a
     command string at all;
  6. for `grep`, no argument reads from a file or a device instead of argv/stdin
     — `-f`/`--file`, `-d`/`--devices` (and their `=value` forms), including
     bundled into a short-option cluster such as `-rf`.

Each command gets a 10-second timeout; a timeout counts as a failure. A
documentation file must not become an arbitrary code execution surface — not via
a subcommand, not via a global option, not via ambient config it never mentions.

Usage:
    check-decision-claims.py            check .harness/harness/docs/DECISIONS.md,
                                         resolved the same way gen-decisions-index.py
                                         resolves its default target
    check-decision-claims.py --file P   check P instead

Exit codes: 0 only when every marker ran and passed (including the zero-marker
case). 1 when any claim failed, was refused, or was a malformed marker lookalike.
2 for a usage error or an unreadable target. The count of markers examined is
always printed on success, so a zero-marker run is visibly distinct from one that
actually exercised something.
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

# Deliberately looser than CLAIM_RE: anything a human or agent MEANT as a claim
# marker. A line that looks like a marker but does not parse as one is an error,
# never a non-marker — mirrors gen-decisions-index.py's ROW_LOOKALIKE_RE /
# MalformedRow shape exactly (see extract_claims).
CLAIM_LOOKALIKE_RE = re.compile(r"^\s*<!--\s*claim:")

ALLOWED_FIRST_TOKENS = {"git", "grep"}

# Read-only git subcommands the live claim markers actually need (rule 3). Anything
# else — a write, or a subcommand this checker has never seen — is refused rather
# than allowed by default.
ALLOWED_GIT_SUBCOMMANDS = {
    "grep", "log", "show", "ls-files", "rev-parse", "cat-file", "diff",
}

# git's pager-launching option (rule 4): long form, with or without `=<pager>`.
_GIT_OPEN_PAGER_LONG = {"--open-files-in-pager"}

# grep options that read from an argument file or a device rather than argv/stdin
# (rule 6): long form, with or without `=<path>`.
_GREP_FILE_OR_DEVICE_LONG = {"--file", "--devices"}
_GREP_FILE_OR_DEVICE_LETTERS = {"f", "d"}

TIMEOUT_SECONDS = 10


class MalformedClaim(Exception):
    """A line means to be a claim marker but does not parse as one."""

    def __init__(self, lines):
        self.lines = lines
        super().__init__(f"{len(lines)} malformed claim marker(s)")


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

    Raises MalformedClaim rather than silently skipping a line that starts
    `<!-- claim:` but does not fully match CLAIM_RE — a single `:` where `::`
    belongs, or trailing text after `-->`. Treating that as "no marker here" is
    the same fail-open shape ROW_LOOKALIKE_RE guards against in
    gen-decisions-index.py: never a skip, a reported failure.
    """
    claims = []
    malformed = []
    current_heading = None
    for lineno, line in enumerate(text.splitlines(), 1):
        h = HEADING_RE.match(line)
        if h:
            current_heading = h.group(1)
            continue
        m = CLAIM_RE.match(line)
        if m:
            claims.append((current_heading, m.group(1), m.group(2)))
        elif CLAIM_LOOKALIKE_RE.match(line):
            malformed.append((lineno, line))
    if malformed:
        raise MalformedClaim(malformed)
    return claims


def _git_open_pager_option(tok):
    """True if `tok` is git's -O/--open-files-in-pager in any form (rule 4):
    bare, bundled with a pager name, or the long `--open-files-in-pager[=pager]`
    spelling. This is an option-POSITION rule — it fires wherever the token
    appears after the subcommand — not a config-key blacklist."""
    if tok in _GIT_OPEN_PAGER_LONG:
        return True
    if any(tok.startswith(f"{o}=") for o in _GIT_OPEN_PAGER_LONG):
        return True
    if tok.startswith("--"):
        return False
    # Short form: "-O", "-Ovim", or "O" bundled among other short flags.
    return tok.startswith("-") and "O" in tok[1:]


def _refusal_reason_git(tokens):
    rest = tokens[1:]
    if not rest:
        return "REFUSED: no git subcommand given"
    if rest[0].startswith("-"):
        # Rule 2: ANY option before the subcommand is refused outright. This one
        # rule kills -c, -C, --config-env, --exec-path, --git-dir, --work-tree at
        # once; a blacklist of the config KEYS reachable through -c specifically
        # (core.fsmonitor, diff.external, alias.*, ...) is not — the next git
        # release can always add another.
        return (
            f"REFUSED: git option {rest[0]!r} before the subcommand is not "
            "allowed — only a bare subcommand may follow `git`"
        )
    subcommand = rest[0]
    if subcommand not in ALLOWED_GIT_SUBCOMMANDS:
        return (
            f"REFUSED: git subcommand {subcommand!r} is not in the read-only "
            f"allowlist ({', '.join(sorted(ALLOWED_GIT_SUBCOMMANDS))})"
        )
    for tok in rest[1:]:
        if _git_open_pager_option(tok):
            return (
                f"REFUSED: git option {tok!r} opens a pager/program directly "
                "(-O/--open-files-in-pager) and is never allowed"
            )
    return None


def _grep_file_or_device_option(tok):
    """True if `tok` reads from an argument file or a device (rule 6): long
    form with or without `=path`, or bundled into any short-option cluster whose
    letters include f or d (e.g. `-rf`)."""
    if tok in _GREP_FILE_OR_DEVICE_LONG:
        return True
    if any(tok.startswith(f"{o}=") for o in _GREP_FILE_OR_DEVICE_LONG):
        return True
    if tok.startswith("--") or not tok.startswith("-") or len(tok) < 2:
        return False
    return bool(set(tok[1:]) & _GREP_FILE_OR_DEVICE_LETTERS)


def _refusal_reason_grep(tokens):
    for tok in tokens[1:]:
        if _grep_file_or_device_option(tok):
            return (
                f"REFUSED: grep option {tok!r} reads from an argument file or a "
                "device instead of argv/stdin and is never allowed"
            )
    return None


def refusal_reason(tokens):
    """None if `tokens` (already shlex-split) is safe to run, else a reason
    string naming which rule refused it.

    Pure and subprocess-free by design: every rule bounds a token POSITION or
    SHAPE (first token, pre-subcommand options, the subcommand itself, an
    execution-primitive option) rather than a blacklist of dangerous config
    KEYS or pager names — a blacklist loses the race against the next git
    release by construction; a position/shape rule does not.
    """
    if not tokens:
        return "empty command"
    first = tokens[0]
    if first not in ALLOWED_FIRST_TOKENS:
        return (
            f"REFUSED: first token {first!r} is not git or grep — a decisions "
            "document must not become an arbitrary code execution surface"
        )
    if first == "git":
        return _refusal_reason_git(tokens)
    return _refusal_reason_grep(tokens)


def _subprocess_env():
    """Base environment for every command this checker runs, with git's ambient
    config sources neutralized (rule 5): a hostile alias or command sitting in a
    developer's or a CI runner's own ~/.gitconfig or /etc/gitconfig must not be
    reachable via a claim command, even though it is never named in the command
    string at all. Derived from os.environ, never wiped wholesale, so PATH and
    everything else a subprocess needs stays intact.
    """
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def run_claim(command):
    """Run `command` (already validated) and return (ok, output_or_reason).

    `ok` is False for a nonzero exit, a timeout, a refusal, or an OS-level
    failure to launch — none of those are treated as a skip; each is a failure
    the caller reports. The ONE subprocess.run call site in this module; rule
    5's neutralized environment is applied here and nowhere else.
    """
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        return False, f"could not parse command: {exc}"
    reason = refusal_reason(tokens)
    if reason is not None:
        return False, reason
    try:
        result = subprocess.run(
            tokens,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            env=_subprocess_env(),
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

    try:
        claims = extract_claims(text)
    except MalformedClaim as exc:
        for lineno, line in exc.lines:
            print(
                f"{target}:{lineno}: malformed claim marker (does not match "
                f"'<!-- claim: <command> :: <expected> -->'): {line}"
            )
        print(f"examined 0 claim(s), {len(exc.lines)} failed")
        sys.exit(1)

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
