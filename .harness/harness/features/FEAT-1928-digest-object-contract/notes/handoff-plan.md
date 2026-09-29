# Handoff — FEAT-1928-digest-object-contract, plan → build — written at 1f021fa3015d721099a87ed840eaf7eaae37db29, seq-4

## Next

Present the pending reconciled BRIEF.md and plan.yaml to the operator for re-signature with the standing 2 rounds / 90 minutes ruling. If FEAT-70 merges before signature, first re-resolve T-04's five named plan-merge symbols to bin/plan_merge/**, amend only T-04's files through plan-merge.py, rerun plan check, and then sign. If signature happens first, T-01 and T-02 may proceed, but T-04 remains blocked until FEAT-70 merges, its anchors are amended and checked, and the resulting approval reset is re-signed.

## Trust

- The reconciled four-task plan resolves 71 anchors with zero failures — .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml — UNVERIFIED
- The panel record retains cycle-0, cycle-1, and reconciliation reader statuses plus all six historical resolved findings — .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml#panel — UNVERIFIED
- T-04 alone gates the five moving plan-merge digest-reader symbols on FEAT-70; T-01 and T-02 remain runnable independently — .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml#T-04 — UNVERIFIED
- Both approval surfaces are pending and feature.json retains the 2 rounds / 90 minutes ruling — .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#Approval — UNVERIFIED

## Dead ends

- Do not start T-04 before FEAT-70 is merged into this worktree and all five symbol anchors are re-resolved — .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml#T-04 — UNVERIFIED
- Do not route enforcement-layer files or owning tests through governed teams; DEC-174 keeps those edits main-session-direct — .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml#lanes — UNVERIFIED
- Do not reopen SC-01 through SC-08, D-01 through D-05, or the 2 rounds / 90 minutes ruling during re-signature — .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md — UNVERIFIED

## Working set

- .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md
- .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml
- .harness/harness/features/FEAT-1928-digest-object-contract/feature.json
- .harness/harness/features/FEAT-1928-digest-object-contract/runs/plan-reconcile-product/digest.md
- .harness/harness/features/FEAT-1928-digest-object-contract/notes/research-FEAT-1928-digest-object-contract-plan-reconcile-apply.md

## Done when

Scope: Operator re-signature of the reconciled FEAT-1928 BRIEF and plan after any required post-FEAT-70 T-04 re-anchoring
Authority: brief-perspective:.harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#operator
Authority: approval:.harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#Approval
Authority: plan-task:T-04.verify
