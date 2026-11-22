# Validate c4 — ESCALATE; acceptance gate not cleared

Pin: 46d0c4bce7cec18e0aabec56a490981496970cc0. Production F3-I is closed under all four ruled rules, but the operator's regression-evidence acceptance is incomplete. Final allowed remediation round is exhausted: return to operator, not another fix.

## Ranked mandatory work
1. substance / med / T-01 / SC-02 — add actual-CLI regression binding same-character closers in both directions. QA's M6 survives 113/113.
2. substance / low / T-01 / SC-02 — add actual-CLI legal tilde-opener/backtick-info control. QA's M8 survives 113/113. Same test-only edit; capture failing evidence before acceptance.

QA independently measured correct current behavior for both, but correct behavior and regression protection are distinct. The ruling explicitly requires each rule test-first through the CLI. Code and pm inspection PASS therefore do not discharge these measured coverage gaps. SC-02's functional outcome is met; its strengthened acceptance evidence is incomplete.

## Reader blocks
- QA: initially PASS despite explicit must_fix; one send-back clarified ESCALATE, mandatory gaps unchanged. Full unit 62 files and integration 89 files green; T-01 40/40 and 113/113; red 108/113 reproduced at d1fd4aa1 without moving HEAD; code-grade PASSING 97; ef269da2 equivalence measured. Evidence: ../../notes/review-harness-qa-c4.md. Initial fail_first evidence remains valid despite correction return omitting it.
- Code PASS: four invariants and single scanner by inspection; no residual. ../../notes/review-harness-code-reviewer-c4.md.
- Security PASS: F3-I closed by static reasoning, no execution assurance. Separate med SEC-C4-01 identifier-prefix advisory. ../../notes/review-harness-security-reviewer-c4.md.
- UI PASS: measured 50 paths, no rendered UI. ../../notes/review-harness-ui-reviewer-c4.md.
- PM PASS: seven SCs, three perspectives and DEC-188 row met by pinned inspection; runtime evidence QA-owned. ../../notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c4.md.

## Separate new classes — operator disposition required
Retain as advisories, not folded into F3-I: QA low Unicode line-break/whitespace mismatch and low list-container fence handling (CLI-reproduced, absent in live corpus); security med DEC-10x identifier confusion (static only). No severity or kind changed. Recommendation: separately adjudicate/backlog; current final-round failure rests on the two within-ruling coverage gaps, not expanding scope.

QA additionally reports its digest validator refuses FAIL for green suite/matrix despite mandatory coverage gaps. This is an unverified harness-contract conflict, not evidence of a test failure. Corrected ESCALATE is preserved; operator must decide acceptance/waiver or authorize further work. cycles_used=1 counts only the QA receipt send-back, not feature rework rounds.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 46d0c4bc closes production F3-I; mandatory regression gaps remain after
    the final allowed fix round.
  open_questions:
  - id: C4-ACCEPTANCE
    question: Authorize further test-only work or waive the two within-ruling T-01/SC-02
      regression gaps? No further fix round is authorized.
    blocking: true
  - id: C4-NEW-CLASSES
    question: Separately adjudicate/backlog QA's Unicode whitespace and list-container
      advisories and security's DEC-10x identifier advisory, outside the four ruled
      rules.
    blocking: false
  - id: C4-QA-CONTRACT
    question: Investigate QA's report that its validator refuses FAIL for mandatory
      coverage gaps when suite/matrix are green; corrected QA verdict is ESCALATE.
    blocking: false
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: ESCALATE
    headline: Green executions; mandatory M6/M8 regression gaps.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Four invariants and single-scanner convention hold.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: F3-I closed by reasoning; medium identifier advisory.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 50 paths; no rendered UI.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Seven SCs, three perspectives and DEC-188 met by pinned inspection.
    files_touched: []
  must_fix:
  - 'substance / med / T-01 / SC-02: actual-CLI regression for same-character closers
    in both directions; M6 survives 113/113.'
  - 'substance / low / T-01 / SC-02: actual-CLI legal tilde-opener/backtick-info regression;
    M8 survives 113/113.'
  branch: none
  escalations: []
  adequacy_notes:
  - QA independently reproduced red 108/113 at d1fd4aa1 and green 113/113 at pin;
    full unit 62 files and integration 89 files pass; code-grade PASSING 97; ef269da2
    equivalence measured.
  - 'Correct behavior is not regression protection: ruling requires actual-CLI test-first
    evidence. PM functional met is retained, but consolidated SC-02 acceptance remains
    partial.'
  - Security closure is reasoning-only; QA supplies execution. UI scope-out measured.
  - One QA receipt send-back corrected contradictory PASS-with-must_fix to ESCALATE;
    original fail_first evidence remains valid. No further implementation round authorized.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c4.md: unit 40/40; base red 13/40 reproduced.'
  - id: SC-02
    verdict: partial
    method: automated
    evidence: 'notes/review-harness-qa-c4.md: green 113/113, red 108/113; M6/M8 survive;
      mandatory coverage incomplete.'
  - id: SC-03
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c4.md: era/provenance green and base red reproduced.'
  - id: SC-04
    verdict: met
    method: inspection
    evidence: 'notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c4.md:
      pinned authoring/scope contracts.'
  - id: SC-05
    verdict: met
    method: inspection
    evidence: 'notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c4.md:
      pinned Mode 2 contracts.'
  - id: SC-06
    verdict: met
    method: inspection
    evidence: 46d0c4bce7cec18e0aabec56a490981496970cc0:.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326;
      PM note.
  - id: SC-07
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c4.md: team tests green in full integration;
      base red reproduced.'
  - id: DEC-188
    verdict: met
    method: inspection
    evidence: 46d0c4bce7cec18e0aabec56a490981496970cc0:.harness/harness/docs/DECISIONS.md:5313-5336;
      successor DEC-254:8253-8326; row decisions_affected[0], owner T-03.
  needs_approval: true
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - Same-character closer regression absent; M6 survives.
  - Legal tilde-info-backtick regression absent; M8 survives.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: qa
    summary: T-01 / SC-02 mandatory closer-character regression gap.
    why: M6 survives 113/113; ruling requires actual-CLI test-first cases.
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: T-01 / SC-02 mandatory legal tilde-info regression gap.
    why: M8 survives 113/113; restriction must apply only to backtick openers.
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'NEW CLASS advisory: Unicode line-break/whitespace mismatch.'
    why: CLI-reproduced spoof selection; absent in live corpus; separate adjudication,
      not F3-I.
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'NEW CLASS advisory: list-container fences create phantom state.'
    why: CLI-reproduced; absent in live corpus; recommend separate backlog.
  - kind: substance
    scope: none
    severity: med
    reader: security-reviewer
    summary: "SEC-C4-01 NEW CLASS \u2014 T-01 / SC-02: DEC-10x can impersonate DEC-10."
    why: Pinned check.py:277-283,329-336 uses (?!\d), accepting alphabetic suffix.
      Static only; reviewer recommends separate adjudication, no c4 must_fix.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-validate-c4-validator/digest.md
```
