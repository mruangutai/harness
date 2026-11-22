# BRIEF — BUG-2187 Review pin and rework rounds

## Problem

Operators following the build-phase seam procedure invalidate their own review pin when station writes change plan.yaml. They must hand-write review_sha because no ledger verb exists, and spend undercounts recorded re-gates when the main session builds the fix directly (#2187, #2201, #2167, #2222).

## Done when — by perspective

**operator** — I can follow the documented review seam without a false stale pin, record the pin through the ledger, and rely on spend to count recorded rework rounds including direct fixes.

**code maintainer** — I can distinguish lifecycle-only movement from changed reviewed content, with regressions defending the pin and spend contracts and their existing safety boundaries.

## Success criteria

- SC-01 (code maintainer): An authentic new integration regression fails on base and passes on the fix: loaded-plan equality ignores only top-level status and each task status, plus serialization-only differences, without STALE. Other reviewed-content changes, including arbitrary nested status changes, retain STALE. Preserve all five deliberate silences (no git work tree, unresolved pin, no disk plan, absent pinned path, terminal station), placeholder handling, and changed-then-restored content acceptance. Existing safety assertions need not fail at base; the new station-only regression must expose the defect.
  verify: automated evidence: integration
- SC-02 (operator): Authentic new unit regressions fail on base and pass on the fix for pin-review --file <feature.json> [--sha <sha>]: omitted sha uses HEAD, explicit refs resolve to full commit ids, noncommits are refused without mutation, and successful pinning uses feature_json_write with APPLIED output; refusal uses REFUSED style. Existing safety assertions need not fail at base; the new verb regression must expose its absence. Regressions also protect both guidance documents naming the verb wherever they instruct pinning or recording review_sha, keeping the seam order minimally changed.
  verify: automated evidence: unit
- SC-03 (operator): Authentic new unit regressions fail on base and pass on the fix: spend counts regate judgements at or after the first validate started_at, including main-session-direct fixes with no fix run; excludes earlier and non-regate judgements; uses existing fix-run counting only when the judgement window has no regate. Cover the exact start boundary, multiple rounds, no validate and legacy fallback, while preserving cycles_used and existing spend/hook contracts. Existing fallback assertions need not fail at base; the new direct-fix regression must expose the undercount.
  verify: automated evidence: unit

## Verification gaps

None for this Python CLI/check-state and guidance patch: active unit and integration runners carry the SCs. No browser, component, TypeScript or model surface is changed; unresolved ui/component/typecheck and excluded functional/eval kinds do not carry these SCs. Intake plan/route gates do not prove behavior or base-red/fix-green; implementation QA must supply commands, exact subject SHAs, regression identities, exit codes, stdout and stderr. No UAT or prototype is required for this administrative patch.

## Constraints

- DEC-174 BLOCKS team implementation of INV-33 and its coupled tests/guidance: T-01 is main-session-direct, as in BUG-2239. Keep all relative edits inside the assigned product worktree.
- DEC-225 SUPPLIES patch intake: one task, at most 120 brief lines, no panel or goal-check; qa and review judge the diff after signature.
- DEC-182 SUPPLIES plan.yaml and its 50 machine-field-line task limit. DEC-120 reserves signature to Main; both artifacts remain pending despite operator pre-approval. Settled rework ruling: 1 round / 45 min; intake does not write the ledger.
- PRODUCT checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2187-review-pin-and-rework-rounds. Its docs/spec.md, docs/decisions.md and docs/architecture.md are absent; no contents or alternate-root guidance are invented. Settled grilling is the behavioral authority for this patch.
- Compare loaded documents, not commit identities or raw bytes; do not recursively discard status keys. Preserve legacy PLAN.md handling and existing refusal/write safety.

## Out of scope

- INV-6 (pin presence), the other INV checks, and `gh-sync.py` station writes themselves.
- `cycles_used` semantics and the rework-ruling hook comparison (`harness-hooks.ts` `parseSpend` reads the same figure and needs no change).
- Back-filling regate judgements into shipped features.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-11-21
