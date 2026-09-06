# Receipt — harness-backend-dev — T-04 — c1

## Task
Retarget layout_migration.READER_TABLE's factory_claim.py row onto factory_config.py
(D-04), rename the layout_fixtures.STUB key in the same edit, and reword case 22's
comment in tests/integration/test-layout-migration.py. No assertion changed.

## Anchor drift
Plan anchors (row at layout_migration.py:92-94, STUB at layout_fixtures.py:45-48,
case 22 comment at test-layout-migration.py:422-425, case 22 check at :426-429) all
matched the actual file content at time of edit — no drift from the plan's cited
line numbers.

## Changes (all three permitted files, no others)
1. `.claude/skills/harness/bin/layout_migration.py` (hardlinked to
   `.agents/skills/harness/bin/layout_migration.py`, same inode both before and
   after): moved the `factory_claim.py` row to `.agents/skills/harness/bin/factory_config.py`,
   keeping both patterns character-for-character (`'"\.harness", "features"'` legacy,
   `'"\.harness", [^,)]+, "features"'` migrated — NOT widened), the trailing
   `# balance: (` comment, and adding a new comment explaining the move (vs. FEAT-42's
   removal precedent immediately below it).
2. `.claude/skills/harness/bin/layout_fixtures.py` (hardlinked to
   `.agents/.../layout_fixtures.py`, same inode both before and after): renamed the
   STUB key from `factory_claim.py` to `factory_config.py` in the same edit; legacy
   fragment `def features_root(repo_name):\n    return os.path.join(r(), ".harness", "features")\n`
   matches only the legacy pattern; migrated fragment
   `def features_root(repo_name):\n    seg = segment_of(repo_name)\n    return os.path.join(r(), ".harness", seg, "features")\n`
   matches only the migrated pattern (uses `seg`, the same paren-free local name
   T-03's real `factory_config.features_root` binds at factory_config.py:395).
3. `tests/integration/test-layout-migration.py`: reworded case 22's comment
   (:421-426 after the edit) to name `factory_config.py` instead of `factory_claim.py`
   as the features reader, and to note the row move. No assertion touched (:427-430
   unchanged verbatim).

Confirmed no widening: T-03's `factory_config.features_root` (factory_config.py:390-396)
binds `seg = segment_of(repo_name)` as a paren-free local before the join, exactly as
D-04/A-01 require — the unwidened migrated pattern `"\.harness", [^,)]+, "features"`
matches it, verified by the probe below. No T-03 defect found.

## Hardlink verification
Before and after every edit:
```
stat -f '%i' .agents/skills/harness/bin/layout_migration.py .claude/skills/harness/bin/layout_migration.py
203802737
203802737
stat -f '%i' .agents/skills/harness/bin/layout_fixtures.py .claude/skills/harness/bin/layout_fixtures.py
203802736
203802736
```
Both pairs share one inode throughout; no restore was needed.

## Tool anomaly encountered (worked around, recorded in observations log)
Two successive `edit` tool calls against `.claude/skills/harness/bin/layout_migration.py`
reported success — including a `read`/`grep` immediately after showing the new
content — but an independent `bash` check moments later (`sed`, `md5sum`,
`stat -f %m`) showed the on-disk bytes and mtime completely unchanged from before
either edit, and a fresh `read` also reverted to the stale pre-edit content and tag.
A retried `edit` was then rejected as stale against the tool's own (unpersisted)
internal snapshot. No concurrent process (rebase, sibling agent, hub job) was found
touching these files in the same window (checked `git reflog`, `hub jobs`, mtimes).
Worked around by applying the identical change via `bash`/`python3` in-place string
replacement, which persisted correctly on every subsequent check. Could not file via
`xd://report_issue` — check-domain blocks this agent from that path in this worktree;
recorded in the observations log instead so it isn't lost.

## Verify — ran verbatim, cross-checked against plan.yaml T-04 `verify:` (:481-507),
matches exactly.
```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root && python3 tests/integration/test-layout-migration.py && python3 -c "
import sys, re; sys.path.insert(0, '.claude/skills/harness/bin')
import layout_migration as lm
R = [r for r in lm.READER_TABLE if r.surface == 'features']
P = [r.path for r in R]
T = '.agents/skills/harness/bin/factory_config.py'
row = [r for r in R if r.path == T]
d = dict(lm.scan('.').surfaces['features'].readers)
L = 'os.path.join(H, \".harness\", \"features\")'
M = 'os.path.join(H, \".harness\", seg, \"features\")'
ok = (len(R) == 5 and '.agents/skills/harness/bin/factory_claim.py' not in P and len(row) == 1
      and d.get(T) == 'migrated'
      and re.search(row[0].legacy, L) and not re.search(row[0].legacy, M)
      and re.search(row[0].migrated, M))
print('READER ROW PROBE:', 'ok' if ok else 'FAIL', len(R), d)
sys.exit(0 if ok else 1)
"
```
Actual output (verbatim, tail):
```
ok   - case 21: real root's harness/docs surface is CLEAN with migrated evidence
ok   - case 22: real root's harness/features surface is CLEAN with migrated evidence
READER ROW PROBE: ok 5 {'.harness/team-config.yaml': 'migrated', '.agents/skills/harness/bin/check-domain.sh': 'migrated', '.agents/skills/harness/bin/check-plan-routes.py': 'migrated', '.agents/skills/harness/bin/factory_config.py': 'migrated', '.agents/skills/harness/bin/check-state.sh': 'migrated'}
```
All 22 cases + all sub-checks `ok`, no `FAIL` lines. Exit code: 0.

## Acceptance checklist
- [x] Features surface keeps exactly 5 reader rows; `factory_claim.py` absent;
      `factory_config.py` present exactly once, classifies `migrated` on the real tree.
- [x] Neither pattern widened; T-03's resolver text checked directly and is paren-free.
- [x] STUB key renamed in the same edit; legacy/migrated fragments each match only
      their own form.
- [x] Case 22's comment reworded; no assertion changed (diff confined to the comment
      block).
- [x] Verify ran verbatim, exited 0.
- [x] Hardlinks intact for both bin files (inodes above).
- [x] Only the three named files changed (`git status --porcelain` shows no other
      new modifications from this task; the other modified files are pre-existing
      from T-01/T-02/T-03, not touched here).

## files_touched
- .agents/skills/harness/bin/layout_migration.py (hardlink of .claude/skills/harness/bin/layout_migration.py)
- .agents/skills/harness/bin/layout_fixtures.py (hardlink of .claude/skills/harness/bin/layout_fixtures.py)
- tests/integration/test-layout-migration.py
