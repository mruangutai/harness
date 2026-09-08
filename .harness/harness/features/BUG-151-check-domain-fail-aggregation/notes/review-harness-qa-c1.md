# QA gate — BUG-151 — review-c1 — re-pinned at `9b7b27d0`

**matrix_ok: true.** The one required kind (`integration`) is satisfied. No kind is missing or
blocked. Both plan `verify:` blocks still pass at this pin. My independent re-derivation of the
four suite numbers agrees exactly with the lead's `0 / 405 / 0 / 0`.

## 1. Change type and matrix resolution

Both `plan.yaml` tasks (T-01, T-02) declare `change_type: bugfix`. The true code diff
(`git diff 6d969ed3..9b7b27d0074924af2be46194536d6baca4ad4dd18 -- tests/integration/test-check-domain.py`)
touches exactly one file, entirely inside `tests/integration/`, and nothing outside it — confirmed
by inspecting the diff directly (208 lines, single-file `diff --git` header).

`bugfix`'s `when` clauses (`.harness/harness.json:203-219`), evaluated against this diff:

- `unit` if `touches_runtime_code` — **does not fire**. The entire diff is confined to a test
  file (`_AggTee`, `_aggregation_verdict`, `_run_block_captured`, `run_bug151_selfcheck_cases`,
  and `main()`'s discovery loop are all inside `tests/integration/test-check-domain.py`, itself
  test infrastructure, not application/production code). No file under production surfaces
  changed.
- `integration` if `fix_confined_to_tests_and_contract_docs` — **fires**. The diff is confined
  to exactly one test file and nothing else; this is the literal case the predicate names.
- `__bug_class__` if `match_bug_class` — **does not fire**. Per this repo's own qa Expertise
  (repository tier, G-08): this predicate is currently an unresolvable placeholder with no
  bug-class taxonomy entry that fires for any diff yet, so it never obligates a kind. Confirmed
  no such taxonomy file exists to consult.

Floor for this cycle: **`integration` only.** `unit` is not required.

## 2. Per-kind result

| kind | required? | cmd | outcome |
|---|---|---|---|
| integration | yes (predicate fired) | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | **pass** — exit 0, 49 files, 0 `^FAIL` lines anywhere in the run; `test-check-domain.py` itself reported `PASS test-check-domain.py (exit 0, 86.66s)` (artifact: `/tmp/bug151_integration_kind.txt`) |
| unit | no | — | not required; not run |

No kind in the matrix has a null `cmd` obligated by this diff, so there is no BLOCKED state to
report.

## 3. Independent re-derivation — the four numbers

Ran `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` directly (not
through the harness runner) and counted from raw stdout (artifact: `/tmp/bug151_run.txt`):

- exit code: **0**
- column-0 `^ok` lines: **405**
- column-0 `^FAIL` lines: **0**
- lines containing `aggregation safeguard`: **0**

This is **`0 / 405 / 0 / 0`, in full agreement with the lead's measurement**. No disagreement to
name. The tail of the run shows all seven `[bug151-selfcheck]` cases, including the new
`wiring-seam-catches-print-fail-return-zero`, printing `ok` at column 0.

## 4. Plan `verify:` blocks, re-run verbatim at this pin

- **T-01** (`_aggregation_verdict` callable, `run_bug151_selfcheck_cases()==0`): **PASS.** Ran
  verbatim; all seven selfcheck cases print `ok`, function returns 0, script prints `PASS`.
- **T-02** (`len(blocks)==24`, `398<=ok`, `bad==0`, `returncode==0`, `run_bug1305_cases` absent):
  **PASS.** Measured `0 405 0 24` then `PASS`. `len(blocks)==24` holds — the discovery extraction
  in this cycle's `_run_block_captured` refactor did not add or remove any module-level `run_*`
  callable; `398<=405` holds with margin.

## 5. Scope note

Per the dispatch, the file set under review is exactly
`tests/integration/test-check-domain.py`; the diff confirms no other file changed. I authored no
tests, fixtures, or source, and made no edits to the file under review. `main` was not touched.
