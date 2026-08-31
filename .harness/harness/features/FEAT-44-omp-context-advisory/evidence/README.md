# Evidence — `ctx.sessionManager.getSessionFile()` exists and resolves per-session

This directory exists because the cycle-0 validator panel raised **F1 (high)**: the plan's
load-bearing premise — that a subagent can resolve its own transcript path — appeared **nowhere in
the tree**, and every planned test stubs it. The panel was right about the tree and right to gate on
it. Issue #923 cited the supporting probe as `/tmp/ctxprobe/` (local, not committed), which is not
evidence anyone else can check.

## How to reproduce

```bash
omp -p "Use the task tool once: spawn a subagent of type 'sonic' whose entire task is to reply with the single word pong." \
    -e ./probe-session-accessors.ts \
    --no-extensions --no-skills --no-rules --auto-approve \
    --model anthropic/claude-sonnet-5 \
    --session-dir /tmp/ctxprobe/sessions
```

The probe registers one `turn_end` handler, enumerates `ctx.sessionManager`'s read-only getters and
calls each. `--no-extensions --no-skills --no-rules` isolates it from harness machinery.

## Result — measured 2026-08-28, reproduced 2026-08-29

| session | `getContextUsage()` | `getSessionFile()` |
|---|---|---|
| main | defined (`{tokens, contextWindow, percent}`) | `<dir>/<ts>_<session-id>.jsonl` |
| **subagent (depth 1)** | **`undefined`** | `<dir>/<ts>_<parent-id>/<DispatchLabel>.jsonl` |

Both halves matter, and the second is the one the design rests on:

1. **The accessor exists** on the installed OMP build.
2. **In a subagent session it returns that subagent's OWN nested transcript**, keyed by dispatch
   label under the parent's directory — *in the very session type where `getContextUsage()` returns
   `undefined`*. The two accessors do not share the broken wiring.

`getSessionId()` returns a plain id in both, so it cannot substitute: it names the session without
locating its file.

## What this does NOT establish

- That every OMP version behaves this way. This is one build, measured twice on the same machine.
  It is a version-floor risk, recorded rather than resolved. **It is watched by
  `.claude/skills/harness/bin/probe-omp-session-accessor.py`, which is a MANUAL check, not a CI
  gate.** That script dispatches a real subagent and so needs both the omp binary and live model
  credentials; this repository's CI has neither, and referencing no `secrets.*` it never will as
  configured. Nothing in CI can verify a property of a binary CI does not have, so this risk is
  watched by a check someone must remember to run. Stated plainly rather than dressed up as
  automation.
- That a **stubbed** test proves anything about the live accessor. The panel's sharper half of F1
  stands regardless of this measurement: if all tests stub `getSessionFile`, a green suite proves
  only the stub works, which is issue #923's own failure shape one layer out. At least one test must
  exercise the real accessor.
