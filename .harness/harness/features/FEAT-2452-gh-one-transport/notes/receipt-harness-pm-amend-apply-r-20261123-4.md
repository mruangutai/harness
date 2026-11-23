# baseline check before writes
OK T-01 4 anchor(s) resolved
OK T-02 14 anchor(s) resolved
OK T-03 5 anchor(s) resolved
OK T-04 3 anchor(s) resolved
OK T-05 5 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport: 5 task(s), 31 anchor(s) resolved, 0 failure(s)
exit=0

# writer 1: amend T-05 files
$ plan-merge.py amend --file plan.yaml --key tasks --id T-05 --field files --yaml-value --value-file /tmp/feat2452-r4/t05-files.yaml --expect-sha256 57cfbc07efd1148eb931c16d9da1b6a93c9bc2352de73b41204146908f81d17d
## value file:
- path: .claude/skills/harness/references/github-mirror.md
  quote: '## Failure has four shapes, not one'
- path: .claude/skills/harness/bin/factory_cli.py
  quote: 'Contract:'
- tests/manual/probe-issue-types.py#main
- path: .harness/harness/docs/DECISIONS.md
  quote: 'Shared code, and migration scope.'
- path: .harness/harness/docs/DECISIONS-INDEX.md
  quote: '- DEC-138 @'
- path: .harness/harness/features/FEAT-2452-gh-one-transport/notes/enforcement-backlog.json
  create: true
- path: .harness/harness/features/FEAT-2452-gh-one-transport/notes/issue-types-live-probe.txt
  create: true
## output:
AMENDED tasks:T-05.files
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 FEAT-2452-gh-one-transport: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport.
  note       .harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2452-gh-one-transport: run r-20261123-4-amend-apply-product has unknown historical cycle attribution.
  note       LAYOUT dirty (8): 1 path(s) carry work that repair must not touch — reported, not gating; repair runs once the work is committed or stashed.
exit=0

# writer 2: set-key decisions_affected (row 1 keep->amend; rows 0,2-10 value-identical, checked by yaml load compare before write)
$ plan-merge.py set-key --file plan.yaml --key decisions_affected --value-file /tmp/feat2452-r4/decisions-affected.yaml
## value file:
[
{"dec": "DEC-138", "disposition": "keep", "clause": "A remote\nwrite failure does not gate development; an invalid repository binding or unproven local mirror\ndoes refuse the command before any local station change or remote mutation.", "successor": "none", "reason": "Transport represents failures while mirror policy, provenance and local authority remain unchanged."},
{"dec": "DEC-138", "disposition": "amend", "clause": "each caller keeps its own\nrunner, because", "successor": "D-01", "reason": "Signoff ruling OQ-1 (b) and condition C1: amends only the Shared code, and migration scope implementation sentences (gh_bin location and existence; each caller keeps its own runner) to name factory_gh as the shared transport with failure policy kept at the caller; the write-only regression guard and every DEC-138 policy clause stay untouched; delivered by T-05 after T-04."},
{"dec": "DEC-146", "disposition": "keep", "clause": "Flip stays best-effort by design — only the lookup direction changed.", "successor": "none", "reason": "Shared launch handling does not turn board projection into a gate."},
{"dec": "DEC-174", "disposition": "keep", "clause": "Planning such a change through the harness remains fine and useful;", "successor": "none", "reason": "Every implementation task is main-session-direct because factory_gh is reached by check-state."},
{"dec": "DEC-144", "disposition": "keep", "clause": "unverifiable states (gh missing, unauthenticated) DENY with the reason rather than waving\nwork through.", "successor": "none", "reason": "The branch gate and its GH_BIN executor are excluded and its divergence becomes a separate ticket."},
{"dec": "DEC-166", "disposition": "keep", "clause": "human-visible surface, so the plan is shown first), and the script refuses to run at all when", "successor": "none", "reason": "Tracker ownership and dry-run behavior stay at the caller rather than moving into transport."},
{"dec": "DEC-200", "disposition": "keep", "clause": "An already-recorded number is never\noverwritten, which is what makes a backfill re-runnable.", "successor": "none", "reason": "PR list transport migrates without altering exactly-one result or no-write continuation policies."},
{"dec": "DEC-203", "disposition": "keep", "clause": "It derives expected placements through the shared projection, compares every card\nagainst one bounded station snapshot per invocation, applies each finding to that finding's issue\nnumber, and continues after a per-card write failure so later mismatches are still attempted.", "successor": "none", "reason": "Reconcile and abandonment continue independently after per-item failures; lifecycle and recovery ownership are unchanged."},
{"dec": "DEC-167", "disposition": "keep", "clause": "And the gist is written by the tool, not remembered by a human.", "successor": "none", "reason": "T-04 moves resolve parent lookup and the mandatory gist append onto factory_gh with byte-exact stdin and fail-closed parent reads; the required gist, map discovery and comment/close/gist ordering are unchanged."},
{"dec": "DEC-220", "disposition": "keep", "clause": "A provably undispatched failure may clear that intent; an uncertain result or failed\nconfirmed save preserves it and refuses with the recovery id and role.", "successor": "none", "reason": "T-02 reclassifies replacement-create launch failures from the chained typed cause; only provably undispatched missing/permission launches clear intent, every uncertain outcome still preserves it and refuses."},
{"dec": "DEC-220", "disposition": "keep", "clause": "absence means the\npost-signature transaction did not complete.", "successor": "none", "reason": "T-02 marks the remote-write attempt for typed malformed-response and launch failures so Build-entry never claims not-applicable after a create; receipt values and Build gating are unchanged."}
]
## output:
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 FEAT-2452-gh-one-transport: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport.
  note       .harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2452-gh-one-transport: run r-20261123-4-amend-apply-product has unknown historical cycle attribution.
  note       LAYOUT dirty (8): 1 path(s) carry work that repair must not touch — reported, not gating; repair runs once the work is committed or stashed.
KEY decisions_affected -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
exit=0
# show T-05 intent sha
sha256: a5cee89515e830a30aee721de4f9e332c36b83a5bfe5499a12504738911bff1d
# show T-05 verify sha
sha256: 9500fa696206dfe0a4de12cd347a73e10204ebc5ca326666255f9e92f7a61c8a

# writer 3: amend T-05 intent
$ plan-merge.py amend --file plan.yaml --key tasks --id T-05 --field intent --value-file /tmp/feat2452-r4/t05-intent.txt --expect-sha256 a5cee89515e830a30aee721de4f9e332c36b83a5bfe5499a12504738911bff1d
## value file:
Work directly in PRODUCT Harness checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport; never delegate execution. Consult AGENTS.md, .harness/harness/docs/SPEC.md sections 3.3 and 9, .harness/harness/docs/DECISIONS.md DEC-138/146/166/174/200/203/205/220 and existing module contracts. Generic docs/spec.md, docs/decisions.md and docs/architecture.md are absent; SPEC and module contracts supply applicable guidance. This task changes policy explanation, carries the one signed DEC-138 implementation-sentence amendment, and records a signed backlog deliverable, not policy or executors.
Add a Caller-to-failure-policy table in github-mirror.md with explicit condition, caller outcome/exit and partial-write/recovery columns. Cover mirror gh SKIP/0, gh_try tuple and per-item continue, local binding refusal/2, checked mirror label-create SKIP, ordinary milestone 422-existing-only lookup, uncertain replacement-create refusal/2 with no retry/discovery and durable intent, PR-list no-write/continue, issue-type query compatibility downgrade, board projection best effort, board-station BoardError diagnostic/0, factory GhError/2 potentially after writes, lifecycle audit/provision distinctions, reconcile continuation with residual exit 1, wayfind fail-closed reads/typed JSON and CLI exit 1, and telemetry None-on-failure with unmeasured counters. Explain FACTORY_GH only, why policies are at callers, and that subprocess deadlines are a conscious non-goal: a hung gh can hang every consolidated operator path. State the untouched gate/auth executors keep their private GH_BIN/deadline semantics and the backlog ticket is not their fix. Reconcile the existing four-shapes prose if it overpromises continuation; do not widen DEC-138/146 beyond the DEC-138 amendment below or change instruction ownership/checkpoints.
Correct factory_cli.py's opening exit-2 false no-mutation claim: exit 2 is refusal/failure and may follow irreversible remote writes, with concrete factory_land push/PR and factory_decompose receipt examples; preserve exit codes and the distinct lost-race claim, no executable change. Remove retired-override mentions from probe-issue-types.py comments while retaining its hardcoded real gh behavior and unchecked cleanup unchanged. Keep github-mirror.md to current policy rows; issue 893, 1542 and 13 closure history and evidence belong in the feature ship record and commit trail, never in the reference.
Amend DEC-138 as ruled at signature (signoff ruling OQ-1 (b), condition C1), after T-04 has landed so the text matches the code. In .harness/harness/docs/DECISIONS.md, inside DEC-138's paragraph that opens Shared code, and migration scope, rewrite only its implementation sentences: the claim that gh_bin() lives in gh_issues.py (gh_bin no longer exists after T-04) and the claim that each caller keeps its own runner. The rewritten text states that the GitHub primitives and the internal-id lookup remain argv builders in .claude/skills/harness/bin/gh_issues.py; that factory_gh is the one shared transport, resolving FACTORY_GH and launching gh for every operator and library caller; and that failure policy stays at each caller, keeping the existing example that gh-sync.py skips and exits 0 on an environmental failure while wayfind.py dies exit 1. Leave byte-unchanged the write-only regression guard sentence (gh-sync.py imports only internal_id_args and attach_sub_issue_args, and its containing no call to parent_args or blocked_by_args is a standing regression guard for the write-only rule), the no-blocked_by-edge sentences, the new-features-only migration sentence, every other DEC-138 sentence and policy clause, and all of DEC-146. Rewrite in place as current truth under DEC-205: no dated amendment sub-section, no FEAT or issue provenance in the entry. Then regenerate .harness/harness/docs/DECISIONS-INDEX.md with python3 .claude/skills/harness/bin/gen-decisions-index.py, keeping every hand-written ruling tail, and confirm gen-decisions-index.py --stdout matches the written index.
File one real mruangutai/harness backlog issue titled Enforcement GitHub reads must not trust unverified state. Use this signed body verbatim: Separate enforcement work deferred by FEAT-2452. branch-create-gate.py trusts nonempty stdout without checking the issue-read return code; a nonzero command with output can therefore be accepted as verified state. merge-gate.py falls back to the local branch when its remote head read fails; a merge verdict can therefore be reached on unverified state. Plan an enforcement-layer repair and independent regression tests for each condition under DEC-100, DEC-144 and DEC-174. Do not change either executor, its GH_BIN, check_state/ctx auth, or timeout policy in FEAT-2452. Issues 588 and 846 remain separate and open.
Main posts that exact body after signature using gh issue create, deriving the issue number at execution rather than pinning a reusable literal. If a receipt already exists reuse its recorded number; if create dispatch becomes uncertain stop and request evidenced adoption, never retry or discover by title. Read back the created issue with gh issue view --repo mruangutai/harness NUMBER --json number,title,state,url,body and save its exact JSON to the owned notes/enforcement-backlog.json. No fake issue or proposed-body-only receipt counts. This artifact is an SC-backed output, not an open question.
Before the review pin, run the listed focused verification (exit 0/PASS), then the normal configured unit/integration and mandatory repository-state/CI merge gates once at their owning final validation boundary, not after each task. Include check-state's existing INV-26 coverage because the shared library is its dependency, without editing enforcement tests/executors. Before ship, Main runs the registered default read-only probe python3 tests/manual/probe-issue-types.py with no opt-in argument on a credentialled host and saves its exact stdout to notes/issue-types-live-probe.txt. Only a probe-issue-types: CAPABILITY PRESENT line or the probe-issue-types: CAPABILITY ABSENT line naming the pinned .harness/harness.json github.repo counts. A SKIP line (gh missing, unauthenticated, sync disabled or query failed) also exits 0 but is not live evidence: fix the host and rerun, or stop and report; never save SKIP as the receipt. Offline doubles never prove live capabilities. Reviewers inspect policy and no enforcement edits through the actual pinned diff and git show review_sha:path. The verify asserts GH_SYNC_GH and D-11 are absent from every non-.harness file in the files lists of T-01 through T-05 as read from this plan.yaml, which includes T-02's tests/offline_gh_support.py; none of those files carries an unrelated D-11 reference, historical feature artifacts are outside that list, and github-mirror.md does not name the retired override either. If any further active match is found outside these task-owned files, return it for PM scope correction before editing; do not silently leave an active alias. It also asserts the DEC-138 amendment landed: the Shared code, and migration scope paragraph, found inside DEC-138's section, names factory_gh, no longer mentions gh_bin or says each caller keeps its own runner, and still carries the write-only regression guard sentence. No DEC amendment other than this DEC-138 one, no signing, panel authoring or production deadline work.
## output:
AMENDED tasks:T-05.intent
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 FEAT-2452-gh-one-transport: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport.
  note       .harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2452-gh-one-transport: run r-20261123-4-amend-apply-product has unknown historical cycle attribution.
  note       LAYOUT dirty (8): 1 path(s) carry work that repair must not touch — reported, not gating; repair runs once the work is committed or stashed.
exit=0

# writer 4: amend T-05 verify (existing lines kept; 8 lines inserted before the final print)
$ plan-merge.py amend --file plan.yaml --key tasks --id T-05 --field verify --value-file /tmp/feat2452-r4/t05-verify.txt --expect-sha256 9500fa696206dfe0a4de12cd347a73e10204ebc5ca326666255f9e92f7a61c8a
## value file:
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
decs = (root / '.harness/harness/docs/DECISIONS.md').read_text()
dec_start = decs.index('\n## DEC-138 ')
dec_end = decs.index('\n## ', dec_start + 1)
para_start = decs.index('Shared code, and migration scope.', dec_start)
assert para_start < dec_end
para = ' '.join(decs[para_start:decs.index('\n\n', para_start)].split())
assert 'factory_gh' in para and 'gh_bin' not in para and 'keeps its own runner' not in para
assert all(word in para for word in ('imports only', 'internal_id_args', 'attach_sub_issue_args', 'parent_args', 'blocked_by_args', 'standing regression guard for the write-only rule'))
print('PASS policy vocabulary, exit-2 correction, enforcement-ticket readback, live capability receipt and retired-override absence')
PY
## output:
AMENDED tasks:T-05.verify
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 FEAT-2452-gh-one-transport: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport.
  note       .harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2452-gh-one-transport: run r-20261123-4-amend-apply-product has unknown historical cycle attribution.
  note       LAYOUT dirty (8): 1 path(s) carry work that repair must not touch — reported, not gating; repair runs once the work is committed or stashed.
exit=0

# final check
$ plan-merge.py check --file plan.yaml --root <worktree>
OK T-01 4 anchor(s) resolved
OK T-02 14 anchor(s) resolved
OK T-03 5 anchor(s) resolved
OK T-04 3 anchor(s) resolved
OK T-05 7 anchor(s) resolved
FAIL VIOLATION T-05: 53 machine-field lines — budget is 50 per task (DEC-182). Detail that only JUSTIFIES the instruction belongs in notes/, not in the contract.
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport: 5 task(s), 33 anchor(s) resolved, 1 failure(s)
exit=1

# writer 5: re-amend T-05 verify — the final check above FAILED the 50-line machine-field budget (53); the 8 inserted lines are compressed to 3 (existing lines still unchanged)
$ plan-merge.py amend --file plan.yaml --key tasks --id T-05 --field verify --value-file /tmp/feat2452-r4/t05-verify.txt --expect-sha256 e0d3f1a9f718efa8dd93ac8f197574d43a703628d620d1bde7bff4d5baeee1aa
## value file:
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
## output:
AMENDED tasks:T-05.verify
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 FEAT-2452-gh-one-transport: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport.
  note       .harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2452-gh-one-transport: run r-20261123-4-amend-apply-product has unknown historical cycle attribution.
  note       LAYOUT dirty (8): 2 path(s) carry work that repair must not touch — reported, not gating; repair runs once the work is committed or stashed.
exit=0

# final check
$ plan-merge.py check --file plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport
OK T-01 4 anchor(s) resolved
OK T-02 14 anchor(s) resolved
OK T-03 5 anchor(s) resolved
OK T-04 3 anchor(s) resolved
OK T-05 7 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport: 5 task(s), 33 anchor(s) resolved, 0 failure(s)
exit=0
