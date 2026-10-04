# Code review — BUG-1898 — c0

**BLUF.** FAIL at spec compliance; quality review did not open. The exact-id lifecycle is otherwise coherently implemented and its targeted suites pass, but `validate-digest.py` explicitly fails open when the canonical registry is unreadable, allowing a dispatch-capable parent to return without enforcing the live-child rule promised by SC-08/D-07's rewritten DEC-204.

## Scope and evidence

- Reviewed canonical range `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..84c3a6cbe74c7c27337d4372a68be60fca834118`; no `[harness:human]` commits occur in the range.
- The worktree has only Harness-record dirt (`STATE.md`, `feature.json`, `notes/handoff-build.md`), not dirty source or tests; pinned source bytes were reviewed.
- Mechanical grade: `code-grade.py --base a4d72e7f… --head 84c3a6cb…` reports 114 passing changed functions, no grade-2 or failing record.
- Targeted verification passed: registry 161/161, dispatch guard 88/88, hook 98/98, OMP port 30/30, digest validator including BUG-1898 76/76, and test-kind declaration 8/8. The dry-run probe correctly refused readiness because this validation panel currently holds feature claims; it started no OMP process and is not SC-07 evidence.

## Stage 1 — spec compliance

| Criterion | Status | Evidence |
|---|---|---|
| SC-01 | PASS | Exact feature+runtime-id refusal/release and occurrence-1 preservation pass in `tests/integration/test-validate-digest.py:5712-5761`. |
| SC-02 | PASS | Atomic create/bind/reuse/refusal is in `inflight_registry.py:396-481`; the real-registry and hook cases pass. |
| SC-03 | PASS | One resolver, one-PM preservation, unreadable run-start refusal, and DEC-100 pass-through are implemented and pass targeted suites. |
| SC-04 | PASS | Result rows reconcile by actual id in `harness-hooks.ts:375-388`; mixed/reordered/repeated-name cases pass. |
| SC-05 | PASS | Lifecycle registration is `pi.events.on` at `harness-hooks.ts:1318`; the wrong-bus mutant reddens. |
| SC-06 | FAIL | Readable-registry exact held-child and recovery-command cases pass, but unreadable-registry handling returns success from `_registry_errand` (`validate-digest.py:2304-2310`), so the rule is not enforced in that state. |
| SC-07 | PENDING OPERATOR MERGE GATE | No live receipt exists, truthfully. This panel neither ran nor failed it. |
| SC-08 | FAIL | DEC-100, index generation, and cutover text inspect correctly. DEC-204:6432-6435 says a lead/orchestrator yield is refused while any exact child claim remains live, but the implementation's unreadable branch explicitly says the contract is not enforced and passes through. |

### Finding F-01 — high · substance · T-03

`validate-digest.py:2304-2310` — if a lead/orchestrator has a live background child and the canonical `.harness/.inflight-claims.json` becomes unreadable before the parent's yield, `_held_children` raises `UnreadableRegistry`; `_registry_errand` catches it and returns `None`, so a schema-valid parent digest is accepted and the parent can settle while its child remains live. This is the fail-open form of the lifecycle defect the feature exists to close, and contradicts DEC-204's current-truth promise inspected by SC-08. **Owner:** T-03. The unreadable state should preserve all rows and refuse the parent return as an operator condition; it must not infer that no child exists.

No scope creep or omitted task surface was found beyond F-01. Because Stage 1 fails, Stage 2 code-quality review did not begin.

## Required candidate dispositions

These are assessed for routing only, not applied and not a substitute for Stage 2:

1. **`settleRun` dedupe by runtime id — dismissed.** A settled id may be woken and reclaim under the same id; session-lifetime dedupe would suppress the later settlement release. The current exact, idempotent `release-run` call is the safe cost boundary.
2. **Share `authorize_runtime_identity`'s unbound predicate — dismissed.** Authorization is the existing mutation-time contract and has a different already-filtered candidate lane. Changing its candidate selection is outside D-01/T-01's run-start cutover and buys no required behavior.
3. **Drop `_held_children` lead/orchestrator pre-filter — dismissed.** The shipped roster has non-empty `spawns:` only for the orchestrator and the three domain leads; `norm()` maps all three lead personas to `lead`. Thus no other governed dispatch-capable seat is skipped. Keeping the filter avoids a strict registry read on every return from the twelve non-dispatching personas. Reassess if a non-lead persona gains `spawns:`.

## Assessed and dismissed

- Result settlement from both `tool_result` and `pi.events` is safe because release is exact and idempotent; per-call `Set` accounting prevents duplicate rows from prematurely completing a receipt group.
- Markerless lookup fails closed on zero, multiple, or any unreadable registry and never selects by persona/name/cwd (`inflight_registry.py:324-369`).
- Exact release preserves unrelated rows and refuses ambiguous selectors (`inflight_registry.py:698-730`).
- No legacy resolver wrapper or bare-name/positional compatibility path remains.

## Principles applied

- **Model the Domain:** the review checked that run readiness is represented as explicit `unready | ready | held` state and that exact runtime identity, not names or positions, drives lifecycle transitions.
- **Delete First:** the review checked the old resolver and positional/prebinding paths were removed rather than retained beside the replacement.
- **Migrate Callers, Then Delete Legacy APIs:** dispatch guard and yield use the shared resolver without a compatibility shim.
- **Type System Discipline:** the hook's held-state union prevents a claimed-ready run from coexisting with a refusal reason; no additional finding was warranted.
