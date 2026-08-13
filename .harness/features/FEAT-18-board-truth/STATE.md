# STATE

## Current

- feature: FEAT-18-board-truth
- run: .harness/features/FEAT-18-board-truth/runs/t01-t05-eng/state.yaml
- squad: eng
- status: building

Build phase open. Both artifacts read `approved` (Mike Ruangutai, 2026-08-13), so the gate passed.
The mirror is live: milestone #10, parent #326, sub-issues #327–#332 for T-01…T-06. Build branch
`feat/FEAT-18-board-truth` created the ordinary way — `git checkout -b`, D-08 struck, no
`gh issue develop`. Branched from `e61e081`.

Sequencing: the six tasks split three team / three main-session-direct under DEC-174. In flight now
is the eng segment for **T-01** (task-status enum in `check-plan-routes.py`) and **T-05** (delete
`branch-create-gate.sh`'s dormant board-flip block), both `depends_on: []`, both `harness-backend-dev`
by the plan's resolved lanes. **T-02** (`gh_board.py`) is unblocked but is a carve-out by content and
must go back to the main session, not to a squad. After T-02: T-03 (team), then T-04 and T-06
(main-session-direct) together.

## Open Questions

- Q1 and Q3 were both answered at signature and are recorded in `BRIEF.md`'s `## Approval` block.
  D-05's three board keys stay in `harness.json` and their placement is knowingly temporary (`#206`
  moves `github`, `test_matrix` and `test_kinds` together). Do not reopen either.
- Q2 was overtaken by the 2026-08-13 revision and is not in force.
