# FEAT-68 code review — validate c2

## Verdict

**FAIL.** Stage 1 does not discharge SC-04/VF-04: the preserved scripts exist only under the feature directory, but `clean-pin-byte-receipts.md` says its commands are exact invocations from repository root and invokes them as `notes/receipt-scripts/...`, a path that does not exist from that root. Stage 2 therefore was not reached.

Reviewed immutable range `e655f14a56a14bf1777cae55a19195c9af10505d..ab17ca1705f85846c446c0921d53ad3544d5b300`; implementation pin `9ab1813e86067ca4a21a84f49364cf4f453055b4`.

## Stage 1 — specification compliance

- **SC-01 met.** The committed red-first record names all five baseline targets at grade 1, and the pinned mechanical grade run reports every introduced function at grade 4 or 5 with no failing or grade-2 record (`notes/red-first-receipts.md`; `notes/clean-pin-byte-receipts.md`).
- **SC-02 met.** The clean receipt now states checkout-root-only normalization and is consistent with its 53/57 table, exact retained D-01..D-05 differences, and A-1..A-3 (`notes/clean-pin-byte-receipts.md`; `notes/build-divergences.md`; `notes/answers-validate-validator.md`).
- **SC-03 met by inspection.** The implementation diff is limited to the five settled decompositions, renderer/residue deletion, the prescribed reference/comment changes, the stale grade exemption removal, and moved source-anchor fixtures. Ordered rules, short circuits, finding order, comments, and deny fallback remain represented in the diff.
- **SC-04 not met.** Both full SHAs, chronology, and the three committed script blobs are present, and the measurements are unchanged. However, the stated repository-root commands 2 and 3 use `notes/receipt-scripts/feat68-*.py`; neither `/Users/molchairuangutai/GitHub/harness/notes/receipt-scripts/` nor the feature-worktree-root `notes/receipt-scripts/` exists. The scripts actually reside at `.harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts/`. Thus the record does not contain exact executable repository-root invocations.
- **SC-05 preconditions met, sequenced observation pending.** The source/residue assertions, unit+integration matrix record, implementation pin, renderer deletion, and Markdown-only design are present. The final actual ship-review Markdown/no-HTML-sibling observation is correctly left to the orchestrator after a clean panel and is not itself a finding here.

### Finding CR-C2-01

- **kind:** form
- **severity:** med
- **binding / owner:** T-01 / main-session-direct
- **scenario:** An auditor follows `notes/clean-pin-byte-receipts.md` from the stated repository root and runs command 2 or 3; Python exits before capture/comparison because `notes/receipt-scripts/...` does not exist, so VF-04's reproduction cannot be executed from the recorded instructions.
- **remedy:** Replace the three script paths in the repository-root invocations with their actual repository-relative feature paths (or state and use a real working directory whose relative paths resolve), without changing scripts, chronology, measurements, rulings, or SHAs.
- **anchors:** `notes/clean-pin-byte-receipts.md` § “Reproduction (VF-04)”; `notes/receipt-scripts/feat68-baseline.py`; `notes/receipt-scripts/feat68-cleanpin.py`; `notes/receipt-scripts/feat68-grade-assert.py`.

## Stage 2 — code quality

**Not reached because Stage 1 failed.** The independently run mechanical grade command over the full pinned range passed 34 reported changed/new functions (all grade 4 or 5), so `code_grade: pass`; this does not substitute for Stage 2.

## Principles applied

None cited.
