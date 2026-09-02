# DESIGN — FEAT-53 Metrics dashboard

**`needs_prototype: true`.** Derived at the bottom of this document, not inherited: three of this
feature's success criteria (SC-02, SC-08, SC-11) are `uat`, the user hand-tests a drill-down in a
browser, and the one thing this contract exists to prevent — a confident chart drawn over absent
data — is a judgement a reader of prose cannot make. The prototype is not built in this dispatch.

**What is designed here is the *surface*.** The payload shape, the entry-point CLI text and the
trend-line schema are the plan's. Every statement below is either a measurement (cited or computed
here) or a contract on code that does not exist yet; nothing is a measurement of a built dashboard.

**One number in this document is an illustration and must never appear in shipped source:** this
repository's file mix, measured at the grilling as 107 `.py` / 12 `.sh` / 3 `.ts`
(`.harness/notes/grilling-metrics-dashboard-2026-09-01.md`, "Facts I verified"). It appears here to
show what S-3 renders. A literal of it in the dashboard's own source **fails SC-06**.

## Substrate

- system: `@astryxdesign/core` — **version unpinned as of this contract; see Q1.** The package is an
  npm dependency with a React ≥19 peer, StyleX internally, and a runtime `defineTheme` taking
  `[light, dark]` tuples (`DECISIONS.md` DEC on team conventions, "Astryx is not globally available
  as a Claude Code capability"). Convention pinned at `team-config.yaml`, `conventions:` id
  `astryx-design-system`.
- provisioned: **no.** There is no `package.json` anywhere in this repository (BRIEF `## Constraints`),
  so the package is not installed and its export surface cannot be enumerated from here. dev-ops
  installs and pins it; frontend-dev resolves component names against the installed package.
- **No second component substrate.** Adding one requires its own plan Decision, which this segment is
  not writing.

**The composition rule, which is what a reviewer checks instead of a component list I cannot
enumerate:**

1. Every rendered element is an Astryx primitive or a composition of Astryx primitives. No bare
   `<div>` carrying layout or colour of its own, no unstyled framework default.
2. **Every colour, size, radius and spacing value in component source comes from a theme token.**
   Raw `#hex` appears in exactly one file — the `defineTheme` call. `grep` for a hex literal outside
   that file is a violation, and that is the check.
3. **Charting is not a substrate exception, it is a mark renderer.** *The charting library* —
   whichever one D-08 resolves to, TanStack Charts or its named fallback — draws marks and nothing
   else. Every colour, stroke, dash and marker it receives is passed in from the same theme tokens;
   it contributes no components, no typography and no palette.
   **The check, so this rule can fail rather than merely be asserted:** every chart mounted in
   component source sets its colour/scheme/theme prop **explicitly, from theme tokens**, and never
   leaves it to the library's default. Enumerate the mount sites — `grep` component source for the
   charting library's import specifier — and a chart among them that passes no token-derived colour
   prop is a violation. This is stated without naming a library on purpose: D-08 may swap the
   library, and the rule must survive the swap.
4. Where a surface needs something Astryx does not provide, it is **composed** — named in §Component
   direction — never substituted. The hatch fill (S-2, S-4) is the one such composition:
   a StyleX `repeating-linear-gradient` applied to an Astryx surface primitive, with both themes'
   stroke colours from tokens. Not a new dependency.

## Palette

**Base tokens are Astryx's, not restated here** — restating a pinned palette turns one upstream
reword into an N-place edit. What this contract adds is the tokens Astryx cannot supply, because they
are semantic to *this* feature: grade bands, series identity, and the unavailable treatment. All are
declared in the same `defineTheme` `[light, dark]` tuple as everything else.

The four surface anchors are named because every ratio below is measured against them:
`bg` `#FFFFFF`/`#0E1116`, `surface` `#F6F7F9`/`#161A21`, `text` `#14181F`/`#E8ECF2`,
`text-muted` `#5A6472`/`#9AA4B2`. Where an Astryx theme value differs, Astryx wins and the ratios
below are re-measured against it rather than the anchor being forced.

| Token | Light | Dark | Used for | Ratio vs `surface` (L / D) |
|---|---|---|---|---|
| `grade-1` | `#B3261E` | `#FF8A80` | histogram bin 1, grade-1 outlier rows | 6.10 / 7.64 |
| `grade-2` | `#8A5300` | `#E0A33A` | histogram bin 2, grade-2 outlier rows | 5.90 / 7.87 |
| `grade-3` | `#5A6472` | `#9AA4B2` | histogram bin 3 — below a source bar, not an outlier | 5.60 / 6.92 |
| `grade-4` | `#1B7A5A` | `#4FD1A5` | histogram bin 4 | 4.92 / 9.13 |
| `grade-5` | `#0B4F6C` | `#69C7E8` | histogram bin 5 | 8.34 / 9.08 |
| `series-1` | `#1B5FCC` | `#7FA9FF` | cycle-time line | 5.51 / 7.49 |
| `series-2` | `#0B4F6C` | `#69C7E8` | touchpoints line | 8.34 / 9.08 |
| `series-3` | `#8A5300` | `#E0A33A` | code-grade line | 5.90 / 7.87 |
| `unavailable-stroke` | `#8A9099` | `#6E7885` | hatch strokes, dashed outlines, `—` glyph | 3.00 / 3.89 |

- contrast: every ratio above is computed by the WCAG 2.x relative-luminance formula against
  `surface` in its own theme. **All nine clear 3:1** (the non-text-graphic floor) and **all eight
  informational tokens clear 4.5:1** (AA body text), so each may legally be used as a label as well
  as a fill — which §Light/dark parity requires. `unavailable-stroke` is deliberately the only token
  below 4.5:1: it is never text, and its 3:1 keeps a hatch visible without letting an absence read as
  loud as a value.
- Grade bands are **five**, not three, and the five map 1:1 onto `code_grade.py`'s scale, where 1 is
  worst and 5 best (`code_grade.py:30-44`). **The bar is per record, not global** — 3 for a test
  path, 4 otherwise (`code_grade.py:484`) — which C-2 turns into a chart capability, not a colour.

## Type

- family: Astryx theme body / Astryx theme mono. This contract adds no family.
- scale: 12 / 13 / 14 / 16 / 20 / 28 / 40. No in-between sizes. 40 is reserved for the single headline
  figure on a KPI tile; 28 for a panel's headline figure; 12 for axis ticks and the reason clause.
- weights: 400 body, 500 labels and table headers, 700 headline figures.
- **Every numeral in a table, tile or axis is set in mono with tabular figures.** Proportional digits
  make a column of counts jitter row to row, and this surface is almost entirely columns of counts.

## Spacing and layout

- unit: 4px. Every margin, padding and gap is a multiple.
- radius: 6px controls and table cells, 10px cards and panels. No other radius.
- container: max 1440px, 24px gutters, content centred.
- breakpoints: 640 / 1024 / 1440. Below 1024 the KPI tile grid drops from 3 columns to 2, and below
  640 to 1. **No layout below 640 is designed** (see §Out of scope).
- Charts fill their container width and are given an explicit height per shape (histogram 280px,
  time-series 320px); no chart has a fixed pixel width.

## Component direction

- **Dense over airy.** This is an instrument panel read by one person looking for a number, not a
  marketing page. A tile shows its figure, its denominator and its trend, and nothing else.
- **A figure never appears without its denominator or its unit.** "4" is not a measurement; "4 of 12
  features" and "4.2 days" are. A reviewer may call any bare figure a violation.
- **The sourcing rule travels with the number it justifies** (REQ-05, SC-13). Escaped defects carry
  their sourcing rule as persistent inline text under the figure — not a tooltip, not a page-footer
  footnote, not a link. Same for S-3's Python-only caveat.
- **No modal at any depth, and every disclosure is inline.** Every drill-down is a route (C-1), so
  every view is linkable, reloadable and back-button-safe. A modal would make SC-11's hand test
  unshareable. The two disclosures this contract asks for — S-2's names list and S-3's
  ungraded-extension list — **expand in flow and displace the content beneath them**; neither is a
  popover, an overlay, a dialog, or any layer drawn above the page. A disclosure rendered over other
  content is a violation of the no-modal rule, not an exception to it.
- **Nothing is hover-only.** Every fact a hover would reveal is also present as text, because SC-11 is
  hand-executed and hovers do not survive a screenshot, a keyboard, or a touch device.
- **Every render state is visually distinct and none of them is a grey box.** Two are not gap states:
  **loaded**, and **loading** — a skeleton in the shape of the eventual content, and **a region never
  renders a chart from a partial payload**, it is skeleton until its data is whole. The remaining
  **five are the gap states C-4 pins**, and they are of two kinds. Four are *alternate* treatments
  that replace a value or a region outright: empty (S-1), pre-capability (S-2),
  unavailable-with-a-reason (S-4), and unattributed-share (S-5). One — the Python-only grading caveat
  (S-3) — is a **persistent caveat that co-occurs with a real value** rather than replacing anything,
  which is why it never appears in a list of alternate treatments and why "five gap states" and "four
  replacement treatments" are both correct.
- **The theme toggle is an explicit control**, defaulting to the OS preference on first load and
  persisting the user's choice in `localStorage`. Browser storage only: SC-12 forbids mutating the
  project, and nothing here writes a file.
- **The window selector is a segmented control of exactly three options** — `30d`, `90d`, `all`, in
  that order, each showing its own token as its label — in the page header, right-aligned, on the
  same row as the theme toggle and immediately to its left. It appears identically on all three
  routes, because `window` is a search param of all three (C-1). **Not a dropdown:** three fixed
  options with no growth path do not need a menu, and a segmented control shows all three options and
  which one is current at once, where a closed dropdown shows only the current one. No collapsed
  variant is designed, since below 640px is out of scope.

## C-1 — the six surfaces, their hierarchy, and the navigation model

**Navigation model: TanStack Router, three routes, and all view state in the URL.** This is what
makes SC-11 ("selects a feature and a time window and drills from an aggregate… no server restart, no
file edit") checkable rather than a matter of feel:

| Route | Level | Shows |
|---|---|---|
| `/?window=<w>` | aggregate | the six KPI tiles for the window |
| `/features?window=<w>&sort=<kpi>` | the rows behind an aggregate | one row per feature, all six KPIs as columns, sorted by the KPI drilled from |
| `/features/$featureId?window=<w>` | one feature | that feature's six values, its trend lines, and its outlier list |

**Contract:** the selected window and the selected feature live **only** in the URL — search params and
a path param. No component holds either in local state as the source of truth, and no reload,
back-navigation or paste of the URL into a second tab loses them. `window` is a named token
(`30d`, `90d`, `all`) rather than a date pair, so a URL stays meaningful when it is read a week later.

**What the landing view shows first — a fixed 3×2 grid, in this order:**

1. **Throughput** — BRIEF-approval-to-ship cycle time (median, days), with run count and change size
   as the tile's secondary line. First because it is the FEAT-08 D-06 gap this feature exists to close.
2. **Rework** — `cycles_used` against `max_total_cycles`, as a ratio with both terms shown.
3. **Blocking human touchpoints** — the mean over **tracked features only**, and on the one secondary
   line **both** counts, never one: *n* **at a tracked zero** (instrumentation was running for that
   feature and nothing blocked — a measurement, S-4's genuine zero) and *m* **not tracked** (no
   measurement exists for that feature, because it started before this project's touchpoint epoch or
   the project carries no epoch at all — S-4's unavailable, plan.yaml D-21). The two counts sit under
   those distinct phrases and are never summed into a single "features at zero"; a not-tracked
   feature is also never in the mean's denominator, and when **no** feature in the window is tracked
   the 40pt headline is itself S-4's `—` with its reason, never `0`. Third because `BUILD.md` item
   11's target has never had a measurement behind it.
4. **Escaped defects** — count in the window, with its sourcing rule inline beneath.
5. **Code grading** — the at-or-above-bar share as the headline figure, the outlier count as the
   secondary line. **Never a mean** (REQ-07): the tile's headline is a share, and a tile rendering a
   central tendency is a violation a reviewer may call without reading the payload.
6. **Usage by agent / model tier** — the two-tier split, with the unattributed count named on the tile
   rather than dropped (SC-14).

Each tile carries: a 40pt headline figure, a one-line denominator or secondary, and — for the three
trend KPIs (1, 3, 5) — an 8-point sparkline or its S-1/S-2 treatment. Nothing else.

**One level down** is the per-KPI panel, reached by clicking the tile. **Not every KPI gets a chart.**
Three do; three are tables (LD-1) — a third chart shape would add capabilities to T-15's probe against
an alpha API whose own named fallback is unproven, and a table renders these three honestly at none of
that cost. A table can be promoted to a chart later without disturbing the substrate decision.
**This is the panel inventory, and C-2 defines exactly these artifacts and nothing else:**

| KPI | The panel's primary artifact | Defined in |
|---|---|---|
| 1 Throughput | Shape B — the cycle-time trend line | C-2 §Shape B |
| 2 Rework | **Table TBL-1**, no chart | C-2 §Tables |
| 3 Blocking human touchpoints | Shape B — the touchpoints trend line | C-2 §Shape B |
| 4 Escaped defects | **Table TBL-2**, no chart | C-2 §Tables |
| 5 Code grading | Shape A, the histogram, beside the named outlier list; **and** Shape B for grade over time | C-2 §Shape A and §Shape B |
| 6 Usage by agent / model tier | **Table TBL-3**, no chart | C-2 §Tables |

Every panel also carries its caveats and a feature table. **Where the primary artifact is already
per-feature — TBL-1 — it *is* that panel's feature table and there is no second table.** TBL-2 and
TBL-3 are not per-feature, so those two panels carry a feature table beside the primary one, as the
chart panels do. **Table ids are `TBL-n` and never `T-n`**, because `T-NN` is a plan task id.

**What a user drills *into*** is a feature: a row in a panel's feature table navigates to
`/features/$featureId`, and the aggregate-to-rows step is the `/features` route with `sort` set to the
KPI they came from — so the path SC-11 exercises is tile → `/features?sort=<kpi>` →
`/features/$featureId`, three routes, no restart, no file edit.

**The grading surface is the one that does not collapse to a figure**, and REQ-07 / SC-05 are why:
the histogram and the **named** grade-1 / grade-2 outlier list sit **side by side in one panel** —
the list is a persistent Astryx table to the right of the chart at ≥1024px and directly beneath it
below that. Each row is `qualname` · `path:line` · grade · driver · bar, its grade cell tinted
`grade-1`/`grade-2`. **The names are never behind a hover, a tooltip, a disclosure or a click**: an
outlier a user must discover is an outlier they do not know about, and REQ-07 asks for a named list,
not a reachable one. Empty list → the words "no grade-1 or grade-2 functions in this window", which
is a *measured absence of outliers* and therefore neither S-1 nor S-4.

## C-2 — the two chart shapes and the three tables

**Two chart shapes and three tables exist in this feature, and nothing else** — C-1's panel inventory
uses every one of the five and asks for no sixth. Each chart capability below is a pass/fail question
eng-lead can put to the charting library's current alpha API. **Where a capability names a server-side
workaround, that workaround is the first fallback; React Charts (BRIEF `## Constraints`) is the second;
a third library is neither, and needs its own plan Decision.** The three tables carry no capability
list because they need none: they are Astryx table primitives with no charting-library dependency at
all. That is why the categorical panels are tables rather than a third chart shape (LD-1), and why
**CAP-01…CAP-13 is closed at thirteen.**

**Shape A — distribution histogram (code grading, REQ-07 / SC-05).**

| ID | Capability | If absent |
|---|---|---|
| CAP-01 | Accepts **pre-binned** counts as a bar series over an **ordinal** axis of exactly five categories (grades 1–5). The server bins; the library must not be required to compute bins, and must not silently re-bin or drop an empty category. | hard requirement — a library that insists on binning continuous input cannot render an ordinal grade axis honestly |
| CAP-02 | Per-bar fill resolved **from the datum**, so each bin takes its own `grade-N` token. | render five single-bar series |
| CAP-03 | Renders the **per-record bar** (3 for test paths, 4 otherwise — `code_grade.py:484`) without a single global threshold line. A reference line at "4" would misreport every test-path function. | encode bar membership as a datum-derived hatch on the sub-portion, computed server-side; never draw one global line |
| CAP-04 | An **empty series** (zero graded functions) renders without throwing and **without inventing axis ticks or a zero baseline** — the region hands over to S-1's treatment instead. | wrap: the component returns S-1 before the chart mounts (this is the preferred implementation regardless) |
| CAP-05 | The chart can be `aria-hidden` while an adjacent real `<table>` carries the same numbers. We supply the table; the library must not be the only route to the values. | hard requirement, and cheap — the table is ours |
| CAP-06 | Bin meaning is readable **without a legend** — an axis label per bin. | render labels ourselves beneath the axis |

**Shape B — time-series lines (cycle time, touchpoints, code grade over time; REQ-10).**

| ID | Capability | If absent |
|---|---|---|
| CAP-07 | A **temporal x axis with irregularly spaced points.** Ships are irregular; a library assuming a uniform interval fabricates a cadence. | hard requirement |
| CAP-08 | **Three series in one plot with per-series y-axis assignment** (hours, a count, and a 1–5 grade share no scale). Still probed by T-18 — the library's answer belongs on the record either way. | **Settled — this is what gets built, whatever the probe returns: three stacked single-series plots sharing one x axis and one window.** The decision and its reason live in plan.yaml T-15; this contract pre-authorised the outcome, so it is the chosen build, not a fallback, and no redesign follows. |
| CAP-09 | **A missing point breaks the line.** No interpolation across a gap, no coercion to zero. This is REQ-11 expressed as a chart capability and it is the single most important one. | segment each series server-side into contiguous runs and render one line per run — deterministic, and preferred if the library's null handling is not explicitly documented |
| CAP-10 | Zero-point series renders no axes and no baseline — hands over to S-1. | as CAP-04 |
| CAP-11 | **Per-series dash pattern and point-marker shape**, set independently of colour. | hard requirement of §Light/dark parity; if the library cannot, draw markers as an overlaid series |
| CAP-12 | Point identity is reachable **as text** — each point's feature id appears in the adjacent table, and any tooltip is a duplicate of it, never the only copy. | ours to supply |
| CAP-13 | Responsive to container width without a fixed pixel width, and no SSR/hydration requirement (client-only is fine). | wrap in a resize observer |

**§Tables — the three categorical panels.** Each is an Astryx table primitive rendering a real
`<table>`, sortable by activating a column header, with the sort reflected in the URL wherever the
panel is itself a route. **Every count carries its denominator** (§Component direction), every
unavailable cell takes S-4's treatment, and no table shows a total the payload does not carry.

| ID | Panel | One row is | Columns, in order | Row order | Beneath the table |
|---|---|---|---|---|---|
| TBL-1 | 2 Rework | one feature in the window | feature id, linking to `/features/$featureId` · `cycles_used` · `max_total_cycles` · the two-term ratio | `cycles_used`/`max_total_cycles` descending, ties by feature id ascending | the aggregate as **both terms summed** and never as a lone ratio (T-06) |
| TBL-2 | 4 Escaped defects | one escaped-defect item | kind (`bug_unit` or `revert`) · id · date · subject | date descending | the window count, and the payload's `sourcing_rule` sentence as persistent inline text (REQ-05, SC-13) |
| TBL-3 | 6 Usage by agent / model tier | one attribution bucket | bucket — a model-tier name, or one of the four named unattributed buckets · commit count · share of `total_commits` | attributed tiers first, count descending; then the four unattributed buckets in the fixed order `no_prefix`, `human`, `feature_only`, `unresolvable_step_id` | `total_commits` and `attributable_share`; **the two groups are separated by a rule and each is subtotalled**, so attributed and unattributed can never be read as one list |

**TBL-3's two groups are never merged and no bucket is ever omitted** — including a bucket whose count
is zero, which renders as a measured `0` in S-4's genuine-zero treatment and never as a dropped row
(SC-14, D-13). A single "unattributed" total standing in for the four named buckets is a violation.

## C-3 — light/dark parity, and keyboard operability

Both themes are first-class and ship from **one** `defineTheme` call with `[light, dark]` tuples.
There is no second stylesheet, no `prefers-color-scheme` query inside component source, and no
theme-conditional branch in a component: a value that differs by theme differs **in the token**.
That is the check — a `prefers-color-scheme` or an `isDark` ternary in a component is a violation.

**Chart colours are tokens passed in, not library defaults** (§Substrate rule 3), so a chart that
looks right in light and wrong in dark is a token bug in one place rather than a chart bug in three.

**What must never be encoded by hue alone, and why it is measured rather than asserted:**
`series-1` and `series-2` differ from *each other* by only **1.51:1** in light and **1.21:1** in dark
(same formula as §Palette). Hue is doing all the work between them, so hue must not be the only
carrier of any meaning:

| Distinction | Carried by, beyond hue |
|---|---|
| which series a line is | dash pattern (solid / 6-2 dash / 2-2 dot) + marker shape (circle / square / triangle) + **a direct end-of-line label**. A legend is a convenience, never the only mapping |
| which grade a bin is | ordinal position on the axis + a printed bin label + the count printed on or above the bar |
| at-or-above bar vs below | the printed share and the word, plus CAP-03's hatch. Never green-vs-red alone |
| unavailable vs zero | glyph, typography, fill and a badge — all four (C-4, S-4) |
| an outlier row | the grade numeral in the cell, not only the row tint |

`unavailable-stroke` holds 3.00:1 light and 3.89:1 dark against `surface`, so the hatch that marks an
absence stays visible in both themes without ever competing with a real value.

### Keyboard operability and focus

`ui` has no automated runner (BRIEF `## Verification gaps`), so SC-15's inspection is the whole gate
for this dimension, and an inspection can only catch what the contract pins. **"Accessible" is not a
contract term.** Each clause below is written so a reviewer can name what violates it.

**1 · What is a focus stop, and in what order.** On every route, tabbing from the document start
reaches exactly these, in exactly this order: (a) the window selector's three segments, (b) the theme
toggle, (c) each KPI tile in the 3×2 grid's reading order, (d) inside a panel, its sortable column
headers, then its row links in displayed order, (e) each inline disclosure's trigger.
**Nothing else is a focus stop:** a chart is `aria-hidden` and not focusable (CAP-05), and a badge, a
hatch cell, a caveat line and a headline figure are never focusable.
*Violated by:* a `tabindex` on a chart or any decorative element; a tile reachable only by mouse; a
sortable column header built as a `<div>` with a click handler instead of a `<button>`; a table whose
tab order follows payload order rather than displayed order after a sort.

**2 · What a focus indicator must look like to count.** A visible ring on the focused element:
**2px wide, offset 2px from the element's edge, drawn in the `text` token of the active theme.** No
`outline: none`, and no indicator that is colour-only. `text` is the highest-contrast token in each
theme — 16.60:1 light and 14.71:1 dark against `surface`, computed here by the same formula as
§Palette — so the ring clears the 3:1 non-text floor in both with room to spare. The indicator is
**identical for mouse and keyboard focus**; there is no `:focus-visible`-only suppression, because a
click-then-tab path would then be unindicated.
*Violated by:* `outline: none` anywhere in component source; an indicator that is a background tint
with no ring; a ring under 2px or with no offset, which against a 6px radius reads as part of the
control rather than around it; an indicator that vanishes in one theme.

**3 · Where focus lands after each transition.** Focus is **never** dropped to `<body>`.
- tile → `/features?sort=<kpi>`: on that route's **first sortable column header**, the one matching
  `sort`.
- `/features` row → `/features/$featureId`: on that page's **`<h1>`**, made programmatically focusable
  for exactly this purpose and not itself a tab stop.
- browser Back, from any of the three routes: on **the control that was activated to leave** — the
  originating tile or row link — so the drill can be re-entered without re-tabbing the page.
- the theme toggle: **focus stays on the toggle.** The toggle is not re-mounted and the tree is not
  re-rendered from a new root, so nothing may move it.
- a disclosure opening or closing: **focus stays on its trigger**, and the revealed content becomes
  the next tab stop after it.
*Violated by:* any of those five transitions leaving `document.activeElement` as `<body>`; a route
change that scrolls the viewport without moving focus; a theme toggle implemented by remounting the
tree.

**4 · Names for the things a chart hides.** Every chart is `aria-hidden` (CAP-05) with a real
`<table>` carrying the same numbers adjacent to it **and in the tab order**, so no value is reachable
only by sighted mouse use. Every S-4 reason and every S-2 label is real text in its cell.
*Violated by:* a chart that is the only route to a number; a reason carried by a `title` or
`aria-label` attribute alone.

## C-4 — the five honest-gap states, each visually distinct

This is the contract's reason for existing. A reviewer must be able to tell these apart **on screen,
without reading the payload**, so each gets a different treatment rather than a different string.

**S-1 · The project has never shipped since this capability existed** — `.harness/metrics/trend.jsonl`
missing or zero lines. **The entire trend region is replaced**, not annotated: one Astryx card, full
region width, `surface` fill, a dashed 1px `unavailable-stroke` outline, **no axes, no gridlines, no
zero baseline, no chart mounted at all.** Headline at 20pt: "No ship records yet". Body at 13pt: names
`.harness/metrics/trend.jsonl`, states that the trend begins at the first ship after this capability
landed, and states that history is never backfilled. The five non-trend KPIs render normally beside
it — this state is scoped to the trend region, never to the page.
*How a reviewer tells it from S-2:* on `/` and `/features`, **no axes are drawn**. On
`/features/$featureId` the two treatments are deliberately identical and only the copy differs — see
S-2.

**S-2 · A pre-capability feature sitting among features that do have trend data** (SC-08, a
user-executed hand test on exactly this). On `/` and `/features`, axes **are** drawn, because other
features have data. The pre-capability feature is:
- **excluded from the line's path** — the line breaks (CAP-09), it does not descend to zero and it is
  not interpolated across;
- present in the feature table with its trend cells on the hatch fill pinned below, carrying an
  em-dash `—` and the label "no trend — shipped before metrics";
- counted in a persistent line beneath the chart: "*n* of *m* features in this window shipped before
  metrics and have no trend line", with the names one **inline** disclosure away (§Component
  direction).

**The hatch fill, pinned here once and referenced by S-4 and CAP-03: 45°, a 1px stroke on a 6px
period, `unavailable-stroke` on `surface`, unchanged between themes except for the token's own value.**
The stroke is 1px at every breakpoint and does not scale with the cell. The angle alone left two
builders free to produce visibly different fills, which is the divergence this pin closes.
**These are contract values, not observed ones:** the prototype chose 1px/6px and **has never been
rendered by anyone**, so this pins a number rather than ratifying an appearance. A reviewer checks the
declared gradient stops in source, not a screenshot.

**On the single-feature route `/features/$featureId`, S-2's table treatment does not apply — the
full-region replacement does.** That page shows one feature, so there is no contrasting feature to
draw axes against, and axes drawn for a lone feature with no points is exactly the confident-empty-chart
failure this contract exists to prevent. When the viewed feature is itself pre-capability, **its whole
trend region is replaced**, by the same treatment S-1 specifies — one Astryx card, full region width,
`surface` fill, a dashed 1px `unavailable-stroke` outline, no axes, no gridlines, no zero baseline, no
chart mounted — but with **S-2's copy, not S-1's**, because the reason is different: headline at 20pt
"No trend for this feature", body at 13pt naming that this feature shipped before metrics, that the
trend begins at the first ship after this capability landed, and that history is never backfilled.
The feature's five non-trend KPIs render normally beside it.
**A `/features/$featureId` page that draws trend axes for a pre-capability feature is a violation**,
and it is the first thing SC-08's hand test should try.

*How a reviewer tells it from S-1:* on `/` and `/features`, axes and other features' lines are
present. On `/features/$featureId` the treatments are identical by design and the copy is the only
difference — S-1 names `.harness/metrics/trend.jsonl` and the project's ship history, S-2 names this
one feature's. *From S-4:* the reason is a fixed, project-wide historical fact, so the label is the
same on every such row and the row is never mistakable for a KPI that failed to compute.

**S-3 · The Python-only grading caveat** (REQ-08 / SC-06). A persistent 13pt caveat **directly beneath
the histogram**, inside the same panel — never a tooltip, never a page-foot footnote:

> Grading covers Python only. *N* of *M* tracked files in this project are ungraded (*P*%).

with a disclosure listing the ungraded extensions and their counts. **Contract, and it is the SC-06
check:** `N`, `M`, `P` and every extension count arrive **only** from the payload, computed from the
viewed project at view time. No file-mix number is written into component source, a default prop, a
fixture imported by production code, or a placeholder string. *Illustration only* — rendered against
this repository as measured at the grilling, the sentence would read "15 of 122 tracked files are
ungraded (12%)" over its 107 `.py` / 12 `.sh` / 3 `.ts` mix; **those digits are an illustration in this document and their
appearance as a literal in shipped source fails SC-06.**

**S-4 · Unavailable-with-a-reason versus a genuine zero** (REQ-11 / SC-07). These are the two most
confusable states on the surface and a shared grey placeholder for both is a defect:

| | Genuine zero | Unavailable, with reason |
|---|---|---|
| value slot | the numeral `0`, mono 700, `text` — **identical type and colour to any other value** | the glyph `—`, mono 400, `unavailable-stroke`. **Never a numeral, never `0`, never blank** |
| second line | its denominator: "0 of 12 features" | **the reason, always present and always specific**: "no ship record for this feature", "no commit carries a resolvable step-id", or — for a touchpoint count — the not-tracked sentence plan.yaml D-21 pins for that branch, rendered verbatim from the payload rather than restated here. A generic "no data" is a violation |
| fill | normal `surface` | the hatch fill pinned in S-2 — 45°, 1px stroke, 6px period, `unavailable-stroke` on `surface` |
| badge | none | an Astryx badge reading "unavailable" |
| in a chart | a plotted point at zero | no point plotted; the line breaks (CAP-09) |

Four independent differences — glyph, typography, fill, badge — because one is a coincidence away from
looking like the other. **A zero is a measurement and is presented with the confidence of one.** No
tile, cell or chart region is ever left blank, and no absence is ever rendered as grey-and-nothing.

**KPI 3 is the sharpest instance of this pair, and the one where the same input produces both
states.** An absent `touchpoints.jsonl` is a genuine zero **only** for a feature that started at or
after this project's touchpoint epoch — instrumentation was running and nothing blocked. For every
other feature the same absence is *not a measurement at all* and takes the unavailable column, with
D-21's reason. So a `0` cell and a `—` cell in the touchpoints column can sit one above the other on
identical files, and the four differences above are the only thing separating them; a surface that
renders `0` for an untracked feature has fabricated the number this whole section exists to prevent.

**S-5 · A large unattributed share, named rather than hidden** (REQ-09 / SC-14, D-13). Measured at
this repository, 753 of 975 commit subjects carry no harness prefix at all
(`notes/research-FEAT-53-routing-and-signals.md`, Signal 2), so on a typical project **most of KPI 6
is unattributable — and that is a measurement, not a hole in the data.** It is therefore neither S-1
nor S-4: nothing failed to compute, and nothing is unavailable.

- **On the tile:** the 40pt headline figure is the **attributable share** (`attributable_share`), and
  the secondary line names the unattributed count against its denominator — "*u* of *t* commits
  unattributed". A tile presenting an attributed count as though it were the total is a violation
  (SC-14).
- **In the panel:** table TBL-3, with its two subtotalled groups and its separating rule.
- **Treatment:** the four unattributed rows are set in `text`, mono 700, **exactly as an attributed
  row is** — the same rule S-4 states for a genuine zero, that a measurement is presented with the
  confidence of one. **No hatch, no `—`, no "unavailable" badge, no muting**: an unattributed commit
  is a counted commit. What separates the group is its position, its subtotal and TBL-3's rule, plus a
  13pt line beneath the table giving each bucket's reason — `no_prefix` "no harness prefix in the
  commit subject", `human` "attributed to a human", `feature_only` "a feature id with no task id",
  `unresolvable_step_id` "a step-id resolving to no agent or no model".

*How a reviewer tells it from S-4:* S-5 carries numerals in ordinary value type with no hatch and no
badge, because these commits **were** counted. *From S-1 and S-2:* nothing is replaced and no region
is missing — the whole KPI renders. **Rendering the unattributed buckets in S-4's treatment is a
violation**, and so is collapsing them to one row.

## The prototype gate

**`needs_prototype: true`.** The user may waive it; the reasoning is on the record either way.

- **The interaction *is* the deliverable.** SC-11 is a three-step operated flow — select a window,
  drill from an aggregate, land on a feature — and REQ-12 requires all of it from the browser with no
  restart. C-1's route table is a claim about that flow; whether it *feels* like drilling in rather
  than jumping sideways is not judgeable from a table.
- **Three success criteria are `uat`, and the BRIEF says why they must be**: `ui` has no runner
  (BRIEF `## Verification gaps`), so **no automated gate will ever look at this surface.** SC-02,
  SC-08 and SC-11 plus SC-15's inspection are the whole of it. A prototype is the only place a
  disagreement about the surface can surface before build rather than after.
- **C-4 is a visual judgement in its entirety.** Whether a hatched row reads as *absence* rather than
  *zero*, and whether S-1 and S-2 are distinguishable at a glance, cannot be settled by the words
  above — that is precisely the failure the contract exists to prevent, and prose is the medium it
  hides in. SC-08 is the user hand-testing exactly this.
- **A real high-fidelity prototype is possible here**, unlike this repo's terminal-surface features:
  Astryx plus React is the substrate, so the prototype is built on the same system the product is.

**Scope, when it is dispatched:** a single-page Astryx + React build over a **fixture payload, never
live data**, covering the landing grid, one KPI panel, the aggregate→rows→feature drill, the window
control, both themes, and **all five C-4 states simultaneously visible**. Published as a single-file
artifact where possible, otherwise runnable locally with the command in its own note; committed under
`notes/prototypes/FEAT-53/`.

**Rejected:** static mockup images. The three things needing judgement — the drill, the theme flip and
the gap states in situ — are all state transitions, and a still frame of each is the one thing that
cannot show whether a transition reads correctly.

**Status of the committed prototype at `notes/prototypes/FEAT-53/` — read this before waiving the
gate.** It predates this contract and does not demonstrate it. It contains **no TBL-1, TBL-2 or
TBL-3** (the three table panels C-2 §Tables pins), **no S-5 state** (C-4's unattributed-commit
treatment), and **nothing implementing C-3's keyboard and focus clauses** — all three were added to
this contract in this cycle, after the prototype was committed. What it does cover is the landing
grid, one KPI panel, the drill and the window control over a fixture payload.
**Its appearance has never been observed by anyone, human or agent.** No browser was available to its
author or to its reviewer, so it has never been rendered — not once, in either theme. Nothing visual
about it is verified: not the palette, not the C-4 states, not the type scale. Any judgement of how it
looks is unmade, not merely unreviewed.

## Out of scope

- **The payload's field names, the API shape, the entry-point command and its failure text.** REQ-01 and
  REQ-14 are the plan's; this contract binds only what is rendered.
- **The `trend.jsonl` line schema.** The grilling lists it as not yet specified; the surface consumes
  it and does not define it.
- **Layouts below 640px.** A local instrument panel on a developer machine; a phone layout would be
  designed against no known use.
- **Per-project theming or branding.** Every onboarded project gets the same surface (REQ-02); a
  project-supplied palette is a later feature and would need its own contract.
- **Cross-project comparison views**, per BRIEF `## Out of scope`. Nothing above renders a second
  project.
- **Print and export.** No print stylesheet, no CSV download, no PNG export.

## Open questions

- **Q1 (non-blocking for the plan, blocking before build): what version of `@astryxdesign/core` is
  pinned?** No version appears anywhere in this repository — the convention says "pinned" and names
  no number, and there is no `package.json` to hold one. I decline to invent a literal a reviewer
  could not check. dev-ops pins it at install and records it in `package.json`; the substrate section
  above is satisfied by whatever it pins, and §Substrate's composition rules are version-independent.
- **Q2 — SETTLED in this cycle, no longer open: CAP-08 is three stacked single-series plots sharing
  one x axis and one window.** The question as asked was "one plot with three y axes, or three stacked
  plots?" **plan.yaml T-15 carries the decision and its reason**: cycle time in days, a touchpoint
  count and a grade share are three incommensurable units, and C-3's measured series-1:series-2
  contrast of 1.51:1 light and 1.21:1 dark leaves three near-identical lines on one shared canvas
  unreadable. C-2 §Shape B CAP-08 had already recorded this outcome as acceptable, so **nothing here
  is overruled and no redesign follows** — the plan took a branch this contract already allowed. The
  single-plot preference recorded earlier was a **density preference, not a requirement**; every REQ
  is satisfied either way. T-18's probe still asks whether three-series-one-plot is supported, and
  CAP-08 remains a probeable capability row — what is closed is the design question, not the probe.
- **Q3 (for the user, at the approval gate, non-blocking): the window tokens are `30d` / `90d` /
  `all`.** Chosen because a shipped feature is a rare event at this repo's rate and a shorter window
  would usually be empty — which would show S-1 constantly and teach the user to ignore it. Cheap and
  reversible; overrule it freely.

**No genuine Astryx gap was found.** The one thing Astryx plausibly does not ship — the hatch fill —
is composed from a StyleX gradient over an Astryx surface primitive (§Substrate rule 4), which is a
composition, not a second substrate, and therefore needs no Decision entry.
