#!/usr/bin/env bash
# PreToolUse hook (matcher: Task|Agent) — DEC-155/DEC-156: a harness agent never
# passes `model:` in a dispatch. The member's model is pinned in its agent
# frontmatter (DEC-152's tiers); a per-invocation parameter silently outranks the
# pin, re-deciding org design per-dispatch with nothing recording it. Observed
# live (kaya-ai FEAT-02, T-02): a lead's `model: "opus"` ran a sonnet-pinned doer
# on opus, unsanctioned and invisible to every gate.
#
# Registered in .claude/settings.json — NOT agent frontmatter (frontmatter
# PreToolUse hooks do not fire for spawned subagents, DEC-110):
#   "PreToolUse": [{ "matcher": "Task|Agent",
#     "hooks": [{ "type": "command",
#       "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/dispatch-guard.sh" }] }]
#
# Only exit 2 blocks (DEC-100). Fail OPEN on our own parse failure — a guard that
# blocks every spawn the moment the payload shape changes is worse than no guard.
# The MAIN SESSION (no agent_type) is never governed: model choice at the user
# channel is the user's.
set -uo pipefail

payload=$(cat)

printf '%s' "$payload" | python3 -c '
import sys, json

try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"dispatch-guard: unreadable hook payload ({e}) — passing through.", file=sys.stderr)
    sys.exit(0)

agent = d.get("agent_type") or ""
if not agent.startswith("harness-"):
    sys.exit(0)  # main session or a non-harness agent — not governed.

ti = d.get("tool_input") or {}
model = ti.get("model")
if not model:
    sys.exit(0)

print(f"dispatch-guard: BLOCKED — {agent} passed model: {model!r} in a dispatch.", file=sys.stderr)
print("  A member runs on the model pinned in its agent frontmatter — that pin is org design",
      file=sys.stderr)
print("  (DEC-152 tiers), not a dispatch option. If this task genuinely needs a stronger model,",
      file=sys.stderr)
print("  that is an ESCALATION: raise it in open_questions with the evidence and let it be",
      file=sys.stderr)
print("  decided above you and recorded (DEC-155). Re-dispatch without the model parameter.",
      file=sys.stderr)
sys.exit(2)
'
exit $?
