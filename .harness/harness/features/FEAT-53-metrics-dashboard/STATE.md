# STATE

## Current

- feature: FEAT-53-metrics-dashboard
- run: .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-17-03-eng/digest.md
- squad: engineering
- status: building

Build entry is open and projected to Building. T-01 through T-09 where dependency-ready, plus T-23, T-24, T-25 and T-30, are recorded done. Engineering run 2026-09-17-03-eng closed PASS after transcribing six eligible stale-path amendments; its two internal send-backs moved the durable cycle total to 19 of 20. T-30 is accepted through BUG-1724's host task-result token stamp rather than transcript summation, with that implementation judgement in the ledger.

DEC-174 permits enforcement-layer work when made directly by the main session with explicit tests and human diff review; it prohibits dispatch through the self-checking team gates. T-25 used the plan's signed main-session-direct lane, so commit `c2483f7a` stands. The earlier stop was a corrected reading and is not a rework cycle under DEC-157; a later `continue: continue` judgement records the authoritative interpretation.

Historical ledger backfill is recorded for every 2026-09-01 FAIL run, and `notes/handoff-plan.md` carries the required `## Done when` shape. Next dependency-ready engineering work is T-10, T-18 and T-26. One recorded cycle remains before the hard ceiling.

## Open Questions

- Blocking before ship: how should the operator-approved historical `max_total_cycles: 20` ceiling be ledgered when `raise-cycles --to 20` refuses a retain ruling? The record must not be hand-edited; retain this as the known INV-39 tool contradiction.
