# BRIEF — BUG-2141 Main-session orchestration for DEC-174

## Problem

For entirely main-session-direct features, the operator builds directly but must improvise lead dispatch and lifecycle ownership. Issue #2141 records that DEC-120's thin user-channel guidance does not explain this DEC-174 case, and dispatch-guard.py does not reject the engineering-lead detour.

## Done when — by perspective

**operator** — I can tell who owns the entire lifecycle of a directly built feature and which leads I may dispatch without improvising duties or creating unnecessary handoff notes.

**code maintainer** — I can change dispatch enforcement with regression evidence that distinguishes the prohibited detour from valid dispatches, using one existing classification policy.

## Success criteria

- SC-01 (operator): At the pinned review_sha, inspection via git show <review_sha>:<path> of DECISIONS.md DEC-174 and DEC-120 establishes main-session ownership of all orchestrator duties for entirely main-session-direct plans: run-start/close-run ledger, judgements, review pin, commit pen, and ship; permits product-lead plan team/panel/patch and validator-lead validate/fix, prohibits engineering-lead, references the zero-micro-management dispatch header, preserves the existing no-handoff exemption, and reconciles DEC-120 through a cross-reference. DECISIONS-INDEX.md is regenerated consistently.
  verify: inspection
- SC-02 (operator): At the pinned review_sha, git show <review_sha>:AGENTS.md under Organization and git show <review_sha>:.omp/commands/harness.md provide matching short DEC-174 exception pointers to ledger.md and the zero-micro-management header rule, without copying procedures or leaving their main-session prohibitions unconditional.
  verify: inspection
- SC-03 (code maintainer): Dedicated unit assertions execute the real dispatch guard: MAIN-SESSION to engineering-lead on a nonempty entirely main-session-direct plan exits 2 before a claim, names DEC-174 and the build-directly remedy; the same valid dispatch fixtures for orchestrator-originated, lead-originated, and non-direct plans retain prior outcomes. QA preserves fail-first evidence against pinned origin/main before production changes, demonstrating assertion failure for the missing refusal rather than fixture or import failure.
  verify: automated evidence: unit
- SC-04 (code maintainer): Integration assertions cover the prohibited dispatch and valid main-session product/validator dispatches, mixed/team plans, and shared-policy nonqualifying shapes; they retain existing unrelated dispatch outcomes. QA preserves fail-first evidence for the new prohibited-dispatch assertion against pinned origin/main. At review, the guard consumes handoff_policy's existing all-direct predicate rather than reproducing it.
  verify: automated evidence: integration

## Verification gaps

None for this bounded surface: unit and integration runners are active and match the named test directories. Contract prose is graded by pinned-content inspection (SC-01/SC-02), not claimed proven by tests. Excluded functional and unresolved component/UI kinds do not cover these Python and documentation changes. No user-only UAT is required. Intake checks do not prove SC-03/SC-04 or implementation readiness.

## Constraints

- DEC-174 BLOCKS governed engineering execution of enforcement scripts and their tests; T-01 is main-session-direct and all edits remain in this feature worktree.
- DEC-120 SUPPLIES the ordinary thin layer-0 channel; reconcile its DEC-174 exception by cross-reference, not by replacing the ordinary organization.
- DEC-179/DEC-182 SUPPLY declared routing and plan-merge authoring; both artifacts remain pending until explicit operator signature.
- DEC-225/DEC-228 SUPPLY the recorded patch mission: one task, no panel or goal-check, qa/review on the implemented diff.
- Issue #2141 settles the lifecycle and lead permissions. Preserve existing handoff_policy semantics and existing origin identification; do not invent a second all-direct policy.

## Out of scope

- Production changes or regression tests during this intake — implementation starts only after signature.
- UI, prototypes, panel and goal-check — settled patch lane has no such work.
- New handoff notes, expanded lead permissions, unrelated dispatch bypasses, and repository-wide organizational cleanup — outside issue #2141's bounded fix.

## Approval

status: pending
approved-by:
date:
