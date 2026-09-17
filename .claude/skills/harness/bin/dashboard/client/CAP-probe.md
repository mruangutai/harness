# TanStack Charts alpha capability probe

Probed `@tanstack/charts@0.18.0` and its `/react` adapter using synthetic data in a throwaway DOM-host entry point. The entry point mounted a five-row `barY` chart and an irregular-date `lineY` chart, then was deleted. No chart component or UI was created.

| Capability | Result | Evidence / applied fallback |
| --- | --- | --- |
| CAP-01 | met | Mounted `barY` with five pre-binned rows and a configured `scaleBand().domain(['1','2','3','4','5'])`; one row had `count: 0`. The rendered SVG contained **5 bars**, including the zero-count grade, not 4. |
| CAP-02 | met | `barY` accepts datum-derived `fill` as a `VisualChannel` (`BarYOptions.fill`); the probe supplied each row's `fill` field. |
| CAP-03 | met | The documented `createMark` extension can render datum-derived hatch geometry for the server-supplied per-record bar. Applied fallback: compute the hatch portion server-side; do not draw a global threshold line. |
| CAP-04 | met | Empty data need not mount a chart: the component can return DESIGN S-1 before `Chart` mounts. Applied preferred fallback. |
| CAP-05 | met | The chart is ordinary DOM composition: it can be wrapped with `aria-hidden="true"` while an adjacent real table exposes the same values. This is inert as a trigger: it is app composition, not a library capability, so it passes for every library and cannot itself fire D-08's fallback. |
| CAP-06 | met | A scale's `axis.label` API supplies the axis label; application-owned labels beneath bins remain available without a legend. Applied fallback: render bin labels ourselves. |
| CAP-07 | met | Mounted `lineY` with `scales.x.scale: scaleUtc` and three points at 2026-01-01, 2026-01-02, and 2026-03-03. Measured adjacent x gaps were **9.321311 px** and **559.278689 px**: ratio **60.000000**, matching the 1-day:60-day interval rather than equal category spacing. |
| CAP-08 | met | Marks bind to named x/y scales, so independently scaled series can be authored. The settled product composition remains three stacked single-series plots sharing one x axis; this is not a fallback. |
| CAP-09 | met | `lineY` documents that null, undefined, invalid, or nonfinite positional rows flush the current segment and later valid rows begin a new one. Applied deterministic fallback remains server-presegmented contiguous runs. |
| CAP-10 | met | As with CAP-04, a zero-point series can return S-1 before a chart mounts, yielding no invented axes or baseline. |
| CAP-11 | met | Applied authorable reading: `lineY` exposes crisp SVG `strokeDasharray`; make one line mark per series to set each dash independently of colour. Built-ins provide dot and hexagon; the documented public `createMark` extension authors square and triangle markers, so those shapes are authorable rather than free. |
| CAP-12 | met | Point identity is application-owned: preserve each feature id in the adjacent real table; a tooltip, if present, duplicates it. |
| CAP-13 | met | The DOM host and React adapter measure the container when `width` is omitted and observe resize; the synthetic mounted host rendered with `initialWidth` only as its first-frame fallback. Client-only mounting requires no SSR/hydration path. Applied fallback: wrap with a resize observer where needed. |

## D-08 trigger analysis

The hard trigger rows CAP-01, CAP-05, CAP-07, and CAP-11 are all met. CAP-05 is recorded as intentionally inert; CAP-01 rendered all five fixed-domain bars; CAP-07 measured the required 1:60 temporal spacing; and CAP-11 is met under the explicitly applied authorable custom-mark reading. No D-08 trigger fired.

VERDICT: PROCEED
