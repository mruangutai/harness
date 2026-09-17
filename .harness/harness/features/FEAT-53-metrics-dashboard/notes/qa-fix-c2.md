# QA gate — FEAT-53 frontend repair c2

**BLUF: FAIL.** `ffd9fb0204701cdae968ef0febc86943fb4829bd` passes all assigned scoped commands and resolves V-03, V-17, V-18, and fixed-dark document state, but V-02's newly added converse-isolation assertion already passes against pre-fix source. It therefore has no credible failing-before proof. The frontend matrix also still lacks its required unit binding.

## Scoped matrix

| Kind | State | Evidence |
|---|---|---|
| component | satisfied | T-13 route suite: 13/13; T-28 work-view suite: 5/5 at `ffd9fb02`. |
| unit | missing | `frontend` requires unit (`.harness/harness.json:180-190`), but its configured unit runner does not execute changed client component tests; no scoped unit test binds T-13/T-14/T-28. |
| ui | not applicable | No browser-driver test matches the configured `ui.detect`, and `ui.cmd` is null. Browser-only V-17/V-18/fixed-dark evidence is assessed below from recorded actual-CDP red/green measurements, not source text. |

- T-13 exact verify: route suite 13/13 and Vite build PASS.
- T-14 exact verify: Vite build and bounded source conjunct PASS.
- T-28 exact verify: work-view suite 5/5 and Vite build PASS.
- Vitest emitted non-fatal jsdom `Window.scrollTo()` notices.

## Finding dispositions

| Finding | Disposition | Evidence |
|---|---|---|
| V-02 converse failure isolation | **open** | `routes.test.tsx:111-123` observes the correct fixed-tip state, but the same current test copied into an isolated worktree at fix parent `7dbb025` passed; the isolated suite failed only V-03's three live-KPI-route cases. The cited c1 red (`receipt-harness-frontend-dev-fix-c1.md:14`) covers the opposite KPI-failure direction. This added assertion has no failing-before proof. |
| V-03 live top-level KPI shape | **resolved** | Isolated parent execution of current `routes.test.tsx` failed the route with `Cannot read properties of undefined (reading 'find')`; fixed-tip route suite passes. `routes.test.tsx:125-149` supplies top-level `{features, aggregate, trend}`, then observes heading, disclosure control, and `/work/BUG-1` drill link. |
| V-17 focus-visible | **resolved** | Actual-CDP red at `review-harness-ui-reviewer-c1.md:29` measures `none 3px`; fixed-tip actual-CDP green recorded in `receipt-harness-frontend-dev-fix-c2.md:9` measures real Tab focus as `:focus-visible`, 2px solid RGB(250,250,250). |
| V-18 effective geometry/overflow | **resolved** | Actual-CDP red at `review-harness-ui-reviewer-c1.md:35-38` measures body-margin gutters and 1018/831 overflow; fixed-tip actual-CDP green in `receipt-harness-frontend-dev-fix-c2.md:10` records 24px/16px internal padding and equal scroll/client widths at 1440/831. |
| NEW-fixed-dark-document | **resolved** | Actual-CDP red at `review-harness-ui-reviewer-c1.md:42` measures `normal`/transparent; fixed-tip actual-CDP green in `receipt-harness-frontend-dev-fix-c2.md:11` records document `dark` and body RGB(27,27,27). |

## Fail-first audit

- V-03: satisfied by the isolated parent red run above and fixed-tip route-suite green.
- V-17, V-18, fixed-dark: satisfied only by the cited actual-browser red/green records; no source-string credit was taken.
- V-02: **missing** for the converse direction. The fixed behavior is exercised, but a test that remains green over `7dbb025` does not discriminate this repair.

## Coverage limits

This gate intentionally did not run formatters, linters, project-wide builds, or project-wide suites. It does not establish a unit-kind test for the frontend repair or replace UAT/browser-driver coverage for the product routes.
