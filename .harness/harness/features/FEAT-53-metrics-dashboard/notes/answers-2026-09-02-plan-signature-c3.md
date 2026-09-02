# Answers — FEAT-53 plan-signature briefing, pass 3 — 2026-09-02

## Q1 — V-1 (high, trend.jsonl commit-disposition gap)
**Ruling: FIX.** Name a committer for `.harness/metrics/trend.jsonl` the same way `D-22`/`T-20`
already do for `instrumented_at` and `touchpoints.jsonl` — one sentence in `D-22`'s `choice` or in
`T-19`, naming which step commits the ship record in the same act it appends it. Same class of gap,
same fix shape as the two files already closed.

## Q2 — B-15..B-18 (advisory, one-clause each)
**Ruling: FIX ALL FOUR**, in the same dispatch as V-1, per the orchestrator's own recommendation:
- B-15: name one authority for the BRIEF approval-date parse; the other caller calls it.
- B-16: add the three missing gap-state fixture cases to T-06.
- B-17: T-11's mutating fixture cases copy to a temp dir first.
- B-18: D-21 compares at day granularity (or takes the epoch's date), not an intra-day instant
  against a date-only start.

## Q3 — new scope: PRs-over-time chart (fold into THIS dispatch)
Add a 7th tile: **merged PRs over time**, weekly buckets, sourced from `.harness/metrics/trend.jsonl`
— one point per shipped feature, per DEC-200's exactly-one-merged-PR-per-feature invariant. No new
data source: this reads the same trend log the other trend tiles already read. Scope it exactly like
the other tiles: honest empty state if the log has fewer than one point in a bucket, never a
fabricated zero. This is the ONLY new scope going into this dispatch — do not add anything else.

## Accuracy KPI (handoff/dispatch eval) — EXPLICITLY OUT OF SCOPE for FEAT-53
Do not touch this in this dispatch or any later FEAT-53 cycle. It is being split into its own
follow-up feature (FEAT-54), scoped from a 30-run controlled eval study the operator ran comparing
handoff artifact variants (required-facts rubric, perfect-response count, ambiguity count,
char/latency proxies). FEAT-54 will cover both the eval harness (ai-dev-owned, DEC-70 ai_behavior
gate) and the dashboard tile that consumes its results log. Nothing about it should appear in
FEAT-53's plan, BRIEF, or design.

## Budget note
This dispatch is expected to bring cycles_used to 8 of the hard 10. Per the orchestrator's own
assessment, this should be treated as the last cycle before signature — if the next panel read
surfaces further findings, escalate back to the operator rather than spending remaining cycles
unilaterally.
