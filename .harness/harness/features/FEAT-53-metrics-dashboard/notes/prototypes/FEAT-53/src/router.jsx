import {Outlet, createRootRoute, createRoute, createRouter, useParams, useSearch} from '@tanstack/react-router';
import {GapStatesFixture, KpiPage, Overview, WorkDetail} from './ui.jsx';
import {REPOS, STATUS, WINDOWS, WORK} from './fixture.js';

const oneOf=(value,allowed,fallback)=>allowed.includes(value)?value:fallback;
const shared=(search)=>({
  window:oneOf(search?.window,WINDOWS,'all'),
  repo:oneOf(search?.repo,REPOS,'all'),
});
const dashboardSearch=(search)=>({
  ...shared(search),
  station:oneOf(search?.station,['all',...new Set(WORK.map((item)=>item.station))],'all'),
  status:oneOf(search?.status,['all',...STATUS.map((item)=>item.id)],'all'),
  kind:oneOf(search?.kind,['all',...new Set(WORK.map((item)=>item.kind))],'all'),
  layout:oneOf(search?.layout,['kanban','table'],'table'),
});

const root=createRootRoute({component:Outlet});
const overview=createRoute({
  getParentRoute:()=>root,
  path:'/',
  validateSearch:dashboardSearch,
  component:()=> <Overview search={useSearch({from:'/'})}/>,
});
const kpi=createRoute({
  getParentRoute:()=>root,
  path:'/kpi/$n',
  validateSearch:shared,
  component:function KpiRoute(){
    const {n}=useParams({from:'/kpi/$n'});
    return <KpiPage id={Math.min(7,Math.max(1,Number(n)||1))} search={useSearch({from:'/kpi/$n'})}/>;
  },
});
const detail=createRoute({
  getParentRoute:()=>root,
  path:'/work/$id',
  validateSearch:shared,
  component:function WorkDetailRoute(){
    const {id}=useParams({from:'/work/$id'});
    return <WorkDetail id={id} search={useSearch({from:'/work/$id'})}/>;
  },
});
const gapStates=createRoute({
  getParentRoute:()=>root,
  path:'/__fixtures/gap-states',
  validateSearch:shared,
  component:()=> <GapStatesFixture search={useSearch({from:'/__fixtures/gap-states'})}/>,
});

export const routeTree=root.addChildren([overview,kpi,detail,gapStates]);
export function makeRouter(options={}){return createRouter({routeTree,defaultPreload:false,...options});}
