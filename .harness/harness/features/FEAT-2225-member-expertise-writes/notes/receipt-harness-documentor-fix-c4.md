# C4-F1 — T-02 generated index repair

PASS: regeneration corrects only DEC-253's generated tags; both assigned gates went red → green. No authored source or tests changed. Branch: `feat/FEAT-2225-member-expertise-writes`.

## Commands and outcomes

Executed from the assigned feature worktree, before generation:

- `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`: exit **1**.
- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gen-decisions-index.py`: exit **1**, 11 named cases passed; `test_committed_index_matches_a_fresh_regeneration` failed because the file carried `[expertise,dispatch,worktree,map]` instead of generated `[expertise,dispatch,state,worktree]`.

Preserved red diff output:

```diff
236c236
< - DEC-253 @8178 [expertise,dispatch,state,worktree] refs: DEC-18 DEC-69 DEC-86 DEC-87 DEC-106 DEC-125 DEC-145 DEC-151 DEC-188 DEC-199 DEC-205 DEC-219 DEC-220 :: Members apply their own feature-tree Expertise; leads verify, orchestrator confirms, and authorized receipt replay precedes serialized merges retaining DEC-220 provenance checks.
---
> - DEC-253 @8178 [expertise,dispatch,worktree,map] refs: DEC-18 DEC-69 DEC-86 DEC-87 DEC-106 DEC-125 DEC-145 DEC-151 DEC-188 DEC-199 DEC-205 DEC-219 DEC-220 :: Members apply their own feature-tree Expertise; leads verify, orchestrator confirms, and authorized receipt replay precedes serialized merges retaining DEC-220 provenance checks.
```

Generator header explicitly documents no-argument writes. Ran `python3 .claude/skills/harness/bin/gen-decisions-index.py`: exit **0**. No hand edit.

Reran only the two assigned gates: index comparison exit **0**, zero output; integration exit **0**, all 12 named cases passed. No other tests or checks ran.

## Actual index diff

```diff
diff --git a/.harness/harness/docs/DECISIONS-INDEX.md b/.harness/harness/docs/DECISIONS-INDEX.md
index dbd0bb90..d66c88f3 100644
--- a/.harness/harness/docs/DECISIONS-INDEX.md
+++ b/.harness/harness/docs/DECISIONS-INDEX.md
@@ -236 +236 @@
-- DEC-253 @8178 [expertise,dispatch,worktree,map] refs: DEC-18 DEC-69 DEC-86 DEC-87 DEC-106 DEC-125 DEC-145 DEC-151 DEC-188 DEC-199 DEC-205 DEC-219 DEC-220 :: Members apply their own feature-tree Expertise; leads verify, orchestrator confirms, and authorized receipt replay precedes serialized merges retaining DEC-220 provenance checks.
+- DEC-253 @8178 [expertise,dispatch,state,worktree] refs: DEC-18 DEC-69 DEC-86 DEC-87 DEC-106 DEC-125 DEC-145 DEC-151 DEC-188 DEC-199 DEC-205 DEC-219 DEC-220 :: Members apply their own feature-tree Expertise; leads verify, orchestrator confirms, and authorized receipt replay precedes serialized merges retaining DEC-220 provenance checks.
```

## Scope and provenance

Initial and post-generation `git diff --stat` both included pre-existing run bookkeeping: feature.json (14 insertions), plan.yaml (one insertion/one deletion). Those are outside deliverables, unchanged by this repair and not staged. The only added deliverable diff is `.harness/harness/docs/DECISIONS-INDEX.md` (one insertion/one deletion), plus this receipt. DECISIONS.md, SPEC.md and review_sha were not edited. No push or gh used.

Fix commit SHA will be recorded below after the explicit-path index/receipt commit; the subsequent commit contains receipt provenance only. Open questions: none.
