# STATE

## Current

- feature: FEAT-09-plan-time-route-check
- phase: build
- worktree: /Users/molchairuangutai/GitHub/harness-FEAT-09 (branch feat/FEAT-09-plan-time-route-check)
- head: abddb28
- run: none open — no lead has been dispatched this phase
- status: awaiting-user

Three of four tasks are DONE and committed. The layer-0 segment landed clean and I verified
every `verify:` myself in the worktree rather than relaying the report: the resolve probe
prints `OK`, the domain test exits 0, the unit suite is 13/13, and `check-docs.sh` and
`check-state.sh` both exit 0 with zero violations.

The load-bearing claim is verified, not trusted. Both matcher functions hash IDENTICALLY
either side of the change — one definition of each survives, and `fnmatch` appears only in the
comment saying why it is wrong. That is the one-matcher invariant this feature exists to
protect. The stdin read now sits in the `else` branch, so the resolve path never touches it;
an open pipe that hung past 10s before answers in 0.21s now. The hook path is unchanged —
checked with my own payload files, out-of-domain exits 2 and in-domain exits 0.

**The build phase is NOT finished.** The last task is held by user ruling until the concurrent
feature merges and this worktree rebases. Until it lands, the suite is 13 PASS not 14, the
registered-test criterion is not exercised by anything here, and the template and rule files
have passed only their land-time greps — their durable cases do not exist yet. The goal-check
cannot run: seven of twelve criteria rest on the held task.

**Cost metering is being deleted by the concurrent feature.** Its whole purpose is removing
cost tracking; the reporter is staged for deletion and the rate table is already stripped from
config, so it now errors where it worked minutes earlier. The 214.93 figure is an honest
snapshot of a moving target and is the last one obtainable. After the rebase this flow cannot
meter at all, which leaves the mandated cost line in the final briefing with no source.

## Open Questions

- Q-B BLOCKING — has the concurrent feature merged to `main` and has this worktree been rebased
  onto it? The held task and the decisions entry both wait on that signal. Segment 1 is now
  committed, so the rebase has nothing uncommitted to collide with.
- Q-E BLOCKING AFTER THE REBASE — the cost reporter will not exist in this tree. What should the
  CEO briefing's cost line say, and should the budget fields be dropped from this feature's
  record? Answering it late costs a redraft of the one artifact addressed to a human.
- Q-F NON-BLOCKING — re-pin the review SHA to the post-rebase HEAD before any reviewer runs. The
  rebase rewrites all four commit hashes, so the currently pinned one will not exist and every
  reviewer's pinned-diff claim would be unfalsifiable.
- Q-C NON-BLOCKING — spend is 1.79x the budget, contaminated upward by the concurrent flow.
  Continue is the default and cost never gates; re-scoping is the user's call.
- Q3 NON-BLOCKING — promote the route checker to a state-check invariant once the concurrent
  feature releases that file? The plan chose a standalone script only because it was unavailable.
- Q4 NON-BLOCKING — the checker copies the state checker's task-block regex rather than sharing
  it. Consolidate later, or accept two copies?
- Q5 NON-BLOCKING — two historical plans use a token this feature retires. Leave them as
  history (the current assumption), or normalise them?
