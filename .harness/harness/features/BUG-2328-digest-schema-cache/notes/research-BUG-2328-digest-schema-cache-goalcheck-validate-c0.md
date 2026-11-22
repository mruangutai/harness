# BUG-2328 goalcheck — validate c0

PASS: delivered freshness and preserved contract coverage meet SC-01..03 at pin `1a26bc9fbb4c4ebadf9b9a6a268ca757aa358c00`. T-01 traces to every SC and owns both implementation files. No source/test edits or verification commands were run by this reader; supplied committed execution receipts are evidence, not a new QA execution claim. QA's concurrent final digest was not yet published when consulted.

## Perspectives and criteria

- **operator: pass** — SC-01 met: pinned `tests/unit/omp-hooks.test.ts:2760-2771` loads a temporary directory, rewrites the referenced common definition, and requires the added persona field on the next load. Pinned `notes/receipts/sc01-red.txt` records the actual stale-second-bundle assertion failure against unchanged dd04e52a loader, exit 1; `notes/receipts/sc01-sc02-green.txt` records 186 pass, 0 fail, exit 0 after the fix.
- **code maintainer: pass** — SC-02 met: pinned `tests/unit/omp-hooks.test.ts:1708-1710` covers all sixteen persona schemas through whole-item toEqual; `:1754-1766` retains structural copy acceptance and distinct-copy assertions; `:2754-2758` covers repeat/alias/alternate-path equivalence. Same green receipt carries the direct Bun suite. SC-03 met: pinned `.omp/extensions/digest-schema.ts:294-309` documents per-call loading and instantiates a fresh loader, without process cache; `:97-103` preserves per-loader documents. Base-to-pin diff leaves aliases, projection and other loader behavior unchanged; no replacement cache or reload mechanism is added. Module header describes synchronous reading without an obsolete cached-lifetime claim.

Receipt transfer: build `cf5ef3ea` and pin have no differences in either implementation/test file (inspected git diff); the pin adds only the simplify note. The receipts do not claim null typecheck or generic runner success.

## Recorded deviations

Both are goal-equivalent, not scope regressions. Deleting the redundant outputSchema identity assertion preserves the promised content comparison through whole-item toEqual (`:1710`), rather than duplicating it. BUG-2305's two overlooked identity checks now use not.toBe(copy) (`:1761,:1766`), while their preceding whole-result toEqual checks prove canonical content; `:1756` still proves distinct copies. These remove cache-identity assumptions while preserving canonical reinjection rather than caller-copy passthrough, matching DEC-237. They are inside T-01's existing file ownership, not additional production behavior.

## Decision dispositions

All four plan rows are **keep**. Canonical PM Mode 2 grades only amend/strike; therefore each literal disposition status is **not graded (keep); conformance met**, not a fabricated amendment landing. Owning pinned path for every citation: `.harness/harness/docs/DECISIONS.md` at the pin above.

- DEC-174: keep; conformance met — `:4458-4461` says execution through Harness is not allowed; signed T-01 explicitly routes main-session-direct, consistent with supplied main-direct execution provenance. No decision edit requested.
- DEC-179: keep; conformance met — `:4788-4791` requires declaration in the plan; pinned lanes and T-01 declare both files before the supplied signed-plan commit f502a7a8.
- DEC-225: keep; shipped-patch conformance met — `:7405-7409` specifies bounded brief, one task and no intake panel/goalcheck. Brief is below 120 lines and plan has exactly T-01. This explicitly requested validation-time goalcheck is a hosting/process exception, not a shipped code defect or a claim that the no-goalcheck clause disappeared. DEC-174 supplies the direct-execution carve-out from the ordinary team default.
- DEC-237: keep; conformance met — supplied clause is present at `:7959-7963`; `:7955-7957` also requires canonical reinjection of an accepted structural copy. Fresh load preserves canonical source/projection/strict injection, and both deviations preserve that contract.

## Operator advisories

- kind: process; severity: low; scope: DEC-225 / validation hosting, outside SC-01..03; reader: harness-pm; summary: requested validate goalcheck differs from the signed no-readers/no-goalcheck intake wording; why: preserve an honest process record without recasting this main-requested review as a patch failure.
- kind: verification-gap; severity: medium; scope: SC-02 / T-01, standing infrastructure; reader: harness-pm; summary: #2257 null typecheck and #2329 generic unit runner missing Bun remain unresolved; why: direct Bun receipts prove runtime coverage only, not static correctness or generic discovery. Neither gap is introduced or repaired here.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs** — removed cache-identity assumptions are judged against preserved content and reinjection contracts; no compatibility cache is warranted.

Open questions: none. No amend/strike remediation task is required. Product docs/spec.md, docs/decisions.md and docs/architecture.md remain absent as supplied; no replacement guidance was invented.
