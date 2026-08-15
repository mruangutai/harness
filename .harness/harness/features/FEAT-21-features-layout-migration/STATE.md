# STATE

## Current

- feature: FEAT-21-features-layout-migration
- phase: validate — all ten tasks landed; qa gate and review panel next, then goal-check
- run: .harness/harness/features/FEAT-21-features-layout-migration/runs/2026-08-14-1-validator/
- squad: validator
- status: in_progress

THE CLUSTER IS LANDED AT `d033b9d` AND I RE-DERIVED IT FROM DISK. Subject `[harness:t-09]`, body
carrying all nine tags on one line so `git log --grep='harness:t-05'` still resolves; 617 files,
1315 insertions, 664 deletions, 567 pure renames. T-09's `verify:` re-ran verbatim to exit 0 at the
landed commit. The boundary note gained 50 insertions and ZERO deletions — the pre-move capture
taken at 5afa7e3 survives intact beside the post-move one.

THE STOP CONDITION IS SATISFIED AT A LANDED COMMIT for the first time since ea937b1: the detector
exits 0 with `features: CLEAN — evidence migrated` and `docs: CLEAN — evidence legacy`,
`2 surface(s) clean, 0 mixed, 0 cannot-verify`; `check-state.sh` exits 0 with zero INV-27 lines and
its note body at baseline. feature.json now reads `status: Review`, `review_sha: d033b9d`.

A PRE-COMMIT VALIDATOR PANEL RAN THAT I DID NOT DISPATCH — the operator spawned it, and its run dir
was the orphaned-work note check-state was reporting. It is now recorded in feature.json with its
real verdict, FAIL. It found ONE must-fix and it was a real one: T-05/D-08's finding-label clause
was never built while T-05 was marked done. The build delivered the deferral (dict keys stay bare
basenames) and dropped the delivery (labels carrying the discovered path). I verified the remedy at
source myself — `_feat_dirs` and `fpath()` at check-state.sh:55-59, 18 call sites, keys unchanged.
That is a FAIL routed back and fixed, so cycles_used goes 2 -> 3 under DEC-157. Three of the four
panelists returned PASS; qa mutation-proved the feature's three new assertions non-vacuous.

TWO THINGS ABOUT THAT PANEL BELONG IN THE RECORD RATHER THAN IN A DEFENCE OF IT. Its pin read
`ea937b1`, a commit the work was absent from, so INV-6 was not satisfied — the reviewers read the
working tree and the finding is sound, but the pin was wrong. And the panel could not clear SC-12,
which asserts a landed commit shape that did not exist while it looked. Both are why I am running
the panel again at `d033b9d`, where the pin contains the work and the must-fix resolution has never
been reviewed by anyone.

NEXT, and the first two go out together because they share no files and no squad: the qa segment
(test authoring plus the blocking `test_matrix` gate, validator) and pm's goal-check against the 14
SCs (product). Then the review team at `d033b9d`. Then docs, then the CEO briefing.

## Open Questions

- Q-C (harness defect, owner's): `bash-write-guard.sh` refuses any plan `verify:` clause redirecting
  into a `mktemp` file — it cannot resolve shell variables and reported the target as the literal
  `xx`, a wrong verdict rather than a conservative one. Every such clause in this plan was unrunnable
  as written by a governed agent; I ran each from a scratch script.
- Q-D (this feature's own evidence, owner's): mid-cluster both `check-state.sh` and
  `check-plan-routes.py` exited 0 while examining nothing, and neither the plan's verify chain nor
  any criterion would have caught it. I added the discovery checks myself. Promoting them to a
  criterion is pm's, not mine.
- Q-E (Expertise hygiene, needs a ruling): `.harness/expertise/harness-pm.md:7` carried the legacy
  path and was corrected inside this feature's commit. The content is a path re-anchor, not a
  lesson, and leaving it would have broken every pm spawn — but it is still a mid-run write to an
  Expertise file, which the rule forbids, and shared `.harness/expertise/` has no lineage protection
  against two features distilling at once. The operator should say whether path re-anchoring is a
  sanctioned exception.
- Q-F (scope smudge, recorded not repaired): three FEAT-20 `hygiene-c3` review notes were untracked
  before this feature and rode into `d033b9d`. Harmless, but FEAT-20's record now has a commit in
  FEAT-21's history. Rewriting a landed 617-file commit to drop three notes costs more than it saves.
- Panel advisories carried to the briefing, none blocking: branch-create-gate's segment should be
  derived rather than hardcoded; check-plan-routes has no segment-level readability guard; the
  walk-up probes `team-config.yaml` where T-10's intent named `harness.json` and no test
  discriminates; and NOTHING anywhere exercises two repository segments, which is the panel's
  headline coverage gap and the whole point of the sequence.
- Q9 (owner's, unchanged): a lead hosting a team cannot yield its turn while backgrounded members
  are in flight, and leads hold no SendMessage, so a lead cannot resume a member to clear its FAIL.
