# Receipt — harness-backend-dev — CR-01 core-layer remediation (wave 1 of 3)

Task IDs: T-01 (code_grade.py), T-07 (gate_policy.py), T-09 (check-plan-routes.py).
Verify commands overridden per operator authorization
(`.harness/harness/features/FEAT-43-code-risk-grading/answers/Q6-cycle-20-remediation-authorization.md`):
ran the three focused test files directly instead of `run-unit-tests.sh --kind unit/integration`.

## What changed

Reduced cognitive complexity on the five grade-3 PRODUCTION functions named in dispatch, all now
grade 4 or 5. No grade band, metric definition, `test_kinds`, or bar was touched. Behaviour
preserved byte-for-byte: same signatures, same exceptions/attributes, same message strings, same
return shapes.

| file | function | before | after helpers extracted | after grade |
|---|---|---|---|---|
| `code_grade.py:229` (was 232) | `_records.collect` | cog 11, grade 3 | `_child_qualname` (module-level, grade 5) | grade 4 (cog 6) |
| `code_grade.py:329` (was 318) | `_changed_python_files` | cog 11, grade 3 | `_next_paths` (grade 5) | grade 4 (cog 8) |
| `gate_policy.py:61` (was 33) | `load_policy` | cog 11, grade 3 | `_load_config` (grade 5), `_require_gates` (grade 5), `_resolve_gate` (grade 4) | grade 5 (cog 0) |
| `gate_policy.py:93` (was 75) | `evaluate_qa` | cog 10, grade 3 | `_validate_suites` (grade 4) | grade 4 (cog 5) |
| `check-plan-routes.py:119` (was 91) | `resolution_manifest` | cog 11, grade 3, driver cognitive+abc | `_owner_root` (grade 4), `_manifest_deviation` (grade 4) | grade 5 (cog 0) |

Every extraction follows the split the dispatch suggested: `load_policy` separated per-gate
resolution (`_resolve_gate`, called once per `GATE_VOCABULARIES` entry) from config-loading
(`_load_config`) and shape validation (`_require_gates`); `evaluate_qa` separated per-suite
validation/skip-collection (`_validate_suites`) from verdict assembly; `resolution_manifest`
separated owner-checkout resolution (`_owner_root`) from the manifest-comparison/deviation message
(`_manifest_deviation`). `_records.collect` and `_changed_python_files` each had their branchy
per-item dispatch pulled into a small named predicate/parser (`_child_qualname`, `_next_paths`),
turning the surrounding loop body into a guard-clause + single dispatch call.

Each extracted helper earns its keep under the deletion test: removing `_resolve_gate` would put
the try/except KeyError + vocabulary-membership check straight back at the call site in a
comprehension it can't hold cleanly; removing `_manifest_deviation` would put the two-stage
realpath/byte-compare check back inline in `resolution_manifest`, re-adding exactly the nesting
that made it grade 3.

## Paths-mode grading — every named function and every helper it graded 4 or better

```
python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/code_grade.py
```
- `_child_qualname`: CYCLOMATIC 2, COGNITIVE 2, ABC 3.2, **GRADE 5**
- `_records.collect`: CYCLOMATIC 4, COGNITIVE 6, ABC 7.5, **GRADE 4** (driver: cognitive)
- `_next_paths`: CYCLOMATIC 2, COGNITIVE 1, ABC 4.1, **GRADE 5**
- `_changed_python_files`: CYCLOMATIC 5, COGNITIVE 8, ABC 11.0, **GRADE 4**

```
python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/gate_policy.py
```
- `_load_config`: CYCLOMATIC 2, COGNITIVE 1, ABC 3.7, **GRADE 5**
- `_require_gates`: CYCLOMATIC 3, COGNITIVE 2, ABC 4.7, **GRADE 5**
- `_resolve_gate`: CYCLOMATIC 4, COGNITIVE 4, ABC 6.2, **GRADE 4** (driver: cognitive)
- `load_policy`: CYCLOMATIC 2, COGNITIVE 0, ABC 5.0, **GRADE 5**
- `_validate_suites`: CYCLOMATIC 4, COGNITIVE 5, ABC 7.7, **GRADE 4** (driver: cognitive)
- `evaluate_qa`: CYCLOMATIC 5, COGNITIVE 5, ABC 10.3, **GRADE 4**

```
python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/check-plan-routes.py
```
- `_owner_root`: CYCLOMATIC 4, COGNITIVE 4, ABC 7.5, **GRADE 4** (driver: cognitive)
- `_manifest_deviation`: CYCLOMATIC 5, COGNITIVE 6, ABC 14.2, **GRADE 4**
- `resolution_manifest`: CYCLOMATIC 1, COGNITIVE 0, ABC 2.8, **GRADE 5**

Paths-mode exit status was NOT used as acceptance (it also grades untouched pre-existing
functions and is legitimately non-zero for reasons outside this batch's scope); acceptance is the
per-qualname `GRADE` lines above, and is also pinned by the new `check_self_grading()` assertions
in `test-code-grade.py` (one `check(...)` per qualname, by name).

## Focused test suites — all three pass by name

- `python3 .claude/skills/harness/bin/test-code-grade.py` → `PASS test-code-grade`, exit 0.
- `python3 .claude/skills/harness/bin/test-gate-policy.py` → all 27 named `ok` cases, exit 0
  (includes 4 new/renumbered QA/review cases unaffected; extraction changed nothing observable).
- `python3 .claude/skills/harness/bin/test-check-plan-routes.py` → `ALL PASS`, exit 0, including
  `case_27a_owner_manifest_controls_routes`, `case_27b_prior_revision_false_ok`,
  `case_27c_unreadable_owner_manifest_refuses` (the three cases that exercise
  `resolution_manifest`/`_owner_root`/`_manifest_deviation` directly).

## Test-first record

For each of the five functions the failing-first record is the grade assertion added to
`test-code-grade.py`'s new `check_self_grading()` (the strong existing suites already pinned
behaviour completely, so per the dispatch's preferred form this is a grade-by-qualname check, not
a new behavioural test):

- Ran `python3 .claude/skills/harness/bin/test-code-grade.py` against the pre-edit source with the
  new checks added: **13 failures**, one `FAIL ... grade >= 4` per target function
  (`_records.collect`, `_changed_python_files`, `load_policy`, `evaluate_qa`,
  `resolution_manifest`) plus one `FAIL ... exists` per not-yet-created helper
  (`_child_qualname`, `_next_paths`, `_load_config`, `_require_gates`, `_resolve_gate`,
  `_validate_suites`, `_owner_root`, `_manifest_deviation`). Confirmed RED.
- After each extraction, re-ran the same file: 0 failures, `PASS test-code-grade`. Confirmed GREEN.

## Mutation proof (required, one performed)

Target: `gate_policy._validate_suites` (extracted from `evaluate_qa`).

1. Mutated line 88 from `if outcome == "skipped":` to `if outcome != "skipped":` (one-character
   comparison flip).
2. Ran `python3 .claude/skills/harness/bin/test-gate-policy.py`:
   named case **`QA detail reports skipped suite`** FAILED —
   `expected 'skipped: integration', got 'skipped: unit'`. All other 26 named cases still `ok`
   (the mutation only changes which suites are collected into `skipped`, so
   `blocking QA does not fail skipped suite` still happened to pass on that fixture, but the
   detail-content case caught it precisely).
3. Restored line 88 to `if outcome == "skipped":` (byte-identical to pre-mutation).
4. Re-ran `python3 .claude/skills/harness/bin/test-gate-policy.py`: all 27 named cases `ok`,
   exit 0.
5. Restore verified via `git status --porcelain -- .claude/skills/harness/bin/gate_policy.py`
   (shows only the intended, un-mutated diff against the pin) and by the green re-run in step 4.

## Working tree

`git status --porcelain` at the FEAT-43 root shows only the four files below as touched by this
task, plus pre-existing unrelated changes to `STATE.md`/`feature.json`/the answers file that this
task did not create or edit. No scratch files.

## Files touched

- `.claude/skills/harness/bin/code_grade.py`
- `.claude/skills/harness/bin/gate_policy.py`
- `.claude/skills/harness/bin/check-plan-routes.py`
- `.claude/skills/harness/bin/test-code-grade.py`

## Boundary note

The sixth grade-3 blocker, `code-grade.py:80 _diff_paths` (the hyphenated CLI), is explicitly
out of scope for this task (wave 2, different owner) and was not touched.
