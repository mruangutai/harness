# FEAT-2397 T-04: red/green evidence

**Red baseline:** HEAD `2346a777`. T-01 (`8f373f76`) did not touch `tests/manual/`. The probe files in the
worktree were byte-identical to `2346a777`, checked with `git diff --quiet 2346a777 -- tests/manual/`,
when the red run was taken. The spec names `9eb07b4f`; the pre-change probe matches it. The new
test file was written first and run against that unchanged probe. Raw outputs are in
`t04-red-green/`; each file's last line is its exit code.

| Step | RED | GREEN |
|---|---|---|
| New `tests/unit/test-session-accessor-probe.py`, run against the unchanged probe | `red-baseline-2346a777.txt`: `AttributeError: ... no attribute 'is_nested'`, exit 1. `red-baseline-per-function.txt`: each of the 6 test functions run separately. 5 fail on the missing helpers (`is_nested`, `session_file`, `usage_numbers`, `observation_checks`); the one structural check that can run passes, because the old probe already had one `re.compile` | `green-session-accessor-probe.txt`: 82 ok, 0 failing, exit 0 |
| Corrected assertions fail when each repair is undone (mutants of the repaired probe, run in a /tmp copy) | `red-mutants.txt`: all 10 mutants exit 1. They are: children chosen by `usageDefined=False`; path validity dropped from `is_nested`; bool accepted as a number; NaN/inf accepted; main made optional; only tokens checked; path validity dropped from flat main; distinctness dropped; numeric strings coerced; measured rows taken from any session | n/a |

## What changed

### `tests/manual/probe-omp-session-accessor.py`
- The existing nested regex is hoisted unchanged to the module constant `NESTED_SESSION_FILE`. It is the only `re.compile` in the file, and the test asserts that.
- `is_nested(path)` is a valid session file (absolute, ends in `.jsonl`, name longer than `.jsonl`) that matches the pattern. `is_flat_main(path)` is a valid session file that is not `is_nested`; no second regex is involved.
- `session_file(row)` returns string results only. The old `str()` coercion is gone.
- `usage_numbers(row)` returns `{tokens, contextWindow, percent}` only when all three are finite `int`/`float`. It rejects bool, absent, null, NaN, ±inf and strings, and never invents or coerces a value.
- `observation_checks(rows)` is pure and covers four cases:
  - case3: a nested child is identified by path.
  - case4: that child's usage is numeric.
  - case5: a flat main exists. This is required; it no longer passes optionally when the main is missing.
  - case6: the measured child and the main have distinct, non-null probe session ids.
- `usageDefined` is not read anywhere in the Python. `main()` now records these four checks, and `_observe` holds the omp subprocess. The omp command, model and timeout are unchanged.
- Docstring changes:
  - The 2026-08 undefined observation is now a bounded historical note: pre-18.0.11 builds, upstream #10097, closed by #10098, released in 18.0.11, with #2194 reported on 18.18.0.
  - It states the API floor as omp >= 18.0.11 and FEAT-2397's omp 19.1.0 acceptance criterion, without claiming that a run happened.
  - The stale "unregistered from every test-kind list" sentence now says the check is registered only as the `locally_run` kind `omp_session_accessor`.
  - The census-pinned line "It was first registered in INTEGRATION_SCRIPTS" is kept verbatim.

### `tests/manual/probe-session-accessors.ts`
- `getContextUsage()` is called once per `turn_end` capture.
- The returned object is saved as `usage`. JSON keeps the numbers numeric, and an undefined result leaves the key absent.
- `usageDefined: usage !== undefined` is kept as a diagnostic only.

### `tests/unit/test-session-accessor-probe.py` (new)
It loads the probe with `importlib` and never copies the pattern. Its table cases are:
- **Identity:** 15 rows. They include nested child, flat main, tryCall's `undefined`/`null`/`THREW`/`no-target`, relative, wrong extension, bare `.jsonl`, trailing slash and non-string paths.
- **`session_file`:** 5 rows.
- **Measurement:** 12 token values (int, 0, float, True, False, null, absent, NaN, ±inf, string, list) and 8 usage-object rows.
- **Independence:** every token value × `usageDefined` True/False leaves the child nested and the main flat.
- **Scenarios:** 11 rows covering:
  - the #2194 case: a nested numeric child plus a flat numeric main;
  - `usageDefined` lying on both rows;
  - undefined child usage, NaN tokens and bool tokens;
  - main missing, child missing, malformed child path and a flat child path;
  - a shared session id, and no rows at all.
- **Structure:** exactly one `re.compile` in the probe; `is_nested` uses the constant; no helper reads `usageDefined`.

## Grades
`grades-changed-functions.txt` lists every function in the probe (bar 4) and in the new test file (bar 3), graded with `code_grade.grade_source`. Nothing is below the bar:
- Probe functions grade 4–5. `main` went from 1 to 4.
- Test functions grade 4–5.

## Verify
`verify-literal.txt` holds T-04's verify block, run verbatim from the worktree, and it exits 0:
- the unit file: PASS, 0 failing;
- `bun run typecheck`: clean;
- `run-unit-tests.py --check-layout`: no findings.

`adjacent.txt` covers the neighbouring checks:
- The new file is in the runner's `tests/unit/test-*.py` glob.
- `tests/integration/test-run-unit-tests-kinds.py` exits 0, so the locally_run registration of the probe is unchanged.
- `tests/integration/test-typescript-typecheck.py` and `tests/unit/test-suite-layout.py` both exit 0.

omp was not invoked to run the probe. T-06 and Main own the live observation and the closure of #2194.
