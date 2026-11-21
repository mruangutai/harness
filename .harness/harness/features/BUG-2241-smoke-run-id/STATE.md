# STATE

## Current

- feature: BUG-2241-smoke-run-id
- run: .harness/harness/features/BUG-2241-smoke-run-id/runs/2026-11-21-01-plan-product/state.yaml
- squad: none
- status: awaiting-user

## Open Questions

- Signature: BRIEF.md and plan.yaml are `pending`; operator signs via `plan-merge.py sign-approval --rework rounds=1,minutes=45` (propose-rework baseline). T-01 is `main-session-direct` because check-domain resolves NOBODY for `.agents/skills/harness-spec-driven/SKILL.md` — acknowledge the route at signature (orchestrator blocked on signature).
