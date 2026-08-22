# Probe — what a PreToolUse payload holds inside a subagent

Run 2026-08-20 from the main session. Method: one line appended to
`bash-write-guard.sh` immediately after `payload=$(cat)`, before any logic, writing the raw
`HOOK_PAYLOAD` to a scratchpad file. A `general-purpose` subagent then ran exactly one Bash
command (`echo probe-ok`). The line was reverted immediately after capture.

**Guard behaviour was unchanged throughout.** `test-bash-write-guard.py` reported
`27/27 worktree-boundary cases passed` with the probe in place and again after the revert, and
`git status` on the file is clean.

## The captured payload — 11 keys

```
agent_id, agent_type, cwd, hook_event_name, permission_mode, prompt_id,
session_id, tool_input, tool_name, tool_use_id, transcript_path
```

## RESULT 1 — the assumption this feature rested on is FALSE

```
transcript_path  '/Users/…/-Users-molchairuangutai-GitHub-harness/070b3f94-….jsonl'
session_id       '070b3f94-b495-4deb-b352-6896cfb60ad3'
```

`transcript_path` is the **PARENT session's** transcript, not the subagent's. It is the main
session's own file, and `session_id` is the main session's id.

Had the brief's design been built as written, the hook would have measured the MAIN SESSION's
context on every orchestrator tool call. It would have returned a number, that number would have
grown, and it would have been wrong — the failure class this repository keeps shipping: an
assertion that is green and incapable of going red.

## RESULT 2 — the mechanism exists anyway, via a field nobody named

```
agent_id  'a169d08f65bcba077'
```

`{session_id}/subagents/agent-{agent_id}.jsonl` — **exists, verified**. Its sidecar reads
`{"agentType": "general-purpose", "description": "Probe: fire the Bash hook once",
"toolUseId": "toolu_01BG2H9y1QJy8f5cSNb7urDQ", "spawnDepth": 1, "model": "haiku"}`.

So the hook can locate the calling agent's own transcript exactly, with no guessing and no race
against concurrent orchestrators. It needs `session_id` and `agent_id`, and NOT
`transcript_path`.

`agent_type` is in the payload too, so the orchestrator filter costs nothing. `cwd` is in the
payload, which is what REQ-05 needs once orchestrators run in worktrees — the transcript
directory is derived from cwd, and the payload carries it.

## Verdict

REQ-08 has a mechanism. REQ-09 and REQ-10 have something to trigger them. The design holds and
the plan is not invalidated — but every statement naming `transcript_path` as the source was
wrong and is corrected.

## What this says about `harness_yaml.py:479`

`_resolve_identity` reads `session_id` first and falls back to the `transcript_path` stem. On this
evidence both resolve to the PARENT session inside a subagent, so that function returns the
session identity and never the agent's. That is correct for its own purpose — the bootstrap marker
is per session — and it is not a defect. It is only wrong as evidence about agent identity, which
is what this brief cited it for.
