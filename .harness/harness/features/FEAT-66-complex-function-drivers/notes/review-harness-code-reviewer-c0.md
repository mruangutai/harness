# FEAT-66 T-01 pinned code review — c0

## Conclusion

**FAIL. Spec compliance fails before code-quality review.** The pinned implementation contradicts signed D-02, and the permanent driver-grade suite contradicts the BRIEF's “only grade lock” constraint. Per the two-stage protocol, code-quality review was not entered. The independent mechanical grade run over `cb6f8050..c4ea33bc` passed all 92 reported changed/new functions.

## Stage 1 — spec compliance: FAIL

1. **D-02 accumulator ownership is not implemented** (`plan.yaml:29-31`; `.claude/skills/harness/bin/plan-merge.py:992-1020`; `notes/build-divergences.md:21`). D-02 says each phase helper returns phase-local deltas and **only `apply_merge` extends the named lists**. Instead `_merge_keys` delegates all six accumulations to `_fold_merge_rows`, which owns and extends the lists. D-06 records the departure but does not amend D-02; an implementation ledger cannot supersede a signed decision. Concrete failure scenario: a maintainer changing phase ordering or adding a seventh receipt delta follows D-02 and edits `apply_merge`, but the actual accumulation seam is hidden two helpers down, so the new delta is omitted or ordered differently while the driver still appears compliant. **Must fix:** restore driver-owned ordered accumulation while retaining the grade bar, or obtain an approved plan amendment changing D-02 before re-review.

2. **A second permanent grade lock was added** (`BRIEF.md`, Constraints; `tests/unit/test-driver-grades.py:1-52`). The BRIEF says the established `code_grade` ratchet remains the only grade lock and forbids adding a second checker or lock. The new suite permanently selects the three driver names and enforces grade ≥4 or exactly 2. Concrete failure scenario: the fleet ratchet’s selection/binding policy changes, but this independent permanent selection continues enforcing the old three-name policy, producing two authorities for which functions are gated. **Must fix:** remove the permanent lock; retain the already-committed red-first receipt and use the signed verify’s direct `code_grade.grade_source` assertion as evidence, or amend the approved constraint.

SC-01’s numerical bar, SC-02’s byte receipts, SC-03’s production-file boundary/comment relocation, and SC-04’s post-pin evidence-file ordering were otherwise supported by the inspected pin and receipts. These do not waive the two explicit constraints above.

## Stage 2 — code quality: NOT RUN

The protocol requires Stage 1 to pass before Stage 2. Mechanical grading was still run because `code_grade` is a mandatory audit claim: `code-grade.py --base cb6f80505721292c0c799cf03b0af6b180ba2970 --head c4ea33bc0ff93b11a846f24d70923ce108aa1358` reported `PASSING: 92`, no `SEVERITY: high`, and no grade-2 reason records. Thus `code_grade: pass`; this does not cure spec failure.

## Assessed and dismissed candidates

- **D-01/D-02 mutant-anchor changes:** dismissed. They retarget source-slicing mutants onto the extracted rule bodies and preserve the observable red condition; they are ledgered and serve SC-01/SC-03.
- **D-04 missing `test-validate-digest-shadows.py`:** dismissed. The file is absent from both baseline and branch, and the amendment narrows files/verify without weakening SC-01..SC-04.
- **D-05 `load_policy` movement:** dismissed at Stage 1. It remains inside the code-reviewer branch and its only outcomes are the same value or an exception before return; no success criterion or decision fixes its exact call position.
- **D-07 lifted `_head`/`deny` closures:** dismissed. This is decomposition local to `shape_problems`; existing explanatory bytes remain with the rules and receipts report unchanged outputs.
- **D-08 appended rationale sentences:** dismissed. The original rationale bytes remain and the marked additions reconcile them with the post-refactor structure; this does not rewrite or drop a load-bearing comment.
- **Fail-open, silent-failure, order, short-circuit, accumulation, and comment-loss candidates beyond the two spec failures:** not adjudicated as quality findings because Stage 2 was correctly stopped after Stage 1 failed.

## Scope and pin

Reviewed `cb6f80505721292c0c799cf03b0af6b180ba2970..c4ea33bc0ff93b11a846f24d70923ce108aa1358`. No `[harness:human]` commits are in range. The only dirty tracked files were Harness run-state records (`STATE.md`, `feature.json`), so pinned source bytes remained reviewable.

## Principles applied

None cited; the findings rest directly on the signed BRIEF and D-02.
