# BUG-1699 lifecycle cards — blocked ship review

## Decision first

Do not ship yet. The signed implementation tasks are complete and their focused gates passed, but the mandatory simplify segment returned `BLOCKED` before `review_sha` could be pinned or the independent validation panel could run. The block is procedural rather than a product finding: the read-only REUSE reader completed its inspection and supplied a concrete finding, but the engineering-member digest schema would not permit a truthful `PASS` without a test suite. The orchestrator playbook requires a stop on any lead `BLOCKED` verdict.

## Definition of done — graded

| Perspective | Signed definition | Verdict | Success criteria | Evidence |
| --- | --- | --- | --- | --- |
| operator | Every recorded source, parent, and eligible task card follows Plan, Ready, Building, Review, and ship-owned Done; reset/resume and bounded reconciliation preserve the signed contracts. | **unmet — not independently validated** | SC-01–SC-03, SC-06–SC-09 | Build implementation and focused task gates completed; see the T-01 build digests, commits `0d56eb7b`, `c67347cb`, and the T-05 digest. No pinned validator goal-check exists. |
| orchestrator | Every lifecycle checkpoint has one explicit caller; the existing rework flow remains bounded and GitHub writes remain best-effort outbound synchronization. | **unmet — not independently validated** | SC-04, SC-05, SC-10 | The T-03 signed gate passed at commit `6e7440e8`, and the build-entry transition ran. No pinned validator goal-check exists. |
| code maintainer | One projection policy is reused by mutation, drift detection, and reconciliation while legacy terminal, closure, discovery, and documentation contracts remain intact. | **unmet — not independently validated** | SC-11–SC-16 | T-01's seven focused runners and T-05's decision/index check passed; the simplify apply reran the exact T-01 gate successfully. The simplify digest records two residual quality rows. No pinned code-review or goal-check exists. |

These rows say **unmet** because the signed definition requires the final pinned inspection and goal-check, not because a validation panel found a product failure. Validation never started.

## What completed

- Planning produced an approved five-task contract after one plan cycle. The panel's two high substance findings and one proportionality finding were applied before signature.
- T-01 established complete active-card projection through the shared lifecycle policy. A focused fail-first correction restored the intended no-mirror eligibility boundary; the exact seven-runner gate passed.
- Main-session-direct T-02 preserved reset/resume station metadata and passed `tests/integration/test-plan-merge.py` at commit `0d56eb7b`.
- Main-session-direct T-04 reconciled every eligible active lifecycle card and passed `tests/integration/test-board-lifecycle.py` at commit `c67347cb`.
- Main-session-direct T-03 wired the explicit lifecycle phase checkpoints and passed its three signed checks at commit `6e7440e8`.
- T-05 refreshed the governing decisions and generated index. Its exact check examined 40 decision anchors with zero failures and a zero-byte generated-index diff.
- The four simplify angles all completed. One eligible simplification removed a dead derived-status branch in `check-state.py`; the exact signed T-01 gate then passed in 57.27 seconds. No formatter, linter, project-wide build, or project-wide test suite ran.

## Why the run stopped

The simplify lead was required to propagate its worst member verdict. The REUSE reader returned canonical `BLOCKED` even though its read-only inspection and finding were complete, because the engineering digest contract rejects `PASS` with a suite result of `n/a`. The lead therefore returned `BLOCKED` with no product `must_fix` findings. Under the orchestrator playbook, a blocked member is not retried and the feature cannot advance to pinning or validation.

Required unblock: repair or explicitly rule the read-only engineering-reader digest contract so a complete inspection can return `PASS` without inventing a test run, then resume at the simplify boundary. This is a Harness process defect outside the signed BUG-1699 task scope.

## Lead summaries

| Run | Verdict | Summary |
| --- | --- | --- |
| `2026-09-15-01-plan-product` | PASS | The lifecycle-card plan became signable after all panel findings were applied; the targeted plan check and perspective goal-check passed. |
| `2026-09-16-02-build-eng` | PASS | T-01 implemented all-card active-phase projection through one policy and passed seven focused runners. |
| `2026-09-16-03-build-eng` | PASS | The fail-first no-mirror regression was fixed without weakening eligible-record projection; the seven-runner gate passed again. |
| `2026-09-16-04-build-product` | PASS | Lifecycle authority and the generated decision index were updated, with 40 anchors passing and no generated diff. |
| `2026-09-16-05-simplify-eng` | BLOCKED | All four angles completed and one eligible simplification passed its signed gate, but the read-only reader digest-schema conflict forced the lead's procedural block. |

## Open blocker

| ID | Blocking | Question |
| --- | --- | --- |
| Q1 | yes | What sanctioned digest result should a read-only engineering simplify reader use when the inspection is complete but no test suite is permitted? The current development digest contract rejects a truthful `PASS` with suite `n/a`. |

## Spend and ledger

- Runs: 5
- Wall-clock run time: 158 minutes
- Feature cycles used: 2 of 10
- Rework ruling consumed: 0 of 2 rounds; 0 of 90 minutes
- Judgements recorded: 3
- Review SHA: not pinned
- Validation runs: 0
- UAT: not required by the signed success criteria; all criteria are automated or code-review evidence.

## Amendments

| At | Decision | Reason | Overruled |
| --- | --- | --- | --- |
| `2026-09-16T12:40:59.303279+00:00` | `T-01.files` | The signed intent required INV-26 to consume the projection and required the start-task regression to remain green; both omitted sites were added without changing an SC, task, or decision. | no |

Overrule rate: 0/1.

## Proposed backlog

| ID | Nature | Residual |
| --- | --- | --- |
| B-1 | enhancement | Consolidate the active feature-phase set now respelled across `gh_board.py`, `gh-sync.py`, `board_lifecycle.py`, and `plan-merge.py` behind one authoritative constant or predicate. The simplify readers disagreed on the best authority, so this intentionally stayed outside the one-fix pass. |
| B-2 | chore | Fold the identical `STATION` and `STATUS` repair branches in `board_lifecycle.py` into one membership branch. It stayed unapplied because T-04 is a signed main-session-direct lane and the simplify one-apply ceiling was already consumed. |

## Sources

No report round was spawned. This briefing was assembled from these on-disk lead digests:

- `.harness/harness/features/BUG-1699-lifecycle-cards/runs/2026-09-15-01-plan-product/digest.md`
- `.harness/harness/features/BUG-1699-lifecycle-cards/runs/2026-09-16-02-build-eng/digest.md`
- `.harness/harness/features/BUG-1699-lifecycle-cards/runs/2026-09-16-03-build-eng/digest.md`
- `.harness/harness/features/BUG-1699-lifecycle-cards/runs/2026-09-16-04-build-product/digest.md`
- `.harness/harness/features/BUG-1699-lifecycle-cards/runs/2026-09-16-05-simplify-eng/digest.md`
