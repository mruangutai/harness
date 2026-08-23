# FEAT-26 plan seam — the plan is signed, the build has not started

Written by the main session at the signature, reconstructed from disk. The orchestrator that
ran the plan flow on 2026-08-18 is gone and left no note; this records what a successor needs.

## Next
Run `/harness-ship FEAT-26-pr-linkage-recorded`. Before any orchestrator is spawned:
1. The worktree at `.claude/worktrees/harness/FEAT-26` sits at `198b024` and `main` is at
   `69d74ec`. Run the `feature-worktree.py behind` check and merge `main` in — it is far
   behind, and the gap holds FEAT-31, FEAT-32 and both layout migrations.
2. `review_sha` still pins `ada8e99`, which is stale. Ship re-pins it after the build.
3. `feature.json` says `branch: none` while the worktree is on `feat/FEAT-26`. Ship's step 0b
   reconciles this.

## Trust
- **Q1 is ANSWERED and MEASURED, not assumed.** T-06 writes four PR numbers that attribution
  by branch cannot derive. Verified 2026-08-23: PR #4's merge commit `04a57fc` adds both
  `.harness/features/FEAT-01/` and `FEAT-02/`, and PR #15's title names FEAT-04 and FEAT-03
  outright. So FEAT-01 → 4, FEAT-02 → 4, FEAT-03 → 15, FEAT-04 → 15.
- The product squad returned PASS. Eight tasks, all specified. Lanes resolved at `8ad7d52`.
- The pre-build UI review ran and is on disk.

## Dead ends
- **Do not re-derive the four PR numbers from branch names.** That is what fails; the
  attribution is by PR title, and #4's title names neither feature it carries.
- **Q5 is a FALSE PREMISE that reached this feature's dispatch:** "check-state.sh carries 19
  invariants, the new one is the twentieth". At `ada8e99` the run is INV-1..INV-27, INV-20 is
  taken, and INV-10 is retired and unreusable. pm used INV-28 correctly. A successor that
  trusts the dispatch text instead of the file will collide.
- **Three questions stay non-blocking and are NOT the plan's to settle:** whether the harness
  opens its own PRs (contradicts DEC-153), whether ship closes source issues directly rather
  than rendering `Closes` lines (crosses DEC-196; D-04 takes render-only), and a feature-id
  collision that left an orphan `FEAT-25-expertise-repository-tier/` on disk.

## Working set
- `.claude/skills/harness/bin/gh-sync.py` — the two writers in this one file disagree today;
  issue #289 is absorbed because the fix lands inside a function this feature already edits.
- `.claude/skills/harness/bin/check-state.sh` and `test-check-state.py` — the new invariant.
- `.claude/skills/harness/bin/feature-schema.json`, `templates/plan.yaml`, `harness/SKILL.md`.
- Eleven historical `feature.json` files gain their `pr` value.
- `.harness/harness/docs/DECISIONS.md` and a regenerated `DECISIONS-INDEX.md`.

## Log
- BRIEF and plan both signed 2026-08-23 by the operator, after Q1 was measured rather than
  confirmed from memory. Status moved Plan → Ready.
- **This feature shares six files with FEAT-33**, including `DECISIONS.md`, its index and
  `gh-sync.py`. If both build in parallel, the second to merge pays a real conflict and must
  renumber its decision entry.
