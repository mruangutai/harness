# FEAT-2423 plan run — 2026-11-28-02-plan-product

**BLUF.** Every c1 operator ruling (`notes/answers-2026-11-28-plan-c1.md`) has been applied, and the re-panel ruled under LEAD-01 has run. BRIEF.md (SC-01..SC-11) and plan.yaml (T-01..T-07) are `pending` and signable. `plan-merge.py check --root /Users/molchairuangutai/GitHub/harness` exits 0 with 80 anchors and no OVERLAP, so Q-05 is closed by ruling and the sparse cone is untouched. The goal-check passes all four perspectives. One new signature question (LEAD-02) remains: apply changed literal verify text in response to c2 findings, and no reader has re-read that text.

## What changed
- Revision (draft c2): T-04 deletes org.html, and SC-10 drops it. The two stray-file test cases are gone. SC-05 is now removal-as-proof (inspection). SC-06 is now a live-behaviour case, `run_budget_denials_route_to_live_records`, that never names the file. New SC-11: dropping Expertise G-01 (validator-lead) and G-05 (code-reviewer) is a ship condition, delivered by this feature's distillation and traced by no task, by ruling. The kaya conditional is dropped. The BRIEF's open questions are replaced by recorded rulings. Tasks changed: T-01, T-02, T-04, T-07.
- Scope re-read (c2): the three c1 high remedies now discriminate. The reader probed each red and green: T-01 rows[-8], the rename witness and the INV grep; T-05's Amended-by ban scoped to DEC-129/150; and the T-06/T-07 sweep. It raised 2 new high and 2 med substance findings: the prior-* fixture exemption contradicts Q-06; "latest non-PENDING" is not "accepted"; the SC-06 witness was weak; and the T-01 range grep was wrong.
- Apply (c2): all 4 findings are resolved. T-02 now removes the name from both prior-* fixtures. pm confirmed that no test hashes them and no decision freezes them. A single accepted-digest definition, keyed on `_is_refused`, is carried verbatim in D-01, SC-02/SC-10, T-03, T-04 and T-05. The SC-06 case asserts each budget's own diagnostic. T-01 parses range endpoints. record-panel, set-panel and check each exit 0. Tasks changed: T-01, T-02, T-03, T-04, T-05, T-07 and D-01.

## Lead assessment
- Readers: scope ran. should-not-exist was skipped by the host: the rulings narrow scope and add no build task, and the dispatch authorised that reader only on a material scope change. design self-scoped out: org.html, its only surface, is deleted.
- DEC-123 carve-out: the scope reader's FAIL ranks as PASS, because all 4 of its c2 findings are resolved in plan.yaml.
- LEAD-02 (expertise O-10): the c2 remedies rewrote literal verify text that no reader has seen. That text is T-01's range parser, T-02's fixture greps and SC-06 assertions, and the normalised-definition checks in T-03/T-04/T-05. A third reader cycle would repeat the pattern that LEAD-01 was meant to end, so I put it to the signer instead.
- Prototype gate: no prototype is needed. No end-user interaction exists, and the only rendered surface is now deleted. This can be overridden in either direction.
- Cycles: 0 send-backs this run. Every member met the criteria in `criteria.md`, which were written before each dispatch.
- No `scope: mission` finding was raised, and no severity was lowered.

## Correction — design reader
The design reader ran; it was not skipped. My first return listed it as skipped, and the digest contract refused that return, because only fable-advisor may be recorded as skipped. I then dispatched harness-ui-reviewer after apply. It self-scoped out with PASS and in_scope false (`notes/review-harness-ui-reviewer-plan-c2.md`). `panel-c2.md` still records design as skipped, because that was the roster at fan-in time. The reader found nothing, so apply's inputs are unchanged. Main's `record-panel --digest` on this file carries the corrected roster.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2423-retire-state-md/.harness/harness/features/FEAT-2423-retire-state-md/runs/2026-11-28-02-plan-product/digest.md
DIGEST:
  headline: FEAT-2423 BRIEF (SC-01..SC-11) and 7-task plan.yaml are pending and signable.
    Every c1 ruling is applied. The re-panel confirmed the c1 high remedies and found
    4 new issues, all resolved. check against the main checkout exits 0 (80 anchors),
    and the goal-check passes all 4 perspectives. One new signature question (LEAD-02)
    remains.
  team: plan
  steps_run: 5
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 'All c1 rulings applied: org.html deleted in T-04, stray-file tests
      and exemptions removed, SC-11 expertise ship condition added, kaya conditional
      dropped, rulings recorded. T-01/T-02/T-04/T-07 changed. check on the main root
      exits 0.'
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/BRIEF.md
    - .harness/harness/features/FEAT-2423-retire-state-md/plan.yaml
    - .harness/harness/features/FEAT-2423-retire-state-md/notes/research-c2-rulings.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'c1 high remedies discriminate red and green. New: prior-* fixture exemption
      contradicts Q-06, non-PENDING is not accepted digest (2 high); weak SC-06 witness
      and T-01 range grep (2 med). All resolved at apply (DEC-123 carve-out).'
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/notes/review-harness-code-reviewer-plan-c2.md
  - step: should-not-exist
    persona: fable-advisor
    status: skipped
    reason: 'Host skip: the c1 rulings narrow scope (org.html deleted rather than
      rewritten, two test cases removed) and add no build task. The dispatch authorised
      this reader only on a material scope change.'
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Self-scoped out: no UI remains in scope. T-04 deletes org.html and
      no live link to it exists.'
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/notes/review-harness-ui-reviewer-plan-c2.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: '4/4 c2 findings resolved: T-02 cleans both prior-* fixtures, one accepted-digest
      definition is used verbatim in D-01/SC-02/SC-10/T-03/T-04/T-05, the SC-06 case
      asserts each budget''s own diagnostic, and T-01 parses range endpoints. record-panel,
      set-panel and check each exit 0.'
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/BRIEF.md
    - .harness/harness/features/FEAT-2423-retire-state-md/plan.yaml
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Plan delivers the operator's stated intent as narrowed by the c1 rulings.
      Operator, orchestrator, code maintainer and reader all pass, and every remaining
      narrowing is ruled.
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/notes/research-FEAT-2423-retire-state-md-goalcheck-plan.md
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2423-retire-state-md/BRIEF.md
  - .harness/harness/features/FEAT-2423-retire-state-md/plan.yaml
  - .harness/harness/features/FEAT-2423-retire-state-md/notes/research-c2-rulings.md
  - .harness/harness/features/FEAT-2423-retire-state-md/notes/review-harness-code-reviewer-plan-c2.md
  - .harness/harness/features/FEAT-2423-retire-state-md/notes/review-harness-ui-reviewer-plan-c2.md
  - .harness/harness/features/FEAT-2423-retire-state-md/notes/research-FEAT-2423-retire-state-md-goalcheck-plan.md
  - .harness/harness/features/FEAT-2423-retire-state-md/observations/harness-pm.md
  - .harness/harness/features/FEAT-2423-retire-state-md/runs/2026-11-28-02-plan-product/state.yaml
  - .harness/harness/features/FEAT-2423-retire-state-md/runs/2026-11-28-02-plan-product/criteria.md
  - .harness/harness/features/FEAT-2423-retire-state-md/runs/2026-11-28-02-plan-product/panel-c2.md
  branch: none
  open_questions:
  - id: LEAD-02
    question: 'Operator at signature: apply resolved the 4 c2 scope findings by rewriting
      literal verify text, and no reader has re-read it. That text is T-01''s INV
      range-endpoint parser, T-02''s prior-* fixture greps and SC-06 per-budget diagnostic
      assertions, and the whitespace-normalised accepted-digest checks in T-03/T-04/T-05.
      pm probed T-01''s parser (INV-1..100 hit, INV-3..4 and INV-6..8 clean, 25 live
      hits at base). The c1 remedies this re-panel targeted did pass the reader. Recommendation:
      sign without a third reader cycle, and have the executing main session observe
      each changed verify block red at base and green on the landed tree before pinning
      review_sha.'
    blocking: true
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Main should run `plan-merge.py record-panel --file <plan.yaml> --digest <this
    run>/digest.md --cycle 2` once after return, so goalcheck joins panel.readers
    (INV-32) and design is recorded as ran. panel-c2.md, which pm recorded at apply,
    lists design as skipped. The digest contract refused that, so design was dispatched
    after apply and self-scoped out with no findings, leaving apply's inputs unchanged.
    The digest.md Correction section records this.
  - The prior-* fixtures now lose the retired name in T-02. pm verified that no test
    hashes or byte-pins them (both are only copied) and that no decision freezes them.
    The INV-number grep in T-01 still exempts them, because INV numbers in an earlier
    gate revision describe that revision; this is separate from Q-06, which concerns
    the file name.
  - SC-05 is inspection-only (removal is the proof). The scope reader judged the generic
    invariants INV-7/15/37/46 not to need a stray-file test, because they read named
    records, not the stray file.
  - 'Prototype gate: no prototype is needed. No end-user interaction exists and the
    only rendered surface is deleted. This can be overridden in either direction.'
  sc_status:
  - id: operator
    verdict: pass
    method: inspection
    evidence: 'plan stage goal-check: SC-01, SC-02, SC-10, SC-11 via T-03, T-04, T-06,
      T-07; notes/research-FEAT-2423-retire-state-md-goalcheck-plan.md re-grade section'
  - id: orchestrator
    verdict: pass
    method: inspection
    evidence: 'plan stage goal-check: SC-02 via T-03; D-01 definition verbatim in
      T-03/T-04/T-05'
  - id: code maintainer
    verdict: pass
    method: inspection
    evidence: 'plan stage goal-check: SC-03..SC-08 via T-01, T-02, T-03, T-07; Q-06
      narrowing ruled'
  - id: reader
    verdict: pass
    method: inspection
    evidence: 'plan stage goal-check: SC-09 via T-05'
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - c2 apply's literal verify text (T-01 range parser, T-02 fixture/SC-06 assertions,
    T-03/T-04/T-05 definition checks) has not been re-read by a reader (LEAD-02)
  findings:
  - reader: scope
    severity: high
    kind: substance
    scope: none
    summary: SC-03 and T-07 exempt live executable fixtures despite the operator's
      Q-06 ruling.
    why: test-check-domain-claims.py and test-check-plan-routes.py install and execute
      the prior-* fixtures, which name the retired file, and the prior-* pathspec
      hid them. Resolved by T-02, which removes the name from both fixtures, and T-07/SC-03,
      which drop the exclusion.
    exposure:
      trigger: routine
      vs_today: no_worse
      control: harness
  - reader: scope
    severity: high
    kind: substance
    scope: none
    summary: The latest non-PENDING run is not necessarily the latest accepted digest
      (D-01, SC-10).
    why: A refused return closes BLOCKED with no accepted digest (feature_record/runs.py;
      DEC-156). Resolved by one _is_refused-keyed definition carried verbatim in D-01,
      SC-02, SC-10, T-03, T-04 and T-05.
    exposure:
      trigger: plausible
      vs_today: regression
      control: harness
  - reader: scope
    severity: med
    kind: substance
    scope: none
    summary: T-02's new SC-06 witness can pass on the wrong denial or miss an indented
      stale routing line.
    why: 'Exit 2 alone does not bind a budget, and Routing lines are indented. Resolved
      by T-02: valid payloads, a per-budget diagnostic, and lines stripped before
      Routing lines are selected.'
    exposure:
      trigger: plausible
      vs_today: regression
      control: harness
  - reader: scope
    severity: med
    kind: substance
    scope: none
    summary: T-01's numeric-range grep does not implement its range claim.
    why: INV-1..100 passed and INV-3..4 false-hit. Resolved by T-01, which now parses
      range endpoints.
    exposure:
      trigger: plausible
      vs_today: regression
      control: harness
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: host skip; c1 rulings narrow scope and add no build task, so no material
      scope change warrants the reader (dispatch authorised it only on one)
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
