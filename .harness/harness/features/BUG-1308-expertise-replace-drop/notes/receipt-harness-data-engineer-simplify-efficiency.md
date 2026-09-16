# SIMPLIFY — EFFICIENCY angle — BUG-1308

**BLUF: no findings. `cmd_ops`/`resolve_ops` do the same one-stat/one-read/one-write/one-lock-hold
as the existing `cmd_apply`, and the resolve-layer work is microseconds at the 45-entry cap. The
only measurable cost the diff adds is in the test suite, all of it either legitimate boundary
proof or too small to matter.**

## Cost model used
`expertise-merge.py ops` runs a handful of times per feature (distillation dispatches), on a file
capped at 45 entries total across four sections. At that population, anything short of an actual
subprocess/lock/disk round-trip is noise; I costed in wall-clock milliseconds against that
frequency, not asymptotically.

## Checked and dismissed, with numbers

- **Lock hold time / repeated I/O** (`cmd_ops`, `expertise-merge.py:484-533`, `harness_merge.py
  locked_update:121-153`): traced the call graph — `require_expertise_destination` is a regex
  match only, no `stat`. `locked_update` does exactly one `os.path.exists` + one `open().read()`
  before calling `transform`, and one tempfile write + `os.replace` after. `cmd_ops`'s `transform`
  (`json.loads` + `parse_expertise` + `resolve_ops` + `render`) runs *inside* that single
  lock/read/write window, same shape as `cmd_apply`. No extra file reads, no extra lock
  acquisitions. Not a finding.

- **`resolve_ops` linear scans** (`_resolve_replace_or_drop`, `_resolve_add`, `_resolve_all`,
  `_rebuild_section`, lines 203-346): measured directly — 1000 calls of `resolve_ops` against a
  base at the full 45-entry cap (15/15/10/5 across sections) with a 14-op proposal (9 replaces +
  5 drops): **15.7 µs/call**. Against a process invocation whose python3 startup alone is tens of
  milliseconds, this is unmeasurable. Not a finding.

- **`json` import added to module top-level** (`expertise-merge.py:27`, now paid by every `apply`
  invocation too): measured `import json` in isolation — **~2.5 µs cumulative** (`json` +
  `json.decoder` + `json.encoder`, via `python3 -X importtime`). Negligible against interpreter
  startup. Not a finding.

- **New unit suite** (`tests/unit/test-expertise-ops.py`): `time python3 tests/unit/test-expertise-ops.py`
  → **0.046s** wall, in-process, no subprocesses. Not a finding.

- **New integration cases** (`tests/integration/test-expertise-merge.py`, the 10 new cases
  `case_replace_at_capacity` … `case_malformed_ops_cli`): isolated and timed each function
  directly (not via the CLI-subprocess main-loop) — sum **3.75s** out of the file's full **6.10s**
  wall run. Two cases dominate:
  - `case_concurrent_writers` (case18, D-09/SC-11): **2.12s**. Spawns two real subprocesses and
    forces genuine lock contention deterministically, with no test-only bypass. This is exactly
    the "deliberate full-suite/boundary proof" the skill says not to flag — a concurrency
    guarantee cannot be proven without a real second process holding the real lock. Not a
    finding.
  - `case_contract_drift` (case17, D-10/SC-09): **0.87s**. Calls `contract_drift()` four times
    (real `SKILL.md` text + 3 mutated copies); each call re-probes every candidate verb against
    the *real* CLI via a fresh subprocess (`_probe_accepted_verbs`, ~4-5 subprocess spawns per
    call). Three of the four calls re-probe the same core verbs (`add`/`replace`/`drop`/`merge`)
    whose accept/reject behaviour cannot change within one test run — a same-process memoization
    keyed on verb name would cut roughly 3 of the ~16 subprocess spawns this case makes. **Real
    but small: at most ~0.4-0.5s, once, on a boundary-step test file that already spends 2.1s on
    a legitimate concurrency proof in the same run.** Rated **backlog**, not apply-now: the fix
    touches test-file structure (adding a cache) for a saving under half a second on a step that
    runs a handful of times per feature — not worth the one-fix ceiling here.
  - The remaining 8 new cases are each 0.07-0.17s (single or double subprocess launches) — pure
    per-process overhead, not added computation, and match the file's own established
    "every case is a subprocess" convention (already true of cases 1-10 before this diff).

## Findings

None rated `apply-now`. One `backlog` observation, not a finding by this pass's own bar (concrete
cost is real but sub-second and one-shot): `case_contract_drift`'s repeated verb-acceptance
subprocess probing (`tests/integration/test-expertise-merge.py:696-725`, `:665-693`) could
memoize `_probe_accepted_verbs` per verb within a test run to save ~0.4-0.5s of the file's 6.1s.
Not proposed as an apply given the one-fix ceiling and the marginal size.
