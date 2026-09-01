# Handoff — FEAT-50-run-artifact-integrity, ship → closed — written at 9f50ee66, seq-1

## Next

**Nothing is dispatchable from inside this checkout. The remaining act is the main session's
finalization, and it is two commands plus a copy.** Run them in the MAIN checkout, on `main`:

```
python3 .agents/skills/harness/bin/plan-merge.py set-feature-station \
    --file .harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml --station done
python3 .agents/skills/harness/bin/gh-sync.py record-pr \
    .harness/harness/features/FEAT-50-run-artifact-integrity --pr 1105
```

then copy `notes/ship-review-2026-09-01-ship.{md,html}`, `notes/handoff-ship.md` and `STATE.md`
from this worktree into the same feature dir on `main`, commit those paths, and remove this
worktree **from outside it**. The briefing's *Terminal state* section carries the same list with
its reasons.

## Trust

- PR #1105 merged at `75bf0901`; tip `9f50ee66` is an ancestor of `origin/main` — `gh pr list
  --head feat/FEAT-50-run-artifact-integrity` and `git merge-base --is-ancestor` — verified-at 9f50ee66
- All 16 recorded cards read `done` and all 16 issues read `CLOSED`/`COMPLETED`; milestone 35
  `state: closed`, `open_issues: 0` — read back from the board and the API after the ship writes,
  not inferred from them — verified-at 9f50ee66
- Final validator run PASS, `must_fix: []`, `severity_max: med` —
  `runs/2026-09-01-1-validator/digest.md` — verified-at 9f50ee66
- `check-state.sh` exits **1** with two FEAT-50 rows (INV-33 stale pin, INV-26 plan/board
  divergence); both close on the `main` station write — run directly in the main checkout —
  verified-at 9f50ee66
- A governed write to the main checkout's FEAT-50 record is REFUSED at exit 2 —
  `check-domain.sh` hook-mode probe, message quoted in STATE.md — verified-at 9f50ee66
- SC-01…SC-21 are graded, but by the PANEL, not by a pm goal-check —
  `notes/qa-feat50-pinned-review.md`, `notes/review-harness-code-reviewer-feat50-pinned.md` —
  verified-at 9f50ee66
- **SC-10 is UNVERIFIED.** No reviewer re-ran the suites; both recorded it as reported ground
  truth, and this closeout was instructed not to run project-wide suites — UNVERIFIED

## Dead ends

- Running the CURRENT `gh-sync.py` against this worktree — it dies at
  `github.board.stations` because this checkout's `harness.json` predates FEAT-41's ordered-list
  format — measured, exit 2 — verified-at 9f50ee66
- Removing `feature.json`'s legacy `status` key here — this checkout's own schema REQUIRES it, so
  `feature_json_write` refuses at MergeRefusal(11) — measured — verified-at 9f50ee66
- Committing the finalization on this branch — merged and two merges behind `main`, so it could
  only land through a second merge, which the dispatch forbids — `git log --oneline main -3` —
  verified-at 9f50ee66

## Working set

- `.harness/harness/features/FEAT-50-run-artifact-integrity/notes/ship-review-2026-09-01-ship.md`
- `.harness/harness/features/FEAT-50-run-artifact-integrity/STATE.md`
- `.harness/harness/features/FEAT-50-run-artifact-integrity/feature.json`
- `.harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml`
