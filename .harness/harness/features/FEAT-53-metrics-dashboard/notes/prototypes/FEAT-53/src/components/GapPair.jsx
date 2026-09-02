// S-4, as a side-by-side pair, because the judgement DESIGN.md asks for is a
// COMPARISON: "these are the two most confusable states on the surface and a
// shared grey placeholder for both is a defect".
//
// Both cells below are real fixture cells, rendered by the same ValueSlot the
// tiles and the table use — not a mock-up of one. They differ in ALL FOUR of:
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
import {featureById} from '../fixture.js';

const DIFFERENCES = [
  ['glyph', 'the numeral 0', 'the em-dash —, never a numeral, never 0, never blank'],
  ['typography', 'mono 700, text colour', 'mono 400, unavailable-stroke'],
  ['fill', 'normal surface', '45° hatch, unavailable-stroke on surface'],
  ['badge', 'none', 'an "unavailable" badge'],
  ['second line', 'its denominator', 'the reason, always present and always specific'],
  ['in a chart', 'a plotted point at zero', 'no point plotted; the line breaks'],
];

export function GapPair() {
  const zeroSource = featureById('FIX-05');
  const unavailableSource = featureById('FIX-04');

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
        title="A genuine zero and an unavailable measurement, side by side"
        sub="both cells are real fixture values, rendered by the same component the tiles and the table use"
        badge={<GapLabel id="S-4" what="unavailable-with-a-reason versus a genuine zero" />}
      />

      <HStack gap={4} wrap="wrap" align="stretch">
        <VStack gap={2} style={{flex: `1 1 ${SIZE.panelMin}`, minWidth: 0}}>
          <Text weight="medium" style={{fontSize: TYPE.body}}>
            Genuine zero — a measurement, presented with the confidence of one
          </Text>
          <ValueSlot
            cell={zeroSource.touchpoints}
            size={TYPE.panelFigure}
            label={`${zeroSource.name} · blocking human touchpoints`}
          />
          <Text color="secondary" style={{fontSize: TYPE.tick}}>
            Zero touchpoints is a result. It carries its denominator and it is set in exactly the
            type and colour any other value gets.
          </Text>
        </VStack>

        <VStack gap={2} style={{flex: `1 1 ${SIZE.panelMin}`, minWidth: 0}}>
          <Text weight="medium" style={{fontSize: TYPE.body}}>
            Unavailable, with a reason — not a smaller number, not a number
          </Text>
          <ValueSlot
            cell={unavailableSource.escaped}
            size={TYPE.panelFigure}
            label={`${unavailableSource.name} · escaped defects`}
          />
          <Text color="secondary" style={{fontSize: TYPE.tick}}>
            The reason names what is missing, so a reader can act on it. "No data" would not.
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
