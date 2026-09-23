# T-38 receipt

## Result

Inspection rows now receive a 30-second-per-capture timeout before their execution loop in `.claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts:112`.

## Signed verification

Command:
```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t38-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list | grep -c "›" # still 23 titles at both projects
```

Verbatim output:
```text
23
```

Command:
```sh
git diff --stat HEAD -- .claude/skills/harness/bin/dashboard/client | grep -c "feat-53.e2e.spec.ts" # only this spec changed by this task
```

Verbatim output:
```text
1
```
