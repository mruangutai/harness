# Handoff — FEAT-48, ship → closed — written at db571edf + this commit, seq-1

## Next

**Nothing is dispatchable from inside this checkout.** The main session runs the ship, in this
order (full command lines are in this run's DIGEST):

1. `gh pr create --base main --head feat/FEAT-48-parallel-safe-suite --body-file notes/pr-body-FEAT-48.md`
2. `gh-sync.py record-pr <this worktree's feature dir> --pr <N>`, commit `feature.json`, push —
   this is what keeps `main` clean when the sweep runs `_record_pr` later.
3. Wait for the **`integration`** check. It is the only required context on `main`.
4. Merge. Then `git checkout main && git pull` **in the main checkout** — the `post-merge` hook
   runs `gh-sync.py ship` and removes this worktree in one act.
5. `gh-sync.py ship <main checkout feature dir> --body-file notes/ship-review-2026-09-02-c9.md` —
   the sweep's own ship passes no body, so the review is posted only by this second call.
6. `gh-sync.py backlog <main checkout feature dir> <the 15 items>` — **exactly once**, not idempotent.
7. Distillation (DEC-145) is dispatched after the merge, from the main checkout, onto a branch.

## Trust

- Station `done` is written on the branch, deliberately, so the landed plan makes the sweep fire —
  `worktree_terminal.py:388-393` reads `status` from the default branch — verified-at db571edf
- `review_sha 27f8105b` unmoved; branch is 31 ahead / **0 behind** `origin/main`, tree clean —
  `git rev-list --left-right --count`, `git status --porcelain` — verified-at db571edf
- Approval reads `approved` in **both** artifacts — `BRIEF.md:236`, `plan.yaml:7-10` — verified-at db571edf
- All 15 staged items parse as `nature:title` with a nature `gh-sync` accepts — awk over
  `notes/backlog-items-FEAT-48.txt`, 15 lines, 0 bad — verified-at db571edf
- Receipts are complete, so `gh-sync.py open` must NOT be re-run — `feature.json` `github` holds
  milestone 40, parent 1191, six sub-issues — verified-at db571edf
- Every gate PASS at the pin is the validate seam's, re-taken there, not re-measured here —
  `notes/validate-evidence-c9.md`, `notes/research-FEAT-48-goalcheck-validate-c9.md` — verified-at 27f8105b
- The suite was **not** re-run this phase; the dispatch forbade it — UNVERIFIED

## Dead ends

- `gh-sync.py ship` from this checkout — refuses at **exit 1** before any write, naming the main
  checkout's path — run here, output quoted in STATE.md — verified-at db571edf
- `gh-sync.py open` / `status done` / `backlog` from here — owner is the main session, and a
  `status done` before the merge would put the card at Done on an unmerged branch —
  `references/github-mirror.md` owner table — verified-at db571edf
- The 21 run digests under `runs/` — ignored by `.gitignore:7`, so they die with this worktree and
  cannot feed the distillation skim; dispatch it against `notes/` and `observations/` instead —
  `git check-ignore -v` — verified-at db571edf
- A closing keyword for parent #1191 or any sub-issue — D-23 gives those to `ship`'s station write;
  only `Closes #1053` is in the PR body — verified-at db571edf

## Working set

- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/pr-body-FEAT-48.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/backlog-items-FEAT-48.txt`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/ship-review-2026-09-02-c9.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/answers-2026-09-02-c9.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/STATE.md`
