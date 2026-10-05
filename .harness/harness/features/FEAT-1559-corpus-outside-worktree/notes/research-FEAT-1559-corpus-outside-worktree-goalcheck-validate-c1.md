# Goalcheck — validate c1

FAIL on collected evidence: SC-13 is partial because predicate-specific unit fail-first evidence is incomplete. SC-10 is **deferred-by-ruling**, not met and not a defect (#2101). No source/spec edits or tests executed by PM.

Pin: 0e8301a58a7de7dc23a067005c9aa8b3ee528de0; pre endpoint e8d868f78a6ec43880598af5c5873f5daa8ba985. Evidence below is existing main-session execution, not a fresh QA verdict. Structural git diff confirms code-final 69e3d81987b8a9d7676dbaf0f18674b8bf039579 to pin changes only five files inside this feature record: production, tests, fixtures and configuration are unchanged. Historical real-owner receipt is explicitly an execution-time observation, not a fresh mutable-corpus measurement.

## Perspectives
- operator — partial: SC-01/06/11 met via creation/retention tests and immutable receipt; standing conversion SC-10 deferred-by-ruling under #2101.
- reader — pass: SC-02/03/04/05/12/14 met via named read, population, refusal, equality-mutant tests and pinned guidance inspection.
- code maintainer — partial: SC-07/08/09 behavior demonstrated; SC-13 lacks complete predicate-level fail-first evidence despite positive/negative assertions.

## Criteria and traceability
Paths below are relative to the pinned repository; notes are this feature's pinned notes. Every T-01..T-06 execution owner is main-session-direct under DEC-174, not a team specialist.

| SC | Grade | Carrying evidence / tasks |
|---|---|---|
| 01 | met | test-worktree-state.py RecordBearingClasses (harness/fleet/pin, new top-level, recordless); test-worktree-state-hooks.py creator cases. suite-baseline.md:46-52; receipt-T-04.md:77-100. T-01/04 |
| 02 | met | test-feature-corpus.py CrossCheckoutReads and WriteGuards; OMP absolute read/selector and relative control, receipt-T-03.md:85-96,100-106; receipt-T-05.md:18-28,83-108. T-01/03/05 |
| 03 | met | test-check-state-corpus.py test_sparse_and_full_agree_on_the_selected_subject, test_reads_stay_in_the_active_feature_and_declared_owner_records, test_a_missing_selected_feature_refuses_before_any_invariant; receipt-T-02.md:60-81. T-02 |
| 04 | met | test-check-state-corpus.py missing recordless/untracked-extra cases; test-feature-corpus.py discovery cases; test-feature-corpus-census.py injected-unmarked, one-marker/two-marker, owner-seam assertions. receipt-T-02.md:60-81; receipt-T-03.md:85-106. T-01/02/03/05 |
| 05 | met | test-feature-corpus-discovery.py BranchClaims (duplicate, sentinels, exact pair, third claimant, empty reason); test-check-state-corpus.py duplicate-other-landed; test-feature-corpus.py MergeGate/BranchCreateGate permission payload controls and refusals. suite-baseline.md:50-52; receipt-T-02.md:60-81; receipt-T-03.md:85-105. T-01/02/03 |
| 06 | met | test-corpus-non-regression.py fresh-clone retention/no-op, hooked pull, every baseline finding; receipt-T-05.md:94-105; non-regression-receipt.md:50-69 plain-clone full-suite execution at code-final, adopted through unchanged execution subjects. T-01/02/05 |
| 07 | met | test-worktree-state.py StructuralBreaks, ClassC (active edit, staged hidden deletion, untracked/ignored, rewritten hidden, mixed A/B/C), second-repair snapshot, Report. suite-baseline.md:26-52 documents bootstrap limitation and actual B/cone regressions. T-01/04 |
| 08 | met | test-worktree-state-hooks.py four creators, merge/rebase newtop, amend/index-rewrite class A, class-C snapshot; unit shim tests preserve stdin/attribute failures/sweep. receipt-T-04.md:45-105 explicitly records Git 2.54 merge-repro substitution, not a claim that merge clears skip bits on this host. T-04 |
| 09 | met | test-check-state-corpus.py structural downstream-not-run, dirty-alone audit-runs, dirty-plus-structural and unusable-report; test-feature-corpus.py broken-layout gate cases. receipt-T-02.md:60-81; receipt-T-03.md:85-105. T-02/03/04 |
| 10 | deferred-by-ruling | BRIEF.md:37; STATE.md:37-44; non-regression-receipt.md:100-103. T-06 abandoned here, receipt owed by #2101 after merge; not met, not defect. |
| 11 | met | non-regression-receipt.md:6-48 immutable endpoints, no other-feature paths, equal 4635-entry manifests; exact code-final-to-pin structural diff confines seam to this feature record. T-05 (T-06 abandoned) |
| 12 | met | test-corpus-real-owner.py test_audited_names_equal_the_tracked_directories, test_check_state_passes_the_corpus_choke_point, staged-missing/wrong-root equality mutants, test_dirty_is_reported_and_a_structural_break_refuses; non-regression-receipt.md:71-98 records six non-skipped cases, owner HEAD and removed probe. Historical observation only. T-05 |
| 13 | partial | Named assertions in test-worktree-state-rules.py, test-feature-corpus-discovery.py, test-check-state-corpus-rules.py and test-feature-corpus-gates.py cover the predicates. suite-baseline.md:15-28 explicitly denies bootstrap red proves each predicate; receipt-T-02.md:56-59 unit ImportError; receipt-T-03.md:82-84 absent APIs plus one parity assertion. These do not establish every relevant predicate's fail-first. T-01/02/03/05 |
| 14 | met | git show pin:AGENTS.md:10; pinned harness/SKILL.md:12-19 and harness-verification-rules/SKILL.md:66-75; .harness/README.md:53-130 describes no symlink/git provider, A/B/C, repair/verify/recovery and local hooksPath. T-05 |

## Finding
- GC-01 — kind substance, severity med: SC-13's explicit each-predicate fail-first clause is only partially evidenced. Pin anchors: tests/unit/test-worktree-state-rules.py:86 (pin parser) and tests/unit/test-feature-corpus-discovery.py:54 (empty exemption reason); the retained receipts establish only bootstrap errors for those unit predicates, not their discriminating red assertions. SC-13 / T-01 (also T-02/03/05 for remaining predicates); owner main-session-direct, DEC-174. Route the evidence gap to QA, not the user or a new implementation task. QA confirmed the limitation and is collecting reds concurrently; this assessment claims none of that not-yet-published execution. Later evidence may discharge the partial grade without a code fix. No requested scope change.

## Settled-contract checks
Content classification and recordless all-segment identity match the signature rulings; no sibling/symlink/git-content provider is accepted. T-03's earlier citation statement is superseded by T-05's approved DEC-214 amendment (receipt-T-05.md:46-49,64-68), not carried as current guidance. The code-final receipt seam and T-06 deferral are operator rulings, not findings. Pinned feature.json contains an earlier review_sha; dispatch's exact pin governs this assessment, rather than fabricating execution at that metadata value.

Open questions: none. Remaining evidence action: QA predicate-specific SC-13 receipts; lead must integrate the concurrent QA report before judging ship-readiness.
