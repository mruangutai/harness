# FEAT-53 frontend fix c2 receipt

**Result:** all five assigned findings are repaired in the source client and committed bundle.

## Fail-first and repair evidence

- **V-02 — resolved.** Added the converse regression case in `src/routes.test.tsx`: a live-shaped settled KPI response plus failed `/api/work` request retains Repository KPIs and the Escaped Defects link while rendering Work list unavailable. The pre-repair test suite was red on the live payload route (`Cannot read properties of undefined (reading 'find')`); after the top-level payload repair the route suite is green (13 tests). The existing opposite-direction case remains at `routes.test.tsx:95`.
- **V-03 — resolved.** The red route test used the live producer shape `{features, aggregate, trend}` and failed because `/kpi/$n` dereferenced fabricated `data.kpis`. `routes.tsx` now derives the fixed seven route labels and passes the whole producer payload to `KpiPanel`; `api.ts` and `tiles.tsx` carry the same contract. Browser probe intercepted `/api/kpis` with that shape, rendered the panel, opened **About Escaped Defects**, and pointer-opened `FEAT-1` into `/work/FEAT-1` with heading **Example Feature**.
- **V-17 — resolved.** `routes.tsx` changes the keyboard-only ring to `2px solid var(--color-text-primary)`. Actual browser keyboard navigation focused **About Escaped Defects** with computed `outlineWidth: 2px`, `outlineStyle: solid`, `outlineColor: rgb(250, 250, 250)`; pointer activation of a radio input computed `outlineStyle: none`.
- **V-18 — resolved.** The shell resets body margin and constrains Astryx tables to the available width rather than allowing their 960px minimum to overflow the page. Browser geometry: at 1440px, content gutters left/right were `24/24`; at 831px, `16/16`, with document `scrollWidth/clientWidth: 831/831` (no page-level horizontal overflow). Before repair, validator measured default-body-margin gutters and `1018px` page scroll width; this probe initially reproduced the table overflow at `976/831`, then passed after the table minimum-width repair.
- **NEW-fixed-dark-document — resolved.** The shell sets `:root { color-scheme: dark }` and opaque `body { background: rgb(27,27,27) }`. Browser measurements under emulated light and dark OS preferences were both `colorScheme: dark` and `backgroundColor: rgb(27, 27, 27)`.

## Scoped verification

- **T-13:** `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/routes.test.tsx && npm --prefix .claude/skills/harness/bin/dashboard/client run build` — PASS: 13 tests; Vite build succeeded.
- **T-14:** `npm --prefix .claude/skills/harness/bin/dashboard/client run build && python3 -c "import pathlib,sys;s=''.join(p.read_text() for p in pathlib.Path('.claude/skills/harness/bin/dashboard/client/src').rglob('*.tsx') if not p.name.endswith('.test.tsx'));[sys.exit('missing '+k) for k in ['NoShipRecords','PreCapability','GradingCaveat','UnavailableValue','/kpi/','/work/'] if k not in s];[sys.exit('forbidden '+k) for k in ['107','122','/features','/kpis'] if k in s]"` — PASS.
- **T-28:** `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/work-view.test.tsx && npm --prefix .claude/skills/harness/bin/dashboard/client run build` — PASS: 5 tests; Vite build succeeded.

Changed paths: `client/src/api.ts`, `client/src/routes.tsx`, `client/src/routes.test.tsx`, `client/src/tiles.tsx`, and regenerated `client/dist/`.

Commit/head SHA: recorded in the terminal handoff after this receipt is committed.
