# T-32 round 5 c6 UI receipt

## Result

**FAIL — the exact lane completed 21/23, so the conditional independent `ui_contract.py gate` was not run.** Both `VIS-DENSITY: initial-request-error` cases exceeded their signed 210000ms timeout while the inspection loop tried to capture the subsequent `table-overflow` surface against a closed page.

## Exact lane command and output

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=2026-09-22-t32-round5-eng npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui
```

```text
Running 23 tests using 6 workers
2 failed
21 passed (3.9m)
```

Exact failures (one per project):

```text
[desktop-1440] feat-53.e2e.spec.ts:108:3 › dense hierarchy and qualitative states match DESIGN › VIS-DENSITY: initial-request-error
Test timeout of 210000ms exceeded.
Error: every signed inspection setup and capture must execute
initial-request-error: page.addStyleTag: Target page, context or browser has been closed
table-overflow: page.addStyleTag: Target page, context or browser has been closed

[desktop-1920] feat-53.e2e.spec.ts:108:3 › dense hierarchy and qualitative states match DESIGN › VIS-DENSITY: initial-request-error
Test timeout of 210000ms exceeded.
Error: every signed inspection setup and capture must execute
initial-request-error: page.addStyleTag: Target page, context or browser has been closed
table-overflow: page.addStyleTag: Target page, context or browser has been closed
```

The complete captured lane output is `artifact://3950` in this execution record.

## Results and artifact inventory

`ui/results.json` reports:

```json
{"status":"failed","check_count":23,"missing_check_ids":[]}
```

The two result errors are evidence-label mismatches for `desktop-1440/VIS-DENSITY` and `desktop-1920/VIS-DENSITY`: expected `overview-default,kpi-unavailable,work-detail-long-content,filtered-zero,source-error-with-valid-rows,initial-request-error,table-overflow`; observed the first five only.

- Referenced WebP paths: 37. `jq -r '.. | objects | .path? // empty' results.json | wc -l` output: `37`.
- Referenced WebP validation: `jq -r '.. | objects | .path? // empty' results.json | xargs -n 1 test -s` exited 0 (every referenced WebP exists and is nonempty).
- Trace ZIP count: 8/8; all nonempty (`test -s` for each ZIP exited 0).

```text
A11Y-AXE--desktop-1440.zip 12733787 bytes
A11Y-AXE--desktop-1920.zip 12016212 bytes
C3-KEYBOARD--desktop-1440.zip 10773485 bytes
C3-KEYBOARD--desktop-1920.zip 7308814 bytes
TBL-DESKTOP--desktop-1440.zip 2660294 bytes
TBL-DESKTOP--desktop-1920.zip 1929112 bytes
VIS-PROTOTYPE--desktop-1440.zip 1751485 bytes
VIS-PROTOTYPE--desktop-1920.zip 1383911 bytes
```

## Independent gate

Not run: the signed instruction makes it conditional on 23/23; the exact lane returned nonzero at 21/23. Therefore there is no truthful `UI GATE: PASS` receipt.
