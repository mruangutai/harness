// The landing 3x2 KPI tile grid, in DESIGN.md §C-1's FIXED order:
//   1 Throughput  2 Rework  3 Blocking human touchpoints
//   4 Escaped defects  5 Code grading  6 Usage by agent / model tier
//
// A tile shows a 40pt headline figure, a one-line denominator, and — for the
// three trend KPIs (1, 3, 5) — an 8-point sparkline or its S-1/S-2 treatment.
// Nothing else, with one contract-mandated exception: escaped defects carries
// its sourcing rule as persistent inline text (REQ-05 / SC-13), because the
// sourcing rule travels with the number it justifies.
//
// The grid is three across at >=1024px, two below and one below 640, done with
// a wrapping flow over a tokenised tile basis rather than a media query.

import {ClickableCard, HStack, Text, VStack} from '@astryxdesign/core';
import {useNavigate} from '@tanstack/react-router';
import {RADIUS, SIZE, T, TYPE, dashedOutline} from '../theme.js';
import {GapLabel, ValueSlot} from './primitives.jsx';
import {SERIES, sparkValues} from '../lib/series.js';
import {Sparkline} from './Sparkline.jsx';
import {AGGREGATE, ESCAPED_SOURCING_RULE, KPIS} from '../fixture.js';

// which trend series backs which tile — tiles 1, 3 and 5 only
const TREND_SERIES = {
  throughput: SERIES[0],
  touchpoints: SERIES[1],
  grading: SERIES[2],
};

function TileTrend({kpiKey, windowToken}) {
  const series = TREND_SERIES[kpiKey];
  if (!series) return null;
  const values = sparkValues(windowToken, series.key);

  // S-1 at tile scale: no ship records in the window, so no sparkline is
  // mounted. Same rule as the full region — replaced, not annotated.
  if (values.length === 0) {
    return (
      <VStack gap={1} padding={2} style={dashedOutline}>
        <GapLabel id="S-1" what={`no ship records in ${windowToken}`} />
        <Text color="secondary" style={{fontSize: TYPE.tick}}>
          no sparkline drawn — no axes, no baseline, nothing plotted
        </Text>
      </VStack>
    );
  }
  return <Sparkline values={values} series={series} />;
}

export function KpiTiles({windowToken}) {
  const navigate = useNavigate();
  const aggregate = AGGREGATE[windowToken];

  return (
    <HStack gap={3} wrap="wrap" align="stretch">
      {KPIS.map((kpi) => (
        <VStack key={kpi.key} style={{flex: `1 1 ${SIZE.tileMin}`, minWidth: 0}}>
          <ClickableCard
            label={`${kpi.title} — see the feature rows behind this figure`}
            padding={3}
            href={`/features?window=${windowToken}&sort=${kpi.key}`}
            onClick={(event) => {
              event.preventDefault();
              navigate({to: '/features', search: {window: windowToken, sort: kpi.key}});
            }}
            style={{borderRadius: RADIUS.card, border: `1px solid ${T.border}`, height: '100%'}}
          >
            <VStack gap={2}>
              <VStack gap={0.5}>
                <Text weight="medium" style={{fontSize: TYPE.label}}>
                  {kpi.title}
                </Text>
                <Text color="secondary" style={{fontSize: TYPE.tick}}>
                  {kpi.unit}
                </Text>
              </VStack>
              <ValueSlot cell={aggregate[kpi.key]} size={TYPE.tileFigure} />
              {kpi.key === 'escaped' ? (
                <Text color="secondary" style={{fontSize: TYPE.caveat}}>
                  {ESCAPED_SOURCING_RULE}
                </Text>
              ) : null}
              <TileTrend kpiKey={kpi.key} windowToken={windowToken} />
            </VStack>
          </ClickableCard>
        </VStack>
      ))}
    </HStack>
  );
}
