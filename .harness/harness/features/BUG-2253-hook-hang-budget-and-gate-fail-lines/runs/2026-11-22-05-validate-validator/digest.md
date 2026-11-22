# BUG-2253 round-3 regate — ESCALATE (contract disposition only)

**SC-01 and SC-02 met; prior high blocker closed; no source must-fix.** Reviewed `3dd8bb677bb2936361e3952030fc24f15bf9afc6..3aa17de30917ca7eee9d5edb6ebc944e6dc45236`, excluding later record-only `d21cf97f`. QA executed the literal T-01 verify at a managed pin: **17 cases, exit 0, 11.42s**, empty stderr. Code, security, UI and goalcheck return PASS. QA returns FAIL solely because the operator-excluded unit-kind gap (#2281) makes matrix_ok false and its contract forbids PASS plus false. No further developer rework is requested or authorized.

## Assessment

The round-3 monotone header-name set removes the destructive close-pairing operation. Same-name PASS and header echoes cannot erase a genuine FAIL. The final echoed-header regression exercises both matching PASS names through the real refusal path. Supplied discriminate-c4 fails only this case on cycle-2 gate b228c3a2; exact-base red-c4 has 14 failures, and green-c4 passes the selected group and full file on 3c6fb908. QA and PM independently measured no code differences from that executed fix to the review pin. Six budget cases, six real-block cases and two readiness-independent watchdog controls remain green. This is discriminating closure, not source inspection alone.

Only QA executed behavioral verification; other lenses inspected immutable source and supplied receipts. Main's grading (29 PASSING, no FAIL) is supplied, not panel-executed. Full-file evidence is not whole integration-kind or unit coverage. UI measured 73 paths: two Python paths plus 71 records, zero visual paths.

## One process question, no patch blocker

Q-UNIT-MATRIX: how should the already-approved #2281 scope exclusion be represented in the strict QA/worst-wins rollup? Source inspection confirms `GATE_FAIL_VALUES[qa].matrix_ok = False` and the matrix floor requires every always kind satisfied. Changing QA to PASS or matrix true would falsify its record; silently overriding its FAIL would violate the lead rollup. Re-prompting QA cannot repair this constraint. ESCALATE preserves the operator's nonblocking substance ruling while requesting only a contract disposition, not unit work or another fix round. Parent was asked; no answer was available at closure.

## Deduplicated advisories, none must-fix

1. **substance/med — #2281:** missing unit coverage, explicitly outside patch (QA/code/PM).
2. **substance/low — accepted:** captured FAIL after a matching real or echoed header may over-list a filename; security's attribution scenario is the same diagnostic ambiguity, not a refusal bypass (QA/code/security/PM).
3. **substance/info — outside patch:** unchanged runner-launch/timeout fail-open (QA/code/security/PM).

Reader artifacts: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c6.md`; `notes/research-BUG-2253-hook-hang-budget-and-gate-fail-lines-goalcheck-validate-c6.md`. State records all five terminal results; zero send-backs and no source changes.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'BUG-2253 at 3aa17de30917ca7eee9d5edb6ebc944e6dc45236 meets both SCs;
    17/17 pass, no source must_fix; strict QA rollup needs disposition of operator-excluded
    #2281.'
  open_questions:
  - id: Q-UNIT-MATRIX
    question: 'How should the already-approved #2281 exclusion be represented in the
      strict QA/worst-wins rollup? QA must report FAIL with matrix_ok:false for missing
      unit coverage, while the operator explicitly ruled that gap nonblocking. This
      requests contract disposition only, not additional patch work.'
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
    headline: Both SCs and prior blocker closed; 17/17 literal verification passes;
      strict contract forces FAIL solely for excluded unit coverage.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Spec compliance and code quality pass; monotone header membership closes
      prior diagnostic-loss blocker.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Refusal and direct-child containment retained; accepted diagnostic attribution
      ambiguity and unchanged fail-open remain advisory.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 73 changed paths, two Python paths and 71 records; no visual
      UI, scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Operator and code-maintainer perspectives pass; both SCs met at the
      review pin.
    files_touched: []
  must_fix: []
  branch: none
  escalations:
  - id: Q-UNIT-MATRIX
    raised_by: harness-qa; harness-validator-lead
    question: Apply the existing nonblocking unit-coverage scope ruling without falsifying
      QA matrix truth or silently overriding its FAIL.
    domain: Harness return-contract disposition
    routed_to: Main
    resolution: Pending contract disposition; no source remediation requested.
    decided_by: none
    recorded_as: runs/2026-11-22-05-validate-validator/digest.md
  adequacy_notes:
  - Reviewed immutable base 3dd8bb677bb2936361e3952030fc24f15bf9afc6 through pin 3aa17de30917ca7eee9d5edb6ebc944e6dc45236;
    excluded later record-only d21cf97f.
  - 'Prior high SC-01 blocker is resolved: header names are never removed, so captured
    matching PASS and echoed headers cannot hide genuine FAIL lines. MUTATED adjacency,
    ordered duplicates, tail and refusal remain preserved.'
  - 'QA executed literal T-01 verify once at a managed pin: 17 named cases, exit 0,
    11.42 seconds, empty stderr. Other lenses inspected pinned source and supplied
    evidence; no lead-executed checks.'
  - Supplied discriminate-c4 isolates the same-name-PASS regression on cycle-2 gate
    b228c3a2. Red-c4 records 14 exact-base subject failures; green-c4 records selected-group
    and full-file passes on 3c6fb908. QA and PM independently measured code equivalence
    to the review pin.
  - Six budget cases, six actual blocked-helper cases and two readiness-independent
    containment controls pass. Reconstructed-base watchdog-kill fixture exceptions
    are not independent defect evidence; observed old budgets and real call execution
    establish SC-02 discrimination.
  - Main supplied code grading exit 0, PASSING 29, no FAIL rows; no panel grader executed.
  - 'Deduplicated security attribution spoofing with the explicitly accepted Low over-listing
    advisory: neither changes refusal or constitutes a new bypass. Unit coverage and
    unchanged runner fail-open remain outside patch and are not must_fix.'
  - QA's FAIL is a verified contract constraint, not contrary evidence about either
    SC. Gate source forbids QA PASS with matrix_ok:false; another QA send-back cannot
    repair the constraint. ESCALATE requests process disposition, not another developer
    round.
  - UI independently measured 73 paths, including two Python paths, 71 records and
    zero visual paths. No visual acceptance is claimed.
  - All five readers are terminal; zero send-backs, no source changes and no additional
    rework authorization.
  sc_status:
  - id: SC-01
    verdict: met
    method: Pinned automated verification, fail-first receipt audit and independent
      source review
    evidence: QA c6 verifies diagnostic cases including PASS outer.py/PASS later.py
      echoes; discriminate-c4 fails only this case on b228c3a2; red-c4 and green-c4
      establish base/fix discrimination. Code and PM confirm monotone membership preserves
      genuine FAIL diagnoses.
  - id: SC-02
    verdict: met
    method: Pinned automated verification, supplied fail-first receipts and source
      inspection
    evidence: QA c6 passes all six budget observations, six real-block cases and delayed/never-ready
      containment controls. Red-c4 records six old-budget observations and six blocked-call
      failures; green-c4 passes on code-equivalent fix 3c6fb908.
  needs_approval: true
  severity_max: med
  matrix_ok: false
  coverage_gaps:
  - 'Required unit-kind coverage is absent, explicitly operator-disposed outside this
    patch as #2281; integration is not relabeled unit.'
  - Selected-group execution and supplied full-test-file evidence do not establish
    whole integration-kind compatibility.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: qa; code-reviewer; pm
    summary: 'Out-of-scope advisory: required unit-kind coverage remains absent, tracked
      in #2281.'
    why: Operator explicitly excluded this work. Matrix remains honestly false, but
      no patch must_fix or scope expansion is assigned; the separate contract question
      concerns how to record that ruling.
  - kind: substance
    scope: none
    severity: low
    reader: qa; code-reviewer; security-reviewer; pm
    summary: 'Accepted diagnostic accuracy cost: echoed FAIL after a matching header
      may over-list a filename.'
    why: Monotone membership deliberately favors listing. Real or echoed headers can
      enable spurious attribution, but completed nonzero runs still refuse with status
      2. The operator explicitly accepted this Low tradeoff.
  - kind: substance
    scope: none
    severity: info
    reader: qa; code-reviewer; security-reviewer; pm
    summary: 'Out-of-scope advisory: pre-existing runner-launch/timeout fail-open
      remains unchanged.'
    why: Unavailable independent execution can leave unconditional QA acceptance unverified.
      Base and pin retain the same policy; BRIEF and operator explicitly exclude changing
      it.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines/.harness/harness/features/BUG-2253-hook-hang-budget-and-gate-fail-lines/runs/2026-11-22-05-validate-validator/digest.md
```
