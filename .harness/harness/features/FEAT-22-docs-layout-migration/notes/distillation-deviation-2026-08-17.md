# Deviation — the distillation record overstated, and one lesson was lost

Recorded 2026-08-17 on the operator's ruling, after the two verify-only reconstruction runs.

Commit `1f4124e` claims "Twenty-five entries added, none lost." **That is false at entry
granularity.** Measured across all ten files: **31 added, 6 removed, net 25.** The no-wipe check
that produced the claim was correct at FILE granularity; the commit message restated it at ENTRY
granularity, which is an unforced widening in a durable record. Four of the six retired a
materially different rule rather than a reworded one. Half the displacements were NOT cap-forced
(validator-lead at 12/15, visual-designer at 6/15), so a curation policy aimed only at full
sections would miss two of the six.

**The concrete casualty, recovered here so the lesson is not lost to git archaeology.** The pm's
retired G-06 read:

> G-06: A sibling worktree under `.claude/worktrees/` is a full second copy inside the search path:
> `.gitignore` hides it from `git grep` but not `grep -r`, and the same path resolves to different
> content there with no error. Confirm which checkout resolved any file:line you cite.

That hazard now exists nowhere in the tree. It is the same failure class this session hit twice
(the stale-checkout diagnostic, and the swept-renames incident at T-09). **Restoring it needs a
displacement in a section already at 15/15, which is the file owner's call during a distillation —
not a main-session edit.** Backlog row, not a silent fix.
