# BUG-2190 c1 security — PASS

No actionable security finding. Inspection at `cf13aab63f308c1d59e33737205a3064fa35b194` preserves the approved offline fail-closed local boundary and authenticated remote refusal. Severity maximum: none. No checks executed.

## Pin and self-scope

- Reviewed `origin/main...cf13aab63f308c1d59e33737205a3064fa35b194` (Git merge-base comparison, not HEAD); measured all 30 changed paths. Current feature.json carries the same review pin.
- Measured c0 `33c0c181e62c5e75692c8320fc01aaaaf06fa40b` through c1: 13 paths; only the two test files change executable behavior. `board.py` has no delta. `fcc91963^..fcc91963` also includes validation records/feature metadata, so “tests only” describes implementation, not its entire changed-file census.
- IN: board.py binding/receipt authority, table.py declared auth dependency, unit/integration regressions, canonical-reader inventory and DEC-221/index's deliberate relaxation. OUT as executable surfaces: BRIEF/plan/STATE/feature metadata, amendment/signature/research/evidence/review notes and run identity/digest/state records. Their full diff was included in the credential-pattern sweep; no credential material found. Previous security review exists; its verdict was not inherited.

## Boundary and remediation assessment

- **SC-03:** `board.py:306-318` rejects non-mapping factories, raw invalid owner/name values and missing fleet membership before selecting any repository. `feature_schema.py:494-505` treats malformed factory shapes as bound, preventing owner routing. New unit `:134-141` asserts invalid binding plus exact zero resolver/product-config calls for string/list factories; integration `:173-184` requires the matching finding, zero contents reads and no traceback. Owner success cannot satisfy those positive failure assertions.
- **SC-02:** Selected factory.repo flows through the unchanged provenance/receipt predicates and `_inv37_finding` (`board.py:327-354`). Unit `:111-126` and integration `:136-158` now assert recovery verbs for missing/mismatched/unproven receipts; the owner-mismatch fixture specifically requires recover-mirror, not owner-compatible open. `feature_schema.py:151-184` confirms why that command selection discriminates the repository argument.
- **SC-01/04/05/06, regression:** Offline return is only from local repository selection, not the receipt gate. Authenticated and unbound selection still delegates to the unchanged shared resolver (`board.py:321-324`); remote FleetError is reported without retrying offline (`:338-344`). Existing tests retain valid offline twins, authenticated remote success/failure, owner controls and no-plan exclusion. Table/inventory additions do not bypass enforcement.
- STRIDE: local feature/fleet → authoritative repository (**T**, mitigated); authenticated remote config → binding (**T**, mitigated); bound repository → provenance/recovery advice (**T**, mitigated). The approved offline absence of remote attestation is not a newly discovered vulnerability; it does not authorize writes or relax merge/sweep/gh-sync.

## Evidence limits and guidance

`notes/fix-evidence-c1-2026-11-08.md` reports M4/M6 killed and green suites; these are main-authored observations, not independently executed here. QA owns exact-pin literal verification and mutation evidence. This review ran no tests/builds/linters/formatters.

Product `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent (docs directory census). AGENTS.md explicitly designates this product's `.harness/harness/docs/SPEC.md` and `DECISIONS.md`; consulted SPEC onboarding and DEC-220/221 including the signed offline amendment. No architecture content invented.

**Must fix:** none. **Open questions:** none. **Source/test changes:** none.
