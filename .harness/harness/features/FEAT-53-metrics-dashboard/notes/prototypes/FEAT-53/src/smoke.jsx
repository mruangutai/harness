import {renderToString} from 'react-dom/server';
import {createMemoryHistory, RouterProvider} from '@tanstack/react-router';
import {makeRouter} from './router.jsx';
import {KPI, STATUS, WORK} from './fixture.js';

async function render(path){
  const router=makeRouter({history:createMemoryHistory({initialEntries:[path]})});
  await router.load();
  return renderToString(<RouterProvider router={router}/>);
}

const paths=[
  '/?window=30d&repo=all&station=all&status=all&kind=all&layout=table',
  '/kpi/5?window=90d&repo=harness',
  '/work/FEAT-53?window=30d&repo=harness',
  '/__fixtures/gap-states?window=all&repo=all',
];
const pages=await Promise.all(paths.map(render));
const checks=[
  ['three product routes and fixture render',pages.every((page)=>page.length>1000)],
  ['six status shortcuts',STATUS.every((status)=>pages[0].includes(status.label))],
  ['seven KPI labels',KPI.every((kpi)=>pages[0].includes(kpi.label.split(' ')[0]))],
  ['dashboard order',pages[0].indexOf('Repository KPIs')<pages[0].indexOf('Work List')&&pages[0].indexOf('Work List')<pages[0].indexOf('Status Shortcuts')&&pages[0].indexOf('Status Shortcuts')<pages[0].indexOf('Station')],
  ['Table is the default',pages[0].includes('All Work, Sorted by')&&pages[0].includes('Status</caption>')],
  ['Kanban and Table controls',pages[0].includes('Kanban')&&pages[0].includes('Table')],
  ['Status column',pages[0].includes('>Status<')&&!pages[0].includes('Attention + reasons')],
  ['all four work kinds',['FEAT','BUG','grilling','worktree'].every((kind)=>WORK.some((item)=>item.kind===kind))],
  ['partial token copy',pages[0].includes('unmeasured 1 of 2 runs')],
  ['operational header first',pages[2].indexOf('Station · Phase · Run')<pages[2].indexOf('Throughput')],
  ['all honest states on fixture route',['S-1','S-2','S-3','S-4','S-5','S-6','S-7'].every((state)=>pages[3].includes(state))],
  ['gallery absent from dashboard',!pages[0].includes('Honest-State Gallery')],
];
for(const [name,ok] of checks)console.log(`${ok?'ok  ':'FAIL'} ${name}`);
if(checks.some(([,ok])=>!ok))process.exitCode=1;
