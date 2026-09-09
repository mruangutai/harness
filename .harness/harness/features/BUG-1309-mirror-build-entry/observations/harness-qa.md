# Observations - harness-qa

- 2026-09-07: BUG-1309 qa re-run — a main-session-direct task (T-13) whose intent names a mutation
  proof instead of a red-first claim leaves NO receipt to cite; running the proof myself in a
  disposable worktree under .claude/worktrees/ (git worktree add is denied elsewhere by
  bash-write-guard) converted an unverifiable claim into directly-measured evidence in ~15s.
  Cheaper than treating it as permanently "could not establish".
- 2026-09-08 (BUG-1309 c17): dispatch framed T-05 as `change_type: bugfix`; `plan.yaml` records `feature`. Floor was unaffected here (`feature`'s `always: [unit, integration]` matches what `bugfix`'s conditional legs would also have obligated), but always re-derive change_type from plan.yaml per G-11 — dispatch framing is inherited, not measured.
- 2026-09-08 (BUG-1309 c17): to discriminate a hook-shell-wrapped Python gate (`merge-gate.sh` execs `merge-gate.py` from its own dirname) against a pre-change commit, copy the whole bin/ directory to a scratch path and overwrite only the one changed module with `git show <old-sha>:<path>` — the shell wrapper's sibling-relative exec then picks up the old logic while `harness_boundary.resolve_root` still honours `HARNESS_PROJECT_DIR` from the test fixture. Cheaper than reconstructing a bespoke fixture harness from scratch.
