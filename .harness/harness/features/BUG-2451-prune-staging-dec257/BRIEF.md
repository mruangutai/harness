# BRIEF — BUG-2451 Prune staging contradicts DEC-257

## Problem

At 47d6c54d, ship's pruner force-stages retained records even though DEC-257 makes those records ordinary tracked artifacts. The operator gets contradictory instructions and an unexpected index mutation; removing staging must not remove the two pre-mutation safety checks added with it.

## Done when — by perspective

**operator** — I can prune obsolete UI evidence without changing my index, and incomplete or unreadable recorded evidence stops pruning before anything changes. Ship instructions agree with the tracked-record contract.

**code maintainer** — I can rely on a regression that fails on the defective pruner and on preserved retention, refusal and symlink protections without a staging implementation to maintain.

## Success criteria

- SC-01 (code maintainer): Tests demonstrate a genuine regression RED against the 47d6c54d pruner before production edits, then PASS for a pruner that invokes no git command and leaves a real temporary git repository's index byte-identical in normal and dry-run modes. Remove the staging half of _stage_paths, _stage, git add -f, staged / would stage output and every staging assertion; retain non-staging coverage.
  verify: automated; evidence: unit
- SC-02 (operator): Both normal and dry-run refuse before any filesystem or index mutation: exit 2 names EVERY missing recorded cycle_evidence path; exit 1 names EVERY unreadable directory under recorded runs. Tests for both checks remain; the unreadable walk collects no paths to stage.
  verify: automated; evidence: unit
- SC-03 (operator): Read git show <review_sha>:.harness/harness/docs/DECISIONS.md and git show <review_sha>:.omp/commands/harness-ship.md: DEC-238's Ship keeps the record and drops the rest bullet and the ship prune paragraph equal their 5e51124e text plus exactly one added sentence each stating BOTH refusals. These restored surfaces and the aligned pruner docstring make no force-staging or runs/**-is-ignored claim; the generated index matches the pinned decision document.
  verify: inspection
- SC-04 (code maintainer): Keep selection, BUG-2294 UI-only deletion, non-UI bytes, symlink safety, --keep and review-pin refusals and the CLI remain unchanged with regression coverage retained; git show <review_sha>:.omp/commands/harness-ship.md preserves prune step position, invocations and the existing prune run evidence at ship commit name.
  verify: inspection

## Verification gaps

No affected active kind has a null runner: unit is active. Component and ui are unresolved null-runner kinds but this patch changes no component/browser surface; functional and eval are excluded under DEC-187 and no criterion rests on them. SC-01/02 require future unit execution and fail-first receipts; SC-03/04 require pinned review, not an intake claim of delivery. No UAT criterion. Production tests are not run during intake.

## Constraints

- DEC-174 BLOCKS execution through the enforcement being changed: main implements gate code and its test directly. DEC-179 SUPPLIES declared routing for the NOBODY layer-0 ship command; coupled docs/index stay in that single direct task. No engineering lead or dev dispatch.
- DEC-225 SUPPLIES one bounded patch intake and one task, no panel or goal-check; pending approval is not permission to build. DEC-120 BLOCKS anyone but main signing on the operator's explicit instruction.
- DEC-257 SUPPLIES ordinary tracked run records and remains unchanged. Amend only DEC-238's named ship bullet as settled; DEC-254 SUPPLIES five-field dispositions and T-01 owns its decision-document change.
- Assigned PRODUCT checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257. Its docs/spec.md, docs/decisions.md and docs/architecture.md are absent at intake; no guidance is invented or substituted. Historical restoration source is 5e51124e; defective subject is 47d6c54de1d91459f84f61ca92e27a47ba553308.

## Out of scope

- .gitignore, templates/gitignore.snippet, DEC-257 itself, merge-gitignore.py, checkout-upgrade.md.
- BUG-2399's shipped records (they stay as history).
- Local check-state parity.

## Approval

status: pending
approved-by:
date:
