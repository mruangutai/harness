# T-32 round 5 c7 receipt

## Verdict

FAIL — exact round-five lane produced 22/23 passed, not the required 23/23. The independent UI gate was not run because its prerequisite is a green lane.

## Exact lane command and output

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=2026-09-22-t32-round5-eng npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui
```

Exit: `1` (55.05s).

```text
Running 23 tests using 6 workers

  1) [desktop-1440] › e2e/keyboard.e2e.spec.ts:80:1 › keyboard focus transitions and restoration match DESIGN

    Test timeout of 30000ms exceeded.

  1 failed
  22 passed (54.4s)
```

Failure evidence: `test-results/playwright-artifacts/e2e-keyboard.e2e-keyboard--7ac3e-nd-restoration-match-DESIGN-desktop-1440/error-context.md`; screenshot attachment: `test-results/playwright-artifacts/e2e-keyboard.e2e-keyboard--7ac3e-nd-restoration-match-DESIGN-desktop-1440/attachments/evidence-C3-KEYBOARD-execution-13b4181bd84533c8cf96eb81ac9a9b9ee8a553a4.webp`; Playwright trace: `test-results/playwright-artifacts/e2e-keyboard.e2e-keyboard--7ac3e-nd-restoration-match-DESIGN-desktop-1440/trace.zip`.

## Gate and bundle validation

`ui_contract.py gate` was intentionally not run: the exact lane was not green.

`runs/2026-09-22-t32-round5-eng/ui/results.json` reports `summary.status: failed`, `check_count: 23`, and `missing_check_ids: []`. It contains 41 screenshot references; all 41 referenced WebPs exist and are nonempty (smallest 44,576 bytes). Eight trace ZIPs exist and are nonempty:

```text
A11Y-AXE--desktop-1440.zip     12693096
A11Y-AXE--desktop-1920.zip     12076051
C3-KEYBOARD--desktop-1440.zip  11537783
C3-KEYBOARD--desktop-1920.zip   7497635
TBL-DESKTOP--desktop-1440.zip   2826731
TBL-DESKTOP--desktop-1920.zip   1929454
VIS-PROTOTYPE--desktop-1440.zip 1914585
VIS-PROTOTYPE--desktop-1920.zip 1387324
```

## Debugging record

Hypothesis: `C3-KEYBOARD` exceeds its fixed 30-second test budget before a clause-level product divergence can be reported, because one long sequential focus/navigation scenario has not completed. Falsifier: a later scoped reproduction identifies a product assertion failure before the 30-second boundary. No source or test changes were made, and the exact lane was not retried.
