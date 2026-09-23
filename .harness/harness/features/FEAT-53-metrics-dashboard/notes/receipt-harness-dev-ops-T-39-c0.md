# T-39 receipt

Initial-request-error now intercepts only `**/api/work*` before its load with the signed 500 JSON fixture and unregisters that route in `inspection` after evidence capture; the existing Retry focus-only interaction remains unchanged. `feat-53.e2e.spec.ts:97-114`.

## Verification

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t39-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list | grep -c "›" # still 23 titles at both projects
git diff --stat HEAD -- .claude/skills/harness/bin/dashboard/client | grep -c "feat-53.e2e.spec.ts" # only this spec changed by this task
```

Verbatim output:

```text
23
1
```

Focused `git diff -- .claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts` shows the signed route fixture/unroute hunk and preserved concurrent T-37/T-38 hunks only.

## Open questions

None.
