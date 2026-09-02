// ============================================================================
//  SYNTHETIC FIXTURE — HAND-AUTHORED, NOT A MEASUREMENT OF ANY REPOSITORY.
//  Every number below is invented. The project is a fictional "Teapot Foundry"
//  and its features are named after teapot parts precisely so that nobody can
//  mistake this for Harness's own data. There is no live data access anywhere
//  in this prototype: no fetch, no fs, no git, no code grader.
//
//  Deliberately NOT modelled here: this repository's own file mix. DESIGN.md
//  records that a literal of it in shipped source fails SC-06, and a prototype
//  that models the wrong habit is the wrong reference.
// ============================================================================

export const PROJECT = {
  label: 'Teapot Foundry',
  banner: 'SYNTHETIC FIXTURE — invented numbers, fictional project, no live data',
};

// S-3's input. Computed-at-view-time in the product; a fixture field here.
// Graded languages, and everything tracked that is therefore ungraded.
export const FILE_MIX = {
  gradedExtensions: ['.py'],
  graded: 41,
  tracked: 48,
  ungraded: [
    {ext: '.rb', count: 5},
    {ext: '.lua', count: 2},
  ],
};

const ok = (value, secondary) => ({state: 'ok', value, secondary});
const zero = (secondary) => ({state: 'ok', value: 0, secondary});
const unavailable = (reason) => ({state: 'unavailable', reason});

// D-21's instrumentation epoch. In the product this is the single RFC3339 instant
// on line 1 of .harness/metrics/instrumented_at, written once by touchpoints.py
// record() on its first call and never rewritten; no agent authors it and no
// route can reach it. Here it is a fixture constant, and it is the ONLY thing
// that separates a tracked feature from an untracked one.
export const TOUCHPOINT_EPOCH = '2026-05-01T00:00:00Z';
export const TOUCHPOINT_EPOCH_DATE = '2026-05-01';

// D-21 branch 3's reason, verbatim except for the dash glyph. A feature whose
// own start instant is before the epoch has NO touchpoint measurement — the
// absence of its touchpoints.jsonl says nothing at all.
const NOT_TRACKED =
  'this feature predates touchpoint instrumentation in this project — touchpoints were never tracked for it';

// D-21 branch 1's reason, for a window in which no feature is tracked at all.
const NO_EPOCH =
  'touchpoints were not tracked in this project — no .harness/metrics/instrumented_at epoch exists, so no count here is a measurement';

// D-21 branch 4: a post-epoch feature with no touchpoints.jsonl. The absent
// file IS the measurement — a tracked run in which nothing blocked — so this
// cell is a zero, and it carries where the tracking came from.
const trackedZero = () =>
  zero(`blocking human touchpoints · tracked from ${TOUCHPOINT_EPOCH_DATE}, no touchpoints.jsonl written`);

// A trend point may be missing entirely — CAP-09: the line breaks, it is never
// interpolated and never coerced to zero. `null` for a metric means exactly that.
const pt = (date, cycleDays, touchpoints, gradeShare) => ({
  date,
  cycleDays,
  touchpoints,
  gradeShare,
});

export const FEATURES = [
  {
    id: 'FIX-01',
    name: 'Copper Kettle',
    shippedAt: '2026-08-24',
    startedAt: '2026-06-02', // post-epoch → touchpoints are tracked
    preCapability: false,
    throughput: ok(3.1, '7 runs · 412 lines changed'),
    rework: ok('4 / 12', 'cycles used of cycles allowed'),
    touchpoints: ok(2, 'blocking human touchpoints'),
    escaped: zero('0 of 1 shipped change in window'),
    grading: ok('81%', '17 of 21 graded functions at or above bar'),
    usage: ok('6 sonnet / 1 opus', '2 commits unattributed'),
    trend: [
      pt('2026-06-11', 5.4, 4, 0.68),
      pt('2026-07-02', 4.1, 3, 0.71),
      pt('2026-08-24', 3.1, 2, 0.81),
    ],
  },
  {
    id: 'FIX-02',
    name: 'Porcelain Spout',
    shippedAt: '2026-08-19',
    startedAt: '2026-06-20', // post-epoch → touchpoints are tracked
    preCapability: false,
    throughput: ok(6.8, '11 runs · 1,204 lines changed'),
    rework: ok('9 / 12', 'cycles used of cycles allowed'),
    touchpoints: ok(5, 'blocking human touchpoints'),
    escaped: ok(2, '2 of 3 shipped changes in window'),
    grading: ok('62%', '13 of 21 graded functions at or above bar'),
    usage: ok('9 sonnet / 4 opus', '6 commits unattributed'),
    trend: [
      pt('2026-06-30', 9.2, 7, 0.55),
      // No ship on the July cadence — the point is absent, not zero.
      pt('2026-08-19', 6.8, 5, 0.62),
    ],
  },
  {
    id: 'FIX-03',
    name: 'Cast Iron Lid',
    shippedAt: '2026-03-02',
    startedAt: '2026-02-10', // PRE-epoch → touchpoints were never tracked (D-21 branch 3)
    preCapability: true, // S-2 — shipped before the metrics capability landed
    throughput: unavailable('no ship record for this feature'),
    rework: ok('7 / 12', 'cycles used of cycles allowed'),
    touchpoints: unavailable(NOT_TRACKED),
    escaped: zero('0 of 2 shipped changes in window'),
    grading: ok('70%', '14 of 20 graded functions at or above bar'),
    usage: unavailable('no commit carries a resolvable step-id'),
    trend: null,
  },
  {
    id: 'FIX-04',
    name: 'Glass Infuser',
    shippedAt: '2026-08-05',
    startedAt: '2026-07-01', // post-epoch → touchpoints are tracked
    preCapability: false,
    throughput: ok(4.4, '5 runs · 288 lines changed'),
    rework: ok('3 / 12', 'cycles used of cycles allowed'),
    touchpoints: ok(1, 'blocking human touchpoints'),
    // S-4, left half of the pair: unavailable WITH A REASON.
    escaped: unavailable('no commit carries a resolvable step-id'),
    grading: ok('88%', '22 of 25 graded functions at or above bar'),
    usage: ok('4 sonnet / 1 opus', '0 commits unattributed'),
    trend: [
      pt('2026-07-14', 5.0, 2, 0.84),
      pt('2026-08-05', 4.4, 1, 0.88),
    ],
  },
  {
    id: 'FIX-05',
    name: 'Bamboo Handle',
    shippedAt: '2026-08-28',
    startedAt: '2026-07-26', // post-epoch → touchpoints are tracked
    preCapability: false,
    throughput: ok(2.2, '3 runs · 96 lines changed'),
    rework: ok('2 / 12', 'cycles used of cycles allowed'),
    // D-21 branch 4, and the whole point of the pair: this feature has NO
    // touchpoints.jsonl either, exactly like FIX-03 — but it started after the
    // epoch, so the absence is a measured zero rather than a hole.
    touchpoints: trackedZero(),
    escaped: zero('0 of 1 shipped change in window'),
    grading: ok('92%', '11 of 12 graded functions at or above bar'),
    usage: ok('3 sonnet / 0 opus', '1 commit unattributed'),
    trend: [
      pt('2026-08-01', 2.9, 0, 0.9),
      pt('2026-08-28', 2.2, 0, 0.92),
    ],
  },
  {
    id: 'FIX-06',
    name: 'Stoneware Base',
    shippedAt: '2026-07-21',
    startedAt: '2026-05-12', // post-epoch → touchpoints are tracked
    preCapability: false,
    throughput: ok(8.9, '14 runs · 2,617 lines changed'),
    rework: ok('12 / 12', 'cycles used of cycles allowed'),
    touchpoints: ok(6, 'blocking human touchpoints'),
    escaped: ok(1, '1 of 4 shipped changes in window'),
    grading: unavailable('this feature changed no Python — nothing to grade'),
    usage: ok('12 sonnet / 3 opus', '9 commits unattributed'),
    trend: [
      pt('2026-05-19', 11.4, 8, null), // grade share absent for this ship
      pt('2026-06-23', 10.1, 7, null),
      pt('2026-07-21', 8.9, 6, null),
    ],
  },
  {
    id: 'FIX-07',
    name: 'Tin Whistle',
    shippedAt: '2026-01-14',
    startedAt: '2025-12-08', // PRE-epoch → touchpoints were never tracked (D-21 branch 3)
    preCapability: true, // second S-2 row, so the count reads "2 of 8"
    throughput: unavailable('no ship record for this feature'),
    rework: ok('5 / 12', 'cycles used of cycles allowed'),
    touchpoints: unavailable(NOT_TRACKED),
    escaped: zero('0 of 1 shipped change in window'),
    grading: ok('76%', '16 of 21 graded functions at or above bar'),
    usage: unavailable('no commit carries a resolvable step-id'),
    trend: null,
  },
  {
    id: 'FIX-08',
    name: 'Silver Filigree',
    shippedAt: '2026-08-30',
    startedAt: '2026-06-30', // post-epoch → touchpoints are tracked
    preCapability: false,
    throughput: ok(3.7, '6 runs · 501 lines changed'),
    rework: ok('5 / 12', 'cycles used of cycles allowed'),
    touchpoints: ok(3, 'blocking human touchpoints'),
    escaped: zero('0 of 2 shipped changes in window'),
    grading: ok('79%', '15 of 19 graded functions at or above bar'),
    usage: ok('7 sonnet / 2 opus', '4 commits unattributed'),
    trend: [
      pt('2026-07-08', 4.9, 4, 0.72),
      pt('2026-08-02', 4.2, 3, 0.75),
      pt('2026-08-30', 3.7, 3, 0.79),
    ],
  },
];

// Ship records per window. `30d` deliberately has NONE: that is S-1, the
// trend region replaced outright while the five non-trend KPIs render on.
export const WINDOWS = {
  '30d': {label: 'Last 30 days', shipRecords: 0, featureIds: ['FIX-05', 'FIX-08']},
  '90d': {
    label: 'Last 90 days',
    shipRecords: 14,
    featureIds: ['FIX-01', 'FIX-02', 'FIX-04', 'FIX-05', 'FIX-06', 'FIX-08'],
  },
  all: {
    label: 'All time',
    shipRecords: 21,
    featureIds: FEATURES.map((f) => f.id),
  },
};

export const WINDOW_TOKENS = ['30d', '90d', 'all'];

// D-21's split for a window, computed from the rows rather than hand-authored,
// so the tile's three terms can never drift from the cells behind them.
export function touchpointCoverage(w) {
  const inWindow = featuresInWindow(w);
  const tracked = inWindow.filter((f) => f.touchpoints.state === 'ok');
  const notTracked = inWindow.filter((f) => f.touchpoints.state === 'unavailable');
  const atZero = tracked.filter((f) => f.touchpoints.value === 0);
  const total = tracked.reduce((n, f) => n + f.touchpoints.value, 0);
  return {
    tracked,
    notTracked,
    atZero,
    // A not-tracked feature is NEVER in the denominator.
    mean: tracked.length === 0 ? null : Math.round((total / tracked.length) * 10) / 10,
  };
}

// KPI 3's tile cell. THREE terms, never two: the mean over tracked features
// only, the count at a tracked zero, and the count not tracked. When no
// feature in the window is tracked the headline is itself S-4's em-dash with
// its reason, never 0 (DESIGN C-1 tile 3, plan.yaml D-21).
function touchpointAggregate(w) {
  const c = touchpointCoverage(w);
  if (c.mean === null) return unavailable(NO_EPOCH);
  return ok(
    c.mean,
    `${c.tracked.length} features tracked · ${c.atZero.length} at a tracked zero · ${c.notTracked.length} not tracked`,
  );
}

// Aggregate figures the landing tiles show. Hand-authored per window so the
// tiles stay coherent with the rows behind them — except KPI 3, which is
// derived from those rows so its three terms cannot drift from them.
export const AGGREGATE = {
  '30d': {
    throughput: ok('2.9 d', 'median BRIEF-approval to ship · 9 runs · 597 lines'),
    rework: ok('7 / 24', 'cycles used of cycles allowed, 2 features'),
    touchpoints: touchpointAggregate('30d'),
    escaped: zero('0 of 3 shipped changes in window'),
    grading: ok('84%', '26 of 31 at or above bar · 3 outliers named'),
    usage: ok('10 sonnet / 2 opus', '5 commits unattributed'),
  },
  '90d': {
    throughput: ok('4.6 d', 'median BRIEF-approval to ship · 46 runs · 5,118 lines'),
    rework: ok('35 / 72', 'cycles used of cycles allowed, 6 features'),
    touchpoints: touchpointAggregate('90d'),
    escaped: ok(3, '3 of 14 shipped changes in window'),
    grading: ok('78%', '77 of 98 at or above bar · 9 outliers named'),
    usage: ok('41 sonnet / 11 opus', '22 commits unattributed'),
  },
  all: {
    throughput: ok('4.4 d', 'median BRIEF-approval to ship · 58 runs · 5,825 lines'),
    rework: ok('47 / 96', 'cycles used of cycles allowed, 8 features'),
    touchpoints: touchpointAggregate('all'),
    escaped: ok(3, '3 of 21 shipped changes in window'),
    grading: ok('74%', '98 of 132 at or above bar · 17 outliers named'),
    usage: ok('61 sonnet / 18 opus', '24 commits unattributed'),
  },
};

// Pre-binned counts over an ordinal five-category axis (CAP-01). The server
// bins; nothing here asks a chart library to compute a bin.
export const GRADE_DISTRIBUTION = {
  '30d': [1, 2, 2, 14, 12],
  '90d': [4, 7, 10, 44, 33],
  all: [6, 11, 17, 65, 33],
};

// Named grade-1 / grade-2 outliers. REQ-07 asks for a named list, not a
// reachable one — these render as a persistent table, never behind a hover.
// `bar` is per record (3 for a test path, 4 otherwise) — CAP-03, no global line.
export const OUTLIERS = {
  '30d': [
    {qualname: 'teapot.brew.orchestrate_steep', path: 'src/teapot/brew.py:212', grade: 1, driver: 'cognitive 41', bar: 4, feature: 'FIX-08'},
    {qualname: 'teapot.kiln.fire_schedule', path: 'src/teapot/kiln.py:88', grade: 2, driver: 'cyclomatic 17', bar: 4, feature: 'FIX-05'},
    {qualname: 'tests.test_glaze.assert_all_finishes', path: 'tests/test_glaze.py:301', grade: 2, driver: 'ABC 29.4', bar: 3, feature: 'FIX-08'},
  ],
  '90d': [
    {qualname: 'teapot.brew.orchestrate_steep', path: 'src/teapot/brew.py:212', grade: 1, driver: 'cognitive 41', bar: 4, feature: 'FIX-08'},
    {qualname: 'teapot.spout.reroute_flow', path: 'src/teapot/spout.py:145', grade: 1, driver: 'cognitive 38', bar: 4, feature: 'FIX-02'},
    {qualname: 'teapot.lid.seat_gasket', path: 'src/teapot/lid.py:64', grade: 1, driver: 'cyclomatic 22', bar: 4, feature: 'FIX-02'},
    {qualname: 'teapot.kiln.fire_schedule', path: 'src/teapot/kiln.py:88', grade: 2, driver: 'cyclomatic 17', bar: 4, feature: 'FIX-05'},
    {qualname: 'teapot.infuser.mesh_pack', path: 'src/teapot/infuser.py:19', grade: 2, driver: 'cognitive 24', bar: 4, feature: 'FIX-04'},
    {qualname: 'tests.test_glaze.assert_all_finishes', path: 'tests/test_glaze.py:301', grade: 2, driver: 'ABC 29.4', bar: 3, feature: 'FIX-08'},
  ],
  all: [
    {qualname: 'teapot.brew.orchestrate_steep', path: 'src/teapot/brew.py:212', grade: 1, driver: 'cognitive 41', bar: 4, feature: 'FIX-08'},
    {qualname: 'teapot.spout.reroute_flow', path: 'src/teapot/spout.py:145', grade: 1, driver: 'cognitive 38', bar: 4, feature: 'FIX-02'},
    {qualname: 'teapot.lid.seat_gasket', path: 'src/teapot/lid.py:64', grade: 1, driver: 'cyclomatic 22', bar: 4, feature: 'FIX-02'},
    {qualname: 'teapot.whistle.tune_pitch', path: 'src/teapot/whistle.py:410', grade: 1, driver: 'ABC 41.2', bar: 4, feature: 'FIX-07'},
    {qualname: 'teapot.kiln.fire_schedule', path: 'src/teapot/kiln.py:88', grade: 2, driver: 'cyclomatic 17', bar: 4, feature: 'FIX-05'},
    {qualname: 'teapot.infuser.mesh_pack', path: 'src/teapot/infuser.py:19', grade: 2, driver: 'cognitive 24', bar: 4, feature: 'FIX-04'},
    {qualname: 'teapot.handle.wrap_cane', path: 'src/teapot/handle.py:57', grade: 2, driver: 'cyclomatic 15', bar: 4, feature: 'FIX-05'},
    {qualname: 'tests.test_glaze.assert_all_finishes', path: 'tests/test_glaze.py:301', grade: 2, driver: 'ABC 29.4', bar: 3, feature: 'FIX-08'},
  ],
};

export const KPIS = [
  {key: 'throughput', title: 'Throughput', unit: 'median days, BRIEF approval to ship', trend: true},
  {key: 'rework', title: 'Rework', unit: 'cycles used of cycles allowed', trend: false},
  {key: 'touchpoints', title: 'Blocking human touchpoints', unit: 'per-feature mean, tracked features only', trend: true},
  {key: 'escaped', title: 'Escaped defects', unit: 'count in window', trend: false},
  {key: 'grading', title: 'Code grading', unit: 'share at or above bar', trend: true},
  {key: 'usage', title: 'Usage by agent / model tier', unit: 'runs by tier', trend: false},
];

// REQ-05 / SC-13: the sourcing rule travels with the number it justifies.
export const ESCAPED_SOURCING_RULE =
  'Sourced: a commit touching a path shipped by a feature, landed after that feature shipped, whose message names a defect.';

export function featureById(id) {
  return FEATURES.find((f) => f.id === id);
}

export function featuresInWindow(w) {
  const ids = WINDOWS[w].featureIds;
  return FEATURES.filter((f) => ids.includes(f.id));
}
