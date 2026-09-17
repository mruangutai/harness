# FEAT-53 frontend fix c2 receipt

**Result:** final frontend repair commit `ffd9fb0204701cdae968ef0febc86943fb4829bd` closes the five assigned findings. The evidence below distinguishes earlier recorded red executions from the fresh green executions run at that commit.

## Fail-first and repair evidence

- **V-02 — resolved.** **RED:** `receipt-harness-frontend-dev-fix-c1.md:14` records `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/routes.test.tsx` failing the behavior test **keeps the available dashboard region usable when the other query fails**: no `Repository KPIs unavailable` region was rendered when `/api/kpis` rejected. **GREEN:** at `ffd9fb02`, the same route suite passed **13/13**, including that test and **keeps settled KPI content usable when the work request fails** (`routes.test.tsx:95-123`), which observes the surviving region, error, and usable content for each independent-request failure direction.
- **V-03 — resolved.** **RED:** against pre-repair `7dbb025995b92a45c6a9d4035b56917a00fc7699`, the current live-shaped `routes.test.tsx` run failed 3 tests, including **renders a complete KPI panel and lands focus after an in-app KPI transition**, with the rendered error boundary `Cannot read properties of undefined (reading 'find')`; its payload has top-level `{features, aggregate, trend}`. **GREEN:** the exact route suite at `ffd9fb02` passed **13/13**; that behavior test clicks **Escaped Defects**, observes its level-one landing, the **About Escaped Defects** control, and the `/work/BUG-1` drill link (`routes.test.tsx:125-149`).
- **V-17 — resolved.** **RED:** actual-browser CDP evidence in `review-harness-ui-reviewer-c1.md:29` at `fa921782d8404c8b635520be0cc1230d23fed6be` sent real Tab input to a `:focus-visible` control and measured `outline: rgb(0, 0, 0) none 3px`. **GREEN:** fresh actual-browser CDP probe at `ffd9fb02` sent Tab input to the rendered dashboard and measured the focused `INPUT` as `focusVisible: true`, `outlineWidth: 2px`, `outlineStyle: solid`, `outlineColor: rgb(250, 250, 250)`.
- **V-18 — resolved.** **RED:** actual-browser CDP evidence in `review-harness-ui-reviewer-c1.md:35-38` at `fa921782d8404c8b635520be0cc1230d23fed6be` measured desktop `main` left/right at `8/8`, narrow `24px` effective gutter, and narrow document `scrollWidth/clientWidth` `1018/831`. **GREEN:** fresh actual-browser CDP probe at `ffd9fb02` measured desktop main left/right `0/0`, internal padding `24px/24px`, and `scrollWidth/clientWidth` `1440/1440`; at 831px it measured left/right `0/0`, internal padding `16px/16px`, and `831/831`.
- **NEW-fixed-dark-document — resolved.** **RED:** actual-browser CDP evidence in `review-harness-ui-reviewer-c1.md:42` at `fa921782d8404c8b635520be0cc1230d23fed6be` measured document `color-scheme: normal` and body `rgba(0, 0, 0, 0)`. **GREEN:** fresh actual-browser CDP probe at `ffd9fb02` measured `getComputedStyle(document.documentElement).colorScheme === "dark"` and `getComputedStyle(document.body).backgroundColor === "rgb(27, 27, 27)"`.

## Scoped verification

- `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/routes.test.tsx` — PASS: 13 tests.
- `npm --prefix .claude/skills/harness/bin/dashboard/client run build` — PASS: Vite build succeeded.
- Actual rendered-browser CDP probes against `python3 .claude/skills/harness/bin/dashboard/serve.py --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53 --port 8973` — PASS: the V-17 focus, V-18 geometry, and fixed-dark measurements recorded above.

Changed paths in repair commit: `client/src/api.ts`, `client/src/routes.tsx`, `client/src/routes.test.tsx`, `client/src/tiles.tsx`, regenerated `client/dist/`, and this receipt.
