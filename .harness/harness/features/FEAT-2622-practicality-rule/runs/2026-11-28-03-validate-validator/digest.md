# FEAT-2622 validate c2: FAIL. MF-1's same-id case is closed, but an unmatched open discounted row still relieves a plan-team reader FAIL

This run reviewed `3e979ae3..edcda5be` (review_sha `edcda5be091e5b1aa6dcc7021e410aae56de0222`), run `2026-11-28-03-validate-validator`, cycle 2. Five readers ran in one wave. `severity_max: high`.

This was the re-review after fix round 1. Under the operator's 2-round budget, the next fix round is the last.

## Closure of the c1 must-fix items

| c1 item | Status at edcda5be | Who measured it |
|---|---|---|
| MF-1 same-id stale row | **Closed.** The current finding must now be discounted too. | QA: the mutant that drops `_discounted_non_gating(item)` turns the stale-row case red. Security probed the predicate in memory. Code-reviewer ran mixed-discount cases sharing one id, in both orders. |
| MF-2 SC-02 ceiling | **Closed.** | QA and code-reviewer: removing `_severity_errors` turns the medmax case red. The acceptance cases now require zero errors. |
| MF-3 DEC-123 text | DEC-123 matches the code. DEC-260 D-06 does not (see item 3 below). | code-reviewer, pm |
| MF-4 SC-09 | **Closed.** | pm quoted each file; code-reviewer agrees. |
| MF-5 SC-11 | **Met in substance.** One letter gap remains (advisory). | pm: met. code-reviewer: low form. |
| VAL-OQ-01 SC-07 | **Met** under the operator's ruling. | pm, code-reviewer |

## Must-fix, in fix order

1. **[substance, high, T-01] An open discounted row with no current finding relieves on its stored rating alone.** Raised by code-reviewer, who executed it offline.
   - I confirmed it at the pin. `validate-digest.py` `_candidate_reason` sends every on-disk row through `_open_row_reason`. That function calls `_row_relieves(row)`, which checks the row only, so it never consults the current digest.
   - Scenario: a reader re-raises A at high and also raises a discounted B. A's earlier discounted row is kept. The lead's digest carries B but omits A. The result is zero errors and the FAIL is ranked PASS. At base, any open row denied relief.
   - Exposure: {trigger: plausible, vs_today: regression, control: harness}. This relaxes an enforcement gate, so it carries full weight.
   - Remedy: an open row relieves only when it is resolved, or when it is discounted at a non-gating severity **and** the current digest carries a finding with that PF id that is itself discounted at a non-gating severity. This is what DEC-260's D-06 bullet already says.
   - The remedy fails closed relative to SC-15's signed text. SC-15's relief case, where the current finding matches, still relieves. A reader that does not re-raise an old discounted finding falls back to worst-wins, which is the same as at base.
   - Acceptance (O-02, P-12): one discriminating case and one red mutant for each leg of the relief predicate:
     - the row's discount;
     - the current finding's exposure discount;
     - the current finding's severity;
     - a current finding with that id is present.
   - The exposure leg is QA's M10 (QA-F1). It is folded in here because this remedy rewrites the predicate. It is not a separate test demand.
2. **[substance, high, T-01] The plan-team carve-out cannot see a reader's independent must_fix.** Raised by security-reviewer, from static analysis.
   - Signed D-06 (plan.yaml) says: "Every other path keeps worst-wins: a FAIL carrying … a must_fix entry".
   - The carve-out ranks a reader FAIL as PASS using findings and rows only. The member entry carries no must_fix.
   - Exposure as rated by security: {plausible, regression, adversary}. This retracts in part my c1 dismissal of the same leg (O-04). At base, an open row denied relief regardless of the lead's honesty, so this is a regression.
   - Remedy, bounded to data the gate already holds, and measured first:
     - If a product-lead `team: plan` PASS with a non-empty team `must_fix` is already refused, record the existing witness and this leg is closed.
     - Otherwise, deny carve-out relief while the team digest's `must_fix` is non-empty. Add a case for it and a mutant that turns red.
   - The residual case, a lead that drops the member's must_fix from its own union, needs a member-shape contract change. That goes to VAL-OQ-03 and is not part of this must-fix.
3. **[form, med, T-05] DEC-123 and DEC-260 D-06 disagree about unmatched open rows.** Raised by code-reviewer.
   - DEC-123 (`DECISIONS.md` about L2501–2502) lets "every other on-disk row" relieve on its stored discount alone. DEC-260 D-06 (about L8879–8882) requires a current finding with that id.
   - After item 1, rewrite DEC-123 in place (DEC-205) to match D-06 and the fixed code. Regenerate the index.
4. **[form, low, T-03/T-04] The plan-side triage reason omits the reader's severity.** Raised by code-reviewer.
   - Signed D-03 requires "a one-line reason beside it naming the reader's severity".
   - `.omp/agents/harness-product-lead.md` (about L441–447) and the `teams/plan.yaml` fan-in comment (about L223–231) require a reason, but not the reader's original severity.
   - Remedy: one phrase in each.

## Advisory (not gating)

- **SC-11 letter gap** (code-reviewer, form low). `harness-verification-rules/SKILL.md` L172–175 states the trust-boundary limit the other way round ("neither a coverage gap nor a finding" where no input crosses a boundary). It does not say "belong only where…" in so many words.
  - pm graded SC-11 met. Exposure is contrived/no_worse/harness.
  - One clause if the T-04 file is touched anyway. It does not gate.
- **QA-F2: PF-id case sensitivity.** The mutant fails open, and still nothing witnesses it. The code is correct at the pin. This is the second cycle carrying it. QA rates it contrived/no_worse/harness, low, so it gets no test demand.
- **Fail-closed mutants still open from c1.** No test catches M4 (strip/lower), M5 (8-hex minimum), M6-* (the FAIL-relief legs) or M7 (severity_max case-fold). M11 is equivalent to the original. None of these is a defect.
- **QA-F3.** SC-15's signed text is looser than the code, which fails closed. No action. Amending it would mean changing signed text, and nothing is lost.
- **QA-OQ-02.** The fix-round receipt says removing `_severity_errors` turns **4** cases red. QA measured **3**. The closure holds either way. The main session should correct the count in `notes/receipt-main-session-build.md` (rule 15).
- **Environment.** Receipts are from this host's interpreter, not CI (G-03). `tsc` is absent, and the diff touches no TypeScript.

## Contradictions resolved

pm says DEC-123 matches the code "clause for clause". code-reviewer says DEC-123 and DEC-260 disagree. Both are true. DEC-123 matches the current code, and the current code is the defect in item 1. Item 3 follows from item 1.

## Assurance bound (P-09)

- Item 1 was executed by code-reviewer's offline validation and confirmed by me at source.
- Item 2 is static only. Security's probe was not refused; it covered the predicate, not the roll-up.
- QA's execution covers MF-1 and MF-2 by mutation.

## Members

| step | persona | verdict | note |
|---|---|---|---|
| qa | harness-qa | PASS | Unit 74/74 and integration 94/94 at the pin. Receipts are in `qa/`. fail_first is present for all 8 automated SCs. MF-1 and MF-2 are closed by mutation. M10 is unwitnessed. |
| code | harness-code-reviewer | FAIL | Item 1 (high) plus 3 form findings. Stage 2 was not opened. |
| security | harness-security-reviewer | FAIL | MF-1 closed. Item 2 (high), static. |
| ui | harness-ui-reviewer | PASS | Scoped out: 57 paths, none UI. |
| goalcheck | harness-pm | PASS | All perspectives pass. SC-01..SC-15 met. DEC-206 and DEC-123 dispositions met. |

Notes: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c2.md` and `notes/research-FEAT-2622-practicality-rule-goalcheck-validate-c2.md`.

```yaml
VERDICT: FAIL
artifact: .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-03-validate-validator/digest.md
DIGEST:
  headline: 'FAIL at edcda5be. All c1 must-fix items are closed: MF-1''s same-id stale-row
    case was closed by a red mutant. A new sibling defect remains in the plan-team
    carve-out (T-01, high): an open discounted row with no current finding still relieves
    a reader FAIL on its stored rating. Security also raises a high: the carve-out
    cannot see a reader''s independent must_fix. Two form fixes follow. The matrix
    is green, fail_first is 8/8 and every SC is met.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Matrix met at edcda5be: unit 74/74 and integration 94/94, receipts
      clean. MF-1 and MF-2 are closed by red mutants. M10 is a fail-open mutant on
      the MF-1 predicate that no test catches.'
    files_touched:
    - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-03-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-03-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2622-practicality-rule/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: The plan-team roll-up accepts PASS when a current gating finding is
      omitted and its older row was discounted.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: MF-1's stale-row match is closed, but open-row relief still masks a
      member's independent must_fix.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B out of scope: 57 changed paths, none UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All perspectives pass. SC-01..SC-15 met. DEC-206 and DEC-123 dispositions
      met.
    files_touched:
    - .harness/harness/features/FEAT-2622-practicality-rule/observations/harness-pm.md
  must_fix:
  - '1 [substance, high, T-01] validate-digest.py _open_row_reason/_row_relieves.
    An open panel row relieves only if it is resolved, or if it is discounted at a
    non-gating severity AND the current team digest carries a finding with that PF
    id that is itself discounted at a non-gating severity (DEC-260 D-06). The resolved-row
    path is unchanged. Acceptance: one discriminating case and one red mutant per
    relief-predicate leg: row discount, current exposure discount (QA M10), current
    severity, and current-finding presence. Include the omitted-current-high case
    from code-reviewer (raised by code-reviewer; confirmed at source).'
  - 2 [substance, high, T-01] Plan-team carve-out vs signed D-06 ('a FAIL carrying
    a must_fix entry keeps worst-wins'). First measure whether a product-lead team:plan
    PASS with a non-empty team must_fix is already refused. If it is, record the existing
    witness. Otherwise, deny carve-out relief while the team digest's must_fix is
    non-empty, and add a case and a red mutant (raised by security-reviewer). The
    residual case, a lead dropping the member's must_fix, goes to VAL-OQ-03.
  - '3 [form, med, T-05] DECISIONS.md: after item 1, rewrite DEC-123 in place (DEC-205)
    so that the ''every other on-disk row'' clause matches DEC-260 D-06 and the fixed
    code, which require a current discounted finding with the row''s id. Regenerate
    the index (raised by code-reviewer).'
  - '4 [form, low, T-03/T-04] .omp/agents/harness-product-lead.md (about L441-447)
    and the teams/plan.yaml fan-in comment (about L223-231): the triage reason must
    name the reader''s original severity, as signed D-03 requires (raised by code-reviewer).'
  files_touched:
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-03-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-03-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-03-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2622-practicality-rule/observations/harness-qa.md
  - .harness/harness/features/FEAT-2622-practicality-rule/observations/harness-pm.md
  branch: none
  open_questions:
  - id: VAL-OQ-03
    question: 'Must-fix 2 closes the case where an honest lead carries the reader''s
      must_fix into its own union. It cannot close the case where a lead drops the
      member''s must_fix from that union. The plan-team member entry has no must_fix
      field, so closing that case needs a member-shape contract change (common.json),
      which is approval-gated. Recommendation: accept that residual. The lead''s must_fix
      union is trusted the same way on base''s resolved-row path and in every other
      roll-up, and lead to roll-up is not a cross-trust boundary. Security rated it
      high with control adversary.'
    blocking: false
  - id: VAL-OQ-04
    question: 'Budget: under the operator''s 2-round/90-minute ruling, fix round 2
      is the last. Must-fix 1 and 2 both re-specify the DEC-123 relief predicate in
      T-01. If round 2 does not close them, the next step is the operator''s ruling,
      not another round.'
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Receipts are from this host's interpreter, not CI. test-typescript-typecheck.py
    cannot run because tsc is absent; the diff touches no TypeScript.
  - 'MF-1''s original same-id case was closed by three independent measurements: QA''s
    mutant, security''s in-memory predicate probe and code-reviewer''s mixed-discount
    cases. Must-fix 1 is a sibling path, _open_row_reason, that code-reviewer executed
    offline (zero errors when only discounted B is present) and that I confirmed at
    source.'
  - 'Must-fix 2 is a static finding; no reader executed it. It partly retracts my
    c1 dismissal of security''s independent-must_fix leg (O-04): at base, an open
    row denied relief regardless of the lead''s union, so this is a regression for
    the honest-lead case.'
  - 'QA-OQ-01 (M10) is folded into must-fix 1''s per-leg acceptance because that remedy
    rewrites the predicate. It is not a standalone test demand: QA rated it contrived/no_worse/harness.'
  - pm (DEC-123 matches the code) and code-reviewer (DEC-123 disagrees with DEC-260)
    are both right. The code DEC-123 matches is the must-fix 1 defect. Must-fix 3
    follows from must-fix 1.
  - 'Advisory, not gating: the SC-11 letter gap in harness-verification-rules L172-175
    (the trust-boundary limit is stated the other way round; pm graded SC-11 met).
    QA-F2 PF-id case sensitivity: a fail-open mutant, correct at the pin, contrived/no_worse,
    second cycle. Fail-closed mutants M4/M5/M6/M7 remain unwitnessed. QA-F3: SC-15''s
    text is looser than the code, which fails closed. QA-OQ-02: the fix-round receipt
    says 4 cases go red; QA measured 3. The main session should correct notes/receipt-main-session-build.md.'
  - Exposure is carried in each finding's why because the live yield schema is still
    the pre-feature schema (VAL-OQ-02, ruled).
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'test-practicality-rule.py:115; base archive: 5 schema cases FAIL (qa
      c2)'
  - id: SC-02
    verdict: met
    method: automated
    evidence: test-practicality-rule.py:142 incl. medmax-capped; the _severity_errors
      removal mutant is red (qa, code-reviewer)
  - id: SC-03
    verdict: met
    method: automated
    evidence: 'test-practicality-rule.py:167; base: 3 cases FAIL'
  - id: SC-04
    verdict: met
    method: automated
    evidence: 'test-practicality-rule.py:174; base: 6 cases FAIL'
  - id: SC-05
    verdict: met
    method: automated
    evidence: 'test-practicality-record-panel.py:129; base: 5 cases FAIL'
  - id: SC-06
    verdict: met
    method: inspection
    evidence: validate-digest.py _discounted_non_gating calls panel_findings.is_discounted/is_non_gating;
      no restated enums (pm, security)
  - id: SC-07
    verdict: met
    method: inspection
    evidence: 'Under the VAL-OQ-01 ruling: only runs/ added are this feature''s runs
      01/02; no other feature path; run_state.py unchanged (pm, code-reviewer)'
  - id: SC-08
    verdict: met
    method: inspection
    evidence: harness-code-review/SKILL.md:132-156; harness-security-reviewer.md:322-332
  - id: SC-09
    verdict: met
    method: inspection
    evidence: Clauses quoted per file at the pin by pm; code-reviewer concurs (validator-lead,
      product-lead, teams/validate.yaml, teams/plan.yaml)
  - id: SC-10
    verdict: met
    method: inspection
    evidence: Team reader prompts, panel-recording.md, templates/plan.yaml (pm, code-reviewer)
  - id: SC-11
    verdict: met
    method: inspection
    evidence: "tdd \xA7 Plausible inputs, verification-rules L172-175, harness-qa.md:262-264\
      \ (pm). The verification-rules letter gap is advisory."
  - id: SC-12
    verdict: met
    method: inspection
    evidence: DEC-260 carries every element; index cmp equal (pm). The DEC-123/DEC-260
      disagreement is must-fix 3.
  - id: SC-13
    verdict: met
    method: automated
    evidence: 'gen-agent-output --check ''agent output: ok''; red at 0daddfc4 (qa
      c1)'
  - id: SC-14
    verdict: met
    method: automated
    evidence: Integration 94/94 at the pin; base case_f59 rc=5 (notes/fail-first-T-02.md)
  - id: SC-15
    verdict: met
    method: automated
    evidence: 'test-practicality-rule.py:235 including stale-row-current-high-denied.
      The unmatched-row relief and the masked independent must_fix fall outside the
      SC''s cases: must-fix 1 and 2.'
  - id: DEC-206
    verdict: met
    method: inspection
    evidence: Rewritten in place, DECISIONS.md 6802-6806 (pm). The D-03 reader-severity
      omission in the plan-side guidance is must-fix 4.
  - id: DEC-123
    verdict: met
    method: inspection
    evidence: Matches the current code (pm). Rewrite needed after must-fix 1 (must-fix
      3).
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'DEC-123 carve-out: no case where an open discounted row has no current digest
    finding (must-fix 1)'
  - 'Relief-predicate current-exposure leg: mutant M10 stays green (folded into must-fix
    1)'
  - 'Plan-team carve-out with a non-empty team must_fix: no case (must-fix 2)'
  - 'PF-id case-insensitivity: no witness; fail-open mutant, advisory'
  - 'Fail-closed mutants M4 (strip/lower), M5 (8-hex minimum), M6-* (FAIL-relief legs),
    M7 (severity_max case-fold): no witness, advisory'
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-01: an open discounted panel row with no current digest finding relieves
      a plan-team reader FAIL on its stored rating, hiding an omitted current gating
      finding'
    why: '_candidate_reason passes every on-disk row to _open_row_reason, which tests
      _row_relieves(row) only. Executed offline: [discounted B] alone gives zero errors
      while A''s re-raised high is omitted. Base denied any open row. Exposure {trigger:
      plausible, vs_today: regression, control: harness}; a gate relaxation, so full
      weight.'
  - kind: substance
    scope: none
    severity: high
    reader: security-reviewer
    summary: 'T-01: DEC-123 open-row relief can turn a plan reader''s FAIL backed
      by an independent must_fix into a team PASS'
    why: 'The member entry carries no must_fix; the carve-out reads only findings
      and rows. Signed D-06 keeps worst-wins for a FAIL carrying a must_fix entry.
      Exposure {trigger: plausible, vs_today: regression, control: adversary} (security).
      Static. The honest-lead leg is must-fix 2; the residual where a lead drops the
      union is VAL-OQ-03.'
  - kind: form
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-05: DEC-123 and DEC-260 D-06 disagree on unmatched discounted open
      rows'
    why: 'DEC-123 lets other rows relieve on their stored discount; D-06 requires
      a current discounted finding with that id. Exposure {trigger: plausible, vs_today:
      regression, control: harness}.'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-03/T-04: plan-side triage reason need not name the reader''s original
      severity (D-03)'
    why: 'harness-product-lead.md:441-447 and teams/plan.yaml:223-231 require a reason
      but not the reader''s severity, which signed D-03 requires. Exposure {trigger:
      plausible, vs_today: regression, control: harness}.'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-04: verification-rules states the trust-boundary test limit conversely,
      not as ''belong only where'''
    why: 'Assessed and kept advisory: L172-175 already says that an absent test where
      no boundary is crossed is neither a gap nor a finding, and pm graded SC-11 met.
      Exposure {trigger: contrived, vs_today: no_worse, control: harness}.'
  - kind: substance
    scope: none
    severity: med
    reader: qa
    summary: 'T-01: mutant M10 (drop is_discounted on the current finding) leaves
      both suites green'
    why: 'The pin is correct; this is about regression resistance only. Folded into
      must-fix 1''s per-leg acceptance because that remedy rewrites the predicate.
      Exposure {trigger: contrived, vs_today: no_worse, control: harness}.'
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'T-01: PF-id case-sensitivity mutant fails open, still unwitnessed'
    why: 'Assessed and kept advisory; the pin refuses correctly. Exposure {trigger:
      contrived, vs_today: no_worse, control: harness}.'
  - kind: form
    scope: none
    severity: low
    reader: qa
    summary: BRIEF SC-15 text is looser than the code after MF-1
    why: 'Assessed and dismissed: the code fails closed relative to the signed text,
      and amending signed text buys nothing. Exposure {trigger: plausible, vs_today:
      no_worse, control: harness}.'
  readers: []
```
