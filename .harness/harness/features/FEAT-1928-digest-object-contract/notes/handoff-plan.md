# Handoff — FEAT-1928-digest-object-contract, plan → build — written at 66d51605, seq-6

## Next

Present the pending BRIEF.md and plan.yaml to the operator for one signature with the standing 2 rounds / 90 minutes ruling. T-04 is already re-anchored to the merged FEAT-70 package; after signature, execute the plan in dependency order and keep T-04 in the main-session-direct lane.

## Trust

- The four-task plan resolves 76 anchors with zero failures, including all 12 T-04 entries — .harness/harness/features/FEAT-1928-digest-object-contract/runs/plan-reanchor-assess-product/digest.md — UNVERIFIED
- T-04 names the package readers, split helpers, canonical classification, retained FEAT-70 splice case, and both verification commands — .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml#T-04 — UNVERIFIED
- The plan-merge integration suite passed, including case_feat70_record_amendments_after_a_block_scalar_splice — tests/integration/test-plan-merge.py — UNVERIFIED
- Both approval surfaces are pending and feature.json retains the 2 rounds / 90 minutes ruling — .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#Approval — UNVERIFIED

## Dead ends

- Do not restore the obsolete wait-for-FEAT-70 condition; the package and CLI locations are resolved in T-04 — .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml#T-04 — UNVERIFIED
- Do not route T-04 or its owning tests through governed teams; DEC-174 keeps the plan gate readers main-session-direct — .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml#lanes — UNVERIFIED
- Do not reopen T-01 through T-03, SC-01 through SC-08, D-01 through D-05, or the 2 rounds / 90 minutes ruling during signature — .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md — UNVERIFIED
- The canonical-reader self-test is T-04's post-implementation gate and is red at this pre-build seam on the inventory that T-01 and T-04 will migrate — tests/integration/test-check-plan-routes.py — UNVERIFIED

## Working set

- .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md
- .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml
- .harness/harness/features/FEAT-1928-digest-object-contract/feature.json
- .harness/harness/features/FEAT-1928-digest-object-contract/runs/plan-reanchor-assess-product/digest.md
- .harness/harness/features/FEAT-1928-digest-object-contract/notes/research-FEAT-1928-digest-object-contract-plan-reanchor.md

## Done when

Scope: Operator signature of the pending FEAT-1928 BRIEF and re-anchored four-task plan
Authority: brief-perspective:.harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#operator
Authority: approval:.harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#Approval
Authority: plan-task:T-04.verify
