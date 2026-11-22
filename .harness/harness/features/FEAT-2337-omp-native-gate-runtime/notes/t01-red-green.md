# T-01 — red/green evidence (async, bounded, concurrent policy runtime)

Worktree: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime`, HEAD `e1aa5837` (baseline `d04c765a`). All commands run from the worktree root. Host: darwin arm64, Bun 1.3.14.

## RED — new tests against the unchanged synchronous extension

Written before any edit to `.omp/extensions/harness-hooks.ts`. Baseline before the new tests: `bun test tests/unit/omp-hooks.test.ts` 186 pass / 0 fail; `python3 tests/integration/test-omp-native-gate-runtime.py` 445 passed / 0 failed.

### Bun (SC-01, SC-02 unit side, SC-03)

Command: `bun test tests/unit/omp-hooks.test.ts --test-name-pattern FEAT-2337` → exit 1, `0 pass / 24 fail`, `Ran 24 tests across 1 file. [9.64s]`.

```
(fail) FEAT-2337: one named 30-second budget, and no synchronous Python policy spawn
(fail) FEAT-2337: the event loop keeps running while a policy child is pending
(fail) FEAT-2337: past the budget a broad gate is visibly unavailable, killed with no survivor
(fail) FEAT-2337: past the budget a matching narrow command is refused, killed with no survivor
(fail) FEAT-2337: past the budget an unrelated narrow command is allowed silently, killed with no survivor
(fail) FEAT-2337: past the budget a helper keeps its non-blocking reason, killed with no survivor
(fail) FEAT-2337: a clean exit settles once and clears its timer
(fail) FEAT-2337: a spawn error followed by close settles once and clears its timer
(fail) FEAT-2337: a death by signal settles once and clears its timer
(fail) FEAT-2337: a deadline before close settles once and clears its timer
(fail) FEAT-2337: a helper spawn error settles once and clears its timer
(fail) FEAT-2337: Bash gates, the first declared refusal wins whatever finishes first
(fail) FEAT-2337: Bash gates, every unavailable notice rides beside the refusal, in declared order
(fail) FEAT-2337: Bash gates, unavailable notices without a refusal stay passive context
(fail) FEAT-2337: Bash gates, a rejected gate hides neither the refusal nor a sibling's notice
(fail) FEAT-2337: Bash gates, a rejection alone still refuses and keeps the notices
(fail) FEAT-2337: Bash gates, an unrelated command still runs every gate
(fail) FEAT-2337: all five real gate processes start before any is allowed to finish [8698.06ms]
(fail) FEAT-2337: delayed helper, an authorization refusal is not an early allow
(fail) FEAT-2337: delayed helper, a yield refusal is not an early pass
(fail) FEAT-2337: delayed helper, an expertise answer is still injected
(fail) FEAT-2337: a run is held until its delayed run-start answers, then ready
(fail) FEAT-2337: a refused batch answers only after its earlier claim is released
(fail) FEAT-2337: a lifecycle settlement resolves only after release-run and the call's receipt release
```

Discriminating failure lines:

- Budget constant: `expect(hooks.POLICY_TIMEOUT_MS).toBe(30_000)` → `Expected: 30000 / Received: undefined`; the timeout and settlement rows fail at the same point (no named budget to shorten in the copy, no timer armed).
- Heartbeat: `expect([ticksAtReturn, ticks >= 20, result])` → received `[0, false, …]`: zero event-loop ticks while a real 0.5 s child ran (spawnSync froze the loop).
- Overlap with five real planted processes: `.met` files `["alone","alone","alone","alone","met"]` — each gate waited its 2 s barrier alone because the next had not started (sequential spawnSync), 8.7 s total.
- Composition / delayed helper / lifecycle rows with a Promise-returning runner: `TypeError: undefined is not an object (evaluating 'stdout.split')` at `jsonLines ← parseRunAnswer` (harness-hooks.ts:104/773): the synchronous hook read an unresolved answer as a result.

### Integration, real copied gates (SC-01, SC-02, SC-03, SC-04 wiring)

Command: `python3 tests/integration/test-omp-native-gate-runtime.py --feat2337` → exit 1, `9 passed, 15 failed in 42.7s`.

```
FAIL  FEAT-2337 heartbeat: the event loop ticks while a real gate runs          {'ticks': 0, …}
FAIL  FEAT-2337 past the budget, broad bash-write-guard is visibly unavailable  {'blocked': False, 'unavailable': None, 'reason': None, 'ticks': 0, 'ms': 16198.7}
FAIL  FEAT-2337 past the budget, broad bash-write-guard is visibly unavailable: settled within the budget plus slack
FAIL  FEAT-2337 past the budget, a matching narrow gh-close-gate command is refused   (no budget in the copy; waited the full hang)
FAIL  FEAT-2337 past the budget, a matching narrow gh-close-gate command is refused: settled within the budget plus slack
FAIL  FEAT-2337 past the budget, an unrelated narrow gh-close-gate command is allowed silently   {'ms': 8099.6}
FAIL  FEAT-2337 past the budget, an unrelated narrow gh-close-gate command is allowed silently: settled within the budget plus slack
FAIL  FEAT-2337 past the budget, helper inflight_registry keeps its non-blocking reason   {'ms': 8135.1}
FAIL  FEAT-2337 past the budget, helper inflight_registry keeps its non-blocking reason: settled within the budget plus slack
FAIL  FEAT-2337 overlap: all five real Bash gates start before any finishes    ['absent', 'absent', 'absent', 'absent', 'absent']
FAIL  FEAT-2337 overlap: an unrelated command runs every gate, in declared order   {'threw': "TypeError: undefined is not an object (evaluating 'stdout.split')"}
FAIL  FEAT-2337 composition: a real Bash refusal still blocks the call
FAIL  FEAT-2337 composition: the declared-first refusal (gh-close-gate) leads the reason
FAIL  FEAT-2337 composition: the unavailable bash-write-guard notice rides beside it
ok    FEAT-2337 benchmark wiring: a failing ratio exits 1
ok    FEAT-2337 benchmark wiring: a passing ratio exits 0
ok    FEAT-2337 benchmark wiring: too few samples are malformed and exit 2
ok    FEAT-2337 benchmark wiring: a non-numeric timing is malformed and exits 2
```

The benchmark wiring rows pass at RED by design: they are SC-04's cheap failing-ratio input to the benchmark's own assertion/exit path (`--benchmark-verdict` → `benchmark_verdict`), recorded here as the required nonzero exit (`a failing ratio exits 1`, malformed evidence exits 2) before the fix is accepted. No serial-mutant sequence (PF-c9a88d3e).

Correction after RED: the first draft of the heartbeat check used check-domain on a `Write` payload, whose real answer for harness-backend-dev in the fixture is a refusal, so its "own answer unchanged" row failed for the wrong reason. It now plants the 0.6 s delay in bash-write-guard on `echo hello` (the section-1 control pass); its discriminating row (`ticks: 0`) is unchanged.

## Implementation (after RED)

`.omp/extensions/harness-hooks.ts`:

- `PolicyRunner` returns `Promise<PolicyResult>`. `runPolicy` is `async`: it uses `spawn` (`detached: true`, so the child leads its own process group) instead of `spawnSync`. The executable is still `gatePath(script)`, the cwd is still the caller's, and the environment is still `{ ...process.env }` with nothing added. Stdin is still exactly `JSON.stringify(payload)`, and stdout/stderr are still classified by the unchanged `classifyPolicyRun`. `spawnSync` remains only for the unrelated `git rev-parse` in `mainBase`.
- `export const POLICY_TIMEOUT_MS = 30_000;` is the only budget. It matches `HOOK_HANG_BUDGET_S = 30` and has no config key, environment override or injection parameter. The process settles exactly once, on whichever comes first: a spawn `error`, the pipes' `close`, or the deadline. Settlement clears the timer. On `exit` the process group is SIGKILLed so that a grandchild holding an inherited pipe cannot block `close`. At the deadline the group is SIGKILLed immediately (no graceful step, so ignoring SIGTERM changes nothing), the pipes are destroyed, and the process settles as `timedOut`.
- Timeout classification goes through the existing DEC-100 paths. `failureDetail` reports a timeout as "exceeded its 30-second budget and was killed". That makes a broad gate `unavailable`, refuses a matching narrow command and allows an unrelated one silently. A helper keeps its non-blocking `reason` convention for a timeout (it neither throws nor blocks), and a helper's spawn error still throws.
- The five Bash gates (`BASH_GATES`, in declared order) start together through `bashGateRefusal`, which runs `Promise.allSettled` over one synchronous launch pass. Outcomes are then read in declared order. The first refusal leads, and every unavailable answer adds its phase-`pre` notice in declared order, beside a refusal too. A rejected runner adds a refusing line ("failed before answering, so the call is refused"), which is the same effect as the earlier hook throw, but the rejection no longer hides a sibling's refusal or notice. The revised input/env injection and the no-`isError` composition are unchanged.
- Migrated callers, all awaited: `reportingRunner` (via `noteUnavailable`), `fileDomain`/`preDomain`/`postDomain` (sequential `for…of`, same order), `releaseClaim`, plus a new `releaseClaims` (sequential, in receipt order) that replaces every `receipts.forEach(releaseClaim)`, `resolveFeature`/`startRun`, `featureRoot`/`rootCall`, `settleRun` (it removes the pending call from the map before the first awaited release), and `authorizationRefusal`/`applyCallerRefusal`/`applyPlacement`/`distillAuthorityRefusal`/`applyExpertise`/`appliedPost`. Also migrated: `mainMergeGate`, the `digest_destination.py` binding, `before_agent_start` (claim, then reconcile, then injection), `agent_start` (wake reclaim), dispatch-guard/attach/rollback, the yield validator, tool_result `isError` release and `settledRunIds` settlement (`for…of` instead of `forEach`), spend feature-root/stamp-tokens/spend, and the post-write gates. The lifecycle listener is `async` and awaits `settleRun`: OMP's EventBus wraps listeners as `async (i) => { try { await r(i) } catch … "Event handler error" }`, as read from the installed omp binary.
- Run readiness: `claimRun` sets `runGate` only after `run-start` and, for leads, after the digest-destination binding have answered. A `finally` keeps the earlier behaviour of "ready even if the digest helper throws". Until then every tool is refused as "has not completed". A second `openRun` while one is in flight joins it (`opening`) instead of claiming again.

## Test migrations (no assertion deleted or weakened)

- `tests/unit/omp-hooks.test.ts`: these standing runners now return Promises (`async`): the lifecycle `fixture` runner, the `governedUriHooks` wrapper (now `await runner(...)`), the context-advisory runner, the two spend/wake runners and the BUG-1898 `world` runner. Their internal fixture `spawnSync` of real Python/git is unchanged, as the intent requires. The fixture's `settle` helper now returns `Promise.all` of the listeners (it was `forEach`, which dropped the promises). The `classifyPolicyRun` table still builds `PolicyProcess` shapes with `spawnSync`, because it is a pure classifier input and not a runner.
- `tests/integration/test-omp-native-gate-runtime.py`: the `DRIVER` now does `await hooks.runPolicy(...)`, and each case is wrapped in its own try/catch. Every standing result field is unchanged; `ticks`/`ms` were added. The `plant_unexecutable` docstring no longer names `spawnSync`. The summary/exit moved into `finish()`. Default mode runs every standing section and then `run_feat2337()`. `--feat2337` runs only the FEAT-2337 checks. `--benchmark` runs only the acceptance measurement. `--benchmark-verdict FILE` runs only the benchmark's assertion/exit over recorded evidence. Any other argument exits 2.
- Changed or new Python functions in the integration script, graded with `python3 .claude/skills/harness/bin/code-grade.py --json tests/integration/test-omp-native-gate-runtime.py`: all 41 grade >= 3. The lowest are `make_root` 3 (unchanged), `plant_guarded_crash` 3 (unchanged) and `run_composition` 3. `evidence_defect` first graded 2 (cyclomatic 13) and was split into `sample_arms`/`timings_defect`/`clean_outcome`/`evidence_defect` before GREEN.

## GREEN

- Literal verify, `bash -o pipefail -c 'timeout 55 bash -o pipefail -c "bun test tests/unit/omp-hooks.test.ts --test-name-pattern FEAT-2337 && python3 tests/integration/test-omp-native-gate-runtime.py --feat2337"'`: exit 0, real 11.5 s, 0 FAIL lines. Bun: `24 pass / 186 filtered out / 0 fail`, `Ran 24 tests across 1 file. [3.27s]`. Integration: `25 passed, 0 failed in 8.2s`. After the run, `pgrep -fl "sleep 8"` found no surviving planted grandchild.
- Full Bun suite, `bun test tests/unit/omp-hooks.test.ts`: `210 pass / 0 fail` (186 standing + 24 FEAT-2337), 20.6 s. `python3 tests/unit/test-omp-hooks.py` (the Python-to-Bun wrapper): 210 pass, 0 fail.
- Default runtime integration, `python3 tests/integration/test-omp-native-gate-runtime.py`: `470 passed, 0 failed in 21.7s` (445 standing + 25 FEAT-2337).
- Adjacent consumers of the extension's text: `python3 tests/integration/test-check-omp-port.py` 31/31 passed (it still finds `plan-sign-gate.py` in the gate list and the lifecycle listener on `pi.events`). `python3 tests/unit/test-no-distribution.py` ALL PASS.
- One proving run of `python3 tests/integration/test-omp-native-gate-runtime.py --benchmark` while the host was busy (load average about 5.5 with other builders running). This is NOT acceptance evidence, which QA records at the review pin on an idle host. Result: exit 0. Sequential samples 174–185 ms, median 176.6 ms, which matches the historical figure of about 180 ms. Parallel samples 53–55 ms, median 53.6 ms. Ratio 0.304, limit 0.75. Recorded alongside: Bun 1.3.14, Python 3.15.2, 12 CPUs, source_sha e1aa5837 (working tree, uncommitted).

Candidate versus installed identity (BRIEF Verification gaps): everything above exercises the candidate extension source in this worktree, either directly or as byte-for-byte copies in fixture roots. None of it touches the installed/host OMP extension that enforces this session.
