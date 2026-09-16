# Observations - harness-documentor

- 2026-09-05: BUG-1286 T-05: hunk headers with repo-relative paths landed both DECISIONS edits in the MAIN checkout instead of the dispatched worktree; snapshot tags matched because the copies were byte-identical at the same commit, so nothing warned. Caught only when the worktree regeneration "reverted" my ruling. Use absolute worktree paths in every hunk header when a worktree is in play (G-18 confirmed again).
- 2026-09-05: BUG-1286 T-05: gen-decisions-index.py preserves only the text right of " :: "; it recomputed DEC-213 tags (dispatch,hooks -> state,skills) and added refs: DEC-189 from the longer body. Report generated-side churn as an effect of the body edit, not as a hand edit.
