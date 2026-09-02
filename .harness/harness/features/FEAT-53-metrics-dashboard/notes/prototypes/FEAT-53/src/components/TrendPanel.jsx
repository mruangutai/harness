// The trend region, and with it S-1 and S-2 — the two states DESIGN.md says a
// reviewer must be able to tell apart on screen without reading the payload.
//
//   S-1  no ship records at all  -> the region is REPLACED. No axes, no
//                                   gridlines, no zero baseline, no <svg> at
//                                   all: the component returns before one is
//                                   mounted (CAP-04 / CAP-10's preferred
//                                   implementation).
//   S-2  a pre-capability feature among features that DO have data -> axes ARE
//        drawn, and the pre-capability features are excluded from the line's
//        path. The line breaks; it never descends to zero and is never
//        interpolated across (CAP-09).
//
// Three stacked plots share one x axis. That is CAP-08's stated fallback for
// "three series in one plot with per-series y-axis assignment" — hours, a count
// and a 1-5 grade share do not share a scale — and DESIGN.md records it as an
// acceptable outcome rather than a redesign.

import {Collapsible, HStack, Text, VStack} from '@astryxdesign/core';
import {NUMERAL, RADIUS, SIZE, T, TYPE, dashedOutline} from '../theme.js';
import {GapLabel, Numeral, PanelHeader} from './primitives.jsx';
import {SERIES, extent, missingCount, preCapability, runs, seriesValues} from '../lib/series.js';
import {useContainerWidth} from '../lib/useContainerWidth.js';
import {WINDOWS} from '../fixture.js';

const PLOT_H = 74;
const PLOT_GAP = 12;
const AXIS_H = 34;
const PAD_LEFT = 46;
const LABEL_W = 148;
const TOP = 10;

const MARKER = {
  circle: (x, y, fill, key) => <circle key={key} cx={x} cy={y} r={2.6} fill={fill} />,
  square: (x, y, fill, key) => (
    <rect key={key} x={x - 2.4} y={y - 2.4} width={4.8} height={4.8} fill={fill} />
  ),
  triangle: (x, y, fill, key) => (
    <polygon key={key} points={`${x},${y - 3} ${x + 2.8},${y + 2.4} ${x - 2.8},${y + 2.4}`} fill={fill} />
  ),
};

/**
 * S-1. The whole region, replaced. Note what is NOT here: no <svg>, no axis,
 * no baseline. That absence is the thing a reviewer checks.
 */
export function NoShipRecords({windowToken}) {
  return (
    <VStack gap={3} padding={4} style={dashedOutline}>
      <GapLabel id="S-1" what={`no ship records in this window (${windowToken})`} />
      <Text as="h3" weight="semibold" style={{fontSize: TYPE.stateHead}}>
        No ship records yet
      </Text>
      <VStack gap={1}>
        <Text color="secondary" style={{fontSize: TYPE.caveat}}>
          The trend reads <Text style={{fontFamily: T.mono}}>.harness/metrics/trend.jsonl</Text>,
          which holds no lines for this window.
        </Text>
        <Text color="secondary" style={{fontSize: TYPE.caveat}}>
          The trend begins at the first ship after this capability landed. History is never
          backfilled, so an empty window here is a fact about the project, not a failure to load.
        </Text>
        <Text color="secondary" style={{fontSize: TYPE.caveat}}>
          No axes, no gridlines and no zero baseline are drawn: there is nothing measured to draw
          them around. The five non-trend KPIs above are unaffected.
        </Text>
      </VStack>
    </VStack>
  );
}

export function AxisAndSeries({points, width}) {
  const plotW = Math.max(width - PAD_LEFT - LABEL_W, 220);
  const times = points.map((p) => new Date(p.date).getTime());
  const t0 = Math.min(...times);
  const t1 = Math.max(...times);
  // CAP-07: a temporal x axis with irregularly spaced points. Ships are
  // irregular; positioning by index would fabricate a cadence.
  const x = (i) => PAD_LEFT + (t1 === t0 ? plotW / 2 : ((times[i] - t0) / (t1 - t0)) * plotW);
  const height = TOP + SERIES.length * (PLOT_H + PLOT_GAP) + AXIS_H;

  const tickIndexes = [...new Set([0, Math.floor((points.length - 1) / 2), points.length - 1])];

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={`Three trend series over ${points.length} ship records. The same values are in the feature table below.`}
    >
      {SERIES.map((series, row) => {
        const values = seriesValues(points, series.key);
        const span = extent(values);
        const top = TOP + row * (PLOT_H + PLOT_GAP);
        const stroke = T.series(series.token);
        const y = (v) =>
          span ? top + PLOT_H - ((v - span.min) / (span.max - span.min || 1)) * PLOT_H : top;
        const segments = span ? runs(values) : [];
        const last = segments.at(-1)?.at(-1);

        return (
          <g key={series.key}>
            {/* y axis for this series only — CAP-08's per-series scale */}
            <line x1={PAD_LEFT} y1={top} x2={PAD_LEFT} y2={top + PLOT_H} stroke={T.borderStrong} />
            <line
              x1={PAD_LEFT}
              y1={top + PLOT_H}
              x2={PAD_LEFT + plotW}
              y2={top + PLOT_H}
              stroke={T.border}
            />
            {span ? (
              <>
                <text
                  x={PAD_LEFT - 6}
                  y={top + 4}
                  textAnchor="end"
                  fill={T.textMuted}
                  style={{fontSize: TYPE.tick, fontFamily: T.mono}}
                >
                  {series.format(span.max)}
                </text>
                <text
                  x={PAD_LEFT - 6}
                  y={top + PLOT_H}
                  textAnchor="end"
                  fill={T.textMuted}
                  style={{fontSize: TYPE.tick, fontFamily: T.mono}}
                >
                  {series.format(span.min)}
                </text>
              </>
            ) : null}
            {segments.map((run, i) => (
              <g key={i}>
                {run.length > 1 ? (
                  <polyline
                    points={run.map((p) => `${x(p.index)},${y(p.value)}`).join(' ')}
                    fill="none"
                    stroke={stroke}
                    strokeWidth={2}
                    strokeDasharray={series.dash ?? undefined}
                  />
                ) : null}
                {run.map((p) => MARKER[series.marker](x(p.index), y(p.value), stroke, p.index))}
              </g>
            ))}
            {/* DESIGN.md §C-3: a direct end-of-line label, so series identity
                never rests on hue. A legend is a convenience, never the only
                mapping. */}
            {last ? (
              <text
                x={PAD_LEFT + plotW + 8}
                y={y(last.value) + 4}
                fill={stroke}
                style={{fontSize: TYPE.tick, fontWeight: 500}}
              >
                {`${series.label} \u00b7 ${series.format(last.value)}`}
              </text>
            ) : null}
          </g>
        );
      })}
      {/* one shared x axis */}
      {tickIndexes.map((i) => (
        <text
          key={i}
          x={x(i)}
          y={TOP + SERIES.length * (PLOT_H + PLOT_GAP) + 16}
          textAnchor="middle"
          fill={T.textMuted}
          style={{fontSize: TYPE.tick, fontFamily: T.mono}}
        >
          {points[i].date}
        </text>
      ))}
    </svg>
  );
}

/**
 * The trend region for one window token. Renders S-1 or the axes-and-series
 * chart, never both, and never a chart over a partial payload.
 */
export function TrendPanel({windowToken, points, isSelected}) {
  const [ref, width] = useContainerWidth();
  const pre = preCapability(windowToken);
  const noRecords = WINDOWS[windowToken].shipRecords === 0 || points.length === 0;

  return (
    <VStack
      gap={3}
      padding={3}
      ref={ref}
      style={{
        borderRadius: RADIUS.card,
        border: `1px solid ${isSelected ? T.borderStrong : T.border}`,
        backgroundColor: T.card,
      }}
    >
      <PanelHeader
        title={`${WINDOWS[windowToken].label} \u00b7 ${windowToken}`}
        sub={
          noRecords
            ? 'trend region replaced'
            : `${WINDOWS[windowToken].shipRecords} ship records \u00b7 ${points.length} plotted points \u00b7 three series, own y scale each`
        }
        badge={
          noRecords ? null : pre.count > 0 ? (
            <GapLabel id="S-2" what="pre-capability features among features that do have trend data" />
          ) : null
        }
      />

      {noRecords ? (
        <NoShipRecords windowToken={windowToken} />
      ) : (
        <>
          <VStack minHeight={SIZE.timeseries}>
            <AxisAndSeries points={points} width={width} />
          </VStack>
          <VStack gap={1}>
            {SERIES.map((series) => {
              const gaps = missingCount(seriesValues(points, series.key));
              if (gaps === 0) return null;
              return (
                <Text key={series.key} style={{fontSize: TYPE.caveat, color: T.unavailable}}>
                  {`${series.label}: ${gaps} of ${points.length} ship records carry no value. `}
                  <Text style={{...NUMERAL, fontSize: TYPE.caveat, fontWeight: 400, color: T.unavailable}}>
                    {'\u2014'}
                  </Text>
                  {' the line breaks across each one; it is not interpolated and not drawn at zero.'}
                </Text>
              );
            })}
            {pre.count > 0 ? (
              <VStack gap={1}>
                <Text style={{fontSize: TYPE.caveat}}>{pre.line}</Text>
                <Collapsible
                  trigger={
                    <Text style={{fontSize: TYPE.caveat}}>
                      which features shipped before metrics
                    </Text>
                  }
                >
                  <VStack gap={0.5} paddingBlockStart={1}>
                    {pre.features.map((f) => (
                      <HStack key={f.id} gap={2} align="baseline">
                        <Numeral size={TYPE.caveat} weight={400} color={T.textMuted}>
                          {f.id}
                        </Numeral>
                        <Text color="secondary" style={{fontSize: TYPE.caveat}}>
                          {`${f.name} \u00b7 shipped ${f.shippedAt} \u00b7 no trend \u2014 shipped before metrics`}
                        </Text>
                      </HStack>
                    ))}
                  </VStack>
                </Collapsible>
              </VStack>
            ) : null}
          </VStack>
        </>
      )}
    </VStack>
  );
}
