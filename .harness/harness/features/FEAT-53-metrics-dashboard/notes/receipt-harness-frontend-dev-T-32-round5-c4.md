# FEAT-53 T-32 round 5 c4 receipt

## Result

The one permitted exact full lane did **not** satisfy the signed gate: 21 passed, 2 failed. Both failures are `VIS-DENSITY` (`desktop-1440` and `desktop-1920`), which time out after the first `overview-default` capture. This is a test-harness/predicate sequencing failure (`page.addStyleTag: Target page, context or browser has been closed` after the test closes), not an observed product-source failure. No source or predicate was changed, and no commit was made.

## Exact signed lane

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=2026-09-22-t32-round5-eng npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui
```

```text
> test:ui
> playwright test --config playwright.config.ts

Running 23 tests using 6 workers

2 failed
21 passed (55.0s)

exit 1
```

The two failed checks report `Test timeout of 30000ms exceeded`; each records `overview-default` only, then every remaining signed inspection capture fails with `page.addStyleTag: Target page, context or browser has been closed`.

The independent `ui_contract.py gate` was not run: the signed procedure makes it contingent on a 23/23 lane result, which did not occur. `UI GATE: PASS` was therefore not obtained. The signed `git ls-files` tracking clause was intentionally not run under the direct no-commit assignment.

## Programmatic bundle inventory

```sh
jq -r '"summary.status=" + .summary.status, "check_count=" + (.summary.check_count|tostring), "referenced_webp_count=" + ([.checks[].screenshots[]?.path]|length|tostring), "unique_referenced_webp_count=" + ([.checks[].screenshots[]?.path]|unique|length|tostring), "trace_count=" + ([.checks[].trace]|map(select(. != null))|length|tostring), "unique_trace_count=" + ([.checks[].trace]|map(select(. != null))|unique|length|tostring)' .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-22-t32-round5-eng/ui/results.json && jq -r '[.checks[].screenshots[]?.path] | unique[]' .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-22-t32-round5-eng/ui/results.json | xargs -n 1 stat -f '%z %N' && jq -r '[.checks[].trace] | map(select(. != null)) | unique[]' .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-22-t32-round5-eng/ui/results.json | xargs -n 1 stat -f '%z %N'
```

```text
summary.status=failed
check_count=23
referenced_webp_count=29
unique_referenced_webp_count=29
trace_count=8
unique_trace_count=8
```

All 29 `results.json`-referenced WebP paths exist (the `stat` stage exited 0). They are under `runs/2026-09-22-t32-round5-eng/ui/evidence/{desktop-1440,desktop-1920}/`; the two failed `VIS-DENSITY` records each contain only `VIS-DENSITY--overview-default.webp`, producing the results summary's expected-label mismatch.

Eight referenced trace ZIPs exist and are nonempty:

```text
12646181 traces/A11Y-AXE--desktop-1440.zip
11959215 traces/A11Y-AXE--desktop-1920.zip
10364118 traces/C3-KEYBOARD--desktop-1440.zip
 7055059 traces/C3-KEYBOARD--desktop-1920.zip
 2654544 traces/TBL-DESKTOP--desktop-1440.zip
 1810868 traces/TBL-DESKTOP--desktop-1920.zip
 1771061 traces/VIS-PROTOTYPE--desktop-1440.zip
 1391974 traces/VIS-PROTOTYPE--desktop-1920.zip
```

Artifacts: `runs/2026-09-22-t32-round5-eng/ui/results.json`, its 29 referenced WebPs, and the eight ZIPs above.

## Principles applied

None; this exact-evidence run made no design or implementation decision.
