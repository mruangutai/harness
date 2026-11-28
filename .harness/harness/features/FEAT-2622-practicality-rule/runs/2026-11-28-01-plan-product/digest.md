# FEAT-2622 plan team — close-out (run 2026-11-28-01-plan-product)

**BLUF: plan is `pending` and signable.** 15 SCs, 6 plan decisions, 5 tasks, all `main-session-direct`. All 7 panel findings resolved in plan.yaml; `plan-merge.py check` exit 0; goal-check re-grade PASS on all three perspectives (operator, reader, code maintainer). One send-back spent (apply, for a red-first predicate that could not pass on a correct build).

## Per member
| step | persona | verdict | headline |
|---|---|---|---|
| draft | harness-pm | PASS | BRIEF + plan drafted; check exit 0 |
| scope | harness-code-reviewer | FAIL | 2 high substance (discounted finding could still force FAIL via severity_max/DEC-123 roll-up; T-02 test unsatisfiable), 1 med, 1 low form; all resolved at apply |
| should-not-exist | fable-advisor | ran | 3 findings (low substance eng-lead `unrated`; info task-trim INV-32 cases; info form is_non_gating); mission proportionate |
| design | harness-ui-reviewer | PASS | self-scoped out: no user-facing surface |
| apply | harness-pm | PASS | 7/7 resolved; added D-06 (DEC-123 amend); send-back fixed T-01 item 4 predicate (measured at base 3e979ae) |
| goalcheck | harness-pm | PASS (re-grade) | first grade FAIL on Q-01 (T-01 red-first unsatisfiable: base schema already refuses `exposure` as unexpected key); re-grade PASS after fix |

## Decisions (constraint 7)
DEC-206 amend (bounded triage narrows severity transcription); DEC-123 amend (successor D-06: discounted-only reader FAIL is non-gating; independently justified FAIL/ESCALATE/BLOCKED keep worst-wins); DEC-31, DEC-228, DEC-230, DEC-229, DEC-237, DEC-174 keep. T-05 owns DECISIONS.md.

## Lead assessment
- Practicality rule applied to this panel: scope's two highs were self-rated plausible/routine and real; fable's two info findings were self-described contrived/no_worse and got one-sentence/trim remedies, no new tests.
- O-10: apply remediated two high findings and the team runs no re-read. D-06 (DEC-123 amendment), D-03 (product-lead triage authority, an extension past the grilling) and the T-01/T-02 verify literals rewritten at apply are unread by any reader. Put to the operator as one signature question.
- Prototype gate: no end-user interaction (design reader self-scoped out) → no prototype required. Overridable.
- Mission: no `scope: mission` finding; fable explicitly found the plan lane proportionate. No downgrade recommended.
- Plan-team carve-out (DEC-123): scope's FAIL ranks as PASS because every finding attributed to `scope` is `resolved` in plan.yaml.

Fan-in: panel-c1.md. Send-back criteria written pre-return: criteria.md.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'FEAT-2622 plan is pending and signable: 15 SCs, 6 plan decisions and
    5 main-session-direct tasks; all 7 panel findings are resolved and the goal-check
    re-grade passes. The operator must rule at signature on D-06 (amends DEC-123),
    D-03 and the verify text rewritten at apply, none of which a reader saw.'
  open_questions:
  - id: OQ-SIG-01
    question: 'Signature question (O-10). Apply fixed two high scope findings, and
      no reader re-read the result. Unread by any reader: (a) D-06, which amends DEC-123
      so that a code, security or ui reviewer FAIL whose every finding is discounted
      does not gate, and which refuses a gating severity_max that only discounted
      findings support. (b) D-03, which gives the product lead triage authority, going
      beyond the grilling. (c) The T-01 and T-02 verify literals, which were rewritten
      at apply (T-01 item 4 predicate, T-02 exposure rows and --cycle). Recommendation:
      sign as written. Treat these three as read-at-signature items.'
    blocking: true
  - id: OQ-01
    question: 'must_fix is a list of free strings. D-02 ties a must_fix entry to a
      discounted finding by containment of its summary or PF id, so a reworded entry
      gets past the check. Recommendation: accept containment now, and move to a structured
      must_fix only if a reworded contrived finding is actually seen getting through.'
    blocking: false
  - id: OQ-02
    question: 'Forward-only (D-04) uses no era marker. The residual risk: a lead run
      that is open when T-01 lands will be refused at close-run. Recommendation: land
      T-01 only when no lead run is open in any in-flight feature.'
    blocking: false
  - id: OQ-03
    question: The severity ceiling for a discounted finding is med, which is DEC-31's
      non-gating band, rather than low. Confirm med.
    blocking: false
  - id: OQ-04
    question: 'Advisory. The T-01, T-02 and T-03 red-first verifies extract git archives
      from a python heredoc. bash-write-guard has blocked python writes to /tmp from
      a pm shell before. These verifies run main-session-direct, so this is not expected
      to bite, but if it does it is a harness-guard question. Separately, SC-01 covers
      six personas: should QA run the five schema cases for each persona, or cite
      the shared common.json $ref (the probe found identical behaviour)?'
    blocking: false
  files_touched:
  - .harness/harness/features/FEAT-2622-practicality-rule/BRIEF.md
  - .harness/harness/features/FEAT-2622-practicality-rule/plan.yaml
  - .harness/harness/features/FEAT-2622-practicality-rule/notes/research-practicality-rule.md
  - .harness/harness/features/FEAT-2622-practicality-rule/notes/review-harness-code-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2622-practicality-rule/notes/review-harness-ui-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2622-practicality-rule/notes/research-FEAT-2622-practicality-rule-goalcheck-plan.md
  - .harness/harness/features/FEAT-2622-practicality-rule/observations/harness-pm.md
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-01-plan-product/state.yaml
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-01-plan-product/panel-c1.md
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-01-plan-product/criteria.md
  expertise_update: []
  team: plan
  steps_run: 6
  cycles_used: 1
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 'Drafted the BRIEF and plan: 14 SCs, 5 decisions, 5 main-session-direct
      tasks; plan-merge check exits 0'
    files_touched:
    - .harness/harness/features/FEAT-2622-practicality-rule/BRIEF.md
    - .harness/harness/features/FEAT-2622-practicality-rule/plan.yaml
    - .harness/harness/features/FEAT-2622-practicality-rule/notes/research-practicality-rule.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Keep the plan lane, but fix two things before signature: the verdict
      roll-up and T-02''s gate, which fails even on a correct build'
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: 'The plan is basically right and the mission is proportionate: 1 low
      eng-lead unrated gap and 2 info findings, self-rated contrived and no worse
      than today'
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode A out of scope: no planned task changes a user-facing UI'
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: All 7 panel findings resolved and D-06 added (DEC-123 amend); a send-back
      fixed T-01's red-first predicate, measured at base 3e979ae
    files_touched:
    - .harness/harness/features/FEAT-2622-practicality-rule/plan.yaml
    - .harness/harness/features/FEAT-2622-practicality-rule/BRIEF.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 'Re-grade passes all three perspectives. The first grade failed on Q-01:
      T-01''s red-first check could not pass on a correct build. The fix closed Q-01
      and changed no grade that was already met'
    files_touched:
    - .harness/harness/features/FEAT-2622-practicality-rule/notes/research-FEAT-2622-practicality-rule-goalcheck-plan.md
  must_fix: []
  branch: feat/FEAT-2622-practicality-rule
  escalations: []
  adequacy_notes:
  - 'Plan-team carve-out (DEC-123): the scope reader''s FAIL ranks as PASS because
    every finding attributed to scope is resolved in plan.yaml.'
  - 'Constraint 7: DEC-206 and DEC-123 are amended (D-06 is DEC-123''s successor).
    DEC-31, DEC-228, DEC-230, DEC-229, DEC-237 and DEC-174 are kept. T-05 owns DECISIONS.md.'
  - 'Prototype gate: the design reader self-scoped out because the plan touches no
    user-facing surface, so no prototype is required. Overridable in either direction.'
  - 'No scope: mission finding. fable-advisor found the plan lane proportionate, so
    no downgrade is recommended.'
  - 'Practicality rule applied to this panel: scope''s two highs were self-rated plausible
    or routine and real. fable-advisor''s two info findings were self-rated contrived
    and no worse than today, so they got a one-sentence fix or a trim and no new tests.'
  - One send-back spent, on apply, for goal-check Q-01. The goalcheck note keeps the
    first FAIL grade and appends the re-grade.
  sc_status:
  - id: operator
    verdict: met
    method: inspection
    evidence: SC-02/03/15 (T-01), SC-05/07 (T-02), SC-09 (T-03, T-04); goalcheck note
      re-grade
  - id: reader
    verdict: met
    method: inspection
    evidence: SC-01/04 (T-01), SC-08/11 (T-03, T-04), SC-10 (T-04); SC-01 fail-first
      measured satisfiable at base 3e979ae3
  - id: code maintainer
    verdict: met
    method: inspection
    evidence: SC-06 (T-01, T-02), SC-12 (T-05), SC-13 (T-03), SC-14 (T-01..T-03)
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-01/T-03/T-04 leave a path for a discounted finding to force FAIL after
      triage
    why: 'Reader-stated exposure: plausible, no_worse, harness. Resolved at apply
      by D-06 (DEC-123 amend).'
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-02 requires its record-panel test to fail even when the writer is correct
    why: 'Reader-stated exposure: routine, regression, harness. Resolved at apply:
      exposure added to the expected rows and --cycle passed.'
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: The verification blocks omit or substitute required fail-first witnesses
    why: 'Reader-stated exposure: routine, regression, harness. Resolved at apply.'
  - kind: form
    scope: none
    severity: low
    reader: scope
    summary: Add a keep disposition for DEC-229
    why: Resolved at apply.
  - kind: substance
    scope: none
    severity: low
    reader: should-not-exist
    summary: The eng-lead persona silently inherits the `unrated` loophole D-01's
      own rationale forbids
    why: 'Reader-stated: trigger plausible, consequence no worse than today, and eng-lead
      behaviour is left untested. Resolved at apply.'
  - kind: proportionality
    scope: task
    severity: info
    reader: should-not-exist
    summary: T-02's two new INV-32 cases test a row record-panel already refuses to
      write
    why: 'Reader-stated: contrived and no worse than today. Trimmed at apply.'
  - kind: form
    scope: none
    severity: info
    reader: should-not-exist
    summary: is_non_gating creates a second non-gating set beside the one gates_signature
      uses
    why: 'Reader-stated: contrived and no worse than today. Fixed with one sentence
      at apply.'
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: ran
    persona: fable-advisor
    reason: none
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2622-practicality-rule/.harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-01-plan-product/digest.md
```
