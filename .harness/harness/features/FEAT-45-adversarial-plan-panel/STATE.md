# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/c4-validator/state.yaml
- squad: none
- status: Done

SHIPPED on the operator's explicit acceptance of `notes/ship-review-2026-08-31.md`, with no
backlog row struck. The ship phase is closed; one external gate remains and it is the operator's:
**the PR and the merge**. Nothing is pushed and `pr` is still `null` — `gh-sync.py record-pr`
found no merged pull request on `feat/FEAT-45-adversarial-plan-panel`.

The mirror is fully landed. `gh-sync.py open` was a clean no-op — milestone #33, parent #983 and
all twelve task sub-issues were already recorded. `gh-sync.py ship --body-file` posted the briefing
verbatim on #983, moved every recorded card to Done (#984..#994, #1051, then parent #983), closed
milestone #33, and wrote `feature.json` `status: Done`. It reported **no HELD and no FAILED line**:
every recorded card reached the done station. Its board audit returned 14 pre-existing findings,
all about OTHER features' parents and four unlabelled `not_planned` closes; ship never gates on
the audit, and the one FEAT-45 line it printed was read before this run's own status write.

All fifteen accepted backlog rows are durable issues, in row order:
B-2 #1054, B-3 #1055, B-4 #1056, B-5 #1057, B-6 #1058, B-7 #1059, B-8 #1060, B-9 #1061,
B-10 #1062, B-11 #1063, B-12 #1064, B-13 #1065, B-14 #1066, B-15 #1067, B-16 #1068 —
each labelled `harness` plus its nature, no milestone, per DEC-138.

`review_sha` bdd5666 still governs the shipped work. HEAD is 4624d1e; f89c90b and 4624d1e are
record-only and every path they touch is inside the feature directory, so the cycle-4 panel PASS
at `severity_max: low` with no `must_fix` is unmoved. Cycles 10 of 10, runs 17 of 20 — the
briefing's "9 of 10 / 16 of 20" predates the B-1 fix cycle and was accepted as read; `feature.json`
is the authority.

Three success criteria stay deferred by their own text — SC-11, SC-12, SC-16 — plus the F5/V1
confirmation that a code reviewer can land a structured return from a worktree, which cannot run
until the hook resolves `main`'s installed validator. The first live `/harness-plan` after merge
settles all four. Feature-close distillation runs at MERGE, not here (DEC-145).

## Open Questions

- OPERATOR GATE, the only one left: open the PR for `feat/FEAT-45-adversarial-plan-panel` and merge
  it. The `post-merge` hook removes this worktree; INV-29 keys on `status: Done` reaching the
  default branch, so it stays quiet until then and REFUSES afterwards if the checkout survives.
- POST-MERGE CHECK, required and recorded in the briefing so it cannot lapse: the first reviewer
  dispatch after merge must be confirmed to land a structured return. That one run also settles
  SC-11, SC-12 and SC-16. — harness-orchestrator
- INV-32 is red for THIRTY-TWO approved plans, FEAT-45's own included, because none carries a
  `panel:` block and none can — every one was signed before the panel existed. This is the gate
  behaving as T-07's approved intent specifies ("fires ONLY on a plan whose approval.status is
  approved", no grandfather clause), and T-07's own `verify:` asserts `$? -ne 2` precisely because
  a non-zero exit was expected. Not a defect and not a ship blocker; raised because 32 permanent
  VIOLATION lines at every session entry is signal dilution the briefing never quantified for the
  operator, and it was not among the rows offered to strike. — harness-orchestrator
- Every other residual from this feature is now a GitHub issue and is tracked there, not here:
  the five harness defects raised during build and validate are B-2/B-3/B-4/B-5/B-6 (#1054..#1058),
  INV-26's structural redness is B-7 (#1059), the `plan-panel.yaml` drift restatement is B-11
  (#1063), and the five pre-existing DEC-154/DEC-156 plan-phase artifacts are B-13 (#1065).
  M4 is CLOSED — finding ids were widened to 128-bit before ship. M5 is unfiled by the operator's
  own reading of the briefing; M6 and M7 are B-15 (#1067). — harness-orchestrator
