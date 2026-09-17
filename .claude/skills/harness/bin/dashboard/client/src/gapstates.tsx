import { Badge, Card, Stack, Text } from '@astryxdesign/core';

const hatch = 'repeating-linear-gradient(45deg, var(--color-neutral) 0, var(--color-neutral) 2px, var(--color-metrics-unavailable-stroke) 2px, var(--color-metrics-unavailable-stroke) 3px, var(--color-neutral) 3px, var(--color-neutral) 6px)';

export function UnavailableValue({ reason }: { reason: string }) {
  return <Card padding={2} style={{ backgroundImage: hatch }}>
    <Stack direction="horizontal" gap={2} align="center" wrap="wrap">
      <Text type="large" style={{ color: 'var(--color-metrics-unavailable-stroke)', fontWeight: 400 }}>—</Text>
      <Badge label="unavailable" />
      <Text type="supporting">{reason}</Text>
    </Stack>
  </Card>;
}

export function NoShipRecords({ scope = 'project' }: { scope?: 'project' | 'feature' }) {
  const feature = scope === 'feature';
  return <Card padding={4} style={{ backgroundColor: 'var(--color-neutral)', border: '1px dashed var(--color-metrics-unavailable-stroke)' }}>
    <Stack gap={2}>
      <Text as="h3" type="large">{feature ? 'No trend for this item' : 'No ship records yet'}</Text>
      <Text type="body">{feature ? 'This item shipped before metrics. The trend begins at the first ship after this capability landed; history is never backfilled.' : <><code>.harness/metrics/trend.jsonl</code> has no ship records in this window. The trend begins at the first ship after this capability landed; history is never backfilled.</>}</Text>
    </Stack>
  </Card>;
}

export function PreCapability({ count, total, ids = [] }: { count: number; total: number; ids?: string[] }) {
  return <Stack direction="horizontal" gap={2} align="center" wrap="wrap">
    <Badge label="S-2" />
    <Text type="supporting">{count} of {total} items in this window shipped before metrics and have no trend line{ids.length ? `: ${ids.join(', ')}` : ''}</Text>
  </Stack>;
}

export function GradingCaveat({ ungraded, tracked, share }: { ungraded: number; tracked: number; share: number }) {
  return <Stack direction="horizontal" gap={2} align="center" wrap="wrap">
    <Badge label="S-3" />
    <Text type="supporting">Grading covers Python only · {ungraded} of {tracked} files ungraded ({Math.round(share * 100)}%)</Text>
  </Stack>;
}
