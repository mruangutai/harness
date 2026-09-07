# STATE

## Current

- feature: BUG-276-expertise-merge-duplicate-id
- run: .harness/harness/features/BUG-276-expertise-merge-duplicate-id/runs/2026-09-07-1-validator/state.yaml
- squad: validator
- status: in_progress

QA GATE PASSED — the project's one blocking gate is green on measurement, not on a receipt's word.
Run 2026-09-07-1-validator (harness-validator-lead → harness-qa) resolved both required matrix
kinds satisfied (unit, plus integration added above the floor for the CLI-boundary SCs), measured
the suites itself with the runner's exit status captured — unit 520 PASS / 0 FAIL, integration
1513 PASS / 0 FAIL, and both task `verify:` blocks verbatim at exit 0 — and proved every one of
the six new checks reddens under a live mutation of the guard's call site in a disposable copy,
which closes D-08's stated risk that a well-named check can pass on a weak assertion. All six SCs
graded PASS by qa (SC-06 by inspection, as the BRIEF declares). `must_fix: []`, 0 send-backs, so
`cycles_used` stays 2. Artifact: notes/qa-BUG-276-c0.md, which also carries two advisory,
non-gating notes: exit 11's precedence over the pre-existing exits 7 and 8 is unpinned by any
test, and SC-06 is inspection-verified by design.

Prior to that, the interrupted eng segment was reconciled: T-01 (88a627da) and T-02 (97e715d1)
were already committed with both tasks at station `done`; run 2026-09-07-06-eng was recorded at
2e1f7142 and both suites re-run green at HEAD by the orchestrator.

NEXT: SIMPLIFY — the last build step, dispatched to harness-eng-lead, which must be told to read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-simplify/SKILL.md` first (it is not preloaded). It runs BEFORE
`review_sha` is pinned, because an apply commit after the pin moves the tip and invalidates the
panel's verdict. Re-run both suites after any apply. An empty pass is a real outcome. Only after
simplify lands does the Building → Review seam open: pin `review_sha`, then
`gh-sync.py status <feature-dir> review`, then the panel. `review_sha` is still `none`.

## Open Questions

The four signature-time questions are settled or residual as recorded below; the two new ones come
from the qa run and neither blocks.

- Q5 (NEW, harness defect, non-blocking): `check-domain.sh`'s worktree-claim guard matches a live
  claim by agent-type STRING alone (`inflight_registry.live_claims` / `claim_worktrees`), never by
  session or feature. A concurrent unrelated harness-qa gate for BUG-240 became this session's
  entire allowed claim set and blocked a write into BUG-276's own tree until qa registered its own
  claim by hand. For the harness owner; not Expertise.
- Q6 (NEW, non-blocking): `test_matrix`'s `__bug_class__` / `match_bug_class` predicate is an
  unresolvable placeholder with no taxonomy entries, so that matrix leg can never fire and can
  never be audited. Remove it, or give it a taxonomy?
- Q2 (residual, for the ship briefing backlog): D-07 records the parse_expertise/render silent
  drop (expertise-merge.py:73-95 plus :103-111, exit 0, both routes) as a known separate defect
  left unfixed. Recommend filing it as its own ticket. PF-59b9da56871cca170a7f66678c292035, med.
- Q1, Q3, Q4 (settled by the signature at a29450a1, which carries no `approval.rulings`): D-09's
  exclusion of the exit-11 row from `harness-distill/SKILL.md` stands (that file resolves to lane
  NOBODY); T-02's case27b was kept and the panel's proposal to drop it stays REJECTED with the
  reason in the plan; and the record correction stands — the merge is FIRST-wins, not last-wins as
  the ticket says, and BRIEF, plan and the landed fix all follow the measurement.
