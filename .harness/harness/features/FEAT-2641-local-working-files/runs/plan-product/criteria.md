# Send-back criteria — plan-product (written before any member return)

## draft (pm)
Send back if any of:
- BRIEF.md or plan.yaml missing, or either not `pending`; `plan-merge.py check` not reported exit 0.
- An operator goal constraint from the dispatch has no SC: (1) notes/ (incl. prototypes, mockups), project .harness/notes/, runs/, observations/ gitignored + existing tracked untracked without history rewrite; (2) notes/runs-reading CI gates removed with tests, runtime local-disk hooks kept; (3) cleanup routine at distill final step after merge-distill + at abandon/reject/skip-distill, ownerless project notes never auto-deleted; (4) feature.json/plan.yaml/BRIEF.md/STATE.md stay committed.
- A task changing a gate/hook/validator/test has no DEC-174 execution lane named.
- Any of the five `## Not yet specified` items is neither resolved as a plan decision nor returned as an open question with one recommendation.
- `decisions_affected:` omits DEC-156, DEC-238 or DEC-257, or no task owns DECISIONS.md.
- A task cites a grilling line anchor (a55453f38d) without re-resolution in the worktree (file:symbol or quoted content instead).

## readers
- scope / design: send back only on an invalid return (missing VERDICT, no note at output path, findings without `kind`).
- should-not-exist: send back only on an unparseable block; unresolvable → skip and record `status skipped`.

## apply
- record-panel and check not both exit 0; a substance finding silently dropped without disposition.

## goalcheck
- Note missing at notes/research-FEAT-2641-local-working-files-goalcheck-plan.md, or a perspective without a grade.
