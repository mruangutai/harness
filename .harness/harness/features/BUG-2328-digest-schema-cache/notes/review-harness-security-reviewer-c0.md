# Security review — BUG-2328 — c0

PASS: fresh schema loads introduce no exploitable security regression; both recorded test deviations are sound. No findings or must-fix items.

Reviewed pinned diff `dd04e52a898109fdbe09cf5fa14e1148161734d0..1a26bc9fbb4c4ebadf9b9a6a268ca757aa358c00`, including all 14 changed paths. In scope: schema files become provider-interpreted dispatch contracts, so cache lifetime crosses a Tampering boundary. The twelve feature-record/evidence paths introduce no executable loading behavior; full-diff credential sweep found only a null tokens field and a public issue URL, not credentials.

## T-01 / SC-01..03

- SC-01: the regression asserts initial projected content, rewrites referenced `common.json`, and asserts the newly required field on the second load (`tests/unit/omp-hooks.test.ts:2762-2772`). Supplied receipts preserve the stale-field failure (`sc01-red.txt`, exit 1) and subsequent full-suite success (`sc01-sc02-green.txt`, 186 pass, exit 0); not rerun here.
- SC-02: repeat, alias and alternate-path checks use content equality (`tests/unit/omp-hooks.test.ts:2754-2758`). Deleting the redundant outputSchema identity assertion is sound: the immediately preceding whole-item `toEqual` checks outputSchema content for all sixteen personas (`:1708-1711`). BUG-2305's two `not.toBe(copy)` replacements are also sound: adjacent whole-result equality checks retain the canonical-content requirement while the identity checks prove caller copies are replaced (`:1759-1766`); `not.toBe(injected)` remains (`:1756`). Neither deviation weakens the caller/canonical-schema boundary.
- SC-03 inspection: `.omp/extensions/digest-schema.ts:294-309` removes the sole process-wide BUNDLES map/get/set, constructs a loader per call, projects and freezes each result, and documents fresh loading. Canonical persona checks, reference containment/refusal, projection and per-loader document caching are unchanged in the pinned diff. No replacement cache or host-reload mechanism appears.

## Threat assessment

Schema-file authority → provider outputSchema (T): mitigated. Fresh reads retain canonical persona selection, realpath/reference containment, unsupported-schema refusal and immutable results. Hook loading failures still refuse dispatch rather than substitute a loose schema (`.omp/extensions/harness-hooks.ts:1782-1793`). A writer of the canonical schema files already controls the contract; freshness grants no new authority. Caller copy → injected schema (T): mitigated by content checks and authoritative reinjection (`harness-hooks.ts:667-707`). No changed auth, network, subprocess, export, secret or cross-user-data surface was identified.

## Principles applied

Migrate Callers, Then Delete Legacy APIs: the internal cache is fully removed without a shim; identity-dependent tests migrate to content/reinjection behavior in the same patch.

## Verification and open questions

Read-only inspection and credential sweep only; no tests/builds/lint/formatters executed. QA owns the explicit `bun test tests/unit/omp-hooks.test.ts` verification. Standing #2257 typecheck and #2329 generic Bun-discovery gaps remain unresolved, not newly introduced or claimed green. Open questions: none.
