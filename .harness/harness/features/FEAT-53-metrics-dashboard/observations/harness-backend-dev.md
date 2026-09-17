# Observations — harness-backend-dev — FEAT-53

- 2026-09-16: The new directory-selected unit runner discovers tests/unit/test-metrics-kpi.py without runner registration; direct focused execution preserves the hand-labelled fixture contract.
- 2026-09-16: Dashboard KPI change-size computation must resolve origin/HEAD once using the supplied project root; a trunk fixture catches hardcoded main and a missing resolution must suppress diffs rather than substitute another repository branch.
- 2026-09-16: dashboard collectors can patch worktree_terminal._worktree_paths in offline fixtures while factory_config.workspace_path keeps fleet workspace derivation single-sourced.
