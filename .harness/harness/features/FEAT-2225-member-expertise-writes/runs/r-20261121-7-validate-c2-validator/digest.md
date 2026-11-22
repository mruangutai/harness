# Validate c2 — FAIL

Reviewed 594af2a8..238058677e6bbeafd5f05cefa9db2ffb76686418. F1 CLOSED; F3 CLOSED; F2 STILL OPEN (high, substance, T-01/T-04). One must-fix; no source edits; cycles_used 0.

## Consolidated ruling
F2: independently authorized provenance must replace arbitrary feature HEAD as an acceptable complete-file anchor. expertise-merge.py:1559-1571 accepts HEAD; validate-digest supplies no independent base. Deleting unrelated G-01, committing it, then legitimately applying P-01 permits the recorded chain to end at tampered HEAD. This scenario is source-derived, not executed. Code/security agree; PM grades SC-02 partial and SC-03 not_met. QA calls the original uncommitted case closed and the committed boundary advisory. I retain high: BRIEF SC-03 expressly requires unreceipted changes cannot pass close-run; later replay/merge refusal is containment, not compliance. Receipt Known limits does not approve narrowing that promise. Remedy T-01 core anchor, then T-04 member/lead live-yield and durable-close regressions; preserve legitimate committed receipts, supersession and replay.

## Reader blocks
- QA PASS: notes/review-harness-qa-c2.md. Unit 61 files/1132 PASS lines and integration 88 files/2909 PASS, both exit 0 under env -u HARNESS_AGENT_TYPE; task verifies green. Matrix true does not close F2's untested committed boundary. F1/F3 CLOSED with execution/mutation evidence. Unchained-batch guard mutant remains green (med substance coverage advisory).
- Code FAIL: notes/review-harness-code-reviewer-c2.md. F1/F3 CLOSED; F2 STILL OPEN/high. Static finding, no executed exploit claimed.
- Security FAIL: notes/review-harness-security-reviewer-c2.md. Same F2, deduplicated; downstream merge mitigation retained. Measured pin/fix code equivalence; only bookkeeping differs.
- UI PASS/scoped out: notes/review-harness-ui-reviewer-c2.md. Measured 85 paths, no visual surface; no a11y/theme success claimed.
- Goalcheck FAIL: notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c2.md. Operator pass, orchestrator partial, maintainer fail. SC-01/04/05/06 met; SC-02 partial; SC-03 not_met.

## Fail-first and assurance
Automated SC-01: red-first-T-04-host.md and red-first-fix-c1-host.md; SC-02: red-first-T-04-digest.md and red-first-fix-c1-{core,digest}.md; SC-03: red-first-T-04-{host,guard}.md and red-first-fix-c1-digest.md; SC-04: receipt-harness-backend-dev-T-01-c1.md; SC-05: red-first-t04-merge-gate.md. All paths under notes/. SC-06 pinned inspection. F3 real host representatives cover five capability classes, both tiers and all verbs; all-16 configuration checks are separate. QA executed isolated mutants; code/security exploit analysis remains reasoning-only. Committed tamper and post-replay boundaries lack tests. Raw QA/T-01 logs in /tmp remain volatile. Static typecheck unresolved; credentialled handoff-comprehension probe not claimed.

## Record and questions
QA-RETURN from c1 is resolved: stale OMP predating BUG-2171 JSON-text yield fix at 594af2a8/#2230; restarted session accepts structured returns. All five reader returns arrived structured; no host-refusal retry needed. No reader-to-reader escalation occurred. QA's N2 used unsupported kind `evidence`, recommending low advisory durability tracking; classification is left as an explicit nonblocking question rather than silently relabelled. This does not affect the single F2 gate.

```yaml
VERDICT: FAIL
DIGEST:
  headline: '238058677e6bbeafd5f05cefa9db2ffb76686418: F1/F3 CLOSED; F2 STILL OPEN/high
    despite green matrix.'
  open_questions:
  - id: QA-N2-CLASSIFICATION
    question: QA N2 uses unsupported kind `evidence` for low advisory historical evidence
      durability (volatile T-01 logs and receipt-only configuration reds). Classification
      unresolved; not silently promoted to substance.
    blocking: false
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Matrix green; committed F2 boundary called advisory.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: F1/F3 CLOSED; F2 STILL OPEN/high.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: F2 committed tamper passes close; merge contains later.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 85 paths measured; no visual surface.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator pass; orchestrator partial; maintainer fail.
    files_touched: []
  must_fix:
  - 'F2 / T-01 + T-04, high substance: anchor complete-file receipt verification to
    independently authorized pre-feature/main content, not arbitrary feature HEAD;
    add committed pre-application unrelated-tampering regressions for member/lead
    live yield and durable close, preserving legitimate committed receipts, supersession
    and replay.'
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed 594af2a8..238058677e6bbeafd5f05cefa9db2ffb76686418. QA/security measured
    code equivalence to 06ab8282; later differences bookkeeping.
  - 'F1 CLOSED: registered distill authority enforced before mutation and at dispatch,
    with execution/mutation evidence. F3 CLOSED: five real host representatives, both
    tiers/all verbs plus separate all-16 configuration assertions.'
  - 'F2 STILL OPEN: code/security high treatment prevails over QA advisory because
    SC-03 forbids unreceipted changes passing close. Known limits cannot narrow signed
    acceptance. Committed-tamper scenario is source-derived, not executed; downstream
    replay refusal is containment only.'
  - 'matrix_ok true: unit 61 files/1132 PASS lines; integration 88 files/2909 PASS;
    configured runners exit 0 under env -u HARNESS_AGENT_TYPE. Literal task verifies
    green.'
  - 'fail_first SC-01: notes/red-first-T-04-host.md and notes/red-first-fix-c1-host.md;
    SC-02: notes/red-first-T-04-digest.md and notes/red-first-fix-c1-{core,digest}.md;
    SC-03: notes/red-first-T-04-{host,guard}.md and notes/red-first-fix-c1-digest.md;
    SC-04: notes/receipt-harness-backend-dev-T-01-c1.md; SC-05: notes/red-first-t04-merge-gate.md.
    SC-06 inspection.'
  - 'QA-RETURN resolved: stale OMP predating BUG-2171 JSON-text fix at 594af2a8/#2230;
    restarted session accepts structured returns. All five reader returns accepted,
    no reader retry. Lead first yield refused for readers.reason shape; corrected
    to none in this return, not a second review.'
  - No reader-to-reader escalation. Deduplicated committed-tamper reports into F2;
    retained independent QA mutation-coverage advisory.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: QA c2; omp-hooks.test.ts:3376-3520 real host reps; test-member-expertise.py
      all-16 grants.
  - id: SC-02
    verdict: partial
    method: automated and inspection
    evidence: Uncommitted tamper refused; committed tamper accepted by HEAD anchor
      at expertise-merge.py:1559-1571.
  - id: SC-03
    verdict: not_met
    method: automated and inspection
    evidence: F1 repaired; F2 committed unreceipted-content close integrity open.
  - id: SC-04
    verdict: met
    method: automated
    evidence: QA c2 replay/collision/refusal/supersession integration and T-01 red
      receipt.
  - id: SC-05
    verdict: met
    method: automated
    evidence: QA c2 merge-gate integration/Main hook; red-first-t04-merge-gate.md.
  - id: SC-06
    verdict: met
    method: pinned inspection
    evidence: Code/PM notes inspect SPEC, skills, personas, decisions/index; kept
      decisions byte unchanged.
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - Committed tamper and post-replay close boundaries lack tests.
  - Removing unchained guard leaves suites green.
  - Raw T-01/QA logs volatile under /tmp; historical configuration red receipt-only.
  - Typecheck unresolved; credentialled handoff-comprehension probe not claimed.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer, security-reviewer, pm
    summary: 'F2 STILL OPEN / T-01 + T-04: HEAD self-authorizes complete-file provenance.'
    why: 'Delete unrelated G-01, commit, then legitimately apply P-01: chain reaches
      tampered HEAD accepted at expertise-merge.py:1559-1571; validate-digest supplies
      no independent base. Source-derived; later replay containment does not meet
      close requirement.'
  - kind: substance
    scope: none
    severity: med
    reader: qa
    summary: 'T-01/T-04 advisory: unchained active-batch guard lacks discriminating
      regression.'
    why: QA isolated mutant removing this guard stays green. Retained nonblocking
      coverage advisory.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-7-validate-c2-validator/digest.md
```
