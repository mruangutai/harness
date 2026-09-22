# Answer — T-32 blocker: /api/kpis 500 on the lane fixture (operator, 2026-09-22)

## Finding (Main reproduced)
`serve.py --root <fixture>` → `GET /api/kpis` = 500 `{"error":"dashboard unavailable: 'cycles_used'"}`. `client/fixture.ts::materializeState` writes feature.json with only `feature_id, branch, fixture_state, fixture, runs` — no `cycles_used`/`max_total_cycles`, which `kpi.py:114` reads by key. The source demo record `fixtures/project-a/.../FIX-SHIPPED/feature.json` does carry them. This is why the RED baseline's VIS-DENSITY/VIS-PROTOTYPE setups failed with `initial-request-error` and why no header/KPI UI renders on any check.

## Ruling
1. The fixture is wrong, not the check. The lane's "default loaded dashboard" state must be a schema-valid feature record: `materializeState` copies the demo record's fields (`cycles_used`, `max_total_cycles`, and whatever else `kpi.compute` reads) and overrides only the state-specific ones. `unavailable-kpis` remains the ONLY state that is allowed to yield an unavailable KPI response, and it does so via the documented mechanism, not by omitting keys. This is a client-package change; extend T-32's `files:` to include `client/fixture.ts` (pm records the amendment; approval does not reset for a files-scope widening the operator has ruled here) — frontend-dev owns it within the same round. Any client-package change re-runs the whole Checks table — already T-32's verify.
2. `kpi.compute` raising on one malformed feature.json is a server robustness gap (one bad record blanks the fleet). Out of FEAT-53's remaining budget: file it as a bug against the dashboard (Main files) — NOT fixed in T-32.
3. This blocker does not count against T-32's two rounds; round 1 restarts once the fixture is valid.
