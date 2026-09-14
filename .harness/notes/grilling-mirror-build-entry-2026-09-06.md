# Grilling — mirror build entry and terminal recovery — 2026-09-06

## Destination
For both `FEAT-*` and `BUG-*` flows, Build entry records an unambiguous mirror outcome immediately after signed approval, and Ship means only post-merge terminal finalization. A sync-enabled feature never silently loses its mirror lifecycle.

## Settled
- `Ship` → the post-merge terminal phase: it finalizes merged code for users, records terminal local state, performs any recorded mirror transition, and releases the worktree.
- `Build entry` → the signed-plan transition that starts execution and runs `gh-sync.py open`; it is never called Ship.
- Build → refuses when the required local Build-entry outcome is absent; it may proceed after a recorded temporary environmental mirror failure.
- Enabled GitHub sync → outcomes are `opened` or `recovery-required`; local configuration/contract errors and partial remote writes block Build.
- Disabled or unconfigured GitHub sync → `not-applicable`; it remains an approved no-mirror delivery mode.
- `recovery-required` → the main session reruns idempotent `gh-sync.py open` before merge and refuses the user’s merge action until a normal mirror receipt is recorded.
- Legacy already-merged enabled-sync features → require an explicit operator-approved recovery. It creates a terminal receipt only: milestone plus parent/source issue, never historical task sub-issues.
- Legacy recovery while GitHub is unavailable → remains non-terminal and retains its worktree until recovery and Ship succeed.

## Not yet specified
- The exact schema field names and command spelling for persisted Build-entry outcomes and terminal-receipt recovery.
- Whether an old `recovery-required` receipt needs age-based escalation; pm may choose the simplest durable behavior consistent with the settled policy.

## Out of scope
- Requiring GitHub sync for projects that intentionally set `github.sync: false` or leave GitHub unconfigured.
- Creating task-level historical mirror records after work completes.
- Changing the user-gated merge policy.

## Facts I verified (so pm does not re-derive them)
- `gh-sync.py:1799-1800` calls `skip("no recorded milestone — nothing to close")` before `_record_pr` and `_record_station(..., "done")` at `:1960-1976`.
- `post-merge-sweep.sh:180-208` retains a worktree when ship emits `gh-sync: SKIP` or `gh-sync: FAILED`.
- FEAT-55’s build handoff said mirror work “belongs at the validate seam”; its validate→ship handoff invoked `ship` but omitted `open`; STATE.md recorded that `open` never ran.
- DEC-138 states `plan approved → create` and that GitHub is a mirror, never a gate (`.harness/harness/docs/DECISIONS.md:2948-2952`).
- The ambiguous phrase `mission ship, right after the approval gate passes` originated in the initial GitHub-mirror implementation at `ab4d2fdc`, then persisted through the reference extraction.
- `check-state.sh:2099-2126` skips mirror validation for terminal features and for all-status-absent plans; FEAT-55 had no task `status` lines, and `plan-merge.py set-task-station` only splices an existing task-status line.
