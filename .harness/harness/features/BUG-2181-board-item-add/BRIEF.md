# BRIEF — BUG-2181 Board item addition

## Problem

Mirroring an issue absent from its configured project fails with "issue carries no item" rather than placing its card. Kaya recover-mirror encountered this on 2026-11-07; operators currently depend on Auto-add to project or manual addition.

## Done when — by perspective

**operator** — I can mirror an issue onto its configured board and station without enabling Auto-add to project. Existing cards are not added again, and board failures remain visible through the existing failure handling.

**code maintainer** — I can rely on regression coverage for missing and existing cards and for lookup, addition and station-write failures, without changing each caller independently. Provisioning guidance explains the behavior accurately.

## Success criteria

- SC-01 (operator): A fake-gh gh-sync station write for an issue absent from the configured project adds that issue exactly once before setting its station using the returned item id; a present item is set without item-add. QA demonstrates the absent-item assertion failing against pre-fix production code and passing after the fix.
  verify: automated evidence: integration
- SC-02 (code maintainer): Direct set_station tests prove lookup precedes guarded addition, the canonical issue URL and configured owner/number are passed, the returned or existing id reaches the station field write, and GhError at each of lookup/add/set becomes BoardError naming the requested issue and lowercase station. QA demonstrates the new absent-item assertion failing before and passing after the fix; existing-item and failure cases pass after it.
  verify: automated evidence: unit
- SC-03 (code maintainer): At the pinned review_sha, git show <review_sha>:.claude/skills/harness/references/repo-board-provisioning.md explains gh-sync adds missing cards itself and Auto-add to project is not required, without changing the three existing registration workflow requirements. Reviewer cites the pinned file and paragraph.
  verify: inspection

## Verification gaps

None for SC-01/SC-02: unit and integration are active with runnable commands. Fake-gh coverage does not prove live GitHub credentials or service availability. Functional is excluded under DEC-187; no SC rests on it. No operator UAT is required.

## Constraints

- The authoritative .harness/notes/grilling-board-item-add-2026-11-08.md supplies the settled behavior: guarded project_item_add inside gh_board.set_station for every caller; an existing item is never re-added; GhError remains BoardError.
- DEC-174 BLOCKS team build execution: main session builds in the assigned feature worktree; harness-validator-lead owns validation.
- DEC-225 SUPPLIES the patch lane: one task, no panel or goal-check, pending approval before build.
- PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in the assigned checkout. No guidance is inferred from them; the explicit grilling settlement supplies this bounded contract.
- Provisioning reference note only; no audit or gate changes.

## Out of scope

- factory_decompose.py's own guarded add path; board_lifecycle.py audit workflow findings; registration gate changes — excluded by the settled intake.
- Retroactive Kaya items — already added by hand on 2026-11-07, as recorded in the BUG-20261006 T-05 note.

## Approval

status: approved
approved-by: operator
date: 2026-11-08
