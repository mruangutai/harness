#!/usr/bin/env bash
# PreToolUse Bash gate for plan-merge.py and quarantine.py.
#
# It carries two rules: DEC-120 unconditionally refuses an agent's `sign-approval`,
# while FEAT-51 quarantines a governed orphan writer's canonical plan mutations and
# adoption attempts.
#
# DEC-120: the approval signature is the USER'S, and it is relayed by the main session alone.
# An agent may ask for a signature and be refused; it cannot write one. Until this gate that
# rule was prose — `sign-approval` takes the lock and writes the block for whoever calls it,
# so an agent that judged the plan finished could sign it and nothing in the tree would notice.
#
# The signature rule refuses one verb, not the tool. The FEAT-51 rule covers the other
# mutating plan verbs only when the governed writer has become an orphan.
#
# NOT SELF-GATING, unlike gh-close-gate.sh and branch-create-gate.sh, and the difference is
# not an oversight. Those two gate on `github.sync` because the behaviour they protect only
# exists where the mirror is on. A signature is the user's word about their own plan; it has
# no GitHub dimension and no configuration that could make signing by an agent acceptable.
# So this gate is unconditional, and the config read those two perform is absent here.
#
# IT TOKENIZES, IT DOES NOT GREP, for the reason gh-close-gate.sh's own comment records as a
# measurement: a character class is not a shell lexer, and ten forms were measured reaching
# `gh issue close` straight through a `grep -E`. `shlex` strips the quoting and the backslash,
# `basename` strips the path, and every token is re-scanned as a command line so `eval` and
# `bash -c` are read rather than skipped.
#
# WHAT IT STILL CANNOT SEE, stated rather than implied: a tool name produced only by shell
# expansion — `P=plan-merge.py; python3 $P sign-approval`. Catching that needs the shell's own
# expansion, which a PreToolUse hook is never given; it receives `tool_input.command` as text.
# So this is a guardrail against a signature written out of over-eagerness, NOT a security
# boundary. What actually bounds the harness is that ONE verb writes the block, and this gate
# makes reaching it from an agent an explicit act of evasion rather than an ordinary call.
#
# THE MAIN SESSION IS EXEMPT BY THE MECHANISM. An absent or empty `agent_type` IS the main
# session, which is how check-domain.sh's approval_guard already reads the same payload; a
# named main-session branch would be a second carve-out to keep in sync, and issue #132
# records what happened the last time that file grew one.
#
# ONE python3, not two: the payload read and the decision share a single interpreter start,
# because this hook runs ahead of EVERY Bash call in the session.
#
# THE DECISION LIVES IN A FILE, NOT A HEREDOC. A `python3 - <<'PY'` feeds the SCRIPT on
# stdin — the same stdin the hook's own JSON arrives on — so the reader would find it already
# consumed and every command would be allowed. `exec`ing a file keeps stdin the hook's, and
# replaces this shell rather than adding a process to it.
set -uo pipefail
# THE ROOT COMES FROM harness_boundary, reached through this script's own directory, never
# from the environment and never from the caller's cwd (FEAT-42 T-15). This gate has no target
# path of its own — it reads tool_input.command — so the correct input is this script's own
# location, which is what resolve_root takes. The root is used for ONE thing: resolving the
# absolute path this gate's refusal tells the reader to run.
#
# REFUSING IS THE POINT — exit 2, never a fallback.
_selfbin="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
root="$(python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import harness_boundary; print(harness_boundary.resolve_root(sys.argv[1]))' "$_selfbin" 2>/dev/null)"
if [ -z "$root" ] || [ ! -d "$root" ]; then
  echo "plan-sign-gate.sh: no harness root could be resolved from $_selfbin — refusing to run" >&2
  exit 2
fi

exec python3 "$(dirname "$0")/plan-sign-gate.py" "$root"
