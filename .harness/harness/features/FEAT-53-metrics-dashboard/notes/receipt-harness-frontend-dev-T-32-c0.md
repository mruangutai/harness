# T-32 frontend receipt

## Result

FAIL — the required 23/23 lane and independent gate were not reached in this retry.

## Commands and output

```sh
npm run build && HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t32focusgeometry npm run test:ui -- e2e/geometry.e2e.spec.ts
```

Exit 1: geometry predicate failed on both desktop projects: Repository selector width was 21.21875px; KPI tile links carried query strings; tile-link widths were unequal.

```sh
npm run build && HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t32focusgeometry2 npm run test:ui -- e2e/geometry.e2e.spec.ts e2e/colour-placement.e2e.spec.ts e2e/contrast-hatch.e2e.spec.ts
```

Exit 1: 2 passed, 10 failed. Header selector width and plain KPI href were repaired; root theme token resolution and unavailable-state fixture/surface remain red.

```sh
npm run build
```

Exit 0; generated `dist/index.html`, `dist/assets/index-BGeYwNXA.css`, and `dist/assets/index-RURx1cXv.js`.

## Remaining blocker

The theme provider emits custom metric tokens on its wrapper, while `C3-CONTRAST` reads them from `html`; the attempted wrapper-to-root computed-value propagation was implemented and compiles, but was not re-run after its final correction. The exact lane, independent gate, round2 results bundle, WebP inventory, and trace inventory were not generated.

## Changed files

- `.claude/skills/harness/bin/dashboard/client/src/main.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/routes.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/tiles.tsx`
- `.claude/skills/harness/bin/dashboard/client/dist/index.html`
- `.claude/skills/harness/bin/dashboard/client/dist/assets/index-BGeYwNXA.css`
- `.claude/skills/harness/bin/dashboard/client/dist/assets/index-RURx1cXv.js`

## Principles applied

- Attack the Premise: tested the shared fixture/theme mounting premise before applying local predicate-specific tweaks.
- Experience First: retained the established route and header interaction while correcting consumer-visible geometry.
