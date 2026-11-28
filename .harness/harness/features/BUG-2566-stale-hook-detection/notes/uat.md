# BUG-2566 UAT: SC-10

Run by the operator after T-01 lands, in this feature's worktree.

1. Start omp with its cwd in `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2566-stale-hook-detection`.
2. Add one comment line to that worktree's `.omp/extensions/harness-hooks.ts`.
3. Dispatch any `task`.
   - **Expect:** it is refused with one line ending "restart omp to load the current hooks."
4. Run a `read`, and an `edit` of any file.
   - **Expect:** both work.
5. Restart omp in the same worktree and dispatch the same `task`.
   - **Expect:** it proceeds.
6. Remove the comment line, or `git checkout` the file.

Record the result here: pass or fail, the date, and the refusal text seen.
