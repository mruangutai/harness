# Observations — harness-backend-dev — FEAT-53

- 2026-09-16: The new directory-selected unit runner discovers tests/unit/test-metrics-kpi.py without runner registration; direct focused execution preserves the hand-labelled fixture contract.
- 2026-09-16: Dashboard KPI change-size computation must resolve origin/HEAD once using the supplied project root; a trunk fixture catches hardcoded main and a missing resolution must suppress diffs rather than substitute another repository branch.
- 2026-09-16: dashboard collectors can patch worktree_terminal._worktree_paths in offline fixtures while factory_config.workspace_path keeps fleet workspace derivation single-sourced.
- 2026-09-16: KPI unit tests patch kpi.subprocess.run, so a new KPI module must not call the shared subprocess.run attribute when its real git history must remain available during kpi tests.
- 2026-09-16: Attribution plan reads must be cached by feature ID because multiple task-prefixed commits can map to one plan.
- 2026-09-16: touchpoints count must bind subprocess.run at import time so kpi unit tests that patch kpi.subprocess.run do not corrupt feature-start git fallback.
- 2026-09-16: Dashboard phase boundaries can be derived deterministically from handoff header seq-N and completed run ended_at values; current phase must not be inferred from station.
- 2026-09-16: T-12 still names retired run-unit-tests.sh plus INTEGRATION_SCRIPTS, while the native run-unit-tests.py migration has directory-only discovery; execution needs a plan amendment rather than recreating the retired wrapper.
- 2026-09-16: T-12 server integration must exercise kpi.compute against both fixture and worktree roots; current grading invocation and binary numstat parsing raise rather than producing a payload, so serving code must not catch them as empty KPI data.
- 2026-09-16: Ship-time trend persistence must compute cycle time against its newly generated shipped_at; the prior per-feature read has no existing ship record and therefore cannot supply the measured duration.
