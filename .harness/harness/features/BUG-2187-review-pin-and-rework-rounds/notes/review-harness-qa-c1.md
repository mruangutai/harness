# QA finding classification — BUG-2187 T-01 @ 1b35414b (run 2026-11-21-02-validate-validator, c1)

BLUF: Form completion of `review-harness-qa-c0.md` (unchanged). Verdict, executions, base-red reproduction,
fail_first and mutation proofs are in c0 and are not restated or altered. No new tests, probes or checks ran.
Original judgements made explicit below; no severity or kind was lowered to suit PASS.
**must_fix: none.** No gap requires it despite the green matrix (reason at the end).

## Classified findings (c0 "Coverage gaps", all task T-01)

| # | severity | kind | location | gate effect | reason |
|---|---|---|---|---|---|
| 1 | med | test-gap | tests/integration/test-check-state-records.py (inv33 cases e–g); feature_record.py:84-89 | advisory | Bytes fallback for unloadable/legacy (PLAN.md) plan has no case; mutants M-C and M-L stay green. A regression treating an unparseable edited plan as equal would hide a real plan edit, which is the exact defect class INV-33 guards. Production is correct today; the test does not defend it. |
| 2 | low | test-gap | tests/integration/test-check-state-records.py inv33.g; feature_record.py:71-72 | advisory | Nested-status boundary pinned only on top-level `approval.status`; task-nested `status` (M-E) unguarded. Narrower than item 1: the stripped-status path is exercised once and the control mutant reddens. |
| 3 | low | test-gap (pre-existing) | tests/integration/test-check-state-records.py; feature_record.py:197 | advisory | Three of five silences (no git work tree, unresolved pin, absent disk plan) and the placeholder have no case before or after this change. Preserved, not regressed by the diff. |
| 4 | med | test-gap | tests/unit/test-feature-record.py PinReviewTest; feature-record.py:607-619 | advisory | Unrelated-field preservation and shared-writer use (M-P/M-Q/M-R, 128 OK) are unasserted although plan intent line 57 requires them. A pin-review that bumps `cycles_used`, wipes judgements, or bypasses the lock/schema ships green. |
| 5a | low | test-gap | tests/unit/test-feature-record.py SpendTest; feature-record.py:673 | advisory | Naive-vs-aware timestamp guard in `_not_before` untested (M-N2, 128 OK). Defensive branch; failure would surface as an error, not silent miscount. |
| 5b | none | evidence-form | receipts/red-inv33.txt (and red-feature-record.txt) | advisory, remedied | Historical red receipts hold ok/FAIL labels without violation text or stderr. Already remedied: my own reproduction in c0 (base-red section) supplies the defect lines and assertion diffs. Item 5 in c0 merged this with 5a; they are two defects and are split here with no new content. |

Unrated: none. Every finding carries one kind and one severity; no recommendation for lead open_questions
is needed for classification. Item 1 and 4 are the strongest candidates if the lead wants a follow-up test task.

## must_fix
None. All findings are advisory: every SC (01/02/03) has a natural-RED fail-first in c0, both required kinds
are `satisfied`, and every pinned verify/audit exits 0. The surviving mutants (items 1, 2, 4, 5a) are
strength gaps beyond what the SCs name; correct production today does not dismiss them, so they stay in
`coverage_gaps` rather than being waived. If the lead judges the bytes-fallback (item 1) or field-preservation
(item 4) in scope of the plan intent, that is a lead decision to dispatch a dev test task, not a QA gate failure.

## Principles applied
Fail-first stays graded on the c0 natural-RED reproduction (O-03); severity tokens are the contract literals (G-09); the merged item is split rather than averaged (O-04).
