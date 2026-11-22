# BRIEF — BUG-2328 Refresh digest schema data on every load

## Problem

A long-running OMP process can inject an obsolete digest contract after schema files change: the process-lifetime BUNDLES map retains the old provider bundle. Operator-verified evidence in the grilling records a missing required persona field after #2252; no invalid durable digest landed. Source: issue #2328; supplied baseline dd04e52a.

## Done when — by perspective

**operator** — I can dispatch with the schema data currently on disk instead of a contract retained from an earlier dispatch.

**code maintainer** — I can rely on a behavioral regression against stale schema data, preserved equivalent alias/path contracts and injection behavior, and comments describing the actual loading lifetime.

## Success criteria

- SC-01 (operator): A behavioral regression loads from a temporary schema directory, rewrites common.json to add a required field, then loads again and observes that field in the second provider bundle. Preserve the actual failing assertion and nonzero exit against dd04e52a before the production fix, and passing assertion and exit 0 after; wording/source-text assertions do not count as regression evidence.
  verify: automated; evidence: unit
- SC-02 (code maintainer): Repeat loads, main-session/backend-dev aliases and alternate paths to the same directory remain equivalent by toEqual rather than toBe; all sixteen persona injection checks compare outputSchema content with toEqual, while the distinct-copy not.toBe(injected) assertion and unrelated checks remain intact. The targeted Bun unit suite passes after the fix.
  verify: automated; evidence: unit
- SC-03 (code maintainer): Read git show <review_sha>:.omp/extensions/digest-schema.ts: the process-lifetime BUNDLES cache is removed, loadDigestSchemaBundle loads/projects files on every call, module/function cache comments describe that lifetime, and existing aliases, projection and per-loader BundleLoader.#documents behavior remain unchanged. No replacement cache, mtime/hash tracking or host-reload mechanism is added.
  verify: inspection

## Verification gaps

- typecheck is unresolved with cmd null for TypeScript: static type correctness is not proven by a configured runner. SC-01/SC-02 use direct bun test tests/unit/omp-hooks.test.ts; SC-03 uses pinned code inspection instead. Existing issue #2257 owns the standing typecheck gap; it remains unresolved, not skipped or claimed green.
- The active unit kind detects tests/unit/omp-hooks.test.ts, but issue #2329 records that its generic run-unit-tests.py command does not discover Bun test files. Direct Bun execution is mandatory evidence here; repairing the generic runner is outside this two-file patch. No criterion rests on the generic runner alone.
- PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in the assigned checkout. No guidance is invented or substituted; the operator-confirmed grilling settles this bounded patch.

## Constraints

- DEC-174 BLOCKS team execution of this hook-library change: it injects every Harness dispatch's digest contract, so main executes the entire hook regression patch directly.
- DEC-179 SUPPLIES explicit main-session-direct routing and the lanes table before signature.
- DEC-225 SUPPLIES the operator-confirmed patch mission: at most 120 brief lines, exactly T-01, no panel and no goal-check; DEC-174 governs execution rather than the ordinary team default.
- DEC-237 SUPPLIES canonical schema loading/projection and strict dispatch injection; preserve its contracts without amendment.
- Only .omp/extensions/digest-schema.ts and tests/unit/omp-hooks.test.ts change. Update existing module/function cache comments in the library, not an additional documentation file. Remove BUNDLES without a replacement cache, mtime/hash tracking or host-reload work.

## Out of scope

- **The hook's own TypeScript code is loaded once per OMP process.** A change to harness-hooks.ts or digest-schema.ts still needs a host restart. That is host behaviour, not ours. This patch covers only the schema data the hook reads.
- BundleLoader.#documents: it is per-loader (per call), so it is never stale across dispatches. It stays as it is.
- The Python side (digest_schema.py via validate-digest.py --hook) runs as a fresh subprocess per yield and is never stale.
- No broader issue #2195 work: the operator states it is closed as resolved by #2230; this patch addresses only the residual schema-data cache.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-11-22
