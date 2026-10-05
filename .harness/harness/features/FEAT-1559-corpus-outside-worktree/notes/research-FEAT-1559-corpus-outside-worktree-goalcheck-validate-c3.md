# Goalcheck — validate c3

**PASS for completed grading, not an assertion that every promise is delivered.** At exact SHA 6c11ab626ed568236978b1640928162b8cf0139f, the c2 population defect is repaired; SC-04/05 are met on inspected implementation and recorded discriminating execution. SC-13 remains partial with the existing substance / med historical assurance advisory G-5; SC-10 is deferred-by-ruling (#2101). No new must-fix, replanning, edits to source/tests, or PM test execution.

## Done when perspectives
- **operator — partial:** SC-01/06/11 support sparse creation, ordinary clones and preserved corpus; SC-10's standing conversion is explicitly deferred to postmerge #2101, not credited as delivered.
- **reader — pass:** SC-02/03/04/05/12/14 support landed reads, subject completeness and duplicate detection. Collision repair now retains both segment/id directories and exercises board and merge consumers; SC-12 is historical host evidence, not a current mutable-owner measurement.
- **code maintainer — partial:** SC-07/08/09 support deterministic state, safe repair and gate boundaries; SC-13's per-predicate pre-production evidence remains incomplete.

## One grade per criterion
Repository paths below mean the exact pin above; receipt paths are under this feature's notes. All automated evidence is collected from execution receipts/readers, never re-executed by PM. Traces read from the approved plan; T-06 is abandoned.

| SC | Grade | Evidence and traces |
|---|---|---|
| SC-01 | met | test-worktree-state.py RecordBearingClasses; test-worktree-state-hooks.py recordless creation; receipt-T-04.md:77-100. T-01/04. |
| SC-02 | met | test-feature-corpus.py CrossCheckoutReads/WriteGuards/DecisionAnchors; receipt-T-05.md:83-108 absolute/selector/relative controls; prior QA local-anchor mutant. T-01/03/05. |
| SC-03 | met | test-check-state-corpus.py selected-subject equality, confined opens and missing selection; receipt-T-02.md:60-81. T-02. |
| SC-04 | met | feature_corpus.py _directory_key/_local_entries/population use (segment,id) in BOTH maps, replace only the identical pair, sort (id,segment). test-feature-corpus.py SegmentIdentity x2 + BoardStatus.test_one_id_active_in_two_segments_is_audited_in_both; receipt-main-session-fix-c2.md:28-41 records four prior-production reds and fixed passes. Existing name-set, missing-landed and census scratch controls retained. T-01/02/03/05. |
| SC-05 | met | New MergeGate.test_one_id_claimed_from_two_segments_is_two_owners_and_denies asserts permissionDecision deny and both claimant labels; same receipt:35-41 records red/pass. Existing exact-pair, third claimant, empty reason, sentinel and allow controls retained. T-01/02/03. |
| SC-06 | met | STATE.md:54-56 records fixed-code suites exit 0, unit 52/integration 80 files; prior QA exact-pin ordinary-clone suites and test-corpus-non-regression.py retained. Full baseline-to-pin changed-path census has no .github paths. This is recorded evidence, not PM/current QA execution. T-01/02/05. |
| SC-07 | met | test-worktree-state.py StructuralBreaks/ClassC/mixed A-B-C snapshots and idempotence; suite-baseline.md:30-39 and prior QA dirty mutants. State implementation unchanged from c2. T-01/04. |
| SC-08 | met | test-worktree-state-hooks.py creators/merge/rebase/refusal; test-worktree-state-hooks-rules.py delegates/stdin/sweep. receipt-T-04.md:45-105 bounds Git 2.54 class-A index-rewrite substitution; no claim of observed merge-cleared skip bits. T-04. |
| SC-09 | met | test-check-state-corpus.py structural downstream-not-run and dirty controls; prior QA board broken-layout mutant; preflight calls _layout and refuses before context. T-02/03/04. |
| SC-10 | deferred-by-ruling | Approved BRIEF amendment: conversion after merge under #2101; plan T-06 status abandoned. No receipt credited here. |
| SC-11 | met | Independently inspected entire e8d868f78a6ec43880598af5c5873f5daa8ba985..6c11ab626ed568236978b1640928162b8cf0139f changed-path census: no other-feature directory changed. non-regression-receipt.md:6-48 freezes endpoints and equal 4635-entry manifests at code-final; this extends preservation, not its obsolete no-production-delta claim. T-05. |
| SC-12 | met | non-regression-receipt.md:71-98 six non-skipped real-owner checks; prior QA converted-caller observation; test-corpus-real-owner.py unchanged. Historical execution-time population only: no fresh mutable-owner measurement inferred from unchanged source or clone skips. T-05. |
| SC-13 | partial | test-worktree-state-rules.py and test-feature-corpus-discovery.py negative cases plus prior QA predicate mutants establish current discrimination, not each predicate's historical pre-production red. Existing G-5 substance / med remains bounded assurance advisory, NOT a new code must-fix. T-01/02/03/05. |
| SC-14 | met | Exact-pin AGENTS.md:10; harness/SKILL.md:12-19; harness-verification-rules/SKILL.md:66-74; .harness/README.md:58-135 distinguish local writes/absolute landed reads, reject sibling/symlink/git providers and explain repair, dirty recovery and non-cloned hooksPath. T-05. |

## Evidence boundaries and disposition
Full c2-to-c3 changed-path census inspected: only production delta is feature_corpus.py, only test delta is test-feature-corpus.py; complete deltas inspected. Prior evidence remains attributed to its execution commit, not represented as re-execution. ctx.population remains unchanged: check_state/corpus.py:108-111 verifies before context, and feature_corpus.active_paths refuses duplicate active-id segment claims before that context exists. No new active-context defect established.

Retained advisories: G-5 substance / med (SC-13 historical ordering), QA G-1 advisory and G-4 inconclusive; twelve grade-2 retention findings belong to code review. No classification/severity invented for G-1/G-4. General Stage-2 code quality and independent c3 QA execution belong to their readers, not this product grading. The historical feature.json committed at the exact pin names the prior review; the authoritative feature-tree feature.json names 6c11ab626ed568236978b1640928162b8cf0139f, matching the explicit dispatch used for this assessment. cycles_used 2 counts main-session fix rounds. This reader sent back nobody.

Open questions: none. No UAT criteria. Own managed pin (validate-c2-validator / harness-pm) removed successfully; no clone created; sibling pins untouched.
