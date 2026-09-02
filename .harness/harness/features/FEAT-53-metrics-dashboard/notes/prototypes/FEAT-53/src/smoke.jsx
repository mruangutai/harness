// A smoke harness, not a test suite. It renders all three routes to HTML in
// node and asserts the handful of things a reviewer would otherwise have to
// take on trust — most importantly that S-1 mounts NO <svg> while S-2 mounts
// axes and more polylines than it has series, which is what "the line breaks"
// looks like in the output.
//
//   npm run smoke
//
// This is how the prototype in this directory was verified without a browser.
// It is not a substitute for looking at it: run `npm run dev` for that.

import {renderToString} from 'react-dom/server';
import {createMemoryHistory} from '@tanstack/react-router';
import {RouterProvider} from '@tanstack/react-router';
import {makeRouter} from './router.jsx';
import {AGGREGATE, touchpointCoverage} from './fixture.js';

async function render(path) {
  const router = makeRouter({history: createMemoryHistory({initialEntries: [path]})});
  await router.load();
  return renderToString(<RouterProvider router={router} />);
}

const failures = [];
function check(name, condition, detail = '') {
  const status = condition ? 'ok  ' : 'FAIL';
  if (!condition) failures.push(name);
  console.log(`${status} ${name}${detail ? ` — ${detail}` : ''}`);
}

const count = (haystack, needle) => haystack.split(needle).length - 1;

const aggregate = await render('/?window=all');
const rows = await render('/features?window=all&sort=grading');
const detail = await render('/features/FIX-02?window=all');
const preCapDetail = await render('/features/FIX-03?window=all');
const thirtyDay = await render('/?window=30d');

console.log('--- T-05 verify literals (the plan greps for these) ---');
for (const token of ['S-1', 'S-2', 'S-3', 'S-4', '30d', '90d']) {
  check(`literal ${token} present on the landing route`, aggregate.includes(token));
}

console.log('--- gap states ---');
check(
  'S-1 mounts no chart at all: the 30d panel contains no <svg>',
  (() => {
    // isolate the 30d trend panel: it is the panel whose header names 30d and
    // whose body is the replacement card.
    const start = thirtyDay.indexOf('No ship records yet');
    const end = thirtyDay.indexOf('Last 90 days', start);
    const region = thirtyDay.slice(start, end === -1 ? undefined : end);
    return start !== -1 && !region.includes('<svg');
  })(),
);
check('S-1 names the trend file', aggregate.includes('.harness/metrics/trend.jsonl'));
check('S-1 states history is never backfilled', aggregate.includes('never backfilled'));

check('S-2 draws axes: the landing route mounts <svg> with <line>', aggregate.includes('<svg') && aggregate.includes('<line'));
check(
  'S-2 breaks the line: more polylines than series',
  count(aggregate, '<polyline') > 3,
  `${count(aggregate, '<polyline')} polylines for 3 series`,
);
check('S-2 count line is persistent text', aggregate.includes('shipped before metrics and have no trend line'));
check('S-2 count reads 2 of 8', aggregate.includes('2 of 8 features in this window'));
check('S-2 hatched trend cells in the table', rows.includes('no trend') && rows.includes('repeating-linear-gradient'));

check('S-3 caveat is Python-only and persistent', aggregate.includes('Grading covers Python only'));
const s3Sentence = (() => {
  const i = aggregate.indexOf('Grading covers Python only');
  // strip tags so the assertion reads the SENTENCE a user sees, not the markup
  return aggregate
    .slice(i, i + 900)
    .replace(/<[^>]*>/g, '')
    .replace(/\s+/g, ' ')
    .slice(0, 120);
})();
check(
  'S-3 states N of M tracked files and a percent',
  /Grading covers Python only\. 7 of 48 tracked files in this project are ungraded \(15%\)\./.test(
    s3Sentence,
  ),
  s3Sentence,
);
check('S-3 discloses ungraded extensions', aggregate.includes('.rb') && aggregate.includes('.lua'));

check('S-4 renders an unavailable badge', aggregate.includes('unavailable'));
check('S-4 renders the em-dash glyph', aggregate.includes('\u2014'));
check('S-4 hatch fill is a repeating-linear-gradient over a surface token', aggregate.includes('repeating-linear-gradient'));
check(
  'S-4 reasons are specific, never "no data"',
  rows.includes('no commit carries a resolvable step-id') && !rows.toLowerCase().includes('>no data<'),
);

// D-21 — the three-term KPI 3, and the pair it rests on. Both features below
// have NO touchpoints.jsonl: only the epoch separates a measured zero from a
// feature that was never tracked.
check(
  'KPI 3 tile carries THREE terms, not two',
  aggregate.includes('6 features tracked'),
);
check(
  'KPI 3 names the tracked-zero count and the not-tracked count separately',
  aggregate.includes('1 at a tracked zero') && aggregate.includes('2 not tracked'),
);
check(
  'KPI 3 unit label scopes the mean to tracked features',
  aggregate.includes('per-feature mean, tracked features only'),
);
check(
  'KPI 3 mean excludes not-tracked features from its denominator',
  AGGREGATE.all.touchpoints.value === 2.8 &&
    touchpointCoverage('all').tracked.length === 6 &&
    touchpointCoverage('all').notTracked.length === 2,
  `mean ${AGGREGATE.all.touchpoints.value} over ${touchpointCoverage('all').tracked.length} tracked`,
);
check(
  'the pair panel states the two cells share one input',
  aggregate.includes('neither feature has a touchpoints.jsonl'),
);
check(
  'a tracked zero carries its provenance, not a bare 0',
  aggregate.includes('tracked from 2026-05-01, no touchpoints.jsonl written'),
);
check(
  'a not-tracked feature carries D-21 branch 3 verbatim, never a 0',
  aggregate.includes('predates touchpoint instrumentation in this project') &&
    aggregate.includes('touchpoints were never tracked for it'),
);
check(
  'both states sit in one column on the rows route',
  rows.includes('predates touchpoint instrumentation in this project') &&
    rows.includes('tracked from 2026-05-01, no touchpoints.jsonl written'),
);

console.log('--- the drill, three routes ---');
check('aggregate route renders six tiles', count(aggregate, 'see the feature rows behind this figure') === 6);
check('rows route renders the eight fixture features', count(rows, 'shipped 2026') === 8);
check('feature route renders one feature', detail.includes('Porcelain Spout'));
check('a pre-capability feature is S-2 on its own page, not S-1', preCapDetail.includes('S-2') && !preCapDetail.includes('No ship records yet'));
check('window tokens are the control values', aggregate.includes('>30d<') && aggregate.includes('>90d<') && aggregate.includes('>all<'));
check('theme toggle offers system, light and dark', aggregate.includes('>system<') && aggregate.includes('>light<') && aggregate.includes('>dark<'));

console.log('--- no live data ---');
for (const forbidden of ['fetch(', 'node:fs', 'child_process']) {
  check(`no ${forbidden} in rendered output`, !aggregate.includes(forbidden));
}

// KPI 3 is the one figure whose wording a reader has to weigh rather than
// merely locate, so the smoke PRINTS it as rendered — the sentences below are
// the ones on screen, tags stripped, not a paraphrase of them.
console.log('--- KPI 3 as rendered ---');
// Tags are stripped BEFORE the search, so a needle can never land inside an
// attribute and a slice can never run off into markup. The tile title also
// appears in the card's aria-label, so each needle below is text the surface
// prints rather than a title.
const asText = (html) =>
  html
    .replace(/<[^>]*>/g, ' ')
    .replace(/&#x27;/g, "'")
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ');
const aggregateText = asText(aggregate);
const rowsText = asText(rows);
const sentence = (text, needle, len) => {
  const i = text.indexOf(needle);
  return i === -1 ? `MISSING: ${needle}` : text.slice(i, i + len).trim();
};
console.log(`tile  : ${sentence(aggregateText, 'per-feature mean, tracked features only', 140)}`);
console.log(`pairL : ${sentence(aggregateText, 'A tracked zero — a measurement', 380)}`);
console.log(`pairR : ${sentence(aggregateText, 'Not tracked — no measurement exists', 400)}`);
console.log(`rows  : ${sentence(rowsText, 'Blocking human touchpoints are tracked', 300)}`);

console.log('');
if (failures.length > 0) {
  console.error(`${failures.length} check(s) failed: ${failures.join(', ')}`);
  process.exit(1);
}
console.log(`all checks passed (${aggregate.length} bytes of landing HTML)`);
