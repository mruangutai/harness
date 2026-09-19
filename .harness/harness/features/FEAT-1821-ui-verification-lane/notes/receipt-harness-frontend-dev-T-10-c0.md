# T-10 receipt

## Status

BLOCKED: `playwright.config.ts` matches only `feat-53.e2e.spec.ts`, so the required sole-owned `e2e/keyboard.e2e.spec.ts` is not discoverable. T-10 prohibits editing configuration or any file other than the owned spec.

## Focused RED command

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t10-red npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/keyboard.e2e.spec.ts
```

```text
> test:ui
> playwright test --config playwright.config.ts e2e/keyboard.e2e.spec.ts

[WebServer] WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
[WebServer]  * Running on http://127.0.0.1:8972
[WebServer] Press CTRL+C to quit
Error: No tests found.
Make sure that arguments are regular expressions matching test files.
You may need to escape symbols like "$" or "*" and quote the arguments.
```

The new spec encodes C3-KEYBOARD with named steps, soft expectations, final WebP attachment, focus/outline assertions, and all signed transitions. The exact list verify cannot run until test discovery includes `e2e/*.e2e.spec.ts`.
