# FEAT-53 c5 backend receipt

Fixed tip: `ae5970d92c5142ccc2530d8b4519afda8b184000`.

Committed pathspecs:

- `.claude/skills/harness/bin/dashboard/trend.py`
- `tests/integration/test-metrics-dashboard.py`
- `tests/integration/test-metrics-trend.py`
- `tests/integration/test-work-dashboard.py`
- `tests/unit/test-metrics-kpi.py`
- `.harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-backend-dev-fix-c5.md`

## V-07 proof

`test_kpi_route_isolated_from_fixture_for_all_output` binds fixture values from `expected.json`, not `kpi.compute`: feature IDs, the shipped feature's every expected KPI field, throughput, rework, feature touchpoints, and aggregate touchpoint nested values. Each binding is separately checked against the fixture API response; the Harness route is separately checked for its resolved project root and payload shape.

Live baseline evidence: `python3 -m unittest tests.integration.test-metrics-dashboard.MetricsDashboardIntegrationTest.test_kpi_route_isolated_from_fixture_for_all_output` — PASS (1 test). The same test installs a systemic mutant at `kpi.compute` that ignores every requested project root and computes from the Harness root. Its independently bound fixture assertions fail under `assertRaises(AssertionError)`; the enclosing test passes only because the mutant was detected. This is a project-derived systemic reroute, not a client-root swap.

## Scoped verification

- `python3 tests/unit/test-metrics-kpi.py` — PASS, 21 tests.
- `python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/integration/test-metrics-trend.py` — PASS; 16 trend tests.
- `python3 tests/integration/test-metrics-dashboard.py` — PASS, 8 tests; full-repository KPI samples 4.315s, 3.862s, 3.820s.
- `python3 tests/integration/test-work-dashboard.py` — PASS; 41 assertions, including `metrics_case`.

Trend `_records` preserves parse/schema/timestamp normalization order, unavailable reasons, duplicate resolution, and segmented reader callers; focused trend coverage passed. The three extracted test helpers retain all prior ordered ship, metric, and hand-labelled assertions.

## Canonical grades

- `python3 .claude/skills/harness/bin/code-grade.py --base a18d6a9f1f832084df84be22097a409d73bf4f61 --head HEAD` — PASSING: 396.
- `python3 .claude/skills/harness/bin/code-grade.py --base d1d9a44eef283949b9465c97358c6741f4b337b0 --head HEAD` — PASSING: 27.

Both ranges pass `.claude/skills/harness/bin/dashboard/trend.py:_records` (production bar 4), `tests/integration/test-work-dashboard.py:metrics_case`, `tests/integration/test-metrics-trend.py:TrendTest.test_cmd_ship_records_trend_before_board_writes_and_handles_failure`, and `tests/unit/test-metrics-kpi.py:KpiCoreTest.test_hand_labelled_feature_and_aggregate_values` (test bar 3).

No out-of-scope path is included in the repair commit; the attention and grilling-status repairs remain untouched.
