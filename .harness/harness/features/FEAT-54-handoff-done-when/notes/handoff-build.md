# Handoff — FEAT-54-handoff-done-when, build → validate — 2026-09-02

## Next

Run the validation panel against the exact `review_sha` recorded in `feature.json`. The panel must assess the complete approved diff and return its own spec-compliance and code-quality verdict before any goal-check or ship work begins.

All planned tasks are already `done`; do not reopen build scope unless the panel returns a concrete must-fix. If it does, route the fix inside the validation phase, re-run the affected suites, commit it, and re-pin before re-review.

## Trust

- T-01–T-12 are all recorded `done` — `.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml` — verified-at d384ca91.
- QA c2 passed the configured unit and integration matrix at 2ac5fe95 — `.harness/harness/features/FEAT-54-handoff-done-when/notes/qa-build-c2.md` — verified-at 2ac5fe95.
- SIMPLIFY ran all four independent angles, applied one eligible cleanup, and left two advisory alternatives unapplied — `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-simplify-eng/digest.md` — verified-at d384ca91.
- Post-SIMPLIFY unit and integration suites pass with 24 and 44 discovered files — `.harness/harness/features/FEAT-54-handoff-done-when/notes/receipt-harness-dev-ops-simplify-apply.md` — verified-at d384ca91.
- The feature and every task issue were moved to Review — `.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml` and GitHub issues #1262–#1274 — UNVERIFIED.
- Rework is within the hard cap at 15 of 30 cycles; run count is above the informational 20-run budget — `.harness/harness/features/FEAT-54-handoff-done-when/feature.json` — UNVERIFIED.

## Dead ends

- Do not rerun the c4 amendment, goal-check, or plan panel; they are authoritative signed inputs.
- Do not treat the manual comprehension probe as a release gate; its registered status is `locally_run` and reporting-only.
- Do not fix the governed-agent `HARNESS_AGENT_TYPE` suite identity mismatch in this feature; main-session-equivalent runs unset it and pass.
- Do not apply SIMPLIFY's grammar-table or duplicate-presence alternatives during validation; both were explicitly left advisory.
- Do not move HEAD, merge, ship, or start the product goal-check from this seam.

## Working set

- .harness/harness/features/FEAT-54-handoff-done-when/plan.yaml
- .harness/harness/features/FEAT-54-handoff-done-when/BRIEF.md
- .harness/harness/features/FEAT-54-handoff-done-when/feature.json
- .harness/harness/features/FEAT-54-handoff-done-when/STATE.md
- .harness/harness/features/FEAT-54-handoff-done-when/notes/qa-build-c2.md

## Done when

Scope: validate the final build against the signed success criteria
Authority: approval:.harness/harness/features/FEAT-54-handoff-done-when/BRIEF.md#Approval
