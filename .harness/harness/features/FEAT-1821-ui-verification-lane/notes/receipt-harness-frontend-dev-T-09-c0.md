# T-09 receipt

## Result

`BLOCKED`: the required test file was created and the configured discovery remains unable to select it because `playwright.config.ts` restricts `testMatch` to `feat-53.e2e.spec.ts`. T-09's immutable ownership forbids changing that configuration.

## Focused RED and task verify

Command (verbatim):

```sh
sh -c '
out=$(HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t09-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list e2e/colour-placement.e2e.spec.ts) &&
printf "%s\n" "$out" &&
test "$(printf "%s\n" "$out" | sed -n "s/^Total: \([0-9][0-9]*\) tests.*/\1/p")" = 4 &&
test "$(printf "%s\n" "$out" | grep -F -c "KPI identity hues stay on identity marks")" = 2 &&
test "$(printf "%s\n" "$out" | grep -F -c "status hue stays on attention labels")" = 2
'
```

Output (verbatim):

```text
Error: No tests found.
Make sure that arguments are regular expressions matching test files.
You may need to escape symbols like "$" or "*" and quote the arguments.
```

Exit: 1

The command was run before the new spec existed to establish RED. After adding the spec, rerunning it cannot change discovery until its out-of-scope `testMatch` excludes no `e2e/*.e2e.spec.ts` files. No smoke run is possible through the configured lane under that condition.
