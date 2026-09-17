# Backend repair receipt — FEAT-53 c4

**BLUF:** Commit `3b78eb833f12e82e711c6e1b82bf712821ab0a1b` closes the assigned backend blockers; the pre-existing excluded static-asset assertion remains the only failure of T-12's full command.

## Files and repairs

- `.claude/skills/harness/bin/dashboard/serve.py` — rejects hostile Host headers before routing; `localhost`, `127.0.0.1`, and `[::1]` forms (with optional numeric ports) remain accepted (V-04).
- `.claude/skills/harness/bin/dashboard/kpi.py` — separates selection/payload work without re-reading trend data; `compute` is grade 4 (V-12).
- `.claude/skills/harness/bin/dashboard/work.py` — separates measured and per-phase token aggregation; `_tokens` is grade 4+ (V-13).
- `tests/integration/test-metrics-dashboard.py` — hostile Host coverage for `/`, `/api/work`, `/api/kpis`; all-output fixture/root route isolation; repeated full-repository timing; decomposed static/API test (V-04, F-QA-02, V-07, V-14).
- `tests/integration/test-metrics-trend.py` — three-record separate-worktree/two-merge survival and every trend field unavailable/not-zero coverage (V-08, V-19).
- `tests/integration/test-work-dashboard.py` — decomposed worktree case preserving every assertion (V-15).

## Fail-first / mutants

- Host red before repair: `test_untrusted_host_cannot_read_dashboard_routes` returned `200` for `/` with `Host: attacker.example`; green after the guard returns JSON `400` on all three protected routes and `200` for all six loopback variants.
- Trend merge mutant: changing `trend._records` to return `{}` failed the new two-merge test with expected `['FEAT-BASE', 'FEAT-FIRST', 'FEAT-SECOND']`, actual `[]`; restored before commit.
- V-07 fixture-isolation live mutant (exit 1): temporarily changed `repository_client = self.serve.create_app(ROOT).test_client()` to `repository_client = self.serve.create_app(self.project).test_client()`, then ran `python3 -m unittest tests.integration.test-metrics-dashboard.MetricsDashboardIntegrationTest.test_kpi_route_isolated_from_fixture_for_all_output`; assertion text: `AssertionError: '<fixture root>' == '<fixture root>'` at `self.assertNotEqual(fixture_payload["project"]["root"], actual["project"]["root"])`. Restored, then the exact same command exited 0 (`Ran 1 test ... OK`).
- V-19 every-field unavailable live mutant (exit 1): temporarily changed `_feature_trend(None)` to emit `0` for `runs`, then ran `python3 -m unittest tests.integration.test-metrics-trend.TrendTest.test_kpi_reports_every_missing_trend_field_unavailable_not_zero`; assertion text: `AssertionError: 0 is not None : runs` at `self.assertIsNone(missing["trend"][field], field)`. Restored, then the exact same command exited 0 (`Ran 1 test ... OK`).
- The initial full T-12 run reproduced the unrelated excluded asset failure twice: `/assets/index-hkwR5g06.js` returned `404`. It was neither modified nor reopened.

## Green evidence

- `python3 tests/unit/test-metrics-kpi.py` — 21 passed.
- `python3 tests/integration/test-metrics-trend.py` — 16 passed.
- `python3 tests/integration/test-work-dashboard.py --case metrics && python3 tests/integration/test-work-dashboard.py --case worktrees` — 7 and 4 assertions passed.
- Targeted Host/isolation/timing dashboard tests: `python3 -m unittest tests.integration.test-metrics-dashboard.MetricsDashboardIntegrationTest.test_untrusted_host_cannot_read_dashboard_routes tests.integration.test-metrics-dashboard.MetricsDashboardIntegrationTest.test_kpi_route_isolated_from_fixture_for_all_output tests.integration.test-metrics-dashboard.MetricsDashboardIntegrationTest.test_repository_api_request_is_kpi_payload_under_ceiling` — 3 passed.
- Full-repository `/api/kpis` timing samples: `4.718s`, `4.532s`, `4.569s`; slowest sample `4.718s`, so minimum repeatable headroom is `3.282s` below the signed `<8.0s` limit.
- Canonical grade: `python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/code-grade.py --base ffd9fb0204701cdae968ef0febc86943fb4829bd --head HEAD` — 38 passing; `compute`, `_tokens`, dashboard API/static test, and `worktree_case` meet their bars.

## Plan verify clauses

- T-10: `python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/integration/test-metrics-trend.py` — exit 0.
- T-12: `python3 tests/integration/test-metrics-dashboard.py` — exit 1 only because the explicitly excluded retained `/assets/index-hkwR5g06.js` assertion returns 404 twice; all assigned backend targeted checks pass.

Commit: `3b78eb833f12e82e711c6e1b82bf712821ab0a1b`.
