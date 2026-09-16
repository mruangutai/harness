# T-01 fix receipt — c1

## Result

PASS — `project` now delegates active-phase selection and parent/source placement without changing its public projection contract; `_inv26_fixture` delegates fixture construction by concern while retaining all scenarios. Code commit: `15fd356ff76e31c7b7ca4978c25819834c0ffe54`.

## Hypothesis and red evidence

Hypothesis: the two reviewed functions combine independent construction/projection concerns, inflating mechanical complexity without requiring different lifecycle behavior. Falsifier: splitting those concerns would leave either named function below its required grade. Before edits, the mandated grader at direct-repair tip `37d846da62bd2e1d88a5406956482398d17bdca5` reported `project`: grade 3, cyclomatic 9, cognitive 10, ABC 16.3 (CR-01), and `_inv26_fixture`: grade 1, cyclomatic 14, cognitive 21, ABC 47.9 (CR-02); exit 1.

## Criterion-specific fail-first record

| SC | Exact automated test | Actual pre-fix evidence |
| --- | --- | --- |
| SC-01 | `tests/integration/test-station-argument-spelling.py:case_lifecycle_checkpoint_order_and_negative_controls` | `notes/receipt-main-direct-validation-c1.md:14`: run against `6e7440e8^` returned 11 violations, including dynamic RESUME/open/status ordering. |
| SC-02 | `tests/integration/test-station-argument-spelling.py:case_lifecycle_checkpoint_order_and_negative_controls` | `notes/receipt-main-direct-validation-c1.md:14`: same pre-fix run reported missing Build-before-dispatch/complete projection contract. |
| SC-03 | `tests/integration/test-station-argument-spelling.py:case_lifecycle_checkpoint_order_and_negative_controls` | `notes/receipt-main-direct-validation-c1.md:14`: same pre-fix run reported missing validation Review-before-dispatch contract. |
| SC-04 | `tests/integration/test-station-argument-spelling.py:case_lifecycle_checkpoint_order_and_negative_controls` | `notes/receipt-main-direct-validation-c1.md:14`: same pre-fix run reported must-fix Building-before-dispatch violation. |
| SC-05 | `tests/integration/test-station-argument-spelling.py:case_lifecycle_checkpoint_order_and_negative_controls` | `notes/receipt-main-direct-validation-c1.md:14`: same pre-fix run reported returned-fix Review-boundary violation. |
| SC-06 | `tests/integration/test-plan-merge.py:case_bug1699_approval_reset_classifies_active_station` | `notes/receipt-main-direct-validation-c1.md:13`: current focused cases against `0d56eb7b^` produced 24 failures, including no Plan reset/resume receipt. |
| SC-07 | `tests/integration/test-plan-merge.py:case_bug1699_reapproval_restores_recorded_station` | `notes/receipt-main-direct-validation-c1.md:13`: same pre-fix run failed Ready/Building/Review restoration. |
| SC-08 | `tests/integration/test-gh-sync-ship.py` all-card Done assertions | `notes/receipt-harness-backend-dev-T-01-c0.md:9-15`: the pre-production T-01 gate run exited 1 on the old task-local projection, before the signed all-card suite passed. |
| SC-10 | `tests/integration/test-gh-sync-record.py` local-first/continuation assertions; `tests/integration/test-plan-merge.py:case_bug1699_plan_mutation_makes_no_github_call` | `notes/receipt-main-direct-validation-c1.md:13,16`: pre-fix reset run failed, and the fake-gh negative control demonstrates the required network boundary. |
| SC-11 | `tests/unit/test-gh-board.py` active-phase projection assertions | `notes/receipt-harness-backend-dev-T-01-c0.md:9-15`: old projection failed all four active phases with mixed task-local stations. |
| SC-12 | `tests/integration/test-gh-sync-record.py` abandoned-card projection assertions | `notes/receipt-harness-backend-dev-T-01-c0.md:9-15`: actual pre-production record-run failure included incomplete active projection; current focused runner preserves abandoned exclusion. |
| SC-13 | `tests/integration/test-gh-sync-ship.py` no-direct-close assertions | `notes/receipt-harness-backend-dev-T-01-c0.md:9-15`: actual pre-production T-01 gate failure before the signed ship behavior passed. |
| SC-14 | `tests/integration/test-gh-sync-ship.py` open-child hold assertions | `notes/receipt-harness-backend-dev-T-01-c0.md:9-15`: actual pre-production T-01 gate failure before the signed hold behavior passed. |

## Verification

Signed T-01 command, executed exactly after the refactor:

```sh
python3 tests/unit/test-gh-board.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-check-state-inv26.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-ship.py && python3 tests/integration/test-gh-sync-abandon.py
```

Result: exit 0; unit runner ended `all pass`; every integration runner ended `ALL PASSED`.

Mandated self-check, executed exactly:

```sh
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/code-grade.py --base "$(git merge-base origin/main HEAD)" --head HEAD
```

Result: `PASSING: 54`; all changed refactor helpers meet their bars. A pre-existing unrelated grade-2 `case_lifecycle_checkpoint_order_and_negative_controls` remains reported as `REASON REQUIRED` (no high finding). Direct path grading measured `project` grade 4 (cyclomatic 3, cognitive 1, ABC 9.4; bar 4) and `_inv26_fixture` grade 4 (cyclomatic 2, cognitive 3, ABC 9.8; bar 3).

## Changed paths

- `.claude/skills/harness/bin/gh_board.py`
- `tests/integration/test-check-state-inv26.py`
- `.harness/harness/features/BUG-1699-lifecycle-cards/notes/receipt-harness-backend-dev-fix-c1.md`
