# STATE

## Current

- feature: BUG-201-depends-on-integrity
- mission: plan — COMPLETE at cycle c1. The plan is approval-ready; the operator's signature is the
  only remaining act of this phase.
- status: awaiting_user (signature), station `plan` (plan.yaml `status: plan`)
- source ticket: issue #201 · intake `.harness/notes/grilling-depends-on-integrity-2026-09-06.md`
  · operator ruling `notes/answers-plan-c0.md` (2026-09-07, Q-A: consumers must surface the
  specific validation error — in scope)
- worktree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity
- branch `feat/BUG-201-depends-on-integrity`, HEAD c6d6ee6e, base af859ee8. `review_sha` stays
  `none`: a plan-phase panel grades a specification, not code (DEC-207), so INV-6 demands no pin.
- budget: cycles_used 1 / 10 · runs 9 / 20
- c1 shape: BRIEF REQ-01..REQ-05, SC-01..SC-09; plan D-01..D-05, T-01..T-06, all `ready`, DAG
  T-01 [] · T-02 [] · T-03 [T-01,T-02] · T-04 [T-03] · T-05 [T-03] · T-06 [T-05].
- runs this cycle: `2026-09-07-01-product` (the interrupted c1 replan, closed BLOCKED — its
  artifacts landed, no return was ever collected), `2026-09-07-01-validator` (advisor consult,
  3 binding rulings), `2026-09-07-02-product` (goal-check c1, PASS), `2026-09-07-02-validator`
  (plan panel c1, PASS — severity_max med, no gating finding, must_fix []), `2026-09-07-03-product`
  (repair of V-1 and S-2, panel transcription), `2026-09-07-03-validator` (advisor ruling on panel
  currency). The one cycle counted is the host-loss re-dispatch that run 01-product records.

**HANDOFF — this section IS the seam note. `notes/handoff-plan.md` could NOT be written; the
defect is measured below and unchanged since the c0 attempt.**

- NEXT: the main session runs ONE batched signature review over the 19 rows in plan.yaml
  `panel.findings` — four remain `open` (L-1, S-1, S-3, S-4; all info/low wording judgements, each
  ruled ride-not-repair) — then signs BOTH fragments: `plan-merge.py sign-approval --file
  <plan.yaml> --by <name> --date <YYYY-MM-DD>` plus `## Approval` in BRIEF.md. Build then opens
  with T-01 and T-02 together to `harness-eng-lead` via the `build` team (both `depends_on: []`,
  different files, the test-first pair T-03 needs); then T-03; then T-04 and T-05 (independent of
  each other); then T-06.
- TRUST, each with its evidence, all verified at c6d6ee6e:
  - both approval fragments read `pending` and no agent wrote either — plan.yaml:3-4,
    BRIEF.md:153-157
  - the panel record is current at cycle 1, both readers `ran`, 19 findings, no high/critical/
    unrated — plan.yaml `panel:` (:109-293), `runs/2026-09-07-02-validator/digest.md`
  - the plan loads and every task routes to a granted lane — `check-plan-routes.py` prints
    OK T-01..T-06, `0 violation(s)`, exit 0
  - SC-09's first clause discriminates: `cmd_set_task_station` is a pure text splice that never
    calls `validate_plan_doc` (`_verify_spliced` is reached only from `apply`, plan-merge.py:796),
    so `gh-sync start-task` still reaches `_projected_for` (gh-sync.py:1246) after T-03 lands and
    exits 0 while unrepaired
  - the two suites SC-07 newly binds are green today, so binding them imports no pre-existing red
    — `tests/integration/test-factory-decompose.py` 163/163 exit 0;
    `tests/integration/test-check-state.py` exit 0, zero FAIL lines
  - the corpus floor is honest — 67 committed feature plans at af859ee8 (BUG-201 absent), 68 in
    this worktree — `git ls-tree -r --name-only af859ee8`
- DEAD ENDS for the next phase:
  - do not validate self-dependencies, cycles or ordering — the operator excluded all three —
    intake `## Out of scope`
  - do not add a second checker beside `check-plan-routes.py` — plan.yaml D-01
  - do not complete `lanes.rows`, do not re-argue T-03/T-06's `team` lane, do not re-argue
    `_projected_for`'s exit 2 — three binding advisor rulings,
    `runs/2026-09-07-01-validator/digest.md`
  - do not re-run the panel over the two pre-signature repairs — binding ruling Q-ADV-4,
    `runs/2026-09-07-03-validator/digest.md`
- WORKING SET: `plan.yaml`, `BRIEF.md`,
  `notes/research-BUG-201-depends-on-integrity-goalcheck-plan-c1.md`,
  `runs/2026-09-07-02-validator/digest.md`, `.claude/skills/harness/bin/harness_yaml.py`

**HARNESS DEFECT, re-measured today, twice.** `notes/handoff-plan.md` cannot be written for a
feature that exists only in a worktree. `check-domain.sh`'s shape rel (`:1141-1149`) asks
`harness_boundary.checkout_relative` for the checkout-relative path and returns `_ck[1]` while
DISCARDING `_ck[0]`, the worktree root; the caller then passes that stripped rel with the MAIN
`root` into `handoff_done_when.problems` (`:1748`). Every authority type resolves through that
base, so no pointer can pass. Measured with one note body: worktree root -> `[]`, main root ->
both pointers unresolved, and the live guard refused the Write with exactly those two lines. Fix:
carry `_ck[0]` and pass it as the root for the handoff check. Not worked around — a pointer
rewritten to satisfy the gate would dangle for every reader after the merge.

## Open Questions

- Q-D (non-blocking, harness owner): the handoff-note defect above. It is a harness change, not a
  BUG-201 change.
- Q-E (non-blocking, dev-ops chore): `plan-merge.py` has no write route to the top-level `lanes`
  key (`AMENDABLE_KEYS == ("tasks","decisions")`, plan-merge.py:1232; `apply` exits 7 CONFLICT), so
  `factory_claim.py` and `gh-sync.py` cannot be listed in `lanes.rows` even though T-06 edits them.
  The 2026-09-07 advisor ruling settles this plan: signable as it stands, lane fact carried by
  D-03's `because`.
- Q-F (non-blocking, at signature): four panel findings ride into the batched review — L-1, S-1,
  S-3, S-4. Each is a wording judgement the advisor ruled ride-not-repair; signing accepts them.
- Q-G (non-blocking, build-time): whether `test-factory-decompose.py` and `test-check-state.py`
  would actually redden under a T-03 regression is unopened — the same adequacy limit the panel
  recorded for the four suites already bound. qa's real run answers it.
