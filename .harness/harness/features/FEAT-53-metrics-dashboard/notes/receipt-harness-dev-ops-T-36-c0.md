# T-36 receipt — correct Status value predicate

## Result

The Status predicate now observes the button-backed combobox's rendered selected label and its polite live announcement, rather than an inapplicable input value.

## Assertion change

- Before: `expect.soft(status, 'Status selection is announced by value').toHaveValue('needs-you')`
- After: the focused Status combobox contains `Needs You`, and `[aria-live="polite"]` contains `Needs You` as the selection announcement.

All other clauses, titles, order, projects, evidence, and trace requirements remain untouched. The same-file diff also contains the intentional pre-existing T-33/T-34/T-35 edits.

## Signed verification

Command:
```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t36-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list | grep -c "›" # still 23 titles at both projects
```
Output:
```text
23
```

Command:
```sh
git diff --stat HEAD -- .claude/skills/harness/bin/dashboard/client/e2e | grep -c "keyboard.e2e.spec.ts" # only this spec changed by this task
```
Output:
```text
1
```

Focused source/diff check:
```sh
git diff --check HEAD -- .claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts && git diff HEAD -- .claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts
```
Output:
```diff
diff --git a/.claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts b/.claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts
index 75eb1972..cd4a071e 100644
--- a/.claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts
+++ b/.claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts
@@ -89,7 +89,12 @@ test('keyboard focus transitions and restoration match DESIGN', async ({ page },
-    await expect.soft(page.locator('svg, [data-chart], [data-unavailable], [data-status-badge]'), 'charts and named noncontrols are aria-hidden').toHaveAttribute('aria-hidden', 'true');
+    const noncontrols = page.locator('svg, [data-chart], [data-unavailable], [data-status-badge]');
+    for (let index = 0; index < await noncontrols.count(); index += 1) {
+      const noncontrol = noncontrols.nth(index);
+      await expect.soft(noncontrol, 'charts and named noncontrols are aria-hidden').toHaveAttribute('aria-hidden', 'true');
+      await expect.soft(noncontrol, 'charts and named noncontrols are not focusable').toHaveJSProperty('tabIndex', -1);
+    }
@@ -167,7 +172,8 @@ test('keyboard focus transitions and restoration match DESIGN', async ({ page },
-    await expect.soft(status, 'Status selection is announced by value').toHaveValue('needs-you');
+    await expect.soft(status, 'Status selected value is exposed').toContainText('Needs You');
+    await expect.soft(page.locator('[aria-live="polite"]'), 'Status selection is announced').toContainText('Needs You');
```

`git diff --check` produced no output and exited 0 before the displayed diff. The diff inventory returned one matching spec; the targeted T-36 hunk is the two-line accessible-value/live-region replacement.

## Principles applied

- Attack the Premise: replaced the invalid assumption that a button-backed Astryx combobox has an input value with assertions over its user-observable selected label and announcement.
