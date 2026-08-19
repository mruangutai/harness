# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight — eng segment `runs/2026-08-19-01-eng/` returned BLOCKED
- squad: none
- status: Building — blocked on an operator plan amendment for T-03

Seven of nine tasks are done. T-01, T-02, T-04 landed PASS from the eng segment; T-05, T-06, T-08 are
the operator's, done. Suite re-run by me: exit 0, zero `^FAIL` lines, 139 `PASS` lines. The DEC-174
carve-out held — `check-state.sh` and `gh-sync.py` are byte-unchanged.

**The cheap read is proven against the real API**, not only against fakes: one live call to
`factory_gh.project_item_stations` read all 486 board-3 items for **5 GraphQL points**, against 506
for the `check-state.sh` run the old path sits inside. That corroborates SC-01 and SC-03; it does not
discharge them, because both require a differenced `check-state.sh` run and that is T-07's.

**T-03 is BLOCKED and needs the operator.** `run-unit-tests.sh:40-55` exits 2 for any `test-*.py` in
neither script array, over the union regardless of `--kind`. T-03 creates `test-gh-cost-log.py` and
does not carry `run-unit-tests.sh` in its `files:`, so landing it would take the whole suite down,
not just T-03's own verify. Widening `files:` amends a signed artifact. Questions are in
`notes/layer0-batch-b-FEAT-29.md` §6.

**THE MIRROR REMAINS FROZEN.** No `start-task`, no `close-task`, for any task, until T-07's
after-measurement is captured. Closing #586 for T-08 already moved that card to `Done` and destroyed
one of the positive control's eight lines; **seven remain reproducible** and each further card move
costs another. Measured, not inferred: T-01/02/03/04/07/09 read `Backlog`, T-05/06/08 read `Done`,
parent reads `Building`. `plan.yaml` statuses are still written on schedule; only the subcommands are
held.

Next, once T-03 is amended: eng-lead with T-03 alone → qa segment (T-03 is `change_type: feature`, so
the matrix needs **unit AND integration**) → SIMPLIFY → re-run suites → pin `review_sha` at the tip →
panel. Batch B for the operator meanwhile, **T-07 before T-09**.

Budget: the window reset — GraphQL reads 6/5000. My whole session spent 46 points (40 `gh-sync open`,
1 issue-state query, 5 live board read). `check-state.sh` runs at zero cost under
`FACTORY_GH=/nonexistent/gh`. 3 cycles used of 10; 2 runs of 20.

## Open Questions

- Q1 (blocking, operator): may T-03's `files:` gain `.claude/skills/harness/bin/run-unit-tests.sh`?
- Q2 (blocking, operator): may it also gain `.claude/skills/harness/bin/test-factory-gh.py`, to set
  `HARNESS_GH_COST_LOG=0` where the recorder asserts call counts?
- Q3 (non-blocking, operator): amendment 2 moved T-07's `intent:` but not its `verify:`. The gate
  still diffs two files that both hold zero INV-26 lines, so it reports `OK` whether the positive
  control reproduced or not.
- Q4 (non-blocking): the positive control's expected set should drop to 7 lines, T-08's having been
  destroyed by closing #586. Recommendation and evidence in `notes/layer0-batch-b-FEAT-29.md` §1.
