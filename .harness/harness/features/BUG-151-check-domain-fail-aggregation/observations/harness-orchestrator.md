# Observations - harness-orchestrator

- 2026-09-07: BUG-151. A handoff note written INSIDE a worktree cannot use `plan-task:` or
  `brief-sc:` authorities. handoff_done_when.py relativises the note against the worktree
  (FEATURE_RE anchors on `^.harness/`) but resolves `root` to the MAIN checkout, so
  feature_dir lands at <main>/.harness/harness/features/<FEAT>, which does not exist.
  `approval:` and `finding:` take an explicit path and DO work if spelled relative to the
  main root — i.e. beginning `.claude/worktrees/<repo>/<FEAT>/`. Absolute paths are refused
  outright ("is absolute").
- 2026-09-07: BUG-151. teams/plan-panel.yaml declares two readers; check-state.sh INV-32
  (line 534) expects three, including `goalcheck`. The goalcheck reader row has to be
  transcribed into panel.readers by hand after the product segment, or the plan goes `bad`
  the moment it is signed. Found only because pm read the invariant rather than the team file.
- 2026-09-07: BUG-151. feature-json-merge.py append-run REFUSES an entry without a non-empty
  `agent` (FEAT-31 SC-07) and the refusal names runs[0], not the entry you passed — it
  re-validates the whole array. The templates/feature.json example does not show the key.
