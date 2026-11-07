# Passing full matrix — fad2e25c

Review pin: `fad2e25c` — the merge of origin/main c4e8bbc8, plus the two advisor rulings and the
delta-review fixes. Authority: `operator-ship-directive-2026-11-07.md`, item 2. Each kind was run
exactly once, in parallel, with no source changes and no retries.

| Command | Result | Files | Pool wall | Command wall |
|---|---|---:|---:|---:|
| `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0, PASS | 57/57 | 38.10s | 38.27s |
| `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0, PASS | 84/84 | 110.24s | 110.40s |

The `FAIL BUG-1290 5a/5b/5c` lines in the unit output come from `test-factory-claim-mutation.py`.
It deliberately runs a mutant, and its result is `MUTATION PROOF: 3/3 cases reddened` with exit 0.

Superseded runs:

- At 4a5fb45e, the unit matrix passed 57/57.
- At 4a5fb45e, the integration run was cancelled before it finished.

Both were superseded by the fixes in `fad2e25c`, and neither is evidence for this pin.

Full-corpus `check-state.py` on a non-sparse checkout of this pin reports no violation except the
two rows caused by the probe's location (INV-25 and INV-29, which say a worktree lies outside
`.claude/worktrees/`). The same command on origin/main c4e8bbc8 gives the same result.

Re-pinned to `d69cf444` after the DEC-182 T-01 amendment (`amendment-T-01-budget-2026-11-07.md`).
`git diff fad2e25c d69cf444` outside `.harness/harness/features/` is empty: every source, test
and runtime blob is identical, so this matrix still covers that pin. The only change is the plan
text and its ledger. `check-plan-routes` (0 violations) and `plan-merge.py check` (44 anchors,
0 failures) pass at d69cf444.
