# Security review — BUG-151 — cycle 0

**Verdict: PASS.** No injection, secrets-exposure, or fail-open exit-path defect in the diff.
One med, non-gating detection-integrity gap in the safeguard's own capture wiring, already flagged
to this panel; confirmed independently below with its own concrete failure scenario.

## What I opened and measured

- `git -C <worktree> diff 6d969ed3..e4efd774 -- tests/integration/test-check-domain.py` (full 149-line
  diff, artifact://1385) and the full file at the pin.
- Census check (grep): enumerated every top-level `def run_*` (24, incl. the new
  `run_bug151_selfcheck_cases`) and every call site of a `run_X(` outside `def`/`main` (none — no
  `run_*` function calls another `run_*` function as a helper). Old explicit `main()` invoked 20
  blocks directly + `run_bug1305_cases()`'s 3 subs = 23. New discovery loop (`globals().items()`
  filtered on `startswith("run_")` and `callable`) covers exactly those same 23 plus the new
  selfcheck block = 24. **1:1 parity — no block dropped, none double-invoked** (no `subprocess.Popen`
  side effects, e.g. `_feat51_omp_case`'s supervisor spawn, fire twice).
- Grepped every `print(f"FAIL...`/`print(f"ok...` call site (36 hits) to confirm the column-0
  `FAIL`/`ok` two-space convention `_aggregation_verdict` greps for is followed uniformly across
  every block, not just the new one — no format drift that would cause a false negative today.

## The four probes from the dispatch

- **Discovery exclusion** — NOT reproducible at runtime. `list(globals().items())` is read inside
  `main()`, after every module-level `def` has executed; nothing rebinds or deletes a `run_*` name
  before that point. The only way to exclude a block is a visible source edit (delete the function or
  rename off the `run_` prefix) — strictly louder than the pre-fix bug (deleting one `fails += `
  token while the block still ran and printed FAIL on screen). Census above confirms no exclusion
  occurred in this diff itself.
- **Exception swallow / short-circuit** — none. `block_fn()` calls in `main()`'s discovery loop are
  unguarded; an unhandled exception propagates, Python exits 1 (loud, non-zero). `contextlib.redirect_stdout`
  restores `sys.stdout` on exception (context-manager semantics) and re-raises, it does not swallow.
  The one `try/except` added (inside `run_bug151_selfcheck_cases`, line ~5222) converts an exception
  from `_aggregation_verdict` into a counted `fails += 1`, not a pass — it exercises the diagnostic's
  own crash-resilience against synthetic cases, it does not touch the real CASES/block path.
- **Verdict-line spoofing** — `_aggregation_verdict` counts `line.startswith("FAIL")` in the tee's
  captured text. Every existing print site that echoes subprocess/attacker-adjacent content (e.g.
  `for l in (r.stdout + r.stderr)...: print(f"      | {l}")`) prefixes with `"      | "`, so column 0
  is never attacker/subprocess-controlled text — confirmed by grep, no bare `print(l)` of raw
  subprocess output anywhere in the file.
- **Secrets/logging** — `_AggTee.write` only tees bytes already being printed by pre-existing code
  (same print statements, unchanged); it introduces no new capture of env vars, paths, or subprocess
  output beyond what was already printed to stdout before this diff.
- **Injection** — none. `_AggTee`, `_aggregation_verdict`, `run_bug151_selfcheck_cases` operate only
  on Python literals/ints; the only `subprocess.run([HOOK], ...)` call is pre-existing and unchanged
  by this diff (just wrapped in `redirect_stdout`).

## The one real gap (already flagged to this panel; independently confirmed, own scenario)

STRIDE-T/R on the CI verification signal, not gating at `high`. `_aggregation_verdict` is unit-tested
only against synthetic `(captured_text, total)` pairs (`run_bug151_selfcheck_cases`); nothing
permanent asserts that `main()`'s `with contextlib.redirect_stdout(block_tee): total = block_fn()`
stays wired together. Concrete failure mode: a future edit that decouples the `with`-block from
`block_fn()` (or routes a block's real failure print somewhere the tee doesn't see) makes
`block_tee.text()` read empty regardless of what actually printed. If that SAME edit also drops a
`fails +=` inside the block (the exact class of bug BUG-151 exists to catch), `_aggregation_verdict`
sees `bool(0 printed) == bool(0 total)` — no mismatch, no diagnostic — reproducing the original
"green while broken" failure one layer up, now inside the safeguard meant to prevent it.

**Severity: med, not gating.** Requires a future source edit by someone who already holds commit
access to this test file — the same access that would let them weaken `check-domain.sh` directly, so
per this role's own P-02 heuristic (an actor who already controls the value already holds the
privilege it would grant) this is a defense-in-depth/detection-integrity gap, not a privilege
escalation. Not reachable from the diff's current state; nothing in this diff introduces or triggers
it today.
