# Receipt — simplify apply: centralize WebP capture

## Outcome

The five permitted hard-failure paths use `ui-evidence.ts`'s `captureHardFailureEvidence`; the keyboard spec was excluded and remains on its deliberately separate soft-capture path.

## Files touched

- `.claude/skills/harness/bin/dashboard/client/ui-evidence.ts`
- `.claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts`
- `.claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts`
- `.claude/skills/harness/bin/dashboard/client/e2e/contrast-hatch.e2e.spec.ts`
- `.claude/skills/harness/bin/dashboard/client/e2e/geometry.e2e.spec.ts`
- `.claude/skills/harness/bin/dashboard/client/e2e/tables-a11y.e2e.spec.ts`

## Proof

- `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=simplify-discovery npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list feat-53.e2e.spec.ts e2e/colour-placement.e2e.spec.ts e2e/contrast-hatch.e2e.spec.ts e2e/geometry.e2e.spec.ts e2e/tables-a11y.e2e.spec.ts` — passed; discovered 21 tests in five files.
- `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=simplify-top-level-proof npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- feat-53.e2e.spec.ts --project=desktop-1440 --grep 'component source uses only theme tokens'` — passed; produced `SRC-TOKENS--execution.webp`, verified by `file` as `RIFF (little-endian) data, Web/P image`.
- `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=simplify-e2e-proof npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/geometry.e2e.spec.ts --project=desktop-1440 --grep 'shared header geometry matches DESIGN'` — expected existing assertion red (missing `header` timed out); its `afterEach` emitted `evidence:C1-HEADER-GEOMETRY:execution`, and `C1-HEADER-GEOMETRY--execution.webp` validated as RIFF/WebP.

## Assertion audit and cleanup

No assertion bodies, titles, locations, or soft/hard expectation choices were changed; only duplicate capture helpers, now-obsolete imports/constants, and their call sites changed. The keyboard spec was not edited or migrated. The shared helper preserves animation suppression, CDP WebP capture beyond the viewport, feature/run path resolution, duplicate refusal, RIFF/WEBP validation, write, and attachment naming. Main removed both scratch run directories and client test outputs; a final run-directory read shows only committed `FEAT-1821-initial-red`, and the scratch-run glob is empty.
