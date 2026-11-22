# Observations — harness-orchestrator — FEAT-2274-omp-native-gate-policy

- 2026-11-21: The plan team (teams/plan.yaml, plan-phase.md) omits DEC-195's plan-surface simplify pass; the product lead escalated it as a blocking OQ. Resolved in-tier: eng-lead run (four readers, flag-only) then a one-step product run for pm to apply — three runs, zero cycles, no re-panel since every finding was form/leave. plan-phase.md and DEC-195 disagree on ordering (simplify before vs after the readers); the lead's escalation was correct and the sequencing is the orchestrator's.
