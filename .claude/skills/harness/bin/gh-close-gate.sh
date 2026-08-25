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
# IT TOKENIZES, IT DOES NOT GREP. An earlier cut matched the raw command string with
# `grep -E`, and a character class is not a shell lexer. Ten forms were measured reaching
# `gh issue close` straight through it: `gh "issue" close`, `/opt/homebrew/bin/gh issue
# close`, `\gh issue close`, `eval "..."`, `bash -c '...'`, `x=$(gh issue close 5)`,
# `$(echo gh) issue close`, `-f state="closed"`, a JSON body on `--input -`, and the
# GraphQL `closeIssue` mutation. `shlex` strips the quoting and the backslash, `basename`
# strips the path, and each token is re-scanned as a command line so `eval` and `bash -c`
# are read rather than skipped.
#
# WHAT IT STILL CANNOT SEE, stated rather than implied: a `gh` that only exists after
# shell expansion -- `G=gh; $G issue close 5`. Catching that needs the shell's own
# expansion, which a PreToolUse hook does not have and never will. So this gate is a
# guardrail against a close typed out of habit, NOT a security boundary; nothing here
# stops a determined evasion, and `curl` to the REST API would not even be a shell
# builtin away. What actually bounds the harness is structural: no harness command closes
# an issue except `abandon`.
#
# MATCHES ON THE COMMAND STRING ONLY. It never resolves the issue number, never calls gh,
# and never reads GitHub state, so it works offline and cannot fail open on a network error.
# The cost of that is real and accepted: this gate CANNOT TELL A TRACKED ISSUE FROM AN
# UNTRACKED ONE, so a legitimate close of an untracked issue is a false deny. A false deny
# is recoverable and a false allow is not, so where the two cannot be distinguished -- a
# close inside a quoted string, or an unparseable command line -- IT DENIES. The refusal
# text is what makes that acceptable: it names the route out.
#
# SELF-GATING, as branch-create-gate.sh is: github.sync off or absent exits 0 instantly, so
# this costs nothing where the mirror is off.
#
# ONE python3, not three. The config read, the command extract and the decision share a
# single interpreter start in gh-close-gate.py, because this hook runs ahead of EVERY Bash
# call in the session and three process spawns per call is a cost paid forever for nothing.
#
# THE DECISION LIVES IN A FILE, NOT A HEREDOC. A `python3 - <<'PY'` feeds the SCRIPT on
# stdin, which is the same stdin the hook's own JSON arrives on -- the reader would find it
# already consumed and every command would be allowed. `exec`ing a file keeps stdin the
# hook's, and replaces this shell rather than adding a process to it.
set -uo pipefail
root="${HARNESS_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"

exec python3 "$(dirname "$0")/gh-close-gate.py" "$root"
