# FEAT-1928 operator briefing — T-03 amendment blocked at approval reset

T-03 now carries the authorized DEC-237 ruling and BRIEF approval is pending. The plan cannot yet be returned for re-signature because `plan-merge.py amend` preserves an existing task's approved signature and only the main session may run `revoke-approval`. T-03 was not resumed.

## Definition of done

No implementation validation goal-check has run, so none of the signed perspectives is yet graded complete. The earlier product goal-check graded plan coverage only.

| Perspective | Signed outcome | Verdict | SCs | Evidence |
|---|---|---|---|---|
| operator | Closed persona contracts reject malformed text, null data, and dispatcher-owned schema controls; live retry evidence precedes repair deletion. | ungraded | SC-01, SC-04, SC-05 | No validate digest exists. |
| orchestrator | Every persona returns the same typed VERDICT/DIGEST/artifact object without prose parsing or omitted-field guessing. | ungraded | SC-02 | No validate digest exists. |
| code maintainer | One canonical schema feeds validation and provider bundles; obsolete parsers, renderers, fallbacks, tables, and live fences are removed. | ungraded | SC-03, SC-08 | No validate digest exists. |
| reader | Human assessment plus deterministic validated YAML remains append-only and historical digests remain readable byte-for-byte. | ungraded | SC-06, SC-07 | No validate digest exists. |

## Current result

- Product planning originally reached complete plan coverage, then reconciled and re-anchored T-04 (`runs/plan-product/digest.md`, `runs/plan-c1-product/digest.md`, `runs/plan-reconcile-product/digest.md`, `runs/plan-reanchor-product/digest.md`, `runs/plan-reanchor-assess-product/digest.md`).
- Documentation stopped correctly when DEC-236 was found allocated (`runs/build-docs-product/digest.md`).
- The trusted operator answer authorized DEC-237. PM amended only T-03 through `plan-merge.py amend`: its number check records DEC-236 as FEAT-1896's allocation and the stale/divergent, no-PR FEAT-46 exception; DEC-237 must record the 2026-09-29 all-required/no-null/sentinel/always-present/closed-entry ruling as superseding DEC-223's documented-optional tier (`runs/plan-amend-T03-product/digest.md`).
- BRIEF is pending. `plan.yaml` remains approved because approval revocation is main-session-only. The main session must run `plan-merge.py revoke-approval`; it must not sign the plan yet.
- The one requested plan check ran after the amendment. T-03 resolved all 6 anchors, but the whole-plan check exited 1 on two T-04 anchors, `_digest_mapping` and `_fenced_blocks`; changing T-04 was expressly outside this amendment.

## Open blockers

1. Main session: revoke `plan.yaml` approval for the authorized T-03 amendment, leaving it pending for operator re-signature.
2. Before signature, route the two stale T-04 anchors separately; this assignment authorized no T-04 change.

## Spend and record

- Runs: 9 of informational 20; this is below the tripwire and the runs remain attributable to planning reconciliation, direct build, documentation stop, and the authorized correction.
- Cycles: 1 of 10.
- Recorded spend at close: 335 wall-clock minutes, 694,951 tokens; build-phase rework is 0 minutes / 0 rounds.
- Judgements: 3. Builder amendments: none; overrule rate: 0/0.
- UAT: not run; no ship-readiness validation has started.

## Proposed backlog

| ID | Nature | Residual |
|---|---|---|
| none | — | No non-gating residual was identified. |

No report round was spawned. This briefing was assembled from every available digest named by `feature.json`: `runs/plan-product/digest.md`, `runs/plan-c1-product/digest.md`, `runs/plan-reconcile-product/digest.md`, `runs/plan-reanchor-product/digest.md`, `runs/plan-reanchor-assess-product/digest.md`, `runs/build-docs-product/digest.md`, and `runs/plan-amend-T03-product/digest.md`. `plan-product-c1` and `build-main-direct` are ledgered runs with no digest present in the feature tree.