# BRIEF — BUG-1725 task file overlap

## Problem

A drafted plan can assign the same file to multiple tasks without showing that overlap. The later task then changes the tree beneath an earlier task's gate, so planning misses a predictable source of cross-task regates and repeated build cycles.

## Done when — by perspective

**operator** — I can run the existing plan-exit check and see every file shared by multiple tasks together with those task ids, without making an otherwise legal overlapping plan fail.

**code maintainer** — I can rely on regression coverage for overlap detection across every supported anchor form, and on planning guidance that slices work by file ownership and calls shared files out during scope review.

## Success criteria

- SC-01 (operator): `plan-merge.py check` emits exactly one `OVERLAP <path>: <task ids>` advisory for each normalized file path named by at least two tasks, treating `path`, `path#symbol`, and `{path, quote}` anchors for the same path as one shared file; the integration test demonstrates the assertion failing before the fix and passing after it.
  verify: automated        evidence: integration
- SC-02 (operator): An overlap advisory alone does not change `plan-merge.py check`'s exit code, so a plan with shared files remains legal; the integration test demonstrates the exit-code assertion failing before the fix and passing after it.
  verify: automated        evidence: integration
- SC-03 (code maintainer): At the pinned `review_sha`, inspection of `git show <review_sha>:.agents/skills/harness-spec-driven/SKILL.md` confirms that tasks own their files, multi-file work is sliced by exclusive file ownership or kept as one task with a per-file checklist, layering over shared files is rejected, and a whole-tree verify belongs to the final touching task or validate.
  verify: inspection
- SC-04 (code maintainer): At the pinned `review_sha`, inspection of `git show <review_sha>:.agents/skills/harness/teams/plan.yaml` confirms that the scope reader asks which tasks share files and whose gate the later task will break, with an answer classified as a `substance` finding.
  verify: inspection

## Verification gaps

- none

## Constraints

- DEC-174 SUPPLIES the main-session-direct execution lane for `plan-merge.py` and its integration test; the two bounded prose edits remain in that same task.
- DEC-225 BLOCKS panel and goal-check work for this patch mission and requires one task in the plan.
- DEC-232 SUPPLIES the supported anchor forms and the existing plan-exit `plan-merge.py check` gate.
- Overlap reporting is advisory only; overlapping plans remain legal.

## Out of scope

- Changing cycle counting under DEC-157 or pinning a tree for a task's gate — a moving tree is part of build execution.
- Refusing overlapping plans — the new output is advisory.
- Re-slicing the shipped `BUG-285-canonical-reader` plan — this patch changes future detection and guidance only.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-15
