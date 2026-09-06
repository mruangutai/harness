# STATE

## Current

- feature: BUG-1305-run-state-clobber
- run: .harness/harness/features/BUG-1305-run-state-clobber/runs/review-c5-validator/state.yaml
- squad: none
- status: awaiting-user
- station: review, ship-ready; review_sha 252a18a9; cycles 17/18 with 18 reserved and unspent; runs 30 against an informational 20
- gates: SC-07 met and every other live criterion carried on a byte-unchanged .claude/skills; qa scoped review PASS with must_fix empty; test_matrix PASS; SIMPLIFY PASS; code grade exit 0; suites and state checker green at the seam
- briefing: notes/ship-review-2026-09-05-final.md; handoff: notes/handoff-validate.md

## Open Questions

- Operator: the ship decision, and which of briefing rows B-1 to B-16 to strike. Unstruck rows become backlog issues on acceptance; SEC-01 is already filed as #1376.
- Main session: remove the four surviving scratch worktrees named in the briefing (qa-c2-c369, qa-c2-dc0, qa-c2-e77, qa-c2-mutate) and prune, before INV-29 sees them. Never a subagent's act.
- Main session: two run digests exist only inline in their leads' returns (review-c5-validator, goalcheck-build-c5-product) because the persona-keyed claim defect refused those writes. Both were assessed at source by their leads; the defect is briefing row B-10.
