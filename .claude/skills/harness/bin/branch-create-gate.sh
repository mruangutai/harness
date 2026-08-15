#!/usr/bin/env bash
# PreToolUse Bash: gate git branch CREATION on work-tracking (DEC-144).
#
# A new branch must name the work it serves — either form:
#   <type>/<issue#>-slug        an OPEN GitHub issue (verified via gh, against the PINNED repo)
#   <type>/FEAT-NN-slug         a harness flow that exists on disk (BUG-NN too)
#
# Ported from kaya-ai's branch-create-gate.sh (field-proven there), genericized:
#   - SELF-GATING: reads .harness/harness.json github.sync — off/absent means this
#     script exits 0 instantly, so it is registered unconditionally as the fifth
#     settings.json prerequisite and costs nothing where the mirror is off.
#   - The repo is the PINNED github.repo (-R on every gh call), never inferred from
#     cwd (DEC-138: a fork or renamed remote must not verify against the wrong repo).
#   - No jq (the original's dependency) — python3 stdlib, like every harness script.
#   - Station moves live in gh-sync.py (FEAT-18) — this gate deliberately never
#     pins any board config keys again: it only ever moved one card, at branch
#     time, with no way to move it back, and the derived parent station covers
#     that case. It is in git history if the derivation ever misses something.
#   - Flow-id branches are validated LOCALLY (the flow dir exists) — harness flows
#     branch per feature, and the feature is the work-tracking record; its issues
#     are per-task and land via gh-sync, so demanding an issue number here would
#     deny every legitimate orchestrator branch.
#
# Deny is a structured permissionDecision (exit 0 + JSON), the PreToolUse contract
# for gating with a reason. Environmental failures NEVER hard-fail the gate open
# silently: gh missing/unauthenticated denies WITH the reason, because a gate that
# cannot verify must say so rather than wave work through (this one is a gate, not
# a mirror — the gh-sync skip rule deliberately does not apply).
set -uo pipefail
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
GH="${GH_BIN:-gh}"

input=$(cat)

# ---- config gate: github.sync on, repo pinned — else pass through instantly
read -r SYNC REPO <<<"$(python3 - "$root" <<'PY'
import json, os, sys
try:
    g = json.load(open(os.path.join(sys.argv[1], ".harness", "harness.json"))).get("github") or {}
except Exception:
    g = {}
print(str(bool(g.get("sync"))).lower(),
      g.get("repo") or "-")
PY
)"
[ "$SYNC" = "true" ] || exit 0
[ "$REPO" != "-" ] || exit 0   # sync-without-repo is INV-13's problem, not this gate's

cmd=$(printf '%s' "$input" | python3 -c 'import sys,json; print((json.load(sys.stdin).get("tool_input") or {}).get("command") or "")')

deny() {
  python3 -c 'import sys,json; print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":sys.argv[1]}}))' "$1"
  exit 0
}

# ---- extract the new branch name across branch-CREATING forms (from the original,
# incl. attached -bNAME / --create=NAME and a leading `git -C <path>`)
name=""
if printf '%s' "$cmd" | grep -qE 'git( +-[cC] +[^ ]+)* +checkout +([^;&|]* )?-[bB]'; then
  name=$(printf '%s' "$cmd" | sed -nE 's/.*checkout +([^;&|]* )?-[bB] *=?([^ ;&|]+).*/\2/p')
elif printf '%s' "$cmd" | grep -qE 'git( +-[cC] +[^ ]+)* +switch +([^;&|]* )?(-[cC]|--create)'; then
  name=$(printf '%s' "$cmd" | sed -nE 's/.*switch +([^;&|]* )?(-[cC]|--create) *=?([^ ;&|]+).*/\3/p')
elif printf '%s' "$cmd" | grep -qE 'git +worktree +add +([^;&|]* )?-[bB]'; then
  name=$(printf '%s' "$cmd" | sed -nE 's/.*worktree +add +([^;&|]* )?-[bB] *=?([^ ;&|]+).*/\2/p')
elif printf '%s' "$cmd" | grep -qE 'git( +-[cC] +[^ ]+)* +branch +[^ -]'; then
  name=$(printf '%s' "$cmd" | sed -nE 's/.*git( +-[cC] +[^ ]+)* +branch +([^ ;&|-][^ ;&|]*).*/\2/p')
else
  exit 0
fi
[ -n "$name" ] || exit 0

leaf="${name#*/}"

# ---- form 1: harness flow branch — the flow must exist on disk
flow=$(printf '%s' "$leaf" | sed -nE 's/^((FEAT|BUG)-[0-9]+[a-z0-9-]*).*/\1/p')
if [ -n "$flow" ]; then
  match=$(ls -d "$root/.harness/harness/features/${flow}"* 2>/dev/null | head -1)
  [ -n "$match" ] || deny "Branch \"${name}\" names flow ${flow}, but no .harness/harness/features/${flow}* exists. Flows are created by /harness-plan — plan first, then branch."
  python3 -c 'import sys,json; print(json.dumps({"systemMessage":"[work-tracking] Branch maps to flow "+sys.argv[1]+"."}))' "$flow"
  exit 0
fi

# ---- form 2: issue-number branch — the issue must be OPEN in the pinned repo
num=$(printf '%s' "$name" | sed -nE 's@^[^/]+/(issue-|#)?([0-9]+)([/_-].*|$)@\2@p')
[ -n "$num" ] || deny "Branch name \"${name}\" carries neither an issue number nor a flow id. Use <type>/<issue#>-slug for an OPEN issue, or <type>/FEAT-NN-slug for a planned flow."

command -v "$GH" >/dev/null 2>&1 || deny "Cannot verify issue #${num}: 'gh' is not installed. Install it (+ gh auth login), or branch under a flow id instead."
state=$("$GH" issue view "$num" -R "$REPO" --json state -q .state 2>/dev/null)
if [ -z "$state" ]; then
  "$GH" auth status >/dev/null 2>&1 || deny "Cannot verify issue #${num}: 'gh' is not authenticated (gh auth login)."
  deny "Issue #${num} not found in ${REPO}. Use a real issue number, or create it first."
fi
[ "$state" = "OPEN" ] || deny "Issue #${num} is ${state}, not OPEN. Branch off an open issue."

python3 -c 'import sys,json; print(json.dumps({"systemMessage":"[work-tracking] Branch maps to OPEN issue #"+sys.argv[1]+" in "+sys.argv[2]+"."}))' "$num" "$REPO"
exit 0
