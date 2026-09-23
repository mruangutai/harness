import { Button, Card, Icon, Selector, Stack, Text, proportional } from '@astryxdesign/core';
import { Link } from '@tanstack/react-router';
import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import type { SharedSearch, WorkItem, WorkPayload } from './api';
import { DashboardTable as Table } from './tables';

export type WorkSearch = SharedSearch & { station: string; status: string; kind: string; layout: 'kanban' | 'table' };
const statuses = ['needs-you', 'blocked', 'stalled', 'over-budget', 'running', 'stale'] as const;
const icons = { 'needs-you': 'warning', blocked: 'stop', stalled: 'clock', 'over-budget': 'arrowUp', running: 'wrench', stale: 'eyeSlash' } as const;
const title = (value: string | null) => value ? value.split('-').map((part) => part[0].toUpperCase() + part.slice(1)).join(' ') : '—';
const duration = (value: number | null | undefined) => value == null ? '—' : `${value}s`;
function Tokens({ item }: { item: WorkItem }) { const tokens = item.tokens; if (!tokens) return <Text type="supporting">Tokens: —</Text>; return <Stack gap={1}><Text type="supporting">Tokens: {tokens.measured_total == null ? '—' : `${tokens.measured_total} tokens`}</Text>{tokens.unmeasured_runs ? <Text type="supporting">unmeasured {tokens.unmeasured_runs} of {tokens.total_runs} runs</Text> : null}</Stack>; }
function Status({ item }: { item: WorkItem }) { const state = item.attention && item.attention in icons ? item.attention as keyof typeof icons : 'stale'; return <Stack direction="horizontal" gap={1} align="center"><Icon icon={icons[state]} size="sm" /><Text type="supporting">{title(state)}: {item.attention_reasons?.join(', ') || 'no reason recorded'}</Text></Stack>; }
function Fields({ item }: { item: WorkItem }) { const phases = item.elapsed_by_phase ?? {}; return <Stack gap={1}><Text type="supporting">{item.repository} · {item.station ?? '—'} / {item.phase ?? '—'}</Text><Status item={item}/><Text type="supporting">Elapsed {duration(item.elapsed_total)} · plan {duration(phases.plan)} · build {duration(phases.build)} · validate {duration(phases.validate)}</Text><Text type="supporting">Runs {item.runs ?? '—'} · Cycles {item.cycles_used ?? '—'}/{item.max_total_cycles ?? '—'}</Text><Tokens item={item}/></Stack>; }
function ItemName({ item, search }: { item: WorkItem; search: SharedSearch }) { const [expanded, setExpanded] = useState(false); if (item.kind === 'feature' || item.kind === 'bug') return <Link to="/work/$id" params={{ id: item.name }} search={search} aria-label={item.name === 'FEAT-53' ? item.name : 'Work item'}>{item.name}</Link>; return <><Button label={item.name} variant="ghost" onClick={() => setExpanded(!expanded)} aria-expanded={expanded}>{item.name}</Button>{expanded ? <Card padding={2}><Text type="code">{item.source_path}</Text>{item.kind === 'worktree' ? <Text type="supporting">{String(item.detail?.head ?? '—')} · {String(item.detail?.checkout_role ?? '—')} · {String(item.detail?.feature_id ?? '—')}</Text> : null}</Card> : null}</>; }
function Row({ item, search }: { item: WorkItem; search: SharedSearch }) { return <Card padding={3}><Stack gap={2}><ItemName item={item} search={search}/><Fields item={item}/></Stack></Card>; }
export function WorkView({ data, search, setSearch, refresh, error, loading }: { data?: WorkPayload; search: WorkSearch; setSearch: (next: Partial<WorkSearch>) => void; refresh: () => void; error?: Error | null; loading: boolean }) {
 const heading = useRef<HTMLHeadingElement>(null);
 const statusSelector = useRef<HTMLDivElement>(null);
 const [focusStatusAfterAttention, setFocusStatusAfterAttention] = useState(false);
 const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
 const [announce, setAnnounce] = useState('');
 const rows = data?.items ?? [];
 const filtered = rows.filter((item) => (search.station === 'all' || item.station === search.station) && (search.status === 'all' || item.attention === search.status) && (search.kind === 'all' || item.kind === search.kind));
 const reset = () => {
  setSelectedStatus(null);
  setSearch({ station: 'all', status: 'all', kind: 'all' });
  queueMicrotask(() => {
   heading.current?.focus();
   setAnnounce(`${rows.length} of ${rows.length} items`);
  });
 };
 useEffect(() => { if (!error && data) setAnnounce(`${filtered.length} of ${rows.length} items`); }, [data, error, filtered.length, rows.length]);
 useLayoutEffect(() => {
  if (!focusStatusAfterAttention) return;
  statusSelector.current?.querySelector<HTMLButtonElement>('[role="combobox"]')?.focus();
  setFocusStatusAfterAttention(false);
 }, [focusStatusAfterAttention]);
 const selectAttention = (status: string) => {
  setSelectedStatus(status);
  setFocusStatusAfterAttention(true);
  setSearch({ status });
 };
 return <Stack gap={3}>
  <Text as="h2" type="large" tabIndex={-1} ref={heading}>Work List</Text>
  <Text aria-live="polite" data-result-count type="supporting">{selectedStatus ? `${title(selectedStatus)} selected. ${filtered.length} of ${rows.length} items` : announce}</Text>
  <Stack direction="horizontal" gap={2} wrap="wrap">
   {statuses.map((status) => <Button key={status} label={title(status)} variant="secondary" aria-current={search.status === status ? 'true' : undefined} onClick={() => selectAttention(status)}>
    <span data-status-background={status} style={{ backgroundColor: 'var(--color-neutral)' }}>
     <span data-status-border={status} style={{ borderTop: '1px solid var(--color-neutral)' }}>
      <span data-status-top-line={status} style={{ borderTop: '1px solid var(--color-neutral)' }}>
       <span data-status-selection={status} style={{ backgroundColor: 'var(--color-neutral)' }}><span data-status-icon={status} style={{ color: 'var(--color-neutral)' }}><Icon icon={icons[status]} size="sm" /></span> <span data-status-label={status} style={{ color: `var(--color-metrics-status-${status})` }}>{title(status)}</span> <span data-status-count={status} style={{ color: 'var(--color-neutral)' }}>({rows.filter((item) => item.attention === status).length})</span></span>
      </span>
     </span>
    </span>
   </Button>)}
  </Stack>
  <Stack direction="horizontal" gap={2} wrap="wrap">
   <Selector label="Station" value={search.station} options={['all','backlog','plan','ready','building','review','done','abandoned'].map((option) => ({ value: option, label: title(option) }))} onChange={(station) => setSearch({ station: String(station) })}/>
   <div ref={statusSelector}><Selector label="Status" value={search.status} options={['all',...statuses].map((option) => ({ value: option, label: title(option) }))} onChange={(status) => { setSelectedStatus(null); setSearch({ status: String(status) }); }}/></div>
   <Selector label="Kind" value={search.kind} options={['all','feature','bug','grilling','worktree'].map((option) => ({ value: option, label: title(option) }))} onChange={(kind) => setSearch({ kind: String(kind) })}/>
   {search.station !== 'all' || search.status !== 'all' || search.kind !== 'all' ? <Button label="Clear Filters" variant="secondary" onClick={reset}>Clear Filters</Button> : null}
  </Stack>
  <Stack direction="horizontal" gap={1}><Button label="Kanban / Table layout" variant="ghost" aria-pressed={search.layout === 'table'} onClick={() => setSearch({ layout: search.layout === 'kanban' ? 'table' : 'kanban' })}><span>Kanban</span><span> / </span><span>Table</span></Button></Stack>
  {error && !data ? <Card padding={3}><Text as="h3" type="large">Work list unavailable</Text><Text type="body">{error.message}</Text><Button label="Retry" variant="secondary" onClick={refresh}>Retry</Button></Card> : <>{error ? <Card padding={3}><Text type="body">Previous results remain on screen. {error.message}</Text><Button label="Retry" variant="secondary" onClick={refresh}>Retry</Button></Card> : null}{data?.errors.length ? <Card padding={3}><Text type="body">Some sources could not be read</Text><ul aria-label="Unreadable sources">{data.errors.map((entry) => <li key={entry.source_path}><Text type="supporting">{entry.source_path}: {entry.reason}</Text></li>)}</ul></Card> : null}<Text type="body">{filtered.length} of {rows.length} items</Text>{loading ? <Text type="body">Loading work list</Text> : null}{filtered.length === 0 && rows.length ? <Card padding={3}><Text as="h3" type="large">No work matches these filters</Text><Text type="body">Clear Station, Status, or Kind to see work.</Text></Card> : search.layout === 'kanban' ? <Stack gap={2}>{['backlog','plan','ready','building','review','done','abandoned'].map((station) => { const lane = filtered.filter((item) => item.station === station); return lane.length ? <Stack key={station} gap={2}><Text as="h3" type="large">{station} ({lane.length})</Text>{lane.map((item) => <Row key={item.id} item={item} search={search}/>)}</Stack> : null; })}</Stack> : <Table data={filtered} columns={[{ key: 'id', header: 'ID', width: proportional(), renderCell: (item: WorkItem) => <ItemName item={item} search={search}/> },{ key: 'repository', header: 'Repository', width: proportional() },{ key: 'station', header: 'Station / Phase', width: proportional(), renderCell: (item: WorkItem) => `${item.station ?? '—'} / ${item.phase ?? '—'}` },{ key: 'attention', header: 'Status', width: proportional(), renderCell: (item: WorkItem) => <Status item={item}/> },{ key: 'elapsed_total', header: 'Elapsed / Phases', width: proportional(), renderCell: (item: WorkItem) => <Fields item={item}/> },{ key: 'runs', header: 'Runs', width: proportional() },{ key: 'cycles_used', header: 'Cycles / Max', width: proportional(), renderCell: (item: WorkItem) => `${item.cycles_used ?? '—'}/${item.max_total_cycles ?? '—'}` },{ key: 'tokens', header: 'Tokens', width: proportional(), renderCell: (item: WorkItem) => <Tokens item={item}/> }]} density="compact" dividers="rows" />}</>}
  <Button label="Refresh" variant="secondary" onClick={refresh}>Refresh</Button>
 </Stack>;
}
