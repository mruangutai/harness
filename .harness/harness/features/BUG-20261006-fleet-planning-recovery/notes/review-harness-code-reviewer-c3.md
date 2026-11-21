# FAIL — LABEL still bypasses the authoritative binding resolver

Pin `a80b9ef3b2a30b1fa73101385a15b71b873cf09b`; fix range `6451153169f469f5bd9d5f3f01bf89b82787b720..a80b9ef3b2a30b1fa73101385a15b71b873cf09b`. T-01/main-session-direct owns the remaining high finding. No suites or live operations executed.

## Stage 1 — compliance and four prior must-fix dispositions

1. **OPEN (partially resolved), high, T-01 / SC-01 / D-01:** the exact foreign-number collision is fixed: `_label_record_owner` rejects a different `factory.repo`, and the paired collision/same-repository assertions require respectively zero/one label writes (`tests/integration/test-board-lifecycle.py:1046-1079`). Unreadable mappings now produce non-actionable residuals (`board_lifecycle.py:929-972,1130-1135`), not the former broad fallback. However, LABEL never calls `feature_schema.resolve_binding`: `board_lifecycle.py:974-984` accepts equality of `factory.repo`, audited repository and `github.repo` as sufficient. **[INFERENCE: source-traced, not executed]** With owner `acme/widget`, a record `{factory: {repo: acme/widget}, github: {repo: acme/widget, issues: {T-01: 17}}}`, and no declared fleet entry (or unavailable/sync-disabled/mismatched product configuration), owner-repository `reconcile --apply` still authorizes `issue edit 17 --repo acme/widget --add-label abandoned` when #17 is NOT_PLANNED without that label. `_resolve_board:301-308` takes the owner board without validating that feature; STATUS's separate refusal does not cancel LABEL's actionable finding (`:536-539,1198-1210`). `resolve_binding` would refuse this record (`feature_schema.py:514-529`). Thus the same-repository positive fixture actually accepts an undeclared binding, rather than proving a valid same-repository mirror. Reuse the shared resolver and turn resolution failure into a report-only residual; retain a **valid declared/configured** same-repository positive control and add an invalid-config no-write control. This is the remaining requested ownership cutover, not new scope.
2. **RESOLVED, prior SC-01 integration gap:** `test-gh-sync-open.py:278-365` exercises successful bound commands and explicit configuration refusals; assertions observe product calls, exclude owner calls and require no mutations/receipt on refusal. These close the prior command-coverage omission, not item 1's independent board consumer defect.
3. **RESOLVED, prior SC-04 gap:** `test-check-state-records.py:1066-1101` invokes actual run-end/check-state readers, requires legacy note presence, and combines that with absence of violations for three FAILs against total one. A restored FAIL floor or missing legacy notes reddens these assertions by inspection.
4. **RESOLVED, prior SC-06 gap:** `test-check-state-records.py:1104-1172` records real refusal provenance before live validation, rejects the same prose at close with byte-unchanged state, and positively requires the unrelated missing-digest violation. Accepting refusal hashes as live returns reddens the explicit live rejection by inspection. Mutation execution remains QA's responsibility.

**SC-07 inspection:** pinned `DECISIONS.md:2992-2998,3675-3689,7187-7219,7929-7940`, index DEC-157/220/221/237, and existing `github-mirror.md:35-39`, `ledger.md:28-42,48-59`, `build-phase.md:20-25` agree. Removing unreadable-record broad fallback does not reverse an adopted governing clause. Code's remaining bypass violates that consistent guidance. Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent (directory census); assigned Harness adopted decisions plus BRIEF/D-01..04 supply the applicable authority. SC-02/03/05/08 are unchanged; operator UAT was not rerun.

## Stage 2 — quality evidence

Before substantive source review, independently ran the requested grader over `fbff8150..pin`: **PASSING: 23**, no grade-2/high records. Repeated only the required grading over canonical merge-base `64511531..pin`: the same 23 pass (four production helpers, nineteen test functions; four Python paths). `code_grade: pass`. The helpers are local and readable; the substantive maintainability/correctness defect is duplicating binding policy rather than using its owning seam. No additional quality findings.

Git reconciliation found no modified tracked source or human-attributed commits. HEAD advanced only feature.json after the pin; inspected source/test/governing-document bytes remain pinned. Fix evidence claims were read as receipts, not independently executed test results. No amendments weaken the acceptance anchor.

## Principles applied

- **Model the Domain:** repository-string equality is not the existing binding interface's declared/configured authority; require the shared resolver instead of a second ownership approximation.

## Open questions

None. QA alone should execute the new binding-refusal regression and valid same-repository control after T-01 remediation.
