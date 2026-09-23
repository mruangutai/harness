# T-40 receipt

C3 now sets a 120-second aggregate timeout before its applicability skip.

## Verification

Command:
```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t40-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list | grep -c "›" # still 23 titles at both projects
git diff --stat HEAD -- .claude/skills/harness/bin/dashboard/client/e2e | grep -c "keyboard.e2e.spec.ts" # only this spec changed by this task
```

Verbatim output:
```text
23
1
```
