# FAIL — fleet reconciliation still crosses repository ownership

Pin **6451153169f469f5bd9d5f3f01bf89b82787b720**. One high T-01 source defect and three bounded acceptance-test gaps block feature acceptance; the matrix is green and operator-accepted SC-08 remains met. No source was edited.

## Ordered must-fix — all T-01, main-session-direct
1. **High / substance / code-reviewer:** LABEL reconciliation unions foreign feature issue numbers, then mutates the owner repository. Kaya #17 can authorize labeling unrelated Harness #17 `abandoned`. Source-traced inference, not executed: `board_lifecycle.py:865-866,932-949,978-993,1137-1142`; `notes/review-harness-code-reviewer-c1.md`. Bind ownership to resolved repository/provenance and fail closed on unreadable mappings. Add collision and same-repository positive cases first.
2. **Med / substance / lead assessment of QA + PM:** SC-01 lacks successful bound-command/config-failure integration outcomes beyond open and the unproven-receipt refusal loop. Complete the signed criterion's integration evidence after the ownership fix; do not introduce broader command scope. `notes/review-harness-qa-c2.md`, SC-01.
3. **Med / substance / lead assessment of QA + PM:** SC-04's positive no-FAIL-floor and unknown-legacy-note outcomes are unit-only, not demonstrated through the integration reader. Preserve existing INV-39/40 and hash cases. Same QA note, SC-04.
4. **Med / substance / lead assessment of QA + PM:** SC-06 lacks the new explicit live-validation/provenance negative regression. Retained live controls pass pre-fix; signature-absent historical-reader reds do not discriminate this missing case. Same QA note, SC-06.

## Adequacy and reconciliation
- QA c1 execution: exact-pin unit 61/61 and integration 87/87 green; first unit run had one 5000ms omp-hooks timeout under concurrent load, then passed alone. T-02 anchors/index passed. These are file counts, not case counts. c1 pre-fix reproductions at c4e8bbc8 distinguish semantic reds from signature absence; no mutation proofs were run.
- QA c1 PASS is explicitly superseded by c2 FAIL: green matrix is not full SC coverage. PM c2 withdraws its stale missing-red/current-pin-matrix objections and clears SC-05. SC-02/03/05/07/08 met; SC-01 not_met; SC-04/06 partial.
- Security PASS traced STATUS and other recovery boundaries, not LABEL ownership. Lead source inspection confirms the separate LABEL consumer, so its narrower clean assessment cannot dispose of code's unchanged high finding. Only QA executed suites; other readers supplied source/receipt reasoning. UI measured 79 attributed paths and correctly scoped out.
- Assessed and dismissed: incidental wording-test deletions and the removed import-shape test have no demonstrated behavioral consequence; existing justification/controls remain. No separate gate. Signature-absent reds remain qualified evidence, not a universal reason to reject SC-02/05.
- All five readers completed. Two genuine reader send-backs (QA contract/adequacy and PM stale evidence) are checkpointed, not production fixes. No new scope, operator decision or approval request. Main owns remediation under DEC-174; do not dispatch an engineering author through the enforcement path.

## Durable reader pointers
QA: `notes/review-harness-qa-c1.md`, `...-c2.md`; code/security/UI: `notes/review-harness-{code,security,ui}-reviewer-c1.md`; goal-check: `notes/research-BUG-20261006-fleet-planning-recovery-goalcheck-validate-c2.md`; accepted UAT: `notes/uat.md`. Checkpoint: `state.yaml`. Product paths are relative to the assigned feature checkout, never another worktree. Open questions: none.

```yaml
VERDICT: FAIL
DIGEST:
  headline: '6451153169f469f5bd9d5f3f01bf89b82787b720: high-severity cross-repository
    reconciliation defect and three acceptance-coverage gaps block completion; matrix
    green, SC-08 accepted.'
  team: validate
  steps_run: 5
  cycles_used: 2
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: Matrix green; SC-01/04/06 integration evidence incomplete.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: LABEL reconciliation can mutate unrelated Harness issues.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No actionable findings within assessed recovery boundaries.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 79 attributed paths; no UI surface.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: SC-01 not met; SC-04/06 partial; other criteria met.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-20261006-fleet-planning-recovery/.harness/harness/features/BUG-20261006-fleet-planning-recovery/notes/research-BUG-20261006-fleet-planning-recovery-goalcheck-validate-c2.md
  must_fix:
  - 'T-01: bind LABEL reconciliation ownership to resolved repository and valid provenance;
    fail closed on unreadable mappings. Add foreign-number collision and same-repository
    positive regressions.'
  - 'T-01 / SC-01: complete integration evidence for successful feature-bound command
    routing and missing/unavailable/mismatched configuration refusal.'
  - 'T-01 / SC-04: demonstrate positive no-FAIL-floor and unknown-legacy-note outcomes
    through integration reader cases.'
  - 'T-01 / SC-06: add a discriminating integration regression proving historical
    refusal provenance cannot satisfy live validation.'
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-20261006-fleet-planning-recovery/.harness/harness/features/BUG-20261006-fleet-planning-recovery/runs/2026-11-21-1-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-20261006-fleet-planning-recovery/.harness/harness/features/BUG-20261006-fleet-planning-recovery/notes/research-BUG-20261006-fleet-planning-recovery-goalcheck-validate-c2.md
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
  - QA executed exact-pin unit 61/61 files and integration 87/87 files successfully.
    First unit execution had one load-sensitive 5000ms omp-hooks timeout; isolated
    rerun passed. T-02 anchor/index checks passed.
  - QA c2 supersedes c1 PASS. PM c2 incorporates completed red-first receipts and
    withdraws its SC-05 receipt objection.
  - Pre-fix receipts distinguish semantic failures from signature-absent failures;
    no mutation proofs were executed.
  - Security's clean STATUS/recovery assessment does not cover LABEL's separate repository-blind
    ownership consumer. Lead source inspection supports code review's unchanged high
    finding; the concrete scenario remains unexecuted.
  - 'Incidental wording/import-shape test deletions were assessed and dismissed as
    separate blockers: no demonstrated behavioral consequence.'
  - SC-08 operator acceptance remains unchanged. No source edits or UAT re-execution
    occurred. All remediation belongs to main-session-direct T-01.
  - Two reader send-backs were recorded; all children completed.
  sc_status:
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: 'notes/review-harness-code-reviewer-c1.md; notes/review-harness-qa-c2.md:
      LABEL ownership defect and incomplete integration routing coverage.'
  - id: SC-02
    verdict: met
    method: automated
    evidence: tests/integration/test-gh-sync-open.py:315-599; notes/review-harness-qa-c1.md
      fail-first table and exact-pin matrix.
  - id: SC-03
    verdict: met
    method: automated
    evidence: tests/unit/test-feature-record.py:1535-1631; notes/review-harness-qa-c1.md
      semantic FAIL-floor red and passing matrix.
  - id: SC-04
    verdict: partial
    method: automated
    evidence: 'notes/review-harness-qa-c2.md: historical refusal/hash integration
      covered; positive no-FAIL-floor and unknown-legacy-note outcomes remain unit-only.'
  - id: SC-05
    verdict: met
    method: automated
    evidence: tests/unit/test-feature-record.py:520-713; notes/review-harness-qa-c1.md
      named pre-fix reds and passing matrix.
  - id: SC-06
    verdict: partial
    method: automated
    evidence: 'notes/review-harness-qa-c2.md: retained live negatives pass pre-fix;
      explicit new live-provenance regression absent.'
  - id: SC-07
    verdict: met
    method: inspection
    evidence: 'notes/review-harness-code-reviewer-c1.md: pinned governing clauses
      agree; QA T-02 anchor/index checks pass.'
  - id: SC-08
    verdict: met
    method: uat
    evidence: 'notes/uat.md: operator accepted 2026-11-21.'
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'SC-01: successful bound routing and configuration-refusal integration outcomes
    incomplete.'
  - 'SC-04: positive no-FAIL-floor and unknown-legacy-note integration outcomes absent.'
  - 'SC-06: explicit live-validation/provenance negative regression absent.'
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-01: LABEL reconciliation omits repository-bound ownership.'
    why: 'board_lifecycle.py:865-866,932-949 unions feature issue numbers without
      repository/provenance checks. A Kaya task #17 makes unrelated Harness #17 CLOSED
      NOT_PLANNED eligible for an abandoned-label mutation at :1137-1142. Source-traced
      inference; not executed.'
  - kind: substance
    scope: none
    severity: med
    reader: validator-lead assessing qa and pm
    summary: 'T-01 / SC-01: required integration routing evidence is incomplete.'
    why: Positive binding is demonstrated for open; other commands have unproven-receipt
      refusal coverage, while configuration failures are unit-only. See notes/review-harness-qa-c2.md.
  - kind: substance
    scope: none
    severity: med
    reader: validator-lead assessing qa and pm
    summary: 'T-01 / SC-04: positive accounting integration evidence is absent.'
    why: No-FAIL-floor and unknown-legacy-note assertions exist only as unit cases,
      not the integration outcomes required by the approved criterion.
  - kind: substance
    scope: none
    severity: med
    reader: validator-lead assessing qa and pm
    summary: 'T-01 / SC-06: new live-provenance regression is absent.'
    why: Retained live controls pass before the fix; the historical-reader signature-absent
      red does not discriminate the missing live-validation/provenance case.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-20261006-fleet-planning-recovery/.harness/harness/features/BUG-20261006-fleet-planning-recovery/runs/2026-11-21-1-validator/digest.md
```
