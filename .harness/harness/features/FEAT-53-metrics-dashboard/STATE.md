# STATE

## Current

- feature: FEAT-53-metrics-dashboard
- run: .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-17-09-eng/digest.md
- squad: engineering
- status: building
- tasks_done: T-01..T-15, T-18..T-21, T-23..T-31
- next_tasks: T-22, T-16
- cycles_used: 25
- max_total_cycles: 30
- rework_rounds: 10
- rework_wall_clock_minutes: 450
- feat61_prototype: retired (T-29). Its restartable data-collection ideas — the plan.yaml
  station + STATE.md + feature.json join per feature, the worktree-aware source selection, the
  attention ranking — were adopted and rebuilt in dashboard/work.py, dashboard/attention.py and
  the fixed-clock collector/attention/worktree cases in tests/integration/test-work-dashboard.py
  (T-23, T-24, T-26, T-27). Its fixed-width table renderer and the plugins/harness-work-status
  Herdr plugin were intentionally discarded. The worktree
  .claude/worktrees/harness/FEAT-61-observe-dashboard and its branch were already absent from
  the control plane's registry at T-29 (removed with its uncommitted files under the operator's
  disposition); nothing from it was committed, copied or merged.

## Open Questions

- none
