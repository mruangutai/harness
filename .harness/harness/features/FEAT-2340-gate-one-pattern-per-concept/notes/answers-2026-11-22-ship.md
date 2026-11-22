# Ship call — FEAT-2340 after validate (2026-11-22)

Decided by the advisor (fable-advisor), standing in for the operator under goal mode. Answers notes/ship-review-r-20261122-2-validate-validator.md.

- **Ship and merge.** The advisor independently checked the goal-check over pin 125a04f8, the code grades 4/5/5 on a file byte-identical to the pin, a production diff confined to the four approved files, and qa's receipts.
- **Backlog:** keep all 18 rows, B-1..B-18. B-6 and the `_FEATURE_ID_RE` half of B-8 open as decision tickets (keep the bootstrap exception, or allow a shared source; DEC-234), not as consolidation mandates.
- **Open notes:**
  - Q-03 is struck: the stray /private/tmp/ship-BUG-2349 worktree is gone, and BUG-2349 has merged.
  - Q-04 is struck: the BUG-2305 fix is merged, and the injection is by design.
- **Distill: run it.** The observations log carries recurring gotchas: the bash-write-guard cp refusal workaround, the `check-state --feature` worktree-cwd false absence, and the INV-17 main-session-direct exemption.
