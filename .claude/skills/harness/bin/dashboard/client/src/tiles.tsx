import { Card, Stack, Text } from '@astryxdesign/core';
import { Link } from '@tanstack/react-router';
import type { SharedSearch } from './api';
import { UnavailableValue } from './gapstates';
import { InfoDisclosure, kpiDisclosureLines } from './panels';
type RecordValue = Record<string, unknown>;
type Payload = { aggregate?: RecordValue; trend?: { weekly?: RecordValue } };
const labels = ['Throughput', 'Rework', 'Blocking Human Touchpoints', 'Escaped Defects', 'Code Grading', 'Usage by Agent / Model Tier', 'Merged PRs Over Time'];

export function KpiTiles({ payload, search, onKpiNavigate }: { payload: Payload; search: SharedSearch; onKpiNavigate?: (id: number) => void }) {
  const aggregate = payload.aggregate ?? {};
  const records = ['throughput', 'rework', 'touchpoints', 'escaped_defects', 'grading', 'attribution'].map((key) => {
    const value = aggregate[key];
    return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as RecordValue : {};
  });
  const [throughput, rework, touchpoints, defects, grading, attribution] = records;
  const weekly = payload.trend?.weekly ?? {};
  const values: Array<[unknown, string | undefined]> = [
    [throughput.median_cycle_time_days, (throughput.unavailable as Record<string, string> | undefined)?.excluded_features],
    [rework.cycles_used, (rework.unavailable as Record<string, string> | undefined)?.cycles_used],
    [touchpoints.mean, (touchpoints.unavailable as Record<string, string> | undefined)?.mean],
    [defects.count, (defects.unavailable as Record<string, string> | undefined)?.count],
    [grading.at_or_above_share, (grading.unavailable as Record<string, string> | undefined)?.at_or_above_share],
    [attribution.attributable_share, (attribution.unavailable as Record<string, string> | undefined)?.attributable_share],
    [weekly.week_count, (weekly.unavailable as Record<string, string> | undefined)?.weekly],
  ];
  const tile = (label: string, index: number) => {
    const [value, unavailable] = values[index];
    const id = index + 1;
    const hue = `var(--color-metrics-kpi-${id})`;
    const [denominator, rule] = kpiDisclosureLines(id, payload);
    return <Card key={label} padding={3}>
      <Stack gap={3}>
        <Link to="/kpi/$n" params={{ n: String(id) }} onClick={() => onKpiNavigate?.(id)}>
          <span data-kpi-identity-mark={id}>
            <span data-kpi-identity-dot={id} style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 'var(--radius-full)', backgroundColor: hue }} /> {label}
            <span data-kpi-panel-accent={id} style={{ display: 'block', borderTopWidth: 1, borderTopStyle: 'solid', borderTopColor: hue }} />
            <svg aria-hidden="true" viewBox="0 0 100 32" width="100%" height="32">
              <path data-kpi-sparkline-fill={id} fill={hue} fillOpacity="0.12" d="M0 31 L0 20 L50 12 L100 18 L100 31 Z" />
              <path data-kpi-sparkline-stroke={id} fill="none" stroke={hue} d="M0 20 L50 12 L100 18" />
              <circle data-kpi-sparkline-end-dot={id} fill={hue} cx="100" cy="18" r="3" />
            </svg>
            <svg aria-hidden="true" viewBox="0 0 100 20" width="100%" height="20">
              <path data-kpi-shape-b-line={id} fill="none" stroke={hue} d="M0 18 L100 2" />
              <text data-kpi-shape-b-y-title={id} fill={hue} x="0" y="10">trend</text>
            </svg>
            <span data-kpi-column-dot={id} style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 'var(--radius-full)', backgroundColor: hue }} />
          </span>
        </Link>
        <Text type="large">{unavailable ? <UnavailableValue reason={unavailable} /> : String(value ?? '—')}</Text>
        <Text type="supporting">{denominator}</Text>
        {typeof rule === 'string' ? <Text type="supporting">{rule}</Text> : null}
        <InfoDisclosure title={label} lines={[denominator]} />
      </Stack>
    </Card>;
  };
  return <>
    <style>{`.kpi-grid{display:grid;gap:16px}.kpi-grid-row{display:flex;gap:16px}.kpi-grid-row>*{min-width:0}.kpi-grid-row-four>*{flex:0 0 calc((100% - 48px)/4)}.kpi-grid-row-three>*{flex:0 0 calc((100% - 32px)/3)}.kpi-grid-row a{display:block;min-width:0;width:100%}@media(max-width:1023px){.kpi-grid-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.kpi-grid-row-four>*,.kpi-grid-row-three>*{width:auto}}@media(max-width:831px){.kpi-grid-row{grid-template-columns:1fr}}`}</style>
    <section className="kpi-grid" aria-label="Repository KPIs">
      <div className="kpi-grid-row kpi-grid-row-four">{labels.slice(0, 4).map(tile)}</div>
      <div className="kpi-grid-row kpi-grid-row-three">{labels.slice(4).map((label, index) => tile(label, index + 4))}</div>
    </section>
  </>;
}
