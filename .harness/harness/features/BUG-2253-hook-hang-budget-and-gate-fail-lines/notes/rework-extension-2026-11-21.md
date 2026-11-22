# Rework extension — 2026-11-21

Validate cycle 1 (run `2026-11-21-03-validate-validator`) returned FAIL after the signed rework budget (1 round / 45 min) was spent: 1 round and 22 minutes used.

The operator (Mike Ruangutai) chose the recommended disposition: **one more round, about 25 minutes**. The budget becomes 2 rounds / 70 min.

The round fixes the two counterexamples the panel confirmed by execution:

- **SC-01:** an echoed header-shaped line inside a file's output opens a block that never closes, which loses the genuine `FAIL` and a later `MUTATED`.
  - A closing line pops back to its matching header.
  - `MUTATED` lines are taken as the run directly before run_pool's own mutation sentence, not by block depth.
- **SC-02:** the watchdog can kill only after the child writes its pid, so a stall before readiness is unbounded.
  - At the deadline the watchdog kills every direct child of the test process, with no pid handshake.
  - Readiness stays a pass condition.

Each fix gets a regression for its counterexample.

Unit-kind coverage advisory: the operator chose to file a separate issue. It is not in scope for this round.
