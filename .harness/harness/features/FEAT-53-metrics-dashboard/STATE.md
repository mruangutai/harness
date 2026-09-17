# STATE

## Current

- feature: FEAT-53-metrics-dashboard
- run: .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-16-02-eng/digest.md
- squad: engineering
- status: awaiting-user

Build entry is open and projected to Building. T-01 and T-05 are recorded done; main-session-direct T-02 is committed at `6f214eea`. The first engineering segment committed T-03, T-06 and T-23 and its checkpoint is complete with PASS. Its lead reports three internal send-backs, so closing the run would move recorded cycles from 14 to 17 of 20.

The run cannot legally close. Its append-only digest contains the original and corrected fenced returns. `validate-digest.py harness-eng-lead` accepts the last block, but `plan-merge.py record-amendments` exits 5 claiming there is no DIGEST mapping. The signed-task amendments must be transcribed before any station moves, while check-domain intentionally forbids replacing the recorded digest. DEC-174 forbids changing that tooling inside FEAT-53. A `continue: stop` judgement records this new harness finding class.

Historical ledger backfill is recorded for every 2026-09-01 FAIL run, and `notes/handoff-plan.md` now carries the required `## Done when` shape. The historical cycle ceiling remains 20 without a `budget_decisions` entry; the instructed retain ruling is rejected by `raise-cycles`, so INV-39 remains a known tool contradiction rather than a hand edit.

## Open Questions

- Blocking: may the harness owner repair `plan-merge.py record-amendments` to select the last valid fenced digest block, matching `validate-digest.py`, outside FEAT-53 and then resume this open run? Recommendation: yes; do not rewrite the append-only digest or weaken DEC-174.
- Blocking before ship: how should the operator-approved historical `max_total_cycles: 20` ceiling be ledgered when `raise-cycles --to 20` refuses a retain ruling? Recommendation: repair the ledger verb to accept the existing signed decision path, then record it without hand-editing `feature.json`.
