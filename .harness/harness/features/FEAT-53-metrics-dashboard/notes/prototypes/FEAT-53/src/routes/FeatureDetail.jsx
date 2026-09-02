// Route `/features/$featureId?window=<w>` — one feature: its six values, its
// trend lines, and its outlier list. The end of the drill.
//
// One state is decided here rather than reused: a PRE-CAPABILITY feature's own
// page. It is S-2, not S-1, and the difference matters — S-1 is a fact about
// the project (nothing has shipped since the capability existed), S-2 is a fact
// about this feature (it shipped before metrics, while others have data). The
// card below says which, and points at the aggregate chart where the axes are
// drawn and this feature is excluded from the line's path.

import {HStack, Link, Text, VStack} from '@astryxdesign/core';
import {Link as RouterLink} from '@tanstack/react-router';
import {NUMERAL, RADIUS, SIZE, T, TYPE, dashedOutline, hatchFill} from '../theme.js';
import {GapLabel, PanelHeader, ValueSlot} from '../components/primitives.jsx';
import {AxisAndSeries} from '../components/TrendPanel.jsx';
import {Shell} from '../components/Shell.jsx';
import {useContainerWidth} from '../lib/useContainerWidth.js';
import {SERIES, missingCount, seriesValues} from '../lib/series.js';
import {KPIS, OUTLIERS, featureById} from '../fixture.js';

function PreCapabilityTrend({feature, windowToken}) {
  return (
    <VStack gap={2} padding={4} style={{...hatchFill, borderRadius: RADIUS.card}}>
      <GapLabel id="S-2" what="this feature shipped before metrics — not an empty project" />
      <Text as="h3" weight="semibold" style={{fontSize: TYPE.stateHead, color: T.unavailable}}>
        {'\u2014 no trend — shipped before metrics'}
      </Text>
      <Text style={{fontSize: TYPE.caveat}}>
        {`${feature.name} shipped ${feature.shippedAt}, before the metrics capability landed, so no ship record exists to plot. This is a fixed historical fact about this feature, and the label is the same on every such row.`}
      </Text>
      <HStack gap={2} align="baseline" wrap="wrap">
        <Text style={{fontSize: TYPE.caveat}}>Not S-1:</Text>
        <Text color="secondary" style={{fontSize: TYPE.caveat}}>
          other features in this window do have trend data, and the aggregate chart draws axes.
        </Text>
        <Link as={RouterLink} to="/" search={{window: windowToken}}>
          see the aggregate chart, where this feature is excluded from the line
        </Link>
      </HStack>
    </VStack>
  );
}

function FeatureTrend({feature}) {
  const [ref, width] = useContainerWidth();
  const points = feature.trend ?? [];

  if (points.length === 0) {
    return (
      <VStack gap={2} padding={4} style={dashedOutline}>
        <GapLabel id="S-1" what="no ship records for this feature" />
        <Text as="h3" weight="semibold" style={{fontSize: TYPE.stateHead}}>
          No ship records yet
        </Text>
        <Text color="secondary" style={{fontSize: TYPE.caveat}}>
          Nothing is plotted and no axes are drawn. The trend reads{' '}
          <Text style={{fontFamily: T.mono}}>.harness/metrics/trend.jsonl</Text>, and history is
          never backfilled.
        </Text>
      </VStack>
    );
  }

  return (
    <VStack gap={2} ref={ref}>
      <VStack minHeight={SIZE.timeseries}>
        <AxisAndSeries points={points} width={width} />
      </VStack>
      {SERIES.map((series) => {
        const gaps = missingCount(seriesValues(points, series.key));
        if (gaps === 0) return null;
        return (
          <Text key={series.key} style={{fontSize: TYPE.caveat, color: T.unavailable}}>
            {`${series.label}: ${gaps} of ${points.length} ship records carry no value — the line breaks there rather than being drawn through it.`}
          </Text>
        );
      })}
      <Text color="secondary" style={{fontSize: TYPE.tick}}>
        {`${points.length} ship records, irregularly spaced — the x axis is temporal, so the gaps between ships are real spacing rather than an invented cadence.`}
      </Text>
    </VStack>
  );
}

export function FeatureDetail({featureId, windowToken}) {
  const feature = featureById(featureId);

  if (!feature) {
    return (
      <Shell windowToken={windowToken}>
        <VStack gap={2} padding={4} style={dashedOutline}>
          <Text as="h2" weight="semibold" style={{fontSize: TYPE.stateHead}}>
            {`No feature ${featureId} in this fixture`}
          </Text>
          <Link as={RouterLink} to="/features" search={{window: windowToken}}>
            back to the feature rows
          </Link>
        </VStack>
      </Shell>
    );
  }

  const outliers = OUTLIERS[windowToken].filter((o) => o.feature === feature.id);

  return (
    <Shell windowToken={windowToken} feature={feature}>
      <VStack gap={6}>
        <VStack gap={3}>
          <PanelHeader
            title={`${feature.name} — six values`}
            sub={`${feature.id} · shipped ${feature.shippedAt} · window ${windowToken}`}
          />
          <HStack gap={3} wrap="wrap" align="stretch">
            {KPIS.map((kpi) => (
              <VStack key={kpi.key} style={{flex: `1 1 ${SIZE.tileMin}`, minWidth: 0}}>
                <ValueSlot cell={feature[kpi.key]} size={TYPE.panelFigure} label={kpi.title} />
              </VStack>
            ))}
          </HStack>
        </VStack>

        <VStack gap={3}>
          <PanelHeader title="Trend" sub="three series, a y scale each, one shared temporal x axis" />
          {feature.preCapability ? (
            <PreCapabilityTrend feature={feature} windowToken={windowToken} />
          ) : (
            <FeatureTrend feature={feature} />
          )}
        </VStack>

        <VStack gap={2}>
          <PanelHeader
            title="Named outliers in this feature"
            sub="grade-1 and grade-2 functions, named in plain text — never behind a hover or a disclosure"
          />
          {outliers.length === 0 ? (
            <Text style={{fontSize: TYPE.body}}>
              no grade-1 or grade-2 functions in this window
            </Text>
          ) : (
            <VStack gap={1}>
              {outliers.map((o) => (
                <HStack key={o.qualname} gap={3} wrap="wrap" align="baseline">
                  <Text style={{...NUMERAL, fontSize: TYPE.label, color: T.grade(o.grade)}}>
                    {o.grade}
                  </Text>
                  <Text style={{fontSize: TYPE.body, fontFamily: T.mono}}>{o.qualname}</Text>
                  <Text color="secondary" style={{fontSize: TYPE.tick, fontFamily: T.mono}}>
                    {`${o.path} · ${o.driver} · bar ${o.bar}`}
                  </Text>
                </HStack>
              ))}
            </VStack>
          )}
        </VStack>
      </VStack>
    </Shell>
  );
}
