# STATE

## Current

- feature: FEAT-21-features-layout-migration
- phase: validate — one fix cycle open on SC-10, then the panel, then the briefing
- run: .harness/harness/features/FEAT-21-features-layout-migration/runs/2026-08-14-2-goalcheck-product/
- squad: none (the fix is main-session-direct)
- status: awaiting-user

THE GOAL-CHECK MET 13 OF 14 AND SC-10 IS UNMET ON MUTATION PROOF. `test-layout-migration.py`'s
`_inv27_text` (:346) is a hand-written MIRROR of check-state.sh's INV-27 composition — the file says
"mirrored" in its own comment — so the parity test binds the module side only. Dropping a blamed
reader inside check-state.sh leaves case 20 at zero failures, and the mutation is proven to have
applied because it reddened test-check-state.py case x.2. I confirmed the premise at source before
spending a cycle. The test proves layout_migration against a COPY of check-state.sh, not against
check-state.sh. That is the exact seam issue #387 exists to pin and it diverged twice on 2026-08-14.

THE BLOCKING QA GATE PASSED AND EARNED IT. `matrix_ok: true` at 5c39f8c, unit 97 and integration 89,
no must-fix. The floor for this diff is `unit` alone, which executes NONE of the three suites that
bind T-03/T-04/T-05 — they sit in INTEGRATION_SCRIPTS. qa added `integration` under the
floor-not-ceiling clause and ran it, so the verdict rests on that addition, not on the floor.

SC-12 AND SC-10 CANNOT BOTH HOLD, AND I AM NOT EDITING EITHER. SC-12 requires everything beyond the
planning record to land in exactly two commits; it is MET today at 5afa7e3 and d033b9d. Any SC-10
remedy is a third commit. Settled under the operator's standing authorization, which covers code on
a feature branch and expressly does not cover signed artifacts: FIX SC-10, TOUCH NO CRITERION, and
record the consequence for the operator to ratify at the briefing. The record reads: SC-12 met at
d033b9d; the fix commit takes the range to three; unmet-as-written thereafter; its PURPOSE intact,
because the cluster still landed atomically and the third commit is post-cluster and additive. Only
the operator may re-word SC-12, and pm drafts that only if he says amend.

THE LANE IS LAYER 0, AND THE GUARD DOES NOT SETTLE IT. `check-domain.sh --resolve` grants
test-layout-migration.py, layout_migration.py and check-state.sh to backend-dev and dev-ops, so the
hook would ALLOW a squad. The DEC-174 carve-out forbids it anyway — check-state.sh by name in
CLAUDE.md, layout_migration.py by content. Policy over grant, applied by judgement, and pm reached
the same conclusion independently.

SCOPE OF THE THIRD COMMIT IS SC-10 ONLY. qa's fixture edit, the check-state zero-discovery guard and
pm's SC-06 regression case are all emergent — no criterion requires them — so they are briefing rows
with my recommendation, not scope I adopt. One deviation, minimal blast radius.

cycles_used is 4 of 10 (this dispatch is the fourth rework), runs 5 of 20. No crossing.

STILL OWED: the SC-10 fix, then the review panel at the final pin — it has never run at a pin that
contains the work, and d033b9d's D-08 label fix has had no second reader — plus a narrow SC-10
re-check by pm, then distillation, then the briefing. Docs stay untouched because SC-11 requires it;
ship-refresh is a skip because no codebase map exists.

## Open Questions

- Q-H (qa's, no gate covers it): D-08's halves are asymmetric. Neutering `fpath()` leaves
  test-check-state.py at exit 0 — the delivery half is correct and pinned by nothing — while
  violating the deferral half reddens seven INV-26 cases. The half previously missed is the half
  still untested. Briefing row.
- Q-C (harness defect, owner's): `bash-write-guard.sh` refuses any plan `verify:` clause redirecting
  into a `mktemp` file; it cannot resolve shell variables and named the target as the literal `xx`.
- Q-E (Expertise hygiene, needs a ruling): `.harness/expertise/harness-pm.md:7` was path-corrected
  inside this feature's commit — a re-anchor, not a lesson, but still a mid-run write to an injected
  file on a branch with no lineage protection.
- Q-F (recorded, not repaired): three FEAT-20 `hygiene-c3` notes were untracked before this feature
  and rode into d033b9d.
- Criterion-wording drifts pm reported without rewriting: SC-02's post-move capture cannot name the
  commit it lands in; SC-06 declares evidence kind `unit` where the pinning suite is registered
  `integration`; SC-05 declares `integration` where its establishing check is T-08's plan verify.
- Advisories for the briefing: nothing exercises two repository segments; branch-create-gate's
  segment is hardcoded rather than derived; the walk-up probes team-config.yaml where T-10's intent
  named harness.json and no test discriminates; 181 of 186 cases are un-mutation-probed.
