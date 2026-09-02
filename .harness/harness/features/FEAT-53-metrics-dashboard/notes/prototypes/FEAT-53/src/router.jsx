// DESIGN.md §C-1's navigation model: TanStack Router, three routes, and ALL
// view state in the URL.
//
//   /?window=<w>                        aggregate
//   /features?window=<w>&sort=<kpi>     the rows behind an aggregate
//   /features/$featureId?window=<w>     one feature
//
// The window is a named token (30d, 90d, all), never a date pair, so a URL
// still means something a week later. `validateSearch` is the only place a
// default is applied, and it is applied to the URL rather than to component
// state — which is what keeps "no component holds either as the source of
// truth" true rather than merely intended.

import {
  Outlet,
  createRootRoute,
  createRoute,
  createRouter,
  useParams,
  useSearch,
} from '@tanstack/react-router';
import {Aggregate} from './routes/Aggregate.jsx';
import {FeatureRows} from './routes/FeatureRows.jsx';
import {FeatureDetail} from './routes/FeatureDetail.jsx';
import {KPIS, WINDOW_TOKENS} from './fixture.js';

// `all` is the default because it is the only window in this fixture that holds
// both pre-capability features and features with trend data — S-2's precondition.
const DEFAULT_WINDOW = 'all';
const KPI_KEYS = KPIS.map((k) => k.key);

const windowOf = (search) =>
  WINDOW_TOKENS.includes(search?.window) ? search.window : DEFAULT_WINDOW;

const rootRoute = createRootRoute({component: Outlet});

const aggregateRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  validateSearch: (search) => ({window: windowOf(search)}),
  component: function AggregateRoute() {
    const {window: windowToken} = useSearch({from: '/'});
    return <Aggregate windowToken={windowToken} />;
  },
});

const featureRowsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/features',
  validateSearch: (search) => ({
    window: windowOf(search),
    sort: KPI_KEYS.includes(search?.sort) ? search.sort : 'throughput',
  }),
  component: function FeatureRowsRoute() {
    const {window: windowToken, sort} = useSearch({from: '/features'});
    return <FeatureRows windowToken={windowToken} sortKey={sort} />;
  },
});

const featureDetailRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/features/$featureId',
  validateSearch: (search) => ({window: windowOf(search)}),
  component: function FeatureDetailRoute() {
    const {featureId} = useParams({from: '/features/$featureId'});
    const {window: windowToken} = useSearch({from: '/features/$featureId'});
    return <FeatureDetail featureId={featureId} windowToken={windowToken} />;
  },
});

export const routeTree = rootRoute.addChildren([
  aggregateRoute,
  featureRowsRoute,
  featureDetailRoute,
]);

export function makeRouter(options = {}) {
  return createRouter({routeTree, defaultPreload: false, ...options});
}
