# FEAT-2622 validate run 02: operator answers, 2026-11-28

Source: run `2026-11-28-02-validate-validator` (FAIL; MF-1..MF-5, VAL-OQ-01, VAL-OQ-02). The main session put a recommendation on each, and the operator took every one ("go with your recommendations").

- **MF-1..MF-5: fix all five** in fix round 1, main-session-direct (DEC-174), inside the 2-round / 90-minute ruling.
- **VAL-OQ-01: SC-07 reads** "no other feature's path and no rewritten historical `runs/` record". This feature's own new run records, which DEC-257 requires to be committed, are lawful. No change to the signed text.
- **VAL-OQ-02: no separate fix.** The readers yield against the control plane's pre-feature schema until this feature merges, so they carried exposure in each finding's `why`. The merge closes the gap.
- **Measuring the workflow effect: option 1.** No reporting tooling in this feature. After about five more features ship, the main session compares rework rounds and minutes, contrived-only fix rounds, operator escalations and lead triage use against the pre-rule baseline, and counts escapes: post-ship bugs traced to a discounted finding. Filed as a backlog row at ship.
