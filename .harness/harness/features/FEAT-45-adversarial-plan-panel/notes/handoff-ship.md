# Handoff — FEAT-45-adversarial-plan-panel, ship → distill — written at 4624d1e, seq-1

## Next

Nothing is dispatchable until the operator merges. After the PR for
`feat/FEAT-45-adversarial-plan-panel` MERGES, the main session runs the distill mission
(DEC-145): dispatch product, eng and validator leads once each to read
`observations/` and distill into `.harness/expertise/`. Then confirm the required
post-merge check named in `notes/ship-review-2026-08-31.md` — the first reviewer
dispatch after merge must land a structured return (F5/V1), which also settles
SC-11, SC-12 and SC-16 on the first live `/harness-plan`.

## Trust

- Mirror is fully landed: 12 sub-issues + parent #983 at Done, milestone #33 closed,
  no HELD and no FAILED lines — `gh-sync.py ship` output this run — verified-at 4624d1e
- Backlog B-2..B-16 are issues #1054..#1068 in order, labelled `harness`+nature —
  `gh-sync.py backlog` output this run — verified-at 4624d1e
- `feature.json` `status: Done`, `pr: null` — written by `_record_status`/`_record_pr`;
  no merged PR exists on the branch yet — verified-at 4624d1e
- `review_sha` bdd5666 still governs: f89c90b and 4624d1e touch only the feature dir —
  STATE.md `## Current` — verified-at 4624d1e
- Cycles 10/10 spent, runs 17/20 — `feature.json` — verified-at 4624d1e. The briefing
  says 9/10 and 16/20; it predates the B-1 fix cycle and was accepted as read

## Dead ends

- Do NOT expect `check-state.sh` green. 42 VIOLATIONs this run, 32 of them INV-32 on
  plans approved before the panel existed (FEAT-45's own included) — `/tmp` run this
  session, `plan.yaml` T-07 intent "fires ONLY on a plan whose approval.status is
  approved" — verified-at 4624d1e. T-07's own `verify:` asserts `$? -ne 2`, so a
  non-zero exit is the designed state, not a regression
- Do NOT remove the worktree. The `post-merge` hook does it; INV-29 keys on
  `status: Done` **on the default branch**, so it stays quiet until merge —
  `worktree_terminal.py:273-275` — verified-at 4624d1e

## Working set

- `.harness/harness/features/FEAT-45-adversarial-plan-panel/feature.json`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/STATE.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/ship-review-2026-08-31.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/observations/`
