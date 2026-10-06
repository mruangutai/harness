# Operator ruling, 2026-10-05: raise the rework budget for one more fix round

**Asked:** after validate c3 passed and an independent outside panel reviewed PR #2103, the
round-2 rework budget (2 rounds, 120 min) was spent. Should the panel's seven high and medium
findings be fixed now?

**Ruling (mruangutai):** "Raise budget, fix 1-7." That means one more main-session fix round,
then a fresh validate. The two lows are filed as issues, and #2101 is amended with a rule on how
old a checkout's HEAD may be.

**New ruling:** 3 rounds and 180 minutes. 38 minutes were spent through validate c3.

## The findings being fixed

They come from three outside reviewers (reviewer, security-reviewer and fable-advisor) on PR #2103:

1. **High.** `factory_claim` reads other features' plans from the checkout it runs in, so from a
   sparse worktree it reports "no plan".
2. **High.** Repair decides a file is safe to remove using its clean-filter hash. A lossy clean
   filter therefore deletes bytes the index does not hold.
3. **Medium.** A tracked symlink outside the cone is hashed through its target, so it is
   wrongly classed as dirty (class C).
4. **Medium.** Git C-quotes sparse-checkout names, and the comparison does not decode them, so
   a cone with Unicode names never verifies.
5. **Medium.** During a rebase, a worktree identified only by its branch has a detached HEAD, so
   it loses its feature identity and becomes a no-op probe.
6. **Medium.** When the active feature's directory is missing, `corpus_path` reads the landed
   owner copy instead.
7. **Medium.** In a converged worktree whose only finding is dirty work, the hooks still print a
   "commit or stash" instruction.
