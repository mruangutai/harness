# STATE

## Current

- feature: BUG-2295-handoff-one-per-phase
- run: .harness/harness/features/BUG-2295-handoff-one-per-phase/runs/2026-11-22-01-patch-product/state.yaml
- squad: product
- status: awaiting-user
- mission: patch
- station: plan
- approval: pending (BRIEF.md `## Approval`, plan.yaml `approval.status`)
- patch-product: PASS, cycles 0, plan-merge check exit 0, check-plan-routes exit 0
- cycles_used: 0 / 10
- next: main session — sign-approval (plan-merge.py sign-approval --rework ...), then build T-01 main-session-direct (DEC-174)

## Open Questions

- Q1 (main session, blocking): sign BRIEF.md and plan.yaml for BUG-2295, with the rework ruling; T-01 is main-session-direct.
