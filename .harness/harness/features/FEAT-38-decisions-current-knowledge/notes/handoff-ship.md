# Handoff — FEAT-38, ship → closed — written at d04be92, seq-1

## Next

**Nothing in this feature.** All 28 tasks `done`, 17 of 17 live SCs met, both gates green, SC-13
answered by the operator, PR #996 merged. The only remaining acts are the main session's and are
listed under Trust: file the accepted backlog rows with `gh-sync.py backlog`, and remove this
worktree from OUTSIDE it. The next feature is FEAT-46, which was HELD pending this ship and
inherits the scope note in `notes/uat-FEAT-38.md`: DEC-138, DEC-174 and DEC-181 are all IN SCOPE
for its triage and this UAT pass must never be cited to exempt them.

## Trust

- SC-13 passed, operator-answered, not agent-graded — `notes/uat-FEAT-38.md:1-5` — verified-at d04be92
- `review_sha` `635cd3ba` still describes the merged code; the 16 files changed since the pin are
  feature notes, logs and observations, zero source — `git diff --name-only 635cd3ba d04be92` —
  verified-at d04be92
- PR #996 merged; `pr` recorded by `gh-sync.py record-pr`, not by hand — `feature.json:3` —
  verified-at d04be92
- Backlog B-25, B-26, B-39 are proposed, NOT filed — `notes/ship-review-2026-08-30-ship-close.md` —
  verified-at d04be92. Unaccepted rows die silently; `gh-sync.py backlog` is the main session's
- Worktree removal is the main session's or the post-merge hook's, never an agent's from inside —
  `harness/SKILL.md` "The worktree" — verified-at d04be92

## Dead ends

- Do NOT re-pin `review_sha` or re-run the panel: the pin was checked by filename against the tip
  and no source file moved — `git diff --name-only 635cd3ba d04be92` — verified-at d04be92
- Do NOT read `feature-worktree.py behind`'s exit 2 as a behind-answer: this repo is not declared in
  `fleet.yaml`, a config gap, not a gate result. Measure with
  `git rev-list --left-right --count main...HEAD` — verified-at d04be92
- Do NOT measure anything in this repo with `/usr/bin/grep`: it is `pi-uu-grep 0.2.0` and a
  line-leading `+` matches every line — B-26 in `STATE.md` — verified-at d04be92

## Working set

- `.harness/harness/features/FEAT-38-decisions-current-knowledge/feature.json`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/STATE.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-30-ship-close.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/uat-FEAT-38.md`
