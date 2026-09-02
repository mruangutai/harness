// S-4, as a side-by-side pair, because the judgement DESIGN.md asks for is a
// COMPARISON: "these are the two most confusable states on the surface and a
// shared grey placeholder for both is a defect".
//
// KPI 3 is the SHARPEST instance of that pair and the reason this panel shows
// touchpoints on both sides rather than two different metrics (DESIGN.md C-4
// S-4, plan.yaml D-21): neither feature below has a touchpoints.jsonl. The
// input is identical. Only the instrumentation epoch decides that one absence
// is a measured zero and the other is not a measurement at all.
//
// Both cells are real fixture cells, rendered by the same ValueSlot the tiles
// and the table use — not a mock-up of one. They differ in ALL FOUR of:
//
//   glyph        the numeral 0        vs  the em-dash
//   typography   mono 700, text       vs  mono 400, unavailable-stroke
//   fill         normal surface       vs  45 degree hatch
//   badge        none                 vs  an "unavailable" badge
//
// and the reason on an unavailable cell is always specific. A generic "no data"
// is a violation.

import {HStack, Text, VStack} from '@astryxdesign/core';
import {RADIUS, SIZE, T, TYPE} from '../theme.js';
import {GapLabel, PanelHeader, ValueSlot} from './primitives.jsx';
import {TOUCHPOINT_EPOCH_DATE, featureById} from '../fixture.js';

const DIFFERENCES = [
  ['glyph', 'the numeral 0', 'the em-dash —, never a numeral, never 0, never blank'],
  ['typography', 'mono 700, text colour', 'mono 400, unavailable-stroke'],
  ['fill', 'normal surface', '45° hatch, unavailable-stroke on surface'],
  ['badge', 'none', 'an "unavailable" badge'],
  ['second line', 'its denominator', 'the reason, always present and always specific'],
  ['in a chart', 'a plotted point at zero', 'no point plotted; the line breaks'],
];

export function GapPair() {
  const trackedZero = featureById('FIX-05');
  const notTracked = featureById('FIX-03');

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
        title="A tracked zero and a never-tracked feature, side by side"
        sub={`neither feature has a touchpoints.jsonl — the input is identical. Touchpoints are tracked in this project from ${TOUCHPOINT_EPOCH_DATE}, and that epoch alone decides which absence is a measurement.`}
        badge={<GapLabel id="S-4" what="a measured zero versus not tracked at all" />}
      />

      <HStack gap={4} wrap="wrap" align="stretch">
        <VStack gap={2} style={{flex: `1 1 ${SIZE.panelMin}`, minWidth: 0}}>
          <Text weight="medium" style={{fontSize: TYPE.body}}>
            A tracked zero — a measurement, presented with the confidence of one
          </Text>
          <ValueSlot
            cell={trackedZero.touchpoints}
            size={TYPE.panelFigure}
            label={`${trackedZero.name} · blocking human touchpoints`}
          />
          <Text color="secondary" style={{fontSize: TYPE.tick}}>
            {`Started ${trackedZero.startedAt}, after the epoch: instrumentation was running and nothing blocked. Zero is a result, set in exactly the type and colour any other value gets, and it counts in the tile's mean.`}
          </Text>
        </VStack>

        <VStack gap={2} style={{flex: `1 1 ${SIZE.panelMin}`, minWidth: 0}}>
          <Text weight="medium" style={{fontSize: TYPE.body}}>
            Not tracked — no measurement exists, so there is no number to show
          </Text>
          <ValueSlot
            cell={notTracked.touchpoints}
            size={TYPE.panelFigure}
            label={`${notTracked.name} · blocking human touchpoints`}
          />
          <Text color="secondary" style={{fontSize: TYPE.tick}}>
            {`Started ${notTracked.startedAt}, before the epoch: the counter did not exist yet. The reason names that specifically, and this feature is never in the tile's mean — a 0 here would be a fabricated number.`}
          </Text>
        </VStack>
      </HStack>

      <VStack gap={1}>
        {DIFFERENCES.map(([axis, zero, unavailable]) => (
          <HStack key={axis} gap={2} wrap="wrap" align="baseline">
            <Text weight="medium" style={{fontSize: TYPE.tick}}>
              {axis}
            </Text>
            <Text color="secondary" style={{fontSize: TYPE.tick}}>
              {`zero: ${zero}`}
            </Text>
            <Text style={{fontSize: TYPE.tick, color: T.unavailable}}>
              {`unavailable: ${unavailable}`}
            </Text>
          </HStack>
        ))}
      </VStack>
    </VStack>
  );
}
