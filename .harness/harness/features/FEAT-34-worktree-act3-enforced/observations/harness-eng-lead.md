# Observations — harness-eng-lead — FEAT-34-worktree-act3-enforced

- 2026-08-24: I passed `model: sonnet` on the first backend-dev dispatch and `dispatch-guard.sh`
  blocked it (DEC-152/155). My own G-16 names this exact habit error. The guard caught what my
  Expertise had already told me to catch — the lesson is not "add a rule", it is that a rule I
  hold does not fire unless I audit the call's parameters before sending.
- 2026-08-24: I overstated a hazard's severity in a dispatch and could not correct it mid-flight
  (leads hold no SendMessage in this run). I told backend-dev the post-fix fixture hazard could
  "delete real work". Re-derived after sending: `_sweep_env` sets `CLAUDE_PROJECT_DIR` to the
  fixture and `feature-worktree.py remove` resolves through `factory_config.harness_root()`,
  which prefers it, so GATE 1 would likely REFUSE a real removal. The real blast radius is
  `gh-sync.py cmd_ship` writing `status: Done` into REAL `feature.json` files
  (`gh-sync.py:1058-1065`) — state corruption, not deletion. The mandated remedy (assert the
  resolved root is inside the fixture) is unchanged by the correction, which is the only reason
  the overstatement was not load-bearing.
- 2026-08-24: `plan.yaml:256-257` states `classify` runs `git worktree list` with `cwd=root`.
  That is what makes the T-03 root-derivation change reach every fixture in
  `test-post-merge-sweep.py`, none of which the plan's T-04 case list anticipates.
- 2026-08-24: the setup step T-13 must grade is a three-step SEQUENCE in
  `harness-init/SKILL.md:62-91` whose decisive branch (step 3, "STOP and ask") is PROSE with no
  command. Only steps 1 and 2 have literal command strings, so "assert the command runs verbatim
  from SKILL.md" can only pin those two — the reporting behaviour of case (d) falls out of the
  ORDER (step 1 before step 2), not out of any single command.
