# /harness-plan — plan a feature to an approved PLAN

Read `.claude/commands/harness.md` and follow it with **mission: plan**. The differences:

- **Step zero, BLOCKING:** load the `harness-grilling` skill and run it first — dialog to clarity
  with the user, name the destination, record settled/fog/out-of-scope, and hand pm the artifact
  **path** as a BRIEF input (DEC-164). A wayfinding map whose frontier and fog are both empty is
  the same hand-off — pass `.harness/efforts/<slug>/MAP.md` (DEC-165). Already have either
  artifact? Cite it and move on. Skipping it is the user's explicit call, never your assumption.
- **Target state:** BRIEF approved (write it via `pm` if absent — or route to `/harness-init` if the
  project has no `.harness/` at all), then the plan-feature sequence run by the orchestrator:
  product-lead's squad plans, the eng squad runs the four-angle simplify pass over the plan surface (`.claude/skills/harness-simplify/SKILL.md`) — FLAG-ONLY, findings return to `harness-pm`, which applies them to its own draft before the signature, because `check-domain.sh` grants `plan.yaml` and `BRIEF.md` to pm alone (D-03) — eng-lead reviews architecture, ui-reviewer checks the design contract.
- **Terminus:** ONE approval, taken by you — the user signs PLAN **and** the prototype (if the
  feature needs one) together. Completing plan is NOT a briefing (§10.3).
- After approval, offer `/harness-ship` — do not start it unasked.
