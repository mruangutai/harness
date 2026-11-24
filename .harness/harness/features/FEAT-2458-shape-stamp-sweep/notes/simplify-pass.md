# FEAT-2458 SIMPLIFY pass (main session, DEC-174) — 2026-11-24

Diff: 322b12b0..1d8e8446 (T-01 35f67a65, T-02 1d8e8446).

- Reuse: classify_feature builds only on existing private helpers (_resolve_default_branch, _landed_dir_names, _fleet_segments, _landed_classification); no new landed rule. The sweep calls worktree_terminal.repo_arg_for_segment; its duplicate is deleted with its registry key and inventory row.
- Simplification: no new constant, no new parameterised reader. One try/except UnicodeDecodeError at the cat-file seam.
- Efficiency: classify_feature walks fleet segments only when the id is not under harness; one ls-tree per segment. The sweep lists `.harness` once.
- Altitude: the sweep decides from klass alone (SC-06). Only OSError is caught in the hook; the broad-catch ceiling stays at zero.
Findings: none.

Verify (HARNESS_AGENT_TYPE unset), all exit 0 at 1d8e8446: test-post-merge-sweep, test-check-plan-routes, test-worktree-terminal, test-checker-structure-locks, unit test-broad-catch-census, unit test-no-distribution, check-plan-routes --canonical-reader-audit; T-01 AST check; T-02 greps. RED observed first: T-01 11 rows (AttributeError), T-02 rows (2)(3)(4)(7)(8).
Note: git stash cleared the sparse skip-worktree bits mid-build; restored with update-index --skip-worktree; worktree-state --verify converged.
