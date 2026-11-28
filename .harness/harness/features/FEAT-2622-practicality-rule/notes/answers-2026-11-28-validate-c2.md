# FEAT-2622 validate run 03: operator answers, 2026-11-28

Source: run `2026-11-28-03-validate-validator` (FAIL, MF-1..MF-4, VAL-OQ-03, VAL-OQ-04). The operator took the main session's recommendations ("go with your recommendations. proceed with fix round 2").

- **MF-1..MF-4: fix all four** in fix round 2, the last round under the 2-round / 90-minute ruling. Fixes run main-session-direct (DEC-174).
- **VAL-OQ-03: residual accepted.** A lead that drops a member's must_fix from its own union is not caught. Closing that case needs a member-shape contract change. The lead's must_fix union is trusted the same way on base's resolved-row path and in every other roll-up.
- **VAL-OQ-04: noted.** If round 2 does not close MF-1 and MF-2, the next step is an operator ruling, not a third round.
