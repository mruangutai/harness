# STATE

## Current

- feature: FEAT-09-plan-time-route-check
- phase: build
- worktree: /Users/molchairuangutai/GitHub/harness-FEAT-09 (branch feat/FEAT-09-plan-time-route-check)
- head: 1185d7f
- run: none open — no lead has been dispatched this phase
- status: awaiting-user

Three of four tasks are DONE and committed. The layer-0 segment landed clean and I verified
every `verify:` myself in the worktree rather than relaying the report: the resolve probe
prints `OK`, the domain test exits 0, the unit suite is 13/13, and `check-docs.sh` and
`check-state.sh` both exit 0 with zero violations.

The load-bearing claim is verified, not trusted. `glob_to_re` and `matches` hash IDENTICALLY
either side of the change — one definition of each survives, and `fnmatch` appears only in the
comment saying why it is wrong. That is the one-matcher invariant this feature exists to
protect. `payload=$(cat)` now sits in the `else` branch, so the resolve path never reads stdin;
an open pipe that hung past 10s before answers in 0.21s now. The hook path is unchanged —
checked with my own payload files, out-of-domain exits 2 and in-domain exits 0.

**The build phase is NOT finished.** The last task is held by user ruling until the concurrent
feature merges and this worktree rebases. Until it lands, the suite is 13 PASS not 14, the
registered-test criterion is not exercised by anything here, and the template and rule files
have passed only their land-time greps — their durable test cases do not exist yet. The
goal-check cannot run: seven of twelve criteria rest on the held task.

Cost is 214.93 against a 120 budget, 1.79x, reported and not a gate. It is contaminated
upward and provably so: an engineering lead I never dispatched moved in this window, which is
the concurrent feature metering into the same project-cumulative reporter.

## Open Questions

- Q-B BLOCKING — has the concurrent feature merged to `main` and has this worktree been rebased
  onto it? The held task and the decisions entry both wait on that signal. Segment 1 is now
  committed, so the rebase has nothing uncommitted to collide with.
- Q-D NON-BLOCKING, POSSIBLE HARNESS DEFECT — the cost delta did not reconcile this time. Rows
  I sampled sum to 99.7568 against a total delta of 99.2191. Cumulative counters cannot fall,
  so either an unsampled row dropped or a session aged out of transcript retention and took its
  spend with it. Not established, not guessed at. It bears on whether any cost figure here is
  stable over time.
- Q-C NON-BLOCKING — spend is 1.79x the budget with the held task, a four-wide panel, the
  goal-check, distillation, the decisions entry and the briefing still to run. Continue is the
  default; re-scoping is the user's call.
- Q3 NON-BLOCKING — promote the route checker to a state-check invariant once the concurrent
  feature releases that file? The plan chose a standalone script only because it was unavailable.
- Q4 NON-BLOCKING — the checker copies the state checker's task-block regex rather than sharing
  it. Consolidate later, or accept two copies?
- Q5 NON-BLOCKING — two historical plans use a token this feature retires. Leave them as
  history (the current assumption), or normalise them?
