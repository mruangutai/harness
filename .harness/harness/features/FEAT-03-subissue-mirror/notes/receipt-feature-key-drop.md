Removed 24 key(s) from FEAT-03-subissue-mirror's feature.yaml because each had no reader; FEAT-14 closed the key set to eleven. This receipt is the only durable record of their values.

## status collapse (the pre-collapse pair survives only here)

- old status: `shipped`
- old phase: `ship`
- new status: `Done`  (rule)

## value normalization

- `pr`: `'none'` (string) -> `null`

## removed keys, full values

```yaml
cost_usd: 358
max_cost_usd: 120
pending:
- USER DECISION on notes/ship-review-2026-07-31-16.md — ship / fix / re-scope / stop
- SC-13 — main-session SKILL.md edit, pre-ship, no agent domain covers it (Q13)
- 'B-13 CANDIDATE, new at run 17-19 — validate-digest.py:493-497 rejects `members:
  []` with a non-zero steps_run, so a lead''s self-executed step has no truthful encoding.
  Raised by both product-lead and validator-lead independently. Not in the signed
  briefing; reaches the user via the run digest only'
- 'GOAL-CHECK PASSED — SC-01..SC-12 all met (run 13). SC-12''s reported gap rested
  on a false premise: ship pre-existed at 4d00dbc, abandon is the only new verb, covered
  at test-gh-sync.py:529'
resolved:
- MF-1..MF-6 all resolved; eng-lead re-verified by id at run 2026-07-31-04-eng
- MF-6 discharged outside the plan at f929d44 (gitignore __pycache__/*.pyc, tracked
  .pyc untracked)
- Q12 tree dirt cleared by the same commit
- Q7 budget answered by the user at 1ce886a — per_feature_usd 40 -> 120, task count
  held at 8
- fix cycle 2 CHANGE 1 + CHANGE 2 applied by pm (run 05), re-verified by eng-lead
  per-item (run 06)
- Q15 CLOSED at fix cycle 3 — ship's parent close now conditional on parent_origin,
  symmetric with abandon; 6 sites edited (run 07), re-verified per-item with must_fix
  [] (run 08)
- Q16 CLOSED at fix cycle 3 — PLAN:20-24 names 1ce886a the pinned review baseline,
  not "current HEAD"
- approval gate PASSED — BRIEF:233 and PLAN:653 both status approved, Mike Ruangutai,
  at 4d00dbc
- LEAD DISTILLATION CLOSED at runs 17-19 — all 13 lead ops applied by their own owners,
  0 dropped; check-expertise.sh over .harness/expertise/ is OK on all 11 files, exit
  0
runs[0].cost_usd: 19
runs[10].cost_usd: 12
runs[11].cost_usd: 30
runs[12].cost_usd: 23
runs[13].cost_usd: 9
runs[14].cost_usd: 26
runs[15].cost_usd: 14
runs[16].cost_usd: 5
runs[17].cost_usd: 6
runs[18].cost_usd: 6
runs[1].cost_usd: 16
runs[2].cost_usd: 21
runs[3].cost_usd: 6
runs[4].cost_usd: 24
runs[5].cost_usd: 7
runs[6].cost_usd: 16
runs[7].cost_usd: 5
runs[8].cost_usd: 11
runs[9].cost_usd: 54
skipped_segments:
- reason: surface is bin/*.py, feature.yaml fields and GitHub API calls — no end-user
    visual surface, no DESIGN.md
  segment: 1b-visual-designer-design-pass
- reason: no DESIGN.md contract exists to review (Expertise O-01)
  segment: 3-ui-reviewer-contract-check
- reason: harness.json github.sync false and github.repo null — open/close-task/ship
    all SKIP (DEC-138)
  segment: gh-sync-mirror-all-three-sync-points
```

## value normalization added during execution — a gap in T-04's instruction

- `github.milestone`: `'none'` (string) -> `null`
- `github.parent`: `'none'` (string) -> `null`

T-04's intent names only `pr` for the string-`none` normalization, and explicitly leaves
`branch` and `review_sha` alone because INV-6 reads them as placeholders. It says nothing about
`github.milestone` and `github.parent`, which the schema types as `integer|null`. Left as written,
T-04's own verify clause could not reach exit 0. Normalized on the same reasoning as `pr` — the
string `none` is a placeholder for absent — and recorded here rather than applied silently.
