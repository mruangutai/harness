# T-09 verification receipt

T-09 passed without an edit: the colour-placement spec discovers exactly four tests, two per approved title.

## Command

```sh
sh -c '
out=$(HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t09-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list e2e/colour-placement.e2e.spec.ts) &&
printf "%s\n" "$out" &&
test "$(printf "%s\n" "$out" | sed -n "s/^Total: \([0-9][0-9]*\) tests.*/\1/p")" = 4 &&
test "$(printf "%s\n" "$out" | grep -F -c "KPI identity hues stay on identity marks")" = 2 &&
test "$(printf "%s\n" "$out" | grep -F -c "status hue stays on attention labels")" = 2
'
```

## Verbatim result

```text
> test:ui
> playwright test --config playwright.config.ts --list e2e/colour-placement.e2e.spec.ts

Listing tests:
  [desktop-1440] › e2e/colour-placement.e2e.spec.ts:122:3 › KPI identity hues stay on identity marks
  [desktop-1440] › e2e/colour-placement.e2e.spec.ts:122:3 › status hue stays on attention labels
  [desktop-1920] › e2e/colour-placement.e2e.spec.ts:122:3 › KPI identity hues stay on identity marks
  [desktop-1920] › e2e/colour-placement.e2e.spec.ts:122:3 › status hue stays on attention labels
Total: 4 tests in 1 file


Wall time: 1.33 seconds
```

## Counts and touched files

- Total listings: 4
- `KPI identity hues stay on identity marks`: 2
- `status hue stays on attention labels`: 2
- T-09 owned spec edits: none
- Files touched: `.harness/harness/features/FEAT-1821-ui-verification-lane/notes/receipt-harness-frontend-dev-fix-c4-eng-T-09.md`
