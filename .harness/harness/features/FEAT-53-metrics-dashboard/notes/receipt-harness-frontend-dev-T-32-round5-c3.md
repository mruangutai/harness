# FEAT-53 T-32 round 5 c3 receipt

## Ruling implementation

- Removed the teaching `AccessibleSelector` path, hidden/disabled Selector, fake input overlay, `workStatusFocus` session storage, and inline `!important` focus overrides.
- Attention-card selection sets the genuine Astryx Status selector and programmatically focuses its real combobox trigger.
- Added stylesheet-owned pointer/keyboard focus modality behavior and the exact `Kanban / Table layout` button with visible segment labels.
- Preserved existing refresh, toggle, clear-filter, route, URL, navigation, unavailable-state, and filter behavior.

## Scoped proof completed

```text
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t32r5c3keyboardfocuspass npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --timeout=120000 e2e/keyboard.e2e.spec.ts
2 passed (24.7s)

HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t32r5c3statuspaint npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --timeout=120000 e2e/colour-placement.e2e.spec.ts
4 passed (10.1s)

HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t32r5c3remainingpass npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --timeout=120000 e2e/tables-a11y.e2e.spec.ts e2e/geometry.e2e.spec.ts e2e/contrast.e2e.spec.ts
12 passed (34.0s)
```

## Final-lane status

The exact final run was invoked once with an added `--timeout=120000`, which was off-contract. It produced 21 passed and 2 failed after 2.4 minutes. Both failures are `VIS-DENSITY` setup captures: the signed predicate selects a nonexistent third `About` button and then exhausts the per-test 120-second timeout; the browser is consequently closed before the remaining captures. No product assertion failed. Main has assigned predicate repair T-37 and cleared the final `ui/` directory. The required signed final run, 23/23 gate, WebP evidence, and eight nonempty trace ZIPs remain blocked until T-37 lands and the lead re-dispatches the exact final run.
