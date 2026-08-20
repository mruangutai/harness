# receipt — harness-dev-ops — simplify pass, EFFICIENCY angle — FEAT-29-graphql-budget

Diff `bee6234..8c7d7bc` (HEAD `8c7d7bc`, branch `feat/FEAT-29-graphql-budget`). Re-run of this
angle; independently re-measured every figure below rather than trusting a prior receipt found
on disk at this same path.

## Verdict: no findings

Every hot path named in the dispatch was measured or read. Nothing crosses a cost worth
flagging.

## Measurements

**`gh_cost_log.measured()`, disabled path** (`HARNESS_GH_COST_LOG` unset — the default, the path
every `gh` call takes in normal operation). Read `_enabled()`
(`.claude/skills/harness/bin/gh_cost_log.py:47-53`): one dict `.get` + string compare, no I/O.
Microbenchmark, 200,000 calls: `measured()` no-op path 0.992 µs/call; `_enabled()` alone
0.364 µs/call. No subprocess, no file I/O on this path. Not flaggable — this is the path that
runs on every `gh` call the wrap sites (`factory_gh.py:151`, `gh-sync.py:111-113`) make, and its
cost is sub-microsecond.

**`gh_cost_log.measured()`/`record()`, enabled path** (`HARNESS_GH_COST_LOG=1`). Confirmed by
reading `measured()` (`gh_cost_log.py:149-166`): 2 counter-read subprocess launches per wrapped
call (before + after), each via `gh api rate_limit --jq .resources.graphql.used`
(`_read_counter()`, `gh_cost_log.py:68-80`) — so 3 subprocess launches total where the unwrapped
call took 1. Benchmarked the Python-side overhead only, `subprocess.run` patched to a fake
(no live `gh`, per constraint 1), **under a temp root** (`tempfile.mkdtemp()`, pointed at via
`CLAUDE_PROJECT_DIR`, with `factory_config.harness_root()` confirmed resolving there before any
write): 5,000 calls in 0.2581s = **51.6 µs/call**, including `record()`'s per-call log-path
resolution, argv sanitization, and file open/append. All 5,001 lines (5,000 records + 1 coverage
header) landed in the temp dir; `shutil.rmtree(tmp)` confirmed the temp dir gone afterward — no
byte touched `.harness/logs/` in the real tree. The two extra `gh api rate_limit` process
launches this angle cannot measure without a live call (forbidden) dominate the real-world cost,
and stay unmeasured rather than guessed. This path is opt-in / default-off
(`gh_cost_log.py:47-53`, approval amendment 5 — not re-litigated here) so the cost never lands on
a default run. Not flaggable — it is the feature's own deliberate instrumentation, correctly
gated.

**`run-unit-tests.sh`'s new array entry** (`test-gh-cost-log.py` appended to `UNIT_SCRIPTS`,
`run-unit-tests.sh:17`, one line). Timed standalone: `python3 test-gh-cost-log.py` → 35/35 PASS,
**0.061s** wall (re-measured, matches a prior 0.062s run). Against the ~4.2-4.7s unit-kind suite
this is ~1.3-1.5% — not worth flagging, and is exactly what registering a new `test-*.py` in
`UNIT_SCRIPTS` is supposed to cost (P-03/G-03: the array entry, not a glob, is what keeps the
drift detector's exit-code path reachable). Did not re-run the full `--kind integration` suite
(64s, unchanged mechanism — `test-gh-cost-log.py` is unit-kind only, no new integration entry) —
re-running a suite this angle's own diff did not touch would be exactly the "re-runs a whole
suite where a targeted case binds equally" waste the EFFICIENCY angle flags on a plan surface, so
skipping it is the efficient call, not an omission.

**Deliberate full-suite runs** at boundary steps (qa-matrix gate, T-03/T-04 receipts, visible in
this diff's `notes/qa-matrix-gate*.md`) are the evidence the boundary exists, per the dispatch's
own framing — not flagged.

## Constraint 4 — log file integrity (real tree)

`.harness/logs/gh-cost-2026-08-19.jsonl`:
- 39504 bytes, sha256 `7f8ae55288af9d5da39e2ebd5355c341b45668bd6e863ebe5a2743c5a6d5a563` —
  matches the byte count named in the dispatch (prior readers measured 39504 bytes).
- No `.harness/logs/gh-cost-2026-08-20.jsonl` exists in the real tree — confirmed via `ls`.
- All benchmarking in this run happened under a `tempfile.mkdtemp()` root with
  `factory_config.harness_root()` confirmed (via assertion) to resolve inside it before any
  write; the temp root and its `gh-cost-2026-08-20.jsonl` were destroyed by `shutil.rmtree()`
  and confirmed gone. No live `gh` call was made (constraint 1); `subprocess.run` was patched to
  a fake for the enabled-path benchmark only.

## Coverage / what else was checked

- `factory_gh.py`'s `_rate_limit_budget_error()` and `project_item_stations()` additions: read
  in full — one extra `gh api rate_limit` call only on the rate-limit-error path (not hot), and
  the pagination loop already settled under B-13 (not re-litigated). No new efficiency finding.
- `gh-sync.py`'s `gh()` wrapper: same `measured()` wrap site pattern as `factory_gh.run_gh`,
  same cost profile — no separate finding.
- `test-factory-gh.py`, `test-gh-board.py`, `test-check-state.py`, `check-state.sh`: read for
  hot-path additions; none found. `test-check-state.py`/`check-state.sh` are flag-only by the
  dispatch's own boundary and carried nothing to flag regardless.

No findings to route.
