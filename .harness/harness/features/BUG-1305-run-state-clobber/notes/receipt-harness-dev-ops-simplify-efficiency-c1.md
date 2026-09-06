# EFFICIENCY pass — BUG-1305 — receipt

**BLUF: one real, measured hot-path finding worth applying.** `harness_boundary.py` now imports
`run_identity` at module load solely to read `MARKER_NAME`, and `run_identity.py` imports
`tempfile`+`uuid` at module top even though only its POST-only mint functions need them. Since
`harness_boundary` is imported on essentially every `check-domain.sh` invocation (every governed
Write/Edit, not just run-directory writes), this adds real per-write latency system-wide. Two other
candidate costs (the PRE witness read, the `check-state.sh` corpus sweep) are measured and
negligible — explicitly not worth applying.

## Method

- `python3 -X importtime` on `run_identity` and on `harness_boundary` alone (isolated copies in
  `/tmp/effbench*`, both pre-change (`git show origin/main:...`) and post-change).
- End-to-end A/B: two sandboxed `.agents/skills/harness/bin` trees (pre vs post), each with a
  minimal `.harness/team-config.yaml`, `check-domain.sh` invoked 60x via a synthetic denied-Write
  payload piped on stdin, wall-clock via `time`. Isolates real subprocess/interpreter cost, not a
  microbenchmark artifact.
- `run_identity.marker_path`/`read_marker` timed directly, 5000 iterations, for the sweep and PRE
  witness costs.
- All scratch files under `/tmp/effbench*`; nothing written in the worktree.

## Findings, ranked

### 1. [Apply] `harness_boundary.py:22` — eager `tempfile`/`uuid` tax on every governed write

`from run_identity import MARKER_NAME as _RUN_IDENTITY_MARKER` (line 22) executes
`run_identity.py`'s full module body, which does `import tempfile as _tempfile` and
`import uuid as _uuid` at module top (lines 8–9) — needed only by `mint_uid`/`inject_uid`/
`record_seed`, all POST-only. `harness_boundary` is imported unconditionally at
`check-domain.sh:406` inside `if _run_domain:`, which is the ordinary path for **every** governed
Write/Edit — not gated on the target path being a run directory at all.

- **Cost, measured:** `-X importtime` on `harness_boundary` alone: 6.47ms pre-change → 12.82ms
  post-change (+6.35ms, dominated by `tempfile`'s `shutil`→`bz2`/`lzma`/`zstd` chain, 5.9ms of the
  8.8ms `run_identity` subtree). End-to-end A/B, 60 real `check-domain.sh` invocations each: pre
  4.060s (67.7ms/call) vs post 4.447s (74.1ms/call) — **+6.45ms/call**, matching the importtime
  delta closely. Against the script's own T-13 comment (`check-domain.sh:~196`, "measured at
  104.7ms for the full governed path"), this is a ~6% tax added to the dominant hot path in the
  whole write-guard system, paid by every write regardless of target.
- **Alternative:** move `import tempfile as _tempfile` / `import uuid as _uuid` in
  `run_identity.py` from module top into the three functions that actually use them
  (`mint_uid`, `inject_uid`, `record_seed`). Verified: a stripped copy with only
  `collections.abc`/`datetime`/`json`/`os`/`re` at module top imports in 2.2ms cumulative — almost
  exactly the pre-change `MARKER_NAME`-only cost, i.e. this recovers essentially the whole delta.
  `MARKER_NAME` stays a single definition (no re-duplicated literal in `harness_boundary.py`).
- **One concrete way this could break something:** `inject_uid`'s except clause only catches
  `(OSError, UnicodeError)`, not `ImportError`. Today, a broken/missing `tempfile` would fail loudly
  at `import run_identity` time, on every invocation, immediately after deploy. Deferred, the same
  break would surface only the first time `inject_uid` actually runs (first POST landing on a
  fresh checkpoint) — narrowing a load-time failure to a narrower, later-triggering one, and
  masking it for every PRE-only call in between. (`tempfile`/`uuid` failing to import is not a
  realistic stdlib failure mode, which is why this is a low-probability risk, not a reason to skip.)

### 2. [Measured, negligible] PRE witness read in `check-domain.sh`'s state.yaml ladder

`run_identity.read_marker()` (open + `json.load`) fires only when `RE_STATE_YAML.match(rel)` is
true AND the prior checkpoint has no `run_uid` yet (self-eliminating after the first successful
POST mint). Measured: 16.83µs/call for `read_marker`, 1.72µs/call for a bare `os.path.lexists`.
Even paid on every PRE Edit to a young run's `state.yaml`, this is three orders of magnitude below
the per-call interpreter cost above. Not worth a separate apply — folding tempfile/uuid out of the
module top (finding 1) already removes the only real cost near this path.

### 3. [Measured, negligible] `check-state.sh` corpus sweep, INV-36

New per-run-directory work: `os.path.lexists(marker_path)` always, `read_marker` + `conflict`/
`uid_conflict` only when the marker exists. At the corpus size named in plan.yaml D-13 (630 run
directories 2026-09-05, up from 575), the *lexists* stat alone costs ~1.08ms across the whole
corpus; if every directory eventually carried a witness (it does not today — D-13's whole point is
that the historical corpus has none), the full `read_marker` cost would add ~10.6ms. Measured
`check-state.sh` end-to-end on this checkout: 12.9s. 11.7ms against 12.9s is 0.09% — negligible,
and it only grows as fast as new run directories are created (bounded, linear, not compounding).
Not worth applying.

### 4. PRE/POST double-read — none found

`_post` is a single boolean selecting exactly one of the PRE ladder or the POST mint block per
invocation; they cannot both run in the same process, so there is no double-read of the same
checkpoint or marker within one hook call.

## The one candidate to apply

**Finding 1** — defer `tempfile`/`uuid` imports inside `run_identity.py`'s `mint_uid`/`inject_uid`/
`record_seed` function bodies. It is the only finding with a real, non-negligible, hot-path-wide
measured cost, and the fix is mechanical (move two import lines) with no observable behavior change
on the happy path.

## Verification

`git -C .../BUG-1305-run-state-clobber status --porcelain`:
```
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
```
That file belongs to a sibling reader (simplify-reuse), not touched here. No file under
`.claude/skills/harness/bin/` or `tests/` was modified; all scratch work lives under
`/tmp/effbench*` and `/tmp/bench_marker.py`.
