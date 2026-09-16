# BRIEF — BUG-1756-qa-reverify-bash Run QA re-verification with Python

## Problem

Operators validating an unconditional qa PASS are blocked even when its claimed matrix is green because validate-digest.py asks bash to read the Python test runner. The resulting import error is mistaken for a red matrix, so honest PASS digests are refused and the validator's recorded result must be worked around.

## Done when — by perspective

**operator** — I can rely on an unconditional qa PASS being independently checked against the matrix kinds it claims: a green rerun is accepted, while a genuinely red rerun is refused with useful output.

**code maintainer** — I can rely on regression coverage to distinguish an actual Python runner invocation from the broken bash invocation, verify kind forwarding and the default runner path, and preserve the existing fail-open and disagreement behavior.

## Success criteria

- SC-01 (operator): Given an unconditional qa PASS that names unit and integration evidence, re-verification executes the runner once with each named kind and accepts the claim when both executions succeed; the integration test demonstrates that this case fails before the fix and passes after it.
  verify: automated        evidence: integration
- SC-02 (operator): When a named-kind rerun returns non-zero, re-verification stops at that first failure, reports the runner's real output tail, and refuses the disagreement with exit 2; the integration test demonstrates its failing state before the fix.
  verify: automated        evidence: integration
- SC-03 (operator): When the claim names no evidence kinds, re-verification executes the runner without a kind selector so its default set governs whether the claim is accepted or refused; the integration test demonstrates its failing state before the fix.
  verify: automated        evidence: integration
- SC-04 (code maintainer): The integration regression fails while bash is used to launch the Python stub and, after the fix, passes while also proving that a missing runner, spawn error, or timeout still reports could not independently re-run and returns 0, while a completed non-zero rerun still returns 2 for disagreement.
  verify: automated        evidence: integration

## Verification gaps

none — the integration test kind has an active runner and covers this validator boundary.

## Constraints

- DEC-174 BLOCKS team execution because validate-digest.py and its test are gate surfaces; implementation, explicit tests, and diff review are main-session-direct.
- DEC-225 SUPPLIES the patch lane: this known-cause, bounded bug has one task and is gated on its diff after approval.
- Keep the existing digest interface, schema, and enforcement boundary unchanged; change only how the existing qa PASS re-verification launches and observes the existing test runner.

## Out of scope

- Re-verifying at review_sha instead of the feature checkout's HEAD; that pinning behavior requires a separate ticket if wanted.
- INV-43 and BUG-1723's own seam grading.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-16
