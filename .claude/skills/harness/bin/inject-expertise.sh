#!/usr/bin/env bash
# SubagentStart hook — inject an agent's Expertise file into its starting context.
#
# VERIFIED (DEC-100): SubagentStart fires for NESTED spawns too, so this reaches
# lead-spawned workers, not just top-level agents.
#
# Contract: stdin = hook JSON carrying `agent_type`. stdout = JSON with
# hookSpecificOutput.additionalContext. Always exit 0 — this hook must never
# block a spawn. A missing Expertise file is normal (a new agent has none).
set -uo pipefail

payload=$(cat)
agent=$(printf '%s' "$payload" | python3 -c '
import sys, json
try:
    print(json.load(sys.stdin).get("agent_type", ""))
except Exception:
    print("")
' 2>/dev/null)

# Only harness agents. Anything else gets no injection and no error.
case "$agent" in
  harness-*) ;;
  *) exit 0 ;;
esac

root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
proj="$root/.harness/expertise/$agent.md"
glob="$HOME/.harness/expertise/$agent.md"

emit() {
  python3 -c '
import sys, json
body = sys.stdin.read()
if body.strip():
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SubagentStart",
        "additionalContext": body,
    }}))
'
}

{
  # Global tier first, project second — project wins on conflict, and later
  # text carries more weight, so ordering encodes the precedence rule.
  if [ -r "$glob" ]; then
    printf '## Your Expertise — cross-project craft (global tier)\n\n'
    cat "$glob"; printf '\n\n'
  fi
  if [ -r "$proj" ]; then
    printf '## Your Expertise — this codebase (project tier, authoritative on conflict)\n\n'
    cat "$proj"; printf '\n'
  fi
} | emit

exit 0
