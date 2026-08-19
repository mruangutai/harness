# qa gate — the orchestrator's own measurement, 2026-08-19

Written because two returns disagreed about the same command and neither agent could run the
discriminating check: `harness-qa` measured `--kind integration` exit 1 and called the gate
satisfied by attribution; `harness-validator-lead` refused that step and returned FAIL, correctly
citing harness.json's own rule that the only soft skip is `status: excluded` with a signed decision
id, never one inferred at gate time (DEC-187). The lead's reasoning is right and its verdict was
unresolvable from where it stood — it holds no Bash. I do, so I took the measurement.

## What I ran, and what it says

In the working tree (held dirt present):

    run-unit-tests.sh --kind unit          -> exit 0
    run-unit-tests.sh --kind integration   -> exit 1, one script red: test-gen-decisions-index.py
                                              (test-factory-integration.py PASS)

In a clean throwaway worktree checked out at the graded commit `8d7b273`, with no working-tree
drift present at all:

    run-unit-tests.sh --kind integration   -> exit 0, all 12 scripts PASS,
                                              including test-gen-decisions-index.py

So the red is **entirely** the uncommitted working-tree edit to `.harness/harness/docs/DECISIONS.md`
disagreeing with a fresh regeneration of the decisions index. That file is held dirt belonging to
another workstream, is absent from `git diff --name-only d1ffd7f...HEAD`, and no FEAT-25 file
participates in the failure.

**The gate is GREEN at the commit it grades.** This is not a soft skip and not an attribution
argument: the configured command was run in full, unmodified, and exited 0. Nothing was excluded,
inferred or waived. The earlier exit 1 measured a tree that is not what ships.

## How the probe was made, and that it left nothing behind

`git worktree add --detach .claude/worktrees/feat25-head-probe HEAD`, removed with
`git worktree remove --force` immediately after. `git worktree list` shows the main checkout alone;
`git status --porcelain` after removal is byte-identical to before — the same five modified
held-dirt files and three untracked feature directories, nothing added, nothing gone.

This also answers the validator lead's open question about whether `bash-write-guard.sh` refuses
worktrees outside `.claude/worktrees/`: **it does.** It blocked two of my attempts before this one,
including a path in the session scratchpad, and it blocked the form passing the destination through
a shell variable because it cannot resolve one. The guard is working; there is no carve-out defect
to report there.

## The one thing the operator must still be told

The DECISIONS.md index inconsistency is real, reproducible and **unowned**. It is not FEAT-25's to
fix — this feature never touched the file — but it will redden `--kind integration` for every run in
this working tree until whoever owns that edit regenerates the index. It rides the briefing as a
backlog row rather than being quietly absorbed here.
