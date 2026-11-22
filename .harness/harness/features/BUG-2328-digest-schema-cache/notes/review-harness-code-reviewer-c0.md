# Code review — BUG-2328 — c0

**PASS — T-01 satisfies SC-01..03; no findings. Both recorded test deviations preserve behavioral assurance.**

Reviewed pinned git content over `dd04e52a898109fdbe09cf5fa14e1148161734d0..1a26bc9fbb4c4ebadf9b9a6a268ca757aa358c00`. Merge-base matches supplied base; all three commits belong to this feature; no `[harness:human]` commits. Only observed dirty path was feature metadata, not implementation. Exactly two implementation paths changed; remaining additions are feature records/evidence. No changed Python: mechanical code_grade is **n_a**, as reported by the digest gate (not a code-quality failure).

## Stage 1 — specification compliance

- **SC-01 / T-01:** `tests/unit/omp-hooks.test.ts:2762-2771` loads a temporary referenced schema, rewrites `common.json`, then requires the new required `persona` field in the second projected bundle. Pinned `notes/receipts/sc01-red.txt` records that exact stale-output assertion failing against the base loader, exit 1; `sc01-sc02-green.txt` records 186 pass / 0 fail, exit 0. Supplied evidence, not reruns by this reader.
- **SC-02 / T-01:** repeat, alias and alternate-path equivalence use content equality (`:2754-2758`). All sixteen injection outputs are compared through whole-task equality (`:1708-1710`); unrelated checks and distinct-copy assertion (`:1756`) remain.
- **Deviation 1 accepted:** deleting redundant `outputSchema.toBe(bundle)` rather than adding another `toEqual` loses no content coverage: whole-task equality already binds that field. Wrong persona/content or missing strict injection still fails.
- **Deviation 2 accepted:** BUG-2305's cache-identity assertions become `not.toBe(copy)` (`:1761,1766`). Whole-result equality (`:1760,1765`) proves canonical content; new assertions reject passing the caller's object through. Shared cached-object identity is intentionally no longer contractual. Both changes serve SC-02.
- **SC-03 inspection / T-01:** `.omp/extensions/digest-schema.ts:294-309` documents per-call reads and constructs a fresh loader before loading, projecting and recursively freezing. BUNDLES declaration, lookup and store are removed without replacement. Aliases, projection, freeze and per-instance `#documents` behavior remain unchanged. No tracking, dependency or host-reload mechanism added.

Stage 1 passed before Stage 2.

## Stage 2 — code quality

No introduced fail-open or silent fallback found. Missing/malformed/escaping references still throw. Injection refuses bundle failures before dispatch claims (`.omp/extensions/harness-hooks.ts:1781-1796`); copied controls whose current bundle cannot load are refused (`:667-697`). Fresh calls cannot return an earlier successful bundle after a later file failure. Assertions execute the real loader/hook; literal expected schema content prevents undefined-return decoration. Cache restoration is the stale-output mutant discriminated by the preserved red receipt; no mutant execution performed here.

## Principles applied

- **Delete First:** removal eliminates state and branches without another lifetime mechanism.
- **Migrate Callers, Then Delete Legacy APIs:** identity-dependent assertions migrate to content/re-injection behavior; no compatibility cache remains.
- **Type System Discipline:** no new cast, parallel schema authority or unchecked boundary; parsing/projection remains intact.

## Open questions and verification limits

None. No tests, builds, lint, formatters or smoke runs performed. QA owns subsequent explicit verification. Standing #2257 null typecheck and #2329 generic Bun discovery remain unresolved, not green, and are not introduced here. Product guidance absence is disclosed by BRIEF; no substitute requirements invented.
