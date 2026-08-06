# VF-2 — the DEC-150 state-file shape gate is bypassed by `Edit`

**Status: FOUND BY THE MAIN SESSION at 7218d63, after the panel closed. Measured, not inferred.
NOT YET FIXED — it needs a user ruling, because the fix is a design question rather than a line.**

Found the way the honest ones usually are: I wrote `feature.yaml` up to **226 lines against its
200-line budget and nothing stopped me**, while the orchestrator reported the same gate rejecting
four of its own drafts at 217/208/206/205. Both observations are true. The difference is the tool.

## What happens

**The gate covers ONE of the THREE routes a state file can be written by.** This was wider than my
first write-up said — that version named only `Edit`, and the `Bash` route was found on a follow-up
check rather than assumed either way.

| Route | Outcome |
|---|---|
| **Write** | Shape gate runs. Over-budget file refused, exit 2, with routing advice. |
| **Edit** | Gate never runs. Any size, any comment count, exit 0, silently. |
| **Bash** (`python3 -c`, `cat >`, `sed -i`, …) | Gate never runs. `bash-write-guard.sh` checks the DOMAIN only — it has no shape logic at all. Exit 0. |

The agents most likely to use `Edit` are the ones doing incremental state updates — the exact bloat
path. And `bash-write-guard.sh`'s own header states that unparseable commands pass by design
(DEC-85/DEC-151): it converts casual bypass into deliberate obfuscation. That is a reasonable
posture for the *domain* question and simply leaves the *shape* question unasked.

## The measurement

Payload files, 400 lines (double the cap), `agent_type: harness-orchestrator`, same target
`.harness/features/FEAT-09-plan-time-route-check/feature.yaml`:

```
Write -> exit 2   check-domain: BLOCKED — state-file shape (DEC-150).
                    feature.yaml is 400 lines — budget is 200.
Edit  -> exit 0
Bash  -> exit 0   (bash-write-guard.sh, no output)
```

## The mechanism

`settings.json` registers the hook for `Write|Edit`, so it **does fire** on Edit. But
`check-domain.sh:376-377`:

```python
if (d.get("tool_name") or "") != "Write":
    sys.exit(0)
content = (d.get("tool_input") or {}).get("content") or ""
```

Everything below that line — the `feature.yaml` budget at `:398`, the comment-line budget at
`:403`, the handoff shape gate at `:504` — is unreachable for an `Edit`. The early exit is not
obviously wrong in isolation: an `Edit` payload carries `old_string`/`new_string` and **no
`content`**, so the gate has nothing to measure. It exits rather than mismeasuring.

**The domain check is NOT affected.** `domain_check()` runs before this early exit, so who-may-write-
what is still enforced on `Edit`. This is narrowly the *shape* gate.

## Why it is the same class as VF-1

VF-1: the guard was disabled by an environment variable, exit 0, nothing logged.
VF-2: the guard is disabled by choosing a different tool, exit 0, nothing logged.

Both are registered, both look enforced from the outside, and in both cases **an all-green run is
not an absent defect**. Neither was visible to a reviewer reading the gate's own logic, because the
logic is correct — it is the *reachability* that is wrong.

## Why the fix is a ruling, not a line

A `PreToolUse` hook sees the Edit payload, not the resulting file. To shape-check an `Edit` it must
reconstruct the result: read the file from disk and apply `old_string`→`new_string`. That is doable
but carries real edge cases — `replace_all`, a string occurring more than once, and a file changing
between the check and the write. Options, none free:

1. **Reconstruct and check the Edit result.** Adds file I/O and replacement semantics to a
   `PreToolUse` hook, and can disagree with what the tool actually does. **Closes Edit only — the
   Bash route stays open**, so it buys two of three.
2. **Check the file's CURRENT size on Edit** and refuse to edit an already-over-budget file. Cheap,
   no reconstruction risk. But it cannot stop the edit that *crosses* the budget, it would block the
   very edits that trim a bloated file (needs a shrink exemption), and it also leaves Bash open.
3. **Move the shape check to `PostToolUse`.** **The only option that covers all three routes** — it
   sees the file as it actually landed, with no reconstruction and no per-tool special-casing. The
   trade is real: it detects rather than prevents, so the over-budget write has already happened and
   the gate's job becomes "tell the agent to fix it" rather than "refuse it".
4. **Accept and document.** Cheapest, and the honest cost is that DEC-150's budget is advisory for
   two of three routes — prose-only enforcement, which is the shape this repo keeps filing tickets
   against.

**Given the Bash route, option 3 is the only one that actually closes VF-2.** Options 1 and 2 narrow
it. That is a genuine trade rather than a free win: 3 gives up prevention to gain coverage, and
whether a state file that is briefly over-budget matters is a judgment about what the budget is
*for* — a context bound, which a post-check still enforces before the next reader loads it.

`check-domain.sh` is a **DEC-174 carve-out**, so whichever option wins is a declared main-session
step, applied directly with the tests run explicitly and a human reading the diff.

## Immediate compliance

Independent of the ruling: `feature.yaml` was trimmed back under 200 lines by hand, rationale routed
to `notes/` per the gate's own routing advice. The bloat was mine, introduced while recording the
VF-1 resolution.
