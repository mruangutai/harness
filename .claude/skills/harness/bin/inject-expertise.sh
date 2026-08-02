#!/usr/bin/env bash
# SubagentStart hook — inject an agent's Expertise file into its starting context.
#
# VERIFIED (DEC-100): SubagentStart fires for NESTED spawns too, so this reaches
# lead-spawned members, not just top-level agents.
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

index="$root/.harness/codebase/INDEX.md"

# Expertise file budget (DEC-145): 150 lines, enforced at authoring time by
# check-expertise.sh and hard-capped here so one bloated file cannot silently
# tax every spawn. Truncation is LOUD — the warning tells the agent curation
# is overdue rather than silently dropping the tail.
cap_body() {  # $1 = file
  head -n 150 "$1"
  if [ "$(wc -l < "$1")" -gt 150 ]; then
    printf '\n[TRUNCATED at 150 lines — this Expertise file violates its budget; distillation is overdue (DEC-145)]\n'
  fi
}

{
  # Global tier first, project second — project wins on conflict, and later
  # text carries more weight, so ordering encodes the precedence rule.
  if [ -r "$glob" ]; then
    printf '## Your Expertise — cross-project craft (global tier)\n\n'
    cap_body "$glob"; printf '\n\n'
  fi
  if [ -r "$proj" ]; then
    printf '## Your Expertise — this codebase (project tier, authoritative on conflict)\n\n'
    cap_body "$proj"; printf '\n\n'
  fi
  # The codebase map's index (DEC-137) — the third knowledge tier, delivered the same
  # way as Expertise because preload is the only delivery path with a clean record
  # (DEC-125 x4: everything that relied on being pointed at failed silently at least
  # once). Absent on an unmapped project, and that is normal — silence is correct here.
  # ONLY the index rides the spawn; details are fetched by path. Cap enforced at
  # authoring time (60 lines); truncated here as a backstop so one runaway index
  # cannot re-create the CLAUDE.md bloat (DEC-135) across every spawn.
  if [ -r "$index" ]; then
    printf '## Codebase map — index (details on disk; every claim carries file:line anchors; the map is a hint, code is truth)\n\n'
    head -n 80 "$index"; printf '\n'
  fi
} | emit

exit 0
