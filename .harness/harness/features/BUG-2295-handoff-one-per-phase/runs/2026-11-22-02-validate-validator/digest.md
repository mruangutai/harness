# Validation — BUG-2295 — c1

FAIL at 253cdf2aedf8f1b40fe712aa4e9301cdb764bf34 (base dd04e52a898109fdbe09cf5fa14e1148161734d0): one T-01 substance defect remains. Main-session-direct owns remediation under DEC-174. No source changed; zero send-back cycles.

## Ranked must-fix

1. Align cycle-name detection with existing case-insensitive handoff routing and add mixed-case Write/Edit regression coverage. `handoff-Build-c1.md` reaches shape validation but evades the lowercase-only detector (`check-domain.py:1486,2296`). Raised by code-reviewer (high), security-reviewer (low), and PM (high); these are one defect, not three fixes. Retain high as the correctness/acceptance gate: SC-01 is partial. Security's low rating accurately describes absence of privilege escalation; it does not rebut the naming guarantee failure. Evidence is static inspection, not an executed mixed-case probe. No reader rating or kind is rewritten.

## Assurance and dispositions

- QA: matrix_ok true; unit rc=0 (63 files, 131 tests), integration rc=0 (91 files). Dedicated integration: 96 ok, zero FAIL. `../../notes/review-harness-qa-c1.md`.
- Fail-first SC-01: pinned Write assertions over baseline production fail for build-c1, validate-c12, plan-c305. SC-02: corresponding Edit assertions fail. Combined natural RED rc=1, 90 ok, six assertion FAILs; pin GREEN rc=0, 96 ok. Existing canonical/cap/section/Done when cases retained. Unchanged-file controls are baseline-green, not refusal proof.
- QA's request for confirmation about absent dedicated unit coverage is assessed and dismissed as nonblocking: registered unit suite ran; integration supplies the contract evidence explicitly assigned by the brief. No extra operator decision or unit-test requirement is created. Limited phase samples and nondiscriminating controls bound assurance, not additional must-fixes. Mixed-case omission is already included above.
- Code: SC-03 and SC-04 pass pinned inspection; ship predicate/exemption byte-identical, historical notes untouched. `../../notes/review-harness-code-reviewer-c1.md`.
- Security: scoped enforcement review, same defect with low security impact; no independent must-fix. `../../notes/review-harness-security-reviewer-c1.md`.
- UI: actual census of 13 changed files finds no UI; valid scoped-out PASS. `../../notes/review-harness-ui-reviewer-c1.md`.
- PM: operator PARTIAL (SC-01 partial, SC-04 met); code maintainer PASS (SC-02/03 met). All DEC-174/225/252/254 keep dispositions preserved; no decision landing failure. `../../notes/research-BUG-2295-handoff-one-per-phase-goalcheck-validate-c1.md`.
- PM's pre-existing DEC-252 commentary discrepancy is explicitly outside this patch, not a new finding or remediation mandate; any decision-text correction would require upgrade plan and operator ownership approval. No open scope question is necessary for T-01 remediation.

Open questions: none. One consolidated must-fix; severity_max high. Green sampled tests do not clear the untested branch identified independently by code and security.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'Pin 253cdf2aedf8f1b40fe712aa4e9301cdb764bf34 fails SC-01: mixed-case
    cycle names bypass refusal; T-01 main-session-direct remediation required.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Matrix green; six baseline refusal failures reproduced, then 96 passing
      assertions.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Mixed-case cycle filenames bypass Write/Edit refusal.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Same bypass rated low security impact.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 13-file diff has no UI surface.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator partial; code maintainer pass; decision keep dispositions preserved.
    files_touched: []
  must_fix:
  - 'T-01 (owner main-session-direct, DEC-174; raised by code-reviewer, security-reviewer
    and PM): align cycle-name detector with existing case-insensitive routing and
    add mixed-case Write/Edit refusal regressions.'
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed pin 253cdf2aedf8f1b40fe712aa4e9301cdb764bf34 against base dd04e52a898109fdbe09cf5fa14e1148161734d0.
    Five reader note paths are recorded in run state and digest.
  - 'fail_first SC-01: baseline production with pinned tests fails build-c1, validate-c12
    and plan-c305 Write assertions. SC-02: matching Edit assertions fail. Combined
    RED rc=1, 90 ok, six FAIL; pin GREEN rc=0, 96 ok.'
  - Unit rc=0, 63 files, 131 tests; integration rc=0, 91 files; per-file verdicts
    green. Captured negative-fixture FAIL strings are not suite failures.
  - 'QA dedicated-unit-coverage confirmation request assessed and dismissed: integration
    supplies assigned contract evidence; registered unit suite ran. Null unrelated
    runners are not findings.'
  - 'One deduplicated defect: code and PM high acceptance impact, security low security
    impact. Preserve each reader rating; retain high consolidated severity because
    low privilege impact does not clear SC-01. Mixed-case evidence is inspection,
    not executed probe.'
  - Operator partial; code maintainer pass. DEC-174/225/252/254 keep dispositions
    preserved. Pre-existing DEC-252 commentary discrepancy is outside T-01; any requested
    correction requires upgrade plan.
  - 'SC-03/04 pinned inspections pass: comment corrected, executable predicate/exemption
    unchanged, specified shipped history untouched.'
  - No source edits, tests authored, commits, shipping, pinning or close-run actions.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated and inspection
    evidence: QA reproduced baseline failures for lowercase Write cases; code/security
      identified mixed-case bypass at pinned check-domain.py:1486,2296. See notes/review-harness-qa-c1.md
      and notes/review-harness-code-reviewer-c1.md.
  - id: SC-02
    verdict: met
    method: automated
    evidence: QA reproduced baseline Edit failures then 96 green assertions at pin;
      canonical and existing shape checks retained. notes/review-harness-qa-c1.md.
  - id: SC-03
    verdict: met
    method: inspection
    evidence: "Pinned gh-sync.py:2586\u20132590 distinguishes prerequisite and shipped\
      \ exemption. notes/review-harness-code-reviewer-c1.md."
  - id: SC-04
    verdict: met
    method: inspection
    evidence: Base-to-pin gh-sync.py changes comments only; no specified shipped-history
      paths changed. notes/review-harness-code-reviewer-c1.md.
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - Mixed-case filename refusal lacks Write/Edit regressions; included in T-01 must-fix.
  - Unit suite has no dedicated filename-rule test; integration is binding evidence.
  - Unchanged-file controls are baseline-green, not refusal proof.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; security-reviewer (low security rating); pm
    summary: 'T-01 owner main-session-direct (DEC-174): mixed-case cycle names bypass
      refusal.'
    why: Pinned check-domain.py:2296 is case-sensitive while RE_HANDOFF:1486 is case-insensitive
      and normalization preserves case. Valid notes/handoff-Build-c1.md enters Write/Edit
      enforcement but receives no filename refusal, violating SC-01. Align case policies
      and add regression coverage.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/runs/2026-11-22-02-validate-validator/digest.md
```
