# Handoff — FEAT-54-handoff-done-when, validate → ship — 2026-09-03 c6

## Next

Present `notes/ship-review-2026-09-03-review-c6-validator.md` to the operator and have them run
`notes/uat-FEAT-54-SC-10.md` (~25 min, four separate judgments J1–J4). SC-10 is the only unmet
criterion and no agent may grade it. Record their four PASS/FAIL lines, then take their ship / fix /
re-scope / stop instruction. Do not merge, open a PR, or remove the worktree before that.

## Trust

- The c6 panel returned PASS with `must_fix: []`, all four readers ran, and code review Stage 2 ran
  for the first time in this feature at 90/90 —
  `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-03-review-c6-validator/digest.md`
  — verified-at dd55b3570c6a20f5ca1da016d6959752bd0ffc74.
- 14 of 14 non-UAT success criteria are met; SC-10 is `pending_uat` —
  `.harness/harness/features/FEAT-54-handoff-done-when/notes/research-FEAT-54-goalcheck-validate-c6.md`
  — verified-at dd55b3570c6a20f5ca1da016d6959752bd0ffc74.
- SC-04's literal repository-root command exits 0 with 478 lines and zero `Done when` lines — I ran
  it myself at this run's start, and QA re-ran it independently —
  `.harness/harness/features/FEAT-54-handoff-done-when/notes/qa-c6.md` — verified-at
  dd55b3570c6a20f5ca1da016d6959752bd0ffc74.
- `check-domain.sh` exits 0 on a blank-`Scope:` note when the claimed path is RELATIVE and cwd is
  outside the project; absolute path or cwd at the root both refuse at exit 2, and
  `CLAUDE_PROJECT_DIR` does not change it. My own four-arm measurement, cause is
  `os.path.abspath(path)` resolving against cwd —
  `.harness/harness/features/FEAT-54-handoff-done-when/notes/ship-review-2026-09-03-review-c6-validator.md`
  — verified-at 98436cd1, backlog row B-2.
- Ledger and disk disagree by three unrecorded run dirs and one absent dir; counts are approximate —
  `.harness/harness/features/FEAT-54-handoff-done-when/feature.json` — verified-at 98436cd1.

## Dead ends

- Do not rebase or merge. The branch is 29 ahead and 60 behind main; rebasing rewrites the pinned
  tip and voids the c6 verdict — `.harness/harness/features/FEAT-54-handoff-done-when/feature.json`
  — verified-at 98436cd1.
- Do not re-run the c6 panel or the goal-check. Both are complete, PASS, and on disk —
  `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-03-review-c6-validator/digest.md`
  — verified-at dd55b3570c6a20f5ca1da016d6959752bd0ffc74.
- Do not fix B-1 or B-2 inside this feature. Both remedies edit the gate tree DEC-174 marks
  main-session-direct — `.harness/harness/docs/DECISIONS.md` — verified-at 98436cd1.
- Do not distill Expertise. That runs at merge, not at close-out —
  `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md` — verified-at 98436cd1.

## Working set

- `.harness/harness/features/FEAT-54-handoff-done-when/notes/ship-review-2026-09-03-review-c6-validator.md`
- `.harness/harness/features/FEAT-54-handoff-done-when/notes/uat-FEAT-54-SC-10.md`
- `.harness/harness/features/FEAT-54-handoff-done-when/feature.json`
- `.harness/harness/features/FEAT-54-handoff-done-when/STATE.md`

## Done when

Scope: obtain the operator's four SC-10 judgments and their ship instruction
Authority: brief-sc:SC-10
