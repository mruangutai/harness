# Validate c3 — FAIL

Pin **6d9e6053a6367c78f1e5848a6801e7ca09d82dd1**: **F1 CLOSED; F2 OPEN; F3 CLOSED; severity_max high**. One must-fix, high/substance, T-01 + T-04: close verification still trusts mutable local default refs as independent provenance. Final rework round exhausted; return to operator, not another automatic fix round.

## Assessment

Code, security and goalcheck identify the same F2; consolidate once. Security executed the decisive counterexample using pinned core: remain on feat/probe, commit unreceipted G-01 deletion, apply legitimate P-01, move only origin/main to the deletion commit: refusal 15 becomes verified:true. Missing remote refs plus moved local main also accepts. No remote-main permission or branch switch is needed. Live/durable propagation is source-derived, not separately executed. See notes/review-harness-security-reviewer-c3.md and code-reviewer-c3.md.

QA PASS is a matrix/evidence judgment, not closure of this broader trust boundary. Its self-anchor advisory assumes default-ref equality means main/default checkout; security falsified that premise on a feature branch. Preserve QA's low rating in its note; adopt security/code high F2 because the demonstrated local-ref bypass violates SC-02/03 without protected-main access. Later replay containment does not satisfy close integrity. Explicit trusted nonancestor --base merge-base behavior is acceptable and preserves supersession; arbitrary explicit HEAD has no current untrusted caller and is advisory, not a second blocker.

QA measured unit 61 files/1136 PASS lines and integration 88 files/2922 PASS lines under env -u HARNESS_AGENT_TYPE, with fail-first evidence for SC-01..05. N2 mutation is caught by exactly one discriminating integration check. Green tests cover the original F2 case, not mutable-ref authority. Raw red logs remain volatile; durable notes retain outcomes (advisory). UI measured 94 changed paths and scoped out correctly. QA's 46-path diff census differs from other readers' 94-path full census; no assurance rests on that count.

Goalcheck regraded SC-02 partial and SC-03 not_met. It explicitly applied the requested current-cycle reassessment as a deviation from its once-per-phase SC-09 rule, not silent compliance. Other SCs remain met. This is recorded process qualification, not another shipped-code defect or new scope decision.

## Disposition

- **Must fix F2 (high, substance, T-01/T-04):** independently authorize close-verification provenance despite moved local default refs; preserve legitimate supersession and missing/unrelated-base refusals.
- QA N3 (low substance T-01): assessed advisory; explicit base is trusted at current callers.
- QA N4 (low substance T-01/T-04): overlaps F2; feature-branch executed counterexample establishes blocking severity, while QA's original rating remains unchanged.
- QA evidence durability (low): advisory, no new blocker.

Reader artifacts: notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c3.md; notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c3.md. No source changes; no further reader passes.

```yaml
VERDICT: FAIL
DIGEST:
  headline: '6d9e6053a6367c78f1e5848a6801e7ca09d82dd1: F1 CLOSED, F2 OPEN, F3 CLOSED;
    severity_max high; operator disposition required.'
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
    headline: Matrix green; fail-first recorded; N2 mutant caught.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'F2 high: mutable default refs self-authorize tampering.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: Executed feature-branch default-ref bypass; F2 high.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured no visual UI surface.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: SC-02 partial; SC-03 not_met.
    files_touched: []
  must_fix:
  - 'F2 / high / substance / T-01 + T-04: independently authorize close-verification
    provenance despite mutable local default refs. Committed unreceipted feature content
    followed by a legitimate receipt must not verify after local default-ref movement.
    Preserve legitimate supersession and missing/unrelated-authority refusals.'
  branch: none
  escalations: []
  adequacy_notes:
  - 'Final rework round exhausted: return FAIL to operator, not another automatic
    fix round.'
  - Deduplicated code/security/goalcheck F2. Security executed pinned-core refusal-to-success
    bypass by moving origin/main while remaining on feat/probe. Live/durable propagation
    is source-derived.
  - QA low N4 retains its original rating; consolidated high follows security's executed
    feature-branch counterexample, falsifying the main-checkout-only premise. Later
    replay containment does not satisfy close integrity.
  - 'QA matrix PASS: unit 61 files/1136 PASS lines; integration 88 files/2922 PASS
    lines under env -u HARNESS_AGENT_TYPE; fail-first recorded for SC-01..05. N2 mutant
    caught by one discriminating integration check.'
  - Trusted explicit nonancestor --base merge-base preserves supersession and is acceptable.
    Explicit HEAD-base advisory is nonblocking at current trusted callers.
  - 'QA red-log durability concern remains advisory: raw logs volatile, durable notes
    retain outcomes.'
  - Goalcheck records requested current-cycle SC-02/03 reassessment as deviation from
    once-per-phase SC-09 rule, not silent compliance.
  - F1/F3 source closure confirmed; QA carrying suites green. UI measured scope and
    declined correctly.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: QA c3 matrix/fail-first; host representatives and all-16 checks.
  - id: SC-02
    verdict: partial
    method: automated
    evidence: Original committed-tamper tests pass; mutable-default-ref F2 remains.
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: Security c3 pinned-core probe changes refusal 15 to verified:true by
      local ref movement.
  - id: SC-04
    verdict: met
    method: automated
    evidence: QA integration green; trusted diverged-base supersession retained.
  - id: SC-05
    verdict: met
    method: automated
    evidence: QA integration and merge-gate red-first evidence.
  - id: SC-06
    verdict: met
    method: inspection
    evidence: Goalcheck carries unchanged c2 pinned documentation inspection.
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No regression binds mutable default-ref authority on a feature branch.
  - Explicit HEAD-base and default-ref self-anchor boundary tests absent.
  - Raw red logs volatile; durable notes retain outcomes.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer, security-reviewer, goalcheck
    summary: 'F2 / T-01 + T-04: mutable default refs self-authorize unreceipted feature
      content.'
    why: 'Executed pinned-core scenario on feat/probe: commit G-01 deletion, apply
      legitimate P-01, repoint origin/main to deletion commit; refusal 15 becomes
      verified:true. No remote-main permission or branch switch required; digest supplies
      no independent anchor.'
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'N3 / T-01 advisory: explicit feature-HEAD base self-anchors.'
    why: 'Assessed nonblocking: current callers supply trusted fetched main or no
      explicit base.'
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'N4 / T-01 + T-04: QA self-anchor advisory overlaps F2.'
    why: Original QA rating preserved; security's feature-branch executed counterexample
      establishes blocking F2, not a second must-fix.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-8-validate-c3-validator/digest.md
```
