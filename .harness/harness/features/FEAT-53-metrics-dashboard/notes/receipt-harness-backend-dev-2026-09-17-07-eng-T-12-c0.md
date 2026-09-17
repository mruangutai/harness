# T-12 receipt — c0

## BLUF

The committed loopback Flask API serves real `kpi/1` fixture and repository payloads without writes; the exact amended verification passes 5 behavioral integration tests.

## Evidence

- **Fail-first:** before source creation, `python3 tests/integration/test-metrics-dashboard.py` exited 1 with 4 `FileNotFoundError` errors for absent `dashboard/serve.py`.
- **Fixture request:** a copied, initialized `project-a` received actual Flask `GET /api/kpis?window=all` status 200, schema `kpi/1`, root equal to the fixture (not this repository), and `FIX-SHIPPED` data. The same run proves all prerequisites independently (Python, PyYAML, Flask, harness.json, bundle), `--check`, busy-port failure, client fallback, JSON API errors, traversal refusal, JavaScript MIME, and byte-identical fixture git status.
- **Repository request:** actual Flask `GET /api/kpis?window=all` returned 200 `kpi/1` in **4.251s**, below the unchanged 8.0-second ceiling; repository git status was byte-identical before and after.
- **No write path:** handlers only compute/read/send; integration status snapshots prove no fixture or repository git mutation. No `trend.append` call is reachable.
- **Exact amended verify:** `python3 tests/integration/test-metrics-dashboard.py`

```text
....full repository /api/kpis elapsed: 4.251s
.
----------------------------------------------------------------------
Ran 5 tests in 5.139s

OK
```

- **Python risk grade:** the two T-12 paths report `PASSING: 27` (production bar 4, test bar 3).
- **Commit:** `c951aae6` — `.claude/skills/harness/bin/dashboard/serve.py`, `tests/integration/test-metrics-dashboard.py`.

## DEC-229 corrections

1. T-12 `intent` was `Create test-metrics-dashboard.py, register it in run-unit-tests.sh INTEGRATION_SCRIPTS`; now `Create tests/integration/test-metrics-dashboard.py in the native integration layout and run it directly as the scoped behavioral proof.` Reason: `The shell registry was retired, and the global layout preflight rejects unrelated frontend-owned colocated tests.`
2. T-12 `verify` was `python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/integration/test-metrics-dashboard.py`; now `python3 tests/integration/test-metrics-dashboard.py`. Reason: `The shared layout preflight fails on tracked frontend-owned files outside T-12, while the integration script directly proves this API contract.`

Every BRIEF success criterion, task, and decision is unchanged.
