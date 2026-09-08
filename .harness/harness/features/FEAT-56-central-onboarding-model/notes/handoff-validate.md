# Handoff — FEAT-56-central-onboarding-model, validate → ship — written at f5790dea, seq-3

## Next

Ship acceptance is the main session's, not a squad's. It holds two things and only two: the
operator's SC-09 UAT verdict from `notes/uat-FEAT-56.md`, and which of the briefing's B-1..B-13
rows they strike. On PASS, open the PR against main, let the operator merge (`gates.merge` is
`user_gated`), then terminalize — `gh-sync.py record-pr`, `ship --body-file
notes/ship-review-2026-09-08-ship.md`, `backlog` for the unstruck rows — and confirm #206 and the
board land at done. Nothing is left to build.

## Trust

- Nine of ten SCs met at the pin, each RE-RUN there rather than inherited across the two pin moves —
  `notes/research-FEAT-56-goalcheck-ship-c0.md` — verified-at e6261060
- SC-09 is `pending_uat` and is the only criterion outstanding; `gates.uat` is
  `blocking_when_uat_criteria_exist`, so it genuinely gates the merge — `BRIEF.md` — verified-at e6261060
- The review panel returned `must_fix: []`, `severity_max: med`, `matrix_ok: true`, with SC-03 at
  6/6 and SC-04 at 15/15 one-per-file citations —
  `runs/2026-09-08-03-review-validator/digest.md` — verified-at 6f34e289
- Every advisory panel finding except V-8 was closed after that panel ran, so the panel's own pin is
  older than the code — `git log 6f34e289..HEAD` — verified-at e6261060
- Unit and integration suites both exit 0; unit's four `^FAIL ` lines are
  `test-factory-claim-mutation.py`'s by-design mutant output while that file passes —
  run directly — verified-at e6261060
- All four per-product-install claims are retired, including one the ship census missed in
  `_handoff_done_when_baseline_note` — `runs/2026-09-08-01-stalestrings-eng/digest.md` —
  verified-at e6261060
- Nine rework cycles of ten are spent; a further fix loop needs an operator decision —
  `feature.json` `cycles_used` — verified-at e6261060

## Dead ends

- Do not open the PR before the UAT verdict: the main session declined a draft PR explicitly —
  hub message 1578007e3388f042 — verified-at 2026-09-08
- Do not treat unit's four `^FAIL ` lines as a red suite; exit status is the only sound signal —
  `notes/qa-FEAT-56.md` adequacy_notes — verified-at e6261060
- Do not re-open #206 item 2 or the pilot product's committed `.harness/` subtrees: both are
  settled scope, the second re-confirmed by the operator mid-build — `BRIEF.md` `## Non-goals` —
  verified-at e6261060

## Working set

- .harness/harness/features/FEAT-56-central-onboarding-model/notes/ship-review-2026-09-08-ship.md
- .harness/harness/features/FEAT-56-central-onboarding-model/notes/uat-FEAT-56.md
- .harness/harness/features/FEAT-56-central-onboarding-model/notes/research-FEAT-56-goalcheck-ship-c0.md
- .harness/harness/features/FEAT-56-central-onboarding-model/feature.json
- .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml

## Done when

Scope: the operator's UAT verdict and backlog disposition are in hand
Authority: brief-sc:SC-09
Authority: brief-sc:SC-04
