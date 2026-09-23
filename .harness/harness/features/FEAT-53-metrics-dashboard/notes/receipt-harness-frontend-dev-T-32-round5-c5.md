# T-32 round 5 c5 receipt

## BLUF

The signed exact lane is **21/23, failed**; do not run the UI gate. Every `KpiPanel` now has one Astryx `InfoDisclosure`, including unavailable KPI 3, with tile-derived denominator/definition text and sourcing rules for KPIs 4 and 7.

## Product proof

- RED: `npm test -- --run src/panels.test.tsx` failed because KPI 3 had no `About Blocking Human Touchpoints` button.
- GREEN: `npm test -- --run src/panels.test.tsx src/kpi-content.test.tsx && npm run build` passed 8 tests and rebuilt `client/dist/`.
- Focused browser proof, no timeout override: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=2026-09-22-t32-round5-c5-density-retry npm run test:ui -- --grep "dense hierarchy and qualitative states match DESIGN"` passed both desktop projects in 9.6s.

## Exact signed lane

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=2026-09-22-t32-round5-eng npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui
```

Verbatim console log: `artifact://3936` (the exact command's captured raw output). Final result: `21 passed`, `2 failed` in 54.5s. Both failures are `VIS-DENSITY` at desktop-1440 and desktop-1920: the 30s budget expires at `initial-request-error`; later `table-overflow` capture reports `page.addStyleTag: Target page, context or browser has been closed`.

`runs/2026-09-22-t32-round5-eng/ui/results.json:607-614` records `status: failed` and the missing evidence labels `initial-request-error` and `table-overflow` for both projects. The complete evidence inventory contains 37 WebPs; all 8 referenced trace ZIPs exist and are nonempty (total 50,499,149 bytes). The independent UI gate was not run because the required 23/23 condition was not met.

## Changed files

- `.claude/skills/harness/bin/dashboard/client/src/panels.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/tiles.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/panels.test.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/kpi-content.test.tsx`
- `.claude/skills/harness/bin/dashboard/client/dist/assets/index-v3HQaj96.js`
- `.claude/skills/harness/bin/dashboard/client/dist/assets/index-C1ILh2B3.css`

