# Observations - harness-backend-dev

- 2026-09-07: T-03 c2, worktree session — passing a bracket-header path like `[tests/unit/test-factory-claim.py#77BA]` from a `read` result straight into `edit` without the worktree-absolute prefix silently wrote to the main checkout instead of the active worktree (edit tool succeeded, new tag returned, but `git status` in the worktree showed no change). Caught by checking `git status --porcelain` in BOTH the worktree and the main checkout immediately after every edit, not just the worktree. Confirms G-18: pass the full absolute worktree path on every edit call, and verify in both trees, not one.
- 2026-09-07: MF-1 fix on `_validate_plan_depends_on` (BUG-201): applying P-16's "extract from the
  start" as a retrofit worked cleanly here because the function had two orthogonal
  responsibilities (per-entry shape coercion vs. cross-task dangling-edge collection) that split
  along an existing loop boundary — the outer `for t in tasks` / inner `for entry in raw` nesting
  was already the seam. Extracting the inner-loop body (`_dangling_edges`) plus its own
  shape-check sub-step (`_depends_on_entries`) took cyclomatic 10/cognitive 14/abc 17.4 (grade 3)
  straight to two grade-4 helpers plus a grade-5 orchestrator, in one pass — no need for (b) from
  the dispatch's fallback plan. Confirms the harness-code-risk-grading skill's "give one loop to
  one function" habit generalizes to nested two-level loops with a guard in the outer one.
- 2026-09-07: MF-1 SC-04 follow-up (c2) — a docstring can trip a literal-string grep criterion just
  as effectively as a second `def`; reworded two docstrings in `_depends_on_entries`/`_dangling_edges`
  (harness_yaml.py:395,415) to say "its caller" instead of naming `_validate_plan_depends_on`, closing
  the prose-vs-code adjudication the lead flagged. Zero executable lines touched; code-grade metrics
  and all three targeted suites (12/12, 16/16, test-plan-merge full green) confirmed byte-identical.
