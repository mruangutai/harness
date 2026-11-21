# Simplify pass: T-01 diff (926383ae..e633f9ca)

Four `reviewer` angles (reuse, simplification, efficiency, altitude), read-only. None reported a must-fix finding; all four rated the diff correct.

| Finding | Angle | Disposition |
|---|---|---|
| Gate runs after `_check_all`, so an unloadable plan prints OK lines and spends resolver spawns before exit 5 | efficiency | Applied: the gate runs first. The exit-5 regression now also asserts that no OK line is printed. |
| The module header contract omits the route gate and exit 5 | altitude | Applied |
| The duplicate-id case restates the `_gate_plan` fixture | reuse, simplification | Applied: the plan is built from `_gate_plan()` |
| Redundant `revisedInput &&` guard beside `schemasInjected` | simplification | Applied: one return |
| The gate re-resolves paths with uncached check-domain spawns (cost matches CI's) | efficiency | Declined: the fix needs a resolver parameter in `check-plan-routes.py`, which the signed T-01 intent rules out |

The full T-01 verify was re-run after the edits and exits 0: `notes/receipts/green-verify.txt`.
