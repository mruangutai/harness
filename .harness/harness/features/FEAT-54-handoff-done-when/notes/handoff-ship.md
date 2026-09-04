# Handoff — FEAT-54, ship → blocked at CI — written at 91495a60, seq-1

## Next

Close F-01 in `notes/ship-review-2026-09-04-ship.md`: add `git config core.hooksPath
.claude/skills/harness/hooks` to the `Repository-state gate` step in `.github/workflows/tests.yml`,
before it runs `check-state.sh`. Main-session-direct — DEC-174 and this feature's own B-5
precedent. Then push, wait for `integration` green, merge PR #1285, pull `main`, and from the MAIN
checkout run `gh-sync.py record-pr <feature-dir>` (idempotent, `pr` already 1285) and `gh-sync.py
ship <feature-dir> --body-file notes/ship-review-2026-09-04-ship.md`, which lands milestone 43,
parent #1262 and sub-issues #1263–#1274 at the done station. Station stays `review` until merged.

## Trust

- `integration` fails on ONE step of eleven, `Repository-state gate`, on `INV-31: core.hooksPath is
  unset` — `gh run view 33877127272 --log-failed` — verified-at 91495a60. Every suite and every
  other gate passed on that run.
- The remedy works and suppresses nothing: fresh clone of the branch, hooksPath unset → exit 1 with
  that one violation; hooksPath set → exit 0 over 877 rows — `/tmp/feat54-ci-probe` (transient,
  re-clone to repeat) — verified-at 91495a60.
- PR #1285 is OPEN, `mergeable: MERGEABLE`, `mergeStateStatus: BLOCKED` — the block is the required
  check, not a conflict — `gh pr view 1285` — verified-at 91495a60.
- Final review PASS with no findings, and the product goal-check PASS on 15/15 —
  `notes/review-harness-code-reviewer-c6.md`, `notes/ship-review-2026-09-03-review-c6-validator.md`
  — verified-at df5f7ea1.
- `review_sha` stays df5f7ea1; commits after it touch only STATE.md, feature.json and this feature's
  notes — no code — `git diff --stat df5f7ea1 <tip>` — verified-at 91495a60.
- Local `main` is 4 commits AHEAD of `origin/main`, unpushed (FEAT-52/BUG-1157 records) —
  `git log --oneline main --not origin/main` — verified-at a12aa4e9.

## Dead ends

- Merging past the red check — `enforce_admins: true` with `contexts: ["integration"]`, so there is
  no override — `gh api repos/mruangutai/harness/branches/main/protection` — verified-at 91495a60.
- Re-running CI unchanged — the failure is deterministic, not flaky; INV-31 is false on every
  runner — verified-at 91495a60.
- Fixing it in `check-state.sh` instead — a CI branch inside the checker edits the DEC-174 tree and
  its test, to weaken a checker where a workflow line suffices — source: DEC-174, harness.json
  lanes.
- Running `gh-sync.py ship` or `record-pr` from this worktree — refused at exit 1 before any write,
  and it prints the main-checkout path — verified-at 91495a60 (expertise G-10).
- Removing this worktree from inside it — `git worktree remove` exits 0 from within the tree it
  deletes — source: harness-handoff, DEC-193.

## Working set

- `.harness/harness/features/FEAT-54-handoff-done-when/notes/ship-review-2026-09-04-ship.md`
- `.github/workflows/tests.yml`
- `.harness/harness/features/FEAT-54-handoff-done-when/feature.json`
- `.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml`
- `.agents/skills/harness/references/github-mirror.md`

## Done when

Scope: close the CI blocker and land PR #1285 on main
Authority: finding:.harness/harness/features/FEAT-54-handoff-done-when/notes/ship-review-2026-09-04-ship.md#F-01
Authority: brief-sc:SC-04
