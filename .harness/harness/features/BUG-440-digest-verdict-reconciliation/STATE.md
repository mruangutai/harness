# STATE

## Current

- feature: BUG-440-digest-verdict-reconciliation
- run: .harness/harness/features/BUG-440-digest-verdict-reconciliation/runs/plan-record-fix-product/state.yaml
- squad: product
- status: awaiting-user

Plan phase COMPLETE and stopped at the operator signature gate. BRIEF.md (4 REQ / 7 SC) and
plan.yaml (1 task T-01, main-session-direct under the DEC-174 enforcement-layer carve-out,
7 decisions) are drafted, goal-checked against the grilling artifact, read by the adversarial
plan panel (3 readers recorded, 5 findings, severity_max med, none gating), and the panel is
recorded in plan.yaml `panel`. approval.status is pending; only the main session signs.

Next: operator answers the A/B/C ruling in BRIEF.md `## Constraints`, then signs
(`plan-merge.py sign-approval`). Handoff: notes/handoff-plan.md. Briefing:
notes/ship-review-plan-BUG-440.md.

## Open Questions

- Q1 (BLOCKING, operator): merging INV-37 turns `/harness` entry red with 4 blocking findings
  against 4 live mismatched records until they are reconciled. Ruling A (merge now, accept red),
  B (reconcile the four records first, merge green), or C (send the plan back). Detail and the
  four rows are in BRIEF.md `## Constraints`.
- Q2 (non-blocking, harness defect): `harness_boundary.claim_worktrees()` unions live dispatch
  claims for the bare agent-type across every linked worktree with no feature or destination
  filter, so a live `harness-code-reviewer` claim in FEAT-05-factory-doc-smoke refused the plan
  panel's scope reader its own in-domain artifact write here. Findings survived via the lead's
  digest; needs its own ticket.
