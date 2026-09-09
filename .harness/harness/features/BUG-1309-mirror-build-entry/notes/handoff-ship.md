# Handoff — BUG-1309-mirror-build-entry, ship → merge — written at 9c07f557, seq-5

## Next

**Nothing is dispatchable, and no agent work remains.** The next act is the OPERATOR's: read
`notes/ship-review-2026-09-09-shipdecision.md` and return (a) ship / fix / re-scope / stop,
(b) struck backlog IDs from its B-1..B-29 table, and optionally (c) whether UAT Steps 3b, 5, 6 and 7
also passed. On "ship", the act belongs to the MAIN SESSION, not to a successor orchestrator:
`gh-sync.py ship` run **from the main checkout** (it refuses at exit 1 when the feature dir resolves
inside `.claude/worktrees/`) with that briefing as `--body-file`, then the operator's own merge, then
the `post-merge` hook removes this worktree, then a distill dispatch — never before the merge
(DEC-145). Do **not** re-dispatch any lead: SC-10 is closed and the goal-check is complete at 11 of
11 (`notes/research-BUG-1309-c19-uat-sc10.md`).

## Trust

- SC-10 is MET by the operator's own UAT, relayed inline by the main session on 2026-09-09 and
  transcribed append-only (45 insertions / 0 deletions, `git diff --numstat`) —
  `notes/uat-BUG-1309-mirror-build-entry.md:360-403` — verified-at 4857818b
- The relay carried an overall "pass" plus the Step 3 wording judgement and **no per-step readout**
  of Steps 3b/5/6/7; that limit is recorded, not inferred away —
  `notes/research-BUG-1309-c19-uat-sc10.md` §"Does the recording move any criterion" — verified-at
  4857818b
- All eleven criteria met, SC-04 by operator ruling on inspected-correct source and NOT by new
  automated evidence — `notes/research-BUG-1309-c19-uat-sc10.md` SC table — verified-at 4857818b
- Both approval fragments read `approved`, and the plan's re-sign commit `de04d841` lands AFTER the
  D-13..D-15 amendment `d8f4dc49`, so the signature covers them; D-19 was appended additively under
  R-7 §4, which owes no re-signature — `plan.yaml:3-6`, git history — verified-at 9c07f557
- Gate state at the pin: integration 36 ok / 0 FAIL / rc=0, panel PASS with `must_fix: []` and
  `severity_max: med` — `notes/qa-c19-copy.md`, `runs/c19copy-validator/digest.md` — verified-at
  4857818b
- Test-first ORDER for 4857818b — **UNVERIFIED**, and unrecoverable from the record: one commit, no
  intermediate red — `notes/qa-c19-copy.md`, STATE.md Q12 — UNVERIFIED

## Dead ends

- Do not re-pin `review_sha`: this phase wrote only feature-dir artifacts, so moving the pin would
  claim the panel reviewed a tree it never saw — `feature.json` — verified-at 9c07f557
- Do not open a fix cycle for any residual: `cycles_used` is 17 of 17 and raising the cap is the
  operator's decision (DEC-157) — `feature.json` — verified-at 9c07f557
- Do not touch `merge-gate.py`, `merge-gate.sh` or `tests/integration/test-merge-gate.py`: the signed
  D-11 carve-out puts all three main-session-direct — `plan.yaml:47-49,73-75` — verified-at 4857818b
- Do not run `feature-worktree.py remove`, and do not run `gh-sync.py ship` from this worktree — it
  refuses there and names the checkout to use instead — skill `harness` — verified-at 9c07f557
- Do not go looking for an answers file: none was named and none exists for this round (issue #671)
  — `notes/research-BUG-1309-c19-uat-sc10.md` §Non-modification — verified-at 9c07f557

## Working set

- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/ship-review-2026-09-09-shipdecision.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/research-BUG-1309-c19-uat-sc10.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/STATE.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/feature.json`

## Done when

Scope: the operator returns a ship instruction and backlog dispositions on the 2026-09-09 briefing
Authority: brief-sc:SC-10
