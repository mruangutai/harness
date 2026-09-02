# FEAT-48 — a parallel-safe suite, and an invariant that keeps it that way

`test-check-domain.py` overwrote the live shared `feature_schema.py` in the checkout for a ~90ms
window on every run, so any concurrent process importing that module got one whose
`problems_for_text` raises. That is issue #1053: `test-gh-sync.py` failed about one run in three at
8-way parallelism and never serially. The hazard was observed directly, not inferred — 5,105 broken
reads in 1,032,849 polls during one run (`notes/research-parallel-safety.md`).

This branch removes the shared-state mutation, adds a static invariant CI runs so it cannot come
back, and turns the runner into a worker pool with attributable output.

## What changed

- **Every mutation probe now runs against a private bin copy** — new `isolated_bin.py`, applied
  across `test-check-domain.py`, `test-check-state.py`, `test-feature-worktree.py`,
  `test-bash-write-guard.py`, `test-check-fixture-secrets.py` and `test-validate-digest.py`. No test
  writes, replaces or deletes a path inside the live checkout while it runs.
- **`test-suite-independence.py`** — a static scanner registered in the `unit` kind, so a
  reintroduced violation fails a gate CI already runs and the failure names file and line. It
  carries six in-file self-tests; all six were proved to discriminate (three monkeypatch probes,
  no ever-green case).
- **`run_pool.py`** — the worker pool, with a `--mutation-check` snapshot of the watched `bin/`
  directory before and after the run. It reports the worker count, the file count and the wall time,
  and one `PASS <file>` / `FAIL <file>` line per file.
- **`run-unit-tests.sh`** keeps every existing contract: `--kind unit`, `--kind integration`,
  `--kind all`, `--check-kinds`, and exit codes 0, 1 and 2 with their present meanings.
- **`DECISIONS.md`** records the choices, including change-based test selection rejected as the
  speed lever.

## Measured

| | |
|---|---|
| serial baseline (planning, `ea6f51f`) | 247s |
| after, 12-core M3 Pro | **8 workers, 63 files, 42.40s wall** — ~5.8x |
| ten consecutive full runs | exit 0 every time, 42.64–47.82s |
| broken reads of the live `feature_schema.py`, post-fix | **0** (pre-fix control: 4968) |

Ten clean runs are not the proof — the old hazard once survived six consecutive clean 8-worker
runs. The static invariant and the runtime mutation check are what carry the claim.

## Verification

Graded at `review_sha 27f8105b`, which is unmoved: the only commits after it are this feature's own
`.harness/` records.

| Gate | Result |
|---|---|
| `.claude/skills/harness/bin/run-unit-tests.sh --kind all` | **exit 0** — 63 files, 8 workers, 48.29s, zero `FAIL`, zero `MUTATED`, clean tree |
| blocking qa gate (`unit` + `integration`) at the pin | **PASS** — matrix satisfied, both kinds green |
| `code-grade.py --base origin/main --head 27f8105b` | **exit 0**, `PASSING: 70`, zero blocking records |
| validation panel (code, security, qa, ui) | c8's two `must_fix` closed with re-taken proofs |
| goal-check | **10 of 10 success criteria met**, every row re-taken at the pin |

## Accepted limits, recorded rather than fixed

Fifteen residual findings were put to the operator at the ship review and all fifteen were accepted
as backlog rather than folded into this feature — they are filed as their own issues. The one that
matters most: `run_pool.py`'s `_record` swallows every `OSError`, so a test that plants a file under
a directory whose execute bit it then removes is omitted from both mutation snapshots. It fails no
success criterion and reproduces identically at `b86ce66a`, `e64e863e` and `27f8105b`, so it is a
pre-existing limit of the detector and not a regression of this work. The full table with each row's
nature is in `notes/ship-review-2026-09-02-c9.md`.

Closes #1053

Milestone 40 · parent #1191 · sub-issues #1192–#1197. T-07 is `abandoned` (superseded by T-02) and
carries no sub-issue.
