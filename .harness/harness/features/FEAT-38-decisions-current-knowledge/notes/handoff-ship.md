# Handoff — FEAT-38, ship → ship-blocked — written at 6be4e0b, seq-2

## Next

**Resolve PR #996's conflict with `origin/main`, then re-gate.** Not dispatchable to a lead as it
stands: it needs a HEAD move, which every governed agent is refused. The main session (or the
operator) merges `origin/main` into `feat/FEAT-38-decisions-current-knowledge` and resolves three
files — `.claude/skills/harness/bin/run-unit-tests.sh` and `.harness/harness.json` by hand (both
FEAT-38 and FEAT-44 registered test scripts and edited `test_kinds`), and
`.harness/harness/docs/DECISIONS-INDEX.md` by REGENERATING it with
`.claude/skills/harness/bin/gen-decisions-index.py`, never by hand-merging. Then re-pin `review_sha`
to the resolved tip and re-run the blocking qa gate (`gates.qa_gate`) via `harness-validator-lead`,
because the resolution touches source files the panel graded. The four-reviewer panel does not need
re-running unless that qa run turns up a finding: `severity_max` was `low` with no `must_fix`, and
`gates.review` is `advisory_unless_high`.

## Trust

- PR #996 is OPEN and CONFLICTING at head `6be4e0b` — `gh pr view 996 --json mergeable,mergeStateStatus`
  → `CONFLICTING`/`DIRTY` — verified-at 6be4e0b
- The real merge-base with `origin/main` is `7ebfc9e`, NOT `7a23d74`; branch is 19 behind the remote
  — `git rev-list --left-right --count origin/main...HEAD` → `19 55` — verified-at 6be4e0b
- Exactly three files conflict; `DECISIONS.md` auto-merges clean —
  `git merge-tree --write-tree --name-only origin/main HEAD` — verified-at 6be4e0b
- SC-13 passed, operator-answered, not agent-graded — `notes/uat-FEAT-38.md:1-5` — verified-at 6be4e0b
- Board is UNTOUCHED and the milestone is OPEN: `gh-sync.py ship` was never run — `feature.json`
  `status: Review` — verified-at 6be4e0b
- Backlog B-25, B-26, B-39 are proposed, NOT filed —
  `notes/ship-review-2026-08-30-ship-close.md` — verified-at 6be4e0b

## Dead ends

- Do NOT measure behind-ness against local `main`: it is 2 ahead / 19 behind `origin/main` and
  reports `0 52` against HEAD — `git rev-list --left-right --count main...origin/main` → `2 19` —
  verified-at 6be4e0b
- Do NOT read `feature-worktree.py behind`'s exit 2 as a behind-answer: this repo is absent from
  `fleet.yaml`, a config gap — verified-at 6be4e0b
- Do NOT treat `review_sha` `635cd3ba` as valid after the resolution: it is valid for the branch as
  it stands only — `git diff --name-only 635cd3ba d04be92` — verified-at 6be4e0b
- Do NOT measure anything here with `/usr/bin/grep`: it is `pi-uu-grep 0.2.0` and a line-leading `+`
  matches every line — B-26 in `STATE.md` — verified-at 6be4e0b

## Working set

- `.harness/harness/features/FEAT-38-decisions-current-knowledge/STATE.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/feature.json`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-30-ship-close.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/uat-FEAT-38.md`
