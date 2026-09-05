# STATE

## Current

- feature: BUG-1302-suite-layout-fail-closed
- run: .harness/harness/features/BUG-1302-suite-layout-fail-closed/runs/2026-09-05-5-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase COMPLETE, awaiting main-session signature. BRIEF.md (6 REQ, 10 SC) and plan.yaml
(3 decisions, 5 tasks T-01..T-05, all main-session-direct under DEC-174) both read
`pending`; only the main session signs. Sequence run: Advisor consult, draft, goal-check
against stated intent, architecture + simplify pass, fix cycle, adversarial plan-panel
(both readers ran, severity_max med, zero high/critical/unrated), panel resolution and
transcription. All four panel findings resolved; panel recorded at plan.yaml `panel`.
Orchestrator-verified: check-plan-routes.py exit 0, 5 DEVIATION, 0 VIOLATION (SC-10 green).
cycles_used 3 of 8. Artifacts committed at 36311d67. Build phase is main-session-direct
work, not a lead dispatch.

## Open Questions

- Q1 (non-blocking, operator): amend DEC-174's script enumeration to name run-unit-tests.sh?
  Amending a signed decision is the operator's call.
- Q2 (non-blocking, operator): B-6 remedy (a) is an Advisor labelled recommendation, not a
  ruling. Accept at signature, or re-argue remedy (b)? Re-planning would touch T-03 only.
- Q3 (non-blocking, operator): PF-1ada4741 — the AST-pin false-positive red is main-session-only
  to clear under DEC-174. Recorded in the BRIEF; belongs on the signature record.
- Q4 (non-blocking, unassessed): SC-09's named-check list is confirmed to name only checks that
  exist, but nobody assessed whether it OMITS a pre-existing check worth protecting.
- Q5 (non-blocking, harness defect): pm's notes grant permits only research-*.md under
  features/<FEAT>/notes/, so plan-merge value files cannot be staged inside the feature tree.
- Q6 (non-blocking, harness defect): three subagent jobs exited 1 under "yield with null data"
  while emitting fully conformant fenced returns whose artifacts verified correct on disk.
