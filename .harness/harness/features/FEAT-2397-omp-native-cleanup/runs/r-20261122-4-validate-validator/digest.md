# FEAT-2397 validation — 53a89eb70251d1529dbffd8e50959c4590a032f7

**Not ship-ready.** Unit has two new standing regressions; SC-08/09/12 fail or remain partial despite integration 95/95, typecheck and the recorded real-host observation passing. Scope/authority questions go to Main, never a blind fix loop. Actual base: 522c94b2b79e5e2021cb670910772428c17914b0.

## Ranked remediation
1. **Resolve authority/scope first:** Main must reconcile T-05's blocking Main→orchestrator instruction with preserved DEC-204's asynchronous edge, authorize migration of the two newly red standing tests outside task files, and reconcile eight live INV-26 board/plan mismatches. Do not restore removed behavior merely to satisfy stale tests.
2. **T-05 / SC-08/09 / DEC-214:** update stale DECISIONS-INDEX tails and durable successors, SPEC:808–811's removed model-refusal claim, DECISIONS:7117–7119's removed tool_input.prompt spelling, and the false completion claim in t05-doctrine.md. Twenty-three tails meet length limits; content, not length, fails.
3. **T-03 / SC-12:** decompose test-check-domain.py::_feat2274_cases and test-layout-migration.py::_parity, both changed executable bodies at grade 2. Canonical grading's 80 passing functions does not cover all 155 changed bodies; all eight changed production functions meet >=4.
4. **T-02/T-06/Main / SC-04/12:** commit exact actual-ref transient command/results and actual-ref full changed-body grading evidence, then fresh runner/corpus receipts at the repaired review pin. The current pin cannot contain evidence generated after it. Earlier positive 31-record corpus success remains true; current positive 34-record execution exits 1.

## Assessment and evidence
- QA: notes/review-harness-qa-c0.md; qa/manifest-unit.json binds 67 selected scripts to the pin, exit 1 (test-lead-stop-and-wake.py and test-no-distribution.py); manifest-integration.json binds 95, exit 0. Both unit reds pass at immutable base. Clean-env bun247/0 confirms the disclosed inherited-env failure is not this regression.
- Code: notes/review-harness-code-reviewer-c0.md. Explicit SC-12 changed-body bar governs over narrower canonical gate. Spec compliance failed, so full stage-two quality clearance is not claimed.
- PM: notes/research-FEAT-2397-omp-native-cleanup-goalcheck-validate-c0.md. Operator/maintainer partial; orchestrator pass. DEC-214 partial routes to T-05; other 22 amend/strike owning clauses landed.
- Security: notes/review-harness-security-reviewer-c0.md: actual 136-path boundary audit, no exploitable regression found. UI: notes/review-harness-ui-reviewer-c0.md: actual 136-path census, org.html prose only, correctly scoped out; no rendered/pixel assurance.
- SC-03's alleged missing isolated red is **dismissed with correction**, not waived: red-H:409/412/426 fail changed refusal/correction/held-child behavior; 411/428 are baseline claim-retention preservation. QA corrected its note/digest without rerunning or changing receipts. SC-07/11 signature-absent rows are supported separately by semantic handler/mutation proofs.
- SC-10 records authorized Main observation only: actual omp19.1.0, 7/7 exit 0, numeric path-identified child and distinct main, issue2194 CLOSED. Executed probe/companion blobs match the pin; reviewers did not author human acceptance or rerun the live host.

Open questions: Main-edge authority; standing-test scope authorization; actual corpus state/board disposition. Ordinary T-03/T-05/evidence repairs are must-fix work, not new product questions. No source edits, suite reruns by the lead, merges or fabricated green outcomes.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: '53a89eb70251d1529dbffd8e50959c4590a032f7 is not ship-ready: two new unit
    regressions, incomplete doctrine and changed-test grading; scope/authority rulings
    required.'
  open_questions:
  - id: scope:standing-regressions
    question: Authorize migration of tests/unit/test-lead-stop-and-wake.py and tests/unit/test-no-distribution.py,
      outside approved task files, for new T-02/T-05-induced failures. Both pass at
      immutable base; do not restore intentionally removed behavior merely to satisfy
      stale expectations.
    blocking: true
  - id: scope:Main-edge-contract
    question: Resolve T-05's signed blocking Main-to-orchestrator command instruction
      versus preserved DEC-204's asynchronous edge before changing either authority.
    blocking: true
  - id: Q-INV26
    question: Reconcile eight live board-versus-plan INV-26 failures at the review
      pin, or explicitly rule the gate's timing. Earlier 31-record success does not
      clear the current 34-record failing execution.
    blocking: true
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: Unit has two new failures; integration95/95 and typecheck pass; current
      corpus gate fails.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Two changed tests grade2; affected index tails retain removed host mechanics.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: 136-path audit finds no exploitable boundary regression.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: '136-path census scopes out visual review: org.html prose only.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator/maintainer partial; orchestrator evidenced; DEC214 partial.
    files_touched: []
  must_fix:
  - 'Main: resolve Main-edge authority and standing-test scope before remediation;
    then migrate both newly red unit expectations without reinstating removed behavior.'
  - 'T-05: rewrite affected DECISIONS-INDEX tails with correct contracts, DEC111 strike
    and durable successors; correct SPEC808-811 model-refusal claim and DEC2147117-7119
    deleted tool_input.prompt spelling; correct t05-doctrine.md''s false completion
    claim.'
  - 'T-03: decompose test-check-domain.py::_feat2274_cases and test-layout-migration.py::_parity
    so both changed tests meet SC12 grade>=3.'
  - 'T-02/T-06/Main: commit exact actual-ref transient command/results and actual-base/review
    full changed-body grading evidence; new reports are not evidence already committed
    at this pin.'
  - 'Main: reconcile eight actual repository-state INV26 rows and retain a fresh positive-discovery
    corpus receipt.'
  - 'After authorized fixes: obtain final-pin QA runner receipts and review evidence;
    commit required ignored run evidence with the closed run record.'
  branch: none
  escalations:
  - id: scope:standing-regressions
    raised_by: harness-qa; harness-pm
    question: Two new standing-test failures require edits outside approved task file
      lists.
    domain: plan scope
    routed_to: Main
    resolution: unresolved; authorization requested, no edits made
    decided_by: none
    recorded_as: notes/review-harness-qa-c0.md; notes/research-FEAT-2397-omp-native-cleanup-goalcheck-validate-c0.md
  - id: scope:Main-edge-contract
    raised_by: harness-pm
    question: Signed T05 blocking instruction conflicts with retained DEC204 async
      Main edge.
    domain: approved contract
    routed_to: Main
    resolution: unresolved; neither authority silently overridden
    decided_by: none
    recorded_as: notes/research-FEAT-2397-omp-native-cleanup-goalcheck-validate-c0.md
  - id: Q-INV26
    raised_by: harness-qa; harness-pm
    question: Actual corpus gate fails on eight live board/plan mismatches.
    domain: orchestration state
    routed_to: Main
    resolution: unresolved; prior success preserved as historical execution
    decided_by: none
    recorded_as: notes/review-harness-qa-c0.md
  adequacy_notes:
  - Actual review range 522c94b2b79e5e2021cb670910772428c17914b0..53a89eb70251d1529dbffd8e50959c4590a032f7;
    build/red baseline bdb1c2f68c63bdc7a2b8ba2203db72da80a2abe0 is distinct.
  - Production receipts bind unit67 selected/exit1 and integration95 selected/exit0
    to the pin. Typecheck passes. No lead suite rerun.
  - Canonical grading80 and changed-body grading155 use different selectors. Two changed
    tests grade2; all eight changed production functions meet>=4.
  - 'SC03 missing-isolated-red concern assessed and dismissed: red-H409/412/426 fail
    changed behavior;411/428 preserve baseline retention. QA corrected note/digest
    in one send-back without reruns or receipt edits.'
  - SC07/11 signature-absent rows are supported separately by semantic handler and
    behavioral mutation proofs.
  - 'SC10 records authorized Main UAT only: actual omp19.1.0/7of7/exit0, path-identified
    numeric child and distinct main, issue2194 CLOSED; executed probe blobs match
    pin. Reviewers did not author acceptance.'
  - Security audited actual136-path boundaries. UI scoped out after actual136-path
    census; no rendered assurance. Stage-two code clearance unavailable while spec
    compliance fails.
  - All23 index tails meet length limits; content/successor omissions fail. Other22
    amend/strike owning clauses landed; DEC214 partial.
  - PM ordinary repair requests consolidated into must_fix, not new product questions.
    Disclosed environment failures are distinct from two new unit regressions.
  - Candidate-pin tests do not prove installed pre-change hooks. T01's tight runtime
    timeout margin remains advisory.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: QA integration and committed t01 red-A/B/C byte-parity/checker witnesses.
  - id: SC-02
    verdict: met
    method: automated
    evidence: QA bun247/0, red-D and decode/context/retry witnesses.
  - id: SC-03
    verdict: met
    method: automated
    evidence: Integration95/95; red-H409/412/426, dispatch and identity witnesses.
  - id: SC-04
    verdict: partial
    method: inspection
    evidence: T02 pinned green describes working tree; fresh actual-ref proof not
      committed at pin. T02/Main owns repair.
  - id: SC-05
    verdict: met
    method: automated
    evidence: Standing root-negative assertions preserved and green.
  - id: SC-06
    verdict: met
    method: automated
    evidence: Accessor-based off/absent/on/eval regression, red-G and green integration.
  - id: SC-07
    verdict: met
    method: automated
    evidence: Bun247/0; semantic red-L handlers plus native usage/threshold/postDomain
      witnesses.
  - id: SC-08
    verdict: not_met
    method: inspection
    evidence: Stale index/SPEC model claim/DEC214 request spelling; Main-edge authority
      conflict. T05/Main.
  - id: SC-09
    verdict: partial
    method: inspection
    evidence: Preservation half confirmed; current doctrine negative clause fails
      on SC08 residuals. T05.
  - id: SC-10
    verdict: met
    method: uat
    evidence: Recorded authorized Main19.1.0 observation7/7 exit0; child/main numeric
      values; matching probe blobs; issue2194 CLOSED. Not reviewer-authored acceptance.
  - id: SC-11
    verdict: met
    method: automated
    evidence: Offline tests green; ten behavioral mutant reds supplement absent-helper
      baseline.
  - id: SC-12
    verdict: not_met
    method: inspection
    evidence: Two T03 changed tests grade2; actual-ref report absent at pin; positive34-record
      corpus exits1 despite earlier31-record success.
  - id: DEC-11
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS153-170.
  - id: DEC-59
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS647-658.
  - id: DEC-63
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS705-720.
  - id: DEC-64
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS724-729.
  - id: DEC-81
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS972-984.
  - id: DEC-101
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS1477-1497,1511-1513.
  - id: DEC-110
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS1761-1789.
  - id: DEC-111
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS1803-1813 strike and6342-6345 citation.
  - id: DEC-112
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS1819-1822,1842-1855.
  - id: DEC-127
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS2724-2743.
  - id: DEC-144
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS3334-3342.
  - id: DEC-151
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS3543-3555.
  - id: DEC-155
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS3657-3673.
  - id: DEC-156
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS3692-3717.
  - id: DEC-173
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS4454-4460,4471-4475.
  - id: DEC-198
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS5910-5919,5936-5958.
  - id: DEC-199
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS6012-6041.
  - id: DEC-201
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS6190-6226.
  - id: DEC-208
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS6868-6874.
  - id: DEC-214
    verdict: partial
    method: inspection
    evidence: Native injection/checker landed, deleted tool_input.prompt remains7117-7119;
      DECISIONS-owning T05 must finish.
  - id: DEC-218
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS7239-7275.
  - id: DEC-222
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS7421-7447.
  - id: DEC-233
    verdict: met
    method: inspection
    evidence: PM pinned DECISIONS7910-7919,7925-7943.
  needs_approval: true
  severity_max: med
  matrix_ok: false
  coverage_gaps:
  - SC04 actual-ref transient and SC12 actual-ref grading evidence not committed at
    pin.
  - Two changed tests violate SC12 despite narrower canonical selection passing.
  - Unit compatibility fails on two new scripts; actual corpus fails on eight live
    INV26 rows.
  - Stage-two quality clearance unavailable while spec compliance fails.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-03: two executable-body-changed test functions violate SC-12''s >=3
      bar.'
    why: test-check-domain.py::_feat2274_cases grades2(CC8/cognitive6/ABC33.5); test-layout-migration.py::_parity
      grades2(CC12/cognitive10/ABC30.8). Canonical gate passes unchanged grades, but
      signed acceptance covers every changed test function.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer; harness-pm
    summary: 'T-05: stale current doctrine contradicts adopted native contracts and
      leaves DEC-214 partial.'
    why: Affected index tails retain retired host/delivery/model/TTL contracts; DEC111
      strike and durable successors missing. PM identifies SPEC808-811 removed model
      checks and DEC2147117-7119 deleted prompt spelling. Generator preserves stale
      tails; t05-doctrine completion claim contradicted by pinned bytes.
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2397-omp-native-cleanup/.harness/harness/features/FEAT-2397-omp-native-cleanup/runs/r-20261122-4-validate-validator/digest.md
```
