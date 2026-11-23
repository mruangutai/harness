# BUG-2399 validate — FAIL

Pin `3835fde4f16d1b34d8711fc8607b5153545bfaec`, base `59289ad1`. All SCs and both perspectives are met, but this is not ship-ready: QA integration is red and code grading has three high failures. Five readers completed; no cycles spent.

## Ranked action set
1. T-02: simplify merger `_without_obsolete` and `_merge` to production grade 4; T-01: simplify operator-command composition test to test grade 3. Preserve migration/command coverage. Code reviewer measured these at the exact range; no runtime bug is alleged.
2. T-03: shorten DEC-257's index ruling (39 words; cap 30). Generator equality alone did not test this invariant; QA's integration gate did.
3. Restore/provision the pinned TypeScript compiler before a future gate run; the second integration failure is environmental, not attributable to this diff. Do not waive it or rewrite the red receipt.

These changes remain main-session-direct under DEC-174; this report does not authorize an engineering fix run.

## Adequacy and dispositions
QA ran 65 unit and 95 integration files once with production receipts; unit green, integration two red files. SC-01..03 have preserved semantic red-before-production evidence and passed inside the pinned integration run. PM's SC-04 inspection confirms DEC-238 unchanged and no historical backfill. Security found no exploitable regression. UI measured 22 changed paths, zero UI surfaces; no visual assurance is claimed.

Three code-review medium grade-2 observations are retained as nonblocking: the reviewer explicitly accepted lifecycle continuity, before/after candidate continuity, and three migration combinations as reasons. Its empty structured grade_2_reasons does not erase those prose reasons.

PYTHONUSERBASE is an acceptable environment adjustment, not evidence of a wholly verbatim verify invocation; QA independently reproduced the import issue. PM GC-F1 (form, unrated): interrupted fixture uses noncanonical in_progress rather than running; removal gates Git dirt, so the demonstrated refusal stands, but real interruption production is untested. PM GC-F2 (form, unrated): five comment/documentation paths lack signed ownership. They serve SC-04 without changing behavior, but a deviation ledger is not authorization. Main/advisor must explicitly dispose these record issues; no severity is invented here. Panel re-transcription is an acceptable record repair. The pre-existing flake's claimed root cause is not established; QA did not rerun it and it did not recur.

## Pointers and open questions
Reader evidence: feature `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c0.md` and `notes/research-BUG-2399-run-records-tracked-goalcheck-validate-c0.md`. Receipts: this run's `qa/manifest-{unit,integration}.json`.

Open: how should pinned checkouts provision TypeScript dependencies? Resolve the five unowned paths and interrupted-fixture record without silently granting scope. Main routes decisions to fable-advisor as delegated. No reader's clean result cancels QA/code failures.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 3835fde4 meets SC-01..04, but red integration and three high code-grade
    failures block readiness; remediation stays main-session-direct.
  open_questions:
  - id: QA-Q1
    question: How should pinned checkouts provision node_modules/.bin/tsc? Its absence
      caused an environmental integration failure, not a green gate.
    blocking: false
  - id: GC-record-disposition
    question: 'Route to delegated fable-advisor: explicitly dispose PM GC-F1 noncanonical
      interrupted-fixture record and GC-F2 five comment/documentation paths outside
      signed task ownership; a deviation ledger does not grant ownership.'
    blocking: true
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: 65 unit files green; 95 integration files completed with index-cap and
      missing-compiler failures; fail-first evidence sound.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Compliance passes; three high exact-range code-grade failures.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No exploitable security regression identified.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 22 changed paths, zero UI/design surfaces; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All SCs and both perspectives met; two form/record deviations noted.
    files_touched: []
  must_fix:
  - 'T-02, main-session-direct: simplify _without_obsolete and _merge to production
    grade 4 without weakening behavior.'
  - 'T-01, main-session-direct: simplify operator checklist composition test to test
    grade 3 without reducing coverage.'
  - 'T-03: shorten DEC-257''s index ruling from 39 words to the 30-word cap; test-gen-decisions-index.py
    fails.'
  - Provision the missing pinned TypeScript compiler before claiming passing integration;
    preserve current red receipts.
  branch: none
  escalations: []
  adequacy_notes:
  - 'QA ran each kind once with production receipts: 65 unit and 95 integration files
    completed; integration has two failed files. No lead rerun occurred.'
  - SC delivery does not cancel QA/code gates. DEC-238, retention and invariant semantics
    remain unchanged according to pinned PM inspection.
  - 'Three medium grade-2 test observations are nonblocking: reviewer accepted lifecycle
    continuity, before/after candidate continuity and three migration combinations
    as reasons. Ratings retained.'
  - PYTHONUSERBASE is an acceptable environment adjustment; QA reproduced the import
    problem, but receipts do not prove a wholly verbatim enclosing invocation.
  - 'PM GC-F1 overlaps QA''s residual concern: Git-dirt refusal and byte preservation
    are proven, actual interrupted-run production is not. GC-F2 concerns ownership,
    not behavioral expansion. Neither is silently dismissed.'
  - UI scope-out rests on measured census. Security supplied read-only analysis, not
    execution evidence.
  - Pre-existing flake root cause remains unproven; QA did not rerun it and it did
    not recur. Panel re-transcription is accepted as record repair.
  - DEC-174 requires main-session-direct remediation, not an engineering fix run.
    PM's missing form severities remain unrated and their disposition is escalated.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: Pinned tracking cases passed in integration; original semantic qa-red.json
      failures and matching qa-green.json red hash preserved.
  - id: SC-02
    verdict: met
    method: automated
    evidence: Pinned migration/check/idempotence/operator-command composition cases
      passed in integration with preserved red-before-production evidence.
  - id: SC-03
    verdict: met
    method: automated
    evidence: Pinned distill refusal/commit and interrupted untracked-record removal
      preservation regressions passed with preserved red evidence. Real interruption
      producer not covered.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: PM git show 3835fde4:path inspection confirms DEC-257, consistent tracking
      instructions, zero-inventory receipt, unchanged DEC-238 and no historical backfill.
      Index cap fails separately.
  needs_approval: true
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - Interrupted fixture proves dirt preservation, not actual aborted-run production.
  - Missing compiler prevents clean pinned integration.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-02: _without_obsolete fails production complexity bar.'
    why: CC 10, cognitive 14, ABC 16.4; grade 3 against bar 4.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-02: _merge fails production complexity bar.'
    why: CC 9, cognitive 11, ABC 21.7; grade 3 against bar 4.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-01: operator checklist composition test is grade 1.'
    why: CC 6, cognitive 2, ABC 50.3 against test bar 3.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: interrupted-run removal test requires grade-2 reason.'
    why: Reviewer accepts lifecycle setup, refusal and byte-preservation continuity;
      nonblocking.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: distill ordering test requires grade-2 reason.'
    why: Reviewer accepts same candidate before/after committing and pushing records;
      nonblocking.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: historical-rule migration test requires grade-2 reason.'
    why: Reviewer accepts covering three shipped-rule combinations under one contract;
      nonblocking.
  - kind: form
    scope: none
    severity: unrated
    reader: goalcheck
    summary: 'GC-F1: interrupted fixture uses noncanonical in_progress status.'
    why: 'PM says nonblocking record issue: dirt preservation proven, actual interruption
      behavior not. Missing severity retained unrated; explicit disposition escalated.'
  - kind: form
    scope: none
    severity: unrated
    reader: goalcheck
    summary: 'GC-F2: five comment/documentation paths lack signed ownership.'
    why: Changes serve SC-04 but deviation ledger grants no ownership. Missing severity
      retained unrated; disposition escalated.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-tracked/.harness/harness/features/BUG-2399-run-records-tracked/runs/r-20261122-3-validate-validator/digest.md
```
