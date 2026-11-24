# FEAT-2489 — plan apply c3 (r-20261124-5-plan-product)

**PASS. All three cycle-3 remedies are in BRIEF.md and plan.yaml. approval.status is still pending. pm reports `plan-merge.py check` with 0 failures. Four findings stay open until the scope reader re-reads them. Two widenings, needed to keep SC-02 satisfiable, go to the signer.**

## Assessed against the pre-written send-back criteria (sendback-criteria.md)
- **SC-02 item 5 (PF-2411, PF-6159).** The class is now stated by what a diagnostic prints (BRIEF.md SC-02, fifth bullet): "Membership is decided by what the diagnostic prints, never by where the printed value comes from". The three producers appear only as illustrations, and the line-number member is included. Before dispatch, the lead confirmed that line-number locators exist in check-plan-routes.py (`{relative}::...:{node.lineno}` at ~1922, ~1940, 2108, 2138, 2360–2444).
- **T-02 (PF-b14b).** The map is derived from the move (old `check-plan-routes.py::NAME` → `MODULE::NAME`, never taken from the inventory). It rewrites only each line's locator, and every other character is compared in order. Line numbers are not modelled: a line-numbered locator in check-plan-routes.py or in either module makes the comparison FAIL. The location-order exception is not modelled either and also FAILs. Nothing is loosened.
- **T-01 (PF-1dd0).** The verify loops over both `canonical_reader_audit.py` and `structure_audit.py` and requires each to be absent at the recorded commit. The ancestor-and-blob binding is unchanged.
- The disclosed-departure note is reworded to the locator class. Ruled scope is untouched: SC-01..SC-05, no new task, no AST checker.

## Lead judgement on pm's two widenings (OQ-c3-1, OQ-c3-2)
pm went past the dispatch's class wording in three places:
- An order exception for producers that emit in file-walk or line order.
- Line shifts for sites that do not move but sit in check-plan-routes.py.
- "First site named" instead of "leading", because `_row_lookup` prints the id mid-line.

All three follow from the move itself. The dispatch's governing invariant (SC-02 must be satisfiable by a verbatim move on every audited tree state) requires them, and its narrower class wording would contradict that invariant. The lead checked the ordering claim: `canonical_reader_audit.py` sorts before `check-decision-anchors.py`/`check-domain.py`, and `structure_audit.py` sorts after `check-plan-routes.py`, so a file-walk order does change. The lead accepts all three as consequences of the move, not as admitted behaviour. They are disclosed in BRIEF and go to the signer as non-blocking questions.

## Residual (not sent back)
- **Low, form.** T-01's intent prose still says the recorded HEAD must hold "no canonical_reader_audit.py". The verify and the expected-exit line say neither module may exist. The verify is the stricter text and the one that is enforced. The re-read may flag the prose; fix it at the next apply.
- The 0-failure check result comes from pm's own run. The lead holds no shell and did not rerun it.

## PF dispositions at exit
- **Resolved this run:** PF-6efa88c8, PF-5dbe6b5e (both confirmed closed by class at c3) and PF-4405ff64 (the c3 confirmation of PF-6efa's closure).
- **Applied but still open until re-read:** PF-24112618, PF-6159b235, PF-b14b5b45, PF-1dd0f7a1.
- **Resolved earlier and unchanged:** PF-b25f, PF-0e91, PF-9bc7, PF-293c, PF-2f03, PF-0dad, PF-b963, PF-29a7.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-5-plan-product/digest.md
DIGEST:
  headline: 'Cycle-3 remedies are applied: SC-02 item 5 is now stated by locator and
    includes line numbers, T-02 rewrites only locators and fails on unmodelled line
    numbers or reordering, and T-01 requires that neither module exists. Approval
    stays pending, and pm reports 0 check failures. Four PF findings stay open for
    re-read, and two widenings go to the signer.'
  open_questions:
  - id: OQ-c3-1
    question: 'SC-02 item 5 adds an order exception. Where a producer prints diagnostics
      in file-walk or line order, a relocated diagnostic takes the position its new
      location gets: canonical_reader_audit.py sorts before check-decision-anchors.py
      and check-domain.py, and structure_audit.py sorts after check-plan-routes.py.
      Without this exception a verbatim move cannot satisfy SC-02. The T-02 checker
      does not model the exception and would FAIL on a reorder; no sampled state reorders.
      The exception is disclosed in BRIEF''s departure note. The lead accepts it as
      a consequence of the move. Does the signer accept it, or narrow SC-02?'
    blocking: false
  - id: OQ-c3-2
    question: Item 5 also covers two cases beyond moved sites. First, sites that stay
      in check-plan-routes.py change line number because SC-01's diff removes or adds
      lines above them. Second, the locator is defined as the first site a diagnostic
      names, because _row_lookup prints the row id mid-line. Both are needed for the
      same satisfiability reason, and both are disclosed in BRIEF. The lead accepts
      them. Does the signer accept them?
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/research-plan-routes-split.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-5-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-5-plan-product/sendback-criteria.md
  expertise_update: []
  team: plan
  steps_run: 1
  cycles_used: 0
  members:
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: 'Remedies A, B and C applied: the locator class, a locator-only map
      that FAILs on unmodelled line numbers and order, and both modules absent at
      the T-01 checkpoint. The plan-merge check reports 0 failures, and two widenings
      are raised to the signer.'
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/BRIEF.md
    - .harness/harness/features/FEAT-2489-plan-routes-split/plan.yaml
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/research-plan-routes-split.md
    - .harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-pm.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'PF dispositions at exit. Resolved this run: PF-6efa88c834c89ca43eea0322509703d9
    and PF-5dbe6b5eecda5efa44c6d9624e826e1a (both confirmed closed by class at c3),
    and PF-4405ff64a842f05eadbdbad42e358e73 (the c3 confirmation of PF-6efa''s closure).
    Applied but still open until re-read: PF-241126189d3c3d16550a5f09c7532ff3, PF-6159b2359da400c4da7dca8dcaa1415e,
    PF-b14b5b45525eb18f63e04849c88d3838, PF-1dd0f7a1329fa5038cc5e6aa8e0c3ecb. Unchanged
    and resolved: PF-b25f, PF-0e91, PF-9bc7, PF-293c, PF-2f03, PF-0dad, PF-b963, PF-29a7.'
  - The 'sibling id' for whole-line replacement is PF-b14b5b45525eb18f63e04849c88d3838,
    read from plan.yaml. PF-6159b2359da400c4da7dca8dcaa1415e is the class-not-closed
    sibling of PF-2411 and shares remedy A.
  - Before dispatch, the lead confirmed that check-plan-routes.py prints line-numbered
    locators ({relative}::symbol:{node.lineno} at ~1922, ~1940, 2108, 2138, 2360-2444).
    The line-number member is therefore real.
  - 'The lead accepts pm''s widenings beyond the dispatch''s class wording (order
    exception, line shifts for sites that do not move, first-site-named locator) because
    the dispatch''s governing invariant requires them: SC-02 must be satisfiable by
    a verbatim move. The narrower class wording would contradict that invariant. They
    go to the signer as OQ-c3-1 and OQ-c3-2.'
  - 'Low form residual, not sent back: T-01''s intent prose still says the recorded
    HEAD must hold ''no canonical_reader_audit.py'', while the verify loop and the
    expected-exit line require that neither module exists. The verify governs. The
    re-read may flag the prose; fix it at the next apply.'
  - The 0-failure plan-merge check is pm's own run. The lead holds no shell and did
    not rerun it.
  - 'No reader ran in this run. The readers entry records only the apply step. There
    is no prototype gate: the feature has no UI surface (c1 design reader).'
  sc_status: []
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'PF-241126189d3c3d16550a5f09c7532ff3 / PF-6159b2359da400c4da7dca8dcaa1415e:
      SC-02 item 5 is now stated as a class by what a diagnostic prints (the locator:
      file, ::symbol, line number where printed), including the order and line-shift
      consequences. Both stay open until re-read.'
    why: Two earlier source-based statements each missed a member, so the verbatim
      move could not satisfy them.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'PF-b14b5b45525eb18f63e04849c88d3838: T-02''s map is derived from the
      move and applies to locators only. Every other character is compared in order,
      and the checker FAILs on unmodelled line-numbered locators or reorders. Open
      until re-read.'
    why: Substituting across the whole line could mask a change outside the sanctioned
      class.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'PF-1dd0f7a1329fa5038cc5e6aa8e0c3ecb: T-01''s verify now requires that
      both canonical_reader_audit.py and structure_audit.py are absent at the recorded
      commit. Open until re-read.'
    why: A guard on one module alone does not prove the checkpoint predates the move.
  readers:
  - reader: apply
    status: ran
    persona: harness-pm
    reason: none
```
