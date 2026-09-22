# T-13 receipt — reporter fails closed

## RED

Before reporter hardening, the required probe command failed: all seven cases stopped at `ERR_MODULE_NOT_FOUND` for `ui-manifest.js`, proving the Node probe could not exercise the reporter path.

## Verify

Command:

```sh
node --experimental-strip-types --test .claude/skills/harness/bin/dashboard/client/ui-reporter.probe.spec.ts
```

Output:

```text
✔ missing record
✔ duplicate
✔ mismatched title
✔ empty WebP
✔ parser error
✔ reporter error
✔ incomplete accounting
ℹ tests 7
ℹ pass 7
ℹ fail 0
```

Each case builds a temporary defective bundle, uses `UiReporter.onBegin`/`onTestEnd`/`onEnd` to emit its real `results.json`, asserts `summary.status === 'failed'` and its defect error, then invokes the real `ui_contract.py gate` on that emitted bundle and observes nonzero refusal. The parser case copies the real reporter and manifest loader into a temporary root with no DESIGN.md, producing the loader's actual parser-error path.

Focused browser discovery:

```sh
npx playwright test --list
```

Output ends `Total: 23 tests in 1 file`; every listed test is in `feat-53.e2e.spec.ts`, so this Node probe adds zero Playwright tests.
