# FEAT-2488 — pending plan delivered; scope reader's loop spent with c2 repairs unread → ESCALATE to signature

BRIEF.md (`## Approval` pending) and a two-task plan.yaml (`approval.status: pending`, both tasks main-session-direct) exist; pm reports `plan-merge.py check --root <worktree>` exit 0 after each apply and `record-panel` exit 0 at cycle 2. Panel: cycle 2, three readers recorded, 12 findings, **all 12 `resolved`** with per-finding rationale in `../../notes/research-journal-design.md` (§Panel c1 / c2 dispositions). Goal-check (re-graded after c2): operator / code maintainer / reader all **pass** against the grilling. No implementation, tests, signing, or gh-sync call (no `APPROVAL-RESET:` receipt printed).

**Why ESCALATE, not PASS.** The scope reader FAILed the draft (c1: 3 high + 1 med substance, 1 form). I sent it back once (its `loop_back`, max_cycles 1) to confirm the repairs: every c1 finding was repaired, but the repairs surfaced 3 new substance findings (2 high, 1 med) in journal-replay mechanism. pm applied them as acceptance behaviours; no reader has re-read those repairs and the loop is spent (`then: escalate`). Per DEC-176 they go to the operator's batched signature review. The trend — each repair of spelled-out journal mechanism exposes a narrower race — reads to me as the plan over-specifying mechanism, not as non-convergent design; the c2 apply was told to state repairs as behaviours (rule 6). The operator should decide whether to sign with the c2 repairs unread or buy one more scope read.

## Member results
- **draft / pm — PASS:** 2 tasks, 7 SCs (SC-01..05 seeds + SC-06 docstrings/lock order, SC-07 consumer regression), D-01 pair write / D-02 recovery; 14 anchors, 0 failures.
- **scope / code-reviewer — FAIL (c1, then c2):** c1 `../../notes/review-harness-code-reviewer-plan-c1.md`; c2 `../../notes/review-harness-code-reviewer-plan-c2.md`. Ruled draft OQ-1 (keep approval.py BRIEF rename migration onto `harness_merge.replace_bytes`) and OQ-2 (one canonical-reader inventory row, no gate edit).
- **should-not-exist / fable-advisor — PASS:** mission proportionate; 4 task-scope trims. pm trimmed 2 (SC-03 call-recording test → inspection anchor; base six-suite replay), applied 1 (recovery narrowed to member writers), declined 1 with code evidence (preflight-recovery hook kept: `amend.py#_amend_preconditions` and `amendments.py#_amendment_against_plan` exit 6 lock-free before any harness_merge call — I confirmed both symbols exist in the worktree).
- **design / ui-reviewer — PASS, self-scoped out:** no user-facing surface; **prototype gate: not required** (overridable).
- **apply / pm — PASS (c1 and c2):** 12/12 findings resolved; c1 dispositions confirmed retained after c2 record-panel.
- **goalcheck / pm — PASS (re-graded after c2):** `../../notes/research-FEAT-2488-plan-merge-atomicity-goalcheck-plan.md`; c2 added no scope beyond the grilling.

## For signature
1. c2 repairs (PF ids on the panel for the three c2 scope findings) are unread by any reader — accept, or one more scope read.
2. pm OQ-c2-1: replay drops the directory fsync after journal unlink (fails closed on a resurrected journal) — accept, or require fsync plus a third outcome class.
3. Record the Q6 rework ruling (2 rounds / 90 min) under DEC-226 — not in BRIEF/plan.
4. SC-04 locks full stdout for two amend shapes only, relying on SC-07's unedited assertions for the rest — accept the narrowing of the seed or widen.
5. Harness defect (pm draft OQ-3): `plan-merge.py apply` exited 0 on a task whose verify `load_plan` then refused ("neither runnable nor manual").
6. Panel readers roster lacks `goalcheck`; the orchestrator re-records the panel from this digest (D-03).

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'The pending 2-task plan delivers the grilled intent: all 3 perspectives
    pass and all 12 panel findings are resolved. The scope reader''s loop is spent,
    though: its c2 FAIL produced 3 substance repairs that no reader has re-read, so
    those repairs go to the operator at signature.'
  open_questions:
  - id: OQ-1
    question: 'Sign with the three cycle-2 scope repairs unread? These are replay-failure
      classification, the base-present failure seam for T-02 case (i), and the journal
      membership recheck plus duplicate-member refusal. pm applied them as acceptance
      behaviours. The alternative is buying one more scope read. The lead''s view:
      the repairs refine over-specified mechanism, not a non-converging design.'
    blocking: false
  - id: OQ-2
    question: 'pm OQ-c2-1: after a journal unlink, replay drops the directory fsync.
      A resurrected journal is then either a no-op or refuses DIVERGED, failing closed
      with nothing lost. Accept this, or require the fsync plus a third outcome class?'
    blocking: false
  - id: OQ-3
    question: Record the grilling's Q6 rework ruling (2 rounds / 90 min) at signature
      under DEC-226. Neither BRIEF.md nor plan.yaml carries it.
    blocking: false
  - id: OQ-4
    question: SC-04 locks full amend stdout for only two amend shapes and relies on
      SC-07's unedited assertions for the rest. The grilling seed said byte-identical
      for every existing green case. Accept this narrowing or widen it?
    blocking: false
  - id: OQ-5
    question: 'Harness defect reported by pm: plan-merge.py apply exited 0 (APPLIED)
      for a task whose verify begins with env -u HARNESS_AGENT_TYPE. harness_yaml.load_plan
      then refused that task as ''neither runnable nor manual'', leaving the plan
      unloadable until amend fixed it. Should apply run load_plan''s verify check
      before it writes?'
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/research-journal-design.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/research-FEAT-2488-plan-merge-atomicity-goalcheck-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/review-harness-code-reviewer-plan-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/review-harness-code-reviewer-plan-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/review-harness-ui-reviewer-plan-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261123-1-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261123-1-plan-product/criteria.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261123-1-plan-product/panel-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261123-1-plan-product/panel-c2.md
  expertise_update: []
  team: plan
  steps_run: 6
  cycles_used: 1
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 'Pending draft: 2 main-session-direct tasks, 7 SCs. D-01 is the fsync''d
      pair-write journal in harness_merge and D-02 is roll-forward recovery. Check
      reported 14 anchors and 0 failures.'
    files_touched:
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/BRIEF.md
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/plan.yaml
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/research-journal-design.md
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/observations/harness-pm.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'c1: 3 high, 1 med and 1 form finding. c2 confirmation read: all c1
      findings repaired, but 3 new substance findings (2 high, 1 med) in journal-replay
      mechanism. Loop spent.'
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: Mission proportionate; 4 task-scope trims (2 low, 2 info), nothing gating.
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Self-scoped out in Mode A: no user-facing surface; no DESIGN.md or
      prototype required.'
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: c1 and c2 applied, 12/12 findings resolved with rationale. One trim
      was declined with code evidence. record-panel (cycle 2) and check both exit
      0.
    files_touched:
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/BRIEF.md
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/plan.yaml
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/research-journal-design.md
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/observations/harness-pm.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 'Re-graded after c2 against the grilling: operator, code maintainer
      and reader all pass. c2 added no scope beyond the grilling.'
    files_touched:
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/research-FEAT-2488-plan-merge-atomicity-goalcheck-plan.md
  must_fix:
  - 'Operator ruling at signature on the three cycle-2 scope repairs no reader has
    re-read (OQ-1): accept them, or buy one more scope read.'
  - Orchestrator re-records the panel from this digest so goalcheck joins the reader
    roster (D-03).
  branch: feat/FEAT-2488-plan-merge-atomicity
  escalations:
  - id: E-01
    raised_by: harness-product-lead
    question: 'The scope reader''s loop_back is at max_cycles (1) and its c2 return
      is FAIL. The 3 c2 substance repairs are applied but unread. The team file''s
      then: escalate applies.'
    domain: plan signature
    routed_to: harness-orchestrator
    resolution: Pending operator ruling at the batched signature review (DEC-176).
      Plan stays pending.
    decided_by: none
    recorded_as: runs/r-20261123-1-plan-product/digest.md
  - id: E-02
    raised_by: harness-product-lead
    question: Re-record the panel from this validated digest, adding goalcheck as
      the fourth reader.
    domain: orchestration
    routed_to: harness-orchestrator
    resolution: Panel is recorded at cycle 2 with 3 readers. Adding the fourth reader
      follows this return.
    decided_by: none
    recorded_as: runs/r-20261123-1-plan-product/digest.md
  adequacy_notes:
  - 'BRIEF.md has ## Approval pending and plan.yaml has approval.status pending. Both
    tasks are main-session-direct. pm reports plan-merge check --root <worktree> exit
    0 after both applies and record-panel exit 0 at cycle 2. No APPROVAL-RESET receipt
    was printed, so there was no gh-sync call.'
  - 'Panel at cycle 2: readers scope, should-not-exist and design all ran. 12 findings,
    0 open, rationale in notes/research-journal-design.md under Panel c1 and Panel
    c2 dispositions. should-not-exist and design were not re-dispatched in c2; their
    c1 returns stand.'
  - 'Dispositions:'
  - '- c1 scope: 4 substance applied; form DEC-230 keep added.'
  - '- should-not-exist: preflight hook declined with evidence; SC-03 test trimmed
    to an inspection anchor; recovery narrowed to member writers; base six-suite replay
    trimmed.'
  - '- c2 scope: 3 applied as acceptance behaviours, not re-read.'
  - 'Panel transcription: the scope reader labelled its c1 findings ''code-reviewer''.
    They are recorded under its step id ''scope'', as its c2 return does. fable-advisor
    self-labelled ''second-opinion-advisor''; it is recorded as the dispatched persona
    fable-advisor. Severities, kinds, summaries and whys are verbatim.'
  - Reader tension resolved by evidence, not deference. Scope endorsed the _resolve_plan
    preflight-recovery hook and should-not-exist called it redundant. pm kept it because
    amend.py#_amend_preconditions and amendments.py#_amendment_against_plan exit 6
    lock-free before any harness_merge call; the lead confirmed both symbols exist
    in the worktree.
  - 'Scope ruled pm''s draft questions: keep the approval.py BRIEF-rename migration
    onto harness_merge.replace_bytes, which SC-02''s zero-hit predicate requires,
    and allow one canonical-reader inventory row. Neither edits check-plan-routes.py
    or its test.'
  - Reader detail sits in the member headlines because the readers[].reason field
    accepts only none.
  - 'Prototype gate: not required. ui-reviewer self-scoped out with no user-facing
    surface. Overridable in either direction.'
  - 'No scope: mission proportionality finding, so no downgrade recommendation.'
  - cycles_used 1 = the one scope send-back. The apply and goalcheck re-runs followed
    from it and are re-dispatches, not separate send-backs.
  sc_status:
  - id: perspective:operator
    verdict: pass
    method: inspection
    evidence: SC-01/04/07 via T-01 and T-02; notes/research-FEAT-2488-plan-merge-atomicity-goalcheck-plan.md
  - id: perspective:code maintainer
    verdict: pass
    method: inspection
    evidence: SC-02/03/06 via T-01 and T-02; goalcheck note
  - id: perspective:reader
    verdict: pass
    method: inspection
    evidence: SC-05 via T-02 migration (8 base checks re-measured at 2491336e); goalcheck
      note
  - id: SC-01..SC-07
    verdict: planned
    method: inspection
    evidence: All SCs trace to T-01/T-02; no implementation verification claimed
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - The three cycle-2 scope repairs have not been re-read by any reader.
  - Power-loss durability and a live SIGKILL mid-transaction stay unproven by design.
    Torn states are built on disk, as stated in the BRIEF's Verification gaps.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-01 can replay or unlink a replaced journal generation.
    why: The journal is read before locking, then checked only for existence. If one
      writer finishes J1 and another dies with J2 pending, a delayed recovery can
      falsely reject J2 as divergent or unlink it. Validate the current journal under
      the replay locks and test replacement and disappearance deterministically.
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-02 reports transaction outcomes from a racy pathname check.
    why: After locks release, another writer can finish recovery before the consumer
      checks the path, yielding a false 'nothing was written' receipt. The core must
      report transaction outcome. A post-commit feedback exception also still aborts
      the CLI before APPLIED; pin that outcome separately.
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-02 final verification omits three SC-07 suites.
    why: Observations, expertise and inflight-registry run against T-01 or the base
      but are absent from the terminal verify. Their base or predecessor results do
      not establish a pass at the final pin.
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: Pin a schema-valid feature.json mutation in T-02 case (e).
    why: The proposed unrelated new key is unspecified and the schema rejects unknown
      top-level fields. A known valid mutation plus an exact assertion proves the
      ordinary writer proceeds after recovery.
  - kind: form
    scope: none
    severity: low
    reader: scope
    summary: Record DEC-230 as keep.
    why: The changed ledger path implements the amendment judgement premise that INV-40
      relies on without changing signed hashes or the invariant. No decision requires
      amendment or strike.
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: T-02's preflight recovery hook (_resolve_plan recover=True, item 3) is
      outcome-redundant with the recovery already inside locked_update and locked_pair_update
      and should not be built
    why: "Verified every mutating verb funnels through _locked_plan_update -> harness_merge.locked_update\
      \ (guards.py:229-233) or write_plan_and_ledger, whose T-01 bodies recover the\
      \ journal before any transform runs; and every transform recomputes under the\
      \ lock from the recovered base with its own CAS or compare-and-splice (amend.py:283-285\
      \ _require_locked_hash, amendments.py _amended_plan_bytes on `was`, approval.py:321-327\
      \ hashes \"computed from the very bytes being signed\"), so every SC-01 convergence-and-exit-6\
      \ outcome lands identically without the preflight call. Building it anyway buys\
      \ only nicer pre-lock messages (--show, preflight refusals) at the cost of a\
      \ second production recovery site, a recover= parameter, and a check.py special-case\
      \ (T-02 item 4) that exist solely to feed it \u2014 two recovery entry points\
      \ to keep consistent forever, and a lock-free call that can race anyway (a journal\
      \ can appear after it runs, which is exactly why locked_update loops)."
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: SC-03's mandatory call-recording fsync-ordering unit test over-builds
      where the grilling explicitly allowed "a test or code anchor cited"
    why: 'The grill''s SC-03 seed (Q5) sanctions a cited code anchor as sufficient
      evidence that the journal is fsync''d before the first rename; the BRIEF hardens
      this into a required monkeypatch test recording the exact sequence of the core''s
      os-level calls plus a QA red-first demonstration. Such a test couples the suite
      to internal call structure, not behavior: a behaviorless refactor of the write
      path (e.g. a different fd/fsync idiom) breaks it and costs a maintainer a test
      rewrite with zero durability information gained, while the torn-state tests
      of SC-01 already prove the only ordering property a user can observe.'
  - kind: proportionality
    scope: task
    severity: info
    reader: should-not-exist
    summary: "D-02's broadening of recovery to every harness_merge write in the directory\
      \ makes a diverged journal block unrelated writers \u2014 blast radius beyond\
      \ the grill's \"every acquirer of the plan lock\" that the pair's atomicity\
      \ does not need"
    why: "T-01 item 6 runs recover_journal unconditionally before any locked_update\
      \ in the directory, and the JOURNAL UNREADABLE/DIVERGED refusal states \"every\
      \ harness_merge write in this directory refuses\". The grill (Q2) scoped recovery\
      \ to plan-lock acquirers; the BRIEF extends to feature.json writers (justified\
      \ \u2014 D-02's feature.json-only-writer rationale is real, verified via _record_rework\
      \ writing feature.json before the plan lock at approval.py:308-313); but the\
      \ further step means a non-member write in the feature directory (e.g. an observations\
      \ or notes-file merge living beside plan.yaml) is bricked at exit 5 by a torn\
      \ amendment it did not create and is not party to, until an operator hand-reconciles.\
      \ Divergence requires manual tampering so this is rare, but the consequence\
      \ should be consciously accepted or the refusal narrowed to member writes, not\
      \ inherited silently from a uniform-rule convenience."
  - kind: proportionality
    scope: task
    severity: info
    reader: should-not-exist
    summary: T-02's six-suite baseline run in the detached base worktree (baseline-t02-regression-base.txt)
      is receipt ritual duplicating evidence the pin already carries
    why: SC-07's information content is "these suites pass at the review pin without
      assertion edits"; re-running test-harness-merge, test-feature-json-merge, test-observations-merge,
      test-expertise-merge, test-inflight-registry and test-check-state-feat59 inside
      the base worktree proves only that main was green at 2491336e, which the repo's
      required CI gates already establish for main [unverified that CI ran at that
      exact SHA]. The red torn-state runs and SC-04's stdout baseline genuinely need
      the base worktree (grill-mandated failure-first), but the marginal six-suite
      replay adds per-task operator minutes and note artifacts with no decision value
      to the reviewer.
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: 'T-01/T-02: classify failures during replay of a published journal.'
    why: "If replay replaces the plan and the ledger then hits ENOSPC, the raw error\
      \ can traceback at preflight or be reported as \u201Cnothing was written\u201D\
      \ inside the pair path (plan.yaml:178,181\u2013184,248\u2013249)."
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-02 case (i) does not exercise the baseline ledger-replace failure.
    why: "The test patches replace_bytes, absent at the base. It can fail at setup\
      \ without demonstrating the old diagnostic (plan.yaml:243\u2013244; base harness_merge.py:141\u2013\
      172)."
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-01 must recheck membership of the current journal and reject duplicate
      members before locking.
    why: "After discovery, a new generation can omit the requested file but still\
      \ block its writer on unrelated divergence. A duplicate primary member can also\
      \ make recovery try to acquire its own lock again (plan.yaml:118,179\u2013182)."
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261123-1-plan-product/digest.md
```
