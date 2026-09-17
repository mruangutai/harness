# FEAT-53 c5 scoped QA gate

**PASS — V-07 resolves at `ae5970d92c5142ccc2530d8b4519afda8b184000`; all requested T-06/T-10/T-12 proofs and canonical grade records pass.**

## Scope and matrix

Phase-1 requirements from T-06, T-10, T-12 and SC-03 required the unit KPI proof, trend/layout integration proof, route integration proof, fixture values independently bound from `kpi.compute`, separate fixture and Harness-route checks, and a systemic project-root leak mutant that reddens the fixture assertion. The c5 diff is exactly the five requested paths. No Phase-1 gap remains. `logic` requires unit; T-10/T-12 API/route behaviour warrants integration. Both kinds are satisfied.

## Scoped commands at fixed tip

- `python3 tests/unit/test-metrics-kpi.py` — PASS, 21 tests.
- `python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/integration/test-metrics-trend.py` — PASS; layout plus 16 tests.
- `python3 tests/integration/test-metrics-dashboard.py` — PASS, 8 tests; full-repository samples 4.153s, 3.842s, 3.840s.
- `python3 tests/integration/test-work-dashboard.py` — PASS, 41 assertions (including `metrics_case`).

## V-07 / SC-03 discrimination

`test_kpi_route_isolated_from_fixture_for_all_output` loads `expected.json`, separately checks the fixture response and Harness response, then installs the systemic `kpi.compute` root-leak mutant. The independently bound fixture assertion is required to raise under that mutant (`tests/integration/test-metrics-dashboard.py:128-146`; bindings at `:345-367`); the unmutated fixture and Harness payload checks pass in the same scoped 8-test run. This is concrete fail-first evidence for SC-03/V-07: forced Harness-root computation fails the fixture-value assertion, restored computation passes it.

## Canonical grades

- Complete feature range `a18d6a9f1f832084df84be22097a409d73bf4f61..ae5970d92c5142ccc2530d8b4519afda8b184000` — PASSING: 396.
- Repair range `d1d9a44eef283949b9465c97358c6741f4b337b0..ae5970d92c5142ccc2530d8b4519afda8b184000` — PASSING: 27.
- Fixed-tip canonical-record grade — PASS: `trend.py:_records` (grade 5/bar 4), `test-work-dashboard.py:metrics_case` (5/3), `TrendTest.test_cmd_ship_records_trend_before_board_writes_and_handles_failure` (4/3), and `KpiCoreTest.test_hand_labelled_feature_and_aggregate_values` (5/3).

V-07: resolved. Four records: resolved. No coverage gaps or newly emergent finding class.
