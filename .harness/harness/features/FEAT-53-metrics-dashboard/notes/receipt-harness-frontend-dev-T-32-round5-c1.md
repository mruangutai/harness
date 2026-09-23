# T-32 round 5 cycle 1 receipt

## Verdict
FAIL. The exact lane is 0/23, and `ui_contract.py gate` reports `UI GATE: FAIL`.

## Commands and results

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t32c1-c3 npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/keyboard.e2e.spec.ts
npm --prefix .claude/skills/harness/bin/dashboard/client run build
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=2026-09-22-t32-round5-eng npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui
python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-22-t32-round5-eng/ui/results.json --feature FEAT-53-metrics-dashboard --run-id 2026-09-22-t32-round5-eng --served-bundle-commit "$(git rev-parse HEAD)" --repo-root . --client-package .claude/skills/harness/bin/dashboard/client
```

The focused browser run fixed the pointer-opened Station Selector ring failures. The remaining C3 failures are the attention-card Status restoration, the check's unsupported `toHaveValue` assertion against Astryx's button-backed `role=combobox`, and the check's strict single-`[aria-live=polite]` assumption while Astryx renders 30 polite live nodes. The exact run could not be cleared first: the write guard rejected the dispatch-authorized exact `ui/` bundle as outside this agent domain. Its stale evidence then caused all other checks to fail publication with duplicate evidence labels.

## Exact artifact inventory

`results.json` exists and records `check_count: 23`, `summary.status: failed`, no missing check IDs, zero accepted screenshot rows, and incomplete accounting. The bundle has eight nonempty ZIPs: `A11Y-AXE--desktop-1440.zip` 11.9MB, `A11Y-AXE--desktop-1920.zip` 11.3MB, `C3-KEYBOARD--desktop-1440.zip` 7.7MB, `C3-KEYBOARD--desktop-1920.zip` 5.2MB, `TBL-DESKTOP--desktop-1440.zip` 2.4MB, `TBL-DESKTOP--desktop-1920.zip` 1.6MB, `VIS-PROTOTYPE--desktop-1440.zip` 1.2MB, and `VIS-PROTOTYPE--desktop-1920.zip` 860KB. Referenced WebP evidence was not accepted by results because stale files blocked publication.

## Round-6 prescription

1. Repair the feature-run `ui/**` domain grant so the exact bundle can be removed before every exact lane.
2. Reconcile the C3 predicate with Astryx's button-backed Selector or provide an Astryx-conformant input-backed Selector; `toHaveValue` cannot run on the current role-bearing button.
3. Make attention filtering schedule focus after router/render completion, then preserve pointer no-ring state on the final Status control.
4. Scope the live-region assertion to the product result-count region or remove Astryx's generated duplicate polite status nodes through the substrate; do not weaken other checks.
5. Rerun focused C3, A11Y, density, and prototype checks with fresh run IDs, then clear the exact bundle and run the full lane and independent gate.

## Changed files

- `.claude/skills/harness/bin/dashboard/client/src/routes.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/work-view.tsx`
- `.claude/skills/harness/bin/dashboard/client/dist/**`
- removed `.claude/skills/harness/bin/dashboard/client/dom-focus-census.mjs`

## Principles applied

- Experience First: retained keyboard/pointer-specific focus behavior rather than collapsing both modalities.
