# STATE

## Current

- feature: BUG-1302-suite-layout-fail-closed
- run: .harness/harness/features/BUG-1302-suite-layout-fail-closed/runs/2026-09-05-3-product/state.yaml
- squad: product
- status: in-flight

BRIEF.md and plan.yaml drafted (6 REQ, 10 SC, 5 tasks, all main-session-direct under DEC-174).
check-plan-routes.py verified at the orchestrator tier: exit 0, five DEVIATION lines, zero
violations — SC-10 green at plan time. Next: goal-check against stated intent plus the
architecture/simplify pass on the draft, then the adversarial plan-panel.

## Open Questions

- Q1 (non-blocking, operator): should BUG-1302 amend DEC-174's script enumeration to name
  run-unit-tests.sh? Amending a signed decision is the operator's call.
- Q2 (non-blocking, operator): B-6 remedy (a) is an Advisor recommendation, not a ruling. Accept
  it at signature, or re-argue remedy (b) first? Re-planning would touch T-03 only.
- Q3 (non-blocking, harness defect): pm's notes grant permits only research-*.md under
  features/<FEAT>/notes/, so plan-merge value files cannot be staged inside the feature tree.
