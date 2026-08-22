# T-01 — the PreToolUse dispatch payload, measured

**The answer: `tool_input.subagent_type` names the DISPATCHED persona.** T-06 and T-08 are
unblocked. Nothing in this plan may cite a payload key this note does not record.

## PreToolUse Task payload keys
cwd
effort
effort.level
hook_event_name
permission_mode
prompt_id
session_id
tool_input
tool_input.description
tool_input.model
tool_input.prompt
tool_input.subagent_type
tool_name
tool_use_id
transcript_path

DISPATCHED_PERSONA_KEY=tool_input.subagent_type

## What the values were

| key | value |
| --- | --- |
| `tool_name` | `Agent` |
| `hook_event_name` | `PreToolUse` |
| `agent_type` | **absent** |
| `tool_input.subagent_type` | `general-purpose` |
| `tool_input.model` | `haiku` |
| `effort.level` | `medium` |

`agent_type` is absent because the dispatch came from the main session, which
`dispatch-guard.sh` deliberately never governs — model choice at the user channel is the
user's. So this capture confirms the dispatched persona key WITHOUT confirming anything about
the dispatcher key on a governed spawn. A governed capture would carry `agent_type`; this one
had no reason to.

## Two findings the capture handed over for free

**`tool_name` came back `Agent`, not `Task`.** The registered matcher is `Task|Agent`, so the
guard fires. Had it named only `Task`, `dispatch-guard.sh` would be dark today with no signal —
the exact silent-failure shape the no-`agent_type` pass-through's stderr line exists to prevent.
The matcher's second alternative is load-bearing, not defensive.

**`effort.level` exists on the payload.** No harness code reads it. Recorded because a later
task that wants to govern reasoning effort per tier does not need a new probe to find it.

## SubagentStop's agent_type is SETTLED, not measured here

Deliberately not re-measured. `validate-digest.py` selects a persona-specific schema from the
dispatched agent's own name, and a live orchestrator return was rejected against the
`orchestrator` schema in the `SCHEMAS` mapping. The no-`agent_type` pass-through, whose print
begins `check-digest: hook payload has no agent_type`, did not fire. A schema chosen by persona
cannot be chosen when the persona is absent. Re-measuring a settled fact spends a spawn on
nothing.

A later reader should read that as settled-by-inference, not settled-by-capture. The inference is
sound but it is not the same evidence class as the key list above.

## Method, so a platform change can be told from a wrong reading

Date: 2026-08-22. Machine: Darwin 25.5.0 arm64, macOS 26.5.2. Claude Code 2.1.235.

1. Appended one best-effort line to `dispatch-guard.sh` immediately after `payload=$(cat)`,
   writing the raw payload to a scratch file **outside the repository**:
   `{ printf '%s\n' "$payload" >> "<scratch>/t01-payloads.jsonl"; } 2>/dev/null || true`
2. `bash -n` on the script to prove the edit could not break a live PreToolUse hook.
3. Dispatched one throwaway subagent (`subagent_type: general-purpose`, `model: haiku`) whose
   whole instruction was to call no tools and reply `ok`.
4. Flattened the captured JSON to dotted key paths and sorted them.
5. `git checkout --` on the script, then `git diff --quiet` to prove it clean.

**The edit was applied to the MAIN checkout, not this worktree, and that is the whole trick.**
The hook is registered as `${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/dispatch-guard.sh`,
which resolves to `/Users/molchairuangutai/GitHub/harness`. A probe installed in this worktree
captured nothing — verified: the file did not exist after the orchestrator dispatch that followed
it. This is the same resolution fact FEAT-31 T-17 established, and it will silently defeat any
future hook probe run from a feature worktree.

Both copies were reverted and both are clean.
