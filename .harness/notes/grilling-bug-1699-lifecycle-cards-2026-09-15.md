# Grilling — BUG-1699 lifecycle cards — 2026-09-15

## Destination
Every recorded source issue, parent, and task card truthfully follows the feature through Plan, Ready, Building, Review, and Done, including approval-reset amendments and rework. Existing active features are reconciled once when the repair lands.

## Mission
mission: plan
reason: The change rewrites the public lifecycle contract across signature, build, validation, rework, amendment, ship, and one-time reconciliation.
confirmed-by: operator

## Settled
- Should issue #1699's confirmed destination govern unchanged? → Yes.
- After signature, which cards enter Ready? → Every recorded source issue, parent, and task card.
- What happens at build, validation, must-fix rework, and ship? → Every recorded card moves respectively to Building, Review, Building, and Done; the next validation returns all to Review.
- What happens when an amendment resets approval? → Every recorded card returns to Plan; reapproval restores Ready, Building, or Review from whether work had started and which phase was interrupted.
- Does this repair existing drift? → Yes, reconcile existing active features once when the repair lands.
- Which existing contracts remain? → GitHub synchronization stays best-effort and outbound; abandonment behavior and the six-column Backlog, Plan, Ready, Building, Review, Done vocabulary stay unchanged.
- Which mission applies? → Plan.

## Not yet specified
- None.

## Out of scope
- Adding, renaming, or aliasing lifecycle stations.
- Making GitHub synchronization gate Harness execution or changing its best-effort failure posture.
- Changing abandonment, detach, issue-closure, or open-child behavior.
- Making GitHub an inbound source for approval-gated state.

## Facts I verified (so pm does not re-derive them)
- `gh-sync.py status ready` currently moves only recorded task sub-issues; `status review` moves the parent and task sub-issues; `start-task` moves one task and derives the parent — inspected at `c280792f2719145a1a41fb3df12075fdb3eebd40`.
- Current `gh-sync.py` does not state an all-recorded-card transition for Ready, Building, or Plan rollback — inspected at `c280792f2719145a1a41fb3df12075fdb3eebd40`.
- DEC-138 makes GitHub an outbound, orchestrator-executed, non-gating mirror; DEC-146 keeps board writes best-effort.
- DEC-203 makes card station authoritative, requires Ship to move every recorded card to Done, preserves the open-child rule, and fixes the six-station vocabulary.
- DEC-220 currently opens the mirror at Build entry after approval and records `github.build_entry`; the new visible Ready phase must reconcile that existing receipt contract rather than bypass it.
- No existing feature directory or worktree matching issue 1699 exists at this baseline.
