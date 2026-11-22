# Goal-check completion — BUG-2187 — validate c1

G-01 is resolved. Exact-pin green and authentic base-red are now supplied. SC-03 is met; SC-01/02 remain partial on specifically promised automated safety coverage, not provenance or an observed production defect. QA's PASS is preserved; it does not establish every clause of the literal goal.

Subject: 1b35414bfc865786baffe0418528deeeef141272; base: 5bd9efd411a4b4a7a6a09dcf7517946c75c5f220. Same run 2026-11-21-02-validate-validator; completion of the initial assessment, not a new review or replan. The c0 note remains unchanged. All evidence below is collected, not rerun.

## G-01 resolution

QA's notes/review-harness-qa-c0.md:18–54 binds execution to the pin. The verbatim T-01 command, python3 tests/integration/test-check-state-records.py && python3 tests/unit/test-feature-record.py, exited 0 in 52.6s: integration 44 ok lines/no FAIL; unit 128 OK. The base-red subject ee550318 is measured between the immutable base and pin, with no .claude/tests differences from base; pinned tests overlaid there produce two actual INV-33 failures and eight unit AssertionErrors, not setup failures. Thus both halves of G-01's question are answered. Auxiliary canonical-reader audit, structure-lock suite, code grade and standing unit/integration runners also passed (QA c0:26–36). Historical receipt incompleteness no longer blocks any SC.

## Perspectives and traceability

- operator — partial: T-01 traces to SC-02/03. Pinning, documented seam and rework counting are implemented and their principal regressions pass; SC-02's shared-writer safety is not bound by its tests. Spend outcome is met.
- code maintainer — partial: T-01 traces to SC-01. Lifecycle/content discrimination is implemented and defect-exposing regressions pass, but the promised regression defence of safety boundaries is incomplete. Neither declared perspective nor SC is orphaned.

## Criteria

- SC-01 — partial (automated/integration). QA c0:29,38–41,51–52 proves station-only/serialization base-red to pin-green via cases inv33.e/f; inv33.g exercises approval.status and its control mutant reddens (c0:57). Existing content/restoration cases and pinned inspection support correctness (notes/review-harness-code-reviewer-c0.md:7; check_state/feature_record.py:66–114,130–197). However task-nested status can be wrongly stripped with the suite green; three named silences and placeholder have no assertions (QA c0:59–69,74–76). The literal SC names arbitrary nested status and preservation of all five silences/placeholder; T-01 explicitly calls for the existing silence boundaries in tests. Those clauses are not fully automated evidence, even though inspection finds them preserved.
- SC-02 — partial (automated/unit). PinReviewTest at tests/unit/test-feature-record.py:1278–1309 provides genuine absent-verb red and pin-green for default HEAD, explicit refs/full ids, refusal/no mutation and both guidance documents (QA c0:29,42–44,53,67,70). Pinned review confirms _apply retains the shared writer and seam order (code reviewer c0:8). But the SC expressly includes successful pinning using feature_json_write; a direct-write mutant survives. T-01 also explicitly requires asserting unrelated-field preservation; destructive-field mutants survive (QA c0:62–63,77). Correct implementation inspection cannot supply those missing regression assertions. This is narrower than demanding arbitrary extra mutants or every writer failure mode.
- SC-03 — met (automated/unit). SpendTest:1231–1254 covers direct fixes, multiple rounds, exact >= boundary, earlier/non-regate exclusion, replacement rather than summation, no validate and fallback. QA c0:29,45–47,54,57 supplies authentic direct-fix/boundary red and pin-green; the boundary mutant fails. Pinned review c0:9 confirms cycles_used and existing spend/hook semantics are retained. No comparable-timestamp outcome required by this SC is reported uncovered.

## Five disclosed gaps — proportional disposition

1. Unloadable/legacy byte fallback: real advisory regression weakness; inspection supports the constraint today. No demand for every mutant to die, and not an independent reason to deny the principal SC-01 fix.
2. Task-nested status: contributes to SC-01 partial because arbitrary nested status is explicitly named; top-level approval.status coverage is not task-nested execution evidence.
3. Three silences/placeholder: pre-existing, not a production regression; nevertheless expressly retained in SC-01 and requested in T-01's regression intent. Their preservation is inspected, not fully regression-defended.
4. Shared writer/unrelated fields: contributes to SC-02 partial for the exact SC writer clause and explicit T-01 preservation assertion. No finding that the current code bypasses the writer or mutates those fields.
5. Naive/aware guard: advisory defensive-branch coverage, not an additional SC-03 acceptance case. Historical red-receipt formatting is remedied by QA's reproduction, not an outstanding gate.

QA's classification completion (notes/review-harness-qa-c1.md:12–27) calls all gaps advisory and says they exceed the SCs. I agree that none demonstrates a current production defect or changes the green matrix; I do not adopt that blanket scope characterization for the explicitly named SC-01 boundaries and SC-02 writer clause. Return those bounded evidence gaps to the owning implementation/QA route, not to the user as a request to execute tests. This assessment authorizes no source/test changes, new scope, or replan.

## Principles applied

- docs/PRINCIPLES.md, Verification is the product: separate passing matrix/principal regressions from unexercised acceptance clauses.
- docs/PRINCIPLES.md, No more specific than necessary: do not turn defensive timezone coverage or every surviving mutant into new acceptance criteria.
- docs/PRINCIPLES.md, Never falsify the record: preserve c0, close its answered provenance finding, and distinguish inspected correctness from regression assurance.

Open questions: none. G-01 is closed; the remaining limitations are known coverage gaps, not unanswered provenance questions. No source, BRIEF, plan or approval changed; no checkout, test, check, build, lint, formatter or probe was executed.
