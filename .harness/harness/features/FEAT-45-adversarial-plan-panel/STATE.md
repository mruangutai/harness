# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-29-1-planfix-product/state.yaml
- squad: none
- status: awaiting-user

## Open Questions

- Ratify the reduced claim: REQ-02/REQ-05 promise an independent CONTEXT, not an independent
  MODEL. No governed spawn can select a model (dispatch-guard keys `model:` on the caller) and
  `advisorModel` is absent from this workstation. Blocks the signature. — harness-pm
- Ratify or replace pm's derived ruling on the resume-phase re-plan: a task-set change resets
  approval, so the plan is presented and read again, scoped to not-done tasks. The grilling left
  this in `## Not yet specified`. Blocks the signature. — harness-pm
- Confirm the team file ships at `.claude/skills/harness/teams/plan-panel.yaml` rather than the
  `.harness/teams/` project-override lane (D-09). — harness-pm
- Confirm the DEC-174 carve-out reading for T-07/T-08, which stay main-session-direct on paths
  that resolve to harness-backend-dev / harness-dev-ops. — harness-pm
- DEC-170's `advisorModel` citation at `~/.claude/settings.json:112` is wrong today. Stale record
  or removed setting? The record needs correcting either way. — harness-eng-lead
