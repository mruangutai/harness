# FEAT-53 combined simplify verification

**BLUF:** FAIL. Native unit and integration gates failed; the client Vitest gate passed. No failure was masked or retried.

## Committed apply scope

- `HEAD`: `60366d15cfe6e18ad99db980d360f916d3889813`.
- `git merge-base --is-ancestor 2f5c087e HEAD`: exit 0.
- `git merge-base --is-ancestor 60366d15cfe6e18ad99db980d360f916d3889813 HEAD`: exit 0.
- `git diff-tree` confirms the committed apply paths are exactly `client/src/routes.tsx`, `client/src/work-view.tsx`, `dashboard/kpi.py`, and `dashboard/trend.py` (under `.claude/skills/harness/bin/`).

## Gates (run once, in order)

1. `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit`
   - Exit 1; runner executed 42 files (8 workers; 8.63s).
   - Failing groups: `test-suite-layout.py` (uncertified integration detect patterns); `test-suite-independence.py` (two live-checkout mutation sites in `test-metrics-client-render.py:86-87`); `test-metrics-kpi.py` (1/19 failed: committed-source sweep found `107` in `client/dist/assets/index-hkwR5g06.js`).
2. `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration`
   - Exit 1; runner executed 77 files (8 workers; 144.86s).
   - Failing groups: `test-check-plan-routes.py` (touchpoints root probe lacks `team-config.yaml`); `test-harness-yaml.py` (control fails and unexpected guarded import `check-state.py`); `test-hooks-install.py` (fixture merge: `gh-sync.py` cannot import `trend`, worktree retained); `test-metrics-dashboard.py` (3/6: two client asset 404s and `/api/kpis` 8.072s > 8.0s); `test-work-dashboard.py` (missing required `--case`).
3. `npm --prefix .claude/skills/harness/bin/dashboard/client run test`
   - Exit 0; 5/5 files and 20/20 tests passed.

Focused proof: `test-metrics-kpi.py` executed 19 cases (18 passed, one stale committed-asset sweep failure); `test-metrics-trend.py` passed 14/14. Passing Vitest aggregate includes the changed-surface groups `client/src/routes.test.tsx` and `client/src/work-view.test.tsx` (all 5 files/20 tests passed).

## Changed-surface classification

Complete diff: `a18d6a9f1f832084df84be22097a409d73bf4f61..HEAD`; apply-touched source is only `routes.tsx`, `work-view.tsx`, `kpi.py`, `trend.py`.

| Failing group | Complete diff | Reaches apply-touched source |
|---|---|---|
| `test-suite-layout.py` | inside (group/test and named integration candidates are in diff) | no |
| `test-suite-independence.py` | inside (reported `test-metrics-client-render.py` is in diff) | no |
| `test-metrics-kpi.py` | inside (reported committed client asset is in diff) | no; failure is asset sweep |
| `test-check-plan-routes.py` | inside (`touchpoints.py` is in diff) | no |
| `test-harness-yaml.py` | inside (`check-state.py` is in diff) | no |
| `test-hooks-install.py` | inside (`gh-sync.py` is in diff) | yes: failing import is `trend` |
| `test-metrics-dashboard.py` | inside (test and client dist are in diff) | mixed: asset 404s do not; KPI-ceiling case calls `serve.py -> kpi.compute` |
| `test-work-dashboard.py` | inside (group is in diff) | no; it exits at argument parsing |

The five predeclared integration failures match exactly: `test-check-plan-routes.py`, `test-harness-yaml.py`, `test-hooks-install.py`, `test-metrics-dashboard.py`, and `test-work-dashboard.py`. They remain failures; no new integration group failed.

## Cleanup

Removed only generated `client/node_modules/.vite/vitest` after Vitest. `client/.vitest` was absent before and after. Scoped `git status --short` for client, `kpi.py`, `trend.py`, `tests/unit`, and `tests/integration` is empty: no generated client/dist, source, or test modifications remain. No commit was made.
