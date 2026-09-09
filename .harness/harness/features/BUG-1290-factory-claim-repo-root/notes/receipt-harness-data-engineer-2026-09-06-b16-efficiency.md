# Receipt — harness-data-engineer — EFFICIENCY angle — BUG-1290 / B-16

## BLUF
**Empty pass.** The added 5g case reruns `_run_5b_scenario()` once more; measured, that second
scenario run is ~1-2% of the file's total wall time and one extra never-cleaned tempdir out of
109 the file already leaves — neither is material, and the file is a one-shot unit-test run, not
a hot path. No EFFICIENCY findings.

## Measurements
- Whole-file wall clock, `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py`,
  3 runs from the worktree root: **0.132s, 0.130s, 0.131s** (`real`). 125/125 checks pass on every
  run (baseline check count: **125**).
- `cProfile -s cumulative` over the same invocation (profiler overhead included, so its own total
  of 0.143s runs a bit high vs the unprofiled ~0.13s, but the *ratios* below are what matter):
  - `run_main` (`test-factory-claim.py:403`): 48 calls, 0.082s cumulative → **~1.7ms/call**.
    5g adds exactly one of these 48 calls (via the shared `_run_5b_scenario()`), i.e. **~1.7ms of
    ~130-143ms total ≈ 1.2-1.3% of wall time**.
  - `tempfile.mkdtemp`: 109 calls, 0.021s cumulative → **~0.19ms/call**, and posix.mkdir itself
    (0.019s / 172 calls) dominates that — filesystem syscall cost, not scenario-construction
    overhead.
- Isolating `_run_5b_scenario()`'s exact cost as an A/B diff (file with the 5g block removed vs.
  the shipped file) was attempted but blocked by the write-guard on any path outside my domain,
  including scratch copies under `/tmp` created via `cp`/`mkdir`/`rm`. The cProfile per-call
  average above is the measured substitute; it is drawn from the same 48 real invocations in the
  actual run, not a synthetic benchmark, so it is not an unmeasured estimate.

## Judgment
- **Not a hot path.** This is a unit-test file executed once per CI/dev invocation — not a
  per-session or per-write code path (per skill: "Judge minutes, and hot-path milliseconds. A
  gate that runs at every session entry or every write earns scrutiny that a one-shot build step
  does not"). 5g's added ~1.7ms against a 130ms one-shot run is not worth flagging.
- **Tempdir accumulation:** the file already calls `tempfile.mkdtemp` 109 times per run with zero
  cleanup (pre-existing behaviour, out of scope to fix per the dispatch). 5g's one additional
  `mkdtemp` (inside its second `_run_5b_scenario()` call) changes that count from 108→109-ish
  proportionally — it does not change the *character* of the pre-existing non-cleanup pattern,
  it is one more instance of an already-accepted cost.
- **The rerun is deliberate evidence, not waste.** 5g exists specifically to prove 5b's
  cache-bleed property is falsifiable under a mutant `_BlockerCache` — rerunning the identical
  scenario under the mutant *is* the test's content, not redundant work standing in for a cheaper
  targeted check. Per the skill: "Deliberate full-suite runs at boundary steps are not waste —
  they are the evidence the boundary exists. Say so rather than flagging them." Same logic
  applies at test-case granularity here: there is no "targeted case" that binds equally, because
  the property under test is precisely "the shared fleet, rerun, differs only in the mutant."

## Findings
`[]` — no EFFICIENCY findings. The added cost is measured, small (~1.3% of a 130ms one-shot run),
and is the evidence the case exists to produce, not incidental waste.
