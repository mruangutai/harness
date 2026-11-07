# FEAT-71 validation — validate-validator

**BLOCKED: the product criteria pass, but a mandatory high-severity complexity failure needs correction and the touched locally-run probe lacks its required receipt.** Pin: `3e6add2af05f5b801afec1ef69440fe54e1529a4`; base: `4a05030d401593003209f525fd06e00802eccd36`. No source edits, new pin or merge by this lead.

## Ranked action set
1. **CR-01 · high · substance · T-01 · must fix:** `tests/integration/test-check-state-records.py:798`, `case_t06_build_entry_invariant`, is grade 1 (CC 9, cognitive 6, ABC 46.7; test bar 3). Code review's exact-range grader exits 1. Simplify without weakening the receipt cases; main owns this DEC-174 path. Evidence: `../../notes/review-harness-code-reviewer-c0.md`, Stage 2.
2. **Q-1 · blocking policy/evidence conflict, not a shipped-code finding:** `omp_session_accessor` is locally_run and its detect file changed. No feature-local live-run receipt exists. Verification-rules requires BLOCKED; approved SC-04 promises only byte-preserving relocation/static inspection. QA c0's inferred waiver was unsupported and explicitly withdrawn in c1. Main must resolve the governing-rule conflict or obtain the required recorded run; this lead grants no exemption. Evidence: `../../notes/review-harness-qa-c1.md`, Q-1. Do not treat this as a newly requested product feature.

## Assessment and dispositions
- **QA BLOCKED:** independently ran 57 unit and 84 integration files in an exact-pin real-.git standalone clone with the exact five folders; both exit 0. Named baseline-implementation reds support automated SC-02/03. One send-back corrected disposition only; no tests rerun. These executions establish the required unit/integration floor, not completion of the separate locally-run obligation.
- **Code FAIL:** CR-01 is the sole code must-fix. CR-02 (`case_t14_exempt_shape`) and CR-03 (`_t07_sweep`) remain med/substance grade-2 advisories with cohesive-fixture reasons; no severity or kind changed. Passing functional suites do not contradict a failed complexity gate.
- **Security PASS, in scope:** enforcement/ownership boundaries audited; no exploitable regression found. **UI PASS, out of scope:** measured 4,975-path census, no rendered UI. Neither lens executed runtime falsification tests; do not count them as extra suite assurance.
- **PM PASS:** operator and code maintainer each pass; SC-01–05 met. Optional row-plan ownership, CLI retirement and decision truth updates were assessed by code/security/PM as the authorized decoupling, not lost enforcement. This is product-goal clearance, not ship clearance.
- **QA finding 1 (low/form) retained as evidence qualification:** SC-02's unit label includes handoff coverage physically under integration; both required kinds ran, and the baseline reds are real. No blocking source remedy.
- **QA finding 2 (low/substance) assessed and dismissed:** QA withdrew the claim that baseline-green assertions cannot discriminate future defects. No mutation proof for those particular INV-37/domain/template assertions was supplied; absence of a pre-change defect is not a demonstrated test defect.
- **QA finding 3 (low/substance) assessed and dismissed as blocking/actionable code defect:** the empty-walk test proves mismatch detection; its adjacent exact-set test supplies non-vacuity. A naming overclaim does not defeat the sound pair. No mutation proof was performed.
- **QA finding 4 withdrawn by its author:** integrity-only live reads comport with the BRIEF's five-folder execution requirement; the invalid text-vs-intent classification is not promoted. **Finding 5 dismissed by its author:** kaya/CLI observations describe assurance scope, not a proportionality defect. No invented reclassification.

## Evidence bounds and open questions
Only Q-1 requires a ruling. QA's optional Q-2 log-retention request is a non-gating durability qualification, not a product question: complete QA stdout/stderr remain at `/private/tmp/feat71-qa-{unit,integration}.log`; write-guard refused copying them. Hashes, byte counts and measured results survive in c1, while the builder's complete standalone verify log survives under notes. The lead did not rerun checks or claim a fresh credentialled accessor run. All five reader steps are terminal; state records one QA send-back. Re-review any source remediation at a new main-pinned SHA, not this stale pin.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: 3e6add2a meets product criteria, but one high complexity finding and a
    missing locally-run receipt prevent clearance.
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: BLOCKED
    headline: 57 unit and 84 integration files pass; touched locally-run probe lacks
      its required receipt.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Exact pinned Python range contains one blocking grade-1 function.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No exploitable regression found in affected enforcement boundaries.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Committed changed-path census establishes no UI surface.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Operator and code maintainer perspectives pass; all five criteria are
      met.
    files_touched: []
  must_fix:
  - 'T-01 CR-01: simplify tests/integration/test-check-state-records.py:798 case_t06_build_entry_invariant
    to meet its complexity bar without weakening receipt assertions.'
  files_touched: []
  branch: none
  open_questions:
  - id: Q-1
    question: Resolve the conflict between approved inspection-only accessor relocation
      and verification-rules requiring a recorded run for the touched locally_run
      omp_session_accessor kind. No receipt or authorized exemption exists; this lead
      cannot grant a waiver.
    blocking: true
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Reviewed 4a05030d401593003209f525fd06e00802eccd36..3e6add2af05f5b801afec1ef69440fe54e1529a4;
    all readers are terminal.
  - QA independently ran both required kinds in an exact-pin standalone clone containing
    exactly five feature folders; named baseline failures support SC-02 and SC-03.
  - One QA send-back corrected an unsupported waiver and withdrawn test-discrimination
    overclaims; no suites were rerun.
  - QA's remaining low-severity qualifications and all withdrawn or dismissed observations
    are explicitly assessed in the artifact.
  - Complete QA output remains in temporary logs; hashes and results are durable in
    QA c1. The builder's complete standalone verification log remains under notes.
  - Product-goal PASS does not override the failed complexity gate or unresolved locally-run
    obligation.
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: Pinned committed tree contains exactly the five authorized feature folders.
  - id: SC-02
    verdict: met
    method: automated
    evidence: QA c0 records named baseline failures and exact-pin green unit/integration
      coverage.
  - id: SC-03
    verdict: met
    method: automated
    evidence: QA c0 and red-first-S2.md establish synthetic non-vacuity, conversion
      execution and canonical-reader baseline failures.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: Pinned probe/config/layout diff and byte-identical accessor relocation;
      no fresh live-run claim.
  - id: SC-05
    verdict: met
    method: inspection
    evidence: Pinned scoped deletions, record-deletion receipt and bounded documentation
      changes; no kaya edits.
  needs_approval: false
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - Touched locally_run omp_session_accessor kind has no recorded feature-local run.
  - QA supplied no mutation proof for the specific INV-37, domain and template assertions
    discussed in c1; baseline-green alone does not establish a defect.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-01 CR-01: case_t06_build_entry_invariant fails mandatory complexity
      gate.'
    why: 'tests/integration/test-check-state-records.py:798: CC 9, cognitive 6, ABC
      46.7, grade 1 against test bar 3. Exact-range grader exits 1; this blocks acceptance
      despite green functional suites.'
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01 CR-02: case_t14_exempt_shape is grade 2; advisory.'
    why: tests/integration/test-check-state-handoff.py:489 combines three outcomes.
      Reviewer records cohesive shared-state fixture justification; not a must-fix.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01 CR-03: _t07_sweep is grade 2; advisory.'
    why: tests/integration/test-post-merge-sweep.py:974 combines repository lifecycle
      operations. Reviewer records identical-fixture justification; not a must-fix.
  - kind: form
    scope: none
    severity: low
    reader: qa
    summary: 'T-01: SC-02''s unit evidence label includes integration-located handoff
      assertions.'
    why: Both required kinds executed successfully and baseline reds are real. Retained
      as an evidence-label qualification, not a blocking source defect.
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence/.harness/harness/features/FEAT-71-corpus-independence/runs/validate-validator/digest.md
```
