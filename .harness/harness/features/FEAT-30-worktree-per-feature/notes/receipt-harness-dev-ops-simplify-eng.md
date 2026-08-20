# EFFICIENCY receipt — FEAT-30 plan.yaml — harness-dev-ops (four-angle simplify pass)

## Verdict: PASS, one low-value finding, no blocking findings

## DAG, derived from `depends_on:` fields (plan.yaml lines 171,339,442,506,704,823,920,957,1003)

Roots (empty `depends_on`): **T-01, T-03, T-06** — confirmed, no others. Three independent
chains: T-01→T-02, T-03→T-04→T-05, T-06→T-07, converging at T-08 (needs T-02+T-06 only —
correctly minimal, not T-01/T-04/T-05) and finally T-09 (needs T-04,T-05,T-07,T-08). The
parallelism is real and unstated in the plan's own prose. No declared edge serialises work
that need not be serialised: every edge I checked matches a same-file write-after-write need
(T-02 after T-01 on `feature-worktree.py`; T-05 after T-04 on `test-bash-write-guard.py`).
T-09 lists both T-04 and T-05 though T-05→T-04 already implies it — redundant but costs
nothing (no extra wait), not flagged as a finding.

## Finding 1 (briefing row, not a feature cycle)

**File/line:** plan.yaml T-04 PART 3, lines 630-635 (sweep globs built from
`harness_boundary.linked_worktrees(root)`), contrasted with the settled classify measurement
at lines 569-571.

**Summary:** D-02/T-04 costs the `checkout_relative` change on the classify hot path
(0.3ms vs 46.8ms/2000 iters, settled, not re-litigated) but the sibling PART-3 change — the
shape-sweep's glob list, rebuilt every POST Bash write from `linked_worktrees(root)` (a
`.git/worktrees` pointer-file read per linked worktree) — carries no equivalent number.

**Measured** (`/private/tmp/.../scratchpad`, synthetic fixture, 5 linked worktrees, 2000
iters, python3 `time.perf_counter`): pointer-read + glob-list build alone: 0.174ms/call;
same plus full `glob.glob()` expansion of all patterns: 0.371ms/call. Today's mechanism
(fixed one-level `.claude/worktrees/*` wildcard, no pointer read) at the same iteration
count: 0.147ms/call. Delta ≈ +0.22ms per governed Bash write at 5 concurrent worktrees,
scaling linearly with worktree count. This sits inside the same file's own comment that
interpreter start-up already costs ~38ms of ~42ms per Bash call — the addition is roughly
0.5% of existing per-call overhead, not a performance concern.

**Alternative:** add one sentence to T-04's PART 3 intent (or fold into D-02) stating this
was measured and is negligible relative to interpreter start-up, mirroring the classify
note already given for PART 1. Costs nothing to add; its absence just leaves a reader unable
to tell "not costed" from "costed and fine" without re-deriving it themselves, exactly the
gap this angle was asked to close.

**Cycle judgment:** briefing row only — the number is fine, the plan doesn't need to change,
only its self-documentation would be marginally more complete. Not worth a feature cycle.

## Not flagged (checked and cleared)

- Double/full-suite runs at T-01/T-02/T-03/T-04/T-05/T-06 verifies: red-state proofs, correctly
  expensive by design (per dispatch item 3), not re-flagged.
- D-06 ordering (no runner call before T-08): an ordering requirement, not re-flagged.
- No repeated whole-file re-reads across sequential tasks found beyond the normal
  per-dispatch context load inherent to the team model (not a plan-level inefficiency).

## Timing commands run

`python3` synthetic benchmark script in scratchpad (see above); no repo files mutated,
`.git/worktrees` on this checkout confirmed empty (`ls .git/worktrees` → exit 1, 0 entries)
before running, so the fixture used a tempdir, not this tree.
