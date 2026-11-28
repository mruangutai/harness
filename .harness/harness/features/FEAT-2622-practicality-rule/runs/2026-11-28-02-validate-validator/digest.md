# FEAT-2622 validate c1 — FAIL: the DEC-123 open-row relief can hide a current gating finding

Reviewed `3e979ae3..d131c231` (review_sha `d131c231d3e4f278019a8acdffd4706e6f622cee`). Run `2026-11-28-02-validate-validator`, cycle 1, five readers in one wave. `severity_max: high`.

Note on exposure: the live yield schema for leads and reviewers is the pre-feature control-plane copy. Its `findings` items are closed and have no `exposure` key. Each reader's exposure is therefore given in that finding's `why` and in the reader's note. That is expected until the feature merges.

## Must-fix, in fix order

1. **[substance, high, T-01] The plan-team carve-out relieves a current non-discounted gating finding through a stale discounted open row.** Raised by code-reviewer and security-reviewer (duplicates). Verified at source:
   - `validate-digest.py` `_digest_finding_reason` (≈L2290–2304) matches the digest finding to its row by PF id, which is built from reader and summary alone. It then tests only the **row** with `_row_relieves`. The digest finding's own severity and exposure are never read.
   - `plan_merge/panel.py` `_recorded_panel` (≈L519–535) keeps the base row whenever the id is already present ("the base's value … wins").
   - Scenario: a reader re-raises the same summary in a later cycle at `high` with `plausible/regression`. The cycle-1 row (`contrived/no_worse`, `med`, open) is kept, and the reader's FAIL is re-ranked PASS. At base, the open row denied relief.
   - Exposure: plausible / regression / harness (code-reviewer). Security rated the control as adversary. Neither rating discounts the finding, so `high` stands.
   - Remedy: an open discounted row relieves only when the current digest finding is itself discounted at a non-gating severity. The resolved-row path is unchanged.
   - Test: a mutant that drops the digest-side check turns red.
   - Security also named the reader's independent must_fix. That part is dismissed as a separate defect: the team-digest member shape carries no must_fix, and base's resolved-row path ignored it the same way, so it is no worse than today.
2. **[substance, med, T-01] SC-02's per-finding ceiling has no discriminating witness, and the acceptance cases ignore unrelated errors.** Raised by code-reviewer (med) and qa (coverage gap and QA-OQ-01).
   - Every gating-severity refusal case also sets `severity_max: high`. QA removed `_severity_errors` and the suite stayed green. Its probe (a discounted `high` finding, `severity_max: med`, PASS) is refused at the pin and accepted by the mutant. That is a fail-open mutant on a gate meant to refuse.
   - Remedy: add that `severity_max: med` case, and make the acceptance cases in `test-practicality-rule.py` assert that no error was raised. Same file and same round as item 1.
   - Exposure: plausible / regression / harness.
3. **[form, med, T-05] The DEC-123 text contradicts the code and SC-15.** Raised by code-reviewer.
   - `DECISIONS.md` ≈L2497–2502 still requires the row that matches each attributed finding to be `disposition: resolved`. It allows discounted open rows only among the "other" rows.
   - The code (`_row_relieves` in `_digest_finding_reason`) and SC-15 relieve a matching discounted row.
   - Remedy: rewrite the clause in place (DEC-205) to state the rule as fixed by item 1. Do this after item 1.
4. **[form, low, T-03/T-04] SC-09 is partial.**
   - goalcheck (pm) found that `.omp/agents/harness-product-lead.md` and the `teams/plan.yaml` lead comments lack the signed-text clause: a remedy touching signed text reaches the operator only when its finding survives triage.
   - code-reviewer also found that the `teams/validate.yaml` lead bullet (L156–159, read by me) lacks "never raises a severity and never revises kind". pm graded that file as carrying every clause, and the source shows code-reviewer is right.
   - Remedy: one sentence in each of the three places.
5. **[form, low, T-04] SC-11 holds only if the files are read together.** Raised by code-reviewer; pm graded it met.
   - Read at the pin: `harness-tdd-enforcement/SKILL.md` L52–56 states plausible inputs and the trust boundary. It does not state that a missing test of that kind is neither a coverage gap nor a finding.
   - `harness-verification-rules/SKILL.md` L172–174 states the gap/finding rule. It does not state that tests target plausible inputs.
   - SC-11 requires each file to state all three. Remedy: one clause in each, which is cheap (G-10).

## Routed up, not must_fix

- **SC-07 literal wording** (code-reviewer, low form, scope change; ui-reviewer raised the same point by IRC).
  - The range adds five records of this feature's own plan run under `runs/2026-11-28-01-plan-product/`. DEC-257 requires them to be committed.
  - No other feature's path and no historical record is touched. `run_state.py` is unchanged. pm graded SC-07 met under that reading.
  - The only remedy amends signed criterion text, so it goes to the operator (G-06).
  - Exposure: routine / no_worse / harness.

## Advisory (not gating)

- These QA mutants all fail closed: removing the SC-15 FAIL-relief acceptance legs (the `must_fix`, `code_grade`, `severity_max` and all-vs-any checks, and the reviewer-only scope), dropping strip/lower from the non-gating compare, and lowering the PF-id bound to 1 hex. Add witnesses if cheap; they are not required.
- PF-id case sensitivity: a case-sensitive mutant fails **open**. The pin is correct today. A one-line witness is recommended alongside item 2 (P-08), but it does not gate.
- The record-panel writer has no case for a malformed exposure. Downstream `shape_faults` (case7c) still refuses it, so the writer check is defence in depth.
- pm advisories carried as recorded, not re-derived:
  - A-1: a residual unqualified sentence in DEC-206.
  - A-2: `_severity_max_errors` compares the literal `high`/`critical`. That is the DEC-31 gate band, not the non-gating set, so it does not breach SC-06.
- Security threat-model rows marked unmitigated with no finding attached:
  - Reader self-rating is the signed reader-rated design, so it is not a code defect.
  - Lead triage reasons are required by guidance only and no gate checks them. Logged here, not escalated.
- Environment gap: `test-typescript-typecheck.py` cannot run because `tsc` is absent. The diff touches no TypeScript. QA's integration receipt is from this host, not CI (G-03).

## Members

| step | persona | verdict | note |
|---|---|---|---|
| qa | harness-qa | PASS | unit 74/74 and integration 94/94 green at the pin; receipts in `qa/`; fail_first present for all 8 automated SCs; 7 coverage gaps |
| code | harness-code-reviewer | FAIL | 1 high substance (item 1), 1 med substance, 4 form |
| security | harness-security-reviewer | FAIL | 1 high substance, a duplicate of item 1; static analysis only |
| ui | harness-ui-reviewer | PASS | scoped out on a census of 45 paths, none UI |
| goalcheck | harness-pm | FAIL | SC-09 partial; every other SC met; DEC-206 and DEC-123 dispositions met |

Assurance bound: the stale-row defect was found by reasoning in both reviewers and confirmed by me at source. No reader executed it. QA's execution evidence (its mutants) covers SC-02 and SC-15, not the carve-out disagreement.

Notes: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c1.md`, `notes/research-FEAT-2622-practicality-rule-goalcheck-validate-c1.md`.

```yaml
VERDICT: FAIL
artifact: .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-02-validate-validator/digest.md
DIGEST:
  headline: 'FAIL at d131c231: in plan-team roll-ups, the DEC-123 open-row relief
    can hide a current non-discounted high finding behind a stale discounted row with
    the same PF id (T-01, high, confirmed at source). QA''s matrix is green with fail-first
    evidence for all 8 automated SCs, but SC-02''s per-finding ceiling has no test
    that catches its removal. SC-09 is partial, and three form fixes are needed in
    the docs and decision record.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: unit 74/74 and integration 94/94 green at the pin; receipts recorded;
      fail_first for all 8 automated SCs; 7 coverage gaps, the SC-02 ceiling leg unwitnessed
    files_touched:
    - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-02-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-02-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2622-practicality-rule/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: T-01 plan-team carve-out can hide a current gating FAIL behind an older
      discounted row with the same PF id
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: DEC-123 open-row relief can mask a reader FAIL backed by a non-discounted
      finding
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'scoped out: 45 changed paths, none UI'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: SC-09 partial; reader and code-maintainer perspectives pass, operator
      partial; DEC-206 and DEC-123 dispositions met
    files_touched:
    - .harness/harness/features/FEAT-2622-practicality-rule/observations/harness-pm.md
  must_fix:
  - '1 [substance, high, T-01] validate-digest.py _digest_finding_reason/_row_relieves:
    an open discounted panel row relieves a plan-team reader FAIL only when the current
    digest finding with that PF id is itself discounted at a non-gating severity.
    Keep the resolved-row path. Add a test where a high, plausible/regression digest
    finding matching an open contrived/no_worse med row is DENIED relief, and show
    that dropping the digest-side check turns it red (raised by code-reviewer and
    security-reviewer).'
  - '2 [substance, med, T-01] tests/unit/test-practicality-rule.py: add a discounted-high-finding
    case with severity_max med so that removing _severity_errors turns it red. Make
    the acceptance cases assert that no error was raised at all (raised by code-reviewer
    and qa QA-OQ-01).'
  - '3 [form, med, T-05] DECISIONS.md DEC-123 (about L2497-2502): rewrite in place
    (DEC-205) so the matching row may be resolved, or open and discounted at a non-gating
    severity with the digest finding agreeing. Write it to match the code as fixed
    by item 1. Do this after item 1 (raised by code-reviewer).'
  - '4 [form, low, T-03/T-04] SC-09: add the signed-text routing clause to .omp/agents/harness-product-lead.md
    and to the teams/plan.yaml lead comments. Add ''never raises a severity, never
    revises kind'' to the teams/validate.yaml lead bullet (raised by pm goalcheck
    and code-reviewer).'
  - '5 [form, low, T-04] SC-11: harness-tdd-enforcement/SKILL.md gains ''absence elsewhere
    is neither a coverage gap nor a finding''. harness-verification-rules/SKILL.md
    gains ''tests target the code''s plausible inputs'' (raised by code-reviewer).'
  files_touched:
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-02-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-02-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-02-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2622-practicality-rule/observations/harness-qa.md
  - .harness/harness/features/FEAT-2622-practicality-rule/observations/harness-pm.md
  branch: none
  open_questions:
  - id: VAL-OQ-01
    question: 'SC-07 says the range lists no runs/ record. The range adds five records
      of this feature''s own plan run (runs/2026-11-28-01-plan-product/), which DEC-257
      requires to be committed. No other feature''s path and no historical record
      is touched, and run_state.py is unchanged. Only amending the signed criterion
      text can fix this. Recommendation: the operator rules that SC-07 means ''no
      other feature''s path, no rewritten historical runs/ record'', and the feature''s
      own new run records are lawful (raised by code-reviewer and ui-reviewer; pm
      graded it met under that reading).'
    blocking: false
  - id: VAL-OQ-02
    question: 'Harness defect, expected before merge: the live yield schema (control-plane
      common.json, pre-feature) closes findings with no exposure key, and its scope
      field accepts only none. The pinned schema requires exposure. Readers and this
      lead therefore carry exposure only in each finding''s why and in the notes.
      Confirm that the merge of this feature closes the gap and no separate fix is
      needed.'
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - QA's receipts are from this host's interpreter, not CI. test-typescript-typecheck.py
    cannot run (tsc absent); the diff touches no TypeScript.
  - The high finding was found by reasoning in two reviewers and confirmed at source
    by the lead (validate-digest.py about L2290-2304; plan_merge/panel.py _recorded_panel,
    where the base row wins by id). No reader executed it.
  - 'The independent-must_fix leg of security''s finding is dismissed as a separate
    defect: the team-digest member shape carries no must_fix, and base''s resolved-row
    path ignored it the same way (no_worse).'
  - pm and code-reviewer disagreed on whether teams/validate.yaml carries every SC-09
    clause. Read at the pin (L156-159), it lacks no-raise and no-kind, so code-reviewer
    is right.
  - 'Advisory, not must_fix: the fail-closed mutants on the SC-15 acceptance legs,
    the strip/lower compare and the PF-id 8-hex bound. The PF-id case-sensitivity
    mutant fails open, so a witness is recommended alongside must_fix 2. The record-panel
    writer has no malformed-exposure case, but shape_faults covers it downstream.
    pm advisories A-1 (a residual DEC-206 sentence) and A-2 (literal high/critical
    in _severity_max_errors, which is the DEC-31 band, not a breach of SC-06).'
  - Exposure is transcribed in each finding's why because the live yield schema is
    closed (VAL-OQ-02). The last finding (SC-07) is a scope change routed to the operator.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'test-practicality-rule.py:110; fail-first: 5 schema cases red at base
      (qa)'
  - id: SC-02
    verdict: met
    method: automated
    evidence: behaviour correct at the pin (qa probe P1 refused), but the per-finding
      leg has no test that catches its removal; see must_fix 2
  - id: SC-03
    verdict: met
    method: automated
    evidence: test-practicality-rule.py:156; red 3/3 at base
  - id: SC-04
    verdict: met
    method: automated
    evidence: test-practicality-rule.py:163; red 6/6 at base
  - id: SC-05
    verdict: met
    method: automated
    evidence: test-practicality-record-panel.py:129; base plan-merge 5 cases red
  - id: SC-06
    verdict: met
    method: inspection
    evidence: panel_findings.py is_discounted/is_non_gating/practicality_fault called
      by validate-digest.py and plan_merge/panel.py (pm)
  - id: SC-07
    verdict: met
    method: inspection
    evidence: under pm's reading; the literal 'no runs/ record' is contested by the
      feature's own plan-run records; see VAL-OQ-01
  - id: SC-08
    verdict: met
    method: inspection
    evidence: "harness-code-review/SKILL.md \xA7 Exposure; harness-security-reviewer.md\
      \ practicality paragraph (pm)"
  - id: SC-09
    verdict: partial
    method: inspection
    evidence: signed-text clause absent from product-lead body and plan.yaml lead
      comments; no-raise/no-kind absent from validate.yaml L156-159; must_fix 4
  - id: SC-10
    verdict: met
    method: inspection
    evidence: team reader prompts, panel-recording.md and templates/plan.yaml (pm)
  - id: SC-11
    verdict: partial
    method: inspection
    evidence: tdd L52-56 lacks the gap/finding clause; verification-rules L172-174
      lacks the plausible-input target; must_fix 5
  - id: SC-12
    verdict: met
    method: inspection
    evidence: DEC-260 present; DEC-206 and DEC-123 rewritten; index equal (pm executed).
      The DEC-123 wording defect is must_fix 3
  - id: SC-13
    verdict: met
    method: automated
    evidence: 'gen-agent-output --check ''agent output: ok''; red at T-01 0daddfc4
      (qa)'
  - id: SC-14
    verdict: met
    method: automated
    evidence: 7 integration files green; base case_f59 rc=5 against the pin (qa)
  - id: SC-15
    verdict: met
    method: automated
    evidence: test-practicality-rule.py:184 and the carve-out relieved/denied pair;
      the stale-row fail-open beyond the SC's cases is must_fix 1
  - id: DEC-206
    verdict: met
    method: inspection
    evidence: rewritten in place per DEC-205 (pm)
  - id: DEC-123
    verdict: met
    method: inspection
    evidence: carve-out names the discounted open row (pm); the matching-row wording
      is must_fix 3
  needs_approval: none
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'SC-02: removing validate-digest._severity_errors leaves the suite green (every
    refusal case also has severity_max high)'
  - 'SC-15 FAIL-relief acceptance legs (must_fix, code_grade, severity_max, all-vs-any,
    reviewer-only): mutants stay green (fail-closed)'
  - 'Non-gating severity trim/case-insensitive compare: no witness (fail-closed mutant)'
  - 'must_fix PF-id 8-hex lower bound: no witness (fail-closed mutant)'
  - 'must_fix PF-id case-insensitivity: no witness (fail-open mutant)'
  - 'record-panel writer malformed-exposure refusal: no writer-level case (covered
    downstream by shape_faults case7c)'
  - 'DEC-123 carve-out: no case where the digest finding disagrees with the open discounted
    row (must_fix 1)'
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer, security-reviewer
    summary: 'T-01: a stale open discounted panel row relieves a plan-team reader
      FAIL whose current finding is non-discounted and gating'
    why: '_digest_finding_reason matches by PF id (reader+summary) and tests only
      the row; record-panel keeps the base row by id, so a later-cycle high plausible
      re-raise is re-ranked PASS; base denied open rows. Exposure: {trigger: plausible,
      vs_today: regression, control: harness} (code-reviewer); security rated control:
      adversary; not discounted either way.'
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: verification can pass while acceptance fails or the per-finding
      cap is removed'
    why: 'Severity_max refusal satisfies both cap cases, and the acceptance cases
      ignore unrelated errors; qa confirmed by mutant. Exposure: {trigger: plausible,
      vs_today: regression, control: harness}.'
  - kind: form
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-05: DEC-123 still requires the matching disk row to be resolved'
    why: 'DECISIONS.md about L2497-2502 contradicts the code and SC-15 relief for
      a matching discounted open row. Exposure: {trigger: plausible, vs_today: regression,
      control: harness}.'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer, pm
    summary: 'T-03/T-04: lead instructions omit required SC-09 triage clauses'
    why: 'Product-lead body and plan.yaml lack the signed-text routing clause; validate.yaml
      lacks no-raise/no-kind. Exposure: {trigger: plausible, vs_today: regression,
      control: harness}.'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-04: TDD and verification guidance each lack part of the SC-11 rule'
    why: 'Each file omits one of the three required statements. Exposure: {trigger:
      plausible, vs_today: regression, control: harness}.'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer, ui-reviewer
    summary: 'SCOPE CHANGE: own-feature plan-run records appear under SC-07''s literal
      no-runs/ check'
    why: 'Remedy amends signed criterion text; routed as VAL-OQ-01, not must_fix.
      Exposure: {trigger: routine, vs_today: no_worse, control: harness}.'
  readers: []
```
