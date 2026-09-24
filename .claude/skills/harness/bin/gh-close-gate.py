#!/usr/bin/env python3
"""PreToolUse guard against hand-typed GitHub issue closure.

Registered in `.omp/extensions/harness-hooks.ts`.

WAS A .sh WRAPPER (issue #1674). This native entry point preserves the wrapper's
isolated root resolution, refusal behavior and hook stream contracts while
removing its extra interpreter launch.
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
# branch-create-gate.py, merge-gate.py, plan-sign-gate.py, run-unit-tests.py: it runs BEFORE the
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
        f"gh-close-gate.py: no harness root could be resolved from "
        f"{_bootstrap_bin} — refusing to run",
        file=_bootstrap_sys.stderr,
    )
    raise SystemExit(2)
import artifact_accessors as _artifact_accessors
_bootstrap_sys.path[:] = _bootstrap_original_path

import json
import os
import re
import shlex
import sys

# ONE refusal text, used verbatim for EVERY denial. A second wording would drift, and the
# operator would learn two different answers to one question.
REASON = (
    "Refused: the harness closes tickets by landing their card at Done, never by closing an issue.\n"
    "If the work is finished, do nothing here \u2014 gh-sync.py ship writes Done at the merge and GitHub\n"
    "closes the issue. If it is being dropped, run:\n"
    "  python3 .claude/skills/harness/bin/gh-sync.py abandon <feature-dir> --reason-file <path> --yes\n"
    "If the issue is not tracked by the harness at all, close it in the GitHub web UI; this gate\n"
    "cannot tell tracked from untracked, by design."
)

# ---- config gate: github.sync on -- else pass through instantly
try:
    config_path = os.path.join(ROOT, ".harness", "harness.json")
    g = _artifact_accessors.load_harness_json(config_path).get("github") or {}
except _artifact_accessors.ArtifactAccessError:
    g = {}
if not g.get("sync"):
    sys.exit(0)

try:
    payload = _artifact_accessors.read_hook_payload(
        sys.stdin.read(), "gh-close-gate hook payload")
    cmd = (payload.get("tool_input") or {}).get("command") or ""
except _artifact_accessors.ArtifactAccessError:
    sys.exit(0)

# Shell operators shlex hands back as their own tokens. They are separators, never words.
OPS = {";", "&", "&&", "|", "||", "(", ")", "<", ">", ">>", "\n"}
ISSUE_PATH = re.compile(r"repos/[^/\s]+/[^/\s]+/issues/\d+")
MUTATES = {"PATCH", "POST", "PUT", "DELETE"}
MAX_DEPTH = 3

# The TEXT fallback, for a command line `shlex` cannot lex at all. It is the pre-tokenizer
# match, kept for exactly this case: it reads the raw string, so an unbalanced quote does not
# stop it. Weaker than tokenizing -- it cannot see through quoting or a path -- but it is only
# ever reached when tokenizing is impossible, and something is far better than nothing.
RAW_CLOSE = re.compile(r"(^|[;&|(]|\s)gh\s+issue\s+close(\s|$)")
RAW_API = re.compile(r"(^|[;&|(]|\s)gh\s+api(\s|$)")
RAW_STATE = re.compile(r"state=[\"']?closed")


def words(s):
    """Token list with quoting resolved, or None when the line will not lex."""
    try:
        lex = shlex.shlex(s, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        return [t for t in lex if t not in OPS]
    except ValueError:
        return None


def is_gh(tok):
    """`gh`, `/opt/homebrew/bin/gh`, `\\gh`, `$(... gh` -- all the same binary."""
    return os.path.basename(tok.strip("\\'\"$()`")) == "gh"


def _raw_denial(line):
    """Apply the bounded text fallback when a command cannot be tokenized."""
    # UNPARSEABLE FALLS BACK TO A TEXT SCAN, IT DOES NOT BLANKET-DENY. An earlier cut
    # returned True here on the reasoning that unparseable is indistinguishable from
    # evasive. That was wrong by a wide margin, and it was measured: `shlex` raises on
    # ANY unbalanced quote, and an apostrophe inside a heredoc or an English contraction
    # is an unbalanced quote. `echo it's fine` did not lex, so the gate refused it. So
    # did every `gh issue comment --body-file` whose heredoc contained the word "does
    # not" in the possessive. The rule refused ordinary work all day and caught nothing,
    # because a real evasion does not need an unbalanced quote to hide behind.
    #
    # A false deny is recoverable and a false allow is not -- but that trade only holds
    # where the two are genuinely indistinguishable. Here they are not: an unlexable line
    # can still be READ as text, so it gets the weaker check rather than a refusal.
    return bool(
        RAW_CLOSE.search(line)
        or (RAW_API.search(line) and ISSUE_PATH.search(line)
            and RAW_STATE.search(line))
    )


def _method_mutates(rest):
    """Return whether a gh api method option names a mutating request."""
    return any(
        argument in ("-X", "--method")
        and index + 1 < len(rest)
        and rest[index + 1].upper() in MUTATES
        for index, argument in enumerate(rest)
    )


def _api_denial(rest):
    """Recognize issue-closing forms beneath `gh api`."""
    joined = " ".join(rest)
    if "closeIssue" in joined:
        return True
    if not ISSUE_PATH.search(joined):
        return False
    # state=closed in any argument order, quoting already stripped by shlex.
    if "state=closed" in joined:
        return True
    # A mutating call on an issue whose body arrives on stdin (`--input -`) or
    # in a file carries no readable state, so the command string cannot prove
    # it is benign. Denied under the same bias: `gh issue edit` is the route
    # for a legitimate field change, and the refusal text names the way out.
    return "--input" in rest or _method_mutates(rest)


def _gh_denial(rest):
    """Recognize a closing subcommand after the gh executable token."""
    if len(rest) >= 2 and rest[0] == "issue" and rest[1] == "close":
        return True
    return bool(rest and rest[0] == "api" and _api_denial(rest))


def _direct_denial(tokens):
    """Recognize a direct `gh` close anywhere in a compound command."""
    for index, token in enumerate(tokens):
        if is_gh(token) and _gh_denial(tokens[index + 1:]):
            return True
    return False


def _nested_denial(tokens, depth):
    """Re-scan tokens that carry a nested shell command."""
    if depth >= MAX_DEPTH:
        return False
    # `eval "gh issue close 5"` and `bash -c '...'` carry a whole command line inside
    # ONE token. Re-scan any token that still looks like a command line.
    return any(
        len(token.split()) >= 3 and denies(token, depth + 1)
        for token in tokens
    )


def denies(line, depth=0):
    tokens = words(line)
    if tokens is None:
        return _raw_denial(line)
    return _direct_denial(tokens) or _nested_denial(tokens, depth)


if denies(cmd):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": REASON,
    }}))
sys.exit(0)
