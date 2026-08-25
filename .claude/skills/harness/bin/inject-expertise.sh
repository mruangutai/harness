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
# The regex anchor is name hygiene for the value interpolated into paths and
# headers below (repository-tier globbing widened what could reach a path).
# It does NOT filter which directories under .harness/ are read — a stray but
# legitimately-named directory is still injected; that cost is D-01's, not
# this filter's.
if ! printf '%s' "$agent" | grep -Eq '^harness-[a-z0-9-]+$'; then
  exit 0
fi

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

# Expertise file budget (DEC-145): 150 lines for craft tiers, 40 for repository
# tiers, enforced at authoring time by check-expertise.sh and hard-capped here
# so one bloated file cannot silently tax every spawn. Truncation is LOUD — the
# warning tells the agent curation is overdue rather than silently dropping the
# tail, and it names the budget actually applied so the agent curates to its
# own limit, not another tier's.
cap_body() {  # $1 = file, $2 = budget
  local file="$1" budget="$2"
  head -n "$budget" "$file"
  if [ "$(wc -l < "$file")" -gt "$budget" ]; then
    printf '\n[TRUNCATED at %s lines — this Expertise file violates its budget; distillation is overdue (DEC-145)]\n' "$budget"
  fi
}

# Gather repository-tier hits: $root/.harness/*/expertise/$agent.md, sorted by
# segment name. A plain glob with an [ -r ] guard means a non-matching glob
# never emits a literal '*' as a filename (no nullglob needed).
repo_segments=()
repo_files=()
for f in "$root"/.harness/*/expertise/"$agent.md"; do
  [ -r "$f" ] || continue
  # segment = the directory name between .harness/ and /expertise
  rest="${f#"$root"/.harness/}"
  segment="${rest%%/expertise/*}"
  # Interpolation hygiene only — skip (silently) any segment that isn't a
  # plain lowercase-alnum-hyphen token.
  case "$segment" in
    ''|*[!a-z0-9-]*) continue ;;
  esac
  repo_segments+=("$segment")
  repo_files+=("$f")
done

# Sort segments (and their paired files) by segment name.
sorted_idx=()
if [ "${#repo_segments[@]}" -gt 0 ]; then
  while IFS= read -r line; do
    sorted_idx+=("${line%%:*}")
  done < <(
    for i in "${!repo_segments[@]}"; do
      printf '%s:%s\n' "$i" "${repo_segments[$i]}"
    done | sort -t: -k2
  )
fi

{
  # Global tier first, project tier second. Precedence among tiers is stated
  # explicitly in the precedence line emitted below (when a repository tier is
  # present) — ordering here is presentation only, not the precedence rule.
  if [ -r "$glob" ]; then
    printf '## Your Expertise — cross-project craft (global tier)\n\n'
    cap_body "$glob" 150; printf '\n\n'
  fi
  if [ -r "$proj" ]; then
    printf '## Your Expertise — this checkout'\''s craft (project tier)\n\n'
    cap_body "$proj" 150; printf '\n\n'
  fi
  # Repository tier(s) — the most specific tier, so they ride last. Only
  # emitted (and the precedence line only stated) when there is at least one
  # repository block, because with none there is nothing to arbitrate.
  if [ "${#sorted_idx[@]}" -gt 0 ]; then
    printf 'Expertise precedence: repository over project over global, by specificity. A repository block whose segment is not the one you were dispatched against is not authoritative for your work — read the segment name.\n\n'
    for i in "${sorted_idx[@]}"; do
      segment="${repo_segments[$i]}"
      file="${repo_files[$i]}"
      printf '## Your Expertise — %s repository (repository tier)\n\n' "$segment"
      cap_body "$file" 40; printf '\n\n'
    done
  fi
} | emit

exit 0
