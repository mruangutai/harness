#!/usr/bin/env bash
# PreToolUse Bash: refuse a hand-typed close of a GitHub issue (DEC-203 item 8).
#
# The harness closes tickets by landing their card at the board's done station, at
# `gh-sync.py ship`. GitHub's Auto-close issue workflow turns that write into a close.
# A close typed by hand bypasses the station, which produces the exact state this whole
# feature exists to prevent: an issue CLOSED with its card NOT at Done.
#
# NO ENVIRONMENT MARKER, and the reason is a measurement rather than a preference. Issue
# #842 specified a marker `gh-sync.py` would set to exempt `abandon`'s own close. It cannot
# work and is not needed: a PreToolUse hook is handed only `tool_input.command`
# (branch-create-gate.sh:47), and `gh-sync.py` reaches `gh` through `subprocess.run`, which
# never traverses the Bash tool. So `abandon`'s close is never presented to this gate at
# all. A marker would only ever be settable BY HAND -- which is precisely the hole the
# grilling flagged. What actually stops a harness command from closing an issue is deleting
# it: T-11 removes `close-task`, leaving `abandon` as the only one.
#
# MATCHES ON THE COMMAND STRING ONLY. It never resolves the issue number, never calls gh,
# and never reads GitHub state, so it works offline and cannot fail open on a network error.
# The cost of that is real and accepted: this gate CANNOT TELL A TRACKED ISSUE FROM AN
# UNTRACKED ONE, so a legitimate close of an untracked issue is a false deny. A false deny
# is recoverable and a false allow is not, so where the two cannot be distinguished --
# including a `gh issue close` that appears only inside a quoted string -- IT DENIES. The
# refusal text is what makes that acceptable: it names the route out.
#
# SELF-GATING, as branch-create-gate.sh is: github.sync off or absent exits 0 instantly, so
# this costs nothing where the mirror is off.
set -uo pipefail
root="${HARNESS_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"

input=$(cat)

# ---- config gate: github.sync on -- else pass through instantly
SYNC="$(python3 - "$root" <<'PY'
import json, os, sys
try:
    g = json.load(open(os.path.join(sys.argv[1], ".harness", "harness.json"))).get("github") or {}
except Exception:
    g = {}
print(str(bool(g.get("sync"))).lower())
PY
)"
[ "$SYNC" = "true" ] || exit 0

cmd=$(printf '%s' "$input" | python3 -c 'import sys,json; print((json.load(sys.stdin).get("tool_input") or {}).get("command") or "")')

# ONE refusal text, used verbatim for BOTH denials. A second wording would drift, and the
# operator would learn two different answers to one question.
read -r -d '' REASON <<'MSG'
Refused: the harness closes tickets by landing their card at Done, never by closing an issue.
If the work is finished, do nothing here — gh-sync.py ship writes Done at the merge and GitHub
closes the issue. If it is being dropped, run:
  python3 .claude/skills/harness/bin/gh-sync.py abandon <feature-dir> --reason-file <path> --yes
If the issue is not tracked by the harness at all, close it in the GitHub web UI; this gate
cannot tell tracked from untracked, by design.
MSG

deny() {
  python3 -c 'import sys,json; print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":sys.argv[1]}}))' "$1"
  exit 0
}

# THERE IS DELIBERATELY NO gh-sync.py EXEMPTION CLAUSE. An earlier cut of this gate exited 0
# early on any command line mentioning gh-sync.py, to keep the sanctioned route from being
# caught. It bought nothing -- neither pattern below can match `gh-sync.py`, because both
# anchor on a `gh` invocation followed by `issue` or `api` -- and it opened a hole: a compound
# command like `gh issue close 1 && gh-sync.py ship` would have been waved through by the
# exemption before either pattern was ever tested.

# `gh issue close` in any position: after a leading env assignment, a cd, a pipe, a
# semicolon, or an && -- the anchor is the gh invocation itself, not the start of the line.
if printf '%s' "$cmd" | grep -qE '(^|[;&|]|[[:space:]])gh[[:space:]]+issue[[:space:]]+close([[:space:]]|$)'; then
  deny "$REASON"
fi

# `gh api ... repos/<owner>/<name>/issues/<n> ... state=closed`, IN ANY ARGUMENT ORDER --
# so the two halves are tested separately rather than as one ordered pattern.
if printf '%s' "$cmd" | grep -qE '(^|[;&|]|[[:space:]])gh[[:space:]]+api([[:space:]]|$)' \
   && printf '%s' "$cmd" | grep -qE 'repos/[^/[:space:]]+/[^/[:space:]]+/issues/[0-9]+' \
   && printf '%s' "$cmd" | grep -qE 'state=closed'; then
  deny "$REASON"
fi

exit 0
