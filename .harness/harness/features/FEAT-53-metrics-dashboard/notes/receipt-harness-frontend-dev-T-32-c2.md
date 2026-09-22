# FEAT-53 T-32 frontend cycle 2 receipt

## Result

**BLOCKED — binding UI predicate contradicts the immutable DESIGN contract.**

## Work completed

- Restored actual client rendering by importing `createRoot` in `src/main.tsx`; the earlier theme/root-token symptom was a render crash, not an Astryx theme propagation defect.
- Moved the root token probe to `document.body`, allowing rendered Astryx/theme colours to propagate to the required root custom properties.
- Corrected the unavailable hatch in `src/gapstates.tsx` to use a 45-degree, 1px unavailable-stroke band on a 6px repeat.

## Scoped evidence

1. `npm run build && HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t32-postfix-c3c4d npm run test:ui -- e2e/contrast-hatch.e2e.spec.ts`
   - build passed
   - **4 passed**: C3 contrast and C4 hatch at both desktop widths.
2. `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t32-colour-geometry npm run test:ui -- e2e/colour-placement.e2e.spec.ts e2e/geometry.e2e.spec.ts`
   - DIR-KPI failure is irreconcilable with DESIGN: its `expectNoOtherPaint` excludes only `[data-kpi-identity-mark="N"]`, then treats the required descendant dot, accent, sparkline paths, end dot, Shape B line/y-title, and column dot as prohibited non-identity paint. DESIGN §Colour placement explicitly requires those descendants.
   - DIR-STATUS additionally fails because DESIGN’s immutable palette deliberately assigns both `kpi-4` and `status-over-budget` `#F58BC2` (DESIGN token table lines 119 and 126), while the predicate requires that computed colour occur only on one selector at a time.
   - KPI-R1 also remains red: 1440 second-row and 1920 both rows report unequal anchor widths; this is reachable work but cannot create an all-green binding lane while the colour predicate is self-contradictory.
3. `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t32-full-diagnostic npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui`
   - 7 passed, 16 failed. The successful C3/C4 results confirm the render/root/hatch repair. Later tables, a11y, keyboard, and visual checks time out after the unresolved lane failures; final UI bundle was intentionally not cleared/generated.

## Required assigning resolution

Either change the binding colour predicate’s allowed selector to include all required identity-mark descendants and handle the intentional `kpi-4`/`status-over-budget` shared colour, or change DESIGN’s immutable palette/placement contract. Client code cannot satisfy both.

## Principles applied

- **Attack the Premise** — validated the rendered root/theme premise with C3 instead of layering further theme overrides; the proven cause was the missing React root import.
- **Experience First** — exercised real rendered overview, KPI, and work-detail routes through C3/C4; hatch, route rendering, and focus-capable client state were checked in-browser.

## Files touched

- `.claude/skills/harness/bin/dashboard/client/src/main.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/gapstates.tsx`
- `.claude/skills/harness/bin/dashboard/client/dist/**`
- this receipt
