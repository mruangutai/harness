# Security review — BUG-2390 — c1

PASS — no introduced exploitable input-validation, fail-open, serialization, authorization, injection or exposure regression.

- **Scope IN:** caller-authored expertise ops cross policy stdin; classification governs enforcement. Reviewed intake `9eb07b4f..780f9138dc3423c45368aa5334f06bd2532e0e8f` and independently compared the recorded main baseline `9a818b46071dadd58d2c59b4dd29d398fc4701e7..780f9138`. The latter isolates the two implementation files, BUG-2390 records and two BUG-2399 completion-metadata changes. Inherited BUG-2399 implementation is not attributed to this payload repair. Existing security coverage: `notes/review-harness-security-reviewer-c0.md`.
- **Classification (T/E):** structured denial and exit 2 still precede shape inspection (`.omp/extensions/harness-hooks.ts:410–433`). Broad-gate unavailable behavior is unchanged. Array narrowing supplies no command; actual narrow-gate callers construct their own object envelope (`:557–566,1728–1733,1916–1930`). An agent submitting ops cannot substitute an array for that envelope. The new test's synthetic failed merge gate on an array is not a newly reachable enforcement bypass.
- **Validation/authority (T/E):** non-array ops still refuse with the same message; `opsList` returns the checked array without transformation (`:970–986`). Caller lineage, destination containment and registered distillation authorization still precede forwarding (`:1602–1686`). Receipt handling still refuses explicit policy errors and missing receipts (`:1047–1056`). No authorization grant changes.
- **Serialization/exposure (T/I):** `runPolicy` still serializes the supplied value using `JSON.stringify` (`:525–529`); wrappers forward unchanged (`:542–547`). No new shell interpolation, argv construction, network destination, dependency, credential use or production logging. Credential-term inspection of the complete baseline-to-pin diff found only review prose, not credential values. Test-only array diagnostics do not add production exposure.
- **c1 identity/evidence:** Git diff proves production is identical to `369096a4`; the test delta is exactly four added lines, including one assertion at `tests/unit/omp-hooks.test.ts:2163–2166`, with no assertion removal. Independently diffed `9eb07b4f..2a479efd`: production adds only the unused exported alias. Historical receipts record reconstructed TS2345 at argument position and green 214 pass / 1554 expects; these are inspected records, not independently executed checks. Original red remains separately recorded.

## Principles applied
Type System Discipline — distinguished honest object-or-array transport typing from runtime authority; checked narrowing removes the array-as-object assertion without treating the union as authorization.

Guidance: product AGENTS.md map, SPEC §§4.2/5.3; DEC-31, DEC-50, DEC-174 and DEC-214. Source read-only; no tests, builds, formatters or linters run. QA owns current-pin typecheck and hook-suite verification.

Findings: none. Must fix: none. Open questions: none.
