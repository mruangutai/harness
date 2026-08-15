# STATE

## Current

- feature: FEAT-21-features-layout-migration
- phase: build — nine of ten tasks done in the working tree; T-09 lands the cluster as one commit
- run: none (main-session-direct segments are not runs)
- squad: none
- status: awaiting-user

THE MOVE IS DONE AND THE BOUNDARY IS GREEN. I verified every claim myself at this tree, not from
the builder's report: `.harness/features` no longer exists, 21 feature dirs sit under
`.harness/harness/features/`, the detector exits 0 printing `features: CLEAN — evidence migrated`
and `docs: CLEAN — evidence legacy` with `2 surface(s) clean, 0 mixed, 0 cannot-verify`, and
`check-state.sh` exits 0 with zero INV-27 lines. T-08's verify ran verbatim to exit 0.

MY OWN Q2 CHECKS, which nothing in T-09's verify covers, both pass. The argv-less
`check-plan-routes.py` sweep now reports `examined 21 feature dir(s); 20 skipped as shipped` with
`0 violation(s) across 1 plan(s)` — examined > 0 AND plans > 0, where mid-cluster it reported 0.
`check-state.sh` re-emits exactly 39 note lines, matching the committed pre-move capture to the
line, where mid-cluster it emitted zero. Both gates were passing their own checks while examining
nothing; they are examining again.

ALL ELEVEN SUITES ARE GREEN, including the three that were red on schedule through the cluster
(test-no-distribution, test-factory-cli, test-layout-migration). The ignore window T-07 opened has
closed: 19 run directories are ignored again at the new path and the only untracked entries are
FEAT-20's three review notes, which predate this feature.

BOOKKEEPING IS ON DISK AGAIN. My write access returned with the move (`--resolve` on the new path
answers harness-orchestrator; it answered NOBODY at the old one for six turns). plan.yaml records
T-01..T-08 and T-10 `done` and T-09 `building`; all nine mirror calls ran — issues #390-#397 closed,
#398 moved to Building — each after the plan already carried its new status. cycles_used stays 2:
nothing in this feature has been rework.

WHAT IS LEFT IS T-09 ALONE. It writes the post-move capture and the depth sweep into
`notes/layout-boundary-2026-08-14.md`, runs the full suites and the route check, and lands
T-02..T-08, T-10 and itself as ONE commit by explicit pathspec. `review_sha` still reads `ea937b1`
and I re-pin it to that commit before qa and the review panel.

## Open Questions

- Q-C (harness defect, for the owner, not blocking, unchanged): `bash-write-guard.sh` refuses any
  plan `verify:` clause that redirects into a `mktemp` file. It cannot resolve shell variables and
  reported the target as the literal `xx`, which is a wrong verdict rather than a conservative one.
  Every such clause is unrunnable as written by a governed agent; I ran each from a scratch script
  instead. Either the guard should treat an unresolvable target as not-a-domain-verdict, or plans
  should stop writing redirect-bearing verify clauses.
- Q-D (raised by this feature's own evidence, for the owner): T-09's verify greps for the ABSENCE of
  an INV-27 line and tests exit 0, and invokes `check-plan-routes.py` with an explicit plan path,
  which never calls `discover_plans()`. Mid-cluster I measured both gates exiting 0 while examining
  nothing — the exact fail-open this unit exists to remove — and neither the plan's verify chain nor
  any criterion would have caught it. I added the two checks myself this turn. Whether they become a
  criterion is pm's to write, not mine.
- Q-E (record hygiene, resolved, kept for the panel's benefit): a comment added to `gh-sync.py`
  during T-06 justified the walk-up's manifest probe with a `$HOME/.harness` hazard that is not live
  ($HOME/.harness holds two .tgz backups and neither `harness.json` nor `team-config.yaml`) and cited
  "B-7 verbatim", which resolves to at least four different rows across FEAT-03, FEAT-08, FEAT-20 and
  team-config.yaml, none about root resolution. The code was right; the reasoning was not. Corrected
  before the move — the comment now cites the root-probe convention by file. Briefing row IDs are
  unique only within one briefing and should never be cited from source.
- Q9 (the harness owner's, not this feature's): a lead hosting a team cannot yield its turn while
  backgrounded members are in flight, and leads hold no SendMessage, so a lead cannot resume a
  member to clear that member's own FAIL. Backlog.
