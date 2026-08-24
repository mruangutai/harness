# Handoff — FEAT-36-merge-gitignore-coverage, ship → acceptance — written at 8635090d648cb95f9e9bc2db9dd6214ef3aa2f3e, seq-ship-2

## Next

Present `notes/ship-review-c1.md` to the operator and collect the ship, fix, re-scope, or stop decision. PLAN T-01 and BRIEF SC-01..SC-06 are complete; if the operator accepts ship, the main session owns PR/merge, backlog B-1 handling, `gh-sync.py ship`, and final Done state.

## Trust

- The immutable reviewed candidate is exactly `f494553bd9fbb987b4a19f91dcf4c3f37253fe38` and review-c2 passed with no must-fix — `runs/review-c2-validator/digest.md` — verified-at f494553bd9fbb987b4a19f91dcf4c3f37253fe38
- SC-01 through SC-06 pass without waivers by their declared methods — `runs/goal-check-c1-product/digest.md` — verified-at f494553bd9fbb987b4a19f91dcf4c3f37253fe38
- Ship-refresh is inapplicable because `.harness/codebase/` does not exist — `runs/ship-refresh-product/digest.md` — verified-at 8635090d648cb95f9e9bc2db9dd6214ef3aa2f3e
- Product and engineering distillation completed with no Expertise changes — `runs/distill-product/digest.md`; `runs/distill-eng/digest.md` — verified-at 8635090d648cb95f9e9bc2db9dd6214ef3aa2f3e
- Security O-09 and UI G-11 are preserved and checked; all six refused replace ops are closed as unapplied/not permitted — `runs/distill-c1-validator/digest.md` — UNVERIFIED

## Dead ends

- Do not apply the six refused replacements by direct or whole-file write; harness-distill requires the merge tool, and the available tool cannot express replace/drop — `runs/distill-c1-validator/digest.md` — UNVERIFIED
- Do not create a second backlog row for the stale P-06 wording or merge-tool capability gap; both are non-gating close-out dispositions — `runs/distill-c1-validator/digest.md` — UNVERIFIED
- Do not invoke `gh-sync.py ship` or backlog, close issues, create/merge a PR, or mark Done before operator ship acceptance — `feature.json` — UNVERIFIED

## Working set

- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/STATE.md`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/feature.json`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/distill-c1-validator/digest.md`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-c1-product/digest.md`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/ship-review-c1.md`
