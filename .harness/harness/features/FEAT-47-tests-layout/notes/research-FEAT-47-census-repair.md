# FEAT-47 census repair — FEAT-48 lands first, and no plan states an expected count

**Every hardcoded test-file count is gone from `BRIEF.md` and `plan.yaml`.** What replaced them is a
floor plus a per-file provenance check per task, and one conservation law asserted once at the end
from the ref this feature merges into. The two plans' censuses now reconcile exactly, arithmetically
verified: 56 in `bin/` today, 58 after FEAT-48, 20 to `tests/unit/` + 37 to `tests/integration/` +
1 declared deletion = 58.

## What changed, by number

| Was | Now | Where |
|---|---|---|
| `[ "$n" = 36 ]` | floor `-ge 37`, source named in the failure message | T-02 verify |
| `[ "$n" = 19 ]` | floor `-ge 20`, source named | T-03 verify |
| `grep -c "^R" >= 36` over `tests` + `bin` | per-file `R<sim> bin/<b> -> <f>` assertion, scoped to `test-*.py` only | T-02, T-03 |
| bin sweep expecting emptiness | `left` must equal exactly `test-run-unit-tests-kinds.py` | T-03 |
| tally counts `= 20` / `= 37` | set equality between tally lines and the kind's directory | T-05 |
| — | new `suite-census.py migration` subcommand: conservation law + `--floor 56` | T-05 step 9 |
| `dec: DEC-206` (11 sites) | `DEC-207`; FEAT-48 takes DEC-206 | plan-wide, T-06 |
| `gen-decisions-index.py --check` | `--stdout` captured, compared byte-for-byte | T-06 verify, SC-07 |
| — | exactly one `run_pool.py` line, carrying `--mutation-check`, no serial loop | T-05 verify |

## Three defects the reorder exposed that were not in the brief

1. **T-03's `bin/` sweep was already broken.** 36 + 19 = 55 of 56; `test-run-unit-tests-kinds.py`
   stays in `bin/` until T-05 `git rm`s it, so a sweep expecting emptiness at T-03 was red for a
   reason no task was wrong about. Now asserted as an exact residue.
2. **The decision number shifts.** FEAT-48 lands first and takes `DEC-206`; FEAT-47's entry is
   `DEC-207`. T-06 now says to re-derive it and update every `dec:` field if it differs.
3. **FEAT-48's own decision entry is inside T-06's live-file sweep.** If it names `UNIT_SCRIPTS` as
   a live mechanism, the sweep goes red. Added T-06 step 3b: rewrite that sentence under DEC-205,
   same treatment DEC-187 and DEC-197 already get.

## Interactions with FEAT-48 that T-05 now states

- `run-unit-tests.sh`'s serial loop is already
  `python3 run_pool.py --mutation-check "$ROOT" -- "${SCRIPTS[@]/#/$BIN_DIR/}"`. T-05 drops only the
  `$BIN_DIR` prefixing, feeds repo-relative discovered paths, and carries `--mutation-check`
  forward verbatim. Nothing in `run_pool.py` changes — that is what made ordering possible instead
  of merging.
- Every line anchor into `run-unit-tests.sh` is de-anchored: FEAT-48 edits that file first.
- `test-suite-independence.py`'s anchor is the odd one out — a **root climb**, four levels from
  `bin/`, two from `tests/unit/`. Get it wrong and it scans a smaller set and still exits 0; its own
  `>= 50` discovered-file floor is what catches that. Named explicitly in T-03.
- Both of T-05's new test files must build fixtures under `tempfile.mkdtemp()`, because
  `test-suite-independence.py` now forbids live-tree writes with no escape hatch.

## Proof run (harnesses under `/tmp/`, all exit 0)

- `feat47-rename-proof.py` — throwaway git repo. All `git mv`'d → green. One file recreated by hand
  while a fixture rename in the same pathspec stays clean → **red, naming that file**. This is the
  masking the old lower-bound count permitted.

- `feat47-sweep-proof.py` — four cases against the live worktree. New ladder: arrays live → `rc=1`
  with the message; token absent → clean; `git grep` errors → `rc=1, "git grep errored, status 129"`.
  **Old `if git grep … | grep .` form on the same erroring search → `rc=0, "sweep clean"`.**
- `feat47-census-proof.py` — 18 checks, all pass, including `union + deletion == baseline` exactly.
- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exit 0. Budgets: T-01 21,
  T-02 27, T-03 37, T-04 16, T-05 48, T-06 30 — all under the 50-line cap; every verify block
  passes `bash -n`.
- The baseline table in `research-tests-layout.md` holds 56 rows: 55 migrated files with rows,
  1 declared deletion, and FEAT-48's two correctly rowless and reported as `new`.

## Two corrections taken from FEAT-48's PM after the first pass

- **`gen-decisions-index.py --check` does not exist.** Verified at source: `parse_argv` rejects any
  argv token but `--stdout` and exits 2, and the banner says so. T-06's verify could not have
  passed. Replaced with a captured `--stdout` compared byte-for-byte against the committed index
  (`check=True`, so a generator failure is loud rather than an empty comparison). Smoke-run on the
  live tree: `index in sync`, exit 0. SC-07 corrected to match.
- **There are TWO non-test helpers, not one:** `isolated_bin.py` **and** `run_pool.py`. And
  `--mutation-check` is not optional (FEAT-48 D-11: it snapshots every tracked file's size and
  mtime around the run, catching the subprocess mutation the static scan is blind to). T-05 now
  carries the flag forward verbatim and asserts the property; dropping it would leave a green suite
  that had stopped checking. The brief's `## Constraints` and T-05's tail both name the runtime
  guard beside the static one.

## What would make each new check go red

- floor: a truncated `ls` or a kind directory the migration never filled.
- per-file rename: any file recreated rather than `git mv`'d, or similarity below `-M`'s threshold.
- set equality: the runner discovering a file the directory lacks, or skipping one it holds.
- conservation law: a dropped file, a copy where a move was intended, or FEAT-48 adding a test this
  feature does not migrate.
- `--floor 56`: a `--base` ref whose history cannot be read. The floor can only go stale downward,
  so it never turns falsely green.

## Open

- **Q1 (non-blocking):** the `DEC-207` prediction assumes FEAT-48 is the only feature landing a
  decision entry between now and T-06. T-06 carries the re-derivation instruction, but the ordering
  is the main session's to confirm.
