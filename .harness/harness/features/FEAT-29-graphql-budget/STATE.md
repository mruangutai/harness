# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight
- squad: none
- status: Ready — awaiting layer-0 batch A

Both approval gates pass. Branch `feat/FEAT-29-graphql-budget` created from `3920513`, `resolved_at`
re-pinned to it, mirror opened (milestone #18, sub-issues #579–#587 under adopted parent #571, no
orphan created). `check-plan-routes.py` reads `0 violation(s)`, exit 0.

**The build is deliberately NOT dispatched.** T-02 rewires `board_stations`, which INV-26 calls, so
T-02 landing in the working tree destroys the 490–507 red state that SC-01 and SC-04 are graded
against. T-06 captures that baseline and is `main-session-direct`. Batch A —
`notes/layer0-segments-FEAT-29.md`, T-05 then T-06 — must be executed by the main session before the
eng segment starts.

Next on batch A's return: dispatch `build` team to eng-lead with T-01, T-02, T-03, T-04; then the qa
segment, SIMPLIFY, pin `review_sha` at the branch tip, panel; then hand back batch B (T-09, T-07,
T-08).

Budget: GraphQL read 3673/5000 at 09:59 local 2026-08-19 — 1,327 left, window resets 10:45:06.
`gh-sync.py open` cost 40 points (3676 → 3716). 1 cycle used of 10; 1 run of 20.

## Open Questions

- None blocking a decision. Q1 (board pruning) is RULED at `BRIEF.md:141` — code fix only, no prune,
  no archive. The task set stands at nine.
