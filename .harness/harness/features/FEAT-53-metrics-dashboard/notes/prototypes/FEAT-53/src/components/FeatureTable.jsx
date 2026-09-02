// The rows behind an aggregate: one row per feature, all six KPIs as columns,
// sorted by the KPI drilled from (DESIGN.md §C-1's /features route).
//
// This is where S-2 and S-4 live at cell scale:
//   S-2  a pre-capability row carries its trend cell on a 45 degree hatch fill
//        with an em-dash and "no trend - shipped before metrics", and the count
//        line beneath the table is persistent, not a disclosure.
//   S-4  an unavailable cell and a genuine zero sit in the same column and
//        differ in glyph, typography, fill and badge.

import {
  Badge,
  HStack,
  Link,
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableHeaderCell,
  TableRow,
  Text,
  VStack,
} from '@astryxdesign/core';
import {Link as RouterLink} from '@tanstack/react-router';
import {NUMERAL, RADIUS, T, TYPE, hatchFill} from '../theme.js';
import {GapLabel, ValueCellBody} from './primitives.jsx';
import {preCapability} from '../lib/series.js';
import {KPIS, featuresInWindow} from '../fixture.js';

/**
 * An unavailable measurement cannot be ranked against a measured one, so it
 * sorts last rather than sorting as zero — the table-level form of the same
 * rule S-4 states for a value slot.
 */
function sortRows(features, sortKey) {
  const numeric = (cell) => {
    if (cell.state === 'unavailable') return null;
    const n = typeof cell.value === 'number' ? cell.value : parseFloat(String(cell.value));
    return Number.isNaN(n) ? null : n;
  };
  return [...features].sort((a, b) => {
    const x = numeric(a[sortKey]);
    const y = numeric(b[sortKey]);
    if (x === null && y === null) return 0;
    if (x === null) return 1;
    if (y === null) return -1;
    return y - x;
  });
}

/** S-2's trend cell. Hatched, em-dash, and the reason spelled out. */
function TrendCell({feature}) {
  if (feature.preCapability) {
    return (
      <VStack gap={0.5} padding={1} style={{...hatchFill, borderRadius: RADIUS.control}}>
        <HStack gap={1} align="center">
          <Text
            style={{...NUMERAL, fontSize: TYPE.body, fontWeight: 400, color: T.unavailable}}
          >
            {'\u2014'}
          </Text>
          <Badge variant="neutral" label="S-2" />
        </HStack>
        <Text style={{fontSize: TYPE.tick, color: T.unavailable}}>
          no trend — shipped before metrics
        </Text>
      </VStack>
    );
  }
  const n = feature.trend ? feature.trend.length : 0;
  return (
    <VStack gap={0.5}>
      <Text style={{...NUMERAL, fontSize: TYPE.body, fontWeight: 700}}>{n}</Text>
      <Text color="secondary" style={{fontSize: TYPE.tick}}>
        ship records plotted
      </Text>
    </VStack>
  );
}

export function FeatureTable({windowToken, sortKey}) {
  const features = featuresInWindow(windowToken);
  const rows = sortRows(features, sortKey ?? 'throughput');
  const pre = preCapability(windowToken);

  return (
    <VStack gap={2}>
      <Table
        density="compact"
        dividers="rows"
        hasHover
        aria-label={`Features in window ${windowToken}, sorted by ${sortKey ?? 'throughput'}`}
      >
        <TableHeader>
          <TableRow isHeaderRow>
            <TableHeaderCell scope="col">Feature</TableHeaderCell>
            {KPIS.map((kpi) => (
              <TableHeaderCell key={kpi.key} scope="col">
                <VStack gap={0.5}>
                  <Text weight="medium" style={{fontSize: TYPE.tick}}>
                    {kpi.title}
                  </Text>
                  {kpi.key === (sortKey ?? 'throughput') ? (
                    <Badge variant="info" label="sorted by" />
                  ) : null}
                </VStack>
              </TableHeaderCell>
            ))}
            <TableHeaderCell scope="col">Trend</TableHeaderCell>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((f) => (
            <TableRow key={f.id}>
              <TableCell>
                <VStack gap={0.5}>
                  <Link as={RouterLink} to="/features/$featureId" params={{featureId: f.id}} search={{window: windowToken}}>
                    {f.name}
                  </Link>
                  <Text color="secondary" style={{fontSize: TYPE.tick, fontFamily: T.mono}}>
                    {`${f.id} \u00b7 shipped ${f.shippedAt}`}
                  </Text>
                </VStack>
              </TableCell>
              {KPIS.map((kpi) => (
                <TableCell key={kpi.key}>
                  <ValueCellBody cell={f[kpi.key]} />
                </TableCell>
              ))}
              <TableCell>
                <TrendCell feature={f} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {pre.count > 0 ? (
        <VStack gap={1}>
          <GapLabel id="S-2" what="counted in a persistent line, never only in a disclosure" />
          <Text style={{fontSize: TYPE.caveat}}>{pre.line}</Text>
        </VStack>
      ) : null}
      <Text color="secondary" style={{fontSize: TYPE.tick}}>
        An unavailable measurement sorts last rather than sorting as zero: it is not a smaller
        number, it is not a number.
      </Text>
    </VStack>
  );
}
