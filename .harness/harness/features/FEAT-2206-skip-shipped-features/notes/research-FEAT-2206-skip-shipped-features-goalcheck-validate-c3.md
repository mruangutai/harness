# Goalcheck — 4a351faea95ad3776f130d0f42f303a4eee3e4b9

Both signed perspectives pass on retained behavioral evidence and pinned implementation inspection. This is a product-outcome assessment, not a claim that the literal T-01 verify ran at this pin.

## Perspectives

operator — pass: SC-01/02/03 exclude shipped subjects while preserving historical ownership/worktree comparisons; evidence: notes/red-first.md:5-54,75-84; notes/review-harness-qa-c3.md:64-94; merge-b5b6fa70f27c9d92cf9ee966eb7a9447de58312e.log:217-236,4005-4011; pinned ctx._load_features, population, runner._shipped_selection and board.inv_24.
code maintainer — pass: SC-04 retires INV-28/30 without widening the shipped exemption to unreadable or non-done subjects; evidence: pinned table.RETIRED and runner._select_names; test-check-state-shipped.py RetiredMirrorChecks and ShippedSubjects; baseline retirement failures at notes/red-first.md:27-47 and passing 18-test receipt at merge-b5b6fa70f27c9d92cf9ee966eb7a9447de58312e.log:4005-4011.

## Prior must-fixes — first discharged against T-01

- C1 item 1, substance, med, T-01/SC-03: closed. A 4,301-digit shipped parent beside usable issue 11 no longer aborts INV-24: pinned board._inv24_issue_number catches ValueError from int(), and test_inv24_skips_an_oversized_shipped_number_and_keeps_usable_ones requires no traceback and the surviving cross-feature collision. Retained red/green: notes/red-first.md:79-84; green integration receipt: merge-b5b6fa70f27c9d92cf9ee966eb7a9447de58312e.log:4005-4011.
- C1 item 2, substance, low, T-01 active-validation preservation: closed. Pinned helper restores str.isdigit(), so active Arabic-Indic '٣' and integer 3 retain their collision; the dedicated test also forbids a malformed-number finding. notes/red-first.md:79-84 records baseline b7af829c PASS, c1 688c5ef5 FAIL, repaired PASS. Same green integration receipt applies.
- Superscript '²' remains contained by the same catch. artifact_accessors._positive_issue_number separately catches ValueError and returns None for its documented loader refusal. The baseline-to-pin diff of feature_json_write.py is empty: opt_int's #2151 raise contract was not changed.

## SC outcomes and trace coverage

All four criteria trace through signed T-01; operator is discharged by SC-01/02/03 and code maintainer by SC-04. No perspective or SC is orphaned.

- SC-01 met, automated: test-check-state-shipped-ctx.py classification/open-order assertions; retained baseline 10 failures and rework duplicate-key reds in notes/red-first.md:5-24,56-65; green unit receipt in merge-b5b6fa70f27c9d92cf9ee966eb7a9447de58312e.log:217-236. DEC-252 governs text-line rather than YAML-mapping classification; see Q-01.
- SC-02 met, automated: ShippedSubjects full/changed/explicit/audit-open assertions plus every-record real-corpus mode. Prior QA's 7-record/21-green and retained 21 behavioral baseline reds: notes/review-harness-qa-c3.md:64-94 and runs/validate-c1-validator/digest.md:12-16. No fresh mutable owner-corpus result is claimed by this reader.
- SC-03 met, automated: ComparisonsKeepShippedRecords tests shipped/active, shipped/shipped, sparse/full INV-24, INV-29 standing worktree, INV-52 branch collision and malformed shipped fields; round-2 tests close both remaining conversion gaps. Existing correct collisions are not misrepresented as newly red. Evidence: notes/red-first.md:29,63-84; green 18-test receipt above.
- SC-04 met, automated: RetiredMirrorChecks and retained adjacent integration controls; baseline retirement failures notes/red-first.md:37-45; prior QA green adjacent coverage runs/validate-c1-validator/digest.md:12-16; equivalent-code current suite receipt below.

## Evidence boundaries and checks performed

Read exact-pin BRIEF/plan and implementation/test changes using git show/diff, not HEAD. Measured 688c5ef5..4a351fae delta: only board helper and two integration regressions on .claude/tests. Measured b5b6fa70..4a351fae whole-tree diff: only this feature's feature.json review_sha and regate entry. Thus source, tests, configuration and fixtures are identical between those commits; the 146-file exit-zero/verify-exit=0 receipt at merge-b5b6fa70f27c9d92cf9ee966eb7a9447de58312e.log:8171-8174 transfers code evidence, not literal execution identity, mutable external corpus, or metadata-sensitive gate results. Literal exact-pin T-01 completion is left to QA's execution audit; no fresh clean exact-pin literal verify is asserted.

No tests, suites, builds, linters, formatters or probes executed by PM. No execution capability was blocked; PM deliberately collects rather than reruns QA evidence. Code-grade 60-function claim was not independently graded by PM. Disclosed INV-33 station drift, live-board mismatches and superseded round-1 regate wording are not new product findings. Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent at the pin (git ls-tree returned no entries); no control-plane substitutes were used. Binding grilling authority read-only.

## Open questions

Q-01 (nonblocking, T-01): YAML-mapping/invalid-YAML intent wording differs from DEC-252's text-line classifier. Recommendation: retain the adopted DEC-252 behavior and reconcile prose through its owner; no new implementation ruling or human decision is required for this assessment. No new findings or unclassified failures.

## Principles applied

No craft leaf cited this run. Evidence transfer is explicitly bounded under harness-verification-rules: product outcomes do not manufacture an exact-pin terminal gate receipt.
