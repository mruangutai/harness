# Handoff — BUG-1309-mirror-build-entry, ship → merge — written at a826673, seq-6

## Next

**Nothing is dispatchable, and no agent work remains.** The next act is the OPERATOR's: read
`notes/ship-review-2026-09-09-shipdecision.md` (amended 2026-09-09) and return ship / fix /
re-scope / stop plus struck IDs from its B-1..B-30 table. Its third item, the optional UAT step
confirmation, is CLOSED. On "ship" the act is the MAIN SESSION's: `gh-sync.py ship` **from the main
checkout** (it refuses a feature dir inside `.claude/worktrees/`) with that briefing as
`--body-file`, then the operator's merge, then the `post-merge` hook removes this worktree, then
distillation — never before the merge (DEC-145). Do not re-dispatch any lead.

## Trust

- SC-10 MET by the operator's own UAT, first inline relay 2026-09-09, transcribed append-only
  (45/0) — `notes/uat-BUG-1309-mirror-build-entry.md:362-403` — verified-at 4857818b
- Steps 3b, 5, 6 and 7 each carry an individual operator PASS from a SECOND inline relay ("flag uat
  pass for these four"), append-only, 60/0 by `git diff --numstat`, no heading moved; SC-10's
  verdict unmoved and nothing re-tested by an agent — `…uat-…md:405-463` — verified-at a826673
- 11 of 11 criteria met, SC-04 by operator ruling on inspected-correct source and NOT by new
  automated evidence — `notes/research-BUG-1309-c19-uat-sc10.md` — verified-at 4857818b
- Both approval fragments `approved`; plan re-sign `de04d841` lands after `d8f4dc49`, D-19 additive
  under R-7 §4 — `plan.yaml:3-6`, git history — verified-at 9c07f557
- Gate state at the pin: integration 36 ok / 0 FAIL / rc=0; panel PASS, `must_fix: []` —
  `notes/qa-c19-copy.md`, `runs/c19copy-validator/digest.md` — verified-at 4857818b
- `cycles_used` 18 of 17 — one OVER, from the lead's reported send-back in the recording round; and
  that run left no run dir, so its entry cites no digest — `feature.json` — verified-at a826673
- Test-first ORDER for 4857818b — **UNVERIFIED**, unrecoverable: one commit, no intermediate red —
  `notes/qa-c19-copy.md`, STATE.md Q12 — UNVERIFIED

## Dead ends

- Do not re-pin `review_sha`: only records were written after it — `feature.json` — at a826673
- Do not open a fix cycle: 18 of 17, raising the cap is the operator's (DEC-157) — `feature.json` —
  verified-at a826673
- Do not re-ask about UAT Steps 3b/5/6/7 or re-run a step to corroborate them; an agent re-test
  cannot substitute for their judgement — `…uat-…md:405-463` — verified-at a826673
- Do not touch `merge-gate.py`, `merge-gate.sh`, `tests/integration/test-merge-gate.py`: signed D-11
  carve-out, main-session-direct — `plan.yaml:47-49,73-75` — verified-at 4857818b
- Do not remove this worktree and do not run `gh-sync.py ship` from it; no answers file exists for
  either round and none may be sought (#671) — `…c19-uat-sc10.md` — verified-at a826673

## Working set

- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/ship-review-2026-09-09-shipdecision.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/uat-BUG-1309-mirror-build-entry.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/STATE.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/feature.json`

## Done when

Scope: the operator returns a ship instruction and backlog dispositions on the amended briefing
Authority: brief-sc:SC-10
