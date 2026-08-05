# STATE

## Current

- feature: FEAT-08-remove-cost-tracking
- run: none in flight — the build phase opens with a main-session batch, not a team run
- squad: none
- status: in_progress

Both artifacts are SIGNED (`BRIEF.md:216`, `PLAN.md:703` — Mike Ruangutai, 2026-08-05), verified on
disk, so the build phase is open. Phase, branch, status and the `approved:` block in `feature.yaml`
were stale from the plan orchestrator's crash and are repaired; nothing on disk was truncated.

Segments S1 and S3 — **T-01, T-02, T-05, T-06, T-07, T-08** — are returned to the main session as
ONE batch, `notes/batch-main-session-s1s3.md`. All six are main-session-direct: T-01 and T-02 under
the DEC-174 carve-out, the other four because `.claude/agents/**`, `harness/SKILL.md`,
`harness-team/SKILL.md` and `teams/*.yaml` are granted to nobody. T-01 leads; the four S3 tasks each
depend on T-01 and nothing else. Nothing is committed — the pen is the orchestrator's (DEC-153).

Gates re-measured by me at `ae2443d`, not inherited: `run-unit-tests.sh` exit 0 (13/13),
`check-docs.sh` exit 0, `check-state.sh` exit 0 with zero violations. That last one read **exit 1**
earlier in this same session, on FEAT-09's unsigned BRIEF; the concurrent flow was signed meanwhile
and nothing of FEAT-08 changed between the two runs.

Next after the batch returns: write the six `[harness:t-NN]` commits, run `gh-sync close-task` for
issues #86, #87, #90, #91, #92, #93, then dispatch S2 (T-03, T-04) to eng-lead and S4 (T-09..T-12)
to product-lead. The validate panel is FOUR-WIDE by user ruling — no pre-emptive skips.

## Open Questions

- Q1 (non-blocking): SC-06's glob over-captures. Restricted to FEAT-01..FEAT-07 — the seven files
  the BRIEF itself names at `:81` — it measures **89** cost lines and **67 of 67** run `state.yaml`
  carrying a `cost:` block, pm's pinned figures exactly, verified at `ae2443d`. The bare
  `.harness/features/*/feature.yaml` now reads 96 and 69-of-69 only because FEAT-08 and FEAT-09
  exist, and after T-03 no new run can carry a `cost:` block at all. Recommend the goal-check use
  the restricted glob and record both numbers.
  Blocked on: nobody — it rides the next user turn.

- Q2 (non-blocking, but it can cost a wasted fix cycle): SC-03 demands `check-state.sh` report zero
  violations across the WHOLE repo, and a concurrent flow can fail it. It did at session start,
  purely because FEAT-09's BRIEF was unsigned; it passes now. If it fails at the goal-check on a
  line naming another feature, that is not FEAT-08 regressing. Re-rooting via `CLAUDE_PROJECT_DIR`
  would hide it and is the re-baselining the ruling forbids.
  Blocked on: nobody — flagged so nobody spends a cycle on another flow's state.

- Q3 (non-blocking, carried from plan): after this ships the briefing carries no size signal except
  `cycles_used`, which counts REWORK only — a healthy 16-run feature and a healthy 4-run feature
  report the same number. D-06 deliberately replaces nothing; perf-review row 10 is the lever and
  is unfiled.
  Blocked on: nobody.

- Q4 (non-blocking, harness defect, carried from plan): a send-back gives the returning member a
  FRESH context, so `open_questions` it raised in its own previous DIGEST are unrecoverable to it.
  `loop_back`'s `feed: [self]` passes the FAILING step's artifact path, which does not cover a
  member's own prior questions. Raised by product-lead; a rule change decided above this tier.
  Blocked on: nobody — routed to the harness owner.
