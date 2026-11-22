# BUG-2253 rework-2 regate — FAIL

Pin `645febc89615f9a508a5cc66122a02a80ddabaac`, base `3dd8bb677bb2936361e3952030fc24f15bf9afc6`. **SC-02 met; SC-01 partial.** Both prior concrete counterexamples are repaired, but the same diagnostic-loss obligation has another confirmed failure. No source changed. The authorized second developer rework round is spent; this assessment authorizes no additional round.

## One blocking remedy — T-01 / SC-01, substance/high

Preserve the genuine file FAIL when captured output contains a same-name PASS, and add a discriminating regression. Producer stream: header `----- outer.py (exit 1, 0.30s) -----`, captured `PASS outer.py`, genuine `FAIL outer.py`, then >20 passing lines. `_closes_failed_block` consumes the header on the captured PASS and discards the real FAIL (`validate-digest.py:2512–2525`; producer `run_pool.py:107–113` emits the body verbatim). QA's bounded pinned-parser probe returned `[]`; code and PM independently reasoned the same mechanism. Exact probe bytes were not retained, so the execution account is less reproducible than the source trace. This is the existing SC-01 obligation, not a new finding class or producer-format requirement.

## Reconciliation and adequacy

QA c5 retracts c4's Low/out-of-scope classification and unsupported assertion that only a producer-format change could fix it. Code/PM's **high** rating is preserved: the patch's core operator diagnosis disappears, although refusal remains intact. Security's PASS is compatible: no new privilege or acceptance bypass, not diagnostic completeness. QA's developer-routing Q-fix is the must-fix above, not an unanswered operator requirement question. One QA assessment send-back; no further test execution or developer rework.

SC-02's readiness-independent watchdog and delayed/never-ready containment are accepted: QA ran the literal verify once at a managed pin, **17 cases, exit 0, 11.03s**, no surviving children. Both containment rows die before readiness; six budget and six real-block rows pass. QA measured code equality `b228c3a2..645febc8`. Supplied red-c3 records 14 failures against reconstructed exact-base subjects; discriminate-c3 isolates the echoed-header gate repair, **not** the old watchdog. Green-c3 selected/full-file evidence is not complete integration-kind coverage. Existing fail-first evidence does not cover the new same-name-PASS gap. Main-supplied grading: PASSING 29, no FAIL; no grader executed by this panel. Code quality stage withheld after compliance failed.

## Nonblocking dispositions

- QA's balanced echoed FAIL in a passing block is a distinct **Low** accuracy advisory; not a second blocker.
- Unit-kind absence remains `matrix_ok: false`, explicitly operator-disposed to **#2281** outside this patch. Integration is not relabeled unit. The previously reported PASS/matrix contract tension does not determine this FAIL.
- Existing runner-launch fail-open remains unchanged and out of scope. Neither settled advisory reopens scope.
- UI measured 53 paths: two Python executable/test paths and 51 records, no visual surface. Only QA executed verification/probes; other lenses inspected source/evidence.

Reader pointers: `notes/review-harness-qa-c5.md` (supersedes c4 assessment, retains its execution); `notes/review-harness-code-reviewer-c4.md`; `notes/review-harness-security-reviewer-c4.md`; `notes/review-harness-ui-reviewer-c4.md`; `notes/research-BUG-2253-hook-hang-budget-and-gate-fail-lines-goalcheck-validate-c4.md`.

Open questions: none. Remediation stays main-session-direct under T-01 / DEC-174; the orchestrator owns disposition under the exhausted rework ruling.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'BUG-2253 at 645febc89615f9a508a5cc66122a02a80ddabaac: SC-02 met, but
    SC-01 still loses genuine FAIL diagnoses after captured same-name PASS.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: 'c5 retracts c4 scope assurance: executed matching-PASS probe loses
      the genuine FAIL despite 17 green selected cases.'
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Prior unmatched-header and readiness counterexamples close; same-name
      captured PASS still suppresses genuine FAIL.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No new exploitable security defect; refusal policy and direct-child
      ownership remain intact.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 53-path pinned diff contains no visual UI; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator perspective partial under SC-01; code-maintainer perspective
      passes SC-02.
    files_touched: []
  must_fix:
  - "P1 \u2014 T-01 / SC-01: preserve genuine FAIL file diagnoses when captured output\
    \ contains PASS matching the enclosing filename; add a discriminating regression\
    \ without changing producer formats, tail or refusal policy."
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed base 3dd8bb677bb2936361e3952030fc24f15bf9afc6 through immutable pin 645febc89615f9a508a5cc66122a02a80ddabaac,
    excluding later record-only bef1d148.
  - 'Both prior concrete counterexamples are repaired: unmatched echoed headers no
    longer hide the producer close or subsequent mutation lines, and containment no
    longer waits for readiness.'
  - 'QA executed the literal T-01 verification once at a managed pin: 17 cases, exit
    0, 11.03s, no surviving children. Other readers inspected source and evidence;
    code quality stage was withheld after compliance failed.'
  - QA reports a bounded non-mutating parser probe returned [] for same-name captured
    PASS followed by genuine FAIL. Exact probe bytes were not retained; code and PM
    independently supply the reproducible source-level scenario.
  - 'QA c5 explicitly retracts c4''s Low/out-of-scope classification and unsupported
    producer-format-only remedy claim. Code/PM high severity is preserved: core operator
    diagnosis is lost even though refusal remains secure.'
  - QA c4's ESCALATE is superseded by c5 FAIL on the in-scope SC-01 defect. Its Q-fix
    is resolved into must_fix, not forwarded as an unanswered operator scope question.
  - QA measured executable-code equality between b228c3a2 and the review pin. Supplied
    red-c3 records 14 failures using reconstructed exact-base subjects; discriminate-c3
    isolates the gate repair, not the old watchdog; green-c3 covers the selected group
    and full integration file.
  - Main supplied code grading exit 0, PASSING:29, no FAIL rows through code-equivalent
    b228c3a2; no grader was executed by this panel.
  - 'Matrix remains false due to operator-excluded unit coverage tracked separately
    in #2281. This and unchanged runner-launch fail-open remain nonblocking and outside
    patch scope.'
  - Security PASS establishes no new exploitable policy change, not full diagnostic
    acceptance. UI measured two Python paths plus 51 records and no visual surface.
  - One QA assessment send-back occurred; no developer remediation or additional suite
    execution occurred. Authorized second developer rework round is spent; this report
    authorizes no additional round.
  sc_status:
  - id: SC-01
    verdict: partial
    method: selected automated verification, QA parser probe, independent pinned-source
      review
    evidence: "notes/review-harness-qa-c5.md reports named=[] after captured same-name\
      \ PASS followed by genuine FAIL; code and PM c4 trace validate-digest.py:2512\u2013\
      2525 and run_pool.py:107\u2013113. Existing buried/unmatched-header regressions\
      \ pass but omit this scenario."
  - id: SC-02
    verdict: met
    method: pinned automated verification, supplied fail-first receipts, source inspection
    evidence: QA c4 executed all six budget rows, six actual blocked-helper rows and
      delayed/never-ready containment within the 17-case verify; readiness-independent
      watchdog kills before readiness. red-c3 and green-c3 preserve prior behavioral
      discrimination.
  needs_approval: false
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - SC-01 lacks a regression for captured same-name PASS consuming the header before
    the genuine FAIL; no red-to-green evidence exists for this remaining scenario.
  - Balanced echoed FAIL inside a passing block is over-reported; separate Low diagnostic-accuracy
    advisory.
  - 'Required unit-kind coverage is absent, explicitly outside this patch under operator
    disposition #2281.'
  - Complete integration kind was not rerun; selected verification and supplied full-file
    evidence do not establish whole-kind compatibility.
  - discriminate-c3 carries the final watchdog and therefore does not demonstrate
    failure of the old watchdog implementation.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; pm; qa-c5 confirmation
    summary: 'T-01 / SC-01: captured matching PASS suppresses the genuine producer
      FAIL.'
    why: For producer header outer.py, captured PASS outer.py removes the matching
      open header; genuine FAIL outer.py is then discarded. More than 20 later passing
      lines also remove it from the tail. QA reports an executed empty named list;
      code and PM independently trace the mechanism. This is the existing diagnostic-loss
      obligation, not new scope.
  - kind: substance
    scope: none
    severity: low
    reader: qa-c4; qa-c5
    summary: 'Nonblocking accuracy advisory: a balanced echoed FAIL inside a passing
      block is over-reported.'
    why: QA reports this separate parser ambiguity from its bounded c4 probe. Retained
      at its reported Low severity, not merged into or used to amplify the genuine-diagnosis-loss
      blocker.
  - kind: substance
    scope: none
    severity: med
    reader: qa; prior validation
    summary: 'Out-of-scope advisory: required unit-kind coverage is absent and tracked
      in #2281.'
    why: Current QA still measures zero covering unit tests; matrix_ok remains false.
      The operator explicitly disposed this outside the patch, so it does not block
      or authorize scope expansion.
  - kind: substance
    scope: none
    severity: info
    reader: security-reviewer; prior validation
    summary: 'Out-of-scope advisory: pre-existing runner-launch fail-open remains
      unchanged.'
    why: Security rechecked unchanged launch/timeout policy. The BRIEF excludes changing
      that policy, and the operator explicitly retained the exclusion; no blocker
      is assigned.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines/.harness/harness/features/BUG-2253-hook-hang-budget-and-gate-fail-lines/runs/2026-11-21-04-validate-validator/digest.md
```
