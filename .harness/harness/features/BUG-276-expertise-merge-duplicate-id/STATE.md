# STATE

## Current

- feature: BUG-276-expertise-merge-duplicate-id
- run: .harness/harness/features/BUG-276-expertise-merge-duplicate-id/runs/2026-09-07-06-eng/state.yaml
- squad: eng
- status: in_progress

BUILD ENG SEGMENT COMPLETE AND COMMITTED. The operator signed BRIEF and plan at a29450a1;
plan.yaml reads `status: building`, `approval.status: approved`, no `approval.rulings` — so every
panel disposition recorded in the plan stands as written (D-07 and D-09 included). T-01 landed at
88a627da and T-02 at 97e715d1; both tasks read station `done` in plan.yaml, the worktree is clean,
and run 2026-09-07-06-eng (PASS, both steps complete) is now recorded in feature.json — the prior
attempt was cut off before it wrote that record, which is the only drift a resume had to repair.

Verified by me at HEAD, not from the lead's digest: `python3 tests/unit/test-expertise-ops.py` and
`python3 tests/integration/test-expertise-merge.py` both end `PASS <file>` with the u23a/b/c and
case27a/b/c checks present.

NEXT: the qa segment — the project's one blocking gate (`harness.json` `gates.qa_gate: blocking`)
against the two-commit diff 6d969ed3..97e715d1, change_type bugfix on both tasks. After qa passes,
SIMPLIFY (harness-eng-lead, reading harness-simplify by path) is the last build step and must land
BEFORE `review_sha` is pinned. `review_sha` is still `none` and stays that way until the
Building → Review seam.

## Open Questions

The four questions below were raised FOR the operator at signature. The signature landed
(a29450a1) with `approval.status: approved` and no `approval.rulings`, so the plan's own recorded
dispositions stand and none of these blocks the build. Q2 survives as a residual for the ship
briefing's backlog table; the rest are settled by the signature.

- Q1 (settled by signature, D-09 stands): no exit-11 row was added to the agent-facing apply
  refusal table in `.claude/skills/harness-distill/SKILL.md` — that file resolves to lane NOBODY.
  Finding PF-8eac8a4b4f41d3ea8f759cdec6e73186, med, open in the panel record.
- Q2 (residual, for the ship briefing backlog): D-07 records the parse_expertise/render silent
  drop (expertise-merge.py:73-95 plus :103-111, exit 0, both routes) as a known separate defect
  left unfixed. Recommend filing it as its own ticket. Finding
  PF-59b9da56871cca170a7f66678c292035, med.
- Q3 (settled by signature, plan stands): T-02's case27b was kept; the panel's proposal to drop it
  was assessed and REJECTED with a reason recorded in the plan. PF-d6fb0ad9a0491cc93c7ac648cd092e8c,
  low.
- Q4 (correction on the record): the ticket and the original dispatch say the merge keeps the
  last-seen entry. Measured: it is FIRST-wins — the later entry never arrives. BRIEF, plan and the
  landed fix all follow the measurement. PF-15e24dab70b6caca5bf5ba4837356157, low.
