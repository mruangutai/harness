// Shared compositions. Every element here is an Astryx primitive or a
// composition of them; every colour, size, radius and spacing value comes from
// a theme token (DESIGN.md §Substrate rules 1 and 2).

import {Badge, Card, HStack, Text, VStack} from '@astryxdesign/core';
import {NUMERAL, RADIUS, T, TYPE, hatchFill} from '../theme.js';

/**
 * The on-screen gap-state label. DESIGN.md's four states are named S-1 … S-4 in
 * the contract, and a reviewer has to be able to POINT at each one, so the
 * token is rendered as visible text rather than living only in a comment.
 */
export function GapLabel({id, what}) {
  return (
    <HStack gap={1.5} align="center">
      <Badge variant="neutral" label={id} />
      <Text size="sm" color="secondary">
        {what}
      </Text>
    </HStack>
  );
}

/** A section heading with its own gap label, used by every panel below. */
export function PanelHeader({title, sub, badge}) {
  return (
    <VStack gap={1}>
      <HStack gap={2} align="center" wrap="wrap">
        <Text as="h2" weight="semibold" style={{fontSize: TYPE.label}}>
          {title}
        </Text>
        {badge}
      </HStack>
      {sub ? (
        <Text color="secondary" style={{fontSize: TYPE.caveat}}>
          {sub}
        </Text>
      ) : null}
    </VStack>
  );
}

export function Panel({children, ...rest}) {
  return (
    <Card padding={4} style={{borderRadius: RADIUS.card, border: `1px solid ${T.border}`}} {...rest}>
      <VStack gap={3}>{children}</VStack>
    </Card>
  );
}

/**
 * S-4, and the only place in the prototype a KPI value is rendered.
 *
 * A genuine zero and an unavailable measurement differ in ALL FOUR of the ways
 * DESIGN.md C-4 requires — glyph, typography, fill, badge — because one is a
 * coincidence away from looking like the other:
 *
 *   genuine zero        the numeral `0`, mono 700, `text`, normal surface, no badge
 *   unavailable         the glyph `—`, mono 400, `unavailable-stroke`, 45° hatch, badge
 *
 * A zero is a measurement and is presented with the confidence of one. And a
 * figure never appears without its denominator or unit (DESIGN.md §Component
 * direction), which is why `secondary` is not optional for an `ok` cell.
 */
export function ValueSlot({cell, size = TYPE.panelFigure, label}) {
  const isUnavailable = cell.state === 'unavailable';
  return (
    <VStack
      gap={1}
      padding={2}
      style={{
        borderRadius: RADIUS.control,
        ...(isUnavailable ? hatchFill : {backgroundColor: T.surface}),
      }}
    >
      {label ? (
        <Text color="secondary" style={{fontSize: TYPE.tick}}>
          {label}
        </Text>
      ) : null}
      <HStack gap={2} align="center" wrap="wrap">
        <Text
          style={{
            ...NUMERAL,
            fontSize: size,
            fontWeight: isUnavailable ? 400 : 700,
            color: isUnavailable ? T.unavailable : T.text,
            lineHeight: 1.1,
          }}
        >
          {isUnavailable ? '\u2014' : cell.value}
        </Text>
        {isUnavailable ? <Badge variant="neutral" label="unavailable" /> : null}
      </HStack>
      <Text color="secondary" style={{fontSize: TYPE.caveat}}>
        {isUnavailable ? cell.reason : cell.secondary}
      </Text>
    </VStack>
  );
}

/**
 * A table cell carrying a KPI. Same four differences as ValueSlot, at cell
 * scale: the hatch and the em-dash are what a reviewer scans a column for.
 */
export function ValueCellBody({cell}) {
  const isUnavailable = cell.state === 'unavailable';
  return (
    <VStack gap={0.5}>
      <HStack gap={1} align="center">
        <Text
          style={{
            ...NUMERAL,
            fontSize: TYPE.body,
            fontWeight: isUnavailable ? 400 : 700,
            color: isUnavailable ? T.unavailable : T.text,
          }}
        >
          {isUnavailable ? '\u2014' : cell.value}
        </Text>
        {isUnavailable ? <Badge variant="neutral" label="unavailable" /> : null}
      </HStack>
      <Text color="secondary" style={{fontSize: TYPE.tick}}>
        {isUnavailable ? cell.reason : cell.secondary}
      </Text>
    </VStack>
  );
}

/** Any numeral outside a ValueSlot — axis ticks, counts, bar labels. */
export function Numeral({children, size = TYPE.body, weight = 700, color = T.text}) {
  return <Text style={{...NUMERAL, fontSize: size, fontWeight: weight, color}}>{children}</Text>;
}

export const hatchStyle = hatchFill;
