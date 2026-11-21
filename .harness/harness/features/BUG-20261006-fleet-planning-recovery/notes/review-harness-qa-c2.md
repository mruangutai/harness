# QA gate c2 — BUG-20261006-fleet-planning-recovery — validate reconciliation

**VERDICT: FAIL.** Pin `6451153169f469f5bd9d5f3f01bf89b82787b720`, attribution `4a05030d^..4a05030d`. The matrix floor and both suites are green, but the acceptance evidence for SC-01, SC-04 and SC-06 is partial. This supersedes the c1 PASS on the gate verdict only. `review-harness-qa-c1.md` is preserved unchanged, and its measurements and red-first table stand.

No execution in this pass. No test, build, lint or remote call ran, and no source or test files were touched. c1's execution report is retained verbatim:
- Unit run 1 ran concurrently with integration and exited 1. The sole failure was the 5000ms `test-omp-hooks.py` timeout under load.
- Unit rerun alone exited 0 with 61/61 files.
- Integration exited 0 with 87/87 files.

I re-read the pinned `test-gh-sync-open.py` (`git show`, read-only) to check the goal-check's SC-01 claim.

## Why c1's PASS was too lenient
c1 resolved the matrix floor correctly and found natural reds for SC-01 to SC-05. It then filed SC-06 as thin and the control removals as "advisory". `harness-verification-rules` says a green matrix does not make a criterion met. SC-01, SC-04 and SC-06 each name a specific integration outcome in the BRIEF, and for each one the integration case is absent or a unit case stands in for it. That is a gap in what the tests prove, not an opinion about wording, so it moves the gate to FAIL.

## Phase 1 expectation vs observed

**SC-01 (BRIEF line 16)** says integration cases show every feature-bound command, build-entry and board reconcile bind to `factory.repo`, and that missing or mismatched config never falls back. It also asks for failing cases first.
- **Proven by integration:**
  - `open` binding: `test-gh-sync-open.py:226` checks remote product config, a complete call log with no `owner/harness`, and provenance.
  - Refusal of unproven active fleet receipts before any mutation, for 9 commands (`:242-270`).
  - Bound board audit and reconcile refusal (`test-board-lifecycle.py:1193-1215`, cited by the goal-check, not re-read).
- **Not proven by integration:**
  - Successful bound routing for `start-task`, `status`, `record-pr`, `ship`, `abandon`, `reject`, `backlog` and `recover-terminal`. The only integration case for these commands is the refusal loop. Their success routing is inferred from shared preflight, not asserted.
  - Missing or unavailable product config and mismatched mappings as integration outcomes. The malformed-target assertions are unit cases (`test-feature-schema-build-entry.py:249-265`).
- **Fail-first:** c1 shows natural semantic reds (tier S) for `open` binding and the 9-command refusal. There is no red for the unproven success and config-failure outcomes, because no test for them exists.
- **Verdict on SC-01:** partial.

**SC-04 (BRIEF line 19)** says integration cases show evidence-based INV-7 grading with no FAIL-count floor, and explicit notes for unknown legacy attribution. It also lists INV-39/40, historical refusal vs accepted return, and the hash-bound evidence refusals.
- **Integration covers:**
  - INV-37, historical refusal surviving a later success, and hash-bound evidence (`test-check-state-records.py:985-1030`).
  - Changed evidence re-triggering INV-7 (`test-check-state-table.py:221-242`).
  - INV-39/40 (`test-check-state-feat59.py#case_inv39,#case_inv40`).
- **Integration does not cover:** the positive no-FAIL-floor outcome and the unknown-legacy-note outcome. Both exist only as unit cases (`test-feature-record.py:1578-1631`). Unit tests do not discharge an SC whose BRIEF evidence kind is integration.
- **Fail-first:** c1's natural reds for INV-37, replay and hash are semantic (tier S). The historical-refusal reader case is signature-absent (tier A, `AttributeError resolve_evidence_ref`).
- **Verdict on SC-04:** partial.

**SC-06 (BRIEF line 21)** says live DEC-237 negatives keep rejecting. It also says historical refusal provenance cannot satisfy live validation or excuse an unexplained missing complete-run digest, and that the new provenance regression must fail first.
- **Live negative controls are retained and pass.** `test-validate-digest.py:656-670,947-965,1506-1521,1576-1612`. They are correctly retained, but they pass before and after the fix. They show the old contract survived. They are not a red for the new regression.
- **The new provenance regression has no explicit negative-control integration test.** `validate-digest.py` has no code path that reads refusal provenance, and no test asserts that one cannot exist. No mutant that makes the live path accept provenance is covered.
- **Reader-side half:** the "cannot excuse an unexplained missing complete-run digest" assertion sits inside `case_historical_refusal_completion` (`test-check-state-records.py:985-1030`). Its only pre-fix red is signature-absent (tier A).
- **Signature-absent red vs no test:** the tier-A red proves the feature was absent before the fix. It does not prove the unexplained-missing-digest assertion rejects a wrong implementation. That is better than no test, but it does not discharge "regression failing first".
- **Verdict on SC-06:** partial. This is the largest gap.

**SC-02, SC-03, SC-05.** Natural reds and passing tests exist (c1 table). Per the goal-check, SC-05 lacks a sufficiently specific named pre-fix refusal-provenance receipt in the audited record. c1 reproduced reds for it: three tier-S subTests, plus tier-A reds for the verdict, valid-return and crash cases. I count SC-05 as satisfied on c1's own reproduction. This is own evidence only, with no second reviewer (O-07). SC-02 and SC-03 stand as in c1.

## Removed controls: behavioural gap vs wording opinion
- **Wording locks.** The deleted message-conjunct checks (`"missing 'task_verify'"`, `"drifted"`, `"undeclared digest key"`) and the two hint cases are incidental wording. The 2026-10-18 build note justifies them. Rejection of the malformed returns is still asserted. I am not raising these.
- **`test_does_not_import_live_schema`.** It pinned that the historical reader does not import the live validator schema. The path it guarded is now exercised by the retained live-negative controls and the reader integration case. I do not claim a behavioural consequence from its removal. It is not a coverage gap or an open question, and I am not asking the operator to adjudicate it. If SC-06's missing negative-control test is written, it should cover the same independence at the behaviour level.

## Gaps and routing
These are task-owned work for T-01 (main-session-direct), not scope changes. They need no human decision and carry no assertion that the source is wrong.
1. SC-01: add integration cases for successful bound routing of each remaining command, and for missing or mismatched config outcomes, each shown red against pre-fix `c4e8bbc8`.
2. SC-04: add integration cases for the no-FAIL-floor and unknown-legacy-note outcomes.
3. SC-06: add an integration negative control showing a refusal-provenance record cannot make live validation accept a digest, with a red against a mutant.

## Principles applied
None of the leaves under `harness-craft/references` was read this run, so none is cited. `harness-verification-rules` governs the verdict above.

## Cleanup
No pin or worktree was created in this pass.
