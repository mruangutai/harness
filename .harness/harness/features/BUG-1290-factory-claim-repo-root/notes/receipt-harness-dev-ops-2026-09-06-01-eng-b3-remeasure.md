# BUG-1290 · B-3 independent re-measurement · harness-dev-ops

**Verdict: all eight items reproduced, all consistent with the claimed fix. No repository file was
changed by this run; only this receipt was written.**

WT = `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root`

## 1. Unit suite

```
cd $WT && python3 tests/unit/test-factory-claim.py; echo "exit=$?"
```
Final line: `124/124 checks passed.` — `exit=0`.
`grep -c '^FAIL '` on captured output: **0**.

5a-5f lines (all `ok`):
```
ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
ok    BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
ok    BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
ok    BUG-1290 5d: owner-qualified name ending in harness resolves to .harness/harness/features
ok    BUG-1290 5e: factory_claim exposes no FEATURES_ROOT attribute
ok    BUG-1290 5f: the owner-strip derivation lives in exactly one place, factory_config.py
```
**PASS** — matches expectation (124/124, exit 0, zero FAILs, all six 5x cases green).

## 2. Integration suite

```
cd $WT && python3 tests/integration/test-factory-integration.py; echo "exit=$?"
```
Tally: `131/131 checks passed.` — `exit=0`.
**PASS** (full green, no regression from the fixture change).

## 3. Probe M1 (plan-cache mutant)

```
python3 /tmp/bug1290_probe_m1.py $WT
```
```
ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
ok    BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
```
**PASS** — 5b reddens, 5a/5c stay green, exactly as expected.

## 4. Probe M2 (issue-map-cache mutant)

```
python3 /tmp/bug1290_probe_m2.py $WT
```
```
ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
ok    BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
```
**PASS** — identical pattern to M1, exactly as expected.

## 5. Pre-edit control (the whole claim of this cycle)

Read-only reproduction: no repository file touched. Built a `/tmp` scratch overlay
(`/tmp/b3-remeasure/scratch/`) consisting of:
- `tests/unit/test-factory-claim.py` = `git -C $WT show HEAD:tests/unit/test-factory-claim.py`
  (HEAD's committed fixture — the fixture change under test is an *uncommitted* working-tree edit,
  confirmed in item 6, so `git show HEAD:...` is genuinely the pre-edit file, not a stale ref).
- `.claude/skills/harness/bin` → symlink to the worktree's own live bin dir (so the mutant patches
  the real, current production module — the seam under test, not a frozen copy).

Ran the M2 probe's own mutant-install/run/restore logic (copied verbatim from
`/tmp/bug1290_probe_m2.py`, only `TEST_PATH`/`BIN_DIR` parameterized) against this scratch
worktree, with `HARNESS_PROJECT_DIR=$WT` so `harness_boundary.resolve_root` locates the real
`.harness/team-config.yaml` (required for `factory_config` to load; this is the "resolves its
production seam from the worktree's live bin" the dispatch anticipated):

```
HARNESS_PROJECT_DIR=$WT python3 /tmp/b3-remeasure/probe_m2_preedit.py /tmp/b3-remeasure/scratch
```
```
ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
ok    BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
ok    BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
```
**PASS** — against the PRE-EDIT fixture the M2 mutant reddens NOTHING: 5a, 5b, 5c all `ok`. This
is the expected result and it is the load-bearing evidence for the whole cycle: the fixture change
is what makes 5b a real discriminator for the M2 mutant. 5b did NOT already redden pre-edit, so
this cycle closed a real gap.

Scratch dir and probe copy are under `/tmp/b3-remeasure/`; nothing under `$WT` was modified to
produce this result.

## 6. Working-tree diff scope

```
cd $WT && git status --porcelain
```
```
 M .harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json
 M .harness/harness/features/BUG-1290-factory-claim-repo-root/observations/harness-backend-dev.md
 M .harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml
 M tests/unit/test-factory-claim.py
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/answers-2026-09-06-b3.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-backend-dev-2026-09-06-01-eng-b3.md
```
```
git -C $WT diff --stat
```
```
 .../BUG-1290-factory-claim-repo-root/feature.json  |  2 +-
 .../observations/harness-backend-dev.md            |  6 ++++++
 .../BUG-1290-factory-claim-repo-root/plan.yaml     |  4 ++--
 tests/unit/test-factory-claim.py                   | 23 +++++++++++++---------
 4 files changed, 23 insertions(+), 12 deletions(-)
```
**No path outside `tests/` and outside
`.harness/harness/features/BUG-1290-factory-claim-repo-root/` appears as modified.** Every changed
or new path falls in one of those two scopes.

`plan.yaml` diff:
```
diff --git a/.harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml b/.harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml
index 261c273e..df0adde7 100644
--- a/.harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml
+++ b/.harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml
@@ -4,7 +4,7 @@ approval:
   date: '2026-09-05'
   approved_by: mruangutai
   status: approved
-status: review
+status: building
 source_issues: [1290]

 lanes:
@@ -268,7 +268,7 @@ tasks:
     execution_mode: team
     execution_agent: harness-backend-dev
     depends_on: []
-    status: done
+    status: building
     files:
       - tests/unit/test-factory-claim.py
     verify: |
```
Only two `status:` scalars changed (feature-level `review`→`building`, task-level `done`→`building`)
— bookkeeping/panel fields. **No task's `verify:` block or `intent:` text changed.**
**PASS** — the plan was not amended in substance, only re-opened for this cycle's re-measurement.

## 7. Probe fidelity — `.claude/skills` vs `.agents/skills`

```
ls -l $WT/.claude/skills
```
Shows `.claude/skills/harness/` as a real directory (not a symlink into `.agents/skills`) —
confirmed also by `readlink $WT/.claude/skills/harness` returning nothing (not a symlink).

```
cmp $WT/.claude/skills/harness/bin/factory_claim.py $WT/.agents/skills/harness/bin/factory_claim.py; echo "cmp=$?"
```
`cmp=0` — **the two files are byte-identical.** Both probes (which import from
`.claude/skills/harness/bin`) are measuring the same `factory_claim.py` content as the production
path at `.agents/skills/harness/bin`. **PASS** — items 3-5 are not invalidated by a module
mismatch.

## 8. Worktree HEAD

```
git -C $WT rev-parse --short HEAD
```
`53a5d658`

---

## Summary judgement

All eight items reproduced exactly as expected; nothing contradicts the fix's claim. Item 5 (the
pre-edit control) is the load-bearing one and it confirms the whole cycle's premise: pre-edit, the
M2 mutant reddened nothing; post-edit (item 4), it reddens exactly 5b. Item 7 confirms the probes
are measuring the real production module. Item 6 confirms the diff stayed inside `tests/` and the
feature directory, and that `plan.yaml`'s substantive fields (verify/intent) were untouched — only
bookkeeping `status:` scalars moved.
