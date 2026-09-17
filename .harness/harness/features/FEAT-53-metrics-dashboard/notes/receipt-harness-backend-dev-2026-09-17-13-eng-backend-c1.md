# FEAT-53 backend KPI optimization repair

**BLUF:** PASS. Commit `7ddf6d67e31cee63ac8fbd4f8fd9f49d2e98a594` selects records from inexpensive feature identity and trend shipping metadata before per-feature enrichment, so discarded records do not run change-size or touchpoint work.

## Changed files

- `.claude/skills/harness/bin/dashboard/kpi.py` — splits metadata selection from the retained `_feature` enrichment seam; `window=all` still enriches every feature.
- `tests/unit/test-metrics-kpi.py` — behavior-level regression proof verifies a 30d request enriches only `FIX-SHIPPED`, not discarded feature records.

## Verification

`python3 tests/unit/test-metrics-kpi.py`

```text
....................
----------------------------------------------------------------------
Ran 20 tests in 3.003s

OK
```

`python3 tests/integration/test-metrics-dashboard.py`

```text
....full repository /api/kpis elapsed: 4.252s
..
----------------------------------------------------------------------
Ran 6 tests in 5.807s

OK
```

The measured `/api/kpis?window=all` request remains below the unchanged 8.0-second ceiling. Commit scope contains only the two files listed above; no dev-ops/shared files were committed.
