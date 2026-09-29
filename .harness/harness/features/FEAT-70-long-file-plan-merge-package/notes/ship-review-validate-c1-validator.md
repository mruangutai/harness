# Ship review — FEAT-70 long-file plan-merge package

FEAT-70 is ready for the operator's ship decision. Validation at review SHA `01af5a511f356d76ee91ced8922e2d53e71479e3` passed the required 43-script unit and 72-script integration matrix, closed both cycle-0 defects, and graded SC-01 through SC-03 met. The immutable implementation pin is `73ba9dceee11253bbf57b7ca1b36323c81d83891`.

## Definition of done

| Perspective | Signed outcome | Verdict | Criteria and evidence |
|---|---|---|---|
| operator | The unchanged hyphenated entry preserves every pre-existing command's exit status, stdout, stderr, and written bytes; the two-entry block-scalar amendment succeeds atomically; clean detached receipts normalize only checkout roots. | met | SC-02: 107/107 cases per side, 293 aligned observations, 6,518 scratch commands per side, and exactly seven advisor-accepted records (`runs/validate-c1-validator/digest.md`). SC-03: the retained six-assertion block-scalar regression and baseline-red/pin-green receipt pass (`runs/validate-c1-validator/digest.md`). |
| code maintainer | The entry is thin over the exact ten-module `plan_merge/` package, keeps `signed_task_hash` reachable, moves tests and reader identities to package owners, and holds every entry/package function at grade 4 or better. | met | SC-01: fresh immutable-pin grading covers 237 functions, with 106 at grade 5 and 131 at grade 4 (`runs/validate-c1-validator/digest.md`). |

## Phase record

- Plan: the two-task specification passed its panel and goal-check, then received operator approval (`runs/plan-product/digest.md`).
- Validation c0: SC-01..SC-03 passed, but the canonical grader found `feat70-grade-assert.py:bodies` at grade 3 and the integration matrix exposed fixtures that copied bin entries without sibling packages (`runs/validate-validator/digest.md`).
- Fix c0: `bodies` was decomposed to grade 4; both affected fixtures now carry `check_state/` and `plan_merge/`; both task verifies passed; SC-02 was re-measured over immutable pin `73ba9dce` (`runs/fix-c0-main-direct/digest.md`).
- Validation c1: all five readers passed. QA measured non-zero discovery and a green unit/integration matrix; code review left one medium advisory; security found no exploitable surface; UI scoped out; goal-check marked SC-01..SC-03 met (`runs/validate-c1-validator/digest.md`).

No report round was spawned. This briefing was assembled from every run digest named by `feature.json`: `.harness/harness/features/FEAT-70-long-file-plan-merge-package/runs/plan-product/digest.md`, `.harness/harness/features/FEAT-70-long-file-plan-merge-package/runs/validate-validator/digest.md`, `.harness/harness/features/FEAT-70-long-file-plan-merge-package/runs/fix-c0-main-direct/digest.md`, and `.harness/harness/features/FEAT-70-long-file-plan-merge-package/runs/validate-c1-validator/digest.md`.

## Open questions and resolved escalations

There are no open questions. VAL-01 and VAL-02 are closed by c1. The advisor's ruling remains exactly seven accepted comparison records: two traceback-coordinate stderr records and five shipped-plan anchor records; no normalization or suppression was broadened.

## Spend and judgements

The ledger records 4 runs, 93 wall-clock minutes, 384,692 measured tokens, 56 rework minutes, and 1 recorded rework round. It contains 3 judgements: mission, succession, and the operator's c0 regate. `cycles_used` remains 2 of 10, including the plan send-back and main-session fix attribution.

## Amendments

No signed task field was amended during build.

| At | Task field | Reason | Overruled |
|---|---|---|---|
| — | — | No amendments | — |

Overrule rate: 0/0.

## UAT

No UAT is required: all three signed success criteria are `verify: automated`, and c1 exercised their configured evidence.

## Proposed backlog

| ID | Nature | Residual |
|---|---|---|
| B-1 | chore | Consider simplifying `tests/integration/test-plan-merge.py:4414-4450`; the atomic two-amendment regression grades 2 (ABC 30.1), below the preferred test bar of 3, but remains coherent and non-gating. |
