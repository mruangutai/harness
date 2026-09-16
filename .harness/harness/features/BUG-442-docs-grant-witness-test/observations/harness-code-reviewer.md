# Observations — harness-code-reviewer — BUG-442-docs-grant-witness-test

- 2026-09-07: relative `read`/`grep` paths silently resolved against the MAIN checkout, not this
  feature's worktree, even though bash cwd was set to the worktree explicitly. Main checkout's
  copy of `tests/integration/test-harness-yaml.py` was a stale 908-line pre-BUG-442 version with no
  `test_docs_domain_*` functions, and `grep` on the relative path returned zero matches for
  `test_docs_domain` with no error — looked exactly like a missing-registration defect until I
  re-ran both with the absolute worktree path and got the real, correct 1090-line file. Any
  reviewer working a worktree-hosted feature must anchor `read`/`grep` calls to the absolute
  worktree path, never a path relative to session cwd, when the main checkout and the worktree can
  disagree on file content.
- 2026-09-07: `code-grade.py --base 6d969ed3 --head 9b3fde7e` for BUG-442's diff happened to equal
  `merge-base(origin/main, 9b3fde7e)` exactly (confirmed via `git merge-base origin/main 9b3fde7e`
  == `6d969ed3`), even though the dispatch warned `merge-base(main, 9b3fde7e)` (LOCAL stale `main`)
  resolves to a much older `de97f4a2`. `origin/main` and local `main` disagreed sharply in this
  checkout; always resolve the default branch as `origin/main` for the grader, never the local
  branch ref, when the two might have diverged.
