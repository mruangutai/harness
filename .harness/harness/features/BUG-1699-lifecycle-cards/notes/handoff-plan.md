# Handoff — BUG-1699-lifecycle-cards, plan → build — written at 959e171c, seq-1

## Next

Do not begin implementation until the operator explicitly starts `/harness-ship`. The plan and BRIEF are approved, the feature station is Ready, and the signed rework ruling is 2 rounds / 90 minutes. At Build entry, follow the dependency graph: complete T-01 first; then T-02 and T-04; then T-03; finish with T-05 after executable truth exists.

## Trust

- The product panel and perspective goal-check passed after all three findings were applied — `runs/2026-09-15-01-plan-product/digest.md` and `notes/review-harness-code-reviewer-plan-c2.md`, verified at 959e171c.
- The plan resolves five tasks and twenty-two live anchors with no route or trace failures — `plan.yaml`, verified by `plan-merge.py check` after approval.
- Approval and the 2-round / 90-minute ruling are recorded — `plan.yaml`, `feature.json`, and `notes/answers-plan-approval-2026-09-16.md`.
- The lifecycle card projection remains outbound-only and best effort; GitHub failure must not gate local progress — `BRIEF.md` SC-10 and `plan.yaml` D-06.

## Dead ends

- Do not add a lifecycle-only fix-team step or serialize independent readers; T-03 uses existing orchestrator checkpoints.
- Do not add lifecycle state to `feature.json`; transient resume context belongs in `plan.yaml` approval metadata.
- Do not change station vocabulary, abandonment, issue closure, or open-child ship behavior.
- Do not implement task-owned DEC-174 enforcement surfaces through a team agent; preserve each task's recorded execution mode.

## Working set

- .harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md
- .harness/harness/features/BUG-1699-lifecycle-cards/plan.yaml
- .harness/harness/features/BUG-1699-lifecycle-cards/feature.json
- .harness/harness/features/BUG-1699-lifecycle-cards/notes/review-harness-code-reviewer-plan-c2.md
- .harness/harness/features/BUG-1699-lifecycle-cards/runs/2026-09-15-01-plan-product/digest.md

## Done when

Scope: implement the approved lifecycle-card plan without changing its five-task contract
Authority: brief-perspective:.harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md#operator
Authority: approval:.harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md#Approval
Authority: plan-task:T-01.verify
