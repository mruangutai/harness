// Derivations over the fixture. No rendering, no tokens, no live data.
//
// The one rule this module exists to enforce: a missing measurement is NEVER
// interpolated and NEVER coerced to zero (DESIGN.md C-2 CAP-09, REQ-11). It
// becomes a BREAK in the series — `runs()` below is the whole implementation of
// that, and every chart in the prototype draws one polyline per run.

import {FEATURES, WINDOWS, featuresInWindow, FILE_MIX} from '../fixture.js';

// DESIGN.md §C-3: which series a line is must be carried by dash pattern and
// marker shape and a direct end-of-line label — never by hue alone, because
// series-1 and series-2 differ from each other by only 1.51:1 in light.
export const SERIES = [
  {
    key: 'cycleDays',
    label: 'Cycle time',
    unit: 'days',
    token: 1,
    dash: null, // solid
    marker: 'circle',
    format: (v) => `${v.toFixed(1)} d`,
  },
  {
    key: 'touchpoints',
    label: 'Blocking touchpoints',
    unit: 'count per ship',
    token: 2,
    dash: '6 2',
    marker: 'square',
    format: (v) => `${v}`,
  },
  {
    key: 'gradeShare',
    label: 'At or above bar',
    unit: 'share of graded functions',
    token: 3,
    dash: '2 2',
    marker: 'triangle',
    format: (v) => `${Math.round(v * 100)}%`,
  },
];

/**
 * Every ship record in a window, oldest first. A feature with `trend: null`
 * (pre-capability, S-2) contributes NOTHING — it is excluded from the line's
 * path rather than plotted at zero.
 */
export function windowPoints(w) {
  const points = [];
  for (const f of featuresInWindow(w)) {
    if (!f.trend) continue;
    for (const p of f.trend) points.push({...p, featureId: f.id, featureName: f.name});
  }
  return points.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
}

/**
 * Split an ordered value list into contiguous runs of present values. This is
 * CAP-09: two runs means the line is drawn twice with a gap between, not once
 * across the gap.
 */
export function runs(values) {
  const out = [];
  let current = null;
  values.forEach((value, index) => {
    if (value === null || value === undefined) {
      current = null;
      return;
    }
    if (!current) {
      current = [];
      out.push(current);
    }
    current.push({index, value});
  });
  return out;
}

/** Number of points a series is missing — the honest gap count, for a caption. */
export function missingCount(values) {
  return values.filter((v) => v === null || v === undefined).length;
}

export function seriesValues(points, key) {
  return points.map((p) => (p[key] === null || p[key] === undefined ? null : p[key]));
}

export function extent(values) {
  const present = values.filter((v) => v !== null && v !== undefined);
  if (present.length === 0) return null;
  const min = Math.min(...present);
  const max = Math.max(...present);
  return min === max ? {min: min === 0 ? 0 : min * 0.9, max: max === 0 ? 1 : max * 1.1} : {min, max};
}

/** S-1's predicate: the window holds no ship records at all. */
export function hasNoShipRecords(w) {
  return WINDOWS[w].shipRecords === 0;
}

/** S-2's predicate and its count line, both from the same source. */
export function preCapability(w) {
  const inWindow = featuresInWindow(w);
  const pre = inWindow.filter((f) => f.preCapability);
  return {
    features: pre,
    count: pre.length,
    total: inWindow.length,
    // DESIGN.md C-4 S-2: a persistent line, not a disclosure.
    line: `${pre.length} of ${inWindow.length} features in this window shipped before metrics and have no trend line`,
  };
}

/**
 * S-3's numbers. DESIGN.md C-4 S-3 is explicit that N, M and P arrive only
 * from the payload — nothing here is a literal in component source, and no
 * digit of the host repository's own file mix appears anywhere in this
 * prototype (SC-06).
 */
export function gradingCoverage() {
  const ungraded = FILE_MIX.ungraded.reduce((n, e) => n + e.count, 0);
  const tracked = FILE_MIX.tracked;
  return {
    ungraded,
    tracked,
    percent: Math.round((ungraded / tracked) * 100),
    extensions: FILE_MIX.ungraded,
    gradedExtensions: FILE_MIX.gradedExtensions,
  };
}

/** The last n ship records of a window, for the tile sparklines. */
export function sparkValues(w, key, n = 8) {
  const values = seriesValues(windowPoints(w), key);
  return values.slice(-n);
}

export function allFeatures() {
  return FEATURES;
}
