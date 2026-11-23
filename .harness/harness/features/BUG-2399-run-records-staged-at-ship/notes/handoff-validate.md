# Handoff — BUG-2399-run-records-staged-at-ship, validate → ship — written at 5a1becd6, seq-3

## Next

Validate is clean at review_sha 74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd (validate c2, run
2026-11-23-03-fix-validator, PASS, no must_fix, no open questions). The briefing is
notes/ship-review-2026-11-23-03-fix-validator.md. The operator decides ship / fix / re-scope /
stop; merge, PR and deploy are the main session's. On ship acceptance, unstruck backlog rows
B-1 and B-2 in the briefing become issues (DEC-138). No push was made.

## Trust

- Validate c2 PASS over 74e6896c: five readers ran, `severity_max: none`, `matrix_ok: true`, SC-01..03 and DEC-238 met — runs/2026-11-23-03-fix-validator/digest.md (validate-digest.py: digest ok) — verified-at 5a1becd6
- qa c2 runner receipt tested_commit 74e6896c — runs/2026-11-23-03-fix-validator/qa/manifest-unit.json — verified-at 5a1becd6
- MF-1 fixed main-session-direct at 74e6896c, test-first; red 3 / green 40 — notes/red-first-T-01.md §c1 fix; code c2 pruner:186–200, 238–243 — reader-verified, not re-run by the orchestrator
- SC-03 removal clause vacuous by operator ruling — notes/answers-2026-11-23-c1-ruling.md — verified-at 5a1becd6
- Rework ruling 1 round / 45 min; spent 1 round, 16 min — feature-record.py spend at close — verified-at 5a1becd6
- cycles_used 0: run 02 re-close at 1 refused (its digest binds 0); the round is the `regate` judgement — feature.json judgements[] — verified-at 5a1becd6

## Dead ends

- `run-start --regate` for run 03 was refused as not owed: run 02's verdict is ESCALATE, not FAIL, so the regate was written with the `judgement` verb before run-start — feature-record.py output — verified-at 5a1becd6
- Run 03 was registered as `2026-11-23-03-fix-validator` (token `-fix-`, counted by spend) but dispatched as HARNESS-MISSION: validate: the fix team hosts a dev member and T-01 is main-session-direct with its fix already committed, and DEC-255 trusts a `fix` receipt only under a `fix-c<N>-validator` id. The validate lineage rule accepted the receipt — validate-digest.py — verified-at 5a1becd6

## Working set

- .harness/harness/features/BUG-2399-run-records-staged-at-ship/notes/ship-review-2026-11-23-03-fix-validator.md
- .harness/harness/features/BUG-2399-run-records-staged-at-ship/runs/2026-11-23-03-fix-validator/digest.md
- .harness/harness/features/BUG-2399-run-records-staged-at-ship/feature.json
- .harness/harness/features/BUG-2399-run-records-staged-at-ship/STATE.md

## Done when

Scope: operator has read the briefing and issued ship / fix / re-scope / stop
Authority: brief-perspective:.harness/harness/features/BUG-2399-run-records-staged-at-ship/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2399-run-records-staged-at-ship/BRIEF.md#code maintainer
