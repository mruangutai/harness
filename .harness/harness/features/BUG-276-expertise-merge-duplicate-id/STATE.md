# STATE

## Current

- feature: BUG-276-expertise-merge-duplicate-id
- run: .harness/harness/features/BUG-276-expertise-merge-duplicate-id/runs/2026-09-07-05-product/state.yaml
- squad: none
- status: awaiting-user

PLAN PHASE COMPLETE, awaiting the operator's signature. BRIEF.md (4 REQ, 6 SC) and plan.yaml
(2 tasks, 9 decisions) are drafted; approval is pending on both and only the main session signs.
All three panel segments ran: the pm goal-check (6 findings, all applied or recorded), the
plan-panel team (both readers ran, 3 findings), and the transcription into plan.yaml's `panel:`
key — 3 readers, 9 findings, every open one info/low/med. Next after signature: the build phase,
T-01 then T-02, both to harness-backend-dev via harness-eng-lead.

The goal-check run left no run directory, so feature.json records it as
2026-09-07-goalcheck-product-no-rundir and check-state.sh emits an accurate informational note
about the absent dir. Its artifact is on disk at notes/research-BUG-276-goalcheck-plan-c0.md.

## Open Questions

- Q1 (for the operator at signature, non-blocking): the exit-11 row in harness-distill/SKILL.md's
  agent-facing apply refusal table. Add it (one new main-session-direct task, since that file
  resolves to lane NOBODY), or keep D-09's recorded exclusion? Finding
  PF-8eac8a4b4f41d3ea8f759cdec6e73186, med, open.
- Q2 (for the operator, non-blocking): D-07 records the parse_expertise/render silent drop as a
  known separate defect left unfixed. File it as its own ticket? Finding
  PF-59b9da56871cca170a7f66678c292035, med, open.
- Q3 (for the operator, non-blocking): the panel's proposal to drop T-02's case27b was assessed
  and REJECTED with a reason recorded in the plan. Accept, or overrule
  PF-d6fb0ad9a0491cc93c7ac648cd092e8c via approval.rulings? Finding low, open.
- Q4 (correction the operator should read, non-blocking): the ticket and the dispatch both say the
  merge keeps the last-seen entry. Measured: it is FIRST-wins — the later entry never arrives.
  BRIEF and plan follow the measurement. Finding PF-15e24dab70b6caca5bf5ba4837356157, low, open.
