# Security review — BUG-1898 — c0

**PASS at `84c3a6cbe74c7c27337d4372a68be60fca834118`.** This diff is security-scoped because it consumes host/runtime identity and controls shared claims, writes, settlement, and recovery. No exploitable regression was found.

## Result

- Exact host runtime and parent ids govern run-start binding; markerless recovery refuses zero, duplicate, corrupt, or unreadable registry results (`inflight_registry.py:267-430`, `harness-hooks.ts:851-936`).
- Settlement and digest release select exact runtime id plus feature, never persona/name/result position; ambiguous release removes nothing (`inflight_registry.py:372-388,700-810`, `validate-digest.py:2236-2322`).
- Registry ownership reads are strict and mutations use `harness_merge.locked_update`; an unclaimable run executes no tool except a syntactically BLOCKED yield (`harness-hooks.ts:1002-1005,1147-1150`). DEC-100 dispatch crash pass-through therefore does not create an authorized unclaimed writer.
- Lifecycle/task results settle by actual result id. Recovery commands target one agent/claim id. The manual cutover requires raw before/after enumeration and one evidence-backed release per known-dead row, forbidding bulk, persona-only, reconcile, live, and ambiguous release (`notes/ship-checklist.md:24-105`).

## Assessed and dismissed

- **`_held_children` role pre-filter:** retained correctly. At this pin only the orchestrator and three squad leads are governed dispatchers, and all normalize to `orchestrator`/`lead` (`validate-digest.py:548-560`). No other governed persona has `task` or spawns. Removing it would impose strict registry/process-liveness reads on every leaf return without closing a reachable boundary. Reassess if another governed persona gains dispatch capability.
- **Unreadable digest registry pass-through:** releases nothing and preserves rows. Exploitation requires registry filesystem control outside governed write grants and grants no capability beyond that stronger control; this is availability/audit posture, not a privilege delta.
- **Strict-read-before-lock race:** Harness writers are serialized and atomically replaced. Corrupting the file in that interval requires out-of-band filesystem authority that already controls the registry.
- **Ambiguous `feature_root` fallback:** creating ambiguous registered worktrees requires operator-level worktree control; the feature-root CLI refuses ambiguity and exact-id recovery refuses duplicate matches.
- **Settle dedupe:** correctly rejected because a revived run reclaims the same id and needs a later release. **Shared authorization predicate:** correctly rejected because it changes receipt candidates without curing a demonstrated security defect.
- The full 28-file diff adds no credential, SSRF, SQL/shell interpolation, spreadsheet export, or cross-tenant response surface.

## Proof

`test-inflight-registry.py` passed 161/161; `test-validate-digest.py` passed all groups including 76/76 BUG-1898 exact-release checks; `bun test tests/unit/omp-hooks.test.ts` passed 98/98 (272 expectations). SC-07 remains the operator-run merge gate; it has no receipt and was intentionally not run or graded.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Security PASS at 84c3a6cbe74c7c27337d4372a68be60fca834118: exact runtime identity, strict discovery, targeted release, and BLOCKED-only refusal close the reviewed paths; SC-07 remains the operator gate."
  in_scope: true
  scope_reason: "The diff crosses the runtime-to-registry trust boundary and governs write authorization, shared claim ownership, child settlement, and operator recovery."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "OMP runtime identity -> governed run claim", stride: "S|T|E", mitigated: true }
    - { boundary: "linked-worktree registries -> markerless recovery", stride: "S|T|I|D", mitigated: true }
    - { boundary: "task/lifecycle result -> exact claim release", stride: "T|E", mitigated: true }
    - { boundary: "governed parent return -> live-child retention", stride: "T|D", mitigated: true }
    - { boundary: "operator cutover -> legacy claim deletion", stride: "T|R|D", mitigated: true }
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-security-reviewer-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-security-reviewer-c0.md
```
