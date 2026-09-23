# T-32 round 5 cycle 2 receipt

## Verdict

BLOCKED by the systematic-debugging three-failed-fix cap. The input-backed Astryx-compatible selector surface is discovered by C3, but attention-card activation still leaves `Status` at `all` and unfocused in both browser widths. No exact run was used.

## Hypotheses and evidence

1. The button-backed Astryx `Selector` caused C3's input-only `toHaveValue` failure. An input selector surface over the Astryx control made C3 resolve `input[role=combobox]`; focused runs then passed overview tab order after the existing layout control's label was aligned with its focus handler.
2. Astryx trigger controls caused an extra tab stop. Hiding and disabling the trigger preserved the intended tab order, but did not repair attention filtering.
3. Overview's relative search update preserved an old `status=all`. Replacing it with the explicit overview route update did not change the observed C3 state: the rendered Status input remains `value="all"`, inactive, and has `outline-width: 3px` after Needs You activation.

The third focused browser reproduction (`r5-c2-keyboard-navigation`) failed identically at both widths, so no fourth source-side attempt was made.

## Commands and results

```sh
npm --prefix .claude/skills/harness/bin/dashboard/client run build
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=r5-c2-baseline npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/keyboard.e2e.spec.ts
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=r5-c2-keyboard-built npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/keyboard.e2e.spec.ts
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=r5-c2-keyboard-final npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/keyboard.e2e.spec.ts
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=r5-c2-keyboard-tab npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/keyboard.e2e.spec.ts
npm --prefix .claude/skills/harness/bin/dashboard/client run build
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=r5-c2-keyboard-navigation npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/keyboard.e2e.spec.ts
```

Every listed keyboard command exited 1. The final run records one observed check (`C3-KEYBOARD`) of 12 listed check IDs, with failure at both `desktop-1440` and `desktop-1920`; it is not a full-lane result. Its UI bundle has `results.json`, two nonempty C3 trace ZIPs (6.5MB and 4.6MB), and C3 WebP evidence. It does not contain the required eight traces or a complete result/WebP inventory. The exact `2026-09-22-t32-round5-eng` bundle was not touched.

## Required signed verification

```sh
# Required lane form: HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=<run> npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui
run="${HARNESS_UI_RUN_ID:?Set HARNESS_UI_RUN_ID to the current build run id}" &&
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID="$run" npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui &&
bundle=".harness/harness/features/FEAT-53-metrics-dashboard/runs/$run/ui" &&
python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results "$bundle/results.json" --feature FEAT-53-metrics-dashboard --run-id "$run" --served-bundle-commit "$(git rev-parse HEAD)" --repo-root . --client-package .claude/skills/harness/bin/dashboard/client &&
git ls-files --error-unmatch "$bundle/results.json" "$bundle"/evidence/*.webp "$bundle"/traces/*.zip
```

The final `git ls-files` clause remains intentionally inapplicable because this dispatch forbids committing.

## Files changed

- `.claude/skills/harness/bin/dashboard/client/src/routes.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/work-view.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/main.tsx`
- `.claude/skills/harness/bin/dashboard/client/dist/**`

## Principles applied

- Experience First: retained a focusable value-bearing selector surface rather than suppressing the observed control contract.
- Type System Discipline: kept the selector bridge's value and option contracts explicit.
