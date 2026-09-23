# T-34 receipt

The C3-KEYBOARD noncontrol assertion now checks every matching locator element for `aria-hidden="true"` and `tabIndex === -1`; the focused run no longer reports strict mode for `svg, [data-chart], [data-unavailable], [data-status-badge]`.

## Verification

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t34-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list | grep -c "›"
```

```text
23
```

```sh
git diff --stat HEAD -- .claude/skills/harness/bin/dashboard/client/e2e | grep -c "keyboard.e2e.spec.ts"
```

```text
1
```

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t34-keyboard npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/keyboard.e2e.spec.ts --grep "keyboard focus transitions and restoration match DESIGN" --project=desktop-1440 --project=desktop-1920
```

```text
2 failed
Command exited with code 1
```

The focused run exercised both configured desktop projects. It contains no `charts and named noncontrols` failure and no strict-mode violation for the repaired multi-element locator. It still reports unrelated product assertion failures: duplicate `Clear Filters` locators and missing table controls on desktop-1440; incorrect tab stop/focus-ring state plus duplicate `Clear Filters` locators on desktop-1920. Trace and evidence captures were produced for both projects under `test-results/playwright-artifacts/`.

```sh
git diff --check HEAD -- .claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts && git diff --unified=0 HEAD -- .claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts
```

```text
1 file changed, 6 insertions(+), 1 deletion(-)
```

Scoped inspection confirms the sole hunk replaces the impossible aggregate attribute assertion with per-element `aria-hidden` and non-focusability assertions. No title, applicability, ordering/restoration assertion, project, evidence, or trace rule changed.

## Principles applied

- Delete First: replaced only the strict-mode-invalid assertion with the smallest local per-element loop; no helper or abstraction was added.

```yaml
VERDICT: PASS
DIGEST:
  headline: Every matched noncontrol is individually asserted aria-hidden and non-focusable without the invalid multi-element strict-mode assertion.
  change_type: infra
  applied: [.claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts]
  suite: fail
  task: T-34
  task_verify: pass
  test_kinds_written: []
  open_questions:
    - { id: Q1, question: "Focused C3-KEYBOARD still has unrelated product assertion failures in both desktop projects; this task explicitly excludes repairing them.", blocking: false }
  files_touched: [.claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-dev-ops-T-34-c0.md
```
