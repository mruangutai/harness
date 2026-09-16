# BRIEF — BUG-1724-run-end-tokens

## Problem

Completed OMP orchestrator dispatches leave `tokens: null` in their `feature.json` run entries even though the host returned integer token counts for the task results. Operators therefore see no token total from `feature-record.py spend` or the `SPEND:` advisory, and orchestrators are asked to transcribe a value the host already has.

## Done when — by perspective

**operator** — I can rely on completed OMP dispatches recording the host-reported token total on the open run before spend is read, while a host that reports no token figure still records `null`.

**orchestrator** — I can close a normal OMP run without copying a token count from a tool result; multiple results from one task call count as one dispatch, and the explicit override remains available only when the host supplied no figure.

**code maintainer** — I can rely on ambiguous or missing open-run state being refused rather than stamped, and on focused regression coverage for stamping, summing, preservation, refusal, compatibility-host null behavior, and the explicit override.

## Success criteria

- SC-01 (operator): When an OMP orchestrator task result carries integer token counts, the hook sums the counts for that task call, stamps that total on the one open run before reading spend, and a subsequent bare `run-end` preserves it so `feature-record.py spend` and any emitted `SPEND:` advisory use the recorded number. The new regression case must fail before the fix and pass afterward.
  verify: automated        evidence: unit
- SC-02 (operator): When the host reports no token count, the hook does not invent or stamp one and a bare `run-end` records `null`, including on the Claude Code compatibility host described by DEC-210. The regression case must fail if the absent-host-value path produces a number.
  verify: automated        evidence: unit
- SC-03 (orchestrator): The normal OMP completion path requires no `--tokens` transcription, sums several result counts once for the dispatch, and retains `run-end --tokens N` as an explicit override only for a host that reported no figure. Regression cases must fail if summing, the bare normal close, or the override is removed.
  verify: automated        evidence: unit
- SC-04 (code maintainer): `stamp-tokens --file <feature.json> --tokens N` writes only when exactly one run has `started_at` and no `ended_at`; it exits 2 without changing the file when there is no open run or more than one, and its diagnostic identifies the conflicting state and run ids. The refusal cases must be demonstrated failing before the verb exists and passing afterward.
  verify: automated        evidence: unit

## Verification gaps

- `typecheck` matches the changed TypeScript hook but has no runner, so static type validity is not proven by that kind; the active `unit` runner's Bun hook suite and code review carry this surface instead.

## Constraints

- DEC-225 SUPPLIES the patch lane: one bounded task, no panel, and no goal-check.
- DEC-227 SUPPLIES the measured-or-null token contract, summed spend behavior, advisory input, and the rule that historical values remain as recorded.
- DEC-210 SUPPLIES compatibility-host behavior: where no task-result token is available, `null` remains correct.
- DEC-174 BLOCKS team execution because the hook and `feature-record.py` are what spend and advisories read, and the tests that vouch for that enforcement path remain inside the same line.
- A bare `run-end` must preserve a pre-stamped token value, and `run-end --tokens N` must remain the explicit override when the host reported nothing.
- Refusal belongs to the new stamping verb, not to `run-end`; `run-end` cannot infer that a token figure exists outside `feature.json`.

## Out of scope

- Back-filling `tokens` on the 28 BUG-285-canonical-reader runs or any historical feature; DEC-227 keeps historical values as recorded.
- Reading tokens from session JSONL for the orchestrator's own context; that is the context advisory already governed by DEC-198.
- Changing what the orchestrator decides after seeing the figure; that is issue #1723.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-15
