# STATE

## Current

- feature: FEAT-52-handoff-done-when
- run: .harness/harness/features/FEAT-52-handoff-done-when/runs/2026-09-02-5-product/state.yaml
- squad: none — plan phase complete, awaiting the operator's signature
- status: awaiting-user

Plan phase finished at the signature gate. BRIEF.md (10 REQ, 14 SC) and plan.yaml (13 tasks,
9 decisions, station `plan`) are drafted, goal-checked twice, repaired twice, and read by the
adversarial panel; both approval blocks read pending. Handoff: notes/handoff-plan.md.

## Open Questions

- Q1 (blocking signature, operator): panel finding PF-4205e7e2 (med) — should INV-17 re-resolve
  every pointer in every post-contract note forever, or check only presence and shape there and
  leave resolution to the write gate? The grilling settled resolution at write time; the permanent
  half is plan-added and makes an untouched valid note rot when a later BRIEF renumbers an SC.
- Q2 (blocking signature, operator): D-04 persists a model-driven comprehension probe as
  bin/probe-handoff-comprehension.py registered as a `locally_run` test kind. The grilling asked
  only that the benchmark be rerunnable at review. Striking D-04 also strikes T-09, T-12's three
  cases and SC-09's registration clauses (finding PF-1e45eb3a).
- Q3 (non-blocking, operator): T-13 authors a one-off mutation-experiment note descending from
  DEC-179 via D-09/SC-07, not from any grilling line. Keep or strike at signature.
- Q4 (non-blocking, operator): the id FEAT-52 is already carried by a live second feature,
  FEAT-52-factory-control-plane (open milestone 41, live branch and worktree). Directory and
  milestone keys do not collide; the numeric prefix is ambiguous in human reference.
