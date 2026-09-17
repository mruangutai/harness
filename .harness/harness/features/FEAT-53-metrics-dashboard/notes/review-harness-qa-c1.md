# QA revalidation — FEAT-53 frontend repair c1

**Verdict: FAIL.** Fixed tip `fa921782d8404c8b635520be0cc1230d23fed6be` restores a tested KPI route surface, but the scoped component suite does not prove both partial-query-failure directions, keyboard-only focus behaviour, or rendered desktop/narrow geometry.

## Scoped command

`npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/routes.test.tsx src/work-view.test.tsx` — **PASS**, 2 files / 18 tests. The jsdom runtime emitted non-fatal `Window.scrollTo()` not-implemented notices.

## Finding dispositions

| ID | Disposition | Before-fix record and test | After-fix binding | Assessment |
|---|---|---|---|---|
| V-02 | **open** | `receipt-harness-frontend-dev-fix-c1.md:14` records the red assertion in `routes.test.tsx:85`. | `routes.test.tsx:85-99` executes the route with `/api/kpis` rejecting and directly observes the KPI error plus usable Work List and row. | This is observable DOM behaviour, not source text, but it does **not** test the converse: `/api/work` rejecting while settled KPIs remain usable. The suite therefore does not prove partial-query-failure isolation for both independently queried regions. Owner: T-14/T-28. Severity: high — a work-query outage can still hide all settled KPI content without a regression test reddening. |
| V-03 | **resolved** | `receipt-harness-frontend-dev-fix-c1.md:15` records the red assertion in `routes.test.tsx:101`. | `routes.test.tsx:101-132` clicks an actual KPI tile and observes the level-one KPI landing, escaped-defect InfoDisclosure, and `/work/BUG-1` drill-down link. | Direct observable DOM/route binding, not a source-text or plumbing assertion. It proves the affected escaped-defect panel's detail and drill-down; it does not establish every KPI-specific panel variant. |
| V-17 | **open** | `receipt-harness-frontend-dev-fix-c1.md:16` records the red route/focus assertion. | `routes.test.tsx:101-132` directly observes focus movement after a synthetic link click; `routes.test.tsx:134-146` only searches an injected style string for focus tokens. | Focus movement is bound for click navigation, but keyboard-only focus is not exercised with keyboard interaction, and the ring rule is source text rather than computed/observable focus styling. Owner: T-13. Severity: high — a keyboard activation or focus-visible regression can ship green. |
| V-18 | **open** | `receipt-harness-frontend-dev-fix-c1.md:17` records the red geometry assertion. | `routes.test.tsx:134-146` searches the injected CSS string for 1600px/24px/831px/16px literals. | This is source text, not rendered geometry. It performs no 1440px, 1920px, or narrow viewport layout measurement, so neither desktop scan width nor narrow gutter is proven. Owner: T-13/T-28. Severity: med — an effective layout regression from CSS precedence or component layout can ship green. |

## Matrix and coverage

- `component`: **satisfied** by the scoped Vitest command above; named tests include `routes.test.tsx:85`, `:101`, and `:134`.
- `unit`: **missing for this frontend repair**. The `frontend` matrix requires it, but the configured unit command does not execute the changed client component tests; no scoped unit test directly exercises these route/work changes.
- `ui`: **not applicable** to this scoped diff: no matching e2e/browser-driver test is present and the configured command is null. This does not turn the required component evidence into browser geometry evidence.

Phase-1 expectations were: independent failure isolation for each query, a populated KPI panel with a real drill-down, focus movement and keyboard-visible focus, and desktop plus narrow rendered geometry. The committed suite directly covers the first V-02 direction and the affected V-03 drill-down, covers click focus movement, and only text-checks CSS. Gaps remain: reverse failure isolation; keyboard-only activation/focus styling; and actual 1440px/1920px/narrow geometry.

No new finding class is raised; all open items are unresolved portions of V-02, V-17, or V-18.
