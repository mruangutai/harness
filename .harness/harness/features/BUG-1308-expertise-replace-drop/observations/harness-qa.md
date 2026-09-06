# Observations - harness-qa

- 2026-09-05: on a worktree-scoped dispatch, my first `edit` call against a bare relative path
  (`tests/integration/test-expertise-merge.py`) silently landed on the stale main-checkout copy at
  the identical relative path, not the worktree — caught only by running `git status --porcelain`
  in the main checkout afterward. Always pass the full absolute worktree path to every `edit`/`read`
  call on a worktree-scoped task, every time, not just the first.
- 2026-09-05: Independent re-run of T-02 acceptance (all 4 commands) all green — exit 0/0, 119+58 PASS/0 FAIL, worktree and main-checkout git status both clean of stray production/test edits. Could not reproduce prior session's claimed 'VERDICT PASS with host exit 1' contradiction; this run's own process behaved consistently with a clean PASS.
