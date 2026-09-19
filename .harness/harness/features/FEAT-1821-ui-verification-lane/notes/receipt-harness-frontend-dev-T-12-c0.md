# T-12 receipt

## Result

`tables-a11y.e2e.spec.ts` contains the sole TBL-DESKTOP and A11Y-AXE checks, with named steps, soft assertions, and WebP capture after each check. The required list verification is currently blocked by Playwright discovery: `playwright.config.ts` has `testMatch: 'feat-53.e2e.spec.ts'`, so the immutable T-12-owned `e2e/tables-a11y.e2e.spec.ts` cannot be discovered without a configuration change outside this task's ownership.

## Focused RED and task verify

```sh
sh -c '
out=$(HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t12-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list e2e/tables-a11y.e2e.spec.ts) &&
printf "%s\n" "$out" &&
test "$(printf "%s\n" "$out" | sed -n "s/^Total: \([0-9][0-9]*\) tests.*/\1/p")" = 4 &&
test "$(printf "%s\n" "$out" | grep -F -c "desktop tables contain overflow and keep ID sticky")" = 2 &&
test "$(printf "%s\n" "$out" | grep -F -c "routes pass axe and expose non-colour equivalents")" = 2
'
```

Output (both the pre-implementation RED and post-implementation required verification):

```text
Error: No tests found.
Make sure that arguments are regular expressions matching test files.
You may need to escape symbols like "$" or "*" and quote the arguments.
```

Exit status: 1.

## Files

- `.claude/skills/harness/bin/dashboard/client/e2e/tables-a11y.e2e.spec.ts`
