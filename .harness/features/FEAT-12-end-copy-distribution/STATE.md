# STATE

## Current

- feature: FEAT-12-end-copy-distribution
- run: .harness/features/FEAT-12-end-copy-distribution/runs/2026-08-10-03-product/state.yaml
- squad: product
- status: awaiting-user

The operator's answers are folded in. BRIEF.md and plan.yaml are on disk, both `pending`, and
**ready for his signature**. 8 REQs, 11 SCs, 14 tasks, 6 decisions — recounted by me at the settled
tree. No blocking question remains. The plan phase ends at the signature, which is the main
session's to write.

Both required fixes landed and I verified each against the files, not against the report: the kaya
agent-count basis is corrected everywhere it appeared, and Q8's SHARP EDGE sites are folded into
T-11 with a verify that fails today for the right reason (exit 1, both comment lines still present).

Three things the operator has not yet seen, all measured, all recorded in the artifacts he signs:
kaya's `settings.json` wires **eight** harness registrations across four hook events where the plan
said three — the four it missed are the ones a Task spawn fires, which is exactly what SC-06's
blocking UAT exercises; `.claude/settings.json.harness-bak` is tracked **on the remote** and wires
six of them, now declared as D-06's deferral; and REQ-03 was narrowed away from kaya's worktree
branches, which carry 153 tracked harness skill files that nothing in this feature reaches.

## Open Questions

- Q1 (non-blocking, ratify at signature): REQ-03 was NARROWED to kaya's three top-level tooling
  directories, and the BRIEF's Goal was reconciled to match. Measured by me: three of kaya's six
  worktree branches carry tracked harness copies — `feat/333-env-test` 55 skills + 8 commands,
  `feat/120-statements-page` 48 skills, `feat/48-live-review-loop` 50 skills, 153 skill files in
  total. `master` tracks nothing under `.claude/worktrees/` and the directory is gitignored at
  `.gitignore:23`, so those copies never enter this feature's commit and never reach a factory
  checkout. Each branch drops its copy the next time it takes `master`. I measured the one thing
  that could make "self-clearing" false: `git log master..<branch> -- .claude/skills/harness
  .claude/commands/harness` returns **0 commits for all three**, so none of them carries its own
  change to those paths and the next master merge deletes cleanly rather than raising a
  modify/delete conflict. The deferral is transient, not three deferred conflicts. Signing the
  BRIEF ratifies the narrowing.
- Q2 (non-blocking, ratify at signature): D-06 defers `.claude/settings.json.harness-bak` rather
  than removing it. It is tracked on `origin/master` and names six harness scripts that will no
  longer exist. It is inert for SC-06 — `merge-settings.py` writes it and never reads it back — so
  nothing breaks; but kaya's `master` keeps one tracked file pointing at deleted paths. Reversal
  costs one path on T-03 and one entry on T-05's pathspec.
- Q3 (non-blocking, for the operator's awareness): the checkout moved during the run. #213 MERGED
  as `1e5f55d` at 16:25:38Z — his own action, untouched by this chain — and the working tree now
  sits on `feat/FEAT-11-graphql-field-resolve` at `8dedeae`, switched by another chain. `365a8a9`
  is an ancestor of HEAD, so the baseline moved forward and never diverged. FEAT-12's feature
  directory is entirely untracked, so nothing of this feature has been committed onto FEAT-11's
  branch. It needs a branch of its own before anything is committed.
- Q4 (non-blocking, a HARNESS DEFECT, not this feature's): `check-domain.sh` blocked pm from
  writing the receipt path its own dispatch named. `harness-pm`'s permitted notes paths are
  `notes/research-*.md` and `notes/uat-*.md`, while `harness-handoff/SKILL.md` instructs every
  member to write `notes/receipt-<agent>-<runid>.md`. The skill and the team-config grant
  contradict each other; pm raised it rather than working around it. Every member that follows the
  handoff skill literally will hit this.
