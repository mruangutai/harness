import { Card, RadioList, RadioListItem, Selector, Skeleton, Stack, Text } from '@astryxdesign/core';
import { useQuery } from '@tanstack/react-query';
import {
  Link,
  Outlet,
  createRootRoute,
  createRoute,
  createRouter,
  useNavigate,
  useParams,
  useSearch,
} from '@tanstack/react-router';
import type { History } from '@tanstack/history';
import { fetchKpis, fetchWork, type SharedSearch } from './api';

export const productPaths = ['/', '/kpi/$n', '/work/$id'];

type Search = SharedSearch;

function sharedSearch(search: Record<string, unknown>): Search {
  return {
    window: typeof search.window === 'string' && search.window ? search.window : 'all',
    repo: typeof search.repo === 'string' && search.repo ? search.repo : 'all',
  };
}

function queries(search: Search) {
  return {
    kpis: useQuery({ queryKey: ['kpis', search.window, search.repo], queryFn: () => fetchKpis(search) }),
    work: useQuery({ queryKey: ['work', search.window, search.repo], queryFn: () => fetchWork(search) }),
  };
}

function SharedHeader({ search }: { search: Search }) {
  const navigate = useNavigate();
  const replace = (next: Partial<Search>) => navigate({ to: '.', search: (current) => ({ ...current, ...next }), replace: true });
  return <Card padding={4}>
    <Stack gap={3}>
      <Text as="h1" type="display-2">Operations Dashboard</Text>
      <RadioList label="Window" value={search.window} onChange={(window) => replace({ window })} orientation="horizontal">
        <RadioListItem label="30d" value="30d" />
        <RadioListItem label="90d" value="90d" />
        <RadioListItem label="All" value="all" />
      </RadioList>
      <Selector label="Repository" value={search.repo} options={[{ label: 'All', value: 'all' }, { label: 'Alpha', value: 'alpha' }]} onChange={(repo) => replace({ repo: String(repo) })} />
    </Stack>
  </Card>;
}

function Shell({ search, children }: { search: Search; children: React.ReactNode }) {
  return <Stack as="main" maxWidth="1200px" padding={4} gap={6} style={{ margin: '0 auto' }}>
    <SharedHeader search={search} />
    {children}
  </Stack>;
}

function LoadingRegion() {
  return <Card padding={4}><Skeleton height={96} /></Card>;
}

function Overview() {
  const search = useSearch({ from: '/' });
  const { kpis, work } = queries(search);
  return <Shell search={search}>
    {kpis.data && work.data ? <Stack gap={4}>
      <Text as="h2" type="large">Repository KPIs</Text>
      <Stack direction="horizontal" gap={3} wrap="wrap">
        {kpis.data.kpis.map((kpi) => <Card key={kpi.id} padding={3}>
          <Link to="/kpi/$n" params={{ n: String(kpi.id) }} search={search}>{kpi.label}</Link>
        </Card>)}
      </Stack>
      <Text as="h2" type="large">Work List</Text>
      <Stack gap={2}>{work.data.items.map((item) => <Card key={item.id} padding={3}>
        {item.kind === 'FEAT' || item.kind === 'BUG' ? <Link to="/work/$id" params={{ id: item.id }} search={search}>{item.name}</Link> : <Text type="body">{item.name}</Text>}
      </Card>)}</Stack>
    </Stack> : <LoadingRegion />}
  </Shell>;
}

function KpiRoute() {
  const search = useSearch({ from: '/kpi/$n' });
  const { n } = useParams({ from: '/kpi/$n' });
  const { kpis, work } = queries(search);
  const label = kpis.data?.kpis.find((kpi) => String(kpi.id) === n)?.label ?? `KPI ${n}`;
  return <Shell search={search}>{kpis.data && work.data ? <Stack gap={4}>
    <Text as="h2" type="large">{label}</Text>
    <Stack gap={2}>{work.data.items.filter((item) => item.kind === 'FEAT' || item.kind === 'BUG').map((item) => <Card key={item.id} padding={3}>
      <Link to="/work/$id" params={{ id: item.id }} search={search}>{item.name}</Link>
    </Card>)}</Stack>
  </Stack> : <LoadingRegion />}</Shell>;
}

function WorkRoute() {
  const search = useSearch({ from: '/work/$id' });
  const { id } = useParams({ from: '/work/$id' });
  const { kpis, work } = queries(search);
  const item = work.data?.items.find((candidate) => candidate.id === id);
  return <Shell search={search}>{kpis.data && work.data ? <Stack gap={4}>
    <Text as="h2" type="large">{item?.name ?? id}</Text>
    <Text type="supporting">{id}</Text>
  </Stack> : <LoadingRegion />}</Shell>;
}

const rootRoute = createRootRoute({ component: Outlet });
const overviewRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', validateSearch: sharedSearch, component: Overview });
const kpiRoute = createRoute({ getParentRoute: () => rootRoute, path: '/kpi/$n', validateSearch: sharedSearch, component: KpiRoute });
const workRoute = createRoute({ getParentRoute: () => rootRoute, path: '/work/$id', validateSearch: sharedSearch, component: WorkRoute });
const routeTree = rootRoute.addChildren([overviewRoute, kpiRoute, workRoute]);

export function makeRouter(options: { history?: History } = {}) {
  return createRouter({ routeTree, defaultPreload: false, ...options });
}

