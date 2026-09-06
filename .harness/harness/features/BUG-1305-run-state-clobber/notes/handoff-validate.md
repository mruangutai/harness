# Handoff — BUG-1305-run-state-clobber, validate → ship — written at e77b30ca, seq-2

## Next

Present `notes/ship-review-2026-09-05-validate-c2.md` to the operator and take the one open ruling:
VL-01 accepted as a named residual (backlog row B-1), or a thirteenth cycle authorised to mirror the
F-04 fix for `RE_STATE_YAML` ahead of `_edit_reconstructed_content`. On acceptance, ship is the main
session's: `gh-sync.py ship <feature-dir> --body-file <that briefing>`, then merge, then the
`post-merge` hook removes this checkout and feature-close distillation follows.

## Trust

- 11 of 11 live success criteria MET at the pin, re-derived not carried — runs/goalcheck-build-c2-product/digest.md — verified-at e77b30ca
- Delta panel readers all PASS; lead verdict ESCALATE on VL-01 alone — runs/review-c2-validator/digest.md — verified-at e77b30ca
- `review_sha` e77b30ca is code-identical to Main's fix commit 2728aa20 — `git diff --stat 2728aa20 e77b30ca` outside the feature dir is empty — verified-at e77b30ca
- Mechanical grade exit 0; unit 28 files, integration 46 files, state checker exit 0 notes-only — runs/review-c2-validator/digest.md — Main-reported, not re-run by me — UNVERIFIED
- This host's Edit refuses a nonexistent file_path, so the Edit-create class is dormant here — notes/receipt-harness-dev-ops-editprobe-c1.md — verified-at e77b30ca

## Dead ends

- Fixing anything with a squad: every surface is main-session-direct under DEC-174 — plan.yaml `lanes.rows` — verified-at e77b30ca
- A directory-shaped Bash guard for SEC-01 in this feature: ruled a follow-up, filed as #1376 — notes/review-harness-security-reviewer-c2.md — verified-at e77b30ca
- Re-running the panel or the suites for the SC-11 evidence repair: production bytes unchanged by it — Advisor ruling relayed by Main — UNVERIFIED
- Spending a cycle on the regression-delta citation rot: operator ruled against it — briefing row B-7 — verified-at e77b30ca

## Working set

- .harness/harness/features/BUG-1305-run-state-clobber/notes/ship-review-2026-09-05-validate-c2.md
- .harness/harness/features/BUG-1305-run-state-clobber/runs/review-c2-validator/digest.md
- .harness/harness/features/BUG-1305-run-state-clobber/runs/goalcheck-build-c2-product/digest.md
- .harness/harness/features/BUG-1305-run-state-clobber/feature.json
- .harness/harness/features/BUG-1305-run-state-clobber/BRIEF.md

## Done when

Scope: operator rules on VL-01 and the ship decision
Authority: brief-sc:SC-01
