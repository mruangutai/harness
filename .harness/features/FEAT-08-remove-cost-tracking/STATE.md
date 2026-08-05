# STATE

## Current

- feature: FEAT-08-remove-cost-tracking
- run: dispatching S2 to eng-lead — runs/s2-eng
- squad: eng
- status: in_progress

**Six of twelve tasks are DONE and committed.** T-01, T-02, T-05, T-06, T-07, T-08 landed as one
main-session batch (`ba9a243`, `aaa315f`, `f9869d1`, `32d23d3`, `89cd01a`, `3503d1d`); issues #86,
#87, #90, #91, #92, #93 closed. I re-ran every `verify:` clause at my own tier rather than trusting
the report — all green, both over-removal guards intact, both unchanged-value clauses matching
their captured pre-edit numbers.

**SC-04 is proven, both halves, and it discriminates.** Against the pre-change validator the
omitting payload returned `BLOCKED (contract violation) — missing 'cost_usd'` at exit 1 and the
carrying payload was accepted; against the post-change validator both are accepted. The first
flipped, the second did not.

**Two PLAN defects of the same shape**, each an `intent:` that falsifies its own `verify:` by
mandating prose containing a token that same `verify:` counts or forbids. Both reconciled in the
batch by writing the same meaning without the literal spelling; both deviations recorded in their
commit messages. See `feature.yaml` `batch_result.plan_defect`.

Next: S2 (T-03, T-04) to eng-lead — both `depends_on: T-02`, now satisfied, both mutate the repo, so
serialized. Then S4 (T-09..T-12) to product-lead, which needs S2 first. Then the four-wide panel.

**The meter dies in the very next dispatch.** T-03 deletes `cost-report.py`. Metered one last time
at `3503d1d`: $370.53 against a $120 budget. Every figure after this is an honest string.

## Open Questions

IDs are not reused. Q1 and Q3 are carried from the plan phase; Q5, Q6 and Q7 are new. Q2 and Q4
were answered during planning.

- Q1 (carried, non-blocking — **raised at the signature gate and signed past without an answer**):
  after this ships the briefing carries no size signal except `cycles_used`, which counts REWORK
  only. D-06 replaces nothing on purpose; perf-review row 10 is the lever and is unfiled. It needs
  answering BEFORE the briefing — by then it cannot be acted on.
  Blocked on: the user.

- Q3 (carried, non-blocking, harness defect): a send-back gives the returning member a FRESH
  context, so `open_questions` it raised in its own previous DIGEST are unrecoverable to it.
  `loop_back`'s `feed: [self]` passes the FAILING step's artifact path, which does not cover a
  member's own prior questions.
  Blocked on: nobody — routed to the harness owner.

- Q5 (non-blocking): SC-06's glob over-captures. Restricted to FEAT-01..FEAT-07 — the seven files
  the BRIEF names at `:81` — it measures **89** cost lines and **67 of 67** run `state.yaml`, pm's
  pinned figures exactly. Recommend the goal-check use the restricted glob and record both numbers.
  Blocked on: nobody.

- Q6 (non-blocking, but it can cost a wasted fix cycle): SC-03 is repo-wide and a concurrent flow
  can fail it. It did at session start on FEAT-09's unsigned BRIEF. FEAT-09 has since moved to its
  own worktree, so this checkout no longer sees its state — the hazard is dormant, not gone.
  Blocked on: nobody.

- Q7 (new, non-blocking, for the review panel and not the user): both comments reworded around the
  plan defect end by justifying themselves with "this task's `verify:`". After this ships there is
  no task and no `verify:`, and the BRIEF states nothing re-runs those greps. Routed to the
  code-reviewer rather than pre-judged by me.
  Blocked on: nobody — the panel rules.
