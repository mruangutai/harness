import {useEffect, useMemo, useRef, useState} from 'react';
import {
  Badge, Button, Card, Divider, HStack, Icon, IconButton, Popover, SegmentedControl,
  SegmentedControlItem, Selector, Text, VStack,
} from '@astryxdesign/core';
import {useNavigate, useRouterState} from '@tanstack/react-router';
import {DEFECTS, GRADES, KPI, OUTLIERS, REPOS, REWORK, SHIPPED, STATUS, USAGE, WINDOWS, WORK} from './fixture.js';
import {T} from './theme.js';

const query=(values)=>`?${new URLSearchParams(Object.entries(values).filter(([,value])=>value!=null&&value!=='')).toString()}`;
const titleCase=(value)=>value.replaceAll('-',' ').replace(/\b\w/g,(letter)=>letter.toUpperCase());
const repositoryOptions=REPOS.map((value)=>({value,label:value==='all'?'All':value==='kaya-ai'?'Kaya AI':titleCase(value)}));
const sharedSearch=(search)=>({window:search.window,repo:search.repo});

function PointerAwareSelector({onChange,...props}){
  const hostRef=useRef(null);
  const pointerOpened=useRef(false);
  useEffect(()=>{
    const trigger=hostRef.current?.querySelector('button[aria-haspopup="listbox"]');
    if(!trigger)return;
    let wasOpen=trigger.getAttribute('aria-expanded')==='true';
    const restoreFocusVisibility=(focusVisible)=>{
      requestAnimationFrame(()=>{
        if(document.activeElement===trigger)trigger.blur();
        trigger.focus({focusVisible});
      });
    };
    const observeOpenState=()=>{
      const isOpen=trigger.getAttribute('aria-expanded')==='true';
      if(wasOpen&&!isOpen)restoreFocusVisibility(!pointerOpened.current);
      wasOpen=isOpen;
    };
    const observer=new MutationObserver(observeOpenState);
    observer.observe(trigger,{attributes:true,attributeFilter:['aria-expanded']});
    const rememberPointer=()=>{
      if(trigger.getAttribute('aria-expanded')==='true')pointerOpened.current=true;
    };
    document.addEventListener('pointerdown',rememberPointer,true);
    return()=>{
      observer.disconnect();
      document.removeEventListener('pointerdown',rememberPointer,true);
    };
  },[]);
  return <div
    ref={hostRef}
    onPointerDownCapture={()=>{pointerOpened.current=true;}}
    onKeyDownCapture={(event)=>{
      const trigger=hostRef.current?.querySelector('button[aria-haspopup="listbox"]');
      if(trigger?.getAttribute('aria-expanded')!=='true'&&(event.key==='Enter'||event.key===' '||event.key.startsWith('Arrow')))pointerOpened.current=false;
    }}>
    <Selector {...props} onChange={onChange}/>
  </div>;
}

if(typeof window!=='undefined'){
  window.__feat53RestoreOrigin=()=>{
    if(sessionStorage.getItem('focusReturnPath')!==location.pathname)return;
    setTimeout(()=>{
      const key=sessionStorage.getItem('focusOrigin');
      const origin=document.querySelector(`[data-focus-key="${key}"]`);
      if(!origin)return;
      origin.focus();
      sessionStorage.removeItem('focusReturnPath');
    },100);
  };
  if(!window.__feat53FocusRestore){
    window.__feat53FocusRestore=true;
    window.addEventListener('popstate',()=>window.__feat53RestoreOrigin());
    window.addEventListener('pageshow',()=>window.__feat53RestoreOrigin());
  }
}

export function InfoDisclosure({title,lines}){
  return <Popover label={`About ${title}`} placement="below" alignment="end" width={320} content={
    <VStack gap={2}>
      <Text type="label">{title}</Text>
      {lines.map((line)=><Text key={line} type="supporting" color="secondary">{line}</Text>)}
    </VStack>
  }>
    <IconButton label={`About ${title}`} variant="ghost" size="sm" icon={<Icon icon="info" size="sm" color="secondary"/>}/>
  </Popover>;
}

function RouteTitle({children,eyebrow}){
  const ref=useRef(null);
  useEffect(()=>{
    if(sessionStorage.getItem('routeFocusPath')!==location.pathname)return;
    sessionStorage.removeItem('routeFocusPath');
    if(sessionStorage.getItem('focusReturnPath')!==location.pathname)ref.current?.focus();
  },[]);
  return <VStack gap={1}>
    {eyebrow?<Text type="supporting" color="secondary">{eyebrow}</Text>:null}
    <Text ref={ref} className="route-title" tabIndex={-1} as="h1" type="display-3">{children}</Text>
  </VStack>;
}

export function Shell({search,children,crumb,dashboardTitle=false}){
  const navigate=useNavigate();
  const pathname=useRouterState({select:(state)=>state.location.pathname});
  const windowRef=useRef(null);
  const update=(patch,focus)=>{
    if(focus)sessionStorage.setItem('headerFocus',focus);
    navigate({to:pathname,search:(previous)=>({...previous,...patch})});
  };
  useEffect(()=>{
    const remember=(event)=>{
      const origin=event.target.closest?.('a[href]');
      if(!origin?.href)return;
      const destination=new URL(origin.href,location.href);
      if(destination.pathname===location.pathname)return;
      sessionStorage.setItem('routeFocusPath',destination.pathname);
      if(!origin.dataset.focusKey)return;
      sessionStorage.setItem('focusOrigin',origin.dataset.focusKey);
      sessionStorage.setItem('focusReturnPath',location.pathname);
    };
    document.addEventListener('click',remember,true);
    return()=>document.removeEventListener('click',remember,true);
  },[]);
  useEffect(()=>window.__feat53RestoreOrigin?.(),[pathname]);
  useEffect(()=>{
    if(sessionStorage.getItem('focusReturnPath')===pathname)return;
    const pending=sessionStorage.getItem('headerFocus');
    if(pending==='window'){
      sessionStorage.removeItem('headerFocus');
      setTimeout(()=>[...windowRef.current.querySelectorAll('button')].find((button)=>button.textContent.trim().toLowerCase()===search.window)?.focus(),50);
    }
  },[pathname,search.window]);

  return <VStack className="app-shell" gap={0}>
    <header className="shared-header">
      <div className="content-frame header-inner">
        <HStack gap={4} justify="between" align="center" wrap="wrap" style={{width:'100%'}}>
          {dashboardTitle
            ?<RouteTitle eyebrow="Harness Operations">Operations Dashboard</RouteTitle>
            :<VStack gap={1}>
              <HStack gap={2} align="center" wrap="wrap"><Text type="label">Harness Operations</Text><Badge variant="neutral" label="Synthetic Fixture"/></HStack>
              <HStack gap={1.5} align="center" wrap="wrap"><a className="crumb" href={`/${query(sharedSearch(search))}`}>Overview</a>{crumb?<><Text color="secondary">›</Text><Text type="supporting">{crumb}</Text></>:null}</HStack>
            </VStack>}
          <HStack gap={3} align="end" wrap="wrap">
            <div ref={windowRef}>
              <SegmentedControl label="Window" value={search.window} onChange={(window)=>update({window},'window')}>
                {WINDOWS.map((value)=><SegmentedControlItem key={value} value={value} label={value==='all'?'All':value}/>) }
              </SegmentedControl>
            </div>
            <PointerAwareSelector label="Repository" options={repositoryOptions} value={search.repo} onChange={(repo)=>update({repo})} width={180} size="md"/>
          </HStack>
        </HStack>
      </div>
    </header>
    <Divider variant="subtle"/>
    <main className="page-content content-frame">{children}</main>
    <footer><div className="content-frame"><Text type="supporting" style={{color:T.faint}}>Synthetic fixture invented for layout and interaction review. No live repository data.</Text></div></footer>
  </VStack>;
}

function StatusMark({id}){
  const status=STATUS.find((item)=>item.id===id);
  return <span className="status-mark"><Icon icon={status.icon} size="sm" aria-hidden="true"/><span>{status.label}</span></span>;
}

function AttentionCard({item,count,search}){
  const href=`/${query({...search,status:item.id})}`;
  const active=search.status===item.id;
  return <a className="attention-card" href={href} aria-current={active?'true':undefined} data-status={item.id} data-focus-key={`status-shortcut-${item.id}`} onClick={()=>sessionStorage.setItem('workFocus','status')}>
    <Icon icon={item.icon} size="md" aria-hidden="true"/>
    <VStack gap={0}>
      <Text type="label" className="status-label" style={{color:T.status(item.id)}}>{item.label}</Text>
      <Text type="supporting" color="secondary" hasTabularNumbers>{count} Items</Text>
    </VStack>
  </a>;
}

function MiniTrend({id}){
  const patterns=[
    [8,9,11,10,12,13,12,15,14,16,15,17,18,19],
    [19,18,17,18,16,15,15,14,13,14,12,12,11,10],
    [7,8,7,9,10,9,11,12,11,13,12,14,15,14],
    [4,5,4,6,5,7,8,7,9,10,9,11,12,13],
    [48,51,53,56,58,61,65,68,71,74,78,81,84,86],
    [35,37,40,42,41,45,48,50,53,55,57,60,61,62],
    [3,3,4,4,5,6,6,7,8,8,9,9,10,11],
  ];
  const values=patterns[id-1];
  const points=values.map((value,index)=>`${index*20},${48-value/2}`).join(' ');
  const area=`0,48 ${points} 260,48`;
  return <svg className="spark" viewBox="0 0 260 52" preserveAspectRatio="none" aria-hidden="true" focusable="false" data-days="14">
    <line x1="0" y1="48" x2="260" y2="48" stroke={T.border}/>
    <polygon points={area} fill={T.kpi(id)} opacity="0.12"/>
    <polyline points={points} fill="none" stroke={T.kpi(id)} strokeWidth="2.5" vectorEffect="non-scaling-stroke"/>
    <circle cx="260" cy={48-values.at(-1)/2} r="3" fill={T.kpi(id)}/>
  </svg>;
}

function KpiTile({kpi,search}){
  const label=titleCase(kpi.label);
  return <Card padding={3} className={`kpi-tile kpi-${kpi.id}`} style={{borderTop:`2px solid ${T.kpi(kpi.id)}`}}>
    <HStack gap={2} justify="between" align="start">
      <a className="tile-primary" data-focus-key={`kpi-${kpi.id}`} href={`/kpi/${kpi.id}${query(sharedSearch(search))}`}><Text type="label">{`${kpi.id} · ${label}`}</Text></a>
      <InfoDisclosure title={label} lines={[kpi.note,kpi.id===7?'One shipped feature is one merged PR; weekly buckets appear in the panel.':'Tile values use the selected window and repository.']}/>
    </HStack>
    <VStack gap={1} className="tile-value">
      <Text type="display-1" weight="semibold" hasTabularNumbers>{kpi.value}</Text>
      <Text type="supporting" style={{color:kpi.delta.startsWith('▲')?T.positive:kpi.delta.startsWith('▼')?T.negative:T.neutral}}>{kpi.delta}</Text>
      <Text type="supporting" color="secondary">{kpi.note}</Text>
    </VStack>
    <MiniTrend id={kpi.id}/>
  </Card>;
}

function WorkAction({item,search,expanded,toggle}){
  if(item.detail)return <a className="row-link" data-focus-key={`work-${item.id}`} href={`/work/${item.id}${query(sharedSearch(search))}`}>{item.id}</a>;
  return <Button label={`${expanded?'Collapse':'Expand'} ${item.id}`} variant="ghost" size="sm" onClick={(event)=>{
    const target=event.currentTarget;
    toggle(item.id);
    requestAnimationFrame(()=>target.focus());
  }}>{item.id}</Button>;
}

function TokenValue({item}){
  return <VStack gap={0.5}>
    <Text type="body" weight="semibold" hasTabularNumbers>{item.tokens==='—'?'—':`${item.tokens} Tokens`}</Text>
    {item.unmeasured?<Text type="supporting" className="token-coverage">◐ {item.unmeasured}</Text>:null}
  </VStack>;
}

function InlineDetail({item}){
  return <Card variant="muted" padding={3} className="inline-detail"><VStack gap={1}>
    <Text type="label">{`${titleCase(item.kind)} Source Context`}</Text>
    <Text type="supporting" color="secondary">{item.kind==='grilling'?'This decision ticket remains in planning; resolve it in the parent issue.':'This worktree has no detail route; inspect its branch and last activity here.'}</Text>
    <Text type="code">{item.kind==='grilling'?'.harness/notes/grilling/GRILL-208.md':'.claude/worktrees/WT-22'}</Text>
  </VStack></Card>;
}

function selectorOptions(key){
  if(key==='status')return [{value:'all',label:'All'},...STATUS.map(({id,label})=>({value:id,label}))];
  return [{value:'all',label:'All'},...new Set(WORK.map((item)=>item[key]))].map((option,index)=>index===0?option:{value:option,label:key==='kind'&&['FEAT','BUG'].includes(option)?option:titleCase(option)});
}

function WorkControls({search}){
  const navigate=useNavigate();
  const statusRef=useRef(null);
  const layoutRef=useRef(null);
  const update=(patch,focus)=>{
    if(focus)sessionStorage.setItem('workFocus',focus);
    navigate({to:'/',search:(previous)=>({...previous,...patch})});
  };
  useEffect(()=>{
    const pending=sessionStorage.getItem('workFocus');
    if(pending==='status'){
      sessionStorage.removeItem('workFocus');
      setTimeout(()=>statusRef.current?.querySelector('button')?.focus(),0);
    }else if(pending==='layout'){
      sessionStorage.removeItem('workFocus');
      setTimeout(()=>[...layoutRef.current.querySelectorAll('button')].find((button)=>button.textContent.trim()===titleCase(search.layout))?.focus(),0);
    }
  },[search.status,search.layout]);
  const active=['station','status','kind'].some((key)=>search[key]!=='all');
  return <HStack gap={3} align="end" wrap="wrap" className="work-controls">
    {['station','status','kind'].map((key)=><div key={key} ref={key==='status'?statusRef:null}><PointerAwareSelector label={titleCase(key)} options={selectorOptions(key)} value={search[key]} onChange={(value)=>update({[key]:value})} width={160}/></div>)}
    {active?<Button label="Clear Filters" variant="ghost" onClick={()=>update({station:'all',status:'all',kind:'all'},'status')}/>:null}
    <div className="layout-control" ref={layoutRef}><SegmentedControl label="Layout" value={search.layout} onChange={(layout)=>update({layout},'layout')}>
      <SegmentedControlItem value="kanban" label="Kanban"/>
      <SegmentedControlItem value="table" label="Table"/>
    </SegmentedControl></div>
  </HStack>;
}

function filtered(search){
  return WORK.filter((item)=>search.repo==='all'||item.repo===search.repo).filter((item)=>['station','status','kind'].every((key)=>search[key]==='all'||item[key]===search[key]));
}

function WorkCard({item,search,expanded,toggle}){
  return <Card padding={3} className="work-card"><VStack gap={2}>
    <HStack justify="between" align="start" gap={2}><WorkAction item={item} search={search} expanded={expanded} toggle={toggle}/><Badge label={item.kind} variant="neutral"/></HStack>
    <Text type="body" weight="semibold">{item.title}</Text>
    <HStack gap={2} wrap="wrap"><StatusMark id={item.status}/><Text type="supporting" color="secondary">{item.station} · {titleCase(item.phase)}</Text></HStack>
    <Text type="supporting" color="secondary">{item.reasons}</Text>
    <HStack gap={3} wrap="wrap"><Text type="supporting">Elapsed {item.elapsed}</Text><Text type="supporting">Cycles {item.cycles}</Text><Text type="supporting">Runs {item.runs}</Text></HStack>
    <TokenValue item={item}/>
    {expanded?<InlineDetail item={item}/>:null}
  </VStack></Card>;
}

function KanbanWork({rows,search,expanded,toggle}){
  const lanes=['Plan','Build','Validate','Blocked','Done'];
  return <div className="kanban">{lanes.map((lane)=><section className="lane" key={lane}>
    <HStack gap={2} justify="between"><Text as="h3" type="label">{lane}</Text><Badge label={`${rows.filter((item)=>item.station===lane).length}`} variant="neutral"/></HStack>
    <VStack gap={2}>{rows.filter((item)=>item.station===lane).map((item)=><WorkCard key={item.id} item={item} search={search} expanded={expanded===item.id} toggle={toggle}/>)}</VStack>
  </section>)}</div>;
}

function WorkTable({rows,search,expanded,toggle,sort,setSort}){
  const ranks=Object.fromEntries(STATUS.map((item,index)=>[item.id,index]));
  const sorted=[...rows].sort((a,b)=>sort==='status'?ranks[a.status]-ranks[b.status]:String(a[sort]).localeCompare(String(b[sort])));
  const head=(key,label)=><button className="sort-button" onClick={()=>setSort(key)}>{label}{sort===key?' ↓':''}</button>;
  return <div className="table-scroll work-table"><table>
    <caption>All Work, Sorted by {titleCase(sort)}</caption>
    <thead><tr><th className="sticky-col">{head('id','ID')}</th><th>{head('repo','Repository')}</th><th>{head('station','Station / Phase')}</th><th>{head('status','Status')}</th><th>{head('elapsed','Elapsed / Phases')}</th><th>{head('runs','Runs')}</th><th>Cycles / Max</th><th>Tokens</th></tr></thead>
    <tbody>{sorted.map((item)=><tr key={item.id}>
      <td className="sticky-col"><WorkAction item={item} search={search} expanded={expanded===item.id} toggle={toggle}/>{expanded===item.id?<InlineDetail item={item}/>:null}</td>
      <td>{titleCase(item.repo)}</td>
      <td><strong>{item.station}</strong><br/><small>{titleCase(item.phase)}</small></td>
      <td><StatusMark id={item.status}/><br/><small>{item.reasons}</small></td>
      <td><strong>{item.elapsed}</strong><br/><small>{item.plan} · {item.build} · {item.validate}</small></td>
      <td>{item.runs}</td><td>{item.cycles}</td><td><TokenValue item={item}/></td>
    </tr>)}</tbody>
  </table></div>;
}

function WorkList({search,counts}){
  const [expanded,setExpanded]=useState(null);
  const [sort,setSort]=useState('status');
  const rows=useMemo(()=>filtered(search),[search]);
  const toggle=(id)=>setExpanded((previous)=>previous===id?null:id);
  return <section aria-labelledby="work-heading"><VStack gap={4}>
    <HStack gap={3} justify="between" align="end" wrap="wrap"><VStack gap={1}><Text id="work-heading" as="h2" type="large">Work List</Text><Text type="supporting" color="secondary">{rows.length} of {WORK.filter((item)=>search.repo==='all'||item.repo===search.repo).length} items in the selected repository scope.</Text></VStack></HStack>
    <section aria-label="Status Shortcuts" className="attention-strip">{STATUS.map((status)=><AttentionCard key={status.id} item={status} count={counts[status.id]} search={search}/>)}</section>
    <WorkControls search={search}/>
    <div className="sr-only" aria-live="polite">{titleCase(search.layout)} layout. {rows.length} results.</div>
    {search.layout==='kanban'?<KanbanWork rows={rows} search={search} expanded={expanded} toggle={toggle}/>:<WorkTable rows={rows} search={search} expanded={expanded} toggle={toggle} sort={sort} setSort={setSort}/>}
  </VStack></section>;
}

export function Overview({search}){
  const scoped=WORK.filter((item)=>search.repo==='all'||item.repo===search.repo);
  const counts=Object.fromEntries(STATUS.map((status)=>[status.id,scoped.filter((item)=>item.status===status.id).length]));
  return <Shell search={search} dashboardTitle><VStack gap={6}>
    <section aria-labelledby="kpi-heading"><HStack gap={2} align="center"><Text id="kpi-heading" as="h2" type="large">Repository KPIs</Text><Text type="supporting" color="secondary">Seven measures for the selected window and repository.</Text></HStack><div className="kpi-grid">{KPI.map((kpi)=><KpiTile key={kpi.id} kpi={kpi} search={search}/>)}</div></section>
    <WorkList search={search} counts={counts}/>
  </VStack></Shell>;
}

function SimpleTable({caption,columns,rows,footer}){
  return <div className="table-scroll"><table><caption>{caption}</caption><thead><tr>{columns.map((column)=><th key={column} scope="col">{column}</th>)}</tr></thead><tbody>{rows.map((row,index)=><tr key={index}>{row.map((value,columnIndex)=><td key={columnIndex}>{value}</td>)}</tr>)}</tbody>{footer?<tfoot><tr>{footer.map((value,index)=><td key={index}>{value}</td>)}</tr></tfoot>:null}</table></div>;
}

function GradePanel(){
  return <div className="panel-split"><Card padding={4}><VStack gap={3}><HStack gap={2} align="center"><Text as="h2" type="large">Grade Distribution</Text><Badge label="S-3 · Python Only" variant="neutral"/></HStack><div className="histogram">{GRADES.map((count,index)=><div key={index} className="bar-slot"><div className="bar" style={{height:`${20+count*2}px`,background:T.grade(index+1)}}/><Text type="supporting">Grade {index+1}</Text><Text type="body" weight="semibold">{count}</Text></div>)}</div><Text type="supporting" color="secondary">Grading covers Python only. 7 of 48 tracked files are ungraded.</Text></VStack></Card><Card padding={4}><VStack gap={3}><Text as="h2" type="large">Named Grade-1 / Grade-2 Outliers</Text><SimpleTable caption="Named Code-Grade Outliers" columns={['Function','Grade','Driver','Bar']} rows={OUTLIERS.map((item)=>[`${item.name} · ${item.path}`,item.grade,item.driver,item.bar])}/></VStack></Card></div>;
}

function KpiArtifact({id,search}){
  if(id===2)return <SimpleTable caption="TBL-1 · Rework by Feature" columns={['Feature','Cycles Used','Max Total Cycles','Ratio']} rows={REWORK.map((row)=>[<a data-focus-key={`kpi-row-${row[0]}`} href={`/work/${row[0]}${query(search)}`}>{row[0]}</a>,row[1],row[2],`${row[1]} / ${row[2]}`])} footer={['Window Aggregate','9','19','9 / 19']}/>;
  if(id===4)return <SimpleTable caption="TBL-2 · Escaped Defects" columns={['Kind','ID','Date','Subject']} rows={DEFECTS}/>;
  if(id===6)return <SimpleTable caption="TBL-3 · Usage by Agent / Model Tier" columns={['Bucket','Commits','Share']} rows={USAGE}/>;
  if(id===7)return <SimpleTable caption="Shipped Features Behind Merged PRs" columns={['Feature','Ship Date','Week','PR']} rows={SHIPPED.map((row)=>[<a data-focus-key={`kpi-row-${row[0]}`} href={`/work/${row[0]}${query(search)}`}>{row[0]}</a>,...row.slice(1)])}/>;
  return <SimpleTable caption={`${titleCase(KPI[id-1].label)} · Feature Rows`} columns={['Feature','Value','Window Status']} rows={WORK.filter((item)=>item.detail).slice(0,5).map((item,index)=>[<a data-focus-key={`kpi-row-${item.id}`} href={`/work/${item.id}${query(search)}`}>{item.id}</a>,id===1?`${3+index}.2 d`:id===3?`${index%3} touchpoints`:`${72+index*4}%`,'Measured'])}/>;
}

export function KpiPage({search,id}){
  const kpi=KPI[id-1]??KPI[0];
  const label=titleCase(kpi.label);
  return <Shell search={search} crumb={`KPI ${kpi.id}`}><VStack gap={5}><RouteTitle eyebrow={`KPI ${kpi.id} · ${search.window} · ${titleCase(search.repo)}`}>{label}</RouteTitle><Card padding={4} style={{borderTop:`2px solid ${T.kpi(kpi.id)}`}}><VStack gap={4}><HStack gap={3} justify="between" align="start"><VStack gap={1}><Text type="display-1" weight="semibold">{kpi.value}</Text><Text type="body" color="secondary">{kpi.note}</Text></VStack><InfoDisclosure title={label} lines={[kpi.note,'Every feature row opens its operational work detail.']}/></HStack>{id===5?<GradePanel/>:<KpiArtifact id={id} search={search}/>}</VStack></Card></VStack></Shell>;
}

function OperationalHeader({item}){
  return <Card padding={4} className="operational-header"><div className="op-header-grid">
    <VStack gap={1}><Text type="label">Status</Text><StatusMark id={item.status}/><Text type="supporting" color="secondary">{item.reasons}</Text></VStack>
    <VStack gap={0}><Text type="label">Station · Phase · Run</Text><Text type="body">{item.station} · {titleCase(item.phase)} · {item.runs}</Text></VStack>
    <VStack gap={0}><Text type="label">Budget</Text><Text type="body">Cycles {item.cycles}</Text></VStack>
    <VStack gap={0}><Text type="label">Phase Elapsed</Text><Text type="body">{item.plan} · {item.build} · {item.validate}</Text></VStack>
    <VStack gap={0}><Text type="label">Tokens</Text><TokenValue item={item}/></VStack>
  </div></Card>;
}

export function WorkDetail({search,id}){
  const item=WORK.find((candidate)=>candidate.id===id&&candidate.detail);
  if(!item)return <Shell search={search} crumb="Work"><VStack gap={3}><RouteTitle eyebrow="No Detail Route">{id}</RouteTitle><Text>This fixture has no FEAT or BUG item with that ID.</Text></VStack></Shell>;
  return <Shell search={search} crumb={`Work · ${id}`}><VStack gap={5}><OperationalHeader item={item}/><RouteTitle eyebrow={`${titleCase(item.repo)} · ${item.kind}`}>{item.id} · {item.title}</RouteTitle><div className="detail-kpis">{KPI.slice(0,6).map((kpi,index)=><Card padding={3} key={kpi.id} style={{borderTop:`2px solid ${T.kpi(kpi.id)}`}}><VStack gap={2}><HStack gap={1} justify="between"><Text type="label">{titleCase(kpi.label)}</Text><InfoDisclosure title={`${item.id} · ${titleCase(kpi.label)}`} lines={['This is the selected work item’s contribution to the repository KPI.']}/></HStack><Text type="display-3" weight="semibold">{index===0?'5.1 d':index===1?item.cycles:index===2?'2':index===3?'0':index===4?'82%':'71%'}</Text></VStack></Card>)}</div><GradePanel/></VStack></Shell>;
}

function StateGallery(){
  return <section aria-labelledby="states-heading"><HStack gap={2} align="center"><Text id="states-heading" as="h2" type="large">Honest-State Gallery</Text><InfoDisclosure title="Honest States" lines={['Each fixture state is visually distinct in addition to its text label.','This route is not part of product navigation.']}/></HStack><div className="state-grid">
    <Card padding={3} className="state s1"><Badge label="S-1" variant="neutral"/><Text type="label">No Ship Records Yet</Text><Text type="supporting" color="secondary">The region is replaced; no axes are present.</Text></Card>
    <Card padding={3} className="state s2"><Badge label="S-2" variant="neutral"/><Text type="label">— No Trend</Text><Text type="supporting" color="secondary">Shipped before metrics; axes remain and the line breaks.</Text></Card>
    <Card padding={3} className="state s3"><Badge label="S-3" variant="neutral"/><Text type="label">Python Only</Text><Text type="supporting" color="secondary">7 of 48 files are ungraded.</Text></Card>
    <Card padding={3} className="state s4"><Badge label="S-4 · Unavailable" variant="neutral"/><Text type="label">0 Measured · — Unavailable</Text><Text type="supporting" color="secondary">Glyph, weight, fill and badge differ.</Text></Card>
    <Card padding={3} className="state s5"><Badge label="S-5" variant="neutral"/><Text type="label">112 Unattributed</Text><Text type="supporting" color="secondary">Named, counted buckets remain visible.</Text></Card>
    <Card padding={3} className="state s6"><Badge label="S-6" variant="neutral"/><Text type="label">▶ 8d 9h So Far</Text><Text type="supporting" color="secondary">The build phase is still accruing.</Text></Card>
    <Card padding={3} className="state s7"><Badge label="S-7 · Partial" variant="neutral"/><Text type="label">184,200 Tokens</Text><Text type="supporting" className="token-coverage">◐ unmeasured 2 of 9 runs</Text></Card>
  </div></section>;
}

export function GapStatesFixture({search}){
  return <Shell search={search} crumb="Fixture · Gap States"><VStack gap={5}><RouteTitle eyebrow="Fixture-Only Route">Gap States</RouteTitle><Text type="body" color="secondary">All C-4 states appear together here for visual review. This route is absent from product navigation and the three-route product contract.</Text><StateGallery/></VStack></Shell>;
}
