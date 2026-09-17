import { Card, Stack, Table, Text, proportional } from '@astryxdesign/core';
import { Link } from '@tanstack/react-router';
import type { SharedSearch } from './api';
import { UnavailableValue } from './gapstates';

export type Feature = { feature_id: string; cycles_used?: number; max_total_cycles?: number; trend?: Record<string, unknown>; unavailable?: Record<string, string> };
type ReworkRow = Feature & { ratio: string };
type GradeOutlier = { qualname: string; path: string; line: number; grade: number; feature_id?: string };

function WorkLink({ id, search }: { id: string; search: SharedSearch }) {
  return <Link to="/work/$id" params={{ id }} search={search}>{id}</Link>;
}

export function ReworkTable({ features, search }: { features: Feature[]; search: SharedSearch }) {
  const rows: ReworkRow[] = [...features].sort((a, b) => (b.cycles_used ?? 0) / (b.max_total_cycles || 1) - (a.cycles_used ?? 0) / (a.max_total_cycles || 1) || a.feature_id.localeCompare(b.feature_id)).map((feature) => ({ ...feature, ratio: `${feature.cycles_used ?? 0}/${feature.max_total_cycles ?? 0}` }));
  return <Table<ReworkRow> data={rows} columns={[
    { key: 'feature_id', header: 'Feature', width: proportional(), renderCell: (row: ReworkRow) => <WorkLink id={row.feature_id} search={search} /> },
    { key: 'cycles_used', header: 'Cycles Used', width: proportional(), renderCell: (row: ReworkRow) => row.unavailable?.cycles_used ? <UnavailableValue reason={row.unavailable.cycles_used} /> : String(row.cycles_used ?? 0) },
    { key: 'max_total_cycles', header: 'Maximum Cycles', width: proportional() },
    { key: 'ratio', header: 'Cycles / Maximum', width: proportional() },
  ]} density="compact" dividers="rows" />;
}

export function FeatureTable({ features, search }: { features: Feature[]; search: SharedSearch }) {
  return <Table<Feature> data={features} columns={[
    { key: 'feature_id', header: 'Feature', width: proportional(), renderCell: (row: Feature) => <WorkLink id={row.feature_id} search={search} /> },
    { key: 'cycles_used', header: 'Cycles Used', width: proportional(), renderCell: (row: Feature) => row.unavailable?.cycles_used ? <UnavailableValue reason={row.unavailable.cycles_used} /> : String(row.cycles_used ?? 0) },
    { key: 'max_total_cycles', header: 'Maximum Cycles', width: proportional() },
  ]} density="compact" dividers="rows" />;
}

export function GradeOutlierTable({ outliers, search }: { outliers: GradeOutlier[]; search: SharedSearch }) {
  if (!outliers.length) return <Text type="body">no grade-1 or grade-2 functions in this window</Text>;
  return <Table<GradeOutlier> data={outliers} columns={[
    { key: 'qualname', header: 'Function', width: proportional() }, { key: 'path', header: 'Path', width: proportional() }, { key: 'line', header: 'Line', width: proportional() }, { key: 'grade', header: 'Grade', width: proportional() },
    { key: 'feature_id', header: 'Feature', width: proportional(), renderCell: (row: GradeOutlier) => row.feature_id ? <WorkLink id={row.feature_id} search={search} /> : '—' },
  ]} density="compact" dividers="rows" />;
}

export function ShippedFeatureTable({ features, search }: { features: Feature[]; search: SharedSearch }) {
  return <Card padding={3}><Stack gap={2}><Text as="h3" type="label">Shipped Features</Text><FeatureTable features={features} search={search} /></Stack></Card>;
}
