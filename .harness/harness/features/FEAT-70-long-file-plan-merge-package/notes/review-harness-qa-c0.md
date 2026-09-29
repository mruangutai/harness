# QA gate — FEAT-70 cycle 0

## Verdict

**FAIL.** T-01 and T-02 verify clauses pass and SC-01..SC-03 have durable fail-first evidence, but required `integration` is red twice on an unrelated named test. The cross-module matrix requires both `unit` and `integration`; a passing subset cannot replace its configured integration command.

## Phase 1 coverage expectation

From `BRIEF.md` and `plan.yaml` before source inspection: (1) package inventory, retained entry import, and all-function grade proof; (2) the 107 pre-existing CLI cases plus baseline/pin byte identity and scratch corpus; (3) a two-entry block-scalar amendment that proves success, both writes, ledger ordering/validity, and no traceback; and (4) the cross-module unit and integration floor. The inspected tests and receipts cover (1)-(3); no coverage gap was found.

## Required matrix and execution

| kind | state | configured command | discovery/execution | outcome |
|---|---|---|---|---|
| unit | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 43 discovered scripts; non-zero discovery | exit 0; all 43 scripts passed |
| integration | satisfied for FEAT-70 coverage; suite red | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 72 discovered scripts; non-zero discovery | exit 1 on both runs; 71 scripts passed and `test-hooks-install.py` failed |

The integration failure is outside FEAT-70's diff: `tests/integration/test-hooks-install.py:436-443` expected a post-merge sweep to remove its temporary terminal-feature worktree and print `post-merge-sweep: removed`; both assertions failed in `case_sc14_end_to_end_and_red_proof` (`:457-463`). Concrete scenario: an actual merge leaves the fixture's terminal worktree in place, so the cleanup contract asserted by that test is not met. FEAT-70 neither changes this test nor its hook/sweep surfaces; nonetheless the configured required command remains red.

T-01 verbatim verify passed (exit 0): package set and grade/import assertion, then `test-plan-merge.py`, `test-check-state-worktrees.py`, and `test-check-plan-routes.py`. T-02 verbatim verify passed (exit 0): receipt commit/pin/ancestry assertions and `feat70-grade-assert.py`; the latter measured 237 functions over 12 files, none below grade 4.

## Automated SC and fail-first evidence

| SC | current automated evidence | fail-first evidence |
|---|---|---|
| SC-01 | `notes/clean-pin-byte-receipts.generated.md:158-168` — pin grade assertion green, complete 12-file surface | `notes/clean-pin-byte-receipts.generated.md:171-185` — same assertion at baseline exits 1 with no package and 12 below-bar functions |
| SC-02 | `notes/clean-pin-byte-receipts.generated.md:25-38` — 107/107 each side, 293 aligned CLI observations, and 6,518 scratch commands each side | `notes/red-first-receipts.md:26-31` — BRIEF-authorized semantics-preserving equivalent: baseline-versus-pin comparison; recorder previously reported 40 concurrency and 18 clock differences before deterministic controls |
| SC-03 | `tests/integration/test-plan-merge.py:4414-4441` — asserts both amendments, block scalar, ordered ledger, validity, and no traceback; T-01 execution passed it | `notes/red-first-receipts.md:3-14` and `notes/clean-pin-byte-receipts.generated.md:128-152` — committed red `937b1242`, baseline exit 1/IndexError with unchanged plan+ledger, pin exit 0 with both changed |

## Receipts and rulings

`clean-pin-byte-receipts.generated.md:3-12` contains the required implementation pin, baseline, 107/107 outcomes, identity outcomes, and overall PASS. The two stderr-only traceback-coordinate records are scoped in `build-divergences.md:7-41` and the five scratch `check` records in `:43-61`; `divergence-rulings.json:3-49` has exactly the corresponding two-plus-five records. These match the operator-delegated rulings without expanding their scope.

## Principles applied

None. This was read-only gate execution; no verification lever was added.
