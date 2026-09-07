# Observations - harness-qa

- 2026-09-07: BUG-1309 qa re-run — a main-session-direct task (T-13) whose intent names a mutation
  proof instead of a red-first claim leaves NO receipt to cite; running the proof myself in a
  disposable worktree under .claude/worktrees/ (git worktree add is denied elsewhere by
  bash-write-guard) converted an unverifiable claim into directly-measured evidence in ~15s.
  Cheaper than treating it as permanently "could not establish".
