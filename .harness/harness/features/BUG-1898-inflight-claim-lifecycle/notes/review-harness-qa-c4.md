# QA c4 pinned gate — BUG-1898

**BLUF: PASS.** Exact-pin `f73c999482fd931021a3eb50d30aa8ab2a885283` supplies the missing SC-07 operator receipt: its final live run is PASS 29/29, while the focused hook and T-04 checks pass and the configured matrix floor is met.

## Scope and matrix

- Reviewed immutable archive at `f73c999482fd931021a3eb50d30aa8ab2a885283`; canonical base is `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`, and focused c4 comparison is `6bfc21e3ccdf78eb86cdd0eb250067348d887096..f73c999482fd931021a3eb50d30aa8ab2a885283`. The assigned worktree HEAD was `53ab555…`, so it was not used for source evidence.
- Phase 1 (BRIEF/plan only): cross-module T-01/T-02 requires unit + integration; runtime bugfix T-03 adds unit; T-04 changes test-kind structure and requires integration. Expected evidence: exact-id pre-write claim/reclaim and held-only refusal; actual-id batch settlement; T-04 declaration/dry-run; retained red-first receipts; credentialled SC-07 receipt. UI/component/typecheck are not required for this lifecycle change.
- `bun test tests/unit/omp-hooks.test.ts` — exit 0, **99 pass / 0 fail**, 273 assertions.
- `python3 tests/manual/probe-inflight-claim-lifecycle.py --dry-run` — exit 0, prerequisites READY; only printed the command and S1–S5 plan; did not start OMP.
- `python3 tests/integration/test-run-unit-tests-kinds.py` — exit 0, **8/8 PASS**.

## Focused behavior

`harness-hooks.ts:909-985,1339-1343` resets an ended run to unready and conditionally reopens it on `agent_start`; `:1016-1019` blocks every non-yield tool until ready. The real-registry unit case at `omp-hooks.test.ts:1895-1911` drives only `agent_start` after settlement (no second `before_agent_start`), reclaims `Lead.Dev`, then authorizes the write. `:1913-1923` proves the no-yield-ended run is held; `:1959-2002` proves exact-id revival/refusal branches and BLOCKED-only yield. `:444-493` covers the Main edge.

T-04 is coherent with the final receipt: S2 samples only after the wake (`probe…py:367-388`); S3 dispatches a nested `harness-eng-lead` with lead digest, excludes all `harness-*` ids from plain ids, and obtains nested lineage from its held claim (`:393-427`); RPC waits for `get_state.isStreaming == false` and uses `streamingBehavior: followUp` (`:285-302`).

## SC evidence and retained red-first proof

- SC-01: `tests/integration/test-suite-claim-preservation.py:107-121`; exact mutant proof and retained red at `notes/review-harness-qa-c0.md:23`.
- SC-02: `tests/unit/omp-hooks.test.ts:1875-2002`; baseline red 85 pass/13 fail, including wake reclaim, at `notes/review-harness-qa-c0.md:24`.
- SC-03: `tests/integration/test-inflight-registry.py:1238-1410`; retained baseline-red receipt at `notes/review-harness-qa-c0.md:25`.
- SC-04: `tests/unit/omp-hooks.test.ts:2020-2130`; retained baseline-red receipt at `notes/review-harness-qa-c0.md:26`.
- SC-05: `tests/integration/test-check-omp-port.py:194-214`; wrong-bus red at `notes/review-harness-qa-c0.md:27`.
- SC-06: `tests/integration/test-validate-digest.py:5815-5844`; retained baseline red at `notes/review-harness-qa-c0.md:28`.
- SC-07: **met from receipt only** — final `notes/live-omp-probe.md:522-561` records PASS 29/29, S1–S5, S2 exact-id wake/write/sample/settlement, S3 `Name-2` and `Nest.Probe`, suite-sentinel preservation, and empty final registry (`:699-714`). No live probe was rerun.

## Findings and dispositions

No active finding. Dismissed: F-01 (T-03 unreadable-registry fail-open) remains closed by strict pre-release reads; F-02 (T-03 grade) remains closed; F-QA-01 (T-03/T-04 weak mutant oracle) remains closed by exact two-label equality plus singleton/substitution controls (`review-harness-qa-c3.md:13-22`). Earlier failed live receipts are superseded by the final 29/29 receipt, not rewritten. `handoff-validate.md:1` sequence-3 late succession is an INV-43 residual ledger note only, not a code finding or blocker.

## Coverage and cleanup

The BRIEF-recorded typecheck gap remains: no executable TS typecheck runner; it is non-gating. The live locally-run kind is satisfied by the recorded final receipt. Created `/tmp/BUG-1898-qa-c4.ztMjSc` using `git archive` for pin isolation; it is removed after this artifact write. No source/tests were modified, no formatter/linter/project-wide suite, and no live probe ran.

## Principles applied

- **Build the Lever** — used the focused executable suite, dry-run, and kind-registration checks rather than hand-inferring their contracts.
