// THE ONLY FILE IN THIS PROTOTYPE THAT MAY CONTAIN A RAW #hex.
// DESIGN.md §Substrate rule 2: "Raw `#hex` appears in exactly one file — the
// `defineTheme` call. `grep` for a hex literal outside that file is a violation,
// and that is the check." Everything else reads var(--...).
//
// One defineTheme call, [light, dark] tuples, no prefers-color-scheme query and
// no isDark ternary anywhere in a component (DESIGN.md §C-3). Light/dark is
// selected by <Theme mode> in main.jsx, which defaults to 'system'.
//
// DELIBERATELY NOT OVERRIDDEN: the four surface anchors (bg, surface, text,
// text-muted). DESIGN.md §Palette: "Where an Astryx theme value differs, Astryx
// wins and the ratios below are re-measured against it rather than the anchor
// being forced." Astryx 0.5.2 ships --color-background-surface as
// light-dark(#FFFFFF, #1F1F22), which differs from DESIGN's #F6F7F9/#161A21
// anchors, so Astryx wins and the nine tokens below were re-measured against
// the real surface. All nine clear 3:1; the eight informational ones clear
// 4.5:1; unavailable-stroke sits at 3.22 light / 3.67 dark — see README
// "Contrast, re-measured".

import {defineTheme} from '@astryxdesign/core';

export const metricsTheme = defineTheme({
  name: 'metrics',
  tokens: {
    // --- the nine feature-semantic colour tokens DESIGN.md §Palette adds.
    // Named --color-metrics-* rather than --color-grade-N so they cannot
    // collide with an Astryx core or domain token name.
    '--color-metrics-grade-1': ['#B3261E', '#FF8A80'],
    '--color-metrics-grade-2': ['#8A5300', '#E0A33A'],
    '--color-metrics-grade-3': ['#5A6472', '#9AA4B2'],
    '--color-metrics-grade-4': ['#1B7A5A', '#4FD1A5'],
    '--color-metrics-grade-5': ['#0B4F6C', '#69C7E8'],
    '--color-metrics-series-1': ['#1B5FCC', '#7FA9FF'],
    '--color-metrics-series-2': ['#0B4F6C', '#69C7E8'],
    '--color-metrics-series-3': ['#8A5300', '#E0A33A'],
    '--color-metrics-unavailable-stroke': ['#8A9099', '#6E7885'],

    // --- DESIGN.md §Type — the scale, as tokens, because rule 2 covers sizes
    // too: "Every colour, size, radius and spacing value in component source
    // comes from a theme token." 12/13/14/16/20/28/40, no in-between sizes.
    '--text-metrics-tick': '12px',
    '--text-metrics-caveat': '13px',
    '--text-metrics-body': '14px',
    '--text-metrics-label': '16px',
    '--text-metrics-state-head': '20px',
    '--text-metrics-panel-figure': '28px',
    '--text-metrics-tile-figure': '40px',

    // --- DESIGN.md §Spacing — 6px controls and table cells, 10px cards and
    // panels, and no other radius. Astryx's own scale has no 6/10 pair.
    '--radius-metrics-control': '6px',
    '--radius-metrics-card': '10px',

    // --- DESIGN.md §Spacing — explicit chart heights, container max width.
    '--size-metrics-chart-histogram': '280px',
    '--size-metrics-chart-timeseries': '320px',
    '--size-metrics-container': '1440px',
    // Half of DESIGN's 1024 breakpoint, less gutters and the panel gap: two
    // panels side by side at >=1024px and stacked below it, expressed as a
    // flex basis so no component needs a media query.
    '--size-metrics-panel-min': '484px',
    // A third of DESIGN's 1024 breakpoint, less gutters and two gaps: three
    // tiles across at >=1024px, two below it, one below 640px.
    '--size-metrics-tile-min': '308px',
  },
});

// Token references. Components import these names; they never see a hex.
export const T = {
  bg: 'var(--color-background-body)',
  surface: 'var(--color-background-surface)',
  card: 'var(--color-background-card)',
  text: 'var(--color-text-primary)',
  textMuted: 'var(--color-text-secondary)',
  border: 'var(--color-border)',
  borderStrong: 'var(--color-border-emphasized)',
  mono: 'var(--font-family-code)',
  grade: (n) => `var(--color-metrics-grade-${n})`,
  series: (n) => `var(--color-metrics-series-${n})`,
  unavailable: 'var(--color-metrics-unavailable-stroke)',
};

// DESIGN.md §Type — every size a component uses resolves through a token.
export const TYPE = {
  tick: 'var(--text-metrics-tick)',
  caveat: 'var(--text-metrics-caveat)',
  body: 'var(--text-metrics-body)',
  label: 'var(--text-metrics-label)',
  stateHead: 'var(--text-metrics-state-head)',
  panelFigure: 'var(--text-metrics-panel-figure)',
  tileFigure: 'var(--text-metrics-tile-figure)',
};

export const RADIUS = {
  control: 'var(--radius-metrics-control)',
  card: 'var(--radius-metrics-card)',
};

export const SIZE = {
  histogram: 'var(--size-metrics-chart-histogram)',
  timeseries: 'var(--size-metrics-chart-timeseries)',
  container: 'var(--size-metrics-container)',
  panelMin: 'var(--size-metrics-panel-min)',
  tileMin: 'var(--size-metrics-tile-min)',
};

// DESIGN.md §Type: "Every numeral in a table, tile or axis is set in mono with
// tabular figures." One object, applied everywhere a numeral is rendered.
export const NUMERAL = {
  fontFamily: T.mono,
  fontVariantNumeric: 'tabular-nums',
};

// DESIGN.md §Substrate rule 4: the hatch is a StyleX repeating-linear-gradient
// over an Astryx surface primitive, both themes' stroke from one token. This is
// a composition, not a second substrate. (The prototype applies it through the
// `style` escape hatch every Astryx primitive accepts rather than
// stylex.create, so no StyleX build step is needed — README "Prototype vs
// product".)
export const hatchFill = {
  backgroundImage: `repeating-linear-gradient(45deg, ${T.unavailable} 0 1px, transparent 1px 6px)`,
  backgroundColor: T.surface,
};

// S-1's card outline: dashed, 1px, unavailable-stroke (DESIGN.md §C-4 S-1).
export const dashedOutline = {
  border: `1px dashed ${T.unavailable}`,
  borderRadius: RADIUS.card,
  backgroundColor: T.surface,
};
