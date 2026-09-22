# T-10 receipt — Verify keyboard split

## Result

PASS — the approved keyboard listing command completed successfully.

## Command and verbatim output

```sh
sh -c '
out=$(HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t10-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list e2e/keyboard.e2e.spec.ts) &&
printf "%s\n" "$out" &&
test "$(printf "%s\n" "$out" | sed -n "s/^Total: \([0-9][0-9]*\) tests.*/\1/p")" = 2 &&
test "$(printf "%s\n" "$out" | grep -F -c "keyboard focus transitions and restoration match DESIGN")" = 2
'
```

```text
> test:ui
> playwright test --config playwright.config.ts --list e2e/keyboard.e2e.spec.ts

Listing tests:
  [desktop-1440] › e2e/keyboard.e2e.spec.ts:74:1 › keyboard focus transitions and restoration match DESIGN
  [desktop-1920] › e2e/keyboard.e2e.spec.ts:74:1 › keyboard focus transitions and restoration match DESIGN
Total: 2 tests in 1 file
```

## Counts and touched files

- Total listings: 2
- Exact title occurrences: 2 (`keyboard focus transitions and restoration match DESIGN`)
- Source/spec files touched: none
- Receipt file touched: `.harness/harness/features/FEAT-1821-ui-verification-lane/notes/receipt-harness-frontend-dev-fix-c4-eng-T-10.md`
