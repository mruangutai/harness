# STATE

## Current

- feature: BUG-1306-agent-type-hermetic-tests
- run: .harness/harness/features/BUG-1306-agent-type-hermetic-tests/runs/2026-09-05-01-eng-simplify/state.yaml
- squad: none
- status: build-complete

Build phase COMPLETE. The one planned task T-01 is at station `done`; the feature station is
still `building` because the `review` transition is coupled to `gh-sync.py status <dir> review`
and this run was instructed not to touch GitHub. `review_sha` is pinned at the seam commit
`536afda3`, whose `plan.yaml` is byte-identical to disk. `cycles_used` is 1 of 8 — unchanged:
all three build segments returned PASS with zero send-backs. Handoff at `notes/handoff-build.md`.

T-01 landed one module-import statement in `tests/integration/test-plan-merge.py`:
`os.environ.pop("HARNESS_AGENT_TYPE", None)`, with its comment and one added sentence in
`run_verb`'s docstring. Both `case_1103_` bodies are byte-identical to the pre-fix blob
(region sha1 `0f5a679182…` on both sides; the two diff hunks sit at pre-image lines 34 and 141,
neither intersecting 1097-1140 — orchestrator-verified, not inferred from a green suite).

Evidence: T-01's `verify:` block prints `VERIFY-OK` at exit 0, both halves 291 PASS / 0 FAIL
(orchestrator-run, and independently by the builder and by qa). qa self-measured the pre-fix red
in an isolated checkout rather than inheriting it. The orchestrator additionally proved the suite
CAN report red at the SHIPPED file: pointing `PLAN_MERGE_BIN` at a wrapper that re-injects the
identity returns exit 1 with 17 failing checks, no repo file modified — which also explains the
pre/post check-count delta (278 → 290: a failed signature short-circuits its own case's later
assertions). SC-05 re-measured at the pin: the merge-base diff names the test file and this
feature's artifacts only, no `bin/` path.

Reconciled at this resume: run dir `2026-09-05-01-validator` (advisor consult, PASS) was orphaned
and is now recorded. `2026-09-05-05-validator` stays unrecorded ON PURPOSE — its own state.yaml
reads `status: superseded` with both steps noting the record moved to `2026-09-05-06-validator`,
which IS recorded, so recording it too would double-count one panel as two runs and inflate the
FAIL count `cycles_used` is checked against.

Log:

- 2026-09-05: feature instantiated; station `plan`.
- 2026-09-05: advisor consult settled scope and mechanism (D-01..D-04).
- 2026-09-05: BRIEF + plan drafted; goal-check PASS; SC-05 pinned to a merge-base diff.
- 2026-09-05: plan panel FAIL (one HIGH); finding closed, panel transcribed; plan phase ends.
- 2026-09-05: operator signed BRIEF and plan; station `building`.
- 2026-09-05: eng segment PASS (T-01, backend-dev, 0 send-backs); committed at 7e38d0ae.
- 2026-09-05: qa segment PASS — test_matrix gate green, `notes/qa-BUG-1306-integration.md`.
- 2026-09-05: simplify PASS — four angles, nothing applied; three residual notes.
- 2026-09-05: T-01 station `done`; build ends at the validate seam; pin moved to 536afda3.

## Open Questions

- Harness defect, blocking nobody here but affecting all six concurrent bug flows: a
  `notes/handoff-*.md` written from a worktree cannot use a pathless authority pointer
  (`plan-task:`, `brief-sc:`). `handoff_done_when.py:361` derives the feature dir from the
  note's worktree-stripped path joined to the MAIN checkout root, and no in-flight feature
  dir exists there — all nine live feature dirs are worktree-local. Re-measured this run: the
  Write of `notes/handoff-build.md` was refused for `brief-sc:SC-04`. Worked around again with
  path-carrying `approval:` pointers.
- Harness defect: `check-state.sh` INV-35 reports a VIOLATION on `plan.yaml:112` for an
  unquoted ` #1103`, but the value IS quoted — it is a multi-line single-quoted flow scalar
  opened on line 111, and `yaml.safe_load` returns the consequence text with `#1103` intact
  (measured). The check is line-based and cannot see the continuation. False positive; nothing
  to fix in the plan, and the plan is approval-gated anyway.
- Harness defect, non-blocking: the checkpoint-key allowlist rejects `applied_fixes`, a plain
  counter of the kind DEC-154 admits. Dropped from the simplify run's state.yaml (the digest
  keeps the fact) rather than argued; the allowlist may want the key.
- Harness defect, non-blocking: two of the builder's early edit-tool calls landed in the sibling
  MAIN checkout instead of the assigned worktree; the builder detected and reverted them.
  Independently confirmed clean by the orchestrator (`git -C <main> status --porcelain --
  tests bin .claude .agents` is empty). Only a shell-holding tier can confirm this, which argues
  for a guard.
- Harness defect, non-blocking: qa reported the Edit tool returning a current-file hash
  inconsistent with two fresh identical reads of the same file, in a worktree several agents
  run against concurrently. It cost qa the mutation check, which the orchestrator then took by
  a different route.
- Owner step deferred, not dropped: `check-state.sh` INV-26 is RED for this feature — the
  GitHub mirror has never run (`gh-sync.py open`), and the `review` station write is
  `gh-sync.py status <dir> review`. Both are GitHub acts this run was told not to perform.
