# DESIGN — FEAT-53 Metrics dashboard

**`needs_prototype: true`, and it is built.** Derived at the bottom of this document, not inherited:
three of this feature's success criteria (SC-02, SC-08, SC-11) are `uat`, the user hand-tests a
drill-down in a browser, and the one thing this contract exists to prevent — a confident chart drawn
over absent data — is a judgement a reader of prose cannot make. The prototype lives at
`notes/prototypes/FEAT-53/`; §The prototype gate records what it now demonstrates and what it
still does not.

**What is designed here is the *surface*, and it is dark — the only theme there is** (C-3, operator
ruling 2026-09-04). The payload shape, the entry-point CLI text and the trend-line schema are the
plan's. Every statement below is either a measurement (cited or computed here, or observed in the
prototype) or a contract on code that does not exist yet; nothing is a measurement of a built
dashboard.

**One number in this document is an illustration and must never appear in shipped source:** this
repository's file mix, measured at the grilling as 107 `.py` / 12 `.sh` / 3 `.ts`
(`.harness/notes/grilling-metrics-dashboard-2026-09-01.md`, "Facts I verified"). It appears here to
show what S-3 renders. A literal of it in the dashboard's own source **fails SC-06**.

## Substrate

- system: `@astryxdesign/core` — **version unpinned as of this contract; see Q1.** The package is an
  npm dependency with a React ≥19 peer, StyleX internally, and a runtime `defineTheme` that accepts
  either a `[light, dark]` tuple or **a single string used for both modes**
  (`core/dist/theme/defineTheme.js`, `resolveTokenValue`). This surface is dark only, so it uses the
  single-string form throughout (C-3). Convention pinned at `team-config.yaml`, `conventions:` id
  `astryx-design-system`.
- **base theme: `@astryxdesign/theme-neutral`** — "restrained warm grays", **extended by exactly one
  `defineTheme`**. `extends: neutralTheme` inherits the theme's resolved tokens into ours, so the
  result is flat and self-contained and **Neutral's `theme.css` is not loaded alongside it**
  (`core/dist/theme/defineTheme.d.ts`, the `extends` doc). That is also the only wiring that works:
  `theme.css` is `@scope ([data-astryx-theme="neutral"])` and the root `<Theme>` writes this theme's
  own name to `<html>`, so every scoped rule in that file is inert. Measured in the prototype:
  importing it changes no computed token value and renders a pixel-identical page.
- **Neutral sets the type family**: `--font-family-body` and `--font-family-heading` are
  **Figtree**, with Neutral's own system-sans fallback. Loading the font file is the consumer's job
  — a `<link>` in the document head, not a token — and offline the fallback renders, which is a
  degradation and not a break.
- provisioned: **no.** There is no `package.json` anywhere in this repository (BRIEF `## Constraints`),
  so the package is not installed and its export surface cannot be enumerated from here. dev-ops
  installs and pins it; frontend-dev resolves component names against the installed package.
- **No second component substrate.** Adding one requires its own plan Decision, which this segment is
  not writing.

**The composition rule, which is what a reviewer checks instead of a component list I cannot
enumerate:**

1. Every rendered element is an Astryx primitive or a composition of Astryx primitives. No bare
   `<div>` carrying layout or colour of its own, no unstyled framework default.
2. **Every colour, size, radius and spacing value in component source comes from a theme token, and
   no Astryx or Neutral base token is overridden.** The theme file adds only what the feature's own
   semantics need — the KPI hues, the direction roles, the grade ramp, the unavailable stroke, a
   third text step and the explicit chart sizes. Neutral's substrate ships as its designers made it:
   surfaces, borders, text colours, families, the `--text-*` presets, `--radius-*`, `--spacing-*`.
   Raw `#hex` appears in exactly one file — the `defineTheme` call. `grep` for a hex literal outside
   that file is a violation, and so is an Astryx or Neutral base token name on the left-hand side of
   a `tokens:` entry. Those two greps are the check.
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
   a StyleX `repeating-linear-gradient` applied to an Astryx surface primitive, its stroke colour
   from a token. Not a new dependency.

## Palette

**Dark is the only theme** (C-3, operator ruling 2026-09-04). Every value below was chosen against
the dark card, all of it is declared in one `defineTheme` call as **single values rather than
`[light, dark]` tuples**, and raw `#hex` appears in that call and nowhere else (§Substrate rule 2).

**The tonal ladder is Neutral's.** An earlier revision of this contract overrode
`--color-background-body/surface/card/popover`, `--color-border`, `--color-border-emphasized` and
`--color-text-primary/secondary` into a four-step ladder of its own. **That override is withdrawn**:
a design system whose surfaces are replaced is not the design system, and every downstream Astryx
component was being drawn on a substrate its own components were not designed against.
`@astryxdesign/theme-neutral` 0.5.2 ships `body` and `card` at `#1B1B1B` in dark and `surface` at
`#262626`, and every ratio below is measured **against Neutral's real `card`** — read out of the
running prototype with `getComputedStyle`, not from core's defaults.

Two consequences the contract owns rather than hides:

- **There is no fill step at all: `card` equals `body` (`#1B1B1B` both), so a card is a hairline and
  nothing else** — `--color-border-emphasized` against the card is 2.20:1. That is Neutral being
  quiet on purpose, and it is accepted rather than corrected: swapping cards onto `surface`
  (`#262626`, a 1.14:1 step over the body) would buy depth and contradict the theme's own intent. A
  reviewer who judges the hairline insufficient should say so — the swap is one token reference.
- **No opaque inset token works**: `muted` equals `card`. So the hatch and the dashed empty-state
  outline sit on **`--color-neutral`**, Neutral's translucent generic fill, which recesses whatever
  it is drawn over: composited on the card it is `#323232` (1.34:1). That is the only substrate
  choice this contract makes, and it is a choice between Astryx tokens rather than a replacement of
  one.
- **The type family is Neutral's Figtree**, so the figures are a geometric sans rather than the
  platform UI face. Numerals stay tabular where they line up (§Type).

**The light column is gone.** Every token below ships as a single dark value (C-3); the light values
this table used to carry were deleted with the light theme, and no ratio here is measured against a
white card any more.

| Token | Dark | Used for | Ratio vs `card` |
|---|---|---|---|
| `text` (`--color-text-primary`, Neutral's) | `#FAFAFA` | every value, every heading | 16.50 |
| `text-secondary` (Neutral's) | `#A3A3A3` | denominators, labels, captions | 6.83 |
| `text-tertiary` (`--color-metrics-text-tertiary`) | `#8A95A3` | axis ticks, sourcing rules, meta | 5.67 |
| `positive` | `#4ADE9B` | a delta in the good direction | 10.02 |
| `negative` | `#FF8172` | a delta in the bad direction | 7.08 |
| `direction-neutral` | `#94A0AE` | no change, or a KPI with no polarity | 6.48 |
| `kpi-1` violet | `#A78BFA` | throughput's identity | 6.33 |
| `kpi-2` blue | `#78A9FF` | rework's identity | 7.31 |
| `kpi-3` teal | `#3FD0B8` | touchpoints' identity | 8.96 |
| `kpi-4` magenta | `#F58BC2` | escaped defects' identity | 7.67 |
| `kpi-5` amber | `#E8B45A` | code grading's identity | 9.11 |
| `kpi-6` chartreuse | `#C6D96B` | usage's identity | 11.10 |
| `kpi-7` sky | `#49B9EA` | merged-PR identity | 7.72 |
| `status-needs-you` amber | `#F8C15C` | Needs You label in the attention strip only | 10.05 |
| `status-blocked` coral | `#FF8172` | Blocked label in the attention strip only | 7.08 |
| `status-stalled` lavender | `#D6A7FF` | Stalled label in the attention strip only | 9.72 |
| `status-over-budget` pink | `#F58BC2` | Over Budget label in the attention strip only | 7.67 |
| `status-running` mint | `#4ADE9B` | Running label in the attention strip only | 10.02 |
| `status-stale` slate | `#8A95A3` | Stale label in the attention strip only | 5.67 |
| `grade-1` | `#FF8A80` | histogram bin 1, grade-1 outlier rows | 7.55 |
| `grade-2` | `#E0A33A` | histogram bin 2, grade-2 outlier rows | 7.77 |
| `grade-3` | `#9AA4B2` | histogram bin 3 — below a source bar, not an outlier | 6.83 |
| `grade-4` | `#3FC98A` | histogram bin 4 | 8.15 |
| `grade-5` | `#86F0BE` | histogram bin 5 | 12.48 |
| `unavailable-stroke` | `#7A8492` | hatch strokes, dashed outlines, `—` glyph | 4.55 |

- contrast: every ratio is the WCAG 2.x relative-luminance contrast against **Neutral's** dark
  `card` (`#1B1B1B`), read out of the running prototype with `getComputedStyle` rather than taken
  from core's defaults. **All twenty clear 3:1** (the non-text-graphic floor) and **all nineteen
  informational tokens clear 4.5:1** (AA body text). `unavailable-stroke` is deliberately the only
  token near the floor — 4.55:1 on the card but **3.38:1 on the `--color-neutral` hatch ground**
  (`#323232`), which is the surface it is actually drawn on; it is never information (the S-4 badge
  and the reason sentence carry that), and 3:1 keeps a hatch visible without letting an absence read
  as loud as a value. It was lightened from `#6E7885`, which measured 2.86:1 on that ground.
- **Astryx's `--color-data-*` tokens were considered for the KPI hues and the grade ramp, and
  rejected on measurement.** Both the ten `--color-data-categorical-*` and the five-step
  `--color-data-<hue>-1..5` ramps ship **one value for both modes** (`light-dark(x, x)`), and on the
  dark card `categorical-blue` `#0171E3` measures 3.67:1 and `categorical-purple` 2.65:1 — under the
  AA floor. The sequential ramps are worse and wrong in shape besides: a single-hue ramp cannot
  carry a diverging worst→best ordinal. The feature's seven hues and five grade steps therefore stay
  literals in the `defineTheme` call. `--color-success/-error/-warning` were likewise not adopted for
  the direction roles: they are Astryx's *status* semantics, reused by Banner, FieldStatus and input
  validation, so a theme is free to retune them for legibility on a filled status background and
  would silently repaint chart direction; and `direction-neutral` has no Astryx counterpart that
  clears the floor, which would leave two of the three roles sourced one way and one the other.
- **Neutral's own `--color-text-disabled` is not used as the third text step.** It means
  "inoperable", which is wrong for a sourcing rule that must be read. Hence the one text token this
  contract adds.
- **The grade ramp is ordered worst → best and intensifies toward best**: red, amber, slate, green,
  a stronger green. `grade-3` is slate on purpose — below a source bar is not an outlier — and
  **the cyan that used to sit at `grade-5` is gone**: it was byte-identical to the old `series-2`
  token, so a palette collision made a chart line and a "best grade" bar the same colour, and being
  colder than `grade-4`'s green it inverted the ordinal it was meant to top.
- **`series-1…3` are retired.** A trend line takes the identity hue of the KPI it belongs to
  (`kpi-1`, `kpi-3`, `kpi-5`, `kpi-7`), so nothing has to hold a mapping between a series number and
  a metric.
- Grade bands are **five**, not three, and the five map 1:1 onto `code_grade.py`'s scale, where 1 is
  worst and 5 best (`code_grade.py:30-44`). **The bar is per record, not global** — 3 for a test
  path, 4 otherwise (`code_grade.py:484`) — which C-2 turns into a chart capability, not a colour.

## Direction encoding

**Colour has three narrow jobs on this surface and they are never conflated.** A **KPI identity
hue** answers *which metric am I looking at*; a **direction role** answers *is this better or worse
than it was*; a **status hue** is permitted only on the matching attention-card label. Status in the
work list is carried by an Astryx icon plus its printed label and reason, never by coloured text,
border or top-line.

| Role | Where it may appear | Where it may never |
|---|---|---|
| identity hue `kpi-1…7` | the tile's label dot, its sparkline stroke and 12%-alpha area fill and end dot, its panel's header accent rule, that KPI's Shape B line and y title, its column header dot | a delta, a grade bin, a status state, any judgement of good or bad |
| `status-*` | the matching attention-card label text, and nowhere else | an icon, work-list text, border, top-line, KPI, delta, grade, or gap state |
| `positive` / `negative` / `direction-neutral` | the delta chip, and nothing else | a series, a tile, a bin, a table row |
| `grade-1…5` | the histogram's bars and the grade numeral in an outlier row | anything that is not a grade |

**Every KPI declares a polarity, and a delta's colour is resolved through it** — so a fall is green
for cycle time and red for the at-or-above-bar share, and the surface never asks the reader to
remember which:

| KPI | Polarity | A fall means |
|---|---|---|
| 1 Throughput — cycle time | **lower is better** | better |
| 2 Rework — cycles used of allowed | **lower is better** | better |
| 3 Blocking human touchpoints | **lower is better** | better |
| 4 Escaped defects | **lower is better** | better |
| 5 At-or-above-bar share | **higher is better** | worse |
| 6 Usage by agent / model tier | **none — descriptive** | neither. A change in attributable share is not a result, and the chip renders in `direction-neutral` |
| 7 Merged PRs over time | **none — descriptive** | neither. A count change is not a judgement, so the chip renders in `direction-neutral` |

**The chip's contract.** It carries an **arrow glyph** (▲ rise, ▼ fall, `=` no change), a **signed
number with its unit** (`−0.5 d`, `+7 pp`), and the words **"vs prior *w*"** naming the window it
compared against — so the direction survives without colour (C-3) and the comparison is never
implicit. Three cases are not the same thing and must not be rendered as one:

1. **the prior window holds a measurement** → the chip, coloured by the polarity above;
2. **the prior window exists and holds no measurement for this KPI** → **S-4's treatment on the
   chip**: the `—` glyph on the hatch, the "unavailable" badge, and the specific reason. Never a
   `0.0` and never a "0%" change;
3. **the window has no prior window at all** (`all`) → **no chip and no text.** Nothing failed to
   compute and nothing is unavailable, so borrowing S-4's treatment here would teach the reader to
   ignore it.

## Type

**The type system is the theme's, entire. This contract adds no family, no size, no scale and no
letter-spacing** — the family is whatever the base theme sets, which under Neutral is **Figtree**
for both body and heading, and the scale is Neutral's `--text-*` presets. Every string on this
surface is an Astryx `<Text>` with a `type` preset —
`display-1 | display-2 | display-3 | large | body | label | supporting | code` — plus `weight` and
`color` props. There is **no parallel size scale**: a component that sets `fontSize`,
`fontFamily`, `letterSpacing` or `textTransform` is a violation, and
`grep -rn -e 'fontSize:' -e 'fontFamily:' -e 'letterSpacing' -e 'textTransform' src` is the check.
It may match exactly one thing: the chart layer's shared SVG text style, which names Astryx's own
`var(--font-family-body)` and `var(--text-supporting-size)` because an SVG `<text>` is the one place
a `<Text>` cannot go.

**Which preset each surface element takes:**

| Element | Preset |
|---|---|
| page title | `display-3` as `h1` — the page is an instrument panel, so the largest thing on it is a measurement, never a title |
| KPI tile headline figure | `display-1`, `weight="semibold"`, tabular figures |
| panel headline figure, and the tile figure on a feature page | `display-3`, tabular figures |
| the figure's unit (`d`, `%`) | `large`, `color="secondary"` |
| panel title, section heading, empty-state heading | `large` as `h2` / `h3` |
| tile label, table header cell, table group/subtotal label | `label` |
| table cell value, a sentence carrying a measurement | `body`, `weight="semibold"` on the value |
| a visible caveat or denominator sentence under a table | `body`, `color="secondary"` |
| delta chip glyph, number and "vs prior *w*" | `supporting` |
| a secondary line under a cell, breadcrumb, provenance, meta | `supporting` |
| axis tick, gridline label, y title, end-of-line label | the SVG text style — Astryx's body family at `--text-supporting-size` |
| a code-like string | `code` |

`size` is spent in one place only, and it is the place Astryx's own doc names — "custom UI elements
that need explicit size control (metrics, callouts)": the KPI headline figure takes a **display**
preset rather than a heading one. No other element overrides a preset's size.

- **Tabular figures everywhere a number is shown, and mono almost nowhere.** Every numeral —
  headline figure, table cell, count, share, delta, axis tick, sparkline readout — carries Astryx's
  `hasTabularNumbers`, so no column of counts jitters row to row. That is what the jitter argument
  actually requires; it never required a monospace family.
- **`code` is for code-like strings and nothing else**: a qualname, a file path, an extension
  (`.rb`), a payload path (`.harness/metrics/trend.jsonl`), a commit-prefix bucket id (`no_prefix`,
  `unresolvable_step_id`). **Ids, dates, counts, ticks, drivers and week buckets are body family** —
  `FIX-02` is a name, `2026-08-19` is a date, and neither is source code. Setting them in mono made
  the surface read as terminal output rather than as an instrument panel.
- weights: the preset's own weight, `medium` for a label that must lift off its row, `semibold` for
  a value. No numeric weights.

## Spacing and layout

- unit: 4px. Every margin, padding and gap is a multiple.
- radius: **Astryx's own scale.** `--radius-element` (8px) for controls, chips, cells and hatch
  patches; `--radius-container` (12px) for cards and panels; `--radius-full` for the identity dot.
  No other radius, and **no custom radius token** — the earlier 6px/10px pair sat within 2px of
  Astryx's steps, which is not a difference worth a parallel scale.
- **container: centred, `max-width: 1600px`, 24px desktop gutters, 16px below 832px.** At the
  1440px design floor it still supplies 1392px of usable content; at wider desktops it caps scan
  travel and line length instead of making the dashboard full-bleed. The same container wraps the
  shared-header contents, every route's main content and the footer, so their left edges never drift.
- breakpoints: 640 / 832 / 1024 / 1440, written in `rem` (40 / 52 / 64 / 90) so a reader who scales their font
  gets the layout their text size needs. **No layout below 640 is designed** (see §Out of scope).
- **KPI-R1 — Overview's KPI tiles use exactly two rows in a 4+3 split at ≥1024.** Tiles 1–4
  fill row 1 at equal width; tiles 5–7 fill row 2 at equal width. No tile spans a row, no slot is
  empty, and reading order remains 1…7. At the 1440px design floor, the 1392px usable container
  gives row 1 a 339px tile width and row 2 a 456px tile width: the narrower row still keeps the
  `display-1` figure, delta chip and full-width fourteen-day sparkline legible, while the longer
  Usage by Agent / Model Tier label sits in the wider row. Below 1024 the existing fallbacks remain:
  two columns with tile 7 spanning both, then one column below 832px.
- **A KPI panel at `/kpi/$n`** uses the existing charts-left / tables-right split at
  `minmax(0, 2fr) minmax(0, 3fr)` with a 24px gap. Below 1024 the columns stack, chart first.
- **The work list is the final section of `/`.** Its six Status shortcut cards open the section,
  followed by its controls directly above its content. The Table layout scrolls horizontally within
  its own bordered region and keeps its id column sticky left; the Kanban layout scrolls its station
  lanes within the container. Neither layout hides a field, and cards wrap their detail grids rather
  than forcing the page itself to overflow.
- **`/work/$id` uses one full-width operational header before the existing 2fr/3fr per-feature KPI
  split.** The header is not a sidebar and is never below KPI content.
- Charts fill their container width and keep the existing explicit heights: histogram 280px,
  time-series 120px per plot row, tile sparkline 48px; no chart has a fixed pixel width.
- **Hard breakpoints are the one thing Astryx's layout primitives cannot express** (`<Grid>` offers
  auto-fill from a minimum width, which at 1200px gives five or six tiles across rather than four),
  so the four responsive layouts live in one stylesheet, `src/layout.css` in the prototype. It
  carries grid templates, breakpoints and Astryx spacing tokens — **no colour, no type, no radius**.

## Component direction

- **Dense over airy, and the density is FIGURES rather than sentences.** This is an instrument panel
  read by one person looking for a number, not a marketing page. A tile shows its figure, its
  denominator and its trend, and nothing else. **Operator ruling 2026-09-05: the page was busy, and
  what made it busy was prose.** Every explanatory, sourcing and caveat sentence moved off the
  surface and behind an info icon (below); what a card shows is what was measured.
- **A figure never appears without its denominator or its unit.** "4" is not a measurement; "4 of 12
  features" and "4.2 days" are. A reviewer may call any bare figure a violation.
- **KPI 4 and KPI 7 put their complete sourcing rule in an adjacent, one-click,
  keyboard-operable InfoDisclosure.** The trigger sits with the figure it justifies in both the tile
  and panel; click, Enter or Space opens the complete rule. The rule is never persistent inline
  text, a tooltip, a page-footer footnote or a link. S-3's Python-only caveat is different: it
  remains visible beside the affected figure because the visible value is partial without it.
- **A navigable name is never identified by colour alone, because Neutral's accent is monochrome.**
  `--color-text-accent` resolves to `#EBEBEB` — near-identical to `text` — so a link
  rendered in the accent is indistinguishable from a value and the affordance survives only as a
  cursor. Every feature name that navigates carries a **non-colour** affordance: an underline, or
  a chevron, present at rest and not on hover (§Nothing is hover-only). The fix is a component
  property, never an override of `--color-accent`.
- **No modal at any depth, and exactly ONE layered disclosure: the InfoDisclosure.** Every drill-down
  is a route (C-1), so every view is linkable, reloadable and back-button-safe; a modal would make
  SC-11's hand test unshareable. The clause this bullet used to carry — *no popover, no overlay, no
  layer drawn above the page* — is **withdrawn for one element and one only**, by the operator's
  2026-09-05 ruling that the explanations belong behind an icon:
  - **What it is.** An Astryx `IconButton` (`variant="ghost"`, `size="sm"`) carrying the theme's own
    `info` glyph, **immediately right of a tile title, a panel title or a table title**, opening an
    Astryx `Popover` anchored to it. One per card, never two, and never anywhere else.
  - **How it behaves, and each clause is checkable.** Opens on click and on **Enter or Space**;
    closes on **Escape** and on **click-outside**; **focus returns to the icon** on close
    (`document.activeElement === the button`, measured); the trigger carries `aria-haspopup="dialog"`,
    `aria-expanded` and `aria-controls`; the panel is `role="dialog"` with the accessible name
    **"About <title>"**, which is also the icon's own label.
  - **What it holds.** The card's definition sentence, its sourcing rule where one exists, its
    polarity, and the caveats and counts that used to sit on the surface — body type `supporting`,
    **max width 320px**. Never a value that appears nowhere else: a disclosure explains numbers, it
    never carries one that the page does not already print.
  - **What it may never be.** A hover target (it is click/keyboard only), a `title` attribute, the
    only route to a measurement, or a second layer type — no tooltip, no dialog, no drawer joins it.
  The two inline disclosures this contract used to ask for — S-2's names list and S-3's
  ungraded-extension list — are now that card's InfoDisclosure copy, not `Collapsible`s in flow.
- **Nothing is hover-only.** Every fact a hover would reveal is also present as text, because SC-11 is
  hand-executed and hovers do not survive a screenshot, a keyboard, or a touch device.
- **Every render state is visually distinct and none is an anonymous grey box.** Loaded and loading
  are not numbered states: loading is a skeleton in the eventual shape, and no partial payload
  mounts a chart. C-4 pins S-1…S-7; S-6 and S-7 extend the existing five without borrowing their
  dashed empty card, hatch, caveat line, ordinary unattributed rows, glyph, or badge.
- **The shared header has exactly two value controls, in this order:** (1) the window segmented
  control `30d`, `90d`, `All`; (2) an Astryx `Selector` labelled **Repository**, with **All** first
  followed by repository names alphabetically. Both sit at the far right, write URL search
  parameters (`window`, `repo`), and default independently to `all`. The header appears identically
  on all three product routes. Changing either value replaces only that parameter and preserves the
  route, the other shared parameter and, on `/`, every work-list parameter.
- **There is no Work toggle.** The left side carries the product name and route breadcrumb;
  breadcrumbs are `Overview`, `Overview › KPI n`, and `Overview › Work › <id>`. Fixture provenance
  is one supporting line in the footer.
- **Casing is semantic, not incidental.** Titles, card labels, dropdown items and toggle labels use
  Title Case; descriptions, reasons and explanatory sentences use sentence case. Stored URL values
  remain lowercase and do not leak into displayed labels.
- **Tile anatomy, pinned because "a big figure and a denominator" left an earlier build with no
  hierarchy at all.** Every KPI tile, in this order, top to bottom, and **nothing else on it**:
  1. **the label** — Astryx `label`, `text-secondary`, preceded by an 8px dot in the KPI's identity
     hue and **followed by the InfoDisclosure icon**. **Not uppercase and not tracked**: neither is
     an Astryx idiom, and a dot plus a weight step already separates a label from a value;
  2. **the figure** — `display-1`, `semibold`, tabular figures, `text`; its unit in `large`,
     `text-secondary`, on the same baseline;
  3. **the delta chip** — §Direction encoding's arrow, signed number and comparison, or S-4 where
     the prior window holds no measurement, or nothing where no prior window exists;
  4. **the secondary line** — `body` in `text-secondary`, one denominator or second term;
  5. **the sparkline** — spans the tile's complete inner width, 48px tall, and uses exactly the last
     fourteen days in daily buckets; identity hue with 12% area fill, a last-point marker and
     printed end value. It never shares a row with the figure. Gap counts live in InfoDisclosure.
  Every tile carries the same anatomy; row position never gives a tile a second anatomy.
- **There is no theme toggle and no light theme.** `<Theme mode="dark">` is fixed, the OS preference
  is never consulted, and no control offers an alternative. Restoring light requires a new set of
  ratios and an operator decision.

## C-1 — three product routes and one dashboard

**Navigation model: TanStack Router, exactly three product routes, and URL-owned view state.**
There is no `/work` route, Work header toggle, alias, redirect or hidden product route. The
prototype-only `/__fixtures/gap-states` route is named in §The prototype gate and is explicitly
outside this product table.

| Product route | Operator question | Required composition |
|---|---|---|
| `/?window=<w>&repo=<r>&station=<s>&status=<a>&kind=<k>&layout=<l>` | How is this repository doing, what needs attention, and what work exists? | shared header → Repository KPIs → work list, opening with the six-card Status shortcut strip before its filters and layout toggle |
| `/kpi/$n?window=<w>&repo=<r>` | What is behind this KPI? | shared header → exactly one KPI panel; every feature/bug row links to `/work/$id` |
| `/work/$id?window=<w>&repo=<r>` | What is operationally true about this feature or bug, then what do its KPIs say? | shared header → operational header → existing per-feature KPI content |

`window` accepts `30d`, `90d`, `all`; `repo` accepts `all` or a repository id. Both default to
`all`, are always present after the first navigation, survive reload and Back, and are sent
unchanged to both APIs. The dashboard's `station`, `status`, `kind` and `layout=kanban|table` are
also URL parameters; Table is the default. `/work/$id` accepts FEAT and BUG ids only. Grilling and
worktree ids have no detail route.

### Single-dashboard composition

The `/` hierarchy is fixed, in this order:

1. **Shared header, 72px minimum height:** Operations Dashboard and breadcrumb at left; `30d / 90d /
   All` then the 180px Repository Selector at right. Each control has a persistent label.
2. **Repository KPIs:** the first content section, laid out under KPI-R1 in §Spacing and layout.
   The fixed order is Throughput, Rework, Blocking Human Touchpoints, Escaped Defects, Code
   Grading, Usage by Agent / Model Tier, **Merged PRs Over Time**. Each tile links to `/kpi/$n`;
   each sparkline spans the complete tile width and covers the last fourteen daily buckets.
3. **Work List:** opens with the **Status shortcut strip**, six equal cards in D-25 order, then
   Station / Status / Kind filters, the Kanban / Table layout toggle, result summary and every FEAT,
   BUG, grilling note and registered worktree in the selected repository and filter slice. Each
   shortcut card shows one neutral Astryx status icon, its Title Case label and a tabular count.
   Activating a card changes the Work List's **Status** filter in place while preserving `window`,
   `repo`, `station`, `kind` and `layout`; it never navigates to another route. The card whose state
   matches the current Status filter carries the neutral selected treatment. Every card uses the
   neutral white border. Its state colour appears on the label text only — never the icon, count,
   background, border, top-line or selected treatment.

The header and sections use 24px major vertical gaps and 16px internal gaps. “Single dashboard”
means one continuous route, not that all rows must fit in the first 1000px of height.

### KPI drill

`/kpi/$n` renders one panel and no aggregate sibling panels. C-2 still defines the panel artifact:
KPI 1 Shape B; KPI 2 TBL-1; KPI 3 Shape B; KPI 4 TBL-2; KPI 5 Shape A plus Shape B and the named
outlier table; KPI 6 TBL-3; KPI 7 the merged-PR weekly line and its shipped-feature table. Every row
whose id is FEAT or BUG is a real underlined anchor to `/work/$id`, preserving `window` and `repo`.
The drill is tile → `/kpi/$n` → row → `/work/$id`, with no modal.

### Work list: common contract

- **Station**, **Status** and **Kind** are three independent Astryx Selectors, each with **All**
  first. There is no Repository filter in this section; repository scope exists only in the shared
  header.
- Station uses `backlog`, `plan`, `ready`, `building`, `review`, `done`, `abandoned`; Status uses
  the exact D-25 order; Kind uses `FEAT`, `BUG`, `Grilling`, `Worktree`.
- A result summary reads “*n* of *m* items” and **Clear Filters** appears only while Station,
  Status or Kind differs from `all`.
- Every item exposes, without hover: **id · repository · station and phase · Status and every
  reason · elapsed total and plan/build/validate · runs · cycles/max · tokens**. The active phase
  reads “so far” and takes S-6. Partial token coverage takes S-7 and literally reads
  `unmeasured n of m runs`; zero is reserved for a measured zero.
- FEAT and BUG ids are real anchors to `/work/$id`. A grilling or worktree row is a button with
  `aria-expanded`; activating it inserts one neutral bordered detail region immediately after
  itself, showing `source_path`, and for a worktree also branch, primary/linked status and mapped
  feature. Activating it again collapses it. Expansion never changes route and never opens a modal.

#### Work-list empty and failure states

- **Filtered zero is not an unavailable list.** When active Station, Status or Kind filters match no
  valid rows, the result summary reads **“0 of m items”** and the list region renders **“No work
  matches these filters”**, **“Clear Station, Status, or Kind to see work.”** and **Clear Filters**.
  Clear Filters resets only `station`, `status` and `kind` to `all`; it preserves `window`, `repo`
  and `layout`, returns focus to the programmatically focusable **Work List** heading, and announces
  the resulting count through the list's one polite live region.
- **A successful payload with source errors remains useful.** Valid rows stay visible, filterable
  and operable. A neutral warning banner reads **“Some sources could not be read”** and lists every
  failed `source_path` with its specific reason. A malformed item becomes one of these source-error
  entries; it never renders as a broken row and is never silently omitted.
- **An initial request failure replaces only the list result region.** Before any usable rows have
  loaded, it renders **“Work list unavailable”**, the specific failure reason and **Retry**. The
  current URL state is untouched. Appearance of the failure does not steal focus; Retry retains
  focus while its request is pending and the polite live region announces the failure once.
- **A refresh failure never erases good rows.** The last usable rows remain visible and are marked
  stale; a failure banner gives the specific reason and offers **Retry**. The URL and current
  control focus remain unchanged, and the polite live region announces that previous results
  remain on screen.
- **Retry has one completion rule.** A failed retry leaves focus on Retry and updates the announced
  specific reason. A successful retry clears the failure or stale banner, focuses the **Work List**
  heading and announces the new result count. Manual Refresh follows the same focus, stale-row and
  live-announcement rules.

**Status icon vocabulary — one Astryx semantic icon per state, everywhere the state appears:**

| Rank | Status | Astryx icon |
|---|---|---|
| 1 | Needs You | `warning` |
| 2 | Blocked | `stop` |
| 3 | Stalled | `clock` |
| 4 | Over Budget | `arrowUp` |
| 5 | Running | `wrench` |
| 6 | Stale | `eyeSlash` |

The icon is primary-colour, followed by the complete printed label and visible reason. No status
uses coloured text in the work list, a coloured border, a coloured top-line, or colour as a second
carrier. The sole colour exception is the matching label text on the six attention cards above.

### Work list: two layouts

The switch labels are exactly **Kanban** and **Table**, with no letter prefixes. Its active state
uses a neutral inset indicator and no white border. **Table is the default.**

**Kanban.** Station lanes appear in lifecycle order. Each lane prints its item count and contains
cards sorted by status rank then oldest write. Every neutral-bordered card prints the full common
field set; the Astryx status icon and printed Status sit inside the card, never on its border or
top-line.

**Table.** One row per item, default sort Status rank then oldest write, with sortable headers for
ID, Repository, Station / Phase, Status, Elapsed / Phases, Runs, Cycles / Max and Tokens. The
column is named **Status**, never “Attention + reasons”. Reasons and phase durations remain visible
sublines, not disclosures. The id column is sticky and horizontal scrolling is contained inside
the table region.

### Work detail

`/work/$id` starts with an operational header, before any KPI title or chart. Its first row is id
and name, repository, station and phase, run state and the Astryx status icon plus printed Status
and every reason. Its second row is `source_path`, `main_path` and nullable `worktree_path` in code
type; absent worktree path reads “no linked worktree”, never blank. Its third row is budget
(`cycles/max` and remaining), elapsed total plus plan/build/validate, runs, and tokens. Active
elapsed uses S-6; partial tokens use S-7. Below a 24px divider, the existing per-feature KPI content
renders; KPI 7 is absent because it has no per-feature value.

The route title is programmatically focusable for route landing but is not in ordinary tab order.
No operational field is pushed into InfoDisclosure: it is primary content.

## C-2 — the two chart shapes and the three tables

**Two chart shapes and three tables exist in this feature, and nothing else** — C-1's seven panels
draw on every one of the five and ask for no sixth. Each chart capability below is a pass/fail question
eng-lead can put to the charting library's current alpha API. **Where a capability's `If absent` cell
names a server-side workaround, that workaround is the fallback; no replacement charting library is
named in advance, and naming one would be an operator decision taken on T-18's probe evidence, needing
its own plan Decision.** The three tables carry no capability list because they need none: they are
Astryx table primitives with no charting-library dependency at all. That is why the categorical panels
are tables rather than a third chart shape (LD-1), and why
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

**Shape B — time-series (cycle time, touchpoints, code grade over time, merged PRs; REQ-10).**
Four KPI panels mount it, plus a sparkline on each tile. KPI 7 is one weekly merged-PR series; its
adjacent shipped-feature table carries the same events as text. The existing CAP-07…CAP-13 contract
applies unchanged: a temporal axis, line breaks over gaps, token-supplied colour, text equivalents,
and container responsiveness. No second KPI-7 series or ticket bucketing exists.

| ID | Capability | If absent |
|---|---|---|
| CAP-07 | A **temporal x axis with irregularly spaced points.** Ships are irregular; a library assuming a uniform interval fabricates a cadence. | hard requirement |
| CAP-08 | **Three series in one plot with per-series y-axis assignment** (hours, a count, and a 1–5 grade share no scale). Still probed by T-18 — the library's answer belongs on the record either way. | **Settled — this is what gets built, whatever the probe returns: three stacked single-series plots sharing one x axis and one window.** The decision and its reason live in plan.yaml T-15; this contract pre-authorised the outcome, so it is the chosen build, not a fallback, and no redesign follows. |
| CAP-09 | **A missing point breaks the line.** No interpolation across a gap, no coercion to zero. This is REQ-11 expressed as a chart capability and it is the single most important one. | segment each series server-side into contiguous runs and render one line per run — deterministic, and preferred if the library's null handling is not explicitly documented |
| CAP-10 | Zero-point series renders no axes and no baseline — hands over to S-1. | as CAP-04 |
| CAP-11 | **Per-series dash pattern and point-marker shape**, set independently of colour. | hard requirement of C-3; if the library cannot, draw markers as an overlaid series |
| CAP-12 | Point identity is reachable **as text** — each point's feature id appears in the adjacent table, and any tooltip is a duplicate of it, never the only copy. | ours to supply |
| CAP-13 | Responsive to container width without a fixed pixel width, and no SSR/hydration requirement (client-only is fine). | wrap in a resize observer |

**What the region looks like, pinned here because CAP-01…CAP-13 is closed at thirteen and none of
this is a library capability — it is composition, and it is what a reviewer checks by pointing:**

- **One region for the window in the URL.** Never one region per window token, and never two
  windows side by side. A surface that renders every window at once is a design proof, not a
  product.
- **Three stacked plots, one shared x axis at the bottom** (CAP-08's settled outcome), each plot
  **120px** tall with a 24px title band above it. The row was 88px when the region spanned a
  max-width container; three 88px rows in a chart column read as three hairlines, so the row keeps
  its height and the axis sheds ticks instead when the column narrows.
- **Three gridlines per plot** — at the series' minimum, midpoint and maximum — drawn in `border`,
  each labelled at the axis with its own unit, in the SVG text style §Type pins (Astryx body family
  at `--text-supporting-size`, tabular figures). No fourth line, and no gridline on the sparklines.
- **A y title at the top-left of each plot**, `<label> · <unit>`, set in **that KPI's identity
  hue** — so the plot, the tile that spawned it and the table column beneath it agree on colour.
- **As many x ticks as FIT, never a fixed count**: a date label needs ~78px, and a tick is taken
  only where it clears the previous one by that much, with the last point always labelled. A fixed
  six ticks overlapped by 46px in the 2fr chart column once the fixture's ships clustered into one
  fortnight — evenly spaced *indices* land on clustered *times*, and an overlapping tick is a date
  the reader has to guess. Two ticks for a two-point series is not a violation.
- **A CAP-09 gap is drawn, not merely left out: a hatched vertical band** across the plot, in the
  hatch pinned in C-4 S-2, spanning the missing points and half the distance to each present
  neighbour, outlined 1px dashed in `unavailable-stroke`. The line still breaks — the band is what
  makes the break a stated absence rather than an ambiguous discontinuity — and the count of
  hatched points is printed beneath the region in text.
- **The region's header states the window and the ship-record count** it drew from.

**§Tables — the three categorical panels.** Each is an Astryx table primitive rendering a real
`<table>`, sortable by activating a column header, with the sort reflected in the URL wherever the
panel is itself a route. **Every count carries its denominator** (§Component direction), every
unavailable cell takes S-4's treatment, and no table shows a total the payload does not carry.

| ID | Panel | One row is | Columns, in order | Row order | Beneath the table |
|---|---|---|---|---|---|
| TBL-1 | 2 Rework | one feature in the window | feature id, linking to `/work/$id` · `cycles_used` · `max_total_cycles` · the two-term ratio | `cycles_used`/`max_total_cycles` descending, ties by feature id ascending | the aggregate as **both terms summed** and never as a lone ratio (T-06) |
| TBL-2 | 4 Escaped defects | one escaped-defect item | kind (`bug_unit` or `revert`) · id · date · subject | date descending | nothing. The window count is the panel's figure; **the complete sourcing rule and denominator are in the adjacent InfoDisclosure on both tile and panel** — never persistent inline text, a tooltip, a page-footer footnote or a link (REQ-05, SC-13, SC-20) |
| TBL-3 | 6 Usage by agent / model tier | one attribution bucket | bucket — a model-tier name, or one of the four named unattributed buckets · commit count · share of `total_commits` | attributed tiers first, count descending; then the four unattributed buckets in the fixed order `no_prefix`, `human`, `feature_only`, `unresolvable_step_id` | `total_commits` and `attributable_share`; **the two groups are separated by a rule and each is subtotalled**, so attributed and unattributed can never be read as one list |

**KPI 7's shipped-feature table is unnumbered.** One row is one shipped feature in the selected
window: feature id linking to `/work/$id` · ship date · week bucket · nullable PR reference. An
absent PR reference uses S-4's em dash and reason but does not change the merged-PR count: the
sourcing rule states that one shipped feature is one merged PR. TBL-1…TBL-3 remain the three
categorical panels' primary artifacts.

**TBL-3's two groups are never merged and no bucket is ever omitted** — including a bucket whose count
is zero, which renders as a measured `0` in S-4's genuine-zero treatment and never as a dropped row
(SC-14, D-13). A single "unattributed" total standing in for the four named buckets is a violation.

## C-3 — dark only, colour never carrying meaning alone, and keyboard operability

**Light is out of scope by operator ruling, 2026-09-04.** There is one theme, it is dark, and
`<Theme mode="dark">` fixes it: the surface never consults the machine's colour-scheme preference,
and there is no toggle to consult instead. Every token ships as a **single value** rather than a
`[light, dark]` tuple — `defineTheme` documents a bare string as "used as-is for both modes", so the
tuple form was only ever carrying a theme this surface no longer has. **The light/dark parity clause
this section used to hold is withdrawn**, along with every light-column measurement it required.
Restoring light is a token-file change and a new set of ratios, not a redesign; the operator may ask
for it.

There is no second stylesheet, no OS-preference media query inside component source, and no
theme-conditional branch in a component: a value that differs by state differs **in the token**.
That is the check — an `isDark` ternary or a colour-scheme query in a component is a violation.
**Verified in the running prototype** with the OS preference emulated as light: `color-scheme`
computes `dark` and the painted ground is `rgb(27,27,27)`, Neutral's own dark body.

**Chart colours are tokens passed in, not library defaults** (§Substrate rule 3), so a chart that
looks wrong is a token bug in one place rather than a chart bug in three.

**THE RULES BELOW ARE UNCHANGED BY THE LOSS OF LIGHT, and they are the ones that matter.** Neighbouring
KPI and Status-label hues are intentionally close enough that hue cannot carry meaning alone:

| Distinction | Carried by, beyond hue |
|---|---|
| better or worse than the prior window | an **arrow glyph** (▲/▼, `=` for no change) + a **signed number with its unit** + the words "vs prior *w*". The polarity-resolved colour is the third carrier, never the first (§Direction encoding) |
| which series a line is | dash pattern (solid / 6-2 dash / 2-2 dot / 4-2 dash) + marker shape (circle / square / triangle) + **a direct end-of-line label**, pushed apart from its neighbour when two series end level + the plot's own y title. A legend is a convenience, never the only mapping |
| which KPI a tile or panel belongs to | its position in the fixed 1…7 order + its printed label. The identity hue is a shortcut across surfaces, never the label |
| which grade a bin is | ordinal position on the axis + a printed bin label + the count printed under the bar |
| at-or-above bar vs below | the printed share and the word, plus CAP-03's hatch. Never green-vs-red alone |
| unavailable vs zero | glyph, typography, fill and a badge — all four (C-4, S-4) |
| an outlier row | the grade numeral in the cell, not only the row tint |

`unavailable-stroke` holds 4.55:1 against Neutral's dark `card` and 3.38:1 on the `--color-neutral`
hatch ground, so the hatch that marks an absence stays visible without ever competing with a value.

### Keyboard operability and focus

`ui` has no automated runner (BRIEF `## Verification gaps`), so SC-15's inspection is the whole gate
for this dimension, and an inspection can only catch what the contract pins. **"Accessible" is not a
contract term.** Each clause below is written so a reviewer can name what violates it.

**1 · Focus stops and order.** From document start every route begins with its Overview breadcrumb
when that breadcrumb is a link → window segments `30d`, `90d`, `All` → Repository Selector. Then:

- Dashboard: each KPI tile then its own info icon, in visual reading order 1…7 → six Status
  shortcut cards → Station → Status → Kind → Clear Filters when present → Kanban / Table toggle →
  sortable headers or lane controls → displayed row controls.
- KPI panel: panel info icon → sortable headers → displayed FEAT/BUG row links.
- Work detail: operational `<h1>` is the programmatic landing only, not a tab stop; then source-path
  links → KPI info icons → sortable headers → row links.

Charts are `aria-hidden` and not focusable. Badges, elapsed/token state marks, hatch cells, caveat
lines and figures are not focusable. Displayed sort order is DOM order.

**2 · Interactive focus indicator.** Every interactive element draws a 2px ring in the `text`
token, offset 2px, **only through `:focus-visible`**. Keyboard Tab and keyboard-restored focus retain
the ring. A mouse click on an attention card or filter leaves no visible outline. A blanket `:focus`
ring, background-only focus and a blanket `outline: none` without the paired `:focus-visible` rule
are violations.

**2a · Route-title exception.** A route `<h1>` is programmatically focusable with
`tabIndex="-1"` but is not interactive and never draws a ring: its `:focus` and `:focus-visible`
states both compute `outline: none`. A fresh document load leaves focus outside the title; only an
in-app route transition lands focus there. **Violated by:** a title in the Tab order, any visible
title outline, title focus on first document load, or an in-app route transition that drops focus
to `<body>`.

**2b · Pointer-aware Selector restoration.** When an Astryx Selector was opened by pointer, either a
pointer selection or dismissal restores its trigger with `element.focus({focusVisible: false})`;
this includes Escape after a pointer-opened menu. A keyboard-opened selection or dismissal restores
the same trigger with its `:focus-visible` ring intact. **Violated by:** disabling
`:focus-visible` globally, drawing a ring after any pointer-opened Selector closes, or suppressing
the ring after a keyboard-opened Selector closes.

**2c · Layout selection is not a focus ring.** The selected Kanban/Table segment keeps semibold
weight and its 2px inset bottom indicator, but its pill uses `neutral` for the surface and `border`
for the inset edge; a pointer click leaves `outline: none`. Keyboard focus still adds the focus ring
from clause 2. **Violated by:** Astryx's white `background-surface` pill, a coloured border, loss of
the selected weight or inset indicator, a pointer outline, or no keyboard outline.

**3 · Focus landings after transitions.** Focus is never dropped to `<body>`:
The title landings below apply to in-app transitions, never the first document load.

- attention card → the **Status** filter on the same dashboard, with its selected value announced;
- KPI tile → `/kpi/$n`: the panel `<h1>`, programmatically focusable with `tabIndex="-1"`;
- KPI row → `/work/$id`: the work-detail `<h1>` under the operational header;
- FEAT/BUG row on the dashboard → `/work/$id`: the same detail `<h1>`;
- grilling/worktree expand or collapse: the row button that was activated;
- changing any header or work filter: the changed control, after results settle;
- switching Kanban / Table: the toggle, then announce layout label and result count through one
  polite live region;
- browser Back: the exact card, tile or row link that initiated the route transition;
- InfoDisclosure open: the Astryx popover's first control; close by Escape or outside click returns
  to its info icon.

**4 · Names for visual marks.** Every chart has a real adjacent table carrying the same values.
Every status prints one Astryx icon plus its complete label; every S-2/S-4/S-6/S-7 reason is real
visible text, never a `title` or `aria-label` alone.

## C-4 — seven honest states, each visually distinct

A reviewer must be able to tell S-1…S-7 apart on screen without reading the payload. S-6 and S-7
extend elapsed and token reporting; they do not repurpose an existing gap treatment.

**S-1 · No ship record where one would be plotted** — `.harness/metrics/trend.jsonl` missing, or
holding no line for the thing being drawn. **The entire trend region is replaced**, not annotated:
one Astryx card, full region width, `--color-neutral` fill, a dashed 1px `unavailable-stroke`
outline, **no axes, no gridlines, no zero baseline, no chart mounted at all.** Headline in `large`:
"No ship records yet". Body in `body`: names `.harness/metrics/trend.jsonl` — one of the few strings
that takes `code` — states that the trend begins at the first ship after this capability landed, and
states that history is never backfilled. The non-trend KPIs render normally beside it: this state is
scoped to the region that had nothing to draw, never to the page.
**It has two scopes, and the copy is the only thing that differs**: the *project* scope, where the
selected window holds no ship record at all, and the *feature* scope, where one feature's own log
does — a feature that started after the capability landed and has not shipped yet. In a feature
table the feature scope is a cell: the hatch, an em-dash and "no ship record yet — this feature has
not shipped", badged S-1.
**KPI 7 is no longer in this state's scope.** It counts merged PRs, independently of whether a
particular trend region has a usable ship record.
*How a reviewer tells it from S-2:* on `/` and `/kpi/$n`, **no axes are drawn** for a region with
no records. On `/work/$id` the two treatments are deliberately identical and only the copy differs
— see S-2.

**S-2 · A pre-capability work item sitting among items that do have trend data** (SC-08, a
user-executed hand test on exactly this). On `/` and `/kpi/$n`, axes **are** drawn, because other
items have data. The pre-capability item is:
- **excluded from the line's path** — the line breaks (CAP-09), it does not descend to zero and it is
  not interpolated across;
- present in the KPI table with its trend cells on the hatch fill pinned below, carrying an
  em-dash `—` and the label "no trend — shipped before metrics". **The cell's reason stays in the
  cell** — it is the one explanatory line the 2026-09-05 ruling leaves on the surface, because
  telling a genuine zero from an absence is done where the two sit side by side;
- marked on the trend panel by its **S-2 badge**, and counted — "*n* of *m* items in this window
  shipped before metrics and have no trend line" — in that panel's **InfoDisclosure**, with the
  ids beside it. The badge is the marker; the sentence is one click away.

**The hatch fill, pinned here once and referenced by S-4 and CAP-03: 45°, a 1px stroke on a 6px
period, `unavailable-stroke` on `--color-neutral`.** Under Neutral, `muted` equals `card` in dark
(`#1B1B1B` both), so the translucent `--color-neutral` is the only ground that reads as an inset at
all (§Palette). The stroke is 1px at every breakpoint and does not scale with the cell. The angle
alone left two builders free to produce visibly different fills, which is the divergence this pin
closes. A reviewer checks the declared gradient stops in source, not a screenshot; the prototype
renders them at 1px/6px on every route.

**On `/work/$id`, S-2's table treatment does not apply — the full-region replacement does.** That
page shows one FEAT or BUG item, so there is no contrasting item to draw axes against, and axes drawn
for one item with no points is exactly the confident-empty-chart failure this contract prevents.
When the viewed item is itself pre-capability, **its whole trend region is replaced** by the same
treatment S-1 specifies — one Astryx card, full region width, `--color-neutral` fill, a dashed 1px
`unavailable-stroke` outline, no axes, no gridlines, no zero baseline, no chart mounted — but with
**S-2's copy, not S-1's**, because the reason is different: headline in `large` "No trend for this
item", body in `body` naming that this item shipped before metrics, that the trend begins at the
first ship after this capability landed, and that history is never backfilled.
The item's three non-trend KPIs (2, 4, 6) render normally beside it.
**A `/work/$id` page that draws trend axes for a pre-capability item is a violation**, and it is the
first thing SC-08's hand test should try.

*How a reviewer tells it from S-1:* on `/` and `/kpi/$n`, axes and other items' lines are present.
On `/work/$id` the treatments are identical by design and the copy is the only difference — S-1
names `.harness/metrics/trend.jsonl` and the selected repository's ship history, while S-2 names
this one item's. *From S-4:* the reason is a fixed historical fact, so the label is the same on
every such row and the row is never mistakable for a KPI that failed to compute.

**S-3 · The Python-only grading caveat** (REQ-08 / SC-06). **The one caveat sentence that stays on
the surface**, because REQ-08 requires the coverage gap to be visible rather than reachable: a
persistent `supporting` line beside its S-3 badge, **directly beneath the histogram**, inside the
same panel — never a tooltip, never a page-foot footnote:

> S-3 · Grading covers Python only · *N* of *M* files ungraded (*P*%)

It is **one line**, not a paragraph (2026-09-05): the extension list, the graded extensions and the
sentence explaining why the gap exists are the grading panel's InfoDisclosure copy. **Contract, and it is the SC-06
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
| value slot | the numeral `0`, `semibold`, tabular, `text` — **identical type and colour to any other value** | the glyph `—`, one weight step lighter, `unavailable-stroke`. **Never a numeral, never `0`, never blank** |
| second line | its denominator: "0 of 12 features" | **the reason, always present and always specific**: "no ship record for this feature", "no commit carries a resolvable step-id", or — for a touchpoint count — the not-tracked sentence plan.yaml D-21 pins for that branch, rendered verbatim from the payload rather than restated here. A generic "no data" is a violation |
| fill | the normal card | the hatch fill pinned in S-2 — 45°, 1px stroke, 6px period, `unavailable-stroke` on `--color-neutral` |
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

**A DAILY BUCKET WITH NO MEASUREMENT STILL TAKES S-4.** The line breaks and no point is plotted; S-6
and S-7 are reserved for operational elapsed and token coverage and never apply to chart buckets.
What a day means remains KPI-specific:

| The day carries | Treatment | Which KPIs |
|---|---|---|
| no ship, no active cycle, no grade snapshot, no commit | **a gap**: the line breaks, the span is hatched, and the gap count is printed beside the strip | throughput, rework, at-or-above-bar, usage |
| an instrument that ran and counted nothing | **a measured `0`**, plotted like any other value | blocking touchpoints, escaped defects, merged PRs |

D-19 reserves `0` for a **measured** zero, and that is exactly the line above: a day on which no
feature shipped is not a day of zero cycle time, while a day on which the defect scan found nothing
*is* a count of zero. Each gap carries its own reason from the payload — "no feature shipped on
`<date>`", "the code grader did not run on `<date>`" — never a generic "no data"; the tile prints the
count of gaps and the panel prints the reason. **A gap rendered as `0`, or a line interpolated across
one, is the fabrication this section exists to prevent.**

**S-5 · A large unattributed share, named rather than hidden** (REQ-09 / SC-14, D-13). Measured at
this repository, 753 of 975 commit subjects carry no harness prefix at all
(`notes/research-FEAT-53-routing-and-signals.md`, Signal 2), so on a typical project **most of KPI 6
is unattributable — and that is a measurement, not a hole in the data.** It is therefore neither S-1
nor S-4: nothing failed to compute, and nothing is unavailable.

- **On the tile:** the `display-1` headline figure is the **attributable share** (`attributable_share`), and
  the secondary line names the unattributed count against its denominator — "*u* of *t* commits
  unattributed". A tile presenting an attributed count as though it were the total is a violation
  (SC-14).
- **In the panel:** table TBL-3, with its two subtotalled groups and its separating rule.
- **Treatment:** the four unattributed rows are set in `text` in ordinary value type, **exactly as an
  attributed row is** — the same rule S-4 states for a genuine zero, that a measurement is presented
  with the confidence of one. **No hatch, no `—`, no "unavailable" badge, no muting**: an
  unattributed commit is a counted commit. What separates the group is its position, its subtotal and
  TBL-3's rule. **Each bucket's reason is in TBL-3's InfoDisclosure, keyed by the bucket id**
  (2026-09-05, superseding "a `supporting` line beneath each bucket id"): `no_prefix` "no harness
  prefix in the commit subject", `human` "attributed to a human", `feature_only` "a feature id with
  no task id", `unresolvable_step_id` "a step-id resolving to no agent or no model". The ids
  themselves stay, and they are the one thing in TBL-3 set in `code`, because they are payload
  literals. **The S-5 badge stays on the panel header**; its "*u* of *t* commits unattributed — a
  measurement, not a hole" sentence is disclosure copy.

*How a reviewer tells it from S-4:* S-5 carries numerals in ordinary value type with no hatch and no
badge, because these commits **were** counted. *From S-1 and S-2:* nothing is replaced and no region
is missing — the whole KPI renders. **Rendering the unattributed buckets in S-4's treatment is a
violation**, and so is collapsing them to one row.

**S-6 · Active phase elapsed, accruing through now.** This is a live duration, not missing data.
The value is ordinary semibold tabular text, preceded by a solid `▶` and followed by the literal
**“so far”** in `supporting`. A neutral inset rule may bind the duration to its active phase; the
Running status itself is carried by the Astryx `wrench` icon and printed label, never a coloured
border or top-line. Completed phases have no mark and read as plain durations; future phases read
`not started` in secondary text, never `0m`. S-6 uses no hatch, em dash, unavailable badge, dashed
outline or caveat line, so it cannot be mistaken for S-1…S-5.

**S-7 · Partially measured tokens.** The measured total remains a normal integer with the unit
`tokens`. Directly beneath it, an outlined badge **S-7 · partial** and the literal
**“unmeasured n of m runs”** appear beside a segmented coverage bar: measured runs are solid and
unmeasured runs are an empty outlined segment. If every run is unmeasured, the value slot is `—`
and the coverage text still names all runs; if every run is measured, no S-7 badge or coverage bar
appears. A measured total of `0 tokens` is legal only when every contributing run measured zero.
S-7 never uses S-4's hatch or “unavailable” badge: some measurements exist, so erasing the total
would be as dishonest as inventing zero for the gaps. No dollar cost appears.

## The prototype gate

**`needs_prototype: true`.** A person operates the window and Repository controls, uses attention
cards as Status shortcuts, switches the Work List between Kanban and Table, opens disclosures and
drills into KPI and work detail. The focus, density and layout transitions therefore require an
interactive prototype at real desktop widths; a static mockup cannot discharge this gate.

The committed Astryx + React prototype at `notes/prototypes/FEAT-53/` uses a synthetic fixture only.
Its product routes are exactly `/`, `/kpi/$n` and `/work/$id`. The prototype-only
`/__fixtures/gap-states` route is outside product navigation and exists only to make C-4's S-1…S-7
simultaneously visible. There is no `/work` list route, Work header toggle, redirect or alias.

The dashboard composes the shared Window and Repository header, Repository KPIs and the Work List
in that order. The six Status shortcut cards open the Work List, before its Station, Status and Kind
filters and Kanban / Table toggle; Table is the default. The cards filter Status in place and the
card matching the current Status filter carries the neutral selected treatment. Repository remains
a header-level scope and is not duplicated in the list. Grilling and worktree items expand inline;
FEAT and BUG items drill to `/work/$id`.

The former attention-grouped candidate and dedicated `/work` surface are rejected. The operator
selected the integrated dashboard with both Kanban and Table, not a three-candidate comparison.
Status is carried by the six specified Astryx icons and complete labels. Work rows and cards use
neutral text, borders and top-lines; only the matching attention-card label receives the state
colour. Every sparkline contains the latest fourteen daily points and spans the tile's inner width.

**Observed in a real browser.** After a fresh `npm run build`, Google Chrome over CDP exercised the
running prototype at **1440×1000** on 2026-09-16. `clientWidth === scrollWidth === 1440`. The
measured top edges established the required composition: Repository KPIs at 113.98px, Work List
heading at 619.98px, Status cards at 683.98px and filters at 769.98px. The seven KPI tiles remained
in exactly two KPI-R1 rows, at 339px per tile in row 1 and 456px in row 2, with no tile or text
overflow and no label collision.

Real Tab input traversed the Window and Repository controls, each KPI tile and its InfoDisclosure
in visual order 1…7, the six Status cards in D-25 order, and only then Station, Status, Kind and the
layout control. This discharges C-3 clause 1's changed order: every KPI control precedes the cards,
and every card precedes the Work List filters. Pointer-activating Needs You kept pathname `/`, set
`status=needs-you`, reduced the table to two fixture rows, and made Needs You the sole
`aria-current="true"` card with the neutral selected treatment.

An earlier same-date 1920×1080 observation remains the KPI-width reference: the capped 1552px grid
measured 379px and 509.33px per tile, with 355px and 485.33px sparklines, and the default table's
`clientWidth` and `scrollWidth` both measured 1550px. Card relocation was re-observed only at the
1440px design floor, as required.

The committed `observed-1440.png` records the current selected-card surface. The prototype README
records commands, the fixture boundary, measurements and observed interaction results.
`InfoDisclosure` remains the sole popover.

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

None. The operator settled one dashboard, both Kanban and Table with Table as the default, the
three product routes, the filter set and the status encoding on 2026-09-16.

**No Astryx gap was found.** The prototype pins `@astryxdesign/core` and
`@astryxdesign/theme-neutral` 0.5.2. The status vocabulary uses Astryx's own semantic icon registry;
the hatch fill Astryx does not ship is composed from a CSS gradient over an Astryx surface primitive
(§Substrate rule 4), not from a second component system.
