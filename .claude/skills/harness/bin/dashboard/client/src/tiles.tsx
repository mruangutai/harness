import { Card, Stack, Text } from '@astryxdesign/core';
import { Link } from '@tanstack/react-router';
import type { SharedSearch } from './api';
import { UnavailableValue } from './gapstates';
import { InfoDisclosure } from './panels';

type RecordValue = Record<string, unknown>;
type Payload = { aggregate?: RecordValue; trend?: { weekly?: RecordValue } };
const labels = ['Throughput', 'Rework', 'Blocking Human Touchpoints', 'Escaped Defects', 'Code Grading', 'Usage by Agent / Model Tier', 'Merged PRs Over Time'];

export function KpiTiles({ payload, search, onKpiNavigate }: { payload: Payload; search: SharedSearch; onKpiNavigate?: (id: number) => void }) {
  const aggregate = payload.aggregate ?? {};
  const records = ['throughput', 'rework', 'touchpoints', 'escaped_defects', 'grading', 'attribution'].map((key) => { const value = aggregate[key]; return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as RecordValue : {}; });
  const [throughput, rework, touchpoints, defects, grading, attribution] = records;
  const weekly = payload.trend?.weekly ?? {};
  const values: Array<[unknown, string, string | undefined]> = [
    [throughput.median_cycle_time_days, `${String(throughput.measured_features ?? 0)} measured features`, (throughput.unavailable as Record<string, string> | undefined)?.median_cycle_time_days],
    [rework.cycles_used, `${String(rework.max_total_cycles ?? 0)} maximum cycles`, (rework.unavailable as Record<string, string> | undefined)?.cycles_used],
    [touchpoints.mean, `${String(touchpoints.zero_count ?? 0)} measured zero touchpoints`, (touchpoints.unavailable as Record<string, string> | undefined)?.mean],
    [defects.count, 'Escaped defects in this window', (defects.unavailable as Record<string, string> | undefined)?.count],
    [grading.at_or_above_share, 'At or above the configured bar', (grading.unavailable as Record<string, string> | undefined)?.at_or_above_share],
    [attribution.attributable_share, `${String(attribution.unattributed ?? 0)} of ${String(attribution.total_commits ?? 0)} commits unattributed`, (attribution.unavailable as Record<string, string> | undefined)?.attributable_share],
    [weekly.week_count, `${String(weekly.empty_bucket_count ?? 0)} unavailable weekly buckets`, (weekly.unavailable as Record<string, string> | undefined)?.weekly],
  ];
  const kpiLabels = labels;
  return <><style>{`.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}@media(max-width:1023px){.kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.kpi-grid>*:nth-child(7){grid-column:span 2}}@media(max-width:831px){.kpi-grid{grid-template-columns:1fr}.kpi-grid>*:nth-child(7){grid-column:span 1}}`}</style><section className="kpi-grid" aria-label="Repository KPIs">{kpiLabels.map((label, index) => {
    const [value, denominator, unavailable] = values[index]; const rule = index === 3 ? defects.sourcing_rule : index === 6 ? weekly.sourcing_rule : undefined;
    return <Card key={label} padding={3}><Stack gap={3}><Stack direction="horizontal" justify="between" align="center"><Link to="/kpi/$n" params={{ n: String(index + 1) }} search={{ window: search.window, repo: search.repo }} onClick={() => onKpiNavigate?.(index + 1)}>{label}</Link>{typeof rule === 'string' ? <InfoDisclosure title={label} lines={[rule]} /> : null}</Stack>{unavailable ? <UnavailableValue reason={unavailable} /> : <Stack gap={1}><Text type="display-1" hasTabularNumbers>{String(value ?? 0)}</Text><Text type="supporting">{denominator}</Text></Stack>}<div aria-label={`${label} latest fourteen daily points`} data-days="14" style={{ minHeight: 32, width: '100%', borderBottom: '1px solid var(--color-metrics-unavailable-stroke)' }} /></Stack></Card>;
  })}</section></>;
}
