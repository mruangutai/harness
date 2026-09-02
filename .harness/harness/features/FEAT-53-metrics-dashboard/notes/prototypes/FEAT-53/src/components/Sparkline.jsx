// The 8-point tile sparkline (DESIGN.md §C-1: "an 8-point sparkline or its
// S-1/S-2 treatment"). Plain SVG driven by theme tokens — no charting library
// is added to this prototype; probing TanStack Charts' alpha against C-2's
// capability list is build task T-15's job, not the prototype's.

import {HStack, Text, VStack} from '@astryxdesign/core';
import {NUMERAL, T, TYPE} from '../theme.js';
import {extent, missingCount, runs} from '../lib/series.js';

const W = 132;
const H = 30;
const PAD = 3;

const MARKER = {
  circle: (x, y, fill) => <circle cx={x} cy={y} r={2.2} fill={fill} />,
  square: (x, y, fill) => <rect x={x - 2} y={y - 2} width={4} height={4} fill={fill} />,
  triangle: (x, y, fill) => (
    <polygon points={`${x},${y - 2.6} ${x + 2.4},${y + 2} ${x - 2.4},${y + 2}`} fill={fill} />
  ),
};

/**
 * `values` may contain nulls. A null is a MISSING measurement: the line breaks
 * there. It is never interpolated across and never drawn at zero (CAP-09).
 */
export function Sparkline({values, series, caption}) {
  const span = extent(values);
  const stroke = T.series(series.token);
  const gaps = missingCount(values);

  if (!span) {
    // No present values at all — CAP-10 hands the region over rather than
    // drawing an axis-less flat line that would read as a measurement of zero.
    return (
      <Text color="secondary" style={{fontSize: TYPE.tick, color: T.unavailable}}>
        no plottable points in this window
      </Text>
    );
  }

  const stepX = values.length > 1 ? (W - PAD * 2) / (values.length - 1) : 0;
  const x = (i) => PAD + i * stepX;
  const y = (v) => H - PAD - ((v - span.min) / (span.max - span.min || 1)) * (H - PAD * 2);
  const segments = runs(values);

  return (
    <VStack gap={0.5}>
      <svg
        width={W}
        height={H}
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={`${series.label} sparkline, ${values.length - gaps} of ${values.length} ship records plotted`}
      >
        {segments.map((run, i) => (
          <g key={i}>
            {run.length > 1 ? (
              <polyline
                points={run.map((p) => `${x(p.index)},${y(p.value)}`).join(' ')}
                fill="none"
                stroke={stroke}
                strokeWidth={1.5}
                strokeDasharray={series.dash ?? undefined}
              />
            ) : null}
            {run.map((p) => (
              <g key={p.index}>{MARKER[series.marker](x(p.index), y(p.value), stroke)}</g>
            ))}
          </g>
        ))}
      </svg>
      <HStack gap={1} align="baseline" wrap="wrap">
        <Text color="secondary" style={{fontSize: TYPE.tick}}>
          {caption ?? `last ${values.length} ship records`}
        </Text>
        {gaps > 0 ? (
          <Text style={{...NUMERAL, fontSize: TYPE.tick, fontWeight: 400, color: T.unavailable}}>
            {`\u2014 ${gaps} with no value: the line breaks`}
          </Text>
        ) : null}
      </HStack>
    </VStack>
  );
}
