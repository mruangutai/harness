# STATE

## Current

- feature: BUG-148-gate-record-correction
- run: .harness/harness/features/BUG-148-gate-record-correction/runs/2026-09-07-02-product/digest.md
- squad: none — ship phase, all six SCs met, briefing written
- status: ship — goal-check PASS, awaiting merge
- station: `plan.yaml` `status: review` → `done` written at ship
- review_sha: re-pinned to the ship-evidence commit (see below). `cycles_used` **5** of 10;
  `len(runs)` **11** of 20 — both under budget, nothing to surface.

**SC-06 is closed and the whole feature is met.** pm's delivery goal-check
(`notes/research-BUG-148-goalcheck-delivery-c5.md`, run `2026-09-07-02-product`, PASS, 0 send-backs)
graded SC-01..SC-06 at `651e60e2` by each criterion's own `verify:` method: **all six met**. SC-04's
runner exited **0** with **zero** `^FAIL ` lines and both named index tests `ok`. SC-01/SC-02 were
graded clause-by-clause, not by a file-global grep.

**SC-06's attribution is split, and the record says so** (`notes/uat-BUG-148-sc06-c5.md`). The
OPERATOR read FEAT-05's `STATE.md` passage and the *superseded, longer* DEC-174 paragraph at cycle 4;
he accepted the facts and sent back only the length. `fable-advisor`, under his standing
authorisation, read the **shortened** paragraph at cycle 5 and ruled PASS. The operator's own eyes
have never been on the text now in the authority. That is stated, not smoothed.

**The reviewer panel's PASS graded `87e6033`, not the current bytes — ruled shippable.** The
cycle-5 wording fix moved the product diff off the sha the panel graded, so no panel run has ever
read the shortened paragraph. Referred to `fable-advisor` as a binding non-external call; ruling:
**ship on the current record, no panel re-run**, on the ground that the only evidence gap at the
current pin is *prose truth*, which the panel by its own adequacy note could never grade and which
SC-06 owns. The split is stated plainly in the ship briefing rather than papered over.

**Post-pin commits carry no product byte.** `git diff 651e60e2..HEAD` over the three product paths
(`DECISIONS.md`, `DECISIONS-INDEX.md`, FEAT-05 `STATE.md`) is **empty**; every post-pin commit lands
inside this feature's own directory, which SC-05 allows explicitly. Re-pinning to the ship-evidence
commit is therefore free, and it satisfies pin-precedes-station before the `done` write.

**The validator-digest repair is recorded.** qa's six-command verification was committed as
`notes/qa-digest-repair-verification-2026-09-07.md`, renamed from `review-harness-qa-c1.md` whose
`c1` suffix implied a second review cycle that never ran. Per the advisor: discarding it would
recreate the missing-evidence-trail hazard the panel flagged.

## Open Questions

- Q1 (RESOLVED at rung 1): SIMPLIFY's altitude angle asked whether FEAT-05 `STATE.md`'s bold
  `Corrected 2026-09-06 under BUG-148:` lead-in narrates where DEC-174 states. Premise fails —
  D-05 ruling 1's "treatment" is the in-place mechanism, not the rhetorical register, and REQ-01
  positively requires the FEAT-05 record to name the date. Carried into SC-06 and cleared there.
- Q2 (non-blocking, harness defect, briefing row B-3): DEC-153's disposable-worktree perturbation
  carve-out is unreachable for `harness-qa` on any non-`tests/**` path — both guards deny, and a
  self-created sibling worktree is refused under DEC-218 claim binding.
- Q3 (non-blocking, harness defect, briefing row B-4): `harness-digest-dev` forbids `suite: n/a`
  with `VERDICT: PASS` (DEC-173), but a read-only reviewer dispatch runs no suite, so an honest
  reader has no legal value.
- Q4 (non-blocking, briefing row B-2): of SC-04's two named tests only
  `test_committed_index_matches_a_fresh_regeneration` was proven red-capable;
  `test_no_amendment_construct_survives_in_the_authority` was observed green, never perturbed. Both
  edits are in-place rewrites per D-01, so this diff cannot newly violate the property.
- Q5 (non-blocking, the main session's act): the untracked source copy of the grilling artifact
  under `.harness/harness/notes/` was removed on purpose and MUST NOT be restored.
- Q6 (non-blocking, harness defect, briefing row B-5): `handoff_done_when.py::_feature_dir` cannot
  resolve `brief-sc:` or `plan-task:` pointers for a feature whose directory lives only in a
  worktree — it strips the `.claude/worktrees/<name>/` prefix and rejoins to the MAIN checkout root.
  Both handoff notes cite `finding:` and `approval:` pointers instead.
- Q7 (non-blocking, gap in this BRIEF, briefing row B-1): REQ-04's `no historical artifact is
  modified` had no criterion grading it. It holds on the SC-05 measurement, but a future BRIEF of
  this shape should state it as its own SC.
- Q8 (non-blocking, harness defect, briefing row B-6): the QA subagent wrapper's return path
  (`yield` with null data → exit 1 → re-emit). Advisor: orthogonal platform defect, worst unfixed
  consequence a spurious re-dispatch, not record corruption. File separately; do not delay ship.
- Panel findings `PF-a2df57f48de3e81d49745cfd1adaa20b` (med, accepted-by-design, disclosed in
  BRIEF's Verification gaps) and `PF-b7b07ec7b7f6cacb3b894cae4bda2a04` (low, informational) remain
  open by design; neither was ruled on and neither gates.
