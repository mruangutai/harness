# Receipt — harness-frontend-dev — A2 (TanStack Charts alpha coverage) — FEAT-53

**BLUF: NO, the bet as written is not sound.** The library itself is capable enough (CAP-01, CAP-07,
CAP-09 are genuinely well supported by the current `@tanstack/charts` alpha), but D-08's actual named
fallback is dead (npm `react-charts`, unmaintained since 2023-11-02, requires React 16 against a
React-19-only substrate), T-15's own verify command cannot pass on its own STOP branch, and the probe
that is supposed to de-risk the bet runs after the entire client UI is already built — inverting the
purpose the decision states for itself. None of this was reachable without hitting the npm registry
directly; MCP doc-query access (`xd://mcp__context_context_query_docs`) was blocked by this dispatch's
write-domain hook, so registry metadata (`registry.npmjs.org`) and `unpkg.com`-served package docs were
used instead — every claim below is cited to one of those two sources, version `@tanstack/charts@0.16.0`
/ `@tanstack/react-charts@0.16.0` (current `latest` as of this review) and `react-charts` (npm,
unscoped) `latest`/`next`/`beta` dist-tags.

## CAP-01..CAP-13 (against `@tanstack/charts@0.16.0` docs, since `@tanstack/react-charts@0.16.0` is a
thin dependant of the same engine — see Finding F4)

| ID | Verdict | Evidence |
|---|---|---|
| CAP-01 | **covered** | `barY`/`barX` take pre-binned rows directly; no auto-binning. Empty bin = a row with `y:0`, not dropped, as long as the category is in the domain — use a **fixed** `scaleBand(['1','2','3','4','5'])` domain, not an inferred one, or a genuinely-empty grade would vanish from the inferred first-seen-order domain (`docs/reference/marks/bar-and-rect.md`, `docs/concepts/scales-and-d3.md` "Factory domains come from marks"). |
| CAP-02 | covered | `barY`'s `color`/`fill` accept a per-datum `VisualChannel` (`bar-and-rect.md`). |
| CAP-03 | **undocumented** | Doc shows `fill: 'url(#id)'` against declared `gradients:` SVG defs, not a repeating hatch pattern; a datum-derived hatch sub-portion is plausible by the same mechanism but not shown (`docs/guides/themes-and-styling.md` "Gradients and clipping"). |
| CAP-04 | covered | App-level guard (render `NoShipRecords` before mount); library imposes nothing here. |
| CAP-05 | covered, with a gotcha | Standard DOM composition (`aria-hidden` wrapper). **Gotcha**: the React adapter defaults `tabIndex=0` even on a non-interactive chart; wrapping a focusable, non-`aria-hidden`-respecting child inside an `aria-hidden` ancestor is itself an a11y violation unless `keyboard: false` is also passed (`docs/framework/react/adapter.md`). Not called out in T-15's intent — F7. |
| CAP-06 | covered | `axis: { label }` per named scale renders without a legend (`docs/reference/chart-spec.md`). |
| CAP-07 | **covered, conditionally** | `lineY`'s `x` scale must be `d3-scale`'s `scaleUtc`/`scaleTime`. The docs explicitly warn the compact `scaleBand`/`scalePoint` "treat Date values as equally spaced categories" — exactly the fabricated-cadence failure DESIGN forbids (`docs/concepts/scales-and-d3.md`). `d3-scale`/`@types/d3-scale` are **not** in T-04's dependency list — F5. |
| CAP-08 | covered (not merely "acceptable gap") | Named scales support a second y-axis (`side: 'left'\|'right'`) via `xScale`/`yScale` bindings — see `docs/reference/scales-guides-and-color.md` "Named scales and multiple axes". A third axis stacks outward on one side; only two true sides exist. This is a real feature, not the alpha gap DESIGN assumed — see A2d. |
| CAP-09 | **covered, explicitly** | "Rows whose required positional value is null, undefined, invalid, or nonfinite create gaps instead of connecting across missing data… A null row flushes the current segment; later valid rows begin a new segment" (`docs/reference/marks/line-and-area.md`). This is CAP-09 verbatim. |
| CAP-10 | covered | Same app-level guard as CAP-04. |
| CAP-11 | **partial** | `strokeDasharray` is a per-series `VisualChannel` on `lineY` — dash pattern is covered outright. Marker **shape** variety (circle/square/triangle) has no built-in beyond circular `dot`/hexagonal `hexagon`; square/triangle need a custom mark via the documented `createMark<Datum,X,Y>()` extension point (`docs/reference/marks/dot-and-hexagon.md`, package README "Type inference"). Real, supported, but not zero-cost — F6. |
| CAP-12 | covered | Point identity is app-supplied (`key` channel + the adjacent table); library-neutral. |
| CAP-13 | covered | React adapter is responsive (`aspectRatio`/`initialWidth`), and "There is no placeholder-only server mode" — client-only render emits the same complete SVG with no SSR requirement (`docs/framework/react/adapter.md`). |

## A2b — is D-08's trigger evaluable

- **CAP-01**: yes, crisply. Concrete observation: render 5 rows with a **fixed** 5-category domain
  including one `count: 0` row; count rendered bars == 5, not 4.
- **CAP-05**: yes, but it is not discriminating — it is app composition, not a library capability, so
  it will pass for *any* charting library and can never itself trigger the fallback. Its presence in
  D-08's four-item trigger list does no work.
- **CAP-07**: **not crisply evaluable as a smoke check.** The failure mode is silent, not a crash: a
  naive probe that renders irregularly-spaced dates through the *default* compact scale (`scalePoint`)
  will render a plausible-looking, non-throwing line — while fabricating equal spacing, exactly what
  CAP-07 forbids. "Does it render" is not "is it met." Concrete observation that decides it: confirm the
  probe used `scaleUtc`/`scaleTime` (not `scaleBand`/`scalePoint`) for x, and that two points 1 day apart
  and two points 60 days apart produce pixel gaps whose ratio approximates 1:60.
- **CAP-11**: borderline. Dash pattern is crisp (option exists or it doesn't). Marker *shape* is not —
  a builder can always satisfy it by authoring a custom mark, so "unmet" depends on whether custom-mark
  authoring counts as "the library can" or "the library cannot" (DESIGN's own fallback text, "draw
  markers as an overlaid series," is itself already a workaround). This is the one most likely to be
  judged met when it is really an aspiration.

**Verdict**: two of the four trigger capabilities (CAP-01, CAP-09-adjacent CAP-07-if-done-right) are
genuinely checkable; CAP-05 is inert; CAP-07 and CAP-11 both have a real risk of being marked "met" by
a probe that does the easy thing rather than the correct thing.

## A2c — can T-15 answer the question, and is it too late

**Too late, and structurally broken, not just late.**

1. **Ordering defeats the trigger's purpose.** T-15 `depends_on: [T-14]` → `depends_on: [T-13]` →
   `depends_on: [T-01, T-04, T-05]` (plan.yaml:538-621). By the time the probe runs, the client shell
   (routing, theme, API layer — T-13) and every tile/panel/table/gap-state component (T-14) are already
   built and merged. D-08's own `because` says "a named trigger keeps the swap a decision rather than a
   rescue" (plan.yaml:68) — a trigger evaluated after 2 of 3 frontend tasks are sunk is exactly the
   rescue-under-pressure dynamic that sentence disclaims.
2. **Concretely, what's sunk if the trigger fires**: T-13's shell is library-independent (charting is
   isolated to T-15's `charts.tsx`), so it survives a swap. T-14 is *not* fully independent: its own
   intent text says the KPI panel shows "the chart" (plan.yaml:599, "PANELS: … the chart, its caveats
   and its feature table"), but `charts.tsx` is T-15's file and doesn't exist while T-14 runs — so either
   T-14's panel ships without a real chart (contradicting its own intent) or T-14 silently grows scope
   into T-15's domain. Either way this is a genuine plan defect, distinct from the two already-known
   issues: **F3**.
3. **For the probe to change course before client work is spent**, T-15 needs to split: a probe-only
   task depending on nothing past `[T-04]` (client toolchain in place, no UI needed to test the alpha
   API against synthetic data), gating D-08's swap decision *before* T-13 starts, and a separate
   chart-render task keeping today's `depends_on: [T-14]` for wiring into panels.
4. **Is the STOP instruction workable?** No. T-15's `verify:` is unconditional:
   `npm … run build && python3 -c … CAP-probe.md …` (plan.yaml:626-627). If the trigger fires, T-15's
   own instruction is "STOP, do not write the charts" (plan.yaml:635) — but `npm run build` will fail
   the moment any earlier-built file (most plausibly T-14's `panels.tsx`, per point 2) imports the
   `charts.tsx` module that this exact branch forbids writing. **A task that correctly follows its own
   STOP instruction cannot pass its own verify command.** This is **F2**, blocking.

## A2d — CAP-08 / Q6: one triple-y-axis plot vs. three stacked single-series plots

**Recommendation: three stacked single-series plots sharing one x-axis. Decide this now; do not leave
Q6 open for pm.**

- **Feasibility is not the tiebreaker** — CAP-08 table above found triple-axis genuinely supported via
  named scales (`side: 'left'|'right'`, third axis stacks outward). This is a real choice, not a forced
  fallback.
- **Readability**: cycle-time (days), touchpoint count, and a 1–5 grade share are three incommensurable
  units. A shared-canvas multi-axis chart is a well-known misread risk regardless of library quality;
  three separate single-metric plots need no axis-reading gymnastics.
- **C-3's own hue-parity admission is decisive**: `series-1` vs `series-2` differ by only 1.51:1 (light)
  /1.21:1 (dark) — hue barely distinguishes them (DESIGN.md:210-211). On one shared plot, a reader must
  hold dash + marker + end-label + hue together to separate three overlapping lines. On three stacked
  single-series plots, no series-to-series disambiguation is needed at all — dash/marker/label become
  redundant reinforcement instead of the only thing standing between two 1.2:1-contrast lines.
- **Alpha risk**: single-y-axis composition (the `facet`/three-`defineChart` pattern) is the library's
  most heavily documented, most idiomatic path (`docs/guides/faceting-and-composition.md`). Named
  multi-axis is a real but narrower-surface feature; less exposure to Alpha's "minor releases may
  contain breaking changes" contract (`docs/stability.md`) is a second, independent reason to prefer it.

## Findings

- **F1** — severity: `blocking`. D-08's fallback ("React Charts") is dead: npm `react-charts`'s
  `latest` tag is `2.0.0-beta.7` (published 2020-05-29, peer `react ^16.6.3`), `next` is `2.1.0`
  (2021-07-07, peer `react >=16`), `beta` is `3.0.0-beta.57` — last published 2023-11-02, ~3 years
  stale as of this review. Astryx requires a React ≥19 peer (DESIGN.md:20). The named safety net cannot
  actually be installed alongside the rest of this client without a peer conflict. Consequence: if the
  trigger fires, there is no working fallback as written — D-08 needs a real second option before the
  four-CAP trigger means anything. Alternative: retarget the fallback to `@tanstack/charts`'s own
  non-grammar surface is not an option (same package); a genuinely independent library needs its own
  plan Decision per DESIGN.md:173-174. remedy_cost: amend (D-08's `choice`/`because` are text scalars).
- **F2** — severity: `blocking`. T-15's `verify:` is unconditional and will fail on the exact branch its
  own STOP instruction requires (see A2c point 4). remedy_cost: amend (`verify:` is a text scalar).
- **F3** — severity: `blocking`. T-15 depends on T-14 depends on T-13, so the probe that is supposed to
  gate D-08's swap decision runs after the client shell and every tile/panel/table/gap-state component
  are built, and T-14's own intent already leans on a chart component (`charts.tsx`) that does not exist
  until T-15. remedy_cost: `task-set-change` (needs a new, earlier probe-only task and a `depends_on`
  edit on the render-only remainder of T-15 — `depends_on` is a list field).
- **F4** — severity: `advisory`. T-04 pins `@tanstack/react-charts`, which its own README calls "a
  compatibility package [that] remains supported for existing applications" — current guidance for a
  *new* application is `@tanstack/charts` + the `@tanstack/charts/react` adapter subpath of the same
  package (npm registry, `@tanstack/react-charts@0.16.0` description field). Not the same package as the
  BRIEF's "React Charts" fallback (different repo: `TanStack/charts` vs `react-tools/react-charts`), but
  worth naming plainly since the question was asked directly: **no**, primary and fallback are not the
  same package under two names; they are two unrelated packages that happen to share "charts" in the
  name, and the primary's own dependency the plan pins (`@tanstack/react-charts`) is itself a legacy
  compatibility shim over the real primary (`@tanstack/charts`). remedy_cost: amend (T-04's `intent:`
  names the dependency in prose, not in `files:`).
- **F5** — severity: `advisory`. CAP-07 needs `d3-scale`/`@types/d3-scale` as a direct dependency
  (docs/concepts/scales-and-d3.md); T-04 does not pin either, and T-15's intent never mentions them.
  Without it, a builder most likely reaches for the compact `scalePoint`, satisfies a naive "does it
  render" probe, and ships a fabricated-cadence axis CAP-07 explicitly forbids. remedy_cost: amend
  (T-04 and T-15 `intent:` are text).
- **F6** — severity: `advisory`. CAP-11 marker-shape variety (square/triangle) has no built-in support;
  it needs a custom mark via `createMark`. Real and documented, but T-15's intent scopes it as if it
  were a prop toggle. remedy_cost: amend (T-15 `intent:`).
- **F7** — severity: `advisory`. CAP-05's `aria-hidden` chart needs `keyboard: false` passed explicitly,
  or the default `tabIndex=0` leaves focusable content inside an `aria-hidden` ancestor — an a11y bug
  T-15's intent doesn't call out. remedy_cost: amend (T-15 `intent:`).
