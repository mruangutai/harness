# Research — BUG-1898 inflight claim lifecycle

## BLUF

The five reported failures are one lifecycle split, not five independent cleanup bugs. Dispatch currently creates a receipt before OMP exposes the child id, the extension guesses identity by name and result position, settlement listens on the wrong bus, and yield validation resolves a different registry root. The smallest durable design is to make run start authoritative for exact-id claim/bind, carry that id through result and settlement events, and make every consumer call the same public feature-root resolver. Cleanup remains exact and manual.

## Sources inspected

- Intent and settled rulings: `.harness/notes/grilling-inflight-claim-lifecycle-2026-09-24.md`.
- Extension lifecycle: `.omp/extensions/harness-hooks.ts#registerHarnessHooks`.
- Claim model and release selectors: `.claude/skills/harness/bin/inflight_registry.py`.
- Dispatch claim and private root resolver: `.claude/skills/harness/bin/dispatch-guard.py#_root_for`.
- Yield child gate and release: `.claude/skills/harness/bin/validate-digest.py#hook_mode`.
- Port conformance: `.claude/skills/harness/bin/check-omp-port.py#check`.
- Existing behavioral seams: `tests/unit/omp-hooks.test.ts`, `tests/integration/test-inflight-registry.py`, `tests/integration/test-dispatch-guard.py`, `tests/integration/test-validate-digest.py`, `tests/integration/test-check-omp-port.py`, and `tests/manual/probe-omp-runtime-lineage.py`.
- Governing records: DEC-100, DEC-174, DEC-204, DEC-205, DEC-218, DEC-231, DEC-232, and DEC-233 in `.harness/harness/docs/DECISIONS.md`.

## Findings A–E

### A — unrelated claims can be released

`validate-digest.py#hook_mode` can reach release without both feature and exact agent identity. Its persona fallback can therefore delete a different live claim. The integration suite calls the real hook, so suite execution can reproduce the same destructive path. The regression floor must seed every governed persona, exercise direct QA yield while PM is live, and assert every unrelated row remains byte-for-byte present.

### B — a settled wake is claimless

OMP calls `before_agent_start` for each run and exposes the actual agent id in extension context, but the current hook only injects identity/expertise context. A settled agent can therefore wake and write before regaining registry authority. Run start must perform the authoritative claim or bind. If that cannot happen, the run is held locally: every tool is refused except yield, and yield must return a BLOCKED digest that names cause and retryability.

### C — batch identity is positional and name-prebound

The task-result handler zips receipt entries to returned identities by array index, while OMP result rows already carry their own ids. Mixed governed/non-governed batches or reordered rows can attach the wrong claim. The dispatch path also prebinds a bare `dispatch.name`, although real ids include lineage and uniqueness such as `Lead.Scope` and `Name-2`. The result row id is authoritative. A dispatch receipt remains useful only to roll back a governed child that never started.

### D — lifecycle handler uses the wrong bus

The extension registers `task:subagent:lifecycle` with `pi.on`, but OMP publishes task lifecycle events through `pi.events`. Existing unit fakes and the current port checker merely observe the marker string, so they cannot catch the wrong bus. The port check must validate registration semantics, and the live probe must demonstrate an actual background child settling and removing its own row.

### E — dispatch and yield use different registries

`dispatch-guard.py#_root_for` resolves the feature's linked worktree, while `validate-digest.py#_root_or_none` resolves the owner checkout. Child lookup, held-child refusal, release, and recovery text can therefore operate on a registry different from the one dispatch wrote. `inflight_registry.feature_root` is the canonical resolver; dispatch and validation both migrate to it. This task follows C and D so it consumes corrected identities and actual settlement.

## Four sharp questions resolved

1. **Occurrence 1 cause:** the historical trigger is not proven. The acceptance contract does not invent one; it proves the safety invariant by yielding QA and running a suite while PM is live, then showing PM's exact row survives.
2. **Single resolver:** `inflight_registry.feature_root` owns feature-worktree resolution. `dispatch-guard._root_for` delegates or disappears, and `validate-digest` uses the same public seam. No second resolver is introduced.
3. **Lifecycle event bus:** OMP task lifecycle belongs on `pi.events`, not `pi.on`. Both semantic integration checking and a live OMP delivery must prove it.
4. **OMP restart/revival marker:** DEC-204 records that `before_agent_start.systemPrompt` loses the feature marker, while the runtime exposes the actual agent id. Recovery therefore uses one deterministic registry lookup before first write: enumerate the owner-checkout registry and every registry in a linked worktree registered by `harness_boundary`, and select a live claim matching the exact OMP agent id. Exactly one match supplies the feature and holding root; zero matches, multiple matches, or any unreadable registry put the run in the cause-and-retryability BLOCKED-only state. Persona, dispatch name, cwd, and guessed session identity are never fallbacks.

## Delivery shape

1. Establish the public root resolver and atomic run-start claim/bind result, preserving one-PM while retaining legal multi-flight claims for personas outside `SINGLE_FLIGHT_AGENTS`, plus DEC-100 pass-through.
2. Correct run-start refusal, id-keyed batch attachment, name handling, lifecycle bus, and restart/revival recovery in the extension.
3. Move digest validation to exact identity and the canonical feature registry; prove held-child behavior after corrected settlement.
4. Add a credentialled live OMP merge-gate probe plus deterministic runner registration coverage.
5. Rewrite DEC-204 to current truth, retain the DEC-100 distinction, and publish the exact one-time cutover and post-merge evidence procedure.

Every task touching `.omp/extensions/**`, `.claude/skills/harness/bin/**`, or `tests/**` is routed `main-session-direct` under DEC-174. DEC-205/current-truth governs the decisions records, while the operator-required lane declaration keeps this feature's evidence notes with the direct task that produces them. Task dependencies are topological, and the defect-E task follows both corrected result identity and lifecycle delivery.

## Principles applied

- **Redesign from first principles:** define ownership at the earliest trustworthy boundary—OMP run start with an actual agent id—then propagate that identity through result, settlement, and yield instead of adding cleanup exceptions at each symptom.
- **Outcome-oriented execution:** each task names its final observable invariant, its owning files, its exact proof command, and its predecessors; no compatibility alias, name fallback, positional fallback, bulk release, or later cleanup task is retained.
- **Weakest sufficient specification:** the restart/revival task has a falsifiable two-branch decision rule, while the plan does not claim an OMP behavior that only the live host can reveal.
- **Verification is the product:** automated invariants, pinned-SHA inspection, and the credentialled live UAT are separated; the live probe cannot be replaced by dry-run output, and the absent typecheck runner is reported rather than implied.
