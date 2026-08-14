# STATE

## Current

- feature: FEAT-20-migration-detector
- run: none — no team run is in flight
- squad: none
- status: awaiting-user

**Phase: build. Both approvals verified** — `plan.yaml` `approval.status: approved` and `BRIEF.md`
`## Approval` status: approved, operator via main session, 2026-08-14. Branch
`feat/FEAT-20-migration-detector` is checked out at `88b1182`; `gh-sync.py open` ran (milestone 11,
parent #360, tasks #361-#364).

**The build stops at its first step, by design.** `plan.yaml` gives T-02, T-03 and T-04 all
`depends_on: [T-01]`, and T-01 is `execution_mode: main-session-direct`. Nothing in the feature is
dispatchable to a lead until T-01 exists. T-01 is marked `building` in `plan.yaml` and
`gh-sync.py start-task T-01` has run (#361 and parent #360 both on `Building`).

**T-01 and T-02 are the operator's lane, in that order.** T-02's only dependency is T-01, so both can
be built in one sitting provided T-01's `verify:` exits 0 first. Their commits must carry
`[harness:t-01]` / `[harness:t-02]`, because that tag is how the orchestrator detects the task landed
and is what `gh-sync.py close-task` is run against. **The mirror is the orchestrator's pen** — the
main session runs no `start-task`/`close-task` for these two.

**Queued behind them, unchanged:** T-03 (eng-lead → dev-ops, `.github/workflows/tests.yml`) and T-04
(product-lead → documentor, the two `docs/harness/` files). They are independent of each other and go
out concurrently, one run per squad, as soon as T-01 has landed and verified.

**Resume protocol for the next orchestrator, step zero.** Re-derive completion from disk — which
`[harness:t-NN]` commits exist — and re-run each landed task's `verify:` block yourself before
dispatching anything; both are cheap suite runs. Then per landed task: set `status: done` in
`plan.yaml` FIRST, then `gh-sync.py close-task`. **Re-pin `review_sha` at a commit that contains the
work before any validator run** — the current pin `88b1182` predates every change in this feature and
would review nothing.

## Open Questions

None blocking a decision. Q1, Q2 and Q5 were settled by the operator at signature (see `BRIEF.md`
`## Approval` notes) and are closed. Two items ride forward:

- **Q3 is an instruction to T-01's implementer, now the operator.** T-01's `intent` covers one
  direction of it — the surfaces are a fixed enum iterated independently of the reader table, and a
  surface with zero rows is CANNOT_VERIFY, not vacuously CLEAN. It does **not** state the other
  direction: a reader-table row keyed to a surface that is not an enum member is silently never
  iterated. Q3's accepted remedy is that such a row is a **loud error** and the relation is checked
  in **both** directions.
- **Harness defect, non-blocking.** The orchestrator playbook says to record the phase in
  `feature.json` `phase:`. `.claude/skills/harness/bin/feature-schema.json` sets
  `additionalProperties: false` and does not define `phase`, so that write would fail validation.
  The phase is recorded here instead.
