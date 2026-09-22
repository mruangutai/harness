# T-12 receipt

## Result

PASS — the approved listing contract discovered exactly four tests: two per required exact title across `desktop-1440` and `desktop-1920`.

## Command

```sh
sh -c '
out=$(HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t12-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list e2e/tables-a11y.e2e.spec.ts) &&
printf "%s\n" "$out" &&
test "$(printf "%s\n" "$out" | sed -n "s/^Total: \([0-9][0-9]*\) tests.*/\1/p")" = 4 &&
test "$(printf "%s\n" "$out" | grep -F -c "desktop tables contain overflow and keep ID sticky")" = 2 &&
test "$(printf "%s\n" "$out" | grep -F -c "routes pass axe and expose non-colour equivalents")" = 2
'
```

## Verbatim output

```text
> test:ui
> playwright test --config playwright.config.ts --list e2e/tables-a11y.e2e.spec.ts

Listing tests:
  [desktop-1440] › e2e/tables-a11y.e2e.spec.ts:51:3 › desktop tables contain overflow and keep ID sticky
  [desktop-1440] › e2e/tables-a11y.e2e.spec.ts:51:3 › routes pass axe and expose non-colour equivalents
  [desktop-1920] › e2e/tables-a11y.e2e.spec.ts:51:3 › desktop tables contain overflow and keep ID sticky
  [desktop-1920] › e2e/tables-a11y.e2e.spec.ts:51:3 › routes pass axe and expose non-colour equivalents
Total: 4 tests in 1 file
```

## Counts

- Total: 4
- `desktop tables contain overflow and keep ID sticky`: 2
- `routes pass axe and expose non-colour equivalents`: 2

## Files touched

- `.harness/harness/features/FEAT-1821-ui-verification-lane/notes/receipt-harness-frontend-dev-fix-c4-eng-T-12.md`

No source, configuration, or specification files were changed.
