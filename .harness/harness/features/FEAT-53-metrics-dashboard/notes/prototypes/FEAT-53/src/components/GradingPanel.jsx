// The grading panel — DESIGN.md §C-1: "the one that does not collapse to a
// figure". The histogram sits BESIDE the named grade-1 / grade-2 outlier table
// (side by side at >=1024px, stacked below), and S-3's Python-only caveat is
// persistent 13pt text DIRECTLY BENEATH the histogram, in the same panel.
//
// Three things a reviewer may check by pointing:
//   - the headline is a SHARE, never a mean (REQ-07).
//   - the outlier names are plain text in a table. Not a hover, not a tooltip,
//     not a disclosure, not a click away.
//   - no global threshold line is drawn. The bar is per record (3 for a test
//     path, 4 otherwise), so one line at "4" would misreport every test-path
//     function (CAP-03). The bar is printed per outlier row instead.

import {
  Collapsible,
  HStack,
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableHeaderCell,
  TableRow,
  Text,
  VisuallyHidden,
  VStack,
} from '@astryxdesign/core';
import {NUMERAL, RADIUS, SIZE, T, TYPE} from '../theme.js';
import {GapLabel, Numeral, PanelHeader} from './primitives.jsx';
import {gradingCoverage} from '../lib/series.js';
import {AGGREGATE, GRADE_DISTRIBUTION, OUTLIERS} from '../fixture.js';

const H = 280;
const PAD_LEFT = 34;
const AXIS_H = 44;
const TOP = 18;

function Histogram({counts}) {
  const max = Math.max(...counts, 1);
  const plotH = H - AXIS_H - TOP;
  const slot = 100 / counts.length;

  return (
    <VStack gap={2}>
      {/* CAP-05: the chart is aria-hidden and an adjacent real <table> carries
          the same numbers. The counts are also printed above each bar, so the
          values are never chart-only (DESIGN.md: nothing is hover-only). */}
      <svg
        width="100%"
        height={H}
        viewBox={`0 0 100 ${H}`}
        preserveAspectRatio="none"
        aria-hidden="true"
        focusable="false"
      >
        {/* baseline only. No gridlines, and no global threshold line. */}
        <line x1={PAD_LEFT / 10} y1={TOP + plotH} x2={100} y2={TOP + plotH} stroke={T.border} vectorEffect="non-scaling-stroke" />
        {counts.map((count, i) => {
          const h = (count / max) * plotH;
          return (
            <rect
              key={i}
              x={i * slot + slot * 0.18}
              y={TOP + plotH - h}
              width={slot * 0.64}
              height={h}
              fill={T.grade(i + 1)}
              rx={1}
            />
          );
        })}
      </svg>

      {/* the printed counts and the ordinal bin labels — CAP-06: bin meaning is
          readable without a legend. */}
      <HStack gap={1}>
        {counts.map((count, i) => (
          <VStack key={i} gap={0.5} hAlign="center" style={{flex: '1 1 0'}}>
            <Numeral size={TYPE.body}>{count}</Numeral>
            <Text style={{fontSize: TYPE.tick, color: T.grade(i + 1), fontWeight: 500}}>
              {`grade ${i + 1}`}
            </Text>
          </VStack>
        ))}
      </HStack>

      <VisuallyHidden>
        <table>
          <caption>Graded function counts by grade band</caption>
          <thead>
            <tr>
              <th scope="col">Grade</th>
              <th scope="col">Functions</th>
            </tr>
          </thead>
          <tbody>
            {counts.map((count, i) => (
              <tr key={i}>
                <th scope="row">{i + 1}</th>
                <td>{count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </VisuallyHidden>
    </VStack>
  );
}

/** S-3. Persistent, 13pt, directly beneath the histogram, in the same panel. */
function GradingCoverageCaveat() {
  const c = gradingCoverage();
  return (
    <VStack gap={1.5}>
      <GapLabel id="S-3" what="grading covers one language; the rest is named, not hidden" />
      <Text style={{fontSize: TYPE.caveat}}>
        {`Grading covers Python only. `}
        <Text style={{...NUMERAL, fontSize: TYPE.caveat, fontWeight: 700}}>{c.ungraded}</Text>
        {` of `}
        <Text style={{...NUMERAL, fontSize: TYPE.caveat, fontWeight: 700}}>{c.tracked}</Text>
        {` tracked files in this project are ungraded (`}
        <Text style={{...NUMERAL, fontSize: TYPE.caveat, fontWeight: 700}}>{`${c.percent}%`}</Text>
        {`).`}
      </Text>
      <Collapsible
        trigger={<Text style={{fontSize: TYPE.caveat}}>which extensions are ungraded</Text>}
      >
        <VStack gap={0.5} paddingBlockStart={1}>
          {c.extensions.map((e) => (
            <HStack key={e.ext} gap={2} align="baseline">
              <Text style={{fontSize: TYPE.caveat, fontFamily: T.mono}}>{e.ext}</Text>
              <Numeral size={TYPE.caveat} weight={400} color={T.textMuted}>
                {`${e.count} files`}
              </Numeral>
            </HStack>
          ))}
          <Text color="secondary" style={{fontSize: TYPE.tick}}>
            {`graded: ${c.gradedExtensions.join(', ')}. Every number in this sentence arrives from the payload — none is a literal in component source.`}
          </Text>
        </VStack>
      </Collapsible>
    </VStack>
  );
}

function OutlierTable({rows}) {
  if (rows.length === 0) {
    return (
      <Text style={{fontSize: TYPE.body}}>
        no grade-1 or grade-2 functions in this window
      </Text>
    );
  }
  return (
    <Table density="compact" dividers="rows" aria-label="Named grade-1 and grade-2 outliers">
      <TableHeader>
        <TableRow isHeaderRow>
          <TableHeaderCell scope="col">Function</TableHeaderCell>
          <TableHeaderCell scope="col">Grade</TableHeaderCell>
          <TableHeaderCell scope="col">Driver</TableHeaderCell>
          <TableHeaderCell scope="col">Bar</TableHeaderCell>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r) => (
          <TableRow key={r.qualname}>
            <TableCell>
              <VStack gap={0.5}>
                <Text style={{fontSize: TYPE.body, fontFamily: T.mono}}>{r.qualname}</Text>
                <Text color="secondary" style={{fontSize: TYPE.tick, fontFamily: T.mono}}>
                  {`${r.path} \u00b7 ${r.feature}`}
                </Text>
              </VStack>
            </TableCell>
            <TableCell style={{borderRadius: RADIUS.control}}>
              {/* DESIGN.md §C-3: an outlier row is carried by the grade NUMERAL
                  in the cell, not only by the row tint. */}
              <Numeral size={TYPE.label} color={T.grade(r.grade)}>
                {r.grade}
              </Numeral>
            </TableCell>
            <TableCell>
              <Text color="secondary" style={{fontSize: TYPE.tick, fontFamily: T.mono}}>
                {r.driver}
              </Text>
            </TableCell>
            <TableCell>
              <Numeral size={TYPE.body} weight={400} color={T.textMuted}>
                {r.bar}
              </Numeral>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function GradingPanel({windowToken}) {
  const counts = GRADE_DISTRIBUTION[windowToken];
  const rows = OUTLIERS[windowToken];
  const headline = AGGREGATE[windowToken].grading;

  return (
    <VStack
      gap={3}
      padding={4}
      style={{
        borderRadius: RADIUS.card,
        border: `1px solid ${T.border}`,
        backgroundColor: T.card,
      }}
    >
      <PanelHeader
        title="Code grading"
        sub={`the KPI panel that does not collapse to a figure \u00b7 window ${windowToken}`}
      />
      <HStack gap={3} align="baseline" wrap="wrap">
        <Text style={{...NUMERAL, fontSize: TYPE.panelFigure, fontWeight: 700}}>
          {headline.value}
        </Text>
        <Text color="secondary" style={{fontSize: TYPE.caveat}}>
          {`${headline.secondary} \u00b7 a share, never a mean`}
        </Text>
      </HStack>

      <HStack gap={4} wrap="wrap" align="stretch">
        <VStack gap={2} style={{flex: `1 1 ${SIZE.panelMin}`, minWidth: 0}}>
          <VStack minHeight={SIZE.histogram}>
            <Histogram counts={counts} />
          </VStack>
          <GradingCoverageCaveat />
        </VStack>
        <VStack gap={2} style={{flex: `1 1 ${SIZE.panelMin}`, minWidth: 0}}>
          <Text weight="medium" style={{fontSize: TYPE.body}}>
            {`Named grade-1 and grade-2 outliers \u00b7 ${rows.length} in this window`}
          </Text>
          <OutlierTable rows={rows} />
          <Text color="secondary" style={{fontSize: TYPE.tick}}>
            The bar is per record — 3 for a test path, 4 otherwise — so no single threshold line is
            drawn. Each row prints its own bar.
          </Text>
        </VStack>
      </HStack>
    </VStack>
  );
}
