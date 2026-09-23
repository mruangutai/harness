# T-32 round 4 receipt

## Result

FAIL. The exact final lane exited 1: 15 passed, 4 failed, 4 inspection-evidence records; `results.json` reports `status: failed`. The independent gate was not run because the signed gate is conditional on a green lane.

## Commands and outputs

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=2026-09-22-t32-round4-eng npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --grep 'keyboard focus transitions' --project=desktop-1440
```

Output: failed, 1 failed (C3-KEYBOARD; 30s timeout after the `in-app KPI and work transitions` clause waits for the dashboard FEAT/BUG row after `/kpi/1` → overview).

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=r4-tables npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --grep 'desktop tables contain overflow' --project=desktop-1440
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=r4-tables npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --grep 'desktop tables contain overflow' --project=desktop-1920
```

Output: passed 1/1 at each width.

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=2026-09-22-t32-round4-eng npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui
```

Output: exit 1; 15 passed, 4 failed, 4 evidence. `UI GATE: NOT RUN` (the required `&&` gate clause was not reached).

## Artifact inventory

- `ui/results.json`: present.
- Referenced WebPs: 29; actual WebPs: 29; every referenced path is present.
- Trace ZIPs: 0 (required: 8); no `ui/traces/` directory was generated because the lane failed.
- No `git ls-files` command was run; artifacts remain uncommitted.

## Remaining reds

- C3-KEYBOARD, desktop-1440 and desktop-1920: after KPI tile activation, the `in-app KPI and work transitions land on unrung h1` clause returns to overview then times out waiting for `getByRole('link', { name: /FEAT|BUG/ }).first()`; replay trace pointers are in `results.json` C3 entries.
- A11Y-AXE, desktop-1440 and desktop-1920: gap treatment check finds one empty `[title]` or `[aria-label]` element.
- VIS-DENSITY, desktop-1440 and desktop-1920: only `overview-default` was captured; six required labels are missing after the 30s setup timeout.
- VIS-PROTOTYPE, desktop-1440 and desktop-1920: inspection setup timed out; the disclosure-open focus assertion did not settle and subsequent setup captures did not complete.

## Files changed

- `.claude/skills/harness/bin/dashboard/client/fixture.ts`
- `.claude/skills/harness/bin/dashboard/client/src/work-view.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/routes.tsx`
- `.claude/skills/harness/bin/dashboard/client/dist/`
- `.harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-22-t32-round4-eng/ui/results.json`
- `.harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-22-t32-round4-eng/ui/evidence/`

## Principles applied

- **Attack the Premise** — the DOM/focus census disproved the prior premise that the predicate was duplicate-only: the rendered dashboard used namespaced item identities, lacked an attention fixture, duplicated Clear Filters in the empty state, and placed Refresh before the layout control. The implementation now exposes one named work identity, a deterministic attention row, one Clear Filters control, one labelled Kanban/Table button, and Refresh after work-list controls.
