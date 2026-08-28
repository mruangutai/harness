# Root cause — domain lead loops instead of ending its turn (FEAT-37 t-01)

**Write-path note:** the named deliverable `notes/root-cause-lead-loop.md` was DENIED by
`check-domain.sh`: `harness-backend-dev may not write .../notes/root-cause-lead-loop.md`. Permitted
paths for this agent are `.claude/skills/harness/bin/**`, `.harness/codebase/api-surface.md`,
`.harness/codebase/domains/**`, `.harness/*/features/*/notes/receipt-harness-backend-dev-*.md`,
`.harness/expertise/harness-backend-dev.md`, `.harness/*/expertise/harness-backend-dev.md`,
`.harness/*/features/*/observations/harness-backend-dev.md`. This is the identical report, written
to the receipt fallback per dispatch instruction. The manifest gap (`notes/root-cause-*.md` is in
no member's `domain:` and not in `shared:`) is itself a second finding — raised in `open_questions`.

## BLUF

**#831's stated cause is CONFIRMED, and a compounding cause is ADDED.** The measured specimen —
`harness-product-lead` agent `a8f1c68d9a0d69f25`, FEAT-34, dispatched `harness-pm` agent
`adb4d9cdb0ba1f095` at `2026-08-25T01:45:50Z` — shows the exact transcript shape #831 describes:
~3.5 minutes into ~40 cycles of one line of "waiting"/"standing by" text followed by one filler
`Read`/`Grep` call, from line 35 to line 186 of its sidecar, until the pm's real completion landed.
**The #811 hook-refusal loop (the dispatch's own stronger candidate) is RULED OUT as the cause of
this transcript**: zero `SubagentStop`/`stop_hook_active`/"children in flight" events appear
anywhere in this sidecar — the lead never even attempted to stop, so the hook was never in the
loop. It burned turns manufacturing filler work instead.

## The failing case, with anchors

Sidecar: `~/.claude/projects/-Users-molchairuangutai-GitHub-harness/e69cbdc1-8355-4358-b5f2-d7604a1a913b/subagents/agent-a8f1c68d9a0d69f25.jsonl`
- Line 32 (`01:45:25`): `Agent` dispatch of `harness-pm`.
- Line 37 (`01:45:50`): tool_result for that dispatch — this is the exact text the lead read.
- Lines ~35–186 (`01:45:54`–`01:49:31`): repeating pattern — one line of text ("Waiting on pm.",
  "Standing by for pm's return.", "Continuing to hold for pm's return.") + one `Read`/`Grep` of an
  unrelated feature artifact, never converging, never ending the turn.
- Line 186 (`01:49:31`): pm's real return is read; the loop stops because real work resumed, not
  because anything taught it to stop.
- `grep -c "stop_hook_active\|children in flight\|Stop hook feedback\|SubagentStop"` on this file
  returns **1**, and that one hit is skill text explaining the hook (from the preloaded
  `harness-team/SKILL.md`), not a live event — 0 live `SubagentStop` refusals occurred in this
  transcript.

## Causal chain

1. **Necessary and sufficient on its own: the lead's preloaded skill set carries no stop-and-wake
   rule.** `harness-product-lead.md:8-13` (and identically `harness-eng-lead.md`,
   `harness-validator-lead.md`) preload exactly `harness-handoff`, `harness-expertise`,
   `harness-principles`, `harness-zero-micro-management`, `harness-team` — never
   `.claude/skills/harness/SKILL.md`, which is the *orchestrator's* playbook and the only file in
   this repo carrying "NEVER WAIT FOR A LEAD. END YOUR TURN." (`harness/SKILL.md:45`) or "There is
   no waiting anywhere in this loop" (`:157`). Grepping all five lead-preloaded files
   (`harness-team/SKILL.md`, `harness-zero-micro-management/SKILL.md`, all three
   `.claude/agents/harness-*-lead.md`, `harness-handoff/SKILL.md`) for "end your turn"/"wait"
   returns zero end-your-turn instructions anywhere — matching #831's own operator-verified greps.
   `harness-team/SKILL.md` goes straight from **d. Dispatch** (`:97`) to **e. Collect returns**
   (`:111`) with nothing between them.
2. **Contributory, and independently discoverable by the agent: the `Agent` tool's own dispatch
   result actively suggests the wrong behavior.** The literal text returned to the lead at line 37
   of the sidecar reads: *"The agent is working in the background. You will be notified
   automatically when it completes. You know nothing about its results until that notification
   arrives — do not report, assume, or predict them; **continue other work or respond to the user
   in the meantime.**"* Nothing in that text says "end your turn" or "you will be woken" — it
   explicitly invites "continue other work... in the meantime," and the lead's transcript does
   exactly that: it manufactures unrelated `Read`/`Grep` calls as "other work" for ~40 turns. This
   is the same tool text an orchestrator receives, but the orchestrator's preloaded playbook
   (`harness/SKILL.md:45-56`) overrides it explicitly; a lead has no such override.

## Candidates ruled in / out

| # | Candidate | Verdict | Evidence |
|---|---|---|---|
| 1 | #811 hook-refusal loop (`validate-digest.py:845,903,909,917-920`) | **RULED OUT as cause of this transcript** | Zero live `SubagentStop` events in the a8f1c68d specimen — the lead never tried to stop. Separately, on the one confirmed live specimen where the refusal DID fire (`harness-product-lead` `aa4bb05730add8058`, FEAT-35, sidecar `.../e69cbdc1.../subagents/agent-aa4bb05730add8058.jsonl` lines 32-61), it fired **exactly once** (line 33), the lead declined to fabricate a verdict (line 35), a real completion notification arrived (line 36), and it returned cleanly with `VERDICT: PASS` at line 61 — matching the code's own "at most once" comment (`validate-digest.py:903`), not the dispatch's infinite-refusal hypothesis. This is a real, separately-filed defect (#811: DEC-201 vs. the children-in-flight refusal composing badly) but it did not generate #831's observed loop. |
| 2 | Missing stop-and-wake sentence in `harness-team/SKILL.md` (#831's stated cause) | **RULED IN — necessary and sufficient** | See chain item 1. Directly reproduces the observed shape: filler tool calls between dispatch and the real return, with no hook interaction at all. |
| 3 | `Agent` tool's own description ("continue other work... in the meantime") | **RULED IN — contributory** | Quoted verbatim above from the live sidecar (line 37). Actively misleads absent an overriding rule; explains *why* the lead invents filler work rather than merely idling. |
| 4 | `harness-zero-micro-management`, the three lead agent files, `harness-handoff` digest contract | **RULED OUT as independent causes** | Greps show none of them mention waiting, notification, or forbid returning — they are silent, not actively wrong. They do not need to change for a fix; the gap is item 1's silence, plus item 3's active nudge in the other direction. |

## Fix surface this implies

- The natural fix location is `.claude/skills/harness-team/SKILL.md` between "d. Dispatch" (`:97`)
  and "e. Collect returns" (`:111`) — the same shape `harness/SKILL.md:45-56` already uses for the
  orchestrator, stating both halves: a lead ends its turn after dispatch, and the member's
  completion wakes it.
- Because the `Agent` tool's own text (candidate 3) independently nudges toward "continue other
  work," the fix should not rely on silence-removal alone; it needs to be explicit enough to
  override that nudge, the way `harness/SKILL.md:50` explicitly names "The single-flight refusal on
  your return is EXPECTED" to pre-empt a different piece of tool/hook behavior.
- `.claude/skills/harness-team/SKILL.md` resolves to nobody in the manifest for write purposes — see
  `open_questions` below.

## Open questions

- Whether `harness-team/SKILL.md`'s current manifest gap (owned by nobody, per the operator's own
  pre-check and confirmed here by the `check-domain.sh` denial above) is itself a defect to fix
  alongside the sentence, or whether the fix should land through a different, owned file. Plan-level
  decision, not a diagnosis this run can settle.
- Whether the `Agent` tool's built-in description text (candidate 3) is itself editable, or whether
  it is platform-fixed and the only lever is the skill-level override. Outside this run's read
  access to confirm either way.
