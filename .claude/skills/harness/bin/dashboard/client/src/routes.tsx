import { Card, RadioList, RadioListItem, Selector, Skeleton, Stack, Text } from '@astryxdesign/core';
import { useQuery } from '@tanstack/react-query';
import { Link, Outlet, createRootRoute, createRoute, createRouter, useNavigate, useParams, useSearch } from '@tanstack/react-router';
import type { History } from '@tanstack/history';
import { useEffect, useRef } from 'react';
import { fetchKpis, fetchWork, type SharedSearch } from './api';
import { KpiPanel, FeatureKpiContent } from './panels';
import { KpiTiles } from './tiles';
import { WorkView, type WorkSearch } from './work-view';
import { UnavailableValue } from './gapstates';

export const productPaths = ['/', '/kpi/$n', '/work/$id'];
type Search = WorkSearch;
type KpiPayload = { aggregate?: Record<string, unknown>; features?: Array<Record<string, unknown>>; trend?: Record<string, unknown> };
const kpiLabels = ['Throughput', 'Rework', 'Blocking Human Touchpoints', 'Escaped Defects', 'Code Grading', 'Usage by Agent / Model Tier', 'Merged PRs Over Time'];

function sharedSearch(search: Record<string, unknown>): Search {
  const queryStatuses = new URLSearchParams(window.location.search).getAll('status');
  const status = queryStatuses.length > 1 ? queryStatuses.at(-1) : search.status;
  return { window: typeof search.window === 'string' && search.window ? search.window : 'all', repo: typeof search.repo === 'string' && search.repo ? search.repo : 'all', station: typeof search.station === 'string' ? search.station : 'all', status: typeof status === 'string' ? status : 'all', kind: typeof search.kind === 'string' ? search.kind : 'all', layout: search.layout === 'kanban' ? 'kanban' : 'table' };
}
function sharedKpiSearch(search: Record<string, unknown>): SharedSearch {
  return { window: typeof search.window === 'string' && search.window ? search.window : 'all', repo: typeof search.repo === 'string' && search.repo ? search.repo : 'all' };
}
function useRouteLanding(path: string, title: React.RefObject<HTMLHeadingElement | null>, ready: boolean) {
  useEffect(() => {
    if (ready && sessionStorage.getItem('routeFocusPath') === path && title.current) {
      sessionStorage.removeItem('routeFocusPath');
      title.current.focus();
    }
  }, [path, ready, title]);
}
function RootLayout() {
  useEffect(() => {
    const rememberRouteTarget = (event: MouseEvent) => {
      const target = event.target instanceof Element ? event.target : null;
      const link = target?.closest<HTMLAnchorElement>('a[href]') ?? null;
      const button = target?.closest<HTMLButtonElement>('button[aria-label]') ?? null;
      if (link && (link.pathname.startsWith('/kpi/') || link.pathname.startsWith('/work/'))) {
        sessionStorage.setItem('routeFocusPath', link.pathname);
        sessionStorage.setItem('returnFocusTarget', `link:${link.getAttribute('href')}`);
      } else if (button) {
        sessionStorage.setItem('returnFocusTarget', `button:${button.getAttribute('aria-label')}`);
      }
    };
    const restoreReturnFocus = () => {
      const target = sessionStorage.getItem('returnFocusTarget');
      if (!target) return;
      const restore = (remaining: number) => {
        const separator = target.indexOf(':');
        const kind = target.slice(0, separator);
        const value = target.slice(separator + 1);
        const selector = kind === 'link' ? `a[href="${CSS.escape(value)}"]` : `button[aria-label="${CSS.escape(value)}"]`;
        const initiator = document.querySelector<HTMLElement>(selector);
        if (initiator) {
          document.documentElement.dataset.inputModality = 'pointer';
          initiator.focus();
        }
        else if (remaining) window.setTimeout(() => restore(remaining - 1), 25);
      };
      window.setTimeout(() => restore(8));
    };
    const notePointer = (event: PointerEvent) => {
      document.documentElement.dataset.inputModality = 'pointer';
      const target = event.target instanceof Element ? event.target : null;
      const dialogTrigger = document.querySelector<HTMLElement>('[aria-haspopup="dialog"][aria-expanded="true"]');
      if (dialogTrigger && !target?.closest('[role="dialog"]') && target !== dialogTrigger) window.setTimeout(() => dialogTrigger.focus());
      target?.closest<HTMLElement>('[role="combobox"]')?.setAttribute('data-pointer-origin', '');
    };
    const noteKeyboard = (event: KeyboardEvent) => {
      document.documentElement.dataset.inputModality = 'keyboard';
      if (event.key === 'Tab') document.querySelectorAll<HTMLElement>('[role="combobox"][data-pointer-origin]').forEach((selector) => selector.removeAttribute('data-pointer-origin'));
    };
    const retainResultAnnouncement = () => document.querySelectorAll<HTMLElement>('[aria-live="polite"]:not([data-result-count])').forEach((region) => region.removeAttribute('aria-live'));
    document.documentElement.dataset.inputModality = 'keyboard';
    retainResultAnnouncement();
    const announcementObserver = new MutationObserver(retainResultAnnouncement);
    announcementObserver.observe(document.body, { childList: true, subtree: true });
    document.addEventListener('click', rememberRouteTarget, true);
    document.addEventListener('pointerdown', notePointer, true);
    document.addEventListener('keydown', noteKeyboard, true);
    window.addEventListener('popstate', restoreReturnFocus);
    if (performance.getEntriesByType('navigation').at(0)?.type === 'back_forward') restoreReturnFocus();
    return () => {
      announcementObserver.disconnect();
      document.removeEventListener('click', rememberRouteTarget, true);
      document.removeEventListener('pointerdown', notePointer, true);
      document.removeEventListener('keydown', noteKeyboard, true);
      window.removeEventListener('popstate', restoreReturnFocus);
    };
  }, []);
  return <Outlet />;
}
function SharedHeader({ search }: { search: Search }) {
  const navigate = useNavigate();
  const replace = (next: Partial<Search>) => navigate({ to: '.', search: (current) => ({ ...current, ...next }), replace: true });
  useEffect(() => {
    const radios = () => [...document.querySelectorAll<HTMLInputElement>('.dashboard-header input[type="radio"]')];
    const tab = (event: KeyboardEvent) => {
      if (event.key !== 'Tab' || event.shiftKey) return;
      const options = radios();
      const active = document.activeElement;
      const index = options.indexOf(active as HTMLInputElement);
      const kind = active instanceof HTMLElement && active.getAttribute('aria-label') === 'Kind';
      const clear = [...document.querySelectorAll<HTMLElement>('button')].find((button) => button.textContent === 'Clear Filters');
      const layout = [...document.querySelectorAll<HTMLElement>('button')].find((button) => button.getAttribute('aria-label') === 'Kanban / Table layout');
      if (kind) { event.preventDefault(); (clear ?? layout)?.focus(); }
      else if (active === clear && layout) { event.preventDefault(); layout.focus(); }
      else if (index >= 0 && index < options.length - 1) { event.preventDefault(); options[index + 1].focus(); }
      else if (active instanceof HTMLAnchorElement && active.closest('.dashboard-header')) { event.preventDefault(); options[0]?.focus(); }
    };
    document.addEventListener('keydown', tab, true);
    return () => document.removeEventListener('keydown', tab, true);
  }, []);
  return <Stack as="header" className="dashboard-header" direction="horizontal" justify="between" align="center" gap={4}><Stack direction="horizontal" align="center" gap={3}><Link to="/" search={search}>Overview</Link><Text as="h1" type="display-2">Operations Dashboard</Text></Stack><Stack direction="horizontal" align="center" gap={3}><RadioList label="Window" value={search.window} onChange={(window) => replace({ window })} orientation="horizontal"><RadioListItem label="30d" value="30d" /><RadioListItem label="90d" value="90d" /><RadioListItem label="All" value="all" /></RadioList><Selector label="Repository" value={search.repo} options={[{ label: 'All', value: 'all' }, { label: 'Alpha', value: 'alpha' }]} onChange={(repo) => replace({ repo: String(repo) })} /></Stack></Stack>;
}
function Shell({ search, children }: { search: SharedSearch; children: React.ReactNode }) {
  return <><style>{`:root{color-scheme:dark}body{margin:0;background:rgb(27,27,27)}.dashboard-header,.dashboard-shell,.dashboard-footer{max-width:1600px;margin:0 auto;padding-left:24px;padding-right:24px}.dashboard-header{min-height:72px}.dashboard-header [role="combobox"]{min-width:180px}.dashboard-shell{padding-top:24px;padding-bottom:24px}.dashboard-footer{min-height:24px}.dashboard-shell table{width:100%;min-width:0}.dashboard-shell table th:first-child,.dashboard-shell table td:first-child{position:sticky;left:0;background:var(--color-background-card);z-index:1}.dashboard-shell :focus-visible{outline:2px solid var(--color-text-primary);outline-offset:2px}.dashboard-shell [data-route-title]:focus,.dashboard-shell [data-route-title]:focus-visible,[data-input-modality="pointer"] .dashboard-shell :focus{outline:0!important;outline-offset:0!important}@media (max-width: 831px){.dashboard-header,.dashboard-shell,.dashboard-footer{padding-left:16px;padding-right:16px}}`}</style><SharedHeader search={{ ...search, station: 'all', status: 'all', kind: 'all', layout: 'table' }} /><main className="dashboard-shell">{children}<UnavailableValue reason="Trend data is unavailable for pre-metrics records." /></main><footer className="dashboard-footer" /></>;
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
  const setSearch = (next: Partial<Search>) => navigate({ to: '/', search: { ...search, ...next }, replace: true });
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
  useRouteLanding(`/kpi/${n}`, title, Boolean(kpis.data && kpiLabels[Number(n) - 1]));
  const id = Number(n);
  const label = kpiLabels[id - 1];
  return <Shell search={search}>{kpis.data && label ? <Stack gap={4}><Text as="h1" type="large" tabIndex={-1} data-route-title ref={title}>{label}</Text><KpiPanel id={id} payload={kpis.data} search={search} /></Stack> : kpis.error ? <FailedRegion title="KPI panel unavailable" error={kpis.error} retry={() => void kpis.refetch()} /> : <LoadingRegion />}</Shell>;
}
function WorkRoute() {
  const search = useSearch({ from: '/work/$id' });
  const { id } = useParams({ from: '/work/$id' });
  const title = useRef<HTMLHeadingElement>(null);
  const work = useQuery({ queryKey: ['work', search.window, search.repo], queryFn: () => fetchWork(search), retry: false });
  const item = work.data?.items.find((candidate) => candidate.name === id);
  useRouteLanding(`/work/${id}`, title, Boolean(item));
  return <Shell search={search}>{item ? <Stack gap={4}><Text as="h1" type="large" tabIndex={-1} data-route-title ref={title}>{item.name}</Text><Text type="body">{item.id} · {item.repository} · {item.station ?? '—'} / {item.phase ?? '—'}</Text><Text type="code">{item.source_path} · {item.main_path ?? '—'} · {item.worktree_path ?? 'no linked worktree'}</Text><Text type="body">Runs {item.runs ?? '—'} · Cycles {item.cycles_used ?? '—'}/{item.max_total_cycles ?? '—'}</Text><FeatureKpiContent feature={item} search={search} /></Stack> : work.error ? <FailedRegion title="Work detail unavailable" error={work.error} retry={() => void work.refetch()} /> : <LoadingRegion />}</Shell>;
}
const rootRoute = createRootRoute({ component: RootLayout });
const overviewRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', validateSearch: sharedSearch, component: Overview });
const kpiRoute = createRoute({ getParentRoute: () => rootRoute, path: '/kpi/$n', validateSearch: sharedKpiSearch, component: KpiRoute });
const workRoute = createRoute({ getParentRoute: () => rootRoute, path: '/work/$id', validateSearch: sharedSearch, component: WorkRoute });
const routeTree = rootRoute.addChildren([overviewRoute, kpiRoute, workRoute]);
export function makeRouter(options: { history?: History } = {}) { return createRouter({ routeTree, defaultPreload: false, ...options }); }
