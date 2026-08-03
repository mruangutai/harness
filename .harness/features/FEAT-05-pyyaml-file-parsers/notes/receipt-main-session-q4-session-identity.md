# Receipt — Q4 / B4 RESOLVED: session identity IS available in a hook subprocess — 2026-08-03

Main session, at `699e756`. Run because Q4 gated SC-08 and REQ-05, and T-09's probe never
executed so the question had stood open on an unproven inference.

## Method

Same technique that settled Q3, which is the point — it is demonstrably capable of producing
evidence. One additive block at the top of the worktree's `check-domain.sh` (immediately after
`payload=$(cat)`, before every early exit), dumping the payload's key set and the length of every
`CLAUDE*` environment variable. `bash -n` and `test-check-domain.py` (9/9) run after insertion and
before spawning. One throwaway `general-purpose` agent attempted a single `Write`. Reverted and
proved byte-identical to HEAD (`git diff --quiet`), 9/9 re-confirmed.

## Result — 21 fires, all consistent

```
PAYLOAD_KEYS=['agent_type', 'tool_input', 'tool_name']
session_id=None
transcript_path=None
CLAUDE_ENV=[('CLAUDECODE',1), ('CLAUDE_CODE_CHILD_SESSION',1), ('CLAUDE_CODE_ENTRYPOINT',3),
            ('CLAUDE_CODE_EXECPATH',60), ('CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH',1),
            ('CLAUDE_CODE_SESSION_ID',36), ('CLAUDE_EFFORT',3), ('CLAUDE_PID',4),
            ('CLAUDE_PROJECT_DIR',84)]
```

Against `_resolve_identity`'s four-entry chain:

| entry | in a genuine `PreToolUse` fire |
|---|---|
| `payload["session_id"]` | **ABSENT** — the payload carries only three keys |
| `payload["transcript_path"]` | **ABSENT** |
| **`CLAUDE_CODE_SESSION_ID`** | **PRESENT, 36 chars** — this is the live entry |
| `CLAUDE_CODE_BRIDGE_SESSION_ID` | absent here (T-09 saw it in a *Bash* subprocess; a hook
subprocess is a different environment, which is exactly the distinction T-09's corrected receipt
was right to insist on) |

End-to-end check of the module itself, replicating a real fire's inputs — payload without
`session_id`, env var present:

```
resolved identity: 'aaaa…' (36)      # env-var entry fires
with NO env var   : None             # chain correctly exhausts
```

## What this settles

- **Q4 / B4 RESOLVED. The bootstrap escape is implementable as designed.** SC-08 and REQ-05 are
  satisfiable as written; no redesign is needed. `_resolve_identity` works, via its third entry.
- **T-09's "extra question" is also resolved.** Its receipt hypothesised that
  `CLAUDE_CODE_SESSION_ID` is an ordinary environment variable inherited by any child process
  "regardless of `HOOK_PAYLOAD` plumbing", and flagged it as unverified. **Confirmed:** the probe
  read it straight from `os.environ` in a genuine fire, with no dependence on the payload. So the
  `:97` call site needs no `HOOK_PAYLOAD` addition.
- **The chain's first two entries are dead in THIS environment** but are correct to keep as
  fallbacks — a payload carrying `session_id` is the documented shape elsewhere, and the chain
  costs nothing when it misses.

## What this CORRECTS in T-09's receipt

That receipt concluded: *"Which copy of `check-domain.sh` executes, for a real Write/Edit in this
worktree: **most likely the main checkout's**"*, while honestly flagging an alternative it could
not rule out — that the worktree copy runs and its probe failed for another reason.

**The alternative was correct.** Both of today's probes fired from the worktree copy (11 fires for
Q3, 21 for Q4). The inference was wrong; the caveat was right. Its cause is still unidentified —
the difference is that both of today's probes sit at the TOP of the script, before every early
exit, whereas T-09's sat inside the second heredoc, which is reached only after `domain_check()`
returns 0 and only for `tool_name == "Write"`. Not chased further: T-09's question is answered by
other means, and the remaining puzzle is about a probe that no longer exists.

## Incidental

**21 fires for one reported write attempt** (Q3's probe saw 11). The multiplier is not constant.
Not chased — it changes no conclusion here, since all 21 agree. Recorded beside Q3's note so the
observation is not rediscovered a third time.
