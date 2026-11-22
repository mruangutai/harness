# PASS — T-01 preserves canonical strict schema authority

Reviewed `7f9cc9d8..297913318472d066ecb9d5eb3f83ee2ca82c3ad7` in the assigned PRODUCT worktree. All implementation and source citations below bind to that pin, read through Git objects. Dispatch-supplied review pin is authoritative; feature.json at the pin has `review_sha: none`.

**Scope IN:** dispatcher-controlled task JSON crosses into hook-owned persona return contracts (STRIDE T/E). Full census: hook implementation and regression tests assessed; DEC-237/index assessed as boundary policy; ten feature planning/evidence/state files assessed for changed enforcement or secrets, neither found. No dependencies, network requests, shell construction, exports or new credentials are introduced. Full-range credential-shaped text sweep found only token-accounting metadata.

## Boundary assessment — T-01 / SC-01..03

- `.omp/extensions/harness-hooks.ts:379–389`: acceptance requires a Harness target, literal `strict`, and an own outputSchema deeply equal to that same target's canonical projected bundle. Key-order independence does not permit a different schema. Unknown/unloadable bundles return false, so controls are refused rather than trusted.
- `harness-hooks.ts:393–409`: batch-top-level controls always remain forbidden; every item is independently inspected and indexed. A permitted early copy cannot hide a later invalid item. Non-Harness controls and incomplete/non-strict pairs remain refused.
- `harness-hooks.ts:416–427,1474–1491`: successful copies are replaced with the canonical bundle and strict mode; all schema checks/loading precede dispatch-guard claim creation. The equality check does not become a caller-selected contract or authorization bypass.
- Unchanged `.omp/extensions/digest-schema.ts:59–67,115–188,194–275,298–315`: persona allowlist, contained file/reference resolution, cycle/unsupported-projection refusals, frozen success-only cache keyed by real schema root and canonical persona remain authoritative. Caller schemas are compared, not loaded/resolved as schema sources. Live semantic validation remains at `harness-hooks.ts`'s yield branch.
- `tests/unit/omp-hooks.test.ts:1743–1763` asserts canonical object identity after independent/reordered copies for every persona and both shapes; `1789–1859` asserts tampering, cross-persona, incomplete/mode, non-Harness, batch-top-level, later-item and unloadable-persona refusals before claims. Assertions inspected, not executed here.

**SC-04 inspection:** `.harness/harness/docs/DECISIONS.md:7917–7928` states precisely the accepted exception and preserved refusals/re-injection/fail-closed behavior. The pinned diff leaves live-yield/durable-record clauses unchanged and shifts only subsequent index anchors by the amendment's five added lines.

## Dismissed concerns / limits

- Copy acceptance is not proof of provenance, nor needs to be: canonical equality plus canonical replacement confers no schema-selection capability. Changed schemas are refused, not silently overwritten.
- Prototype/getter-based exceptions are not supplied by task JSON; no concrete new attacker capability demonstrated. No speculative finding.
- Batch-top-level/non-Harness controls, host persistence and disclosed #2257 typecheck gap remain the signed boundaries, not new findings.
- Red/green receipts read as builder claims; no baseline failures rerun and no tests/builds/lint/formatters executed. QA owns the final `set -eu; bun test tests/unit/omp-hooks.test.ts` gate.

Findings: none. Must-fix: none. Open questions: none. Severity maximum: none. No source or test changes.
