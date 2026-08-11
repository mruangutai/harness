# FEAT-12 — the nine layer-0 work orders

**These are not questions. They are work the approved plan lane-locked to the main session, and
this orchestrator cannot execute them.** Written after the eng and product segments landed, at
`ff75afb`.

## Why they are not mine — measured, not assumed

| Task | Surface | What the guard says to `harness-orchestrator` |
|---|---|---|
| T-06, T-08, T-11 | `fleet.yaml`, `.claude/commands/`, rule skills, both `team-config.yaml` | `check-domain.sh` **BLOCKED, exit 2** on Write. Probed each path myself |
| T-01..T-05 | `/Users/molchairuangutai/GitHub/kaya-ai/**` | outside `CLAUDE_PROJECT_DIR`; both guards pass through, **exit 0** |
| T-09 | `$HOME/.harness/registry.json` | outside `CLAUDE_PROJECT_DIR`; guards pass through, **exit 0** |

So T-01..T-05 and T-09 are **not** mechanically blocked. They are lane-locked by the signed plan
under DEC-179, whose stated reason is that a cross-repo destructive push stays with the tier that
has an operator channel. That is a ruling, not a hook, and re-litigating it is not mine.

The `intent:` block for each task is in `plan.yaml` and is the specification. The `verify:` strings
below are verbatim so nobody has to re-open the plan to run them.

---

## Segment A — kaya-ai. Destructive, cross-repo, and the one with a live ambiguity

**Order: T-01 → (T-02, T-03) → T-04 → T-05.** Nothing in this segment touches this repository.

**BEFORE STAGING ANYTHING, resolve this. It blocks.** The dispatch that opened this ship phase says:
*"IF ANY of kaya's ~63 uncommitted entries sit under `.claude/skills/harness*` or
`.claude/commands/harness*`, STOP."* But `BRIEF.md`'s settled rulings record that **34 tracked files
under exactly those paths** carry local modifications the operator signed off on discarding. Read
literally the stop condition fires on the signed-for work and the segment can never run. Read as
intended it means *entries under those paths beyond the signed 34*. Two readings, and the cost of
guessing wrong is a permanent discard on another repository's `master`. The operator disambiguates,
not an agent.

Staging is **by explicit pathspec**. Never `git commit -a`, never `git add .`, never `git add -A`.
Keep kaya's `.harness/expertise/`, `codebase/`, `features/`, `harness.json`, `team-config.yaml`.

**D-06 is REVERSED and folds into T-03 and T-05** — remove `.claude/settings.json.harness-bak`, one
path on T-03, one entry on T-05's pathspec. It is not a new task.

### T-01 — capture the kaya `.harness` manifest before any deletion
```
test -s .harness/features/FEAT-12-end-copy-distribution/notes/kaya-harness-manifest-before.txt && awk 'END{print NR}' .harness/features/FEAT-12-end-copy-distribution/notes/kaya-harness-manifest-before.txt | awk '$1>50{exit 0} {exit 1}'
```

### T-02 — delete kaya's harness skills, slash commands and agents
`git rm -f` is authorized: `git rm` refuses a locally-modified tracked file without it, and all 34
are reproducible from this repository.
```
cd /Users/molchairuangutai/GitHub/kaya-ai && test "$(ls -1d .claude/skills/harness* 2>/dev/null | wc -l | tr -d ' ')" = 0 && test "$(ls -1 .claude/commands/harness*.md 2>/dev/null | wc -l | tr -d ' ')" = 0 && test -d .claude/agents && test "$(ls -1 .claude/agents/harness-*.md 2>/dev/null | wc -l | tr -d ' ')" = 0 && test -s /Users/molchairuangutai/GitHub/harness/.harness/features/FEAT-12-end-copy-distribution/notes/kaya-agents-count-before.txt && test "$(cat /Users/molchairuangutai/GitHub/harness/.harness/features/FEAT-12-end-copy-distribution/notes/kaya-agents-count-before.txt)" -gt 0 && test -d .claude/commands && test -f .claude/commands/review-team.md && test -d .harness/expertise && test -d .harness/codebase && test -d .harness/features && test -d .harness/artifacts && test -d .harness/notes && test -f .harness/harness.json && test -f .harness/team-config.yaml
```

### T-03 — unwire all eight harness hook registrations, and remove `settings.json.harness-bak`
Eight registrations across four hook events, not three. The four the plan first missed are the ones
a Task spawn fires — exactly what SC-06's blocking UAT exercises.
```
cd /Users/molchairuangutai/GitHub/kaya-ai && python3 -c "
import json
t = open('.claude/settings.json').read()
d = json.loads(t)
assert 'skills/harness' not in t, 'a harness skill path survives in settings.json'
assert set(d) >= {'hooks', 'env'}, 'a top-level key was lost: %s' % sorted(d)
cmds = [h['command'] for ev in d['hooks'].values() for m in ev for h in m['hooks'] if 'command' in h]
for s in ('work-tracking-nudge.sh', 'pre-commit-tests.sh', 'pr-issue-gate.sh', 'branch-issue-gate.sh'):
    assert any(s in c for c in cmds), 'a non-harness hook was lost: ' + s
assert all('.claude/hooks/' in c for c in cmds), 'a hook outside .claude/hooks/ survives: %s' % cmds
print('ok', len(cmds), 'hooks remain')
"
```

### T-04 — re-capture the manifest and prove kaya's project state is untouched
```
diff .harness/features/FEAT-12-end-copy-distribution/notes/kaya-harness-manifest-before.txt .harness/features/FEAT-12-end-copy-distribution/notes/kaya-harness-manifest-after.txt && echo IDENTICAL
```

### T-05 — commit and push to `mruangutai/kaya-ai` `master`, deletion commit only
```
cd /Users/molchairuangutai/GitHub/kaya-ai && git fetch origin master --quiet && test "$(git ls-tree -r --name-only origin/master | grep -c '^\.claude/skills/harness')" = 0 && test "$(git ls-tree -r --name-only origin/master | grep -c '^\.claude/commands/harness')" = 0 && git ls-tree -r --name-only origin/master | grep -q '^\.claude/commands/review-team.md' && echo REMOTE_CLEAN
```

---

## Segment B — this repository. Independent of segment A, and it unblocks the rest of the build

**T-06, T-08, T-09 and T-11 have no dependency on each other** except T-09 on T-07, which landed at
`e987c6d`. All four can be done in one pass.

**T-08 and T-11 are what T-14 is waiting on.** I ran T-14's own verify clause against the tree at
`ff75afb`: it returns six hits, four of them in T-08's and T-11's files
(`.claude/commands/harness-deploy.md:6`, `harness-init/SKILL.md:9`, `harness-team/SKILL.md:37`,
`templates/team-config.yaml:46`) and two in T-14's own targets. Note the plan lists T-14's
`depends_on` as `[T-10, T-11, T-12]` and **omits T-08** — measured, and it does block.

### T-06 — add `mruangutai/kaya-ai` to `.harness/factory/fleet.yaml`
`default_branch: master`, not `main`. Leave `workspace_root` alone: commit `7f29d6c` on this branch
reverted it because `~/GitHub` made this repository a hard-reset target.
```
python3 -c "import sys; sys.path.insert(0,'.claude/skills/harness/bin'); import factory_config; f=factory_config.load_fleet(); r={x['name']:x for x in f['repos']}; assert set(r)=={'mruangutai/harness','mruangutai/kaya-ai'}, r; assert r['mruangutai/kaya-ai']['default_branch']=='master'; assert r['mruangutai/harness']['default_branch']=='main'; print(factory_config.repo_entry('mruangutai/kaya-ai'))"
```

### T-08 — delete `.claude/commands/harness-deploy.md`
```
test ! -e .claude/commands/harness-deploy.md && test "$(ls -1 .claude/commands/harness*.md | wc -l | tr -d ' ')" -ge 6 && echo DELETED_AND_DOORS_INTACT
```

### T-09 — delete `$HOME/.harness/registry.json`
```
test ! -e "$HOME/.harness/registry.json" && test "$(ls -1 "$HOME/.harness"/global-harness-*-backup-2026-08-10.tgz | wc -l | tr -d ' ')" = 2 && python3 .claude/skills/harness/bin/test-check-plan-routes.py > /tmp/feat12-t09.log 2>&1; s=$?; tail -3 /tmp/feat12-t09.log; exit $s
```

### T-11 — sweep the rule skills, the templates readme and both `team-config.yaml` files
Its verify is nine clauses: four absence, five presence. The presence half is the point — it pins
the SHARP EDGE comment lines that must survive the sweep in both config files.
```
test "$(git grep -ciE 'harness-deploy|deploy\.sh|Enroll = deploy \+ init|never touches project state|distributes the tool and never|replaced wholesale on every|deploy never touches' -- .claude/skills/harness-team/SKILL.md .claude/skills/harness-init/SKILL.md .claude/skills/harness/templates/README.md .claude/skills/harness/templates/team-config.yaml .harness/team-config.yaml | wc -l | tr -d ' ')" = 0 && test "$(git grep -ciE 'it owns deploy|merge and deploy stay user-gated' -- .claude/skills/harness/templates/team-config.yaml .harness/team-config.yaml | wc -l | tr -d ' ')" = 0 && test "$(git grep -c 'SHARP EDGE (DEC-85)' -- .claude/skills/harness/templates/team-config.yaml .harness/team-config.yaml | wc -l | tr -d ' ')" = 2 && test "$(git grep -c 'bypasses path checks' -- .claude/skills/harness/templates/team-config.yaml .harness/team-config.yaml | wc -l | tr -d ' ')" = 2 && test "$(git grep -ci 'user-gated' -- .claude/skills/harness/templates/team-config.yaml .harness/team-config.yaml | wc -l | tr -d ' ')" = 2 && test "$(git grep -c 'DEC-113' -- .claude/skills/harness/templates/team-config.yaml .harness/team-config.yaml | wc -l | tr -d ' ')" = 2 && test "$(git grep -ci 'resolved first' -- .claude/skills/harness/templates/team-config.yaml .harness/team-config.yaml | wc -l | tr -d ' ')" = 2 && git grep -q '.harness/teams/' .claude/skills/harness-team/SKILL.md && test "$(ls -1 .claude/skills/harness/templates | wc -l | tr -d ' ')" -ge 10 && echo SWEPT
```

**T-11 must not edit `.harness/team-config.yaml` in any way that touches the documentor grant.**
PR #222 is open and unmerged and carries a new `harness-documentor` receipt grant on that file. A
sweep that rewrites surrounding lines will conflict with it.

---

## What comes back to a fresh orchestrator afterwards

T-14 (docs, product squad) then T-13 (the sweep test, eng squad), then the qa gate, the review
panel, the goal-check, close-out and the briefing. Re-delegate with this file's path and
`feature.yaml`. **Do not run `gh-sync.py open` again** — it already ran and recorded milestone 6,
parent 223 and fourteen sub-issues in `feature.yaml`'s `github:` block.

**One thing T-13's author must be told, measured at `ff75afb`:** `git grep -E` does **not** honour
`\b`. `git grep -cE '\bdeploy' -- docs/harness/BUILD.md` matches **nothing** while
`git grep -c 'deploy'` on the same file returns **5** and `git grep -cP '\bdeploy'` returns **5**.
T-13's case 4 says to match `DEC-12` "with a word boundary". In a Python `re` scan that is fine; via
`git grep -E` it would pass vacuously, which is the exact failure the case exists to prevent.
