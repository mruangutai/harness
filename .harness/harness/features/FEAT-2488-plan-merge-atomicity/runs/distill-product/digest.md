# FEAT-2488 distill (product) — PASS: pm +2 craft entries by displacement, lead +1 Outcome

**pm (craft, batch `60cd6d3f…`):** P-17 dropped → P-19 added (LC-1: probe one boundary beyond a class contract before calling the class closed); G-17 dropped → G-22 added (observation 3: trace per-invocation guarantees through every entry path's preflight). Counts craft P 15→15, G 15→15, O 10→10, Open 0→0; repository tier untouched (P 13, G 15, O 1, Open 0). Receipt `notes/expertise-receipt-1da16933…json`; dispositions in `notes/research-FEAT-2488-plan-merge-atomicity-distill.md`.

**Rejected by pm with reasons:** LC-2 (final-round terminal condition is the ruling author's surface, not pm's — fable-advisor carries it as its own P1); observation 1 (harness defect, already backlogged at signoff Q3 / ship BL-5); observations 2, 4, 5, 6 (covered by existing rules or recipe/mechanism detail).

**Lead (craft, batch `99743fd9…`):** O-09 added — when plan-time repairs each surface one narrower failure in one mechanism, have pm state the family as a class contract with exhaustive state enumeration before signature. Counts P 15→15, G 15→15, O 8→9, Open 0→0. This corrects my plan-run trend reading (over-specified mechanism only): signature expected one rework round; validate spent four, one class member per round.

**Assessment:** all seven send-back criteria (`sendback-criteria.md`, written before dispatch) met; verified P-19 and G-22 present in the resulting file. Reservation, not send-back (O-03): P-17's displacement relies on role text carrying the same rule. No diff reviewed and no suite run — distill only.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'Product distill done: pm added 2 craft entries by displacement (P-19
    probe beyond class contract before ''closed''; G-22 trace per-invocation guarantees
    through every entry-path preflight), rejected LC-2 and 5 observations with reasons;
    lead added O-09 (state repair families as class contracts before signature).'
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/expertise/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/expertise/harness-product-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/research-FEAT-2488-plan-merge-atomicity-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/distill-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/distill-product/sendback-criteria.md
  expertise_update:
  - persona: harness-pm
    op: drop
    target: P-17
    section: Patterns
    why: 'Displaced by P-19: weakest Pattern in my judgment; its rule (evidence cannot
      grant task ownership) is already carried by the goal-check role text that names
      a change with no owning task as a plan/scope defect.'
  - persona: harness-pm
    op: add
    target: P-19
    section: Patterns
    entry: WHEN declaring a defect class closed DO run one probe one boundary beyond
      the stated class contract (an adjacent route, configuration or caller) and state
      that boundary in the claim. Measured only inside its contract, closed is true
      by definition while the next round finds the neighbour.
    why: 'LC-1: my final goal-check called both classes closed as a class with no
      probe beyond the contract, and adjacent members surfaced from readers who probed
      outside it; distinct from P-06, which re-measures a failed premise but never
      tests the boundary.'
  - persona: harness-pm
    op: drop
    target: G-17
    section: Gotchas
    why: 'Displaced by G-22: narrowest Gotcha (git status on ignored paths), rarely
      reached from a pm seat.'
  - persona: harness-pm
    op: add
    target: G-22
    section: Gotchas
    entry: 'WHEN a criterion promises every invocation converges, recovers or checks
      something DO trace each entry path to where that mechanism runs: a preflight
      that refuses before reaching the shared core skips it, so a re-run never converges.
      Grade per entry path, not by the core alone.'
    why: 'Observation: two verbs refused in lock-free preflight before the core, so
      recovery placed only in the core would never have run on re-run; general to
      any per-invocation guarantee.'
  - persona: harness-product-lead
    op: add
    target: O-09
    section: Outcomes
    entry: "WHEN a plan-time reader's repairs each surface one narrower failure in\
      \ the same mechanism DO ask pm to state that family as a class contract with\
      \ an exhaustive state enumeration before signature \u2014 instance repairs reach\
      \ validate as instances, and each round there surfaces one more member."
    why: My plan-run escalation read successive journal-replay races as over-specified
      mechanism only; signature expected one rework round, validate then spent four
      with one class member per round until a ruling enumerated the class exhaustively.
  team: distill
  steps_run: 1
  cycles_used: 0
  members:
  - step: distill-pm
    persona: harness-pm
    verdict: PASS
    headline: 2 craft entries added (P-19, G-22) displacing P-17 and G-17; LC-2 and
      5 observations rejected with reasons; repository tier untouched.
    files_touched:
    - .harness/expertise/harness-pm.md
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/research-FEAT-2488-plan-merge-atomicity-distill.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Per-section counts, pm craft (batch 60cd6d3f8c39e2a4ec51fc50829cafd19d9be6b8b8b03cbb692919df5905808a):
    Patterns 15->15, Gotchas 15->15, Outcomes 10->10, Open 0->0. pm repository (harness):
    untouched at P 13, G 15, O 1, Open 0.'
  - 'Lead craft (batch 99743fd954e634c1bf1afa15cf7d020ae53995a0f767ade1937b380cdb1cf6fe):
    Patterns 15->15, Gotchas 15->15, Outcomes 8->9, Open 0->0. Lead repository tier
    untouched.'
  - 'Candidate dispositions: LC-1 applied as P-19. LC-2 rejected, because the final-round
    terminal condition belongs to the ruling author and fable-advisor carries it as
    its own P1. LC-3 yielded G-22 from observation 3. Observation 1 is a harness defect
    already backlogged (signoff Q3, ship BL-5), so it is not Expertise.'
  - 'All seven send-back criteria in runs/distill-product/sendback-criteria.md, written
    before dispatch, were met. I confirmed P-19 and G-22 in the resulting file. One
    reservation, not a send-back (O-03): dropping P-17 relies on role text carrying
    the same rule.'
  - This was a distillation only. No diff was reviewed and no suite was run.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/distill-product/digest.md
```
