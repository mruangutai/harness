# STATE

## Current

- feature: FEAT-13-single-issue-board-lookup
- run: pending first build dispatch
- squad: eng
- status: in-progress

Mission SHIP, build phase open. Both approvals verified on disk by me: `BRIEF.md ## Approval` and
`plan.yaml approval.status` each read approved / operator / 2026-08-10. The mirror is open —
milestone 7, parent 244, T-01 issue 245, T-02 issue 246.

THE TREE MOVED, AND THIS IS THE ONE FACT A SUCCESSOR MUST NOT MISS. The dispatch said the feature
branch was checked out; it was not. `/Users/molchairuangutai/GitHub/harness` sits on
`chore/203-end-copy-distribution` at 275de45, which is FEAT-12 mid-build, and switching it would
have pulled that tree out from under a live flow. So FEAT-13 runs in a git worktree at
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-13-single-issue-board-lookup`,
on `feat/FEAT-13-single-issue-board-lookup` at 6dfbf7c. That path is the DEC-143 shape: the
domain hook strips the `.claude/worktrees/<one-segment>/` prefix and matches the same globs, so
grants are unchanged. A worktree anywhere else — `/tmp`, a scratchpad — escapes the project root
and `check-domain.sh` returns WITHOUT ENFORCING, which is a silent fail-open, not a block.

EVERY COMMAND AND EVERY EDIT RUNS FROM THE WORKTREE, by absolute path. An edit to the main
checkout's copy of a `factory_*.py` passes the domain hook (backend-dev owns that path in both
trees) and passes a test run in that same tree, so a wrong-root edit lands FEAT-13's work on
FEAT-12's branch silently. It fails no gate. The main checkout's nine in-scope files are re-checked
byte-identical to `origin/main` after each build run as the tripwire for exactly that.

The three plan-phase run dirs were copied into the worktree because `.gitignore` holds
`.harness/features/*/runs/**`, so they exist only where they were written. Without the copy the
ship briefing would have silently omitted the whole plan phase.

## Open Questions

- Q1 (non-blocking, harness observation, not a plan question): creating the worktree fired a
  one-time PostToolUse shape-sweep burst over historical state files the checkout duplicated —
  `FEAT-02/STATE.md` and `FEAT-05-pyyaml-file-parsers/STATE.md`, both pre-existing violations on
  the branch, neither in this feature's scope and neither mine to fix. It did not repeat: the
  `.harness/.shape-sweep-stamp` high-water mark advanced and the next Bash call was clean. Raised
  so the harness owner knows a worktree costs one noisy sweep, and because that burst is where a
  real violation of this feature's own state files could hide.
