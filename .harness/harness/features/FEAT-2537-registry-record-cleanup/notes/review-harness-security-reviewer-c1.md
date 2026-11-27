# T-01 security review — FAIL, two stop-and-rule deltas

Reviewed `a24eacee718898c4512379de1fe87b9611a7df43..8ae96bea9dd8eb0f412c654158cbb3050322cfff`. An existing non-v2 registry in the requested shape census **never returns no claims from the pinned strict reader**. But the dispatch caller can turn the new unreadable result into task-supplied authority, and the locked writer can discard a live record that the signer characterized as a warning-only change for malformed v2. Neither is the already accepted strict refusal of `{}`, the warning for a malformed-v2 file without recoverable rows, or the case-18 expired-count change.

## Findings

1. **Substance · med · T-01 — Unreadable sibling suppresses the registered distill dispatch check.** With a live distill lead in one worktree and `{}` in an unrelated linked worktree, the base lookup finds the lead, but the pin's `find_run_claim` returns `unreadable` and no claim (`inflight_registry.py:320–338,342–357`). `dispatch-guard.py:748–759,771–789,792–808,843–855` falls back to the proposed task's feature. For an ordinary member dispatch proposing a different, non-distill feature, that fallback can skip the registered parent feature/mission refusal that the base reaches. Even a correctly marked same-feature task may lose a trusted placement signal through this fallback; the vulnerability is the different-feature authorization decision, not the signed reader error. Preconditions are a ready distill lead, an unrelated unsupported registry, an otherwise admissible member task with a different assignment, and no other denial; this does not mint distill authority or bypass the child's later lineage checks. Measured the changed lookup with a live v2 claim and an isolated sibling (controlled worktree enumeration); downstream admission is source-traced, not run through the hook. Preserve the distinction between lookup failure and unbound dispatch at this caller, or obtain an explicit ruling on the changed preflight.
2. **Substance · med · T-01 — Malformed envelope recovery can now erase live claims, not just warn.** A malformed v2 object can contain a list under a different key while `claims` is not a list. With one OMP row carrying a live supervisor and matching persona/feature, base strict already refuses, but base `live_claim` salvages and preserves the row. At the pin the same locked query warns, returns `(None, 0)`, and commits empty v2 (`inflight_registry.py:57–94,506–523`). An explicit invalid version with a `claims` list similarly loses the row; unversioned live lists and live persona maps have the same fold. Dispatch admission is **not** strict: its initial query and second locked claim both use the recovering parser (`dispatch-guard.py:857–889`; `inflight_registry.py:526–560`). With a damaged envelope holding a live same-feature PM claim, the pinned query removes evidence before the second check; a subsequent strict reader sees readable v2, not the original damage. A stale/external writer or envelope corruption is a prerequisite; no current writer emits a non-v2 envelope and no agent write capability into the registry is asserted. The warning reports the file, not the lost claim or recoverable payload. D-01 orders an empty fold generically, but the signature explicitly resolved malformed v2 as a diagnostic change with unchanged on-disk result, then required a ruling on other deltas. Preserve recoverable evidence before admission, or have the signer explicitly rule on this measured live-record case and its dispatch consequence.

## Base → pin shape census

Isolated probes loaded both pinned module blobs into Python and used temporary registries, a live supervisor, and exact-parent criteria. No deployed guard, repository registry, or integration suite was run. Strict reads left the tested bytes unchanged. `U` = `UnreadableRegistry`; numeric cells are counts (`_read_strict` rows / exact-parent `live_claims` rows). `E` = writer commits empty v2; `L` = matching live row retained and returned. Writer uses a matching feature except the historical runtime-less case below.

| File shape | Strict base → pin | Locked writer base → pin |
|---|---|---|
| Missing file | `0/0 → 0/0` | Absent → absent |
| Empty file | `U → U` | `E → E`, silent |
| Truncated JSON | `U → U` | `E → E`, warns both |
| JSON list / scalar / null (each) | `U → U` | `E → E`, warns both |
| `{}` | `0/0 → U` | `E → E`, new warning |
| v1 persona map, live matching row | `1/1 → U` | `L → E`, new warning |
| v1 persona map, historical runtime-less row | `1/0 → U` | Unscoped query expires one at base vs zero at pin (signoff and case-18 red receipt); empty v2 both |
| Explicit v1 with live row in `claims` | `U → U` | `L → E`, new warning |
| v2 missing `claims` | `U → U` | `E → E`, new warning |
| Unversioned `{"claims": []}` | `0/0 → U` | `E → E`, new warning |
| Unversioned `claims` with live row | `1/1 → U` | `L → E`, new warning |
| v2 non-list `claims`, no other list | `U → U` | `E → E`, new warning |
| v2 non-list `claims`, live row in another list | `U → U` | `L → E`, new warning |
| v2 with live row | `1/1 → 1/1` | `L → L`, silent |
| Version numeric `2.0`, empty list | `0/0 → 0/0` | `E → E`, silent; pre-existing Python equality with `2`, not a newly accepted shape |

## Strict caller census and boundaries

- Three direct callers of `_read_strict`: `live_claims` (propagates `U`), `claim_run_start` (returns structured `unreadable`, CLI exit 2, hook holds run), `repository_binding` (returns `unreadable`, both product write guards deny). Run-start preflight is outside its write lock; it is not a guarantee about a different snapshot read by the writer.
- Four `live_claims` callsites: `_live_claims_for_run` collects unreadable roots; `harness_boundary._registry_claim_worktrees` feeds `claim_worktrees` and both Write/Edit and Bash guards (refuse incomplete evidence unless a readable claim independently proves destination, DEC-218); validator `_settle_in` reads its own exact id and `_held_children` reads exact parent id then filters feature. Both validator reads refuse a non-`BLOCKED` lead/orchestrator result at exit 2, without release. The existing leaf / `BLOCKED` continuation logs unreadable and does not release; neither is a no-child assertion. For an unchanged missing-file result, the strict readers act on no rows, not on unreadable evidence.
- Five `find_run_claim` consumers: `release_run` refuses without release, CLI `find-run` exits 2 and markerless OMP placement holds, `digest_destination._check_runtime_claim` denies digest binding, validator `_claimed_run` refuses distill authority, and dispatch `_dispatcher_feature` falls back (finding 1). These outcomes apply to every `U` cell above; base accepted rows go through normal persona, feature, lineage and liveness selection.
- `live_claim`, receipt creation, runtime authorize, attach, release/reconcile and CLI `list` are recovering writers; `list` can print `NO CLAIMS` after a fold. Normal dispatch single-flight checks live records on the writer side. The unchanged fail-open policy on registry I/O/lock exception is separate from successful recovery into an empty v2 snapshot. The new warning contains only the resolved local registry pathname and fixed text, with no registry contents, credentials, or claim identifiers. It is not a substitute for the discarded claim evidence.

## Scope and immutable evidence

SC-01: pinned production `live_children` search exits 1; exact-parent positive control is `validate-digest.py:2914`. SC-03: pinned ledger clauses at `DECISIONS.md:6038,6614,7263`, with ledger commit `d1777a89` before code `8764b820`. Validator, canonical inventory, prior fixture and frozen validator integration test each have equal base/pin blob IDs. SC-04: hook diff is comment-only; verified held-run retry and the nonawaiting OMP bus against `harness-hooks.ts:1716–1720,1934–1952,2071–2082` and `event-bus.ts:24–46`. The registry, related tests and governing records were in scope; other feature-management artifacts do not change enforcement. Open: signer ruling or remediation for the two findings above.
