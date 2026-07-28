# /harness-plan — plan a feature to an approved PLAN

Read `.claude/commands/harness.md` and follow it with **mission: plan**. The differences:

- **Target state:** BRIEF approved (write it via `pm` if absent — or route to `/harness-init` if the
  project has no `.harness/` at all), then the plan-feature sequence run by the orchestrator:
  product-lead's squad plans, eng-lead reviews architecture, ui-reviewer checks the design contract.
- **Terminus:** ONE approval, taken by you — the user signs PLAN **and** the prototype (if the
  feature needs one) together. Completing plan is NOT a briefing (§10.3).
- After approval, offer `/harness-ship` — do not start it unasked.
