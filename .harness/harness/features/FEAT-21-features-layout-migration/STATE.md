# STATE

## Current

- feature: FEAT-21-features-layout-migration
- phase: validate — SC-10 fixed and proven; panel and the narrow SC re-check are the last gates
- run: none in flight at this write; panel and SC-10 re-check dispatching next
- squad: validator and product
- status: in_progress

SC-10'S FIX LANDED AT `b1d3925` AND I KILLED THE MUTANT MYSELF RATHER THAN ACCEPTING THE REPORT.
`_inv27_text` is gone — zero occurrences. The session-entry side is now the ACTUAL `check-state.sh`
run as a subprocess against a fixture tree (`test-layout-migration.py:343,358`), the CI side is
`render()` over `lm.scan()` of the same tree, and no composed expectation exists anywhere in the
test. My probe copied `bin/` to scratch, BASELINED it first (case 20: 10 assertions, 0 failures),
then dropped the blamed-reader clause from the scratch gate's MIXED branch and re-ran: case 20 goes
RED on `MIXED, one migrated reader on legacy evidence — real gate and render name the same reader
set`. The mutant that survived the mirror dies against the real gate. The live tree was never
touched — `git status` carries only the pre-existing held dirt.

Two honesty notes about that probe, because a mutation proof that lies is worse than none. The
scratch copy shows three case-1 failures at BASELINE: case 1 scans the real repository root, which a
copy outside the repo cannot see. That is a property of the scratch location, not of the fix, which
is exactly why I scoped the verdict to case 20's own assertions rather than to an exit code. And I
asserted the mutation applied before believing its result.

EVERYTHING ELSE IS GREEN AT THIS TREE: T-01's `verify:` exit 0 (it still governs this file and still
requires a `parity` label through the runner), unit and integration both exit 0, the detector exits
0 on `features: CLEAN — evidence migrated`, `check-state.sh` exits 0 with no INV-27 line.

THE SC-12 DEVIATION IS NOW REAL AND RECORDED, NOT PREDICTED. The feature stands at three commits
beyond its planning record — 5afa7e3, d033b9d, b1d3925 — where SC-12 asks for two. No criterion has
been edited and none will be by me. SC-12 was met at d033b9d and is unmet-as-written from b1d3925;
its PURPOSE survives, because the cluster still landed atomically and the third commit is
post-cluster and purely additive to a test. This is the briefing's top decision row and the operator
ratifies or amends it.

`review_sha` is pinned to `b1d3925`, the commit containing the code under review. cycles_used is 4
of 10, runs 5 of 20 — no crossing, and every run so far has resolved something.

LAST TWO GATES, dispatched together because they share no squad and no files: the review panel at
the correct pin — it has never run at one that contains the work, and both d033b9d's D-08 label fix
and b1d3925's SC-10 fix have had no second reader — and pm's narrow SC-10 re-verdict, because I
proved the behaviour but I never mark a criterion met. Then distillation, then the briefing. Docs
stay untouched because SC-11 requires it; ship-refresh is a skip because no codebase map exists.

## Open Questions

- Q-H (qa's, no gate covers it): D-08's halves are asymmetric — neutering `fpath()` leaves
  test-check-state.py at exit 0, so the delivery half is correct and pinned by nothing, while
  violating the deferral half reddens seven INV-26 cases. The half previously missed is the half
  still untested. Strongest briefing row.
- Q-C (harness defect, owner's): `bash-write-guard.sh` cannot resolve shell variables and denies on
  the unresolved text — it blocked a plan `verify:` redirecting to `mktemp` (target reported as the
  literal `xx`) and an `rm` on a scratch path (reported as `$M`). Both were legitimate; both had to
  be re-expressed as script files.
- Q-E (Expertise hygiene, needs a ruling): `.harness/expertise/harness-pm.md` was path-corrected
  inside d033b9d — a re-anchor rather than a lesson, but still a mid-run write to an injected file
  on a branch with no lineage protection.
- Q-F (recorded, not repaired): three FEAT-20 `hygiene-c3` notes were untracked before this feature
  and rode into d033b9d.
- Criterion-wording drifts pm reported and did not rewrite: SC-02's post-move capture cannot name
  the commit it lands in; SC-06 declares evidence kind `unit` where the pinning suite is registered
  `integration`; SC-05 declares `integration` where its establishing check is T-08's plan verify.
- Coverage advisories for the briefing: nothing exercises two repository segments; the SC-10 case
  covers six of seven cause paths because `no-rows` cannot be staged through a real tree without a
  table override — flag it if pm reads SC-10 as requiring all of them; branch-create-gate's segment
  is hardcoded rather than derived; the walk-up probes team-config.yaml where T-10's intent named
  harness.json and no test discriminates; 181 of 186 cases are un-mutation-probed.
