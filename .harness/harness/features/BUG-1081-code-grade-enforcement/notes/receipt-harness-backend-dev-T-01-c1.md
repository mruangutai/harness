# Receipt — T-01 — harness-backend-dev — c1

## Seam (for T-02)

- Module: `.claude/skills/harness/bin/code_grade.py`
- Function: `code_grade.classify(grades, test_kinds)`
  - `grades`: any iterable of `code_grade.FunctionGrade` (e.g. `gated_set()`'s first return
    element, or `grade_source()`'s return).
  - `test_kinds`: the caller's already-parsed active `test_kinds` policy (harness.json's
    `"test_kinds"` mapping). The seam never opens `.harness/harness.json` and never reads
    ambient cwd.
  - Returns `(records, result)`:
    - `records`: `list[dict]`, one per input grade, each carrying `path`, `line`, `qualname`,
      `cyclomatic`, `cognitive`, `cognitive_method`, `abc`, `grade`, `driver`, `bar`,
      `severity` (`"high"` / `"med"` / `None`), `result` (`"PASS"` / `"FAIL"`) — every field
      `code-grade.py`'s CLI renders, computed once.
    - `result`: `str`, one of `"fail"` / `"grade_2"` / `"pass"` — the mixed-precedence
      summary over `records`: `"fail"` if any record blocks (`grade < bar and grade != 2`),
      else `"grade_2"` if any record graded exactly 2, else `"pass"`. Never `"n_a"` —
      that discrimination belongs to the caller (T-02).
- Named error: `code_grade.TestKindsError` — subclasses `ValueError` (so `code-grade.py`'s
  existing `except ValueError -> parser.error` catch site keeps working unchanged). Raised by
  the seam when `test_kinds` is missing (`None`, not a mapping) or malformed (an active kind
  entry is not a mapping, or is missing `"detect"`) — evaluated lazily, only when at least one
  record actually needs the bar resolved.
- Bars preserved exactly: active-test bar 3, production bar 4. Blocking rule preserved exactly:
  `_blocks(grade, bar) = grade < bar and grade != 2` (grade 2 is reasoned, not blocking).

## Move, not copy

`code-grade.py` no longer defines `_patterns`, `_is_test`, `_blocks`, `_severity`, `_record`,
or `_result` — all moved into `code_grade.py`. `grep -n "bar" code-grade.py` shows only
rendering/aggregation uses of an already-computed `record["bar"]` (BAR: line, PASSING: count,
JSON), no second `3 if ... else 4` definition; `grep "!= 2"` finds no match in `code-grade.py` —
the `grade != 2` predicate lives only in `code_grade._blocks`. `code-grade.py`'s own
`record["grade"] == 2` check in `_text` is purely presentational (whether to print
`REASON REQUIRED:`), not a re-derivation of blocking.

`code-grade.py`'s CLI now loads `test_kinds` once via a new `_load_test_kinds(root)` helper and
threads it through `_diff_report(root, base, head, test_kinds)` and
`_paths_report(root, paths, test_kinds)`, both of which call `code_grade.classify(...)` and
return its `records` unchanged. `_status` now derives the exit-1 condition from
`record["severity"] == "high"` (equivalent to the old `_blocks` call, since severity `"high"`
is defined as exactly the blocking case) instead of re-implementing `_blocks`. `_text` renders
`record["result"]` directly instead of calling a local `_result`.

## RED-first evidence (both groups, before any production edit)

Procedure: staged the finished production edits aside, `git checkout --` reset
`code_grade.py`/`code-grade.py` to the pre-fix committed content, added/updated the tests, ran
both suites against the **unmodified** production code, then restored the staged production
files and re-ran to green.

**Unit (`test-code-grade.py`)** — `python3 .claude/skills/harness/bin/test-code-grade.py`
against unmodified production aborted with:
```
File "test-code-grade.py", line 269, in _check_self_graded_file
    bar = 3 if code_grade._is_test_path(relative, test_kinds) else 4
AttributeError: module 'code_grade' has no attribute '_is_test_path'
```
This is `check_self_grading`, the first check in the tuple reaching the new API — correct
reason (seam doesn't exist yet). The four new direct-call checks were verified individually
(module-exec, bypassing the abort) against the unmodified production module:
```
check_classify_bars                     RED: AttributeError module 'code_grade' has no attribute 'classify'
check_classify_grade_two_is_reasoned    RED: AttributeError module 'code_grade' has no attribute 'classify'
check_classify_precedence               RED: AttributeError module 'code_grade' has no attribute 'classify'
check_classify_rejects_bad_test_kinds   RED: AttributeError module 'code_grade' has no attribute 'TestKindsError'
```

**Integration (`test-code-grade-cli.py`)** — `python3 .claude/skills/harness/bin/test-code-grade-cli.py`
against unmodified production aborted with:
```
File "test-code-grade-cli.py", line 280, in test_diff_and_determinism
    left, head, "HEAD", code_grade_cli._load_test_kinds(left))
AttributeError: module 'code_grade_cli' has no attribute '_load_test_kinds'
```
`test_diff_paths_complexity` (reached after the abort point in the full run) verified
individually against unmodified production — 16 named-assertion failures, all for the intended
reason (moved functions not yet present in `code_grade.py`; old functions not yet removed from
`code-grade.py`):
```
FAIL _load_test_kinds present in code-grade.py: expected True, got False
FAIL _load_test_kinds grades 4 or better: expected True, got False
FAIL _record moved out of code-grade.py, not duplicated: expected False, got True
FAIL _severity moved out of code-grade.py, not duplicated: expected False, got True
FAIL _blocks moved out of code-grade.py, not duplicated: expected False, got True
FAIL _is_test moved out of code-grade.py, not duplicated: expected False, got True
FAIL _result moved out of code-grade.py, not duplicated: expected False, got True
FAIL _patterns moved out of code-grade.py, not duplicated: expected False, got True
FAIL classify present in code_grade.py: expected True, got False
FAIL classify grades 4 or better: expected True, got False
FAIL _is_test_path present in code_grade.py: expected True, got False
FAIL _is_test_path grades 4 or better: expected True, got False
FAIL _severity present in code_grade.py: expected True, got False
FAIL _severity grades 4 or better: expected True, got False
FAIL _blocks present in code_grade.py: expected True, got False
FAIL _blocks grades 4 or better: expected True, got False
```
16 failures, all named, all for the intended reason.

After restoring the staged production edits: `test-code-grade.py` → `PASS test-code-grade`
(exit 0); `test-code-grade-cli.py` → `PASS test-code-grade-cli` (exit 0). No allowlist grade
drifted — `check_self_grading` passed unmodified on the first green run, so
`SELF_GRADING_ALLOWLIST` (including `("code-grade.py", "main"): 2`) needed no edits.

## Mutation proof

Restore method for both: `md5` before mutating, hand-restore the exact original file content
from the staged copy, re-`md5` to confirm, confirm absence from `git status --porcelain`.
`code_grade.py` md5 before both mutations and after both restores:
`925af35ffd24d494e05db78085c5c5dd` (unchanged).

**Mutation A — flip fail-over-grade_2 precedence** (swap the `if`/`elif` order in
`code_grade.classify` so grade-2 is checked, and wins, before blocking):
```
FAIL a blocking record beats a simultaneous grade-two record: expected 'fail', got 'grade_2'
1 failures
```
Exactly `check_classify_precedence` reddened, for the intended reason. `test-code-grade-cli.py`
was not separately re-run against this mutation (it never asserts the seam's aggregate
`"fail"`/`"grade_2"`/`"pass"` string — the CLI only renders per-record fields — so an unpredicted
CLI redness/greenness on this particular mutation is expected and was not treated as a finding).

**Mutation B — treat grade 2 as blocking** (`_blocks(grade, bar): return grade < bar`, dropping
`and grade != 2`):
```
test-code-grade.py:
FAIL grade two is reasoned, not blocking: expected 'med', got 'high'
FAIL grade two alone classifies grade_2, not fail: expected 'grade_2', got 'fail'
2 failures

test-code-grade-cli.py:
FAIL text field SEVERITY: med: expected True, got False
FAIL json severity: expected 'med', got 'high'
FAIL grade two authorization is nonblocking: expected 0, got 1
FAIL diff grade two authorization exit: expected 0, got 1
FAIL checks/grade-two.py boundary exit: expected 0, got 1
FAIL checks/grade-two.py bar-relative severity present: expected True, got False
FAIL checks/grade-two.py JSON boundary exit: expected 0, got 1
FAIL checks/grade-two.py JSON bar-relative severity: expected 'med', got 'high'
```
Both the new unit precedence assertions **and** the pre-existing CLI grade-2-nonblocking
assertions reddened — confirming the precedence rule is enforced at both the unit (seam) level
and observably through the CLI surface, not only in one.

Both mutations reverted; hash-confirmed identical to the pre-mutation file; re-ran both suites
green after each restore.

## Final verify (verbatim commands from T-01)

```
.agents/skills/harness/bin/run-unit-tests.sh --kind unit
```
Exit status: **0**. `grep -c "^FAIL "` on captured output: **0**. `test-code-grade.py` present
in the run (`PASS test-code-grade.py` at line 1435 of the captured log).

```
.agents/skills/harness/bin/run-unit-tests.sh --kind integration
```
Exit status: **0**. `grep -c "^FAIL "` on captured output: **0**. `test-code-grade-cli.py`
present in the run (`PASS test-code-grade-cli.py` at line 1946 of the captured log).

Both re-run a second time after the mutation-proof restores, with identical results (exit 0,
zero FAIL lines, both scripts present), to confirm the final on-disk state is the one verified.

## `git status --porcelain`

```
 M .claude/skills/harness/bin/code-grade.py
 M .claude/skills/harness/bin/code_grade.py
 M .claude/skills/harness/bin/test-code-grade-cli.py
 M .claude/skills/harness/bin/test-code-grade.py
 M .harness/harness/features/BUG-1081-code-grade-enforcement/feature.json
 M .harness/harness/features/BUG-1081-code-grade-enforcement/plan.yaml
?? .harness/harness/features/BUG-1081-code-grade-enforcement/STATE.md
?? .harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-backend-dev-T-01-c1.md
```
The four named source files are the only ones I edited. `feature.json`, `plan.yaml`, and the
untracked `STATE.md` were not touched by this task and are outside my domain (concurrent
orchestrator/lead activity) — reported per observation, not investigated or reverted.

## Test obligations checklist (per dispatch)

- Direct bar/precedence assertions live in `test-code-grade.py` (unit): `check_classify_bars`
  (test path → bar 3, production path → bar 4), `check_classify_grade_two_is_reasoned` (grade 2
  reasoned not blocking), `check_classify_precedence` (blocking beats grade 2; empty set →
  pass), `check_classify_rejects_bad_test_kinds` (missing/malformed `test_kinds` →
  `TestKindsError`).
- CLI text/JSON/severity/exit-status/sort-order behavior preserved and asserted unchanged in
  `test-code-grade-cli.py` (pre-existing tests, all still pass byte-for-byte).
