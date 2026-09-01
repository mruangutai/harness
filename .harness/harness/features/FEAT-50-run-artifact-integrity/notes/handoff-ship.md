# Handoff — FEAT-50-run-artifact-integrity, ship → closed — written at 852bb45d, seq-1

## Next

**Nothing is dispatchable from inside this checkout.** The main session lands this feature dir on
`main`, then removes the checkout **from outside it**. Seven tracked files differ from `main`, and
`feature-worktree.py remove` compares every one byte for byte, so copy all seven — `STATE.md`,
`feature.json`, `plan.yaml`, `notes/handoff-ship.md`,
`notes/ship-review-2026-09-01-ship.{md,html}`, `observations/harness-orchestrator.md`. Only two
lines actually change: `"pr": 1105` and `status: done`. Equivalently:

```
python3 .agents/skills/harness/bin/plan-merge.py set-feature-station \
    --file .harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml --station done
python3 .agents/skills/harness/bin/gh-sync.py record-pr \
    .harness/harness/features/FEAT-50-run-artifact-integrity --pr 1105
```

Same bytes either way — the worktree's copies came from these same two tools off the identical
base. Commit the seven paths, then `feature-worktree.py remove --id FEAT-50-run-artifact-integrity`
from the main checkout.

## Trust

- PR #1105 merged at `75bf0901`; tip `9f50ee66` is an ancestor of `origin/main` — `gh pr list
  --head feat/…` and `git merge-base --is-ancestor` — verified-at 852bb45d
- All 16 recorded cards read `done`, all 16 issues `CLOSED`/`COMPLETED`, milestone 35 closed with
  `open_issues: 0` — read back from the board and the API AFTER the ship writes — verified-at 852bb45d
- The worktree's records differ from `main` by exactly those two lines — `diff <(git show main:…)`
  on both files — verified-at 852bb45d
- Final validator run PASS, `must_fix: []`, `severity_max: med` —
  `runs/2026-09-01-1-validator/digest.md` — verified-at 852bb45d
- `check-state.sh` exits **1** with two FEAT-50 rows (INV-33 stale pin, INV-26 plan/board
  divergence); both close on the `main` station write — run in the main checkout — verified-at 852bb45d
- A governed write to the main checkout's FEAT-50 record is REFUSED at exit 2 —
  `check-domain.sh` hook-mode probe, quoted in STATE.md — verified-at 852bb45d
- SC-01…SC-21 are graded by the PANEL, not by a pm goal-check —
  `notes/qa-feat50-pinned-review.md`, `notes/review-harness-code-reviewer-feat50-pinned.md` —
  verified-at 852bb45d
- **SC-10 is UNVERIFIED** — no reviewer re-ran the suites, both recorded it as reported ground
  truth, and this closeout was told not to run project-wide suites — UNVERIFIED

## Dead ends

- The CURRENT `gh-sync.py` against this worktree — dies at `github.board.stations`, this
  checkout's `harness.json` predates FEAT-41's ordered-list format; use this checkout's own copy —
  measured exit 2 — verified-at 852bb45d
- Dropping `feature.json`'s legacy `status` key through `feature_json_write` — this checkout's
  schema still REQUIRES it, refuses at MergeRefusal(11). The `Write` route did it; the key is gone,
  which is what makes the byte-copy clean — measured — verified-at 852bb45d
- Committing the finalization on this branch — merged and two merges behind `main`, so it lands
  only through a second merge, which the dispatch forbids — `git log --oneline main -3` —
  verified-at 852bb45d

## Working set

- `.harness/harness/features/FEAT-50-run-artifact-integrity/notes/ship-review-2026-09-01-ship.md`
- `.harness/harness/features/FEAT-50-run-artifact-integrity/STATE.md`
- `.harness/harness/features/FEAT-50-run-artifact-integrity/feature.json`
- `.harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml`
