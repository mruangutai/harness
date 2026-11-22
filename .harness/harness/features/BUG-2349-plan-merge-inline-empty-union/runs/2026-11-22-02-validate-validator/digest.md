# BUG-2349 validation

ESCALATE — review pin `2a476ca04c3516bdac3e69dfe66cec7eb372e243` meets the assigned premerge outcomes, but the required unit-kind coverage is missing. One high substantive must-fix; its remedy exceeds T-01's approved two-file scope. Main must resolve scope before remediation, not dispatch an impossible ordinary fix cycle.

## Consolidated must-fix
1. T-01: add a unit-kind regression binding `_union_key_head` head selection and demonstrate red/green evidence. QA reports unit runner rc=0 across 63 files but none binds this change; integration rc=0 across 91 files does not satisfy the separate unit floor. `.harness/harness.json` requires unit when bugfix touches runtime code; verification-rules explicitly rejects unrelated existing tests. Recommended resolution: authorize a `tests/unit/` file in scope, implemented main-session-direct under DEC-174. No waiver inferred.

## Assessment
Code, security, UI and goalcheck pass; UI measured the 12-path census before declining. Code's compliance PASS and PM's premerge outcome PASS do not contradict QA: they grade behavior, not the independent matrix floor. SC-01 has natural red and green receipts; SC-02 preserves preexisting refusal; SC-03 exact bounded predicate/diff passes. SC-04 passes only its premerge portion; postmerge scratch receipt from the surviving merged owner checkout remains a main-session ship obligation.

QA artifact: `notes/review-harness-qa-c0.md`; other four reader notes use the corresponding review persona and research goalcheck names. QA corrected finding shape in a direct follow-up without changing its artifact: missing unit = substance/high/blocking; receipt SHA = form/low/advisory; uncovered neighbors = proportionality/low/advisory, task T-01. These classifications are preserved, not reassigned by the lead.

Receipt-SHA advisory retained: premerge receipt identifies checkout HEAD with an uncommitted fix; independent integration execution at the pin strengthens behavior evidence, while merged-SHA receipt remains outstanding. Neighbor coverage advisory assessed-and-dismissed: no SC requires blank/null heads or zero-item proposal variants; do not expand this bounded patch for them. No reviewer performed mutation proofs; QA executed matrix suites, while other lenses were inspection-only. Missing product guidance remains a documented limitation, not invented requirements.

## Open question
Q-unit-floor: authorize the recommended unit-test scope addition, or explicitly rule on QA's proposed integration-as-unit exception? No exception has been granted. This is the only operator decision; there is one consolidated defect, not two gates.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: Pin 2a476ca04c3516bdac3e69dfe66cec7eb372e243 meets premerge outcomes;
    unit coverage needs scope authorization.
  open_questions:
  - id: Q-unit-floor
    question: Authorize a tests/unit/ regression file for T-01 (recommended), or explicitly
      decide QA's integration-as-unit exception? Approved files cannot satisfy unit-kind
      floor.
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
    headline: Unit coverage missing despite green suites.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Exact contract and bounded diff pass.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No security findings.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured census has no UI surface.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Premerge outcomes pass.
    files_touched: []
  must_fix:
  - 'T-01: authorize scope and add unit-kind _union_key_head regression with red/green
    evidence.'
  branch: none
  escalations: []
  adequacy_notes:
  - 'ESCALATE: remediation needs a file outside signed T-01 scope; implementation
    remains main-session-direct under DEC-174.'
  - 'QA: unit rc=0, 63 files; integration rc=0, 91 files. No unit test binds this
    change.'
  - SC-04 premerge only passes; postmerge scratch receipt using surviving merged owner
    checkout remains main's ship obligation.
  - SC-01 natural red present; SC-02 preserves existing refusal. No mutation proofs
    performed.
  - QA corrected finding classifications in follow-up; consolidated artifact records
    correction.
  - Neighbor coverage advisory dismissed as outside required SCs; product guidance
    absence documented.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: Separate decisions/tasks cases and red/green receipts.
  - id: SC-02
    verdict: met
    method: automated
    evidence: Nonempty flow-base refusal regression.
  - id: SC-03
    verdict: met
    method: inspection
    evidence: Code reviewer verified exact predicate and bounded diff at pin.
  - id: SC-04
    verdict: met
    method: automated
    evidence: 'Premerge only: notes/receipts/sc01-sc02-sc04-green-prefix.txt:688-691;
      postmerge outstanding.'
  needs_approval: true
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - Required unit coverage missing.
  - Postmerge SC-04 receipt outstanding as ship obligation.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-qa
    summary: T-01 lacks required unit-kind head-selection regression.
    why: Runtime bugfix triggers unit floor; unrelated green unit tests cannot satisfy
      it.
  - kind: form
    scope: none
    severity: low
    reader: harness-qa
    summary: Premerge receipt HEAD predates uncommitted fix.
    why: 'Advisory: integration passed independently at pin; postmerge receipt must
      identify merged SHA.'
  - kind: proportionality
    scope: task
    severity: low
    reader: harness-qa
    summary: Untested neighboring head variants.
    why: 'Assessed-and-dismissed: no SC requires these cases; extra scope unjustified.'
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2349-plan-merge-inline-empty-union/.harness/harness/features/BUG-2349-plan-merge-inline-empty-union/runs/2026-11-22-02-validate-validator/digest.md
```
