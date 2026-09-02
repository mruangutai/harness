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
  aggregate.includes('no commit carries a resolvable step-id') && !aggregate.toLowerCase().includes('>no data<'),
);
check('S-4 genuine zero keeps its denominator', aggregate.includes('0 of 12 features needed one'));

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

console.log('');
if (failures.length > 0) {
  console.error(`${failures.length} check(s) failed: ${failures.join(', ')}`);
  process.exit(1);
}
console.log(`all checks passed (${aggregate.length} bytes of landing HTML)`);
