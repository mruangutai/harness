# BUG-1699 main-session direct remediation receipt

Date: 2026-09-16
Pinned validation: `2026-09-16-07-validate-validator`
Operator rulings: `notes/answers-validation-c0-2026-09-16.md`

## Scope

This receipt covers the operator-authorized direct fixes for QA-01, QA-02, QA-04, the OMP terminal-yield runtime defect that blocked canonical goalcheck, and fail-first evidence for the main-session-direct T-02, T-03, and T-04 slices. T-01 complexity and its remaining criterion-specific evidence stay with the orchestrator's owning-developer fix cycle.

## Fail-first evidence

- **T-02 / SC-06, SC-07, SC-10:** the current focused BUG-1699 resume cases were executed against `0d56eb7b^`'s `plan-merge.py`. They produced 24 failing assertions: active task mutations did not move the feature to Plan, did not record `resume_station`, emitted no post-reset receipt, reapproval emitted no stored station, new ready work did not recompute Building, and terminal features were not protected by the new behavior. The same focused cases pass against the task commit and current tip.
- **T-03 / SC-01 through SC-07, SC-10:** the current lifecycle ordering checker was evaluated against the eight governed files at `6e7440e8^`. It returned 11 violations, including missing dynamic RESUME validation, signature open/status order, approval-reset gating, Build-before-dispatch, fix Building/Review bracketing, and complete projection wording. The current checker passes and its eight mutation controls each redden when the corresponding caller/order contract is broken.
- **T-04 / SC-09, SC-10, SC-12:** the current board lifecycle suite was executed against `c67347cb^`'s `board_lifecycle.py` with the current dependency path. It returned 10 failures, including all-card BUG-1699 dry-run/apply, bounded-snapshot, continuation/idempotence, and terminal Done exemption scenarios. The current suite passes in full.
- **SC-10 no-network guard:** the plan-mutation scenario first invokes the same fake `gh` boundary as a negative control and observes exit 97 plus a call-log write. It then clears the log, performs the real local `delete-items` mutation, observes `APPROVAL-RESET`, and proves no `gh` call occurred.
- **OMP goalcheck yield:** before the hook repair, `bun test tests/unit/omp-hooks.test.ts` reported 73 pass / 2 fail: top-level `{data: ...}` was normalized incorrectly and the task lifecycle hook rejected that real OMP payload as empty. This reproduces the canonical goalcheck agents' observed terminal-yield failure.
- **QA-01 and QA-02:** their failing-before state is the pinned validator digest: the inherited feature-record unit case saw `undefined` instead of explicit `null`, and factory case L expected a STATUS mismatch from a terminal `done` fixture that the BUG-1699 active-only policy intentionally excludes.

## Changes

- `.omp/extensions/harness-hooks.ts`: accept current OMP top-level `{data|error}` yield envelopes while retaining legacy `result` compatibility and fallback handling for truly empty yields.
- `tests/unit/omp-hooks.test.ts`: prove top-level data preservation and exercise the real task-hook envelope; update the direct `feature-record.py run-end` fixture to pass its required `--cycles-used 0` argument.
- `tests/integration/test-factory-integration.py`: make case L an active `review` versus `backlog` mismatch, so it tests the intended STATUS contract instead of a terminal exemption.
- `tests/integration/test-plan-merge.py`: add execution-bound no-network proof and a powered negative control.

## Green verification

- `bun test tests/unit/omp-hooks.test.ts` — 75 pass, 0 fail.
- `python3 tests/integration/test-factory-integration.py` — 131/131 checks passed.
- `python3 tests/integration/test-plan-merge.py` — passed, including the no-network negative control and no-call assertion.
- `python3 tests/integration/test-board-lifecycle.py` — all checks passed.
- `python3 tests/integration/test-station-argument-spelling.py` — passed, including all eight lifecycle negative controls.
- `python3 tests/integration/test-sync-command-adapters.py` — 15/15 cases passed.
- `python3 .claude/skills/harness/bin/sync-command-adapters.py --check` — exit 0.
