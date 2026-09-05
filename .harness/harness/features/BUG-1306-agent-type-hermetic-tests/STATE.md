# STATE

## Current

- feature: BUG-1306-agent-type-hermetic-tests
- run: .harness/harness/features/BUG-1306-agent-type-hermetic-tests/runs/2026-09-05-06-validator/state.yaml
- squad: none
- status: awaiting-user

Plan phase COMPLETE. BRIEF.md and plan.yaml are approval-ready and both read `pending`;
only the main session signs. Station `plan`. `cycles_used` 1 of 8 (one lead-reported
send-back inside the panel-close run). Handoff at `notes/handoff-plan.md`.

The defect (issue #1306 / B-13): `tests/integration/test-plan-merge.py` inherits
`HARNESS_AGENT_TYPE` from the running agent's shell, and `plan-merge.py:1188`
`cmd_sign_approval` — the only production reader of that variable from the environment —
refuses at exit 10, so the suite is red for an agent and green for a human. Reproduced by
the orchestrator at HEAD `c369fb1`: governed env 14 `FAIL` lines / exit 1, clean env 0 / exit 0.

The plan is one task: pop the variable once at module import in that file only. The
adversarial panel ran both readers at cycle 0, raised one HIGH (SC-03 had no automated
gate), and that finding was CLOSED in T-01's `verify:` before signature — recorded in
plan.yaml `panel` as PF-8d2608761fd582d9e04a7fe844b2e0da, disposition `resolved`.

Log:

- 2026-09-05: feature instantiated; station `plan`.
- 2026-09-05: advisor consult settled scope and mechanism (D-01..D-04).
- 2026-09-05: BRIEF + plan drafted; goal-check PASS; SC-05 pinned to a merge-base diff.
- 2026-09-05: plan panel FAIL (one HIGH); finding closed, panel transcribed; plan phase ends.

## Open Questions

- Harness defect, blocking nobody here but affecting all six concurrent bug flows: a
  `notes/handoff-*.md` written from a worktree cannot use a pathless authority pointer
  (`plan-task:`, `brief-sc:`). `handoff_done_when.py:361` derives the feature dir from the
  note's worktree-stripped path joined to the MAIN checkout root, and no in-flight feature
  dir exists there — all nine live feature dirs are worktree-local. Worked around here with
  a path-carrying `approval:` pointer.
