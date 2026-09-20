# QA gate — FEAT-61 control-plane consolidation (c1)

## BLUF

**FAIL:** all five signed verify clauses exited 0 at `57ef1c5739f55dd67d9daffd5da69d7d7b980ea7`, grading exactly `066638e8acf68b47e74637006a01c8823cff939c..57ef1c5739f55dd67d9daffd5da69d7d7b980ea7`; however, durable history contains no captured pre-fix failing run for SC-01 through SC-06. The divergence ledger's unmeasured “Red-first test” labels are not fail-first receipts. SC-07 has a current controlled-mutation failure proof.

## Phase 1 coverage expectations and matrix

From BRIEF/plan before source inspection: SC-02 needs unit coverage; SC-01, SC-03, SC-05, SC-06, and SC-07 need integration coverage; SC-04 needs both unit and public-validator integration coverage. The three `code` tasks span shared modules and integration routes, so unit + integration are required; T-04 changes the `gates` container shape, which triggers `config.when.touches_config_shape -> integration` (`.harness/harness.json:226-233`). No UI, component, eval, or locally-run detect surface changed. **matrix_ok: false** solely because the mandatory fail-first evidence floor is unsatisfied, not because a required command failed.

| kind | state | coverage / result |
|---|---|---|
| unit | satisfied | T-01, T-02, and T-04 named seven unit scripts; all passed. |
| integration | satisfied | T-02, T-03, T-04, and T-05 named eleven integration scripts; all passed. |
| component | not applicable | No frontend/component surface in the reviewed diff. |
| ui | not applicable | No user interaction surface in the reviewed diff. |
| eval | not applicable | No `ai_behavior` task or eval surface. |

## Exact signed verification outcomes

All commands ran from the feature worktree and exited 0:

1. `python3 tests/unit/test-factory-config.py && python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/unit/test-harness-boundary.py`
2. `python3 tests/integration/test-plan-merge.py && python3 tests/integration/test-board-lifecycle.py && python3 tests/integration/test-worktree-terminal.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/unit/test-gh-board.py && python3 tests/unit/test-handoff-done-when.py`
3. `python3 tests/integration/test-check-state-feat59.py && python3 tests/integration/test-check-domain.py && python3 tests/integration/test-check-domain-worktree.py && python3 tests/integration/test-bash-write-guard.py`
4. `python3 tests/unit/test-gate-policy.py && python3 tests/integration/test-validate-digest.py`
5. `python3 tests/integration/test-check-plan-routes.py && .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`

## SC evidence and fail-first audit

| SC | current covering test | durable fail-first evidence |
|---|---|---|
| SC-01 | `tests/integration/test-check-plan-routes.py:2505`; fixture receipt named at `notes/build-divergences.md:8-11` | **MISSING.** Ledger asserts byte identity and calls divergences red-first, but records neither a red command/output nor a pre-fix SHA. |
| SC-02 | `tests/unit/test-factory-config.py:541-601` | **MISSING.** No receipt/history records this test failing before the station-table implementation. |
| SC-03 | `tests/integration/test-plan-merge.py:3342-3389`; baseline corpus receipt `notes/research-FEAT-61-control-plane-consolidation.md:14-16` | **MISSING.** Ledger labels the cases red-first (`notes/build-divergences.md:17-22`) without a captured red run. |
| SC-04 | `tests/unit/test-gate-policy.py:63-82`; `tests/integration/test-validate-digest.py:3749-3764` | **MISSING.** Ledger labels tests red-first (`notes/build-divergences.md:42-46`) without a captured red run. |
| SC-05 | `tests/integration/test-check-domain-worktree.py:712-814`; `tests/integration/test-bash-write-guard.py:995-1108` | **MISSING.** The tests claim prior receipts at those lines, but no durable receipt/output is present. |
| SC-06 | `tests/unit/test-artifact-accessors.py`; `tests/unit/test-harness-boundary.py`; `tests/integration/test-check-state-feat59.py` case 61 and `tests/integration/test-check-domain.py` run-schema cases | **MISSING.** `notes/build-divergences.md:29-38` names red-first tests but does not capture a failure. |
| SC-07 | `tests/integration/test-check-plan-routes.py:2450-2475` | **SATISFIED:** T-05's passing output includes `feat61_lock_station_literal_mutant_fails_for_its_own_finding` and `feat61_lock_second_loader_mutant_fails_for_its_own_finding`; each is a controlled mutation that makes its named lock fail. |
| SC-08 | inspection only; deliberately not automated | n/a |

## Finding

- **high — harness-qa — substance — T-01/T-02/T-03/T-04/T-05:** The gate cannot establish SC-01–SC-06 fail-first compliance. The only range commits touching the relevant tests are `2967b204`, `1ed20fa1`, and `40294807`, and their messages contain no red receipt; the ledger's assertion of red-first is not evidence. A future change could make the newly added tests mirror the implementation and still pass, while the gate reports success. **Remedy:** attach durable, per-SC captured failing-run receipts (or reproduce each relevant pre-fix state in disposable worktrees and retain the output/receipt with the baseline SHA) before regating.

## Nonblocking observations

- `notes/build-divergences.md:38` records an accepted malformed-list schema output divergence; it is explicitly ruled and exercised, so no separate QA finding.
- No coverage gaps other than the six missing fail-first receipts.
