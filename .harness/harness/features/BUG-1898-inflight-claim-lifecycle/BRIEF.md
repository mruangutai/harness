# BRIEF — BUG-1898 inflight claim lifecycle

## Problem

The governed-agent claim lifecycle is split across dispatch, OMP run start, task-result delivery, lifecycle settlement, and digest validation, but those stages do not share one identity or one registry root. Five defects follow: the integration suite and digest hook can release unrelated live claims (A); a settled agent can wake without reclaiming before its next write (B); background batch results are paired to dispatch receipts by position and a bare dispatch name is prebound before OMP supplies the real child id (C); the extension registers lifecycle handling on `pi.on` although OMP publishes that event on `pi.events` (D); and dispatch and yield validation can consult different checkout registries (E). Together these defects make one-PM enforcement unreliable, disable the held-child yield gate, leak rows, and make cleanup capable of deleting another live agent's authority.

## Done when — by perspective

**operator** — I can run planning, build, validation, and a suite without one live governed agent releasing another agent's claim; an unclaimable child states the cause and retryability, can only return a BLOCKED digest, and no automatic or bulk cleanup guesses that a row is dead.

**orchestrator** — I can dispatch foreground or mixed background work, receive OMP's actual child ids, wake a settled agent, and trust that each governed run owns its exact claim before its first write and releases only its own claim on settlement.

**code maintainer** — I can follow one feature-root resolver and one id-keyed lifecycle from run start through result delivery and yield, with the existing one-PM invariant, legal concurrent claims for personas outside `SINGLE_FLIGHT_AGENTS`, and DEC-100 guard-crash pass-through preserved.

**reader** — I can inspect current-truth decision records, the one-time cutover procedure, red-first evidence, and a live OMP receipt that distinguish automated proof, inspection, and the operator-run merge gate.

## Success criteria

- SC-01 (operator): Red-first integration cases prove that a digest hook missing either the feature or exact harness agent id refuses before release, and that direct validation plus a suite run leave every unrelated seeded live claim intact, including one live claim for each governed persona and the occurrence-1 case where QA yields while PM remains live.
  verify: automated
  evidence: integration
- SC-02 (orchestrator): Unit cases prove that every governed run claims or binds its exact OMP agent id before its first tool write; a settled agent wake reclaims that id without hand binding; a claim refusal identifies its cause and whether retry can succeed, permits only a BLOCKED yield, and settlement releases only that run's claim.
  verify: automated
  evidence: unit
- SC-03 (code maintainer): Integration cases prove the unchanged one-PM invariant and the single feature-root/run-claim API: the dispatch guard and yield path resolve the same feature worktree; a competing PM refusal names the live holder and is retryable after settlement; an unreadable registry is a non-retryable operator condition; and a dispatch-guard crash retains DEC-100 pass-through behavior.
  verify: automated
  evidence: integration
- SC-04 (orchestrator): Unit cases prove that mixed governed and non-governed background results are matched by each result row's actual id rather than array position, dispatch receipts only roll back governed children that never started, and repeated names plus `Lead.Scope` and `Name-2` first writes neither cross-attach nor leave governed claims behind.
  verify: automated
  evidence: unit
- SC-05 (code maintainer): The OMP port integration check fails when the lifecycle marker exists on the wrong event bus and passes only when `task:subagent:lifecycle` is subscribed through `pi.events`.
  verify: automated
  evidence: integration
- SC-06 (orchestrator): Integration cases prove that digest validation reads the feature worktree registry, refuses a lead or orchestrator yield while an exact live child is held without releasing the parent, accepts the next yield after child settlement, and prints only exact targeted recovery commands.
  verify: automated
  evidence: integration
- SC-07 (operator): From an OMP session started inside the feature worktree, the operator runs the scripted live probe and records a PASS showing background delivery settlement, settled-agent wake and reclaim, mixed governed/non-governed batches with real ids, one suite run that preserves an unrelated live claim, and an empty feature registry at the end; this PASS is required before merge.
  verify: uat
- SC-08 (reader): At the pinned review SHA, inspection of `git show <review_sha>:.harness/harness/docs/DECISIONS.md`, its generated index, and the feature ship checklist confirms DEC-204 was rewritten in place to current truth under DEC-205, DEC-100 still makes guard crashes pass through while an unclaimable run self-refuses, the pre-load cutover enumerates every feature registry and releases only individually confirmed dead rows, and the first real post-merge feature records a complete plan/build/validate cycle without becoming a merge or ship gate.
  verify: inspection

## Verification gaps

- The configured `typecheck` kind has no executable runner for `.omp/extensions/harness-hooks.ts`. Focused Bun unit behavior, the semantic OMP port integration check, pinned-SHA inspection, and the live OMP UAT cover this surface; no typecheck result may be claimed.
- The null component and UI kinds do not match this non-UI lifecycle change.

## Constraints

- The baseline is commit `4e8c73c0` on branch `feat/BUG-1898-inflight-claim-lifecycle`.
- Preserve the one-PM rule exactly: at most one live `harness-pm` claim per feature. Personas outside `inflight_registry.SINGLE_FLIGHT_AGENTS` retain legal multi-flight behavior and may hold multiple concurrent live claims for the same feature; do not synthesize a persona-scoped single-flight rule.
- Claim at run start with the actual OMP agent id. A unique parent-bound dispatch receipt may be bound to that id, but a bare dispatch name is never an identity.
- Restart/revival feature recovery is exact-id only: when `before_agent_start` has no canonical feature marker, enumerate the owner-checkout registry and every registry in a linked worktree registered by `harness_boundary`, then match live claims by the actual OMP agent id. Exactly one match supplies both the feature and its registry root; zero matches, multiple matches, or any unreadable registry hold the run and permit only a cause-and-retryability BLOCKED yield. Never fall back to persona, dispatch name, cwd, or guessed session identity.
- DEC-100 SUPPLIES dispatch-guard crash pass-through. Do not turn a guard infrastructure failure into a dispatch refusal; the child run performs the authoritative claim and, if it cannot claim, refuses all tools except a BLOCKED yield with cause and retryability.
- DEC-174 BLOCKS team execution for `.omp/extensions/**`, `.claude/skills/harness/bin/**`, and every `tests/**` change; each such task is `main-session-direct`. DEC-179 SUPPLIES the explicit lane record.
- DEC-204 and DEC-218 SUPPLY the claim and lineage model. DEC-205 requires stale decision prose to be rewritten in place as current truth rather than amended with a contradictory addendum. DEC-231 SUPPLIES perspective-tagged criteria and DEC-232 SUPPLIES stable file anchors.
- Defect E is implemented only after defects C and D so validation consumes the corrected id and lifecycle semantics.
- The live OMP probe must use a real OMP process and credentials from a session whose working directory is this linked worktree. Its live mode cannot silently skip, substitute fixtures, or accept a dry-run receipt.
- Cutover is manual and happens once, before any live session loads the changed hook: enumerate every feature registry, identify known-dead rows, release them one by one with exact selectors, then enumerate again. Never release an ambiguous or live row and never add automatic or bulk cleanup.
- Approval remains pending until the operator signs the reviewed plan.

## Out of scope

- Issue 1919 and issue 1882.
- A mechanical retry limit or an automatic retry loop for refused claims.
- Automatic stale-row cleanup, release-all behavior, or inference that a row is dead.
- Clearing the currently live or leaked FEAT-65 rows during implementation; only the explicit merge cutover may act on rows that the operator has confirmed dead.
- Making the first real post-merge full plan/build/validate cycle a merge gate or ship gate; it is recorded follow-up evidence in that feature's own notes.

## Approval

status: pending
approved-by:
date:
