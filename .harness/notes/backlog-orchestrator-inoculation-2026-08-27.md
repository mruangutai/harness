# Backlog row — the orchestrator playbook lost its never-wait inoculation — 2026-08-27

**FILED as #903** — https://github.com/mruangutai/harness/issues/903 — on 2026-08-27, with the
operator's approval. This note is the local record; the ticket is the authority.

**Title:** The orchestrator playbook lost its never-wait rule and its inoculation to c5e59aa, so
every orchestrator takes an expected refusal it was never told to expect

## Provenance

Struck from FEAT-37-lead-stop-and-wake at signature on 2026-08-27. FEAT-37 gives the LEAD tier the
never-wait rule; this is the same defect one tier up. The operator ruled the lead-tier rule ships
sooner without waiting on it. The strike record is D-12 in that feature's `plan.yaml`.

## What happens

An orchestrator ends a dispatch turn while a lead is in flight. `validate-digest.py` refuses that
return. The orchestrator reads a `BLOCKED` message, has no instruction telling it the refusal is
expected, and stays alive to watch instead of ending its turn again. That is the exact loop FEAT-37
removes at the lead tier.

## Measured at 766d7b6

- `.claude/skills/harness/SKILL.md` is 288 lines. `grep -nEi "never wait|refusal.*expected|end
  (your|the|its) turn again"` returns NOTHING.
- The only surviving text is `:60` — "Each wake advances the plan by exactly one step. There is no
  waiting anywhere in this loop." It says there is no waiting. It does not say the refusal for not
  waiting is expected.
- `inflight_registry.py:328` `children_refusal_lines(agent, children)` keys on HAVING CHILDREN, not
  on `SINGLE_FLIGHT_AGENTS` (`:34`, which holds `harness-pm` alone). So every orchestrator ending a
  dispatch turn takes this refusal — not an edge case.

## Cause

`c5e59aa` (#815, "Trim the orchestrator playbook 51%: 6,409 -> 3,157 words") took the file from 527
lines to 288 and deleted the whole NEVER WAIT FOR A LEAD paragraph, including the clause saying the
refusal is expected. The trim was correct in bulk; the inoculation went out with it, unnoticed.

## What a fix has to deliver

The window around the no-waiting sentence must carry all six: a turn-ending directive; the platform
resuming the orchestrator when the child completes; the refusal being EXPECTED; the response being
to end the turn again; the refusal RECURRING; and the MEASURED bound in one sentence — at most once
per consecutive stop sequence, re-firing on a later wake. An unqualified "fires once" sentence is
false, and DEC-199 is being corrected for exactly that.

FEAT-37's struck task carried a full instruction for this. Read it in that feature's history at
`766d7b6^` before re-deriving.

## Do not restore the rest of the trim

`c5e59aa` was right. Only this paragraph is missing.
