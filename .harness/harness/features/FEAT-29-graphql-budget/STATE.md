# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight — `runs/2026-08-19-09-validator/` returned PASS
- squad: none
- status: Building — **the blocking gate is GREEN**; SIMPLIFY is the last build step

**`matrix_ok: true`.** `--kind unit` exit 0, 18 of 18 scripts; `--kind integration` exit 0, 12 of 12;
`must_fix` empty, `severity_max: low`. A code reviewer and a security reviewer ran alongside qa — the
validator lead reversed its own scope-out of security after reading the briefing's disclosure that no
security reviewer had ever seen this feature, and that reversal produced a real finding.

`review_sha` pinned at **`c472a02`**, verified equal to the branch tip.

**SC status:** SC-02, SC-05, SC-06, SC-07, SC-10 **met**. SC-01, SC-03, SC-04 **pending** — they grade
against T-07 and T-09, which are main-session-direct and unrun. SC-08 and SC-09 are `not-assessed`:
both sit on `NOBODY` paths, so no agent domain covers them and they are pre-ship steps for the
operator, not gaps.

**An escalation I relayed was refuted on evidence, and the correction is mine to carry.** I routed the
eng lead's claim that SC-05's OFF-side failing clause was "asserted nowhere". It is asserted, at
`test-gh-cost-log.py:251-259`, driving `rc=1` with the variable genuinely popped. Two tiers reasoned
from control flow without grepping the assertion set; one grep settled it. I verified the line myself
after the fact. The validator lead's own proposed rescue mutation was also refuted — `record()`
re-checks `_enabled()` at `gh_cost_log.py:112`, and `measured()`'s OFF branch is `yield m; return`
with no `try/finally` at `:157-159`, so the OFF path is rc-independent by construction.

**THE MIRROR REMAINS FROZEN.** No `start-task`, no `close-task`, until T-07's after-measurement lands.
Seven positive-control lines depend on cards reading `Backlog`.

Next: SIMPLIFY as an eng-squad segment → re-run both suites → re-pin `review_sha` → hand batch B
(**T-07 first, then T-09**) → goal-check → close-out.

Budget: 46 GraphQL points spent all session. **7 cycles of 10; 10 runs of 20.** Two runs bought no
artifact, both my error: a premature lead close and a re-dispatch over a live run.

## Open Questions

- Q1 (non-blocking): **B-8 should be un-struck, narrowly.** I struck it as moot because the opt-in
  default stops the log being written. The security reviewer showed that conflates a *time-window*
  control with a *containment* one: `.harness/logs/` has no ignore rule and the file is created
  `0644`. The remedy is a `.harness/logs/gh-cost-*.jsonl` rule specifically — **not** blanket
  `.harness/logs/`, whose sibling session logs are tracked.
- Q2 (non-blocking, operator): the stray `.harness/logs/gh-cost-2026-08-19.jsonl`, 39504 bytes, is
  untracked **and** un-ignored, so the tree is dirty at ship. `--resolve` is `NOBODY`.
- Q3 (record, mine): two of my own factual claims were corrected by the panel today — the SC-05
  premise above, and a dispatch stating the delta was one commit when `3fbfd0a..c472a02` is three.
  Neither changed a verdict; both are recorded rather than smoothed.
