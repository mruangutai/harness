# FEAT-53 backend dashboard repair

**BLUF:** PASS. Commit `1933b81279f8f6b77dc38fb138593065590447f2` repairs the owned KPI/dashboard/work test failures; all focused proofs pass.

## Pre-fix reproductions

- `python3 tests/unit/test-metrics-kpi.py` — exit 1; 19 tests, with `test_committed_dashboard_source_sweep_rejects_mix_literal` failing because committed `client/dist/assets/index-hkwR5g06.js` contains `107`.
- `python3 tests/integration/test-metrics-dashboard.py` — exit 1; 6 tests, 2 failures: both static-route checks requested the retired `index-DzoXKmQ_.js` and received 404. The full-repository KPI request was already below the unchanged ceiling at `4.378s`; the reported latency failure did not reproduce after infrastructure repair.
- `python3 tests/integration/test-work-dashboard.py` — exit 1 at argument parsing: `usage: test-work-dashboard.py --case collector|metrics|attention|worktrees`.

## Repair and focused proofs

- The committed-source sweep now restricts itself to authored Python and `client/src` runtime source, retaining its mutation proof for a committed `107` literal while excluding generated `client/dist` bytes.
- Static-route assertions now request the committed bundle `index-hkwR5g06.js` without changing server routing.
- No-argument work-dashboard execution runs collector, metrics, attention, and worktree cases; fixture collection filters worktree rows before display-name indexing, avoiding linked-worktree/feature-name collisions. `--case collector` remains supported.
- `python3 tests/unit/test-metrics-kpi.py` — exit 0; 19 tests.
- `python3 tests/integration/test-metrics-dashboard.py` — exit 0; 6 tests; full-repository `/api/kpis` measured `4.410s < 8.0s`.
- `python3 tests/integration/test-work-dashboard.py` — exit 0; 35 assertions (9 collector, 7 metrics, 15 attention, 4 worktrees).
- `python3 tests/integration/test-work-dashboard.py --case collector` — exit 0; 9 collector assertions.

## Commit scope

- `tests/unit/test-metrics-kpi.py`
- `tests/integration/test-metrics-dashboard.py`
- `tests/integration/test-work-dashboard.py`

No generated bundle was rebuilt and no source or infrastructure files were modified.
