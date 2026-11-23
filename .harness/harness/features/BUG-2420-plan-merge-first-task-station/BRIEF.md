# BRIEF — BUG-2420 First task station

## Problem

An operator moving an apply-added task to its first station receives exit 3 even though the task exists: set-task-station confuses an absent status line with an absent task. This blocks FEAT-2397's build and prints a contradictory missing-task message (settled grilling, reproduction at 9eb07b4f).

## Done when — by perspective

**operator** — I can move an existing task to its first station without re-signing its approved plan. A genuinely missing task is still refused clearly.

**code maintainer** — I can rely on focused regression evidence for first-station insertion, existing-status preservation and the drafting path, without changes to adjacent contracts.

## Success criteria

- SC-01 (operator): A three-row table-driven unit test exercises set-task-station: a status-less task gains status: building at its field indent with the usual STATION/APPLIED output; an existing status is rewritten with every other byte unchanged; a genuinely missing task exits 3 with non-confusable missing-task text and no write. Preserve raw fail-first evidence against the pinned pre-fix stations.py and matching green evidence; the insertion row must fail before the fix.
  verify: automated evidence: unit
- SC-02 (operator): A unit assertion compares the entire signed approval block byte-for-byte before and after the first-station insert, including approval.status: approved, proving no re-sign is required. Preserve its failing pre-fix receipt and matching green receipt.
  verify: automated evidence: unit
- SC-03 (code maintainer): One integration case starts with tasks: [], applies T-01 without status, asserts apply does not seed status, then successfully sets T-01 building and reloads the written plan with that station. Preserve raw red evidence at the pinned pre-fix state and matching green evidence. Do not duplicate inline-empty union mechanics.
  verify: automated evidence: integration

## Verification gaps

None applicable: active unit and integration runners discover tests/unit/ and tests/integration/ respectively. Runtime bugfixes require the unit floor in harness.json; integration additionally proves this drafting-path bug class. Unresolved component/ui and the TypeScript typecheck surface do not cover this Python-only patch. Product read inputs are .harness/harness/docs/SPEC.md and .harness/harness/docs/DECISIONS.md in the assigned checkout; consult the relevant specification sections and DEC-120, DEC-174 and DEC-225 alongside the settled intake and existing behavior. No UAT criterion.

## Constraints

- DEC-174 BLOCKS governed execution of this enforcement writer and its tests: T-01 is main-session-direct; all edits including task subagent edits remain inside the assigned feature worktree.
- DEC-225 SUPPLIES one patch product run, a brief of at most 120 lines and one task, with no readers, panel or goal-check. DEC-174 overrides the generic patch team route.
- DEC-182 SUPPLIES plan-merge controlled writes and literal verification; DEC-120 reserves signature for main. Both artifacts remain pending at intake.
- Only .claude/skills/harness/bin/plan_merge/stations.py and its tests may change. Existing status rewrite remains exactly as today. Preserve usual STATION/APPLIED output. Only a genuinely missing task refuses exit 3.
- Tests come first. New/changed Python test functions must grade at least 3; production plan_merge functions have bar 4 (code_grade.py _record). Grade-2 advisory exit behavior is not permission to miss these floors.
- This patch's seeding proposal explicitly carries T-01 status: ready to avoid its own first-station deadlock. This is not a change to apply's behavior.

## Out of scope

- All other plan-merge verbs, refusals and formatting behavior; apply's IGNORED-status rule stays — bounded known-cause patch.
- #747 and #1104 — separate work; apply must not seed status on newly added tasks.
- FEAT-2397 plan content — not a workaround in the blocked feature.
- Why sign-approval moved FEAT-2337 to ready but left FEAT-2397 at plan — separate investigation.
- Adjacent cleanup and production documentation edits — preserve the bounded source-and-tests patch.

## Approval

status: approved
approved-by: Mike Ruangutai (delegated to fable-advisor)
date: 2026-11-22
