python3 - <<'PY'
import json, pathlib, re, yaml
root = pathlib.Path.cwd()
ref = (root / '.claude/skills/harness/references/github-mirror.md').read_text()
assert 'Caller-to-failure-policy' in ref
assert all(word in ref for word in ('gh_try', 'SKIP', 'board-station', 'reconcile', 'factory', 'wayfind', 'gh_cost_log', 'subprocess deadlines', 'exit 2'))
cli = (root / '.claude/skills/harness/bin/factory_cli.py').read_text().split('import json')[0]
assert 'nothing mutated); exit 3' not in cli
receipt = json.loads((root / '.harness/harness/features/FEAT-2452-gh-one-transport/notes/enforcement-backlog.json').read_text())
assert type(receipt['number']) is int and receipt['number'] > 0
assert receipt['url'] == 'https://github.com/mruangutai/harness/issues/' + str(receipt['number'])
assert receipt['title'] == 'Enforcement GitHub reads must not trust unverified state' and receipt['state'] == 'OPEN'
assert all(word in receipt['body'] for word in ('branch-create-gate.py', 'merge-gate.py', 'nonempty stdout', 'return code', 'local branch', 'head read'))
repo = json.loads((root / '.harness/harness.json').read_text())['github']['repo']
probe = (root / '.harness/harness/features/FEAT-2452-gh-one-transport/notes/issue-types-live-probe.txt').read_text().splitlines()
assert probe and not any('SKIP' in line for line in probe)
assert any(line.startswith('probe-issue-types: CAPABILITY PRESENT ' + repo + ' ') or line == 'probe-issue-types: CAPABILITY ABSENT ' + repo + ' declares no native issue types' for line in probe)
plan = yaml.safe_load((root / '.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml').read_text())
owned = {(f if isinstance(f, str) else f['path']).split('#')[0] for t in plan['tasks'] for f in t['files']}
owned = sorted(rel for rel in owned if not rel.startswith('.harness/'))
assert 'tests/offline_gh_support.py' in owned and len(owned) == 29
for rel in owned:
    text = (root / rel).read_text()
    assert 'GH_SYNC_GH' not in text, rel
    assert not re.search(r'\bD-11\b', text), rel
decs = (root / '.harness/harness/docs/DECISIONS.md').read_text(); dec_start = decs.index('\n## DEC-138 '); para_start = decs.index('Shared code, and migration scope.', dec_start)
para = ' '.join(decs[para_start:decs.index('\n\n', para_start)].split()); assert para_start < decs.index('\n## ', dec_start + 1)
assert 'factory_gh' in para and 'gh_bin' not in para and 'keeps its own runner' not in para and all(word in para for word in ('imports only', 'internal_id_args', 'attach_sub_issue_args', 'parent_args', 'blocked_by_args', 'standing regression guard for the write-only rule'))
print('PASS policy vocabulary, exit-2 correction, enforcement-ticket readback, live capability receipt and retired-override absence')
PY

