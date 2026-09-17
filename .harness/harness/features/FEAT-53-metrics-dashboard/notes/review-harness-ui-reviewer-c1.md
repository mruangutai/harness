# UI review — FEAT-53 metrics dashboard — c1

**BLUF: FAIL.** At fixed tip `fa921782d8404c8b635520be0cc1230d23fed6be`, regional failure isolation is repaired (V-02 resolved), but the required browser proof does not close V-03 and runtime measurements show V-17 and V-18 remain open. The source surface also does not establish the contract's fixed-dark browser state.

- mode: B
- review SHA: `fa921782d8404c8b635520be0cc1230d23fed6be`
- browser: headless Google Chrome through CDP against the Vite source server at 1440×1000 and 831×1000; `/api/kpis` and `/api/work` were independently fulfilled through CDP Fetch interception. No dist build or dist write occurred.
- pin integrity: `HEAD` resolved exactly to the review SHA. Existing dirty paths were feature records/review notes and Vite cache; none supplied product evidence.

## Original finding dispositions

### V-02 — RESOLVED

Both failure directions remained region-local in the actual browser:

- KPI success / work HTTP 502: seven `/kpi/$n` links and KPI values remained operable; the Work List alone showed `Work list unavailable`, the specific `Dashboard request failed: 502`, and Retry. No TanStack `Something went wrong` boundary appeared.
- Work success / KPI HTTP 503: the one real work row/link remained present and operable; the KPI region alone showed `Repository KPIs unavailable`, `Dashboard request failed: 503`, and Retry. No error-boundary collapse appeared.

This meets the finding's two-direction discriminator.

### V-03 — OPEN

The browser demonstrated an in-app `/kpi/1` transition, a focused `h1[tabindex=-1]`, and two SVGs, so the former label-only route is repaired. A separate direct `/kpi/4` controlled-payload probe rendered the panel heading and a table. However, that browser probe did not expose an `About Escaped Defects` disclosure or a `/work/$id` row link, so neither keyboard disclosure operation nor the full KPI-row drill could be proven in the required runtime surface. Source/component-test evidence (`routes.test.tsx:102-131`, `panels.tsx:64-99`) supplements the implementation claim but cannot substitute for the required browser observation. V-03 therefore remains open as a verification disposition; this run does not assert a new shipped-code defect from the deliberately controlled fixture mismatch.

### V-17 — OPEN

Route/state landing improved: browser clicks from `/` landed on the KPI and work-detail `H1`, each with `tabindex=-1`, and computed no title outline. Mouse navigation also computed `:focus-visible === false` and no retained ring.

The signed keyboard ring still fails. After real CDP Tab input, the focused interactive input matched `:focus-visible`, but computed `outline: rgb(0, 0, 0) none 3px` with `outline-offset: 2px`, rather than a visible 2px solid text-token ring. `routes.tsx:51` uses `var(--color-text)`, while the signed/Astryx token is `--color-text-primary`; the invalid outline leaves no meaningful indicator. This remains a high accessibility failure owned by T-13.

### V-18 — OPEN

Measured browser geometry still misses the signed gutters:

- 1440px viewport: `main` border box x=8, width=1424, right=8, padding=24px. Actual content begins at 32px and usable content is 1376px, not the signed 24px gutter / 1392px usable width.
- 831px viewport: `main` x=8, width=815, right=8, padding=16px. Actual content begins at 24px, not the required 16px. The document also measured `clientWidth=831`, `scrollWidth=1018`, so the page itself horizontally overflows below 832px.

The 1600px declaration and responsive padding were added, but the unreset browser body margin shifts both breakpoints and the narrow layout still overflows. V-18 remains medium, owned by T-13/T-28.

## New finding

1. **MED — substance — scope change — owner T-13 — fixed-dark browser state is not applied at the document surface.** On the stable loaded dashboard, `documentElement.dataset.theme` was `dark`, but computed `color-scheme` was `normal` and body background was transparent (`rgba(0, 0, 0, 0)`). DESIGN C-3 requires computed `color-scheme: dark` and the Neutral dark ground (`rgb(27,27,27)`) regardless of OS preference. Scenario: native controls/browser painting may use light defaults while application components claim dark, breaking fixed-dark parity. This class was not one of V-02/V-03/V-17/V-18 and is therefore explicitly a scope change rather than silently bound to an original finding.

## Accessibility and theme

- **High:** V-17's keyboard-focused interactive element has no computed visible outline.
- Route titles are programmatic landings and remain outside ordinary tab order; pointer navigation does not retain a ring.
- Dark is the sole contracted theme, so light-theme parity is inapplicable. Fixed-dark parity itself is not met at the document surface (new finding above).
- Rendered pixel aesthetics beyond the recorded DOM/computed-style/viewport evidence require human/UAT eyes.

## Gate

- severity_max: high
- must_fix: V-17 and V-18; close V-03 only with a browser run that observes and operates the complete disclosure and row drill-down; apply the fixed-dark document state.
- no ruled-out or out-of-scope c0 finding was re-raised.
