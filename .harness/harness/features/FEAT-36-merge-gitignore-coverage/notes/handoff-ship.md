# Handoff — FEAT-36-merge-gitignore-coverage, ship → operator decision — written at f494553bd9fbb987b4a19f91dcf4c3f37253fe38, seq-ship-1

## Next

Ask the operator Q1 from `STATE.md`: authorize a lock-safe replacement/drop mechanism for the six accepted cap-bound Expertise ops, or direct that those ops remain unapplied. Then resume ship close-out from `runs/distill-validator/digest.md`; PLAN T-01 and BRIEF SC-01..SC-06 are already complete, so no product fix task remains.

## Trust

- The immutable reviewed candidate is exactly `f494553bd9fbb987b4a19f91dcf4c3f37253fe38` and review-c2 passed with no must-fix — `runs/review-c2-validator/digest.md` — verified-at f494553bd9fbb987b4a19f91dcf4c3f37253fe38
- SC-01 through SC-06 pass without waivers by their declared methods — `runs/goal-check-c1-product/digest.md` — verified-at f494553bd9fbb987b4a19f91dcf4c3f37253fe38
- Ship-refresh is inapplicable because `.harness/codebase/` does not exist — `runs/ship-refresh-product/digest.md` — UNVERIFIED
- Product and engineering distillation completed with no Expertise changes — `runs/distill-product/digest.md`; `runs/distill-eng/digest.md` — UNVERIFIED
- Security and UI Expertise additions pass the corpus checker; six code-reviewer/QA replacements remain unapplied — `runs/distill-validator/digest.md`; ship-review briefing affected-gates section — UNVERIFIED

## Dead ends

- Do not waive or silently drop the six accepted replacement ops; the validator owner judged them durable, and the mandated merge tool refused them — `runs/distill-validator/digest.md` — UNVERIFIED
- Do not change `expertise-merge.py` under FEAT-36 without operator-approved scope; it is outside approved PLAN T-01 and BRIEF REQ-01..REQ-05 — `plan.yaml`; `BRIEF.md` — verified-at f494553bd9fbb987b4a19f91dcf4c3f37253fe38
- Do not invoke `gh-sync.py ship` or backlog, close issues, create/merge a PR, or mark Done before ship acceptance — `feature.json` — UNVERIFIED

## Working set

- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/STATE.md`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/feature.json`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/distill-validator/digest.md`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-c1-product/digest.md`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/ship-review-c1.md`
