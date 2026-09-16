# SIMPLIFY / efficiency — BUG-151 aggregation safeguard

**Result: zero findings.** Every suspected cost was measured and is negligible relative to the
38s suite it runs inside. No wasted work found.

## Suite baseline (measured, matches the pinned spec exactly)

Command: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` from worktree
root, wall time 40.92s.

- `exit=0` (matches pinned baseline)
- `^ok` count: 404 (matches)
- `^FAIL ` count: 0 (matches)
- `aggregation safeguard` lines: 0 (matches)
- Total captured output: 477 lines, 32361 bytes

No drift from the pinned baseline — reporting this plainly per instructions, not absorbing it.
The 40.92s full run **is** the deliberate boundary evidence for this change (SC requires
discovery be verified against real output); it is not itself flagged as waste.

## 1. `_AggTee.write` hot-path cost

Measured with a throwaway `python3 -c` benchmark (no file written into the tree), simulating the
real observed volume: 477 lines / 32361 bytes total output across the whole run, modeled as ~954
`write()` calls of ~33 bytes each (print splits content + line-ending across writer calls).

- Direct-write baseline (no tee): 56.6 µs for the full simulated volume
- Tee (list-append + write + one `.text()` join): 84.9 µs for the full simulated volume
- **Overhead: 28.3 µs total**, for the entire run's aggregate write volume, against a 40.92s
  wall-clock run — **0.00007% of total runtime**.

Explicitly negligible. `self.parts` peak memory is bounded by the largest single block's output
(well under 32KB even in the worst case of one block producing all of it) — not a concern at this
scale.

## 2. `block_tee` lifetime / closure retention

Read `main()`: `block_tee = _AggTee(sys.stdout)` is rebound fresh **inside** the `for block_name,
block_fn in list(globals().items())` loop body (test-check-domain.py, `main()`, the discovery
loop). No closure captures it; the only value that survives past a loop iteration is
`block_verdict` (a short string appended to `problems`, or `None`). Each block's tee — and its
`self.parts` buffer — is eligible for GC as soon as the next iteration rebinds `block_tee`. No
long-lived object holding the whole run's output alive at once, and no closure-scope leak.

## 3. Double execution risk from discovery vs. hand-written list

The measured suite run (404 ok / 0 FAIL, exit 0) matches the pinned baseline **exactly**. Had any
block executed twice under discovery, the `ok`/`FAIL` totals would diverge from the pinned
404/0 baseline (each block prints one line per sub-case). They didn't. This is the concrete
observational check the dispatch asked for, not reasoning-from-the-diff: `run_bug1305_cases`
(the composite) is gone, its three sub-blocks (`run_bug1305_digest_repair_cases`,
`run_bug1305_marker_cases`, `run_bug1305_identity_cases`) are discovered and run individually —
once each, as evidenced by the unchanged 404/0 totals. 24 module-level `run_*` functions exist
(`grep -c '^def run_'`); none run twice.

## 4. `list(globals().items())` cost

Measured with a synthetic 600-entry globals dict (this module has ~157 top-level `def`/`class`
statements plus imports/constants, so its real global count is lower): **130.33 µs** for the
`list(...)` call. Against the 40.92s run, this is unmeasurably small — stated explicitly as
negligible, not a non-answer.

## 5. Import/startup cost of the three new definitions

`_AggTee` (a 4-method class), `_aggregation_verdict` (one function), `run_bug151_selfcheck_cases`
(one function) are ordinary `def`/`class` statements compiled once at import. This class of cost
is sub-microsecond at CPython bytecode-compile granularity for objects this small; not separately
benchmarked because there is no plausible mechanism by which it would register against a 40s run —
stated as negligible by inspection, no measurement fabricated.

## Scope note

Did not propose weakening `_AggTee`, `_aggregation_verdict`, or the discovery loop — the dispatch
correctly identifies these as the deliverable, not a target for streamlining. Did not touch
wiring-adjacent test-coverage gaps (already triaged, out of this feature's scope per the shared
context).

## Verification

- `git -C <worktree> status --porcelain` before and after: clean except an unrelated sibling
  reader's artifact (`receipt-harness-backend-dev-simplify-reuse.md`), which is not mine. No
  source file touched, no probe/timing script left in the tree; all measurement was `python3 -c`
  inline, discarded after each command.
- Suite invoked exactly once (within the 2-run budget), prefixed `env -u HARNESS_AGENT_TYPE`,
  `$?` captured, `^FAIL ` counted via `grep -c`, not the tail line.
