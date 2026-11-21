# BUG-2171 validation — FAIL (one-use smoke recipe)

Pin `d3792019e74ff266c2414708124512544d1fc9f6` satisfies the four product criteria on code, saved live-runtime evidence, and current automated gates, but the approved literal verification recipe is not re-runnable: its hard-coded `2026-11-08-02-smoke-product` run id is already closed, so the fresh smoke refused before dispatch and QA returned FAIL.

## Assessment

- QA freshly passed the required unit matrix (59 files; Bun 140/0), integration gate (31/31), and genuine assertion-red/base to green/fix probes for SC-02 and SC-04. `matrix_ok` is true and fail-first evidence is present.
- QA's smoke failure and PM/code's SC-03 PASS are not contradictory claims about shipped behavior. PM and code inspected the saved credentialled OMP 19.1.0 child/lead yields, strict injected schemas, preserved human prefix, and hook-owned canonical append; QA measured that the literal command cannot produce a *fresh* instance after consuming its fixed run id.
- The durable remedy is to make the signed smoke recipe allocate an unused run id (and use that id consistently), then execute it and revalidate. T-01 is main-session-direct under DEC-174; no implementation squad owns this correction.
- Code's low form note about `notes/receipts/live-smoke.txt:3` is retained but dismissed as nonblocking: current pinned inspection supersedes the historical narrator's schema-attribution interpretation without rewriting historical evidence.
- Security found no exploitable regression at the parsed-yield/authorized-append boundary. UI measured all 22 changed paths and correctly scoped out.

## Ordered findings

1. **Form / medium / task / QA + validator lead:** the approved T-01 verify block hard-codes a one-use smoke run id. The ledger correctly refuses reuse, making the literal verification non-repeatable. Fix the recipe first; only then rerun the fresh smoke.
2. **Form / low / none / code reviewer:** historical smoke narration calls hook-injected schema fields caller-supplied. Assessed and dismissed because successful refusal-before-injection plus saved-session inspection resolves provenance; shipped behavior and SC-03 evidence are unaffected.

## Open questions

None. The required correction and owner are known.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Pin d3792019 meets all four SCs, but QA proved the signed smoke recipe
    cannot be revalidated because it reuses a closed run id.
  open_questions:
  - id: QA-SMOKE-RUN-ID
    question: QA recommends re-signing T-01 with a fresh or parameterized smoke run
      id before revalidation; the current approved literal command cannot rerun. Must
      the main session apply that record correction and obtain approval?
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
    headline: Unit and integration gates plus fail-first probes pass, but the literal
      fresh smoke refused the consumed run id.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Pinned patch satisfies all SCs and fails closed; one low historical-record
      note is nonblocking.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Strict validation, held-run enforcement and authorized append remain
      secure.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 22-path diff has no user-facing UI and is correctly scoped
      out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Operator and code-maintainer perspectives pass at the pinned SHA.
    files_touched: []
  must_fix:
  - Main session must replace the one-use hard-coded smoke run id in T-01's signed
    verify recipe with an unused or parameterized id, use it consistently, obtain
    required re-approval, and rerun validation.
  branch: none
  escalations:
  - id: QA-SMOKE-RUN-ID
    raised_by: harness-qa
    question: The literal T-01 smoke cannot start because 2026-11-08-02-smoke-product
      is already closed; how should the approved recipe allocate a fresh run id?
    domain: main-session-direct signed verification record
    routed_to: main session
    resolution: Unresolved; QA recommends correcting the signed recipe before another
      validation.
    decided_by: harness-validator-lead
    recorded_as: .harness/harness/features/BUG-2171-task-structured/runs/2026-11-21-04-validate-validator/digest.md
  adequacy_notes:
  - Reviewed immutable range b7af829c0207522b43f978b5275a2ebdc96b3210..d3792019e74ff266c2414708124512544d1fc9f6.
  - 'QA''s matrix is green: unit covers 59 files with Bun 140/0, integration is 31/31,
    and genuine assertion failures at base turn green at the fix for SC-02 and SC-04.'
  - 'PM/code''s SC-03 PASS and QA''s failure address different claims: saved live
    evidence proves shipped behavior, while QA proved the literal recipe cannot produce
    a second fresh run after consuming its fixed id.'
  - QA did not classify the recipe failure by kind or severity, so the canonical digest
    carries it as an open question and must-fix rather than inventing a heavier finding.
    This supersedes the preliminary prose artifact's lead-assigned form/medium label.
  - 'The code reviewer''s low form note about historical smoke narration is assessed-and-dismissed:
    current pinned inspection resolves provenance without rewriting historical evidence.'
  - Typecheck remains unresolved with cmd:null as disclosed in the approved BRIEF;
    no static TypeScript assurance is claimed.
  - T-01 is main-session-direct under DEC-174; no implementation squad is eligible
    to remediate the signed verification record.
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: Code and PM verified task.structured true and the exact bounded hook
      delta at d3792019.
  - id: SC-02
    verdict: met
    method: automated
    evidence: Fresh integration 31/31 plus assertion-red base and green fixed gate
      evidence, including integer 1.
  - id: SC-03
    verdict: met on saved live evidence; fresh recipe rerun failed
    method: inspection and attempted live rerun
    evidence: Saved OMP 19.1.0 child/lead yields, injected strict schemas, preserved
      prefix and hook append pass inspection; fresh run-start refused the already
      closed hard-coded id.
  - id: SC-04
    verdict: met
    method: automated
    evidence: Fresh Bun handler suite 140/0 and targeted historical-hook assertion
      red/fixed-hook green evidence cover string object handling and held-run behavior.
  needs_approval: true
  severity_max: low
  matrix_ok: true
  coverage_gaps:
  - The literal T-01 live-smoke command is non-repeatable because its fixed run id
    has already been consumed; no fresh c1 child/lead yield or append was produced.
  - Typecheck remains unresolved with cmd:null; behavior is covered by Bun rather
    than static TypeScript checking.
  findings:
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: Historical live-smoke narration misclassifies hook-injected schemas as
      caller-supplied.
    why: Successful refusal-before-injection and saved-session inspection supersede
      that interpretation; historical bytes remain unchanged and the issue does not
      affect shipped behavior or SC-03 proof.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/runs/2026-11-21-04-validate-validator/digest.md
```
