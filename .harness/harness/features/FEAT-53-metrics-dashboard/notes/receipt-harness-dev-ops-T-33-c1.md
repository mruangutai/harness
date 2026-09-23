# T-33 c1 verification receipt

## Result

`colour-placement.e2e.spec.ts` now asserts icon, count, background, border, top-line, and selected treatment against `--color-neutral` before and after selection for every signed status pair. Each selected state re-scans KPI and status authored-token ownership.

Changed source: `.claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts`.

## Signed verification

```text
$ HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t33-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list | grep -c "›"
23

$ git diff --stat HEAD -- .claude/skills/harness/bin/dashboard/client | grep -c "e2e/colour-placement.e2e.spec.ts"
1
```

The list remains 23 project-expanded titles; the signed client-scope leg reports one matching changed spec.

## Focused UI evidence

```text
$ HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t33-focused-c1 npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/colour-placement.e2e.spec.ts
2 failed
2 passed (15.3s)
exit 1
```

The two passing project-expanded tests are `DIR-STATUS-LABEL`; they exercise all six cards, every named neutral role before and after selection, and the selected-state ownership re-scan. The two failing project-expanded tests are only `DIR-KPI-IDENTITY`: in both desktop projects all seven `data-kpi-panel-accent` winning `border-top-color` declarations are `currentcolor`, not their required `var(--color-metrics-kpi-N)`. This is the legitimate pre-existing T-32 application defect required to remain red, not a T-33 predicate failure or an indirect-inheritance exemption.

Failure evidence was captured for the two KPI failures; this run had no duplicate-label or other failure-evidence collision. No build, formatter, linter, project-wide suite, or commit was run.

## Principles applied

- Foundational Thinking: represented the six required neutral role/property pairs as one data list, making both pre- and post-selection assertions exact and symmetric.
