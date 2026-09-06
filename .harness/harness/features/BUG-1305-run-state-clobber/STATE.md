# STATE

## Current

- feature: BUG-1305-run-state-clobber
- run: .harness/harness/features/BUG-1305-run-state-clobber/runs/qa-c1-validator/state.yaml
- squad: validator
- status: in-flight
- station: review; all eight live tasks recorded done; review_sha pinned at the seam commit
- gates so far: qa test_matrix PASS, SIMPLIFY PASS, SC-01 re-gate MET (cycle 10), code-grade exit 0 with 50 passing records after the cycle-11 refactor

## Open Questions

- Main session: INV-26 reports no mirrored issues; gh-sync.py open has not run for this feature.
- Main session: the scratch worktree .claude/worktrees/harness/qa-regate-sc01-baseline-c10 (detached 592e88dc) still stands and INV-29 will notice it. Removal is not a subagent's act.
- Harness defect, twice observed: per-persona worktree claims are cross-feature exclusive, so a lead dispatched against BUG-1305 was refused writes into its own BUG-1305 run directory while holding claims on FEAT-55 and BUG-1308. The qa collated digest could not be persisted; its evidence is durable at notes/qa-testmatrix-c1.md.
