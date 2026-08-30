# Receipt — validate-crashclass-c28 — harness-backend-dev

**BLUF:** All three ASDL-optional-field guards added to `_Counter` in
`code_grade.py` (`visit_With:154`, `visit_Try:167`, `visit_AnnAssign:91`), each an inline
`if ... is not None:` matching `visit_Assert`'s existing pattern — no new abstraction. Six
literal-metric assertions added in `test-code-grade.py` (`check_optional_field_guards`),
test-first, observed RED before the fix (uncaught `AttributeError`) and GREEN after. Blast radius
16→0 crashes across all 99 `bin/*.py`. All three mutation proofs pass — removing any one guard
fails the named test `check_optional_field_guards`, restore verified byte-identical by sha256.
Self-grading clean: touched functions 5/5/5 → 5/4/5 (`visit_Try` at the bar, not below), new test
function grades 4 (bar 3), no allowlist entry. Five focused suites all exit 0. Exactly two files
touched, worktree left uncommitted, main checkout has no tracked modification.

## 1. Guards — diff (exactly the three, matching `visit_Assert`)
```
@@ -88,7 +88,8 @@ class _Counter(ast.NodeVisitor):
-        self.visit(node.value)
+        if node.value is not None:
+            self.visit(node.value)
@@ -150,7 +151,8 @@ class _Counter(ast.NodeVisitor):
-            self.visit(item.optional_vars)
+            if item.optional_vars is not None:
+                self.visit(item.optional_vars)
@@ -162,7 +164,8 @@ class _Counter(ast.NodeVisitor):
-            self.visit(handler.type)
+            if handler.type is not None:
+                self.visit(handler.type)
```
`git diff --stat`: `code_grade.py | 9 ++++--`, `1 file changed, 6 insertions(+), 3 deletions(-)`.

## 2. RED before the fix
Ran `test-code-grade.py` with the new `check_optional_field_guards` registered but before any
production edit:
```
File "code_grade.py", line 153, in visit_With
    self.visit(item.optional_vars)
  ...
  File ".../ast.py", line 273, in iter_fields
    for field in node._fields:
AttributeError: 'NoneType' object has no attribute '_fields'
```
Uncaught, exit 1 — matches the ruling's described crash exactly.

## 3. Mutation proofs (all three, one at a time, restore verified)
sha256 of the fixed file throughout: `e2fe943d...c559b8e`.
- **With**: removed guard → `check_optional_field_guards` (test-code-grade.py:656, the With
  assertion) raises the same `AttributeError`, exit 1. Restored; sha256 matched; re-run green.
- **Try**: removed guard → `check_optional_field_guards` (line 661, the Try assertion) raises,
  exit 1. Restored; sha256 matched; re-run green.
- **AnnAssign**: removed guard → `check_optional_field_guards` (line 674, the AnnAssign
  assertion) raises, exit 1. Restored; sha256 matched; re-run green.

(Note: mid-task I mistakenly ran `git checkout -- code_grade.py`, which reverted the fix to HEAD.
Caught it immediately via sha256/grep, reapplied all three guards by hand via `edit`, and
reconfirmed the diff and sha256 are identical to the original fix before proceeding. No git
commands used for any mutation/restore thereafter — plain Python file writes only.)

## 4. Blast radius
Throwaway script under `mktemp -d`, imported `code_grade`, called `grade_source` on all
`.claude/skills/harness/bin/*.py`: **before** 83 graded / 16 crashed (per QA's c27 count);
**after: 99 graded / 0 crashed**.

## 5. Metric correctness (literal, derived, matches QA section D exactly)
- `def f():\n    with lock:\n        pass\n` → `cyclomatic=1, cognitive=0, abc_a=0, abc_b=0,
  abc_c=0`. `lock` is a Load-context Name (uncounted); `optional_vars` is None (skipped); body
  only bumps depth. **Not** asserted identical to `with lock as x:` — `x` is a Store-context Name,
  which `visit_Name` counts, so the `as` form's `abc_a=1` vs. the bare form's `abc_a=0`. This
  difference is real and intentionally not asserted away.
- `def f():\n    try:\n        pass\n    except:\n        pass\n` → `cyclomatic=2, cognitive=1,
  abc_a=0, abc_b=0, abc_c=1`. `_decision()` for the handler: cyclomatic+1, c+1, cognitive+=1+0;
  `handler.name` is None so `a` stays 0; `handler.type` is None, skipped. Asserted
  metric-identical to `except Exception:` — `Exception` is a Load-context Name, uncounted, so both
  forms measure the same.
- `def f():\n    x: int\n` → `cyclomatic=1, cognitive=0, abc_a=1, abc_b=0, abc_c=0`. `node.target`
  is a Store-context Name → `a=1`; `node.value` is None, skipped. Asserted metric-identical to
  `x: int = None` — `None` is a zero-cost `Constant`, no visitor increments anything for it.
All six values measured directly against the patched engine; all matched section D and the lead's
cross-check derivation with zero discrepancy.

## 6. Self-grading — touched functions, before/after
- `visit_With`: 5 → 5 (cyclomatic 2→3, cognitive 1→3, abc 3.3→4.4; still grade 5)
- `visit_AnnAssign`: 5 → 5 (cyclomatic 1→2, cognitive 0→1, abc 2.0→2.8; still grade 5)
- `visit_Try`: 5 → 4 (cyclomatic 3→4, cognitive 2→4, abc 7.7→8.7; driver `cognitive+abc`) — at the
  bar (4), not below it.
`python3 code-grade.py code_grade.py`: 53 functions, 0 `RESULT: FAIL`, distribution
`{4: 12, 5: 41}` (baseline `{4: 11, 5: 42}` — the one `visit_Try` function moved 5→4, nothing
else shifted). Zero functions below grade 4.

## 7. New test function's own grade
`check_optional_field_guards`: `cyclomatic=1, cognitive=0, abc=14.9, GRADE=4, BAR=3` (test-file
bar). Clears the bar with margin — **no `SELF_GRADING_ALLOWLIST` entry added**.

## 8. Five focused suites
- `test-code-grade.py` → exit 0, `PASS test-code-grade`
- `test-code-grade-cli.py` → exit 0, `PASS test-code-grade-cli`
- `test-gate-policy.py` → exit 0 (all `ok` lines)
- `test-check-plan-routes.py` → exit 0, `ALL PASS`
- `test-validate-digest.py` → exit 0, `ALL PASSED.`

## 9. Scope discipline
B26 (med fail-open) and B27 (low containment item) are **untouched** — confirmed by the diff
above: exactly three inline guards, nothing else, in the two named files only.

## 10. Working tree / cleanup
- Worktree `git status --porcelain`: `M code_grade.py`, `M test-code-grade.py`, plus
  `M feature.json` and `?? answers/Q12-...md`, both pre-existing before this run (per QA's own
  c27 receipt) and untouched by me. No scratch files added anywhere in the worktree; all temp
  files (`/tmp/*`) removed.
- Main checkout `git -C /Users/molchairuangutai/GitHub/harness status --porcelain`: only
  pre-existing untracked (`??`) entries from unrelated in-flight work — **no tracked
  modification**.
- No commit made.

## 11. Send-backs
0 — no send-backs against this dispatch.

## Task-verify
No `T-NN` PLAN task was cited in this dispatch; this is a direct crash-class remediation
assignment, not a PLAN task. `task: none`.

## 12. Send-back 1 — blank-line separation
Inserted the missing second blank line before `def check_optional_field_guards():` (line 647→648)
so it matches the file's own two-blank-line convention between top-level `def`s (confirmed against
`check_direction_pairs`→`check_optional_field_guards` and every other adjacent pair in the file).
Diff is a pure insertion — `test-code-grade.py`: 1 file changed, 41 insertions(+) (was 40), no
existing line touched. `code_grade.py` side unchanged: still `1 file changed, 6 insertions(+), 3
deletions(-)`. `python3 test-code-grade.py` → `PASS test-code-grade`, exit 0.
`python3 code-grade.py test-code-grade.py`: `check_optional_field_guards` → `cyclomatic=1,
cognitive=0, abc=14.9, GRADE=4, BAR=3, RESULT: PASS` — unchanged from section 7, no
`SELF_GRADING_ALLOWLIST` entry added. Main checkout `git status --porcelain`: same pre-existing
untracked entries only, no tracked modification. No git commands run other than read-only `diff`
and `status`.
