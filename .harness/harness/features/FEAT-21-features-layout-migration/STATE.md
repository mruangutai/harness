# STATE

## Current

- feature: FEAT-21-features-layout-migration
- phase: validate — qa gate passed, goal-check found one criterion unmet, panel still owed
- run: .harness/harness/features/FEAT-21-features-layout-migration/runs/2026-08-14-2-goalcheck-product/
- squad: product
- status: awaiting-user

THE FEATURE MET ITS GOAL ON 13 OF 14 CRITERIA AND THE ONE MISS IS REAL. SC-10 is unmet by mutation
proof: `test-layout-migration.py`'s `_inv27_text` (:346) is a hand-written MIRROR of check-state.sh's
INV-27 composition — the comment at :347 says "mirrored" in the file's own words — so the parity
test binds the module side only. Dropping a blamed reader inside check-state.sh leaves case 20 at
zero failures. I confirmed the premise at source myself before treating it as a cycle. The test that
exists proves layout_migration against a copy of check-state.sh, not against check-state.sh.

THE BLOCKING GATE PASSED HONESTLY. qa returned PASS with no must-fix at 5c39f8c, unit 97 and
integration 89, and it earned the verdict rather than relaying it: the `test_matrix` FLOOR for this
diff is `unit` only, and `unit` executes none of the three suites that bind T-03/T-04/T-05 — they
are all in INTEGRATION_SCRIPTS. qa added `integration` under the floor-not-ceiling clause and ran
it. A future gate run that takes the floor literally passes while binding nothing.

THE REMEDY COLLIDES WITH A SIGNED CRITERION, WHICH IS WHY THIS STOPS HERE. SC-12 requires that
everything beyond this feature's planning record land in EXACTLY TWO commits, and it is met today
(5afa7e3, d033b9d). Any fix for SC-10 is a third commit. So the two criteria cannot both hold once
SC-10 is found unmet, and choosing which gives way is the operator's, not mine — I never mark, waive
or edit a criterion. My recommendation is on the record in my return: SC-12's PURPOSE (no
intermediate state for a gate to miss) survives a third commit that lands after the atomic cluster,
while SC-10's purpose dies if unfixed — the seam it guards diverged twice on 2026-08-14.

THE LANE FOR THAT FIX IS LAYER 0, AND THE GUARD DOES NOT SETTLE IT. `check-domain.sh --resolve`
grants all three candidate files to backend-dev and dev-ops, so the hook would ALLOW a squad. The
DEC-174 carve-out forbids it anyway: check-state.sh is named in CLAUDE.md and layout_migration.py is
a carve-out by content. Policy over grant, applied by judgement.

cycles_used is 3 of 10 and runs 5 of 20 — no crossing. The 3 counts the pre-commit panel's FAIL that
was routed back and fixed inside the cluster. An SC-10 re-dispatch would make it 4.

STILL OWED, in this order once the operator rules: the review panel at the final tree (it has never
run at a correct pin, and the D-08 label fix in d033b9d has had no second reader), then the briefing.
DOCS ARE DELIBERATELY UNTOUCHED AND THAT IS NOT AN OMISSION — SC-11 requires it, `docs/harness/**`
moves in unit 4, and editing it here would flip the docs surface to MIXED and redden INV-27. No
codebase map exists, so ship-refresh has nothing to refresh; distillation still applies.

## Open Questions

- Q-G (BLOCKING, the operator's): SC-10 unmet versus SC-12 met. Fix the parity test in a third
  commit and have pm re-word SC-12 under signature, or ship with SC-10 recorded unmet? Two further
  items ride the same decision, because each also needs that third commit: qa's one fixture edit to
  test-check-state.py and test-check-plan-routes.py — which closes the two-segment gap, pins D-08's
  delivery half, and adds the segment-level readability guard in a single change — and whether
  check-state.sh gains the zero-discovery guard check-plan-routes already has in CI.
- Q-H (qa's finding, no gate covers it): D-08's two halves are asymmetric. Neutering `fpath()` on a
  scratch copy leaves test-check-state.py at exit 0 — the delivery half is correct today and pinned
  by nothing — while violating the deferral half reddens seven INV-26 cases. The half that was
  previously missed is the half still untested.
- Q-C (harness defect, owner's): `bash-write-guard.sh` refuses any plan `verify:` clause redirecting
  into a `mktemp` file; it cannot resolve shell variables and named the target as the literal `xx`.
- Q-E (Expertise hygiene, needs a ruling): `.harness/expertise/harness-pm.md:7` was path-corrected
  inside this feature's commit — content-wise a re-anchor, not a lesson, but still a mid-run write to
  an injected file, on a branch, with no lineage protection.
- Q-F (recorded, not repaired): three FEAT-20 `hygiene-c3` notes were untracked before this feature
  and rode into d033b9d.
- Panel and qa advisories for the briefing: nothing exercises two repository segments;
  branch-create-gate's segment is hardcoded rather than derived; the walk-up probes team-config.yaml
  where T-10's intent named harness.json and no test discriminates; 181 of 186 cases are
  un-mutation-probed, so green cannot distinguish broad coverage from narrow.
