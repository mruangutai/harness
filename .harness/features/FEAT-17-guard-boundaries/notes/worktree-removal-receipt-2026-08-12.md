# Receipt — the out-of-place worktrees were removed OUTSIDE this task — 2026-08-12

T-06 was written to remove them under its own discipline. That is not what happened, and this
receipt records the truth rather than reconstructing the evidence T-06 asked for.

## What actually happened

The main session removed all out-of-place worktrees on 2026-08-12 during the **FEAT-13
close-out** (task 16), as ordinary cleanup, without knowing T-06 owned that removal. Two of
T-06's four steps were safeguards, and both were skipped:

| T-06 step | Done? |
|---|---|
| 1. Capture `git worktree list` BEFORE touching anything | **NO** |
| 2. `git tag archive/worktree-r6 52d8334` before removal | **LATE** — applied 2026-08-12, after removal |
| 3. `git worktree remove` on r6, then `git worktree prune` for wt140 | yes, during task 16 |
| 4. Capture `git worktree list` after | possible, but see below |

## What that cost, measured rather than assumed

**`52d8334` was unreachable and gc-eligible between the removal and the tag.** It is NOT an
ancestor of `main` — confirmed with `git merge-base --is-ancestor`, which is exactly why T-06
ordered the tag before the removal. The commit survived only because no `gc` ran in the gap.
It is now preserved by `archive/worktree-r6`.

`ffbdbfa` (wt140) was never at risk — it IS an ancestor of `main`. Tagged as
`archive/worktree-wt140` anyway, harmlessly.

**The before capture cannot be written.** T-06's own words: "Untracked live state leaves no
commit evidence, so an uncaptured before is unrecoverable." Writing it now would mean
reconstructing it from memory, which falsifies the record.

**The paired negative was destroyed.** T-06 required
`.claude/worktrees/FEAT-13-single-issue-board-lookup` to still appear in the after capture, as
"the paired negative proving the prune was targeted and not a sweep." The FEAT-13 close-out
removed that worktree too, deliberately and for its own reasons. So the control does not exist,
and the honest characterisation is that this WAS a sweep, not a targeted prune.

## State now, taken at this commit

```
git worktree list  ->  /Users/molchairuangutai/GitHub/harness   [main]
```

One entry. No worktree outside the main checkout, and none under `.claude/worktrees/` either.

Tags: `archive/worktree-r6` -> `52d8334`, `archive/worktree-wt140` -> `ffbdbfa`.

## Why this replaces T-06's captures instead of imitating them

T-06's verify checks three things, and two were already true before this task started: no
out-of-place worktrees, and the archive tag present. The third — an "after" file exists and is
non-empty — is one command away. **So T-06 would have gone green while asserting a before/after
comparison nobody can make and a targeted prune that did not happen.**

That is a criterion satisfied by its own checkbox rather than by its evidence, which is the
defect class this whole feature exists to remove. A green T-06 built on a fabricated before
capture would have put that defect inside the feature that fixes it.

The work T-06 wanted is done. Its evidence cannot be back-dated, so the receipt says so.

## The lesson worth carrying

**Cleanup performed outside the task that owns it loses the task's safeguards silently.** No
gate noticed, and none could have: `git worktree prune` is an ordinary command, and the
discipline that made it safe lived only in a plan nobody was reading at that moment.
