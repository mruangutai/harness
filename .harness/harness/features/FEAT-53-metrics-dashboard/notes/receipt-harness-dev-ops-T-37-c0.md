# T-37 receipt

`kpi-unavailable` now scopes its About-button lookup to the `Blocking Human Touchpoints` panel heading's parent and selects its first disclosure. The overview `disclosure-open` lookup remains `.last()`.

## Signed verify

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t37-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list | grep -c "›" # still 23 titles at both projects
git diff --stat HEAD -- .claude/skills/harness/bin/dashboard/client | grep -c "feat-53.e2e.spec.ts" # only this spec changed by this task
```

Output:

```text
23
1
```

## Focused diff

```sh
git diff -- .claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts
```

The target spec has one changed hunk: the unavailable branch replaces `.nth(2)` with the panel-heading-scoped `.first()` locator. No other line in that spec changed.

## Principles applied

None. Attack the Premise's repeated-fix premise does not apply: this task provides one concrete locator defect and one required local locator shape.
