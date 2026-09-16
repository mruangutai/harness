// Synthetic fixture only. These figures describe no repository.
export const WINDOWS = ['30d', '90d', 'all'];
export const REPOS = ['all', 'harness', 'kaya-ai'];

export const STATUS = [
  {id: 'needs-you', label: 'Needs You', icon: 'warning'},
  {id: 'blocked', label: 'Blocked', icon: 'stop'},
  {id: 'stalled', label: 'Stalled', icon: 'clock'},
  {id: 'over-budget', label: 'Over Budget', icon: 'arrowUp'},
  {id: 'running', label: 'Running', icon: 'wrench'},
  {id: 'stale', label: 'Stale', icon: 'eyeSlash'},
];

export const KPI = [
  {id: 1, label: 'Throughput', value: '4.6 d', delta: '▼ 0.8 d', note: 'median ship cycle'},
  {id: 2, label: 'Rework', value: '14 / 38', delta: '▼ 4 pp', note: 'cycles used / allowed'},
  {id: 3, label: 'Blocking touchpoints', value: '0.7', delta: '= 0.0', note: 'mean per shipped feature'},
  {id: 4, label: 'Escaped defects', value: '3', delta: '▲ 1', note: 'bugs and reverts'},
  {id: 5, label: 'At or above bar', value: '86%', delta: '▲ 6 pp', note: 'Python functions'},
  {id: 6, label: 'Usage by agent / model tier', value: '62%', delta: '▲ 3 pp', note: 'attributable commits'},
  {id: 7, label: 'Merged PRs', value: '11', delta: '▲ 2', note: 'one per shipped feature'},
];

export const WORK = [
  {id:'FEAT-53', repo:'harness', kind:'FEAT', title:'Metrics dashboard', station:'Build', phase:'prototype', status:'needs-you', reasons:'Choose a work layout.', elapsed:'12d 4h', plan:'2d 6h', build:'▶ 8d 9h so far', validate:'not started', runs:9, cycles:'4 / 6', tokens:'184,200', unmeasured:'unmeasured 2 of 9 runs', detail:true},
  {id:'BUG-81', repo:'harness', kind:'BUG', title:'Registry lock recovery', station:'Blocked', phase:'review', status:'blocked', reasons:'Awaiting upstream release.', elapsed:'3d 2h', plan:'7h', build:'1d 4h', validate:'▶ 1d 15h so far', runs:5, cycles:'2 / 4', tokens:'92,400', unmeasured:null, detail:true},
  {id:'GRILL-208', repo:'kaya-ai', kind:'grilling', title:'Settle model fallback policy', station:'Plan', phase:'grilling', status:'stalled', reasons:'No operator reply in 4d.', elapsed:'4d 8h', plan:'▶ 4d 8h so far', build:'not started', validate:'not started', runs:1, cycles:'—', tokens:'—', unmeasured:'unmeasured 1 of 1 runs', detail:false},
  {id:'WT-19', repo:'harness', kind:'worktree', title:'Orphaned release worktree', station:'Build', phase:'cleanup', status:'over-budget', reasons:'Cycle allowance exceeded.', elapsed:'6d 1h', plan:'1d', build:'▶ 5d 1h so far', validate:'not started', runs:7, cycles:'7 / 5', tokens:'228,090', unmeasured:'unmeasured 1 of 7 runs', detail:false},
  {id:'FEAT-61', repo:'kaya-ai', kind:'FEAT', title:'Trace explorer', station:'Build', phase:'implementation', status:'running', reasons:'Agent active now.', elapsed:'1d 9h', plan:'6h', build:'▶ 1d 3h so far', validate:'not started', runs:3, cycles:'1 / 5', tokens:'66,800', unmeasured:null, detail:true},
  {id:'WT-22', repo:'kaya-ai', kind:'worktree', title:'Experiment branch', station:'Build', phase:'prototype', status:'stale', reasons:'No commit in 11d.', elapsed:'15d 6h', plan:'2d', build:'13d 6h', validate:'not started', runs:2, cycles:'1 / 2', tokens:'24,600', unmeasured:'unmeasured 1 of 2 runs', detail:false},
  {id:'BUG-91', repo:'harness', kind:'BUG', title:'Popover focus return', station:'Validate', phase:'ui review', status:'needs-you', reasons:'Needs keyboard acceptance.', elapsed:'2d 3h', plan:'4h', build:'1d 2h', validate:'▶ 21h so far', runs:4, cycles:'2 / 4', tokens:'71,220', unmeasured:null, detail:true},
  {id:'FEAT-62', repo:'harness', kind:'FEAT', title:'Evidence index', station:'Done', phase:'shipped', status:'running', reasons:'Shipping record pending.', elapsed:'5d 7h', plan:'1d 2h', build:'3d', validate:'1d 5h', runs:6, cycles:'3 / 6', tokens:'119,400', unmeasured:null, detail:true},
];

export const GRADES = [3, 6, 14, 22, 31];
export const OUTLIERS = [
  {name:'render_work_row', path:'src/work_table.py', grade:1, driver:'ABC 44', bar:4},
  {name:'resolve_attention', path:'src/attention.py', grade:2, driver:'cognitive 19', bar:4},
  {name:'test_window_filter', path:'tests/test_metrics.py', grade:2, driver:'ABC 18', bar:3},
];

export const REWORK = [
  ['FEAT-53','4','6'], ['BUG-81','2','4'], ['FEAT-61','1','5'], ['BUG-91','2','4'],
];
export const DEFECTS = [
  ['bug_unit','BUG-77','2026-09-22','selector lost URL value'],
  ['revert','REV-19','2026-09-18','restore focus after popover close'],
];
export const USAGE = [
  ['opus','93','31%'], ['sonnet','71','24%'], ['gpt-5','22','7%'],
  ['no_prefix','83','28%'], ['human','17','6%'], ['feature_only','9','3%'], ['unresolvable_step_id','3','1%'],
];
export const SHIPPED = [
  ['FEAT-47','2026-09-09','2026-W37','#882'], ['FEAT-49','2026-09-16','2026-W38','#901'], ['FEAT-50','2026-09-23','2026-W39','—'],
];
