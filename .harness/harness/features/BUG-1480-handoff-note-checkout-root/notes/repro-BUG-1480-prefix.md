# Live reproduction — BUG-1480, before the fix

**The defect reproduces on this feature's own handoff note, at commit `3c0d647f`, in this
worktree.** Captured 2026-09-07 by the orchestrator, as an ordinary `Write` through the live
`PreToolUse` hook — not a fixture, not a simulation.

## What was attempted

Writing the plan → build seam note DEC-159 requires, at

    <worktree>/.harness/harness/features/BUG-1480-handoff-note-checkout-root/notes/handoff-plan.md

with a well-formed five-section body whose `## Done when` block cites two authorities that both
exist and are both unsatisfied in this worktree's `plan.yaml`: `plan-task:T-01.verify` and
`plan-task:T-02.verify`. T-01 and T-02 are at station `ready` and each carries a non-empty
`verify:`, so neither is already-satisfied under FEAT-54's rule.

## What the gate returned, verbatim

    check-domain: BLOCKED — .claude/worktrees/harness/BUG-1480-handoff-note-checkout-root/.harness/harness/features/BUG-1480-handoff-note-checkout-root/notes/handoff-plan.md: handoff shape (DEC-159).
      Authority pointer 'plan-task:T-01.verify' is unresolved in /Users/molchairuangutai/GitHub/harness/.harness/harness/features/BUG-1480-handoff-note-checkout-root/plan.yaml: cannot resolve target: [Errno 2] No such file or directory: '/Users/molchairuangutai/GitHub/harness/.harness/harness/features/BUG-1480-handoff-note-checkout-root'; follow templates/HANDOFF.md
      Authority pointer 'plan-task:T-02.verify' is unresolved in /Users/molchairuangutai/GitHub/harness/.harness/harness/features/BUG-1480-handoff-note-checkout-root/plan.yaml: cannot resolve target: [Errno 2] No such file or directory: '/Users/molchairuangutai/GitHub/harness/.harness/harness/features/BUG-1480-handoff-note-checkout-root'; follow templates/HANDOFF.md

## Why this is the whole diagnosis in one message

The refusal **names the wrong path itself.** The note is in the worktree; the plan it is being
checked against is looked for at `/Users/molchairuangutai/GitHub/harness/.harness/...` — the MAIN
checkout — where this feature's directory does not exist and will not exist until the branch
merges. The worktree copy, which does exist and does carry both tasks, is never opened.

Both halves of `_norm`'s answer are visible in that one message: the path is worktree-relative
(so `_ck[1]` was used) and the root is the main checkout (so `_ck[0]` was thrown away).

## The consequence, stated plainly

Nothing an author can write closes this. Every legal authority type resolves through the same
`_feature_dir(rel_path, root)` join, so no choice of pointer helps; bending a pointer to something
that happens to exist in the main checkout would leave a false authority in the record. The note
DEC-159 requires at every phase seam is unwritable for every feature, because every feature lives
in a worktree until it merges.

## After the fix

This exact note is written again, unchanged, and must be accepted. That re-attempt is the
end-to-end evidence for SC-01 and is recorded at the build → validate seam.
