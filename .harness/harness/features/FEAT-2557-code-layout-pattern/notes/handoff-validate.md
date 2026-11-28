# Handoff — FEAT-2557, validate → ship — written at afd20116, seq-4

## Next

The operator reads `notes/ship-review-r-20261127-2-validate-validator.md` and rules ship, fix,
re-scope or stop, striking any backlog rows B-1..B-6. On ship, open the PR from
`feat/FEAT-2557-code-layout-pattern`; the merge is the operator's. After merge, run `gh-sync.py ship`,
file the unstruck backlog rows, and run the distill mission.

## Trust

- validate c2 passed at afd20116 with an empty must_fix list and severity_max low — `runs/r-20261127-2-validate-validator/digest.md` — verified-at afd20116
- review_sha in feature.json is afd20116 — `feature.json` review_sha — verified-at afd20116
- Rework ruling spent: 1 of 1 round, 14 of 45 min — `feature-record.py spend` — verified-at afd20116
- check-state reports no FEAT-2557 violation from this worktree's copy — `.claude/skills/harness/bin/check-state.py` — verified-at afd20116

## Dead ends

- Validate runs record `tokens: null`: in a main-session-direct feature nothing stamps the validator lead's run — `feature.json` runs — verified-at afd20116

## Working set

- `.harness/harness/features/FEAT-2557-code-layout-pattern/notes/ship-review-r-20261127-2-validate-validator.md`
- `.harness/harness/features/FEAT-2557-code-layout-pattern/runs/r-20261127-2-validate-validator/digest.md`

## Done when

Scope: operator ships FEAT-2557
Authority: brief-perspective:.harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md#operator
