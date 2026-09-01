# BRIEF — BUG-1081 Code-grade enforcement

## Problem

A code reviewer reports `code_grade` as `pass`, `fail`, `grade_2`, or `n_a`. `validate-digest.py` confirms that the report ends at the feature's `review_sha`, but for `pass`, `fail`, and `grade_2` it never runs the mechanical check. A review can therefore pass when `code-grade.py` was skipped, crashed, or produced a blocking result that was reported incorrectly. Issue #1055 demonstrated the crash class; issue #1081 records the remaining enforcement gap.

## Goal

Make the enforcement layer calculate the code-grade result for the repository-owned review range and reject a code-reviewer digest that disagrees with it. The reviewer continues to own human judgment: ordinary findings, `must_fix`, severity, and grade-2 reasons.

## Definition of Done

The work is successful when a reviewer cannot get a green review by merely writing `code_grade: pass`. On a pinned change containing a blocking new or worsened function, the digest validator rejects that claim. On a genuinely clean pinned change, it accepts the matching claim. If grading crashes or cannot inspect the canonical range, validation refuses the review and names the grading failure. GitHub issue #1081 remains linked to the defect throughout delivery and its board card reaches `Done` only after the reviewed fix is merged. That final board move is tracked by the existing ship/close gate; it is deliberately not a pre-merge success criterion that goal-check would be forced to mark unmet.

## Requirements

- REQ-01: A code-reviewer's `code_grade` claim is checked against a mechanical result calculated from repository state, not trusted as evidence of its own correctness.
- REQ-02: The mechanical calculation uses the feature's pinned `review_sha` and a base derived by the repository; neither boundary is chosen by the digest.
- REQ-03: A missing, crashed, unparseable, or otherwise incomplete mechanical calculation refuses the code-reviewer digest rather than accepting it.
- REQ-04: The four existing result names remain `pass`, `fail`, `grade_2`, and `n_a`, and existing grade bars and grade-2 treatment do not change.
- REQ-05: Reviewer judgment remains able to fail an otherwise clean mechanical result through findings, `must_fix`, severity, and the existing review policy.
- REQ-06: Plan reviews remain `code_grade: n_a` and do not attempt to grade a code diff before one exists.

## Success Criteria

- SC-01: In a purpose-built repository whose canonical reviewed range adds a blocking production function, a `code_grade: pass` digest is accepted before the fix and rejected after it, with the mismatch named.
  verify: automated      evidence: integration
- SC-02: The same fixture accepts `code_grade: fail` with `VERDICT: FAIL`, proving the validator discriminates instead of rejecting every graded code review.
  verify: automated      evidence: integration
- SC-03: Canonical ranges producing `pass`, `grade_2`, and `n_a` each accept the matching digest value, while at least one wrong value for each result is rejected and every mismatch names the expected value.
  verify: automated      evidence: integration
- SC-04: A committed Python syntax error in the canonical range rejects validation with a named grading error and no traceback; the same digest was accepted before the fix.
  verify: automated      evidence: integration
- SC-05: A digest-supplied base that differs from the repository-derived base cannot change the mechanical result, while its head must still resolve to `review_sha`.
  verify: automated      evidence: integration
- SC-06: Production and active-test paths keep their existing grade bars, blocking grades still outrank grade 2, and grade 2 still requires a non-empty reason.
  verify: automated      evidence: unit
- SC-07: A non-code plan review still validates only as `reviewed: plan:<path>` with `code_grade: n_a` and does not invoke the grading seam.
  verify: automated      evidence: integration
- SC-08: A clean mechanical result still cannot override a failing `must_fix` or high-severity review-policy result.
  verify: automated      evidence: integration
- SC-09: The code-review guidance states that the reviewer reports findings and grade-2 reasoning while `validate-digest.py` independently checks the mechanical result; it also states that no changed Python path means `n_a` and a mismatch refusal names the expected value.
  verify: inspection
- SC-10: Inspection reads `git show <review_sha>:.claude/skills/harness/bin/test-validate-digest.py` and confirms the committed integration tests drive the real validator entry path and contain their pre-fix RED evidence for the intended mismatch and grading-failure reasons.
  verify: inspection
- SC-11: For an ordinary `pass`, `fail`, or `grade_2` claim, an unresolvable default branch, a missing merge base, and a degenerate range each refuse validation with a specific remediation-bearing error; none silently falls back to the digest's base.
  verify: automated      evidence: integration
- SC-12: Inspection reads `git show <review_sha>:.harness/harness/docs/DECISIONS.md` and confirms the decision records enforcement ownership, canonical-range derivation, the availability consequence, fail-closed behavior, and the retained human-judgment boundary.
  verify: inspection

## Verification gaps

None for the changed behavior. `unit` and `integration` both have active runners. This feature changes no UI, service API, database, or model behavior, so the unresolved `component`, `ui`, `eval`, and `typecheck` runners do not cover an affected surface.

## Constraints

- DEC-122 supplies the SubagentStop enforcement point: malformed or contradictory digests are rejected at source.
- DEC-123 supplies the precedent that arithmetic or deterministic roll-ups are computed rather than trusted; human review judgment is not mechanized.
- DEC-127 requires hook behavior to be exercised through its real entry path and distinguishes rejection from a crash.
- DEC-174 blocks Harness team execution of changes to `validate-digest.py` and `test-validate-digest.py`; those edits are main-session-direct. It permits team work on the grading library, but the cutover that makes the validator consume it remains main-session-direct.
- DEC-207 supplies the separate pre-signature plan-review target, which has no code diff and must remain unaffected.
- The result vocabulary and grade bars shipped by FEAT-43 are retained. This defect changes who computes and verifies the result, not what grades mean.
- A second independent grading implementation is out of scope. Re-execution catches skipped runs, crashes, and false reports; semantic correctness of the one grading implementation remains protected by its contract tests and mutation evidence.

## Approval

status: approved
approved_by: operator
date: 2026-09-01
