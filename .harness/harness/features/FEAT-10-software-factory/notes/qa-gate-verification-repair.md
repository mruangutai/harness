# QA gate verification repair — FEAT-10

Part A: appended ` <!-- ok-stale -->` to line 34 of
`notes/review-harness-qa-qa2-validator.md`, no other change. Confirmed via check-docs.sh below.

## Part B — three gates, exit codes

1. `python3 .claude/skills/harness/bin/validate-digest.py lead .harness/features/FEAT-10-software-factory/runs/panel-validator/digest.md`
   → stdout: `digest ok` — **exit 0** (expected 0, matched).

2. `.claude/skills/harness/bin/check-state.sh`
   → **exit 1**. VIOLATION count: **before 5 (per dispatch), after 4** — matches expectation.
   No VIOLATION line names FEAT-10. All four remaining are FEAT-04/FEAT-07 lead-digest-contract
   violations (DEC-156):
   ```
   VIOLATION  features/FEAT-07-verify-teeth-batch-probe/runs/goalcheck-product/digest.md: does not satisfy the lead digest contract — a successor reads this file, not the transcript (DEC-156). Run bin/validate-digest.py lead on it for reasons.
   VIOLATION  features/FEAT-07-verify-teeth-batch-probe/runs/sc07-fix2-product/digest.md: does not satisfy the lead digest contract — a successor reads this file, not the transcript (DEC-156). Run bin/validate-digest.py lead on it for reasons.
   VIOLATION  features/FEAT-04-decisions-index/runs/2026-08-02-13-product/digest.md: does not satisfy the lead digest contract — a successor reads this file, not the transcript (DEC-156). Run bin/validate-digest.py lead on it for reasons.
   VIOLATION  features/FEAT-04-decisions-index/runs/2026-08-02-15-product/digest.md: does not satisfy the lead digest contract — a successor reads this file, not the transcript (DEC-156). Run bin/validate-digest.py lead on it for reasons.
   ```
   (check-state.sh also emits many `note` lines, unrelated to VIOLATION count, left untouched.)

3. `.claude/skills/harness/bin/check-docs.sh` (run after Part A)
   → stdout: `checked 62 superseded pattern(s) across 303 file(s). no stale statements found.`
   — **exit 0** (expected 0, matched).

## Summary

- Part A repair confirmed effective: check-docs.sh now exits 0.
- Digest repair (VERDICT PASS→FAIL) confirmed valid by validate-digest.py: exit 0.
- check-state.sh VIOLATION count dropped 5→4 as expected; FEAT-10 no longer named; remaining 4
  are FEAT-04/FEAT-07, not this feature's to repair, left untouched.
