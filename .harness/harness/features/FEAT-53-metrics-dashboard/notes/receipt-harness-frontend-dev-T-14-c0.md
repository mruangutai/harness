# T-14 receipt

KPI content modules provide the seven tile links, panel/table compositions, and payload-map-driven S-1–S-4 treatments. The focused rendered-surface test passed: `gapstates.test.tsx` confirms unavailable values render `—`, the unavailable badge, and their specific reason rather than a zero; `kpi-content.test.tsx` renders all seven KPI links and measured zero without an unavailable marker.

## Evidence

- Focused smoke: `npm run test -- kpi-content.test.tsx gapstates.test.tsx` → 2 files, 2 tests passed.
- Build output: `vite v8.3.0 building client environment for production... ✓ 2599 modules transformed. dist/index.html 0.32 kB; dist/assets/index-DzoXKmQ_.js 697.35 kB; ✓ built in 171ms.` (The pre-existing large-chunk warning remained.)
- Source commit: `7974fffa feat(dashboard): add KPI panel surfaces`.
- Files touched: `.claude/skills/harness/bin/dashboard/client/src/{gapstates,gapstates.test,kpi-content.test,panels,tables,tiles}.tsx`.

## Exact task verification

The exact T-14 command was run verbatim. Its build portion passed, then its source scan failed with `forbidden /features` because it scans every `src/**/*.tsx`, including T-13-owned `routes.test.tsx`, which deliberately asserts retired `/features` and `/kpis` paths are unregistered. T-14 source contains none of the forbidden literals.

DEC-229-eligible stale-path amendment: task `T-14`; field `verify`; was `forbid /features and /kpis across all src/**/*.tsx`; now `forbid them only in runtime production modules, excluding T-13 retired-route regression assertions`; reason `the current command cannot pass without editing a T-13-owned test that is explicitly outside T-14 scope`.
