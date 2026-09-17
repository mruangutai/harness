import { Card, RadioList, RadioListItem, Selector, Skeleton, Stack, Text } from '@astryxdesign/core';
import { useQuery } from '@tanstack/react-query';
import { Link, Outlet, createRootRoute, createRoute, createRouter, useNavigate, useParams, useSearch } from '@tanstack/react-router';
import type { History } from '@tanstack/history';
import { useEffect, useRef } from 'react';
import { fetchKpis, fetchWork, type SharedSearch } from './api';
import { KpiPanel, FeatureKpiContent } from './panels';
import { KpiTiles } from './tiles';
import { WorkView, type WorkSearch } from './work-view';

export const productPaths = ['/', '/kpi/$n', '/work/$id'];
type Search = WorkSearch;
type Kpi = { id: number; label: string; aggregate?: Record<string, unknown>; features?: Array<Record<string, unknown>>; trend?: Record<string, unknown> };
type KpiPayload = { kpis: Kpi[]; aggregate?: Record<string, unknown>; trend?: Record<string, unknown> };
let routeFocusTarget: string | undefined;

function sharedSearch(search: Record<string, unknown>): Search {
  return { window: typeof search.window === 'string' && search.window ? search.window : 'all', repo: typeof search.repo === 'string' && search.repo ? search.repo : 'all', station: typeof search.station === 'string' ? search.station : 'all', status: typeof search.status === 'string' ? search.status : 'all', kind: typeof search.kind === 'string' ? search.kind : 'all', layout: search.layout === 'kanban' ? 'kanban' : 'table' };
}
function sharedKpiSearch(search: Record<string, unknown>): SharedSearch {
  return { window: typeof search.window === 'string' && search.window ? search.window : 'all', repo: typeof search.repo === 'string' && search.repo ? search.repo : 'all' };
}
function useRouteLanding(path: string, title: React.RefObject<HTMLHeadingElement | null>) {
  useEffect(() => {
    if (routeFocusTarget === path) {
      routeFocusTarget = undefined;
      title.current?.focus();
    }
  }, [path, title]);
}
function RootLayout() {
  useEffect(() => {
    const rememberRouteTarget = (event: MouseEvent) => {
      const link = event.target instanceof Element ? event.target.closest<HTMLAnchorElement>('a[href]') : null;
      if (link && (link.pathname.startsWith('/kpi/') || link.pathname.startsWith('/work/'))) routeFocusTarget = link.pathname;
    };
    document.addEventListener('click', rememberRouteTarget, true);
    return () => document.removeEventListener('click', rememberRouteTarget, true);
  }, []);
  return <Outlet />;
}
function SharedHeader({ search }: { search: Search }) {
  const navigate = useNavigate();
  const replace = (next: Partial<Search>) => navigate({ to: '.', search: (current) => ({ ...current, ...next }), replace: true });
  return <Card padding={4}><Stack gap={3}><Text as="h1" type="display-2">Operations Dashboard</Text><RadioList label="Window" value={search.window} onChange={(window) => replace({ window })} orientation="horizontal"><RadioListItem label="30d" value="30d" /><RadioListItem label="90d" value="90d" /><RadioListItem label="All" value="all" /></RadioList><Selector label="Repository" value={search.repo} options={[{ label: 'All', value: 'all' }, { label: 'Alpha', value: 'alpha' }]} onChange={(repo) => replace({ repo: String(repo) })} /></Stack></Card>;
}
function Shell({ search, children }: { search: SharedSearch; children: React.ReactNode }) {
  return <><style>{`.dashboard-shell{max-width:1600px;margin:0 auto;padding:24px}.dashboard-shell :focus-visible{outline:2px solid var(--color-text);outline-offset:2px}.dashboard-shell [data-route-title]:focus,.dashboard-shell [data-route-title]:focus-visible{outline:none}@media (max-width: 831px){.dashboard-shell{padding:16px}}`}</style><Stack as="main" className="dashboard-shell" gap={6}><SharedHeader search={search as Search} />{children}</Stack></>;
}
function LoadingRegion() { return <Card padding={4}><Skeleton height={96} /></Card>; }
function FailedRegion({ title, error, retry }: { title: string; error: Error; retry: () => void }) {
  return <Card padding={4}><Stack gap={2}><Text as="h2" type="large">{title}</Text><Text type="body">{error.message}</Text><button type="button" onClick={retry}>Retry</button></Stack></Card>;
}
function Overview() {
  const search = useSearch({ from: '/' });
  const navigate = useNavigate();
  const kpis = useQuery<KpiPayload>({ queryKey: ['kpis', search.window, search.repo], queryFn: () => fetchKpis(search) as Promise<KpiPayload>, retry: false });
  const work = useQuery({ queryKey: ['work', search.window, search.repo], queryFn: () => fetchWork(search), retry: false });
  const setSearch = (next: Partial<Search>) => navigate({ to: '.', search: (current) => ({ ...current, ...next }), replace: true });
  return <Shell search={search}><Stack gap={4}>
    {kpis.data ? <><Text as="h2" type="large">Repository KPIs</Text><KpiTiles payload={kpis.data} search={search} /></> : kpis.error ? <FailedRegion title="Repository KPIs unavailable" error={kpis.error} retry={() => void kpis.refetch()} /> : <LoadingRegion />}
    <WorkView data={work.data} search={search} setSearch={setSearch} refresh={() => void work.refetch()} error={work.error} loading={work.isFetching} />
  </Stack></Shell>;
}
function KpiRoute() {
  const search = useSearch({ from: '/kpi/$n' });
  const { n } = useParams({ from: '/kpi/$n' });
  const title = useRef<HTMLHeadingElement>(null);
  const kpis = useQuery<KpiPayload>({ queryKey: ['kpis', search.window, search.repo], queryFn: () => fetchKpis(search) as Promise<KpiPayload>, retry: false });
  useRouteLanding(`/kpi/${n}`, title);
  const kpi = kpis.data?.kpis.find((candidate) => String(candidate.id) === n);
  return <Shell search={search}>{kpi ? <Stack gap={4}><Text as="h1" type="large" tabIndex={-1} data-route-title ref={title}>{kpi.label}</Text><KpiPanel id={kpi.id} payload={kpi} search={search} /></Stack> : kpis.error ? <FailedRegion title="KPI panel unavailable" error={kpis.error} retry={() => void kpis.refetch()} /> : <LoadingRegion />}</Shell>;
}
function WorkRoute() {
  const search = useSearch({ from: '/work/$id' });
  const { id } = useParams({ from: '/work/$id' });
  const title = useRef<HTMLHeadingElement>(null);
  const work = useQuery({ queryKey: ['work', search.window, search.repo], queryFn: () => fetchWork(search), retry: false });
  useRouteLanding(`/work/${id}`, title);
  const item = work.data?.items.find((candidate) => candidate.id === id);
  return <Shell search={search}>{item ? <Stack gap={4}><Text as="h1" type="large" tabIndex={-1} data-route-title ref={title}>{item.name}</Text><Text type="body">{item.id} · {item.repository} · {item.station ?? '—'} / {item.phase ?? '—'}</Text><Text type="code">{item.source_path} · {item.main_path ?? '—'} · {item.worktree_path ?? 'no linked worktree'}</Text><Text type="body">Runs {item.runs ?? '—'} · Cycles {item.cycles_used ?? '—'}/{item.max_total_cycles ?? '—'}</Text><FeatureKpiContent feature={item} search={search} /></Stack> : work.error ? <FailedRegion title="Work detail unavailable" error={work.error} retry={() => void work.refetch()} /> : <LoadingRegion />}</Shell>;
}
const rootRoute = createRootRoute({ component: RootLayout });
const overviewRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', validateSearch: sharedSearch, component: Overview });
const kpiRoute = createRoute({ getParentRoute: () => rootRoute, path: '/kpi/$n', validateSearch: sharedKpiSearch, component: KpiRoute });
const workRoute = createRoute({ getParentRoute: () => rootRoute, path: '/work/$id', validateSearch: sharedSearch, component: WorkRoute });
const routeTree = rootRoute.addChildren([overviewRoute, kpiRoute, workRoute]);
export function makeRouter(options: { history?: History } = {}) { return createRouter({ routeTree, defaultPreload: false, ...options }); }
