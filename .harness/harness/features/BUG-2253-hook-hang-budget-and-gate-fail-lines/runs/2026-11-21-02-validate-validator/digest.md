# BUG-2253 validation — FAIL

Pin `21e064c9475e35a4abfdd71b5b5cdd23517c0659`, base `3dd8bb677bb2936361e3952030fc24f15bf9afc6`. Both perspectives are partial despite green suites. Two acceptance defects require T-01 remediation; no source changed by this panel.

## Ranked remedies

1. **SC-02, substance/high:** make the missing-timeout probe independently bounded and cleaned up regardless of startup/readiness. The one-shot timer starts before setup and silently abandons an absent/empty PID; delayed startup beyond two seconds can escape it and sleep for 3600 seconds (`tests/integration/test-validate-digest.py:6533–6581`). Require blocker readiness before crediting a genuine blocked execution; test delayed-start plus missing-timeout explicitly. Fix this containment before exercising new adversarial probes.
2. **SC-01, substance/high:** preserve whitespace-bearing producer filenames in the summary without changing tail/refusal behavior. Fullmatch `\S+` drops `MUTATED notes/my file.md` above the last 20 lines, although the producer prints raw paths (`validate-digest.py:2495–2508`; `run_pool.py:113,134`). Add regression coverage for this case.

Code and PM rate both high; security rates the same defects low because neither adds attacker capability. Retain those source ratings: consolidated high is acceptance/completion risk, not a claim of high exploitability. QA c1 withdraws c0's contrary adequacy claims. Call-only timing is sound; the regex and readiness/watchdog deviations are not. The existing selector amendment is approved.

## Evidence and limits

QA measured 14 selected cases green in 6.7s; full integration green, 88 files, 122.5s. QA reproduced buried-case red with the exact base gate; budget reds used the final test harness with six literal-three-second callsites, not execution of the full base subject. These prove the original defects, not the omitted counterexamples. Supplied red/green receipts lack complete separate streams and immutable green identity; QA's pinned execution resolves current-green identity/duration, not historical capture completeness. Mechanical code grading is unmeasured; inferred `pass` is not credited.

## Advisory operator decisions — not additional blockers

- Matrix remains false: runtime-code bugfix requires unit coverage, but no unit file covers this change. A unit-file remedy lies outside T-01; operator decides scope or a governed exception. Integration is not silently substituted.
- PM's unchanged runner-launch fail-open concern is out of scope; retain as advisory only (`validate-digest.py:2480–2483`).
- Historical receipt-form limitation is acknowledged, not a new code gate; retain original receipts and QA c0/c1 qualifications.

## Reader record

QA **FAIL** (`notes/review-harness-qa-c1.md`, supersedes c0 assurance); code **FAIL** (`notes/review-harness-code-reviewer-c0.md`, quality stage withheld); security **PASS** with two merged advisories (`notes/review-harness-security-reviewer-c0.md`); UI **PASS**, measured 14-file no-visual-UI scope-out (`notes/review-harness-ui-reviewer-c0.md`); PM **FAIL**, operator/maintainer partial (`notes/research-BUG-2253-hook-hang-budget-and-gate-fail-lines-goalcheck-validate-c0.md`). Only QA executed tests. One QA assessment send-back, no developer remediation round. Open operator decision: unit-test scope/exception; no blocking product question.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'BUG-2253 at 21e064c9475e35a4abfdd71b5b5cdd23517c0659 fails SC-01/SC-02:
    whitespace filenames disappear and delayed-start missing-timeout probes escape
    the watchdog.'
  open_questions:
  - id: OQ-unit-scope
    question: 'Advisory operator decision: required unit coverage is missing, but
      adding tests/unit files exceeds T-01 ownership. Extend scope or explicitly rule
      on a governed exception; integration does not automatically satisfy unit.'
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
    headline: Green suites do not discharge both SCs; missing unit floor; c0 assurance
      withdrawn in c1.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Whitespace filenames omitted; watchdog can miss late-starting children.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Refusal policy intact; overlapping diagnostic/containment defects rated
      low for security impact.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 14-file diff contains no built visual UI; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator and code-maintainer perspectives are partial.
    files_touched: []
  must_fix:
  - "P1 \u2014 T-01 / SC-02: independently bound and clean up missing-timeout probes\
    \ regardless of startup/readiness; require blocker readiness and cover delayed-start\
    \ plus missing-timeout behavior."
  - "P2 \u2014 T-01 / SC-01: retain legitimate whitespace-containing FAIL/MUTATED\
    \ filenames above the unchanged diagnostic tail, with a regression and unchanged\
    \ refusal policy."
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed immutable base 3dd8bb677bb2936361e3952030fc24f15bf9afc6 through pin 21e064c9475e35a4abfdd71b5b5cdd23517c0659,
    not later record-only commits.
  - 'QA measured targeted verification exit 0: 14 cases, 6.7s; full integration exit
    0: 88 files, 122.5s. These passing cases omit both reported counterexamples.'
  - QA c1 retracts c0's both-SCs-proven/watchdog-adequate claims and changes ESCALATE
    to FAIL. One assessment send-back, no developer remediation round.
  - Call-only timing is sound and the selector amendment approved. One-token matching
    and readiness/watchdog simplifications narrow acceptance and are unsound.
  - 'QA reproduced SC-01 red with the exact base gate. SC-02 red used the final harness
    with six literal-three-second callsites: source-equivalent reconstructed evidence,
    not full-base execution.'
  - Only QA executed verification. Other readers inspected source/evidence. Mechanical
    grading is unmeasured; the code review's inferred pass is not credited; its quality
    stage was withheld after compliance failed.
  - Receipt-form concerns are retained and qualified, not additional blockers. QA
    supplies pinned current-green identity/duration but does not retroactively complete
    historical streams.
  - Security's low ratings concern exploitability; code/PM's high ratings concern
    signed acceptance and unbounded regression execution. Both source ratings are
    preserved; consolidated severity is high.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated verification plus source review
    evidence: "QA notes/review-harness-qa-c1.md: buried-file/fallback cases green\
      \ and base gate red. validate-digest.py:2495\u20132508 excludes whitespace-bearing\
      \ names emitted verbatim by run_pool.py:113,134."
  - id: SC-02
    verdict: partial
    method: automated verification plus source review
    evidence: "QA c1: six default/rebound observations and six blocking cases green.\
      \ test-validate-digest.py:6533\u20136581 has a one-shot PID-dependent timer\
      \ that can abandon delayed-start missing-timeout probes; readiness is unasserted."
  needs_approval: false
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - 'SC-01: no whitespace-containing producer filename regression.'
  - 'SC-02: no independent containment proof for missing timeout combined with startup
    beyond the watchdog deadline; genuine blocker readiness is not established.'
  - Required unit kind missing; remedy outside T-01 is advisory operator scope decision,
    not an added blocker.
  - Historical receipts lack complete separate streams and immutable green identity;
    SC-02 base subject is reconstructed.
  - Mechanical complexity grading unmeasured.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; pm; security-reviewer; qa-c1
    summary: 'T-01 / SC-02: one-shot watchdog can miss delayed startup and leave a
      missing-timeout probe hanging.'
    why: "test-validate-digest.py:6533\u20136581 starts its timer before setup, swallows\
      \ absent/empty PID, and never retries or independently contains/reaps the probe\
      \ group. A child starting after two seconds can sleep for 3600 seconds. Code/PM:\
      \ high; security: low; acceptance risk governs consolidated high. Fix containment\
      \ before adding adversarial probes."
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; pm; security-reviewer; qa-c1
    summary: 'T-01 / SC-01: one-token fullmatch drops legitimate whitespace-containing
      file diagnoses.'
    why: 'validate-digest.py:2495,2506 rejects MUTATED notes/my file.md although run_pool.py:134
      emits raw paths. Above 20 passing lines the diagnosis disappears entirely. Code/PM:
      high; security: low; signed acceptance failure governs consolidated high.'
  - kind: form
    scope: none
    severity: med
    reader: code-reviewer; pm; qa-c1
    summary: 'T-01 / SC-01/SC-02: historical receipts have incomplete provenance and
      stream capture; assessed and qualified, not an additional code blocker.'
    why: Code rates low and PM med. red.txt names source-equivalent 3769919f and reconstructed
      timeout sites; green.txt lacks immutable identity/duration and complete separate
      streams. QA's pinned run resolves current-green identity/duration, not historical
      completeness. Original records remain unchanged.
  - kind: substance
    scope: none
    severity: med
    reader: qa
    summary: 'Out-of-scope advisory: required unit coverage is missing; operator scope
      decision only.'
    why: Bugfix touches_runtime_code applies to validate-digest.py, but no tests/unit
      file covers this change. Integration green cannot substitute. A unit-file remedy
      exceeds T-01's file set; matrix remains false without making this an additional
      scope blocker.
  - kind: substance
    scope: none
    severity: info
    reader: pm; qa-c1
    summary: 'Out-of-scope advisory: existing runner-launch failure remains fail-open.'
    why: "validate-digest.py:2480\u20132483 returns 0 with an unverified-suite diagnostic.\
      \ Unchanged refusal-policy behavior is explicitly outside this patch; operator\
      \ decides whether to pursue it."
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines/.harness/harness/features/BUG-2253-hook-hang-budget-and-gate-fail-lines/runs/2026-11-21-02-validate-validator/digest.md
```

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'BUG-2253 at 21e064c9475e35a4abfdd71b5b5cdd23517c0659 fails SC-01/SC-02:
    whitespace filenames disappear and delayed-start missing-timeout probes escape
    the watchdog.'
  open_questions:
  - id: OQ-unit-scope
    question: 'Advisory operator decision: required unit coverage is missing, but
      adding tests/unit files exceeds T-01 ownership. Extend scope or explicitly rule
      on a governed exception; integration does not automatically satisfy unit.'
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
    headline: Green suites do not discharge both SCs; unit floor missing; c0 assurance
      withdrawn in c1.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Two acceptance failures; supplied byte-equivalent-range grading establishes
      mechanical pass.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Refusal policy intact; overlapping defects rated low for security impact.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 14-file diff contains no built visual UI; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator and code-maintainer perspectives are partial.
    files_touched: []
  must_fix:
  - "P1 \u2014 T-01 / SC-02: independently bound and clean up missing-timeout probes\
    \ regardless of startup/readiness; require blocker readiness and cover delayed-start\
    \ plus missing-timeout behavior."
  - "P2 \u2014 T-01 / SC-01: retain legitimate whitespace-containing FAIL/MUTATED\
    \ filenames above the unchanged diagnostic tail, with a regression and unchanged\
    \ refusal policy."
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed immutable base 3dd8bb677bb2936361e3952030fc24f15bf9afc6 through pin 21e064c9475e35a4abfdd71b5b5cdd23517c0659,
    not later record-only commits.
  - 'QA measured targeted verification exit 0: 14 cases, 6.7s; full integration exit
    0: 88 files, 122.5s. Passing cases omit both reported counterexamples.'
  - QA c1 retracts c0's both-SCs-proven/watchdog-adequate claims and changes ESCALATE
    to FAIL. One assessment send-back, no developer remediation round.
  - Call-only timing is sound and selector amendment approved. One-token matching
    and readiness/watchdog simplifications narrow acceptance and are unsound.
  - 'QA reproduced SC-01 red with exact base gate. SC-02 red used final harness with
    six literal-three-second callsites: reconstructed evidence, not full-base execution.'
  - 'Grading correction supersedes the initial digest''s unmeasured-evidence claim:
    code reviewer subsequently received Main''s code-grade.py --base 3769919f --head
    16ec2047 result, exit 0, PASSING: 21, no failing rows, plus supplied Python endpoint
    equivalence to the pinned range. Credit supplied mechanical pass, not an exact-endpoint
    rerun or reader execution. See runs/2026-11-21-02-validate-validator/grading-update.md.'
  - Only QA executed panel verification; other readers inspected source/evidence.
    Code quality stage withheld after compliance failed.
  - Receipt-form concerns retained and qualified, not additional blockers. QA supplies
    pinned current-green identity/duration without retroactively completing historical
    streams.
  - Security's low ratings concern exploitability; code/PM high ratings concern acceptance
    and unbounded regression execution. Source ratings preserved; consolidated severity
    high.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated verification plus source review
    evidence: "QA notes/review-harness-qa-c1.md: buried-file/fallback green and base\
      \ gate red. validate-digest.py:2495\u20132508 excludes whitespace names emitted\
      \ verbatim by run_pool.py:113,134."
  - id: SC-02
    verdict: partial
    method: automated verification plus source review
    evidence: "QA c1: six budget observations and six blocking cases green. test-validate-digest.py:6533\u2013\
      6581 has one-shot PID-dependent timer that can abandon delayed-start missing-timeout\
      \ probes; readiness unasserted."
  needs_approval: false
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - 'SC-01: no whitespace-containing producer filename regression.'
  - 'SC-02: no independent containment proof for missing timeout plus startup beyond
    watchdog deadline; genuine blocker readiness not established.'
  - Required unit kind missing; remedy outside T-01 is advisory operator scope decision,
    not an added blocker.
  - Historical receipts lack complete separate streams and immutable green identity;
    SC-02 base subject reconstructed.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; pm; security-reviewer; qa-c1
    summary: 'T-01 / SC-02: one-shot watchdog can miss delayed startup and leave a
      missing-timeout probe hanging.'
    why: "test-validate-digest.py:6533\u20136581 starts timer before setup, swallows\
      \ absent/empty PID and never retries or independently contains/reaps probe group.\
      \ Child starting after two seconds can sleep for 3600 seconds. Code/PM high;\
      \ security low; acceptance risk governs consolidated high. Fix containment before\
      \ adding adversarial probes."
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; pm; security-reviewer; qa-c1
    summary: 'T-01 / SC-01: one-token fullmatch drops legitimate whitespace-containing
      diagnoses.'
    why: validate-digest.py:2495,2506 rejects MUTATED notes/my file.md although run_pool.py:134
      emits raw paths. Above 20 passing lines diagnosis disappears entirely. Code/PM
      high; security low; signed acceptance failure governs consolidated high.
  - kind: form
    scope: none
    severity: med
    reader: code-reviewer; pm; qa-c1
    summary: 'T-01 / SC-01/SC-02: historical receipts have incomplete provenance and
      streams; qualified, not an additional code blocker.'
    why: Code rates low, PM med. red.txt names source-equivalent 3769919f and reconstructed
      timeout sites; green.txt lacks immutable identity/duration and separate complete
      streams. QA's pinned run resolves current-green identity/duration, not historical
      completeness. Original records unchanged.
  - kind: substance
    scope: none
    severity: med
    reader: qa
    summary: 'Out-of-scope advisory: required unit coverage missing; operator scope
      decision only.'
    why: Bugfix touches_runtime_code applies to validate-digest.py; no tests/unit
      file covers change. Integration cannot substitute. Unit-file remedy exceeds
      T-01 ownership; matrix remains false without making this an additional scope
      blocker.
  - kind: substance
    scope: none
    severity: info
    reader: pm; qa-c1
    summary: 'Out-of-scope advisory: existing runner-launch failure remains fail-open.'
    why: "validate-digest.py:2480\u20132483 returns 0 with unverified-suite diagnostic.\
      \ Unchanged policy explicitly outside patch; operator decides whether to pursue."
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines/.harness/harness/features/BUG-2253-hook-hang-budget-and-gate-fail-lines/runs/2026-11-21-02-validate-validator/digest.md
```
