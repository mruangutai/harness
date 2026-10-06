# Goalcheck — validate c2

**FAIL on literal assurance, not a demonstrated product defect:** SC-04's discovery hole and SC-02/04 consumer evidence gaps are closed; SC-13 remains partial on the signed historical pre-production requirement. SC-10 is deferred-by-ruling (#2101), not missing delivery. No replanning, source edits, test authorship or test execution.

## Perspectives
- operator — partial: SC-01/06/11 met; standing conversion SC-10 deferred-by-ruling, with no defect charged here.
- reader — pass: SC-02/03/04/05/12/14 met on the bounded evidence below.
- code maintainer — partial: SC-07/08/09 behavior supported; SC-13's each-predicate historical evidence is incomplete.

## Criteria and traces
Paths are repository-relative at review SHA 42856abb91a3a87b9f27ebc933cc363a900afd3d; receipts are in this feature's notes. Automated outcomes collect main-session/c1 QA evidence, not PM re-execution. T-01..T-05 are main-session-direct; T-06 is abandoned. No handoff gap.

| SC | Grade | Evidence / tasks |
|---|---|---|
| 01 | met | test-worktree-state.py RecordBearingClasses and recordless creation tests in test-worktree-state-hooks.py; suite-baseline.md:46-52, receipt-T-04.md:77-100. T-01/04 |
| 02 | met | test-feature-corpus.py CrossCheckoutReads/WriteGuards and NEW DecisionAnchors: landed history absent locally passes; unavailable owner exits 2. receipt-main-session-fix-c1.md:37-43 records discriminating local-routing mutant. OMP absolute/selector and relative controls: receipt-T-05.md:83-108. T-01/03/05 |
| 03 | met | test-check-state-corpus.py sparse/full selected-subject equality, confined opens and missing-selected refusal; receipt-T-02.md:60-81; QA c1:109-110 mutation attribution. T-02 |
| 04 | met | check-plan-routes.py:802 calls require_landed BEFORE the walk; feature_corpus.py:185-201,253-260 compare tracked/reached directory names. NEW Discovery missing-owner and missing-full-clone assertions require exit 2; sparse case asserts no examined output. NEW BoardStatus compares owner-only active-plan cards and broken-layout refusal. Fix receipt:8-43 records old-route red and consumer mutants; existing check-state name-set and census scratch/marker controls remain. T-01/02/03/05 |
| 05 | met | test-feature-corpus-discovery.py:29-63 sentinel/exact-pair/third/empty-reason cases; test-check-state-corpus.py duplicate owner claim; test-feature-corpus.py MergeGate/BranchCreateGate permission payloads and allow controls. QA c1:96-98,112-113 discrimination. T-01/02/03 |
| 06 | met | test-corpus-non-regression.py fresh plain-clone/no-op and immutable baseline findings; STATE.md:49-50 records fix-seam full suites 52/80, exit 0. C1 independent exact-pin full clone: QA c1:44-53. Whole-range .github diff independently empty. Current QA final gate still belongs to QA; c1 execution is NOT represented as c2 execution. T-01/02/05 |
| 07 | met | test-worktree-state.py StructuralBreaks/ClassC/mixed A-B-C/idempotence snapshots; suite-baseline.md:30-39 actual class-B/cone reds, QA c1:107-108 dirty mutants. Fix render extraction preserves exit/remedy semantics by diff inspection. T-01/04 |
| 08 | met | test-worktree-state-hooks.py four creators, merge/rebase, class-C snapshot; test-worktree-state-hooks-rules.py stdin/delegate/exit/sweep controls; receipt-T-04.md:45-105 records Git 2.54 index-rewrite substitute for class-A merge repro, not an observed merge clearing skip bits. T-04 |
| 09 | met | test-check-state-corpus.py structural downstream-not-run, dirty-alone, dirty+structural and unusable report; gates' broken-layout controls; QA c1:106,111,113 mutants. T-02/03/04 |
| 10 | deferred-by-ruling | BRIEF.md:37 and STATE.md:37-44: conversion receipt belongs to postmerge #2101, not this review. T-06 abandoned. |
| 11 | met | non-regression-receipt.md:6-48 frozen full endpoints and 4635-entry equal manifests; independently checked FULL e8d868f78a6ec43880598af5c5873f5daa8ba985..42856abb91a3a87b9f27ebc933cc363a900afd3d diff: no other-feature or .github change (exit 0). Fix supersedes original claim that C-to-review changes only feature records; preservation remains true, execution transfer does not. T-05 |
| 12 | met | test-corpus-real-owner.py equality/floor, staged-missing/wrong-root controls and disposable dirty/structural pin; non-regression-receipt.md:71-98 six non-skipped cases; QA c1:57 independently ran from converted caller. Historical execution-time owner observation only, NOT fresh measurement of mutable owner at c2. T-05 |
| 13 | partial | Exact unit negative assertions inspected: test-worktree-state-rules.py:38-127; test-feature-corpus-discovery.py:29-129; QA c1:88-106 names discriminating predicate mutants including parser and empty exemption. suite-baseline.md:15-28 and QA c1:71-82,139 establish bootstrap-only original reds for most predicates, not each predicate before production. Fix delta adds no unit historical evidence. T-01/02/03/05 |
| 14 | met | Pinned AGENTS.md and harness/SKILL.md, harness-verification-rules/SKILL.md additions distinguish active writes/absolute landed reads; .harness/README.md:53-130 forbids sibling/symlink/git providers and documents A/B/C, repair/verify/dirty recovery and non-cloned hooksPath. T-05 |

## Closure and assurance bounds
- Full changed-path inventory and complete production/test fix delta inspected. SC-04 refusal now happens before discovering survivors; explicit-path semantics are unchanged. Board/anchor tests exercise behavior rather than census markers. Main-session red/mutant claims are consistent with exact source and assertions; PM did not repeat them. Complexity-bar closure is the code reader's gate, not a product SC inferred from helper count.
- GC-01's blanket parser/exemption concern is dismissed: QA c1:94,98 demonstrated those tests fail. **Retained limitation G-5, kind substance, severity med:** at review SHA, tests/unit/test-worktree-state-rules.py:86 and tests/unit/test-feature-corpus-discovery.py:54 have discriminating current assertions but no predicate-specific pre-production red receipt. BRIEF.md:17 and SC-13 / T-01 (also T-02/03/05) require that historical ordering. Mechanism: a bootstrap ImportError or a post-production mutant can establish existence/discrimination, but cannot establish the demanded earlier predicate execution. This is an evidence limitation, not proof of a parser/exemption defect or non-falsifiable tests. Route to QA/lead evidence consolidation; no new scope or criterion amendment.
- QA G-1 maximal-cone concern stays advisory by ruling; G-4 own-checkout sweep stays inconclusive, not a manufactured defect. Original count receipt retained with erratum: 52/80 files, not 54/86 PASS-line counts.
- C2 QA may supply new exact-pin gates and mutable-host observations. None presumed here; lead must integrate its independent final evidence. No user-run UAT is required.

## Pin and cleanup
Managed pin key FEAT-1559-corpus-outside-worktree / validate-c2 / harness-pm; printed path /Users/molchairuangutai/GitHub/harness/.claude/worktrees/.pins/FEAT-1559-corpus-outside-worktree--validate-c2--harness-pm. git rev-parse HEAD returned the full review SHA above. Source was read-only; no clone fallback. Managed remove exited 0; subsequent read returned Path not found for this exact pin. Sibling pins untouched.

Open questions: none. Remaining consolidation: QA's c2 final gate and literal SC-13 historical assurance disposition; SC-10 remains ruled deferred.
