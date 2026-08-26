#!/usr/bin/env python3
import json, os, re, shlex, sys

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

ROOT = sys.argv[1]
# ---- config gate: github.sync on -- else pass through instantly
try:
    g = json.load(open(os.path.join(ROOT, ".harness", "harness.json"))).get("github") or {}
except Exception:
    g = {}
if not g.get("sync"):
    sys.exit(0)

try:
    cmd = (json.load(sys.stdin).get("tool_input") or {}).get("command") or ""
except Exception:
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


def denies(line, depth=0):
    toks = words(line)
    if toks is None:
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
            or (RAW_API.search(line) and ISSUE_PATH.search(line) and RAW_STATE.search(line))
        )
    for i, t in enumerate(toks):
        if not is_gh(t):
            continue
        rest = toks[i + 1:]
        if len(rest) >= 2 and rest[0] == "issue" and rest[1] == "close":
            return True
        if rest and rest[0] == "api":
            joined = " ".join(rest)
            if "closeIssue" in joined:
                return True
            if ISSUE_PATH.search(joined):
                # state=closed in any argument order, quoting already stripped by shlex.
                if "state=closed" in joined:
                    return True
                # A mutating call on an issue whose body arrives on stdin (`--input -`) or
                # in a file carries no readable state, so the command string cannot prove
                # it is benign. Denied under the same bias: `gh issue edit` is the route
                # for a legitimate field change, and the refusal text names the way out.
                if "--input" in rest:
                    return True
                for j, a in enumerate(rest):
                    if a in ("-X", "--method") and j + 1 < len(rest) \
                            and rest[j + 1].upper() in MUTATES:
                        return True
    if depth < MAX_DEPTH:
        # `eval "gh issue close 5"` and `bash -c '...'` carry a whole command line inside
        # ONE token. Re-scan any token that still looks like a command line.
        for t in toks:
            if len(t.split()) >= 3 and denies(t, depth + 1):
                return True
    return False


if denies(cmd):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": REASON,
    }}))
sys.exit(0)
