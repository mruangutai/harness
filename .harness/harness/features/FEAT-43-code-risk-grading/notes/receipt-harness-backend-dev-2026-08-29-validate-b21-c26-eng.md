# Receipt — harness-backend-dev — FEAT-43-code-risk-grading — validate-b21-c26 (T-B21)

## Task
T-B21: bind `_qualname` and `_strip_docstring` (`code_grade.py:343-352`) to a NAMED mutation-sensitive
test each, per `answers/Q10-b21-hold-and-fix.md`. `verify:` — the acceptance list in the dispatch
(mutation-then-restore proof, five focused suites, self-grade, diff-stat scope, clean main checkout).

## Change
One file: `.claude/skills/harness/bin/test-code-grade.py`. Added two tests beside the existing
`gated_set` fixtures (`check_changed_function_resolution` convention: inline `_git init` + two
`config` prelude, `_write`/`_commit` helpers, `code_grade.gated_set(...)` assertion on the
gated/informational qualname partition), and registered both in `main()`'s `checks` tuple.

- `check_docstring_only_rename_not_gated` (line 480) — fixture renames `documented` -> `renamed` and
  rewrites only the docstring, so the qualname lookup misses and resolution must fall through to the
  body hash. Asserts `gated == set()`, `informational == {"renamed"}`.
- `check_method_qualname_collision_pre_images` (line 511) — one module template, only variable is a
  top-level function's name (`run` at base, `dispatch` at head), plus `Alpha.run`/`Beta.run` methods
  of the same bare name. Asserts `gated == set()`,
  `informational == {"Alpha.run", "Beta.run", "dispatch"}`.

## Mutation proof

### `_strip_docstring` -> `return body`
Applied to `code_grade.py:347-351`, ran the suite:
```
FAIL docstring-only rename gated set: expected set(), got {'renamed'}
FAIL docstring-only rename informational set: expected {'renamed'}, got set()
2 failures
EXIT:1
```
Restored `_strip_docstring` byte-identically (edited back the original 5-line body). Confirmed via
`git status --porcelain -- code_grade.py` → empty, then suite:
```
PASS test-code-grade
EXIT:0
```

### `_qualname` -> `return name`
Applied to `code_grade.py:343-344`, ran the suite:
```
FAIL qualname collision gated set: expected set(), got {'dispatch'}
FAIL qualname collision informational set: expected {'Alpha.run', 'dispatch', 'Beta.run'}, got {'Alpha.run', 'Beta.run'}
2 failures
EXIT:1
```
Clean named failures — no `KeyError`/traceback, confirming the top-level-function-collision fixture
avoids the `by_name[qualname]` KeyError the dispatch warned about. Restored `_qualname` byte-
identically. Confirmed via `git status --porcelain -- code_grade.py` → empty, then suite:
```
PASS test-code-grade
EXIT:0
```

## Self-grade
`python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/test-code-grade.py`:
- `check_docstring_only_rename_not_gated` — GRADE 4, RESULT PASS
- `check_method_qualname_collision_pre_images` — GRADE 4, RESULT PASS
- `check_method_qualname_collision_pre_images.source` — GRADE 5, RESULT PASS
- New-qualname count below bar: **0**
- Pre-existing failures unrelated to this change and untouched by it: `check_commit_resolution`
  (GRADE 2) and `check_changed_function_resolution` (GRADE 2) — both existed before this cycle; out
  of B21's enumerated scope.

`python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/code_grade.py`:
`PASSING: 53`, every listed function `RESULT: PASS` — unchanged, file untouched.

## Focused suites (all five, exit 0)
- `test-code-grade.py` → `PASS test-code-grade`, EXIT:0
- `test-code-grade-cli.py` → `PASS test-code-grade-cli`, EXIT:0
- `test-gate-policy.py` → all `ok`, EXIT:0
- `test-check-plan-routes.py` → `ALL PASS`, EXIT:0
- `test-validate-digest.py` → `ALL PASSED.`, EXIT:0

## Scope confirmation
- `git -C <worktree> diff --stat` shows two paths: `test-code-grade.py` (mine, 68 insertions/0
  deletions) and `.harness/harness/features/FEAT-43-code-risk-grading/feature.json` (4 lines,
  NOT touched by this agent — a concurrent sibling, `Feat43B21C26`, is checkpointing in the same
  worktree per the hub roster). No other file under this agent's control changed.
- `git -C /Users/molchairuangutai/GitHub/harness status --porcelain` — every line is untracked
  (`??`); zero tracked modifications (`M`) in the main checkout.
- No scratch files created; working tree left uncommitted.

## Result
Both branches now fail a named test under their mutation and pass cleanly against the correct
engine. `code_grade.py` is byte-identical to HEAD.
