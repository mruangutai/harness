import { Badge, Card, Icon, IconButton, Popover, Stack, Text } from '@astryxdesign/core';
import type { SharedSearch } from './api';
import { GradingCaveat, NoShipRecords, PreCapability, UnavailableValue } from './gapstates';
import { FeatureTable, GradeOutlierTable, ReworkTable, ShippedFeatureTable, type Feature } from './tables';

type RecordValue = Record<string, unknown>;
type Payload = { aggregate?: RecordValue; features?: Feature[]; trend?: RecordValue };

function asRecord(value: unknown): RecordValue | undefined { return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as RecordValue : undefined; }
function asString(value: unknown): string | undefined { return typeof value === 'string' ? value : undefined; }
function asNumber(value: unknown): number { return typeof value === 'number' ? value : 0; }

export function InfoDisclosure({ title, lines }: { title: string; lines: string[] }) {
  return <Popover label={`About ${title}`} placement="below" alignment="end" width={320} content={<Stack gap={2}><Text type="label">{title}</Text>{lines.map((line) => <Text key={line} type="supporting">{line}</Text>)}</Stack>}><IconButton label={`About ${title}`} variant="ghost" size="sm" icon={<Icon icon="info" size="sm" />} /></Popover>;
}

function TrendRegion({ trend, featureScope = false }: { trend?: RecordValue; featureScope?: boolean }) {
  const unavailable = asRecord(trend?.unavailable);
  if (unavailable?.records || unavailable?.weekly) return <NoShipRecords scope={featureScope ? 'feature' : 'project'} />;
  const records = asRecord(trend?.records) ?? {};
  const preCapability = Object.entries(records).filter(([, item]) => Object.keys(asRecord(item)?.unavailable ?? {}).length > 0).map(([id]) => id);
  return <Card padding={3}><Stack gap={2}><Text type="supporting">Trend data covers the selected window.</Text>{preCapability.length ? <PreCapability count={preCapability.length} total={Object.keys(records).length} ids={preCapability} /> : null}</Stack></Card>;
}

export function KpiPanel({ id, payload, search }: { id: number; payload: Payload; search: SharedSearch }) {
  const aggregate = payload.aggregate ?? {}; const features = payload.features ?? []; const defects = asRecord(aggregate.escaped_defects); const grading = asRecord(aggregate.grading); const attribution = asRecord(aggregate.attribution); const merged = asRecord(payload.trend?.weekly); const fileMix = asRecord(grading?.file_mix);
  const labels = ['Throughput', 'Rework', 'Blocking Human Touchpoints', 'Escaped Defects', 'Code Grading', 'Usage by Agent / Model Tier', 'Merged PRs Over Time']; const title = labels[id - 1] ?? `KPI ${id}`;
  const defectItems = Array.isArray(defects?.items) ? defects.items.filter((item): item is Feature => { const row = asRecord(item); return typeof row?.feature_id === 'string'; }) : [];
  const outliers = Array.isArray(grading?.outliers) ? grading.outliers.filter((item): item is { qualname: string; path: string; line: number; grade: number; feature_id?: string } => { const row = asRecord(item); return typeof row?.qualname === 'string' && typeof row.path === 'string' && typeof row.line === 'number' && typeof row.grade === 'number'; }) : [];
  const rule = id === 4 ? asString(defects?.sourcing_rule) : id === 7 ? asString(merged?.sourcing_rule) : undefined;
  return <Stack gap={4}><Stack direction="horizontal" justify="between" align="center"><Text as="h2" type="large">{title}</Text>{rule ? <InfoDisclosure title={title} lines={[rule]} /> : null}</Stack>
    {id === 1 ? <TrendRegion trend={payload.trend} /> : null}{id === 2 ? <ReworkTable features={features} search={search} /> : null}{id === 3 ? <FeatureTable features={features} search={search} /> : null}
    {id === 4 ? <Card padding={3}><Stack gap={2}><Text type="display-1">{asNumber(defects?.count)}</Text>{asString(asRecord(defects?.unavailable)?.count) ? <UnavailableValue reason={asString(asRecord(defects?.unavailable)?.count) ?? ''} /> : null}<FeatureTable features={defectItems} search={search} /></Stack></Card> : null}
    {id === 5 ? <Stack direction="horizontal" gap={4} wrap="wrap"><Card padding={3}><Text type="label">Grade Distribution</Text></Card><Card padding={3}><GradeOutlierTable outliers={outliers} search={search} /></Card><GradingCaveat ungraded={asNumber(fileMix?.ungraded_files)} tracked={asNumber(fileMix?.tracked_files)} share={asNumber(fileMix?.ungraded_share)} /></Stack> : null}
    {id === 6 ? <Card padding={3}><Stack gap={2}><Badge label="S-5" /><Text type="body">{asNumber(attribution?.unattributed)} of {asNumber(attribution?.total_commits)} commits unattributed — a measurement, not a hole</Text></Stack></Card> : null}
    {id === 7 ? <Stack gap={3}><TrendRegion trend={merged ? { unavailable: merged.unavailable } : undefined} /><Text type="supporting">{asNumber(merged?.week_count)} weeks · {asNumber(merged?.empty_bucket_count)} unavailable buckets</Text><ShippedFeatureTable features={features} search={search} /></Stack> : null}
  </Stack>;
}

export function FeatureKpiContent({ feature, search }: { feature: Feature; search: SharedSearch }) { return <Stack gap={4}><Text as="h3" type="large">Feature KPIs</Text><TrendRegion trend={feature.trend} featureScope /><FeatureTable features={[feature]} search={search} /></Stack>; }
