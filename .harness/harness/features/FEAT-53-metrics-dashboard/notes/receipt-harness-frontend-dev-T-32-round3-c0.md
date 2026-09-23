# T-32 round 3 receipt

- Run: `2026-09-22-t32-round3-eng`
- Build: PASS (`npm --prefix .claude/skills/harness/bin/dashboard/client run build`)
- Exact UI lane: FAIL, 13/23 passed.
- Independent gate: FAIL (the first attempt found no results after the required clear; the regenerated lane remained red, so a passing gate cannot be claimed).

Implemented native sortable table regions, sticky first columns, KPI identity paint ownership, the 4+3 KPI grid, KPI panel fallback tables, unique work-link accessible labels, and focus/status styling.

Remaining evidence: both desktop table/a11y and visual iteration tests time out at 30 seconds while traversing routes; keyboard still has remaining transition failures behind its timeout. The generated lane output is under `runs/2026-09-22-t32-round3-eng/ui`.
