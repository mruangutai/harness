# BRIEF — BUG-2253 Hook hang budget and gate fail lines

## Problem

Loaded hosts spuriously time out the digest integration suite's hook calls after three seconds. When an independent gate re-run fails, completion-ordered pooled output can bury the failing file above a passing last-20-line tail, leaving the operator without the useful diagnosis.

## Done when — by perspective

**operator** — I can identify every failing or mutated file when the gate rejects a QA PASS, without losing the existing diagnostic tail or changing refusal policy.

**code maintainer** — I can run the hook safety cases with load headroom while genuine hangs remain bounded, and regressions expose both defects before the fixes.

## Success criteria

- SC-01 (operator): A nonzero independent re-run reports every FAIL <file> and MUTATED <file> line before its existing last-20-line tail, including multiple entries buried above 20 passing lines; with no matching entries it retains the tail alone. RUN_UNIT_TESTS_BIN behavioral regressions must fail against the exact base gate and pass against the fixed gate; fallback and existing refusal status remain covered.
  verify: automated evidence: integration
- SC-02 (code maintainer): All six formerly three-second hook calls use the same 30-second hang budget. Executing each call observes 30 by default and follows two distinct temporary budget values; actual blocked subprocess execution through each helper times out within the selected budget plus bounded scheduling tolerance. A missing timeout must fail under an independent watchdog, not pass or hang the regression. The same new behavioral regressions must demonstrably fail against the exact base test subject and pass against the fixed subject; source-text assertions are insufficient.
  verify: automated evidence: integration

## Verification gaps

None for this Python integration surface: integration is active with a runnable command and detects tests/integration/**. No performance or loaded-host latency guarantee is claimed. Unresolved component, ui and typecheck runners do not cover this surface; excluded functional/eval kinds do not carry these SCs. Intake executes planning gates only, not regressions.

## Constraints

- DEC-174 BLOCKS team execution of validate-digest.py and its coupled tests: T-01 is main-session-direct by explicit operator exception to the patch default.
- DEC-225 SUPPLIES the bounded one-task patch intake, without panel or goal-check; DEC-182 SUPPLIES controlled YAML writes and the 50-machine-field-line task cap.
- Use HOOK_HANG_BUDGET_S = 30 at all six sites. Its rationale names registration FIFO, dangling symlink and 10,000-deep JSON, explains that blocking must fail rather than hang a test, and identifies load headroom rather than performance.
- Use the one-line heading "Failing or mutated files:" only when matching lines exist. Preserve exit codes and every fail-open/fail-closed rule.
- PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in this worktree; do not invent their contents or add documentation scope.
- Operator preapproved signature and a rework ruling of 1 round / 45 min; main session records them later. Both intake artifacts remain pending.

## Out of scope

- run_pool.py and run-unit-tests.py output formats: the gate reads them as they are.
- Which suite kinds the gate re-runs, the 1800s re-run timeout, and every other gate rule.
- Any other timeout in the test file, including the 30–120s subprocess timeouts later in the file: they are not these hang detectors.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-11-21
