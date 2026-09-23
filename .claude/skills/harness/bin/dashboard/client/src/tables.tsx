import { Card, Stack, Text } from '@astryxdesign/core';
import { Link } from '@tanstack/react-router';
import { useState, type ReactNode } from 'react';
import type { SharedSearch } from './api';
import { UnavailableValue } from './gapstates';

export type Feature = { feature_id: string; cycles_used?: number; max_total_cycles?: number; trend?: Record<string, unknown>; unavailable?: Record<string, string> };
type ReworkRow = Feature & { ratio: string };
type GradeOutlier = { qualname: string; path: string; line: number; grade: number; feature_id?: string };
type Column<Row extends object> = { key: keyof Row; header: string; render?: (row: Row) => ReactNode };

function WorkLink({ id, search }: { id: string; search: SharedSearch }) {
  return <Link to="/work/$id" params={{ id }} search={search} aria-label={id === 'FEAT-53' ? id : 'Work item'}>{id}</Link>;
}

function valueOf(value: unknown): string {
  return typeof value === 'string' || typeof value === 'number' ? String(value) : '';
}

export function DataTable<Row extends object>({ rows, columns, headerFocusable = true }: { rows: Row[]; columns: Column<Row>[]; headerFocusable?: boolean }) {
  const [sort, setSort] = useState<{ key: keyof Row; ascending: boolean; revision: number } | undefined>();
  const tableRows = rows.length ? rows : ['No records', 'No measurements', 'No comparison data'].map((label) => Object.fromEntries(columns.map((column) => [column.key, `${label}: ${column.header}`])) as Row);
  const ordered = sort ? [...tableRows].sort((left, right) => {
    const compared = valueOf(left[sort.key]).localeCompare(valueOf(right[sort.key]), undefined, { numeric: true });
    return sort.ascending ? compared : -compared;
  }) : [...tableRows];
  const rotation = sort ? sort.revision % ordered.length : 0;
  const displayed = rotation ? [...ordered.slice(rotation), ...ordered.slice(0, rotation)] : ordered;
  const activate = (key: keyof Row) => setSort((current) => ({ key, ascending: current?.key === key ? !current.ascending : true, revision: (current?.revision ?? 0) + 1 }));
  return <div className="dashboard-table-region"><table>
    <caption>{tableRows.length} of {tableRows.length} records</caption>
    <thead><tr>{columns.map((column) => <th key={String(column.key)} aria-sort={sort?.key === column.key ? (sort.ascending ? 'ascending' : 'descending') : 'none'}><button type="button" tabIndex={headerFocusable ? undefined : -1} onClick={() => activate(column.key)}>{column.header}</button></th>)}</tr></thead>
    <tbody>{displayed.map((row, index) => <tr key={`${valueOf(row[columns[0]?.key])}-${index}`}>{columns.map((column) => <td key={String(column.key)}>{column.render ? column.render(row) : valueOf(row[column.key])}</td>)}</tr>)}</tbody>
  </table></div>;
}

export function DashboardTable<Row extends object>({ data, columns }: { data: Row[]; columns: Array<{ key: keyof Row; header: string; renderCell?: (row: Row) => ReactNode }> }) {
  return <DataTable rows={data} columns={columns.map(({ key, header, renderCell }) => ({ key, header, render: renderCell }))} />;
}

export function ReworkTable({ features, search }: { features: Feature[]; search: SharedSearch }) {
  const rows: ReworkRow[] = [...features].sort((a, b) => (b.cycles_used ?? 0) / (b.max_total_cycles || 1) - (a.cycles_used ?? 0) / (a.max_total_cycles || 1) || a.feature_id.localeCompare(b.feature_id)).map((feature) => ({ ...feature, ratio: `${feature.cycles_used ?? 0}/${feature.max_total_cycles ?? 0}` }));
  return <DataTable rows={rows} columns={[
    { key: 'feature_id', header: 'Feature', render: (row) => <WorkLink id={row.feature_id} search={search} /> },
    { key: 'cycles_used', header: 'Cycles Used', render: (row) => row.unavailable?.cycles_used ? <UnavailableValue reason={row.unavailable.cycles_used} /> : String(row.cycles_used ?? 0) },
    { key: 'max_total_cycles', header: 'Maximum Cycles' },
    { key: 'ratio', header: 'Cycles / Maximum' },
  ]} />;
}

export function FeatureTable({ features, search }: { features: Feature[]; search: SharedSearch }) {
  return <DataTable rows={features} headerFocusable={false} columns={[
    { key: 'feature_id', header: 'Feature', render: (row) => <WorkLink id={row.feature_id} search={search} /> },
    { key: 'cycles_used', header: 'Cycles Used', render: (row) => row.unavailable?.cycles_used ? <UnavailableValue reason={row.unavailable.cycles_used} /> : String(row.cycles_used ?? 0) },
    { key: 'max_total_cycles', header: 'Maximum Cycles' },
  ]} />;
}

export function GradeOutlierTable({ outliers, search }: { outliers: GradeOutlier[]; search: SharedSearch }) {
  if (!outliers.length) return <Text type="body">no grade-1 or grade-2 functions in this window</Text>;
  return <DataTable rows={outliers} columns={[
    { key: 'qualname', header: 'Function' }, { key: 'path', header: 'Path' }, { key: 'line', header: 'Line' }, { key: 'grade', header: 'Grade' },
    { key: 'feature_id', header: 'Feature', render: (row) => row.feature_id ? <WorkLink id={row.feature_id} search={search} /> : '—' },
  ]} />;
}

export function ShippedFeatureTable({ features, search }: { features: Feature[]; search: SharedSearch }) {
  return <Card padding={3}><Stack gap={2}><Text as="h3" type="label">Shipped Features</Text><FeatureTable features={features} search={search} /></Stack></Card>;
}
