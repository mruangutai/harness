# Observations - harness-pm

- 2026-08-25: FEAT-41 SC-02 carried a hand-typed grep count that drifted twice (31 -> 26, split 13/7) while the criterion itself named the command; re-running it gave 27 with 11/9. A criterion that quotes its own command has no excuse for a number not read off that command.
- 2026-08-25: FEAT-41 R-01 repeated F-03 exactly: a task deleted a shared name by SPAN, and the name had one use outside the span. The post-condition grep named only one of the two dead identifiers, so the plan asserted a deletion no gate measured. When a task deletes an identifier, grep every dead identifier in the verify, and address deletions by name rather than by line span.
