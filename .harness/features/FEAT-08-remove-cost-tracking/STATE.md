# STATE

## Current

- feature: FEAT-08-remove-cost-tracking
- run: none in flight — the build phase opens with a main-session batch, not a team run
- squad: none
- status: in_progress

Both artifacts are SIGNED (`BRIEF.md:216`, `PLAN.md:703` — Mike Ruangutai, 2026-08-05), verified on
disk, so the build phase is open. Phase, branch, status and the `approved:` block in `feature.yaml`
were stale from the plan orchestrator's crash and are repaired; nothing on disk was truncated.
Bookkeeping committed as `b5f20af` so the six task diffs land clean for the DEC-174 human read.

Segments S1 and S3 — **T-01, T-02, T-05, T-06, T-07, T-08** — are returned to the main session as
ONE batch, `notes/batch-main-session-s1s3.md`. All six are main-session-direct: T-01 and T-02 under
the DEC-174 carve-out, the other four because `.claude/agents/**`, `harness/SKILL.md`,
`harness-team/SKILL.md` and `teams/*.yaml` are granted to nobody. T-01 leads; the four S3 tasks each
depend on T-01 and nothing else. Nothing of the task work is committed — the pen is mine (DEC-153).

Gates re-measured by me, not inherited: `run-unit-tests.sh` exit 0 (13/13), `check-docs.sh` exit 0,
`check-state.sh` exit 0 with zero violations. That last one read **exit 1** earlier in this same
session, on FEAT-09's unsigned BRIEF; the concurrent flow was signed meanwhile and nothing of
FEAT-08 changed between the two runs.

Next after the batch returns: write the six `[harness:t-NN]` commits, run `gh-sync close-task` for
issues #86, #87, #90, #91, #92, #93, then dispatch S2 (T-03, T-04) to eng-lead and S4 (T-09..T-12)
to product-lead. The validate panel is FOUR-WIDE by user ruling — no pre-emptive skips.

## Open Questions

Question IDs are NOT reused. Q1 and Q3 are carried from the plan phase with their original numbers;
Q5 and Q6 are new this phase. There is no Q2 or Q4 — those were answered during planning.

- Q1 (carried, non-blocking — **raised at the signature gate and signed past without an answer**):
  after this ships the briefing carries no size signal except `cycles_used`, which counts REWORK
  only, so a healthy 16-run feature and a healthy 4-run feature report the same number. D-06
  deliberately replaces nothing; perf-review row 10 (count and budget RUNS) is the lever and is
  unfiled. It needs answering BEFORE the briefing, not in it — by then it cannot be acted on.
  Blocked on: the user.

- Q3 (carried, non-blocking, harness defect): a send-back gives the returning member a FRESH
  context, so `open_questions` it raised in its own previous DIGEST are unrecoverable to it.
  `loop_back`'s `feed: [self]` passes the FAILING step's artifact path, which does not cover a
  member's own prior questions. Raised by product-lead; a rule change decided above this tier.
  Blocked on: nobody — routed to the harness owner.

- Q5 (new, non-blocking): SC-06's glob over-captures. Restricted to FEAT-01..FEAT-07 — the seven
  files the BRIEF itself names at `:81` — it measures **89** cost lines and **67 of 67** run
  `state.yaml` carrying a `cost:` block, pm's pinned figures exactly, verified at `ae2443d`. The
  bare `.harness/features/*/feature.yaml` now reads 96 and 69-of-69 only because FEAT-08 and
  FEAT-09 exist, and after T-03 no new run can carry a `cost:` block at all. Recommend the
  goal-check use the restricted glob and record both numbers.
  Blocked on: nobody — it rides the next user turn.

- Q6 (new, non-blocking, but it can cost a wasted fix cycle): SC-03 demands `check-state.sh` report
  zero violations across the WHOLE repo, and a concurrent flow can fail it. It did at session
  start, purely because FEAT-09's BRIEF was unsigned; it passes now. If it fails at the goal-check
  on a line naming another feature, that is not FEAT-08 regressing. Re-rooting via
  `CLAUDE_PROJECT_DIR` would hide it and is the re-baselining the ruling forbids.
  Blocked on: nobody — flagged so nobody spends a cycle on another flow's state.
