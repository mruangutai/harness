# BUG-2253 regate — FAIL

Pin `2e96b583dadaff642873566c3234dde6af0eda74`, base `3dd8bb677bb2936361e3952030fc24f15bf9afc6`. Both perspectives remain **partial**: ordinary whitespace names and the 2.5s late starter are repaired, but two in-scope acceptance holes survive. No source changed. The assigned developer rework round is spent; this report authorizes no additional round.

## Ranked T-01 remedies

1. **SC-02 · substance/high:** obtain termination authority before readiness and independently bound/reap the missing-timeout probe. Polling a PID written only after startup cannot bound delayed/absent readiness (`test-validate-digest.py:6551–6576`). QA's bounded probe with delay 5s was killed at 5.2s, not the 2s deadline; permanent pre-readiness stall remains a reasoned, unexecuted case. The 2.5s containment test proves eventual post-readiness cleanup only. Fix containment before exercising further adversarial probes.
2. **SC-01 · substance/high:** preserve real producer verdicts despite header-shaped captured output (`validate-digest.py:2513–2524`; producer `run_pool.py:107–113` prints body verbatim). An unmatched echoed fixture header prevents the enclosing FAIL from closing and hides subsequent MUTATED lines. QA's isolated parser probe returned `named=[]`. Add failing- and successful-block echo regressions while retaining spaces, echo exclusion, tail and refusal behavior.

## Assessment and evidence

Code c2 raised both defects; QA c3 confirmed them by bounded probes and explicitly withdraws c2's closure assurance/ESCALATE. Existing selected verification remains green: **15 cases, exit 0, 9.43s**, executed once by QA at the exact pin. The green suite omits these counterexamples. PM's PASS rests on those same insufficient cases; lead assessment is partial for operator/SC-01 and maintainer/SC-02. Security's PASS establishes no new exploitable policy change, not complete diagnostic or deadline acceptance. UI measured 32 changed files and no visual UI. Only QA executed panel checks; code quality stage remains withheld.

Exact-base carried-test red and immutable fix green with separate streams repair prior receipt-form concerns (`notes/receipts/red-c2.*`, `green-c2.*`). Green code at `6cbdc417` is unchanged at the pin. The full receipt is execution of the **integration test file**, not a rerun of the complete integration kind; no broader suite claim. Supplied mechanical grading: exit 0, PASSING:25, no FAIL rows, base through `6cbdc417`; not reader execution. Red qa-record timeout-outcome ambiguity is an assurance qualification, not a separate gate. Correct-but-slow startup causing readiness failure is inherent to the required handshake, not another requested fix.

## Advisories only

Matrix remains false: unit-kind coverage is absent outside T-01 ownership. Operator scope/exception decision only; no silent substitution of integration for unit. QA additionally reports a persona-contract conflict for advisory-only matrix false plus PASS; that claim was not independently audited. Existing runner-launch fail-open is unchanged and out of scope (`security c2` policy review). Neither advisory causes this FAIL. One QA assessment send-back, no developer remediation in this run.

Reader artifacts: `notes/review-harness-qa-c3.md` (supersedes c2); `notes/review-harness-code-reviewer-c2.md`; `notes/review-harness-security-reviewer-c2.md`; `notes/review-harness-ui-reviewer-c2.md`; `notes/research-BUG-2253-hook-hang-budget-and-gate-fail-lines-goalcheck-validate-c2.md`.

Open questions: nonblocking unit-scope/exception ruling and reported advisory-matrix contract tension. No new product scope or blocking requirement question.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'BUG-2253 at 2e96b583dadaff642873566c3234dde6af0eda74 still fails SC-01/SC-02:
    echoed headers hide diagnoses and the watchdog remains unbounded before readiness.'
  open_questions:
  - id: Q-unit-floor
    question: 'Advisory only: required unit coverage exceeds T-01 ownership; operator
      decides scope or governed exception. Integration is not automatically substituted
      for unit.'
    blocking: false
  - id: Q-advisory-matrix-contract
    question: QA reports its persona contract forbids PASS with matrix_ok:false even
      when missing unit coverage is explicitly advisory. This reported Harness tension
      was not independently audited; operator may investigate separately.
    blocking: false
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: c3 withdraws c2 closure assurance; bounded probes confirm both acceptance
      counterexamples despite 15 green selected cases.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Echoed headers poison diagnostic framing; missing-timeout containment
      depends on readiness.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No new exploitable security finding; production refusal and timeout
      policy unchanged.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 32-file pinned diff has no visual UI; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Reader graded both perspectives PASS; lead overrides completion assessment
      using QA-confirmed counterexamples.
    files_touched: []
  must_fix:
  - "P1 \u2014 T-01 / SC-02: independently bound and reap missing-timeout probes before\
    \ child readiness; acquire termination authority before the handshake and cover\
    \ delayed/absent readiness. Fix containment before further adversarial probes."
  - "P2 \u2014 T-01 / SC-01: preserve genuine producer FAIL/MUTATED diagnoses despite\
    \ unmatched header-shaped captured output; cover echoes inside failing and successful\
    \ blocks while preserving whitespace names, tail, and refusal behavior."
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed immutable base 3dd8bb677bb2936361e3952030fc24f15bf9afc6 through pin 2e96b583dadaff642873566c3234dde6af0eda74,
    not later record-only commits.
  - Ordinary whitespace filenames and the supplied 2.5-second late starter are repaired.
    General diagnostic and readiness-independent containment obligations are not.
  - 'QA executed the literal selected verify once at the exact pin: exit 0, 15 passing
    cases, 9.43 seconds. These cases omit both confirmed counterexamples.'
  - 'QA c3 executed bounded non-mutating probes: parser returned named=[] despite
    genuine FAIL/MUTATED; delayed child was killed at 5.2 seconds rather than the
    watchdog''s 2-second deadline. Permanent no-readiness hang is source reasoning,
    not an executed indefinite probe.'
  - QA c3 explicitly withdraws c2's closure assurance and advisory-only ESCALATE.
    One assessment send-back occurred; no developer remediation occurred in this run.
  - PM's PASS depends on insufficient selected cases; lead assesses both perspectives
    partial. Security PASS establishes no new exploitable policy change, not full
    acceptance. Code and QA substance/high ratings are preserved.
  - Only QA executed panel verification/probes. Other readers inspected source and
    evidence; code quality stage was withheld after compliance failed.
  - New exact-base carried-test red and immutable-fix green receipts with separate
    streams resolve prior provenance concerns. Fix 6cbdc417 has unchanged executed
    code at the review pin.
  - Supplied green-c2-full evidence covers the integration test file, not the complete
    integration kind. This panel claims no complete-kind rerun.
  - Main supplied mechanical grading exit 0, PASSING:25, no FAIL rows for base through
    6cbdc417; accepted as supplied code-equivalent evidence, not reader execution.
  - The red qa-record timeout-outcome ambiguity remains an assurance qualification,
    not a separate blocker. Readiness-related startup flake exposure is assessed as
    inherent to the required handshake, not an additional requested fix.
  - Missing unit coverage and unchanged runner-launch fail-open remain advisory only.
    Neither causes this FAIL. The assigned developer rework round is spent; this report
    authorizes no further round.
  sc_status:
  - id: SC-01
    verdict: partial
    method: selected automated verification, source review, and executed counterexample
    evidence: notes/review-harness-qa-c3.md confirms _run_pool_file_lines returns
      [] when an unmatched echoed fixture header precedes the genuine enclosing FAIL
      and later MUTATED. Ordinary space-name red/green evidence remains valid.
  - id: SC-02
    verdict: partial
    method: selected automated verification, source review, and bounded containment
      probe
    evidence: "notes/review-harness-qa-c3.md: six budget/block rows green, but a five-second\
      \ readiness delay causes watchdog termination only at 5.2s. tests/integration/test-validate-digest.py:6551\u2013\
      6576 has no readiness-independent deadline."
  needs_approval: false
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - 'SC-01: unmatched header-shaped captured output inside successful/failing producer
    blocks is not regression-covered.'
  - 'SC-02: missing timeout combined with delayed/absent readiness lacks independently
    bounded containment and regression coverage.'
  - Required unit-kind coverage is missing outside T-01 ownership; advisory operator
    decision only.
  - Complete integration kind was not independently rerun by this panel; supplied
    full evidence is the integration test file.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; qa-c3
    summary: 'T-01 / SC-02: watchdog cannot bound missing-timeout probes before readiness.'
    why: The watchdog obtains the child PID only after the blocker writes readiness.
      QA's five-second-delay probe terminated at 5.2s, not 2s; permanent pre-readiness
      stall remains unbounded by source reasoning. The existing 2.5s case proves eventual
      post-readiness cleanup only.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; qa-c3
    summary: 'T-01 / SC-01: echoed header markers suppress genuine FAIL and MUTATED
      diagnoses.'
    why: "validate-digest.py:2513\u20132524 pushes unescaped header-shaped child output\
      \ and closes only the stack top. run_pool.py:107\u2013113 prints captured bodies\
      \ verbatim. QA reproduced named=[] after an unmatched fixture header, genuine\
      \ outer FAIL, passing blocks, and a final MUTATED line."
  - kind: substance
    scope: none
    severity: med
    reader: qa; prior validation
    summary: 'Out-of-scope advisory: required unit-kind coverage remains missing.'
    why: The changed runtime gate triggers the unit floor, but T-01 owns no tests/unit
      file. Matrix remains false without silently substituting integration; the assignment
      explicitly makes this an operator advisory, not a blocker.
  - kind: substance
    scope: none
    severity: info
    reader: security-reviewer; prior pm
    summary: 'Out-of-scope advisory: existing runner-launch failure remains fail-open.'
    why: Security c2 rechecked unchanged launch/timeout policy. The BRIEF excludes
      altering refusal policy; this retained operator advisory does not gate the patch.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines/.harness/harness/features/BUG-2253-hook-hang-budget-and-gate-fail-lines/runs/2026-11-21-03-validate-validator/digest.md
```
