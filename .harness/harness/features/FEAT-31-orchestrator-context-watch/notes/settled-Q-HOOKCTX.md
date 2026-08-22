# Q-HOOKCTX settled — hook stderr DOES reach a running agent, as a tool-result error string

Settled 2026-08-21 by the main session, by DIRECT OBSERVATION rather than by reading source. This
closes the one item `notes/probe-hook-delivery-channel.md` explicitly left open under "Not verified
here": *that the stderr text is visible to the model as context rather than only as a tool-result
error string.*

## The observation

Earlier in this same session the main session appended a section to
`FEAT-31-.../STATE.md`. `check-domain.sh --post` — registered on `PostToolUse` for `Write|Edit|Bash`
in `.claude/settings.json`, the exact registration T-17 targets — exited 2. What arrived in the
running agent's turn was this, in full:

    PostToolUse:Bash hook blocking error from command:
    ".../check-domain.sh --post": check-domain: OVER BUDGET (already written) —
    ...STATE.md: state-file shape (DEC-150).
      STATE.md is 132 lines — budget is 120. It holds no history: ## Current is replaced, never appended.
      illegal section(s) [...] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
      Routing: current truth REPLACES STATE.md ## Current; ...

Three things are established by that, and none of them was established before:

1. **The stderr text arrives in full.** Every line the gate wrote, including the routing advice, was
   present. Nothing was truncated to an exit code or a summary.
2. **It arrives as a TOOL-RESULT ERROR, not as free-standing context.** The harness wraps it as
   `PostToolUse:Bash hook blocking error from command: ...`. So the answer to Q-HOOKCTX as posed is
   the second half, not the first.
3. **The agent read it and acted on it.** The append was reverted and the content re-routed to
   `notes/`. Delivery is not theoretical.

## What follows for T-17, and it is not "proceed unchanged"

**The design stands.** REQ-08 and SC-13 require the orchestrator "is told so in its own context,
while it is running". A tool-result error carrying the full text, which the agent then acts on,
satisfies that. `PostToolUse` + exit 2 is the channel. Nothing needs rethinking.

**But the ERROR framing is a hazard the warning text must defuse, and now it is measured rather
than anticipated.** The observed reaction to that error was to **undo the write** — because in this
case undoing was correct. In post mode the write has ALREADY LANDED. An orchestrator receiving
"you are over the context threshold" as a *blocking error* on a Write may reasonably conclude its
write failed and either retry it (a duplicate) or revert it (a loss).

`check-domain.sh` already anticipated exactly this and encodes the remedy at `:698-703`: the verb is
mode-dependent, and in post mode it is `OVER BUDGET (already written)` rather than `BLOCKED`,
precisely "because in PRE the write is genuinely" stopped and in POST it is not.

**So T-17's warning text carries a hard obligation, not a stylistic one:** it must state in its
first line that nothing was blocked, the tool call succeeded, and no retry or revert is needed —
before it says anything about context size. A warning that reads as a failure is worse than no
warning, because the recipient's corrective action damages the tree.

## Scope of this note

This settles delivery. It does NOT settle the matcher question the probe note flagged as "the one
thing the plan must still check rather than assume" — whether `Write|Edit|Bash` actually fires for a
real orchestrator. That was measured separately by the orchestrator: of 36 orchestrator transcripts
crossing 200,000 tokens, 36 made a Write, Edit or Bash call after the crossing. Zero would go
unwarned. Both halves are now evidenced.
