# FEAT-30 apply round — second pm spawn, BLOCKED by the concurrency guard

**The guard fired for real: the round was already applied by the earlier spawn, and I wrote
nothing to `plan.yaml`.** Procedural must 1 said to stop if the starting line count is not 1058.
It was 1171, mtime `Aug 20 08:41:10`, ~74 s before my check, and
`notes/research-FEAT-30-simplify-apply.md` existed at the same minute. Two writers on one file is
exactly the condition the guard exists to stop, so I stopped rather than merging over it.

## What the earlier spawn landed (verified by read, not assumed)

- `D-09` (`plan.yaml:170-204`): shape 2, widened — every fixture directory a case treats as a
  worktree becomes a real linked worktree with both sides of the pointer pair; the literal
  `.claude/worktrees/*/` strip and glob are DELETED, not retained. Cost named in the entry: a
  directory under `WORKTREES_SEGMENT` that is not a registered linked worktree stops being swept
  and stops being normalised, so state files inside one are no longer budget-checked.
- T-03 intent carries a `per D-09` paragraph building `wt1` as a real linked worktree and telling
  the executor to report, not adjust, any flipped verdict. T-04 converts the two `run_post`
  fixtures with assertions unchanged. A-4's `+0.22 ms` sentence is in T-04 PART 3.
- `D-08` rewritten: SC-09 is the suite half only; the `check-state.sh` clause is labelled an
  operator-run ship-time sanity check owned by no task, with no new `verify:` invented.
- T-06's `files:` is still exactly `expertise-merge.py` + `test-expertise-merge.py`; the caps
  drift case reads `check-expertise.sh`'s `CAPS` mapping.
- `approval.status: pending`, `lanes.resolved_at: eeabc59`, and A-1/A-3/A-5/A-6 all untouched
  (no `_roster` lift, no `basename` derivation, `factory_config.py` in no `files:` list, and
  T-09 still carries both of A-3's sentences).

## Independent corroboration, which is the only new signal I add

I reached the same design answer from source before I saw the file, and one part of it independently:
**L-1's blast radius is larger than the eng digest's two sweep assertions.** `check-domain.sh:212`
(the resolve branch's `WORKTREE_REL_RE` match) and `harness_boundary.classify`'s `rel_candidates`
are both `.git`-independent today, so T-03's sixteen in-worktree cases and T-04's own per-agent
SC-02c cases go red under PART 1/PART 2 unless their fixtures are real linked worktrees. `fixture()`
(`test-check-domain.py:89-94`) creates no `.git` at all, and the owner-side entries in
`run_worktree` are empty directories with no `gitdir` file, so `linked_worktrees` would enumerate
nothing. `D-09` and the amended T-03 both cover this. I have no disagreement to record with the
landed text, and none with the four untouched briefing rows.

## Route check, at the landed file

`check-plan-routes.py` exit **0**, `0 violation(s) across 1 plan(s)`. Three informational
`DEVIATION` lines (T-03, T-04, T-05 declared `main-session-direct` on granted surfaces) — the
more-restrictive direction, and per the dispatch this check is no evidence either way about the
DEC-174 carve-out.

## Open question for the operator

Nothing in the harness serialises two pm spawns on one `plan.yaml`; the only control that worked
here was a hand-written line-count precondition in the dispatch. A second spawn arriving 60 s
earlier would have interleaved two rewrites of the same intents with no detection.
