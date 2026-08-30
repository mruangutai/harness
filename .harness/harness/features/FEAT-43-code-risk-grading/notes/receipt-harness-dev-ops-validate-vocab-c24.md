# Receipt — harness-dev-ops — validate-vocab-c24

**BLUF:** Both prose sites corrected to match the grade-vs-bar/severity semantics in
`code-grade.py`. Two-hunk diff, nothing else touched. All four verification scripts pass
(exit 0 before and after). No stray tracked modification anywhere; the worktree's
`feature.json` shows as modified but was NOT touched by this run (I made no edit to it).

## Tool re-verification (quoted, not summarized)

`code-grade.py:55-56`:
```
def _blocks(grade, bar):
    return grade < bar and grade != 2
```

`code-grade.py:59-62`:
```
def _severity(grade, bar):
    if _blocks(grade, bar):
        return "high"
    return "med" if grade == 2 else None
```

`code-grade.py:66`:
```
    bar = 3 if _is_test(root, grade.path) else 4
```

`code-grade.py:138-139`:
```
def _result(record):
    return "PASS" if record["grade"] >= record["bar"] else "FAIL"
```

All four claims in the dispatch match the tool exactly. Consequence confirmed: `_blocks` is true
(hence `high`) whenever `grade < bar and grade != 2`. Production bar is 4 → grade 1 or grade 3
blocks and is `high`. Test bar is 3 → only grade 1 blocks (grade 3 in a test file equals its bar,
so `grade < bar` is false — it PASSes). Grade 2 is never `high` (short-circuited to `med`)
regardless of bar. This is exactly what edit 1 now states.

## Diff (full, two hunks, nothing else)

```diff
diff --git a/.claude/skills/harness-code-risk-grading/SKILL.md b/.claude/skills/harness-code-risk-grading/SKILL.md
index 4b57fd6..8a0425d 100644
--- a/.claude/skills/harness-code-risk-grading/SKILL.md
+++ b/.claude/skills/harness-code-risk-grading/SKILL.md
@@ -10,7 +10,7 @@ Write functions that remain easy to read, change, and review. Aim for **grade 4
 production code** and **grade 3 or better in test code**. These are design bars, not an invitation
 to make unrelated cleanup changes or to split coherent logic into meaningless helpers.
 
-## Habits that keep a function under the bar
+## Habits that keep a function at or above the bar
 
 ### Return early instead of nesting
 
@@ -166,7 +166,7 @@ ratchet.
 
 ## Review semantics and self-check
 
-A grade-1 gated function is a **high** finding and fails review under the existing review rule. A
+A gated function below its bar and not grade 2 — grade 1 anywhere, or grade 3 in production — is a **high** finding and fails review under the existing review rule. A
 grade-2 function passes only with a written reason naming the function. Before review, inspect your
 changed Python functions with:
```

## Acceptance checklist

1. **Two-hunk diff, nothing else** — confirmed above. ✅
2. **Claims verified against `code-grade.py`** — quoted above, all four match. ✅
3. **`test-code-grade.py` exit status**
   - BEFORE: `PASS test-code-grade` / `BEFORE exit=0`
   - AFTER: `PASS test-code-grade` / `AFTER exit=0`
   - No difference; the worked-examples parser (split on `## Worked examples`) is unaffected
     because both edits sit above that split point. ✅
4. **`test-code-grade-cli.py` AFTER** — `PASS test-code-grade-cli` / `CLI exit=0`. ✅
5. **`sync-agent-adapters.py --check`** — exists at `.claude/skills/harness/bin/sync-agent-adapters.py`;
   ran, exit=0. ✅
6. **Worktree `git status --porcelain`**:
   ```
    M .claude/skills/harness-code-risk-grading/SKILL.md
    M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
   ```
   Only the SKILL.md modification is mine. `feature.json` was already modified before this run
   started (this run made no edit to it) — flagging per instruction to touch nothing outside
   the SKILL.md and this receipt; I did not revert it since I did not cause it and it is outside
   my writable domain to investigate/alter. ✅ (for my own edit scope)
7. **Main checkout `git status --porcelain`** — output contains only untracked (`??`) entries
   (feature/log/notes directories from concurrent runs). No tracked (` M `) modification to the
   main checkout. ✅

## Non-goals honored

No restructuring, no example changes, the four closed blockers untouched, no commit made, no
Python file touched, `.harness/glossary.md` untouched, `harness-code-review/SKILL.md` untouched.
