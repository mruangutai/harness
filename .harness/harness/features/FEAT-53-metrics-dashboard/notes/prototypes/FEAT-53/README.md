# FEAT-53 metrics dashboard — high-fidelity prototype

**What this is for:** the four honest-gap states of `DESIGN.md` §C-4 are a visual judgement, and
three of this feature's success criteria are `uat` with no automated runner behind them. This build
exists so that judgement can be made **before** anything ships, on the same substrate the product
will use.

**The payload is a HAND-WRITTEN SYNTHETIC FIXTURE. It is never live data.** Every figure comes from
`src/fixture.js`, the project is a fictional "Teapot Foundry", and its features are named after
teapot parts so nobody can mistake them for a real measurement. There is no `fetch`, no filesystem
read, no `git` and no code grader anywhere in this build. Nothing here measures this repository, and
none of this repository's measured file-mix numbers appears anywhere in this directory (SC-06).

## Run it

```
npm install
npm run dev        # http://localhost:5273
```

Then walk the drill: a tile → the feature rows → one feature. `npm run build` produces `dist/`;
`npm run smoke` renders all three routes in node, asserts the gap-state contract (below), and prints
KPI 3's sentences exactly as they render, so its wording can be read without a browser.

## What to look at, and where

| State | Where on screen | What makes it that state |
|---|---|---|
| **S-1** | the `30d` trend panel, and the `30d` tile sparklines | the region is **replaced**: a dashed card naming `.harness/metrics/trend.jsonl`. **No axes, no gridlines, no zero baseline, no `<svg>` mounted at all.** The five non-trend KPIs render beside it |
| **S-2** | the `90d` and `all` trend panels, and the trend column of the feature table | axes **are** drawn. Pre-capability features are excluded from the line's path, the line **breaks** across a missing value rather than descending to zero, hatched trend cells carry an em-dash and "no trend — shipped before metrics", and "2 of 8 features in this window shipped before metrics" is persistent text |
| **S-3** | directly beneath the histogram, inside the grading panel | persistent 13pt: "Grading covers Python only. 7 of 48 tracked files in this project are ungraded (15%)." with a disclosure naming the ungraded extensions. Never a tooltip, never a page-foot footnote |
| **S-4** | the pair panel on the landing route, KPI 3's tile, and every unavailable cell in the table | a **tracked zero** and a **not-tracked** feature sit side by side on *identical* input: neither Bamboo Handle (`FIX-05`) nor Cast Iron Lid (`FIX-03`) has a `touchpoints.jsonl`, and only the instrumentation epoch — `2026-05-01` here, plan.yaml `D-21` — decides that one absence is a measured zero and the other is not a measurement at all. The two differ in **all four** of glyph (`0` vs `—`), typography (mono 700 `text` vs mono 400 `unavailable-stroke`), fill (normal surface vs 45° hatch) and badge (none vs "unavailable"), and the reason is always specific — the not-tracked cell carries D-21's own sentence, never "no data" |

KPI 3's tile therefore carries **three** terms, never two: the per-feature mean **over tracked
features only**, the count **at a tracked zero**, and the count **not tracked** (`2.8 · 6 features
tracked · 1 at a tracked zero · 2 not tracked` on `all`). A not-tracked feature is never in the
mean's denominator, and the feature-rows table repeats the split as persistent text beneath it.

The window control exposes the literal tokens `30d`, `90d` and `all`; the window and the feature id
live **only** in the URL, so every view is linkable, reloadable and back-button-safe. There is no
modal at any depth and nothing is hover-only.

## The Astryx version — and why DESIGN Q1 is still open

`package.json` pins `@astryxdesign/core` at **`0.5.2`**, and that pin is a **measurement, not a
guess**: the package is real, it was installed here, and its export surface was read from
`node_modules` rather than assumed. Reproduce it with

```
npm view @astryxdesign/core version      # -> 0.5.2 (latest, 2026-09-01)
```

**DESIGN Q1 remains open and this file does not close it.** Q1 asks what the *product* pins, which
is T-04's job: an exact pin plus a committed `package-lock.json`, reported by dev-ops. A prototype's
throwaway dependency set is not that decision. Every other version here is pinned exactly, at what
the registry resolved on 2026-09-01.

`@stylexjs/stylex` `0.19.0` is listed explicitly because Astryx declares it a peer.

## Prototype vs product — three deliberate divergences

1. **The trend section renders one panel per window token**, not one panel for the selected window.
   S-1 and S-2 are told apart by *whether axes are drawn*, and a reviewer cannot compare two states
   they have to navigate between. The product shows one region for the selected window.
2. **Styling uses the `style` escape hatch every Astryx primitive accepts**, not `stylex.create`, so
   no StyleX build step is needed. Values are unchanged — every one is a `var(--…)` token.
3. **Charts are plain SVG driven by theme tokens.** No charting dependency was added: probing
   TanStack Charts' alpha against `DESIGN.md` §C-2's capability list is build task T-15's job. SVG
   *geometry* (viewBox coordinates, plot heights in the local coordinate space) is arithmetic, not a
   design value; every colour, dash, font size and radius still resolves through a token.

## Contrast, re-measured

`DESIGN.md` §Palette measures its nine tokens against named surface anchors, and says that where an
Astryx theme value differs, **Astryx wins and the ratios are re-measured**. Astryx 0.5.2 ships
`--color-background-surface` as `light-dark(#FFFFFF, #1F1F22)`, so the anchors are *not* overridden
here and the ratios were recomputed against the real surface:

- all nine tokens clear 3:1 (the non-text-graphic floor);
- the eight informational tokens clear 4.5:1, so each may be used as a label as well as a fill;
- `unavailable-stroke` sits at 3.22 light / 3.67 dark — deliberately the only one below 4.5:1, so an
  absence stays visible without reading as loud as a value.

`src/theme.js` is the **only** file that may contain a raw `#hex`, and one `defineTheme` call with
`[light, dark]` tuples ships both themes. No component queries `prefers-color-scheme` and none
branches on `isDark`; the theme toggle is an explicit control defaulting to the OS preference.

## How this was verified

- `npx vite build` — 705 modules transformed, so every import `index.html` reaches resolves.
- `npm run smoke` — 31 assertions over the SSR-rendered HTML of all three routes, including the two
  that matter most: the `30d` region contains **no `<svg>`**, and the landing route mounts more
  polylines than it has series (11 for 3), which is what a broken line looks like in the output.
- `npm run dev` — served `/`, `/src/main.jsx` and `/features/FIX-02?window=all` at 200.
- **Not verified: how it looks.** No browser was available in the authoring session. The visual
  judgement this artifact exists for is the reviewer's, and it has not been made yet.

**One caveat for whoever runs T-05's `verify`.** It concatenates *every* file under this directory
and greps for `S-1 … S-4`, `30d` and `90d`. It passes on the committed tree, but it raises
`UnicodeDecodeError` if `node_modules/`, `dist/` or `.smoke/` are present, because those hold binary
files. Run it before `npm install`, or remove those three directories first — they are gitignored
and rebuilt by `npm install` / `npm run build`.

## Files

```
index.html          entry
src/main.jsx        Theme + RouterProvider
src/router.jsx      three routes; all view state in the URL
src/theme.js        ONE defineTheme call — the only file with a raw #hex
src/fixture.js      the synthetic payload
src/lib/            series derivations (the "a gap breaks the line" rule lives here)
src/components/     tiles, trend panels, grading panel, feature table, the S-4 pair
src/routes/         aggregate → rows → feature
src/smoke.jsx       the assertions above
```
