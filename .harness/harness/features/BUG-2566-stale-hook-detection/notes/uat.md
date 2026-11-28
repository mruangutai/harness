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

## Result: PASS (2026-11-27)

The main session ran the steps at the operator's request: two headless `omp -p --auto-approve` sessions started with their cwd in this worktree, extensions enabled. Transcripts are in `/tmp/bug2566-uat.3D9x/{a,b}`.

- **Session A, step 1.** Bash `printf '// BUG-2566 UAT probe\n' >> .omp/extensions/harness-hooks.ts`, run after the hook had loaded: exit 0.
- **Session A, `task`.** The `scout` dispatch was **refused**, verbatim: "Harness refuses this call: the Harness hook code this omp process loaded at 2026-11-28T01:11:54.656Z no longer matches .omp/extensions/harness-hooks.ts on disk; restart omp to load the current hooks."
- **Session A, read and edit.** The `read` of README.md and the `edit` of a scratch file outside the repository both **worked**.
- **Session B.** A fresh process, standing in for the restart, with the comment line still on disk. The same `task` dispatch was **not blocked**: status `completed`, output `ok`.
- **Cleanup.** The probe line was reverted with `git checkout -- .omp/extensions/harness-hooks.ts`.
