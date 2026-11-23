# FEAT-2398 validation — FAIL

**Pin `685e861a667efd13e3c9720dffe9dbb847d4207b` is not ship-ready: reproduced empty-kind CLI bypass, red integration floor, incomplete promised omission coverage and a false QA instruction.** All remediation belongs to existing **T-01, main-session-direct (DEC-174)**; no signed decision or scope change is requested.

## Ranked, deduplicated must-fix

1. **High · substance · code + QA:** establish pinned QA policy before the empty-kind early return (`validate-digest.py:1795–1800`). QA reproduced a schema-valid PASS with `kinds: []` and no trusted feature directory: the candidate CLI returns `digest ok`, exit 0. Add a real CLI regression; preserve legitimate all-excluded behavior. Evidence: `notes/review-harness-code-reviewer-c0.md`, `notes/review-harness-qa-c1.md`.
2. **Med · substance · QA:** migrate T-01's `_kp_harness_repo` / `_kp_product_repos` config producers through the shared fixture writer (`test-validate-digest.py:7032–7175`). The required integration runner is red: fixture audit reports eight findings, versus zero at baseline. Preserve deliberately malformed-config cases through the existing fixture convention. Evidence: `notes/review-harness-qa-c0.md` and original runner manifests below.
3. **Med · substance · PM + QA:** complete SC-01/04 omission regressions for both unresolved and active/null kinds: ESCALATE and independently varied schema-valid `matrix_ok` cases. Current defaults couple matrix state to verdict. The implementation appears unconditional; correct-by-inspection is not the signed automated proof. Retain fail-first and both-repair assertions. Evidence: `notes/research-FEAT-2398-qa-test-kind-status-goalcheck-validate-c1.md` (GC-01).
4. **Low · substance · PM:** correct the operational claim that INV-49 governs which kinds config may declare (`harness-verification-rules/SKILL.md:38`); it governs BRIEF gap disclosure, never a waiver. No INV-49 implementation change. This is factual contract drift, not a style nit; PM's canonical classification is retained (GC-02).

Fix policy/fixture prerequisites before collecting fresh focused and final matrix evidence; update the instruction in the same direct cutover. Do not route source edits through a validator-hosted dev fix.

## Evidence and reconciliation

- QA: **FAIL**, pinned unit **65/65, exit 0**; integration **95/95 completed, exit 1**. Receipts: `qa/manifest-unit.json`, `qa/manifest-integration.json`. Integration also lacked `tsc`; its isolated post-install diagnostic passed, but the original receipt remains red. Prepare dependencies before the next authorized final run; that environmental failure is not another product defect.
- Focused T-01 verify: **52/52 pass at pin**. Independent baseline reproduction: **39/52 fail**, 13 controls pass. This supports SC-01–04's existing cases, not the newly exposed missing cases.
- Goal-check: **FAIL**. SC-02 met; SC-01/03/04/05 partial. D-01/D-02 partial; D-03 and DEC-256 amendment met. No additional decision-record amendment is claimed necessary.
- Code: **FAIL**, initially reasoning-only bypass now independently executed by QA. Security: **PASS**, static trust-boundary audit; its clean hook-path analysis does not discharge the distinct CLI bypass. UI: **PASS, scoped out** after a 102-file pinned-range census with zero visual surfaces; no visual/a11y pass claimed. Inherited BUG-2399 merge content is not attributed to T-01.
- **Assessed, nonblocking:** no extra matrix-only SC-03 pair is required. PM identifies existing P1 omission discrimination of both tables; that sufficiency is inspection inference, not executed mutation evidence. QA's coarser SC-05 inspection is supplemented by PM's pinned prose review.
- Two evidence/classification sendbacks resolved cross-panel gaps. PM's c0 evidence-unavailable qualification is superseded by c1; QA's c1 integration-satisfied transcription is not accepted over its red immutable receipt. No suites were rerun in the sendback.

## Boundaries and next owner

Only QA executed candidate behavior; other reviewers were static or census-only. The installed pre-change control-plane hook is not candidate evidence. Known product-document absence remains disclosed; no new guidance or requirements were invented. No unrelated INV-25/INV-29 check-state finding was encountered. Required paths stay within this feature; source remediation is Main's direct lane. **Open questions: none.**

```yaml
VERDICT: FAIL
DIGEST:
  headline: '685e861a fails validation: reproduced empty-kind CLI bypass, red integration
    floor, omission-coverage gaps and incorrect INV-49 instruction.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 2
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: CLI bypass reproduced; unit 65/65 green, integration 95/95 completed
      red; focused 52/52 green.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: High-severity missing-pin bypass through empty-kind CLI return; mechanical
      grade pass.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Static trust-boundary audit found no exploitable security defect.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 102 changed files, zero visual UI surfaces; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: SC-02 met; remaining criteria partial; omission evidence and instruction
      require T-01 correction.
    files_touched: []
  must_fix:
  - "T-01, main-session-direct: establish pinned QA policy before validate-digest.py:1795\u2013\
    1800 empty-kind return; add fail-first real-CLI regression for kinds=[] without\
    \ trusted feature/pin."
  - 'T-01, main-session-direct: migrate _kp_harness_repo/_kp_product_repos config
    producers through shared fixture support; restore fixture audit from eight findings
    to zero without weakening malformed-config controls.'
  - 'T-01, main-session-direct: complete unresolved and active/null omission tests
    under ESCALATE and independent schema-valid matrix_ok values, retaining fail-first
    evidence and both-repair diagnostics.'
  - 'T-01, main-session-direct: correct verification-rules SKILL:38 to describe INV-49
    as verification-gap disclosure, not config-kind declaration governance; preserve
    no-waiver contract.'
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed 685e861a667efd13e3c9720dffe9dbb847d4207b against baseline 9eb07b4f3cd235c234a10edddbfe5542c1e85fba.
    Inherited BUG-2399 merge content is not attributed to T-01.
  - QA independently reproduced 39/52 baseline failures and 52/52 candidate focused
    passes. These do not cover the exposed CLI branch or missing omission combinations.
  - 'Immutable receipts bind the pin: unit exit 0, integration exit 1. Genuine fixture
    regression is distinct from environmental missing tsc; an isolated post-install
    diagnostic passed, but no suite rerun or green receipt is claimed.'
  - Security's static hook-path assurance does not clear the distinct CLI bypass independently
    executed by QA. Only QA executed candidate behavior; installed pre-change hook
    behavior is not candidate proof.
  - 'SC-03 matrix-only pair assessed as nonblocking: PM identifies existing P1 discrimination
    of both tables. Sufficiency is inspection inference, not mutation evidence.'
  - PM supplied canonical substance classifications for GC-01/02. The low instruction
    defect is required factual SC-05 correction, not style.
  - QA's contradictory c1 integration-satisfied transcription was returned and corrected;
    red manifests remained unchanged. PM's earlier unavailable-QA qualification was
    superseded.
  - All remedies are existing signed T-01 work under DEC-174, owned by Main's direct
    lane. Fix policy/fixture prerequisites before fresh focused and matrix evidence;
    prepare dependencies first and commit receipts with the closed run record.
  - Known product-document absence remains disclosed. No unrelated INV-25/INV-29 finding
    was encountered. Initial lead return's scope/reason shape was refused and corrected;
    no behavioral rerun.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated
    evidence: QA c0 confirms existing baseline-red/candidate-green cases; QA/PM c1
      identify absent ESCALATE and independent matrix_ok omission controls.
  - id: SC-02
    verdict: met
    method: automated
    evidence: QA c0 and goalcheck c1 confirm active/excluded/locally_run controls
      and disclosure noninterference at pin.
  - id: SC-03
    verdict: partial
    method: automated plus inspection
    evidence: 'Policy-selection cases pass; QA c1 reproduces candidate CLI accepting
      empty-kind PASS without trusted feature/pin: digest ok, exit 0.'
  - id: SC-04
    verdict: partial
    method: automated
    evidence: Existing three-gate controls pass; omission loop excludes ESCALATE and
      does not independently vary matrix_ok (GC-01).
  - id: SC-05
    verdict: partial
    method: inspection
    evidence: Pinned docs substantially agree; QA SKILL:38 incorrectly assigns config-declaration
      governance to disclosure-only INV-49 (GC-02).
  - id: D-01
    verdict: partial
    method: automated plus inspection
    evidence: Unified policy path exists, but reproduced CLI bypass violates missing-pin
      refusal; remedy T-01.
  - id: D-02
    verdict: partial
    method: inspection plus automated
    evidence: Three gates appear implemented; GC-01 leaves promised universal omission
      proof incomplete.
  - id: D-03
    verdict: met
    method: inspection
    evidence: "PM pinned DEC-187:5339\u20135344 records Kaya BLOCKED consequence,\
      \ both repairs and no waiver."
  - id: DEC-256
    verdict: met
    method: inspection
    evidence: "PM pinned DECISIONS.md:8528\u20138530,8540\u20138563 confirms actual\
      \ clause replacement with QA-pin exception and preserved non-QA contract; owner\
      \ T-01."
  needs_approval: false
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - Missing empty-kind/no-trusted-pin real-CLI regression (SC-03).
  - Missing ESCALATE omission and independent schema-valid matrix_ok controls for
    unresolved and active/null kinds (SC-01/04).
  - Required integration floor remains red; focused green does not replace its receipt.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; independently reproduced by qa
    summary: 'T-01: empty-kind CLI PASS bypasses mandatory pinned policy establishment.'
    why: "validate-digest.py:1795\u20131800 returns before _qa_policy when kinds and\
      \ started tasks are empty. QA CLI probe accepts with digest ok/exit 0 despite\
      \ absent trusted feature/pin; D-01/SC-03 require refusal."
  - kind: substance
    scope: none
    severity: med
    reader: qa; validator severity assessment
    summary: 'T-01: new config fixture producers break required integration audit.'
    why: Fixture audit reports eight findings in _kp_* producers versus zero at baseline;
      integration runner_exit 1. Plan explicitly requires shared fixture support.
  - kind: substance
    scope: none
    severity: med
    reader: pm; corroborated by qa
    summary: 'T-01: all-verdict, matrix-independent omission behavior lacks promised
      automated proof.'
    why: Both status omission loops exclude ESCALATE; matrix_ok remains coupled to
      verdict. Existing SC-01/04 require those distinctions.
  - kind: substance
    scope: none
    severity: low
    reader: pm
    summary: 'T-01: QA instruction incorrectly describes INV-49 authority.'
    why: SKILL:38 assigns config-kind governance to INV-49; pinned implementation
      governs BRIEF gap disclosure. Correct the factual operational instruction, not
      INV-49 code.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/runs/validate-validator/digest.md
```
