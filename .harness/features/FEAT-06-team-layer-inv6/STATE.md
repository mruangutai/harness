# STATE

## Current

- feature: FEAT-06-team-layer-inv6
- phase: build
- run: runs/t08-product/ (complete, PASS, metered 11.39)
- squad: product
- status: in_progress

**9 of 10 tasks are done and PASS. Only T-07 remains, and it is main-session-direct.** Segment 1
(T-01, T-02, T-04, T-10, T-05, T-06, T-09, T-11) landed 8 of 8 and is committed at `f45fd0f` with
its eight mirror issues closed. T-08 landed clean on the first pass. **Zero send-backs across the
whole build, so `cycles_used` stays 4 of 10** (DEC-157: a first pass is work, not rework).

**Every gate re-run at the orchestrator's own tier after T-08:** `check-docs.sh` exit 0,
`check-state.sh` zero VIOLATION lines, `run-unit-tests.sh` exit 0. The lead holds no `Bash`, so its
gate claims were reported, not measured — they are now measured.

**T-07's downstream gate is safe, checked not assumed.** T-07 check (9) fails loudly if a §13 DAG
row carries zero or more than one `∥`-bearing brace group. Measured after T-08: `SPEC.md:1978` has
2 brace groups and exactly **1** with `∥`; `:1980` has 1. Both now read `{code ∥ qa ∥ security ∥ ui}`
and `review.yaml` parses to the same set — SC-15's three legs already agree.

**SC-14 measured both ways.** At `635ef14`: `test_matrix` lines 0, 8-line window 0 hits. Now: lines
2, window 7 hits. Line budgets held with room — `SKILL.md` +14 of 20, `harness-team/SKILL.md` +12 of
14, **zero deletions on either**, so no reflow inflated the count.

**Four defects caught mid-execution that would each have shipped green.** (1) T-05's widened gate
would have scanned NOTHING — Python `glob` does not descend into dotted directories, so
`glob('**/*.yaml')` from the repo root returns 0 while `os.walk('.harness')` finds 54; re-measured
here. (2) SC-06 proven to discriminate against the pre-widening `scan()`: 0 files, 0 findings.
(3) A comment naming `PLACEHOLDER_UNSET` broke T-01's own `== 1` verify. (4) T-02's sweep created a
sixth count-bearing comment, caught by its own closing re-grep — the handoff named four, the
orchestrator's re-grep found a fifth, the sweep made a sixth. Enumeration would have missed it.

**T-08's Q1 resolved here, no user call needed.** documentor declared no stale marker; its premise
verified at source — `{code ∥ security ∥ ui}` also occurs at `BRIEF.md:28` and `PLAN.md:139/:156/:161`,
all approval-gated, so declaring the marker would red-line four files nobody here may edit.

**Cost: 42.89 measured of the $100 build allowance** — orchestrator by_agent delta 31.50 plus the
t08-product run 11.39. It understates reality: 9 of 10 tasks ran at depth-0 in the main session,
which is not separable to this feature.

**Two carries.** T-01's `wc -l == 1` conjunct must be re-run AFTER T-07 lands a new file in `bin/`.
**`feature.yaml` is at exactly 200 of its 200-line cap** — the next write must trim in the same pass
or the shape gate blocks it.

## Open Questions

- none blocking. Issue #36 (`run-unit-tests.sh` misconfigured-error outside the repo root,
  pre-existing at `635ef14`, fail-closed) is filed and out of scope. The ten advisories, AQ-2 and
  `DECISIONS.md:1634`'s stale three-wide panel row are backlog for the user's ship acceptance.
