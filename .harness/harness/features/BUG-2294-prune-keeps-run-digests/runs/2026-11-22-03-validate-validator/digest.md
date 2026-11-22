# Validation c2 — BUG-2294

PASS at `88bf039f6ff31edbb1d5a4b2f6620762e3cc095a`: SEC-01 closed; all five final reader grades pass; no must-fix, severity maximum none. Reviewed `c1724230c4d931ad46d433c8ba93df8cf312f898..88bf039f6ff31edbb1d5a4b2f6620762e3cc095a`, emphasizing `70981edd..e51277a4ce11c91f2252026ae4dd6e0fbf12a503`; readers verified the pin contains the fix.

## Per-member outcomes

- **QA — PASS:** literal T-01 verify `python3 tests/unit/test-prune-run-evidence.py`: 25 PASS/0 FAIL, rc0, 0.93s. Required unit-kind runner: 63 files, rc0, 22.94s; changed test explicitly discovered. Exact-pin execution plus identity-audited natural-RED receipts: seven base assertion failures cover SC-01/02, four c1 failures cover SEC-01. Reds were not rerun. [QA note](../../notes/review-harness-qa-c2.md).
- **Code — PASS:** SC-01–03 compliant, unchanged selectors/refusals/CLI/ship invocations and placement; Python risk grading passes all 20 functions. [Code note](../../notes/review-harness-code-reviewer-c2.md).
- **Security — PASS:** original raiser closes SEC-01 for kept-run aliases, outside-run aliases and UI aliases; named skips precede targeting. Real UI containing symlink children is removed without following child targets, by inspected shutil semantics, not an executed child-link regression. [Security note](../../notes/review-harness-security-reviewer-c2.md).
- **UI — PASS, out of scope:** measured 20-file census, zero rendered/interactive paths. No visual/accessibility/theme pass claimed. [UI note](../../notes/review-harness-ui-reviewer-c2.md).
- **Goal-check — PASS:** operator and code maintainer pass; SC-01–03 and DEC-238 amendment met, including protected records, #2177 rationale, preserved Abandon/INV-51 and index. Initial conditional FAIL/SC-01 partial awaited QA; one evidence-completion sendback resolved it without code changes. Initial record retained. [Final supplement](../../notes/research-BUG-2294-prune-keeps-run-digests-goalcheck-validate-c2-final.md).

## Lead assessment

The formerly unrepresented destructive alias paths now have both discriminating natural-RED receipts and independent exact-pin green execution; security/code inspection agrees. No duplicate, dismissed or remaining gating findings. QA's timing-based statement that no second reviewer examined the fix is superseded at panel scope by the independent security/code reviews, not adopted as an assurance limit.

Assurance remains bounded: linked ancestors/traversal-bearing feature selection and concurrent replacement are pre-existing authorization questions, not fixed containment guarantees. SEC-C2-Q1 asks whether to scope that separately; nonblocking, no T-01 expansion. Unexercised cases: explicit --keep of a symlink, linked runs parent, linked children inside real UI, and ui-link-run digest-byte preservation. These do not contradict the measured three-shape closure.

QA's Q-QA-C2-1 bookkeeping question is resolved by retaining its two extra run-directory text logs as evidence; their creation was outside QA's domain, not precedent or a source change. Canonical QA evidence remains its note. No operator decision needed for retention.

The signed one-round/45-minute rework allowance was spent on c1's main-session-direct fix; this run spends no further code rework. One PM evidence sendback is counted separately. Settled INV-7 scope and task ownership remain accepted. Must-fix: none. Open question: SEC-C2-Q1 only.

```yaml
VERDICT: PASS
DIGEST:
  headline: '88bf039f6ff31edbb1d5a4b2f6620762e3cc095a: SEC-01 closed; five-reader
    final panel passes with no must-fix.'
  open_questions:
  - id: SEC-C2-Q1
    question: Should a separate root/feature authorization task reject linked ancestors
      and traversal-bearing operator feature arguments, and define concurrent-writer
      expectations? These pre-existing paths are not contained by the fix; recommend
      deciding that boundary separately without expanding T-01.
    blocking: false
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Exact-pin literal verify 25 PASS/0 FAIL; required unit runner 63 files
      rc0; natural-RED receipts audited.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: "SC-01\u201303 compliant; reported symlink paths closed; pinned Python\
      \ risk grading passes."
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: SEC-01 closed for static run/UI aliases; pre-existing ancestor authorization
      separately scoped.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 20-file census contains no rendered or interactive UI; scoped
      out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: "Final evidence reconciliation: both perspectives pass; SC-01\u2013\
      03 and DEC-238 amendment met."
    files_touched: []
  must_fix: []
  branch: none
  escalations:
  - id: Q-QA-C2-1
    raised_by: harness-qa
    question: Delete or retain two QA text logs copied outside QA's domain into the
      validator run directory?
    domain: validator run bookkeeping
    routed_to: harness-validator-lead
    resolution: Retain qa-c2-verify.txt and qa-c2-kind.txt as supplemental evidence;
      acknowledge domain violation without authorizing recurrence. Canonical QA evidence
      remains its review note.
    decided_by: harness-validator-lead
    recorded_as: runs/2026-11-22-03-validate-validator/digest.md
  adequacy_notes:
  - Reviewed c1724230c4d931ad46d433c8ba93df8cf312f898..88bf039f6ff31edbb1d5a4b2f6620762e3cc095a,
    emphasizing remediation 70981edd6f9f110965a0148b4490ed2673d262dc..e51277a4ce11c91f2252026ae4dd6e0fbf12a503.
    Readers verified fix ancestry and unchanged source/test from fix to pin.
  - 'QA independently executed literal T-01 verify `python3 tests/unit/test-prune-run-evidence.py`
    at pin: 25 PASS/0 FAIL, rc0, 0.93s. Required unit-kind runner rc0, 63 files, 22.94s,
    explicitly includes changed test. Evidence: notes/review-harness-qa-c2.md.'
  - 'SC-01/SC-02 natural-RED receipt identity audited against exact git objects: base
    c1724230 yields seven semantic assertion failures, including ten lost digests/post-prune
    INV-7; c1 70981edd yields four symlink assertion failures while all twenty earlier
    checks pass. Known reds were not rerun; current green was independently executed.'
  - Security's original raiser closes SEC-01 statically; QA execution covers all three
    reported link shapes and nonempty destination-byte comparisons. Code/security
    agree on unchanged keep/refusal/CLI/ship behavior. No surviving, duplicate or
    dismissed findings.
  - "PM initial FAIL/SC-01 partial was conditional on concurrent QA completion. One\
    \ same-pin evidence-completion sendback returned PASS for operator, code maintainer\
    \ and SC-01\u201303; original note retained and final supplement is notes/research-BUG-2294-prune-keeps-run-digests-goalcheck-validate-c2-final.md.\
    \ cycles_used=1 records that sendback, not another code rework round."
  - The signed one-round/45-minute rework allowance was spent by the c1 main-session-direct
    fix. No code remediation remains; any actual T-01 remediation routes to Main,
    not an engineering persona.
  - UI scope-out rests on a measured twenty-path census, not visual verification.
    Security/code/PM use inspection, with only QA executing the regression suite.
    QA's timing-based no-second-reviewer statement does not describe the completed
    panel.
  - SEC-C2-Q1 is a nonblocking, pre-existing ancestor/selection/concurrent-writer
    boundary question, deduplicated across security and final PM. Do not read PASS
    as a realpath authorization or race-safety guarantee. Settled INV-7 scope and
    task ownership were not reopened.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated and pinned inspection
    evidence: Exact-pin verify 25 PASS/0 FAIL; receipt-audited semantic base/symlink
      reds; security original raiser closes SEC-01 for three static link shapes.
  - id: SC-02
    verdict: met
    method: automated
    evidence: Exact-pin ten-run hash-bound empty-keep/final-BLOCKED/no-UI regression
      passes; audited base receipt loses ten digests and fails post-prune INV-7 with
      sound preconditions.
  - id: SC-03
    verdict: met
    method: inspection
    evidence: Code/security/PM pinned inspection confirms unchanged selectors, --keep,
      refusals, CLI, ship invocations/placement and matching UI-only retention prose.
  - id: DEC-238
    verdict: met
    method: inspection
    evidence: 'PM final goalcheck confirms UI-only ship amendment, protected records,
      #2177 rationale, preserved Abandon/INV-51 and coupled index; T-01 owns disposition.'
  needs_approval: false
  severity_max: none
  matrix_ok: true
  coverage_gaps:
  - Symlink explicitly named in --keep is not exercised.
  - Linked runs parent and symlinked children inside real UI are not regression-tested;
    ancestor authorization is separately scoped and child-target preservation is static
    library analysis.
  - ui-link-run digest.md byte preservation is not asserted in the new symlink fixture;
    ordinary fixtures assert all run-record bytes.
  - Natural-RED evidence is receipt-audited, not freshly rerun; no mutation proof
    beyond base-versus-fix natural reds.
  findings: []
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/runs/2026-11-22-03-validate-validator/digest.md
```
