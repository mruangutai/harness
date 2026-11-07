# BUG-2180 — T-01 pinned code review

**FAIL: implementation matches the bounded acceptance, but the new `case_x` fails the mandatory Python complexity gate (high).**

Reviewed `4a05030d401593003209f525fd06e00802eccd36..556a23ffea8dafcf5110e80fe25a42ee2542ff2b`, never HEAD. Pin agrees with feature.json; no tracked dirty files or `[harness:human]` commits. The only untracked entry was the intake grilling note. Read BRIEF, plan decisions (empty), build-evidence and patch-intake notes before judging compliance. No build amendment list was supplied.

## Stage 1 — spec compliance

No scope creep, omission or mismatch found by inspection; stage 1 passes. Automated acceptance results remain QA's responsibility.

- SC-01: `check_state/board.py:632-671` reuses `feature_schema.has_repository_binding/resolve_binding`, isolates candidates by repository and board, and never falls back after bound resolution failure. `:709-747` allows bound checking with owner mirroring disabled. Regression `tests/integration/test-check-state-inv26.py:735-793` covers parent/task/source requests, corrected/misplaced twins, owner-off and overlapping issue 41 with distinct repository station values.
- SC-02: `board.py:432-440,591-629` retain eligibility/projection/comparison logic; `:408-417,719-722,743-747` preserve owner declaration diagnostics and offline/authentication skips. Existing cases v/w are unchanged; x.4 adds mixed owner/bound controls.
- SC-03: `board.py:695-706` catches actual `gh_board.BoardError` and `gh_board.factory_gh.GhError`, reports affected features plus underlying error, and lets subsequent groups run. Regression x.5 at test `:797-812` checks CANNOT VERIFY and the healthy owner's misplaced card.
- SC-04: `board.py:644-647,659-662` catches `artifact_accessors.FleetError` without owner fallback; x.6 at test `:816-833` requires the error and a healthy comparison, and excludes bound numbers from owner reads.

The assigned product docs/spec.md, docs/decisions.md and docs/architecture.md are absent as disclosed in intake; BRIEF supplies settled acceptance, with no specific unresolved guidance question. No other product guidance was substituted.

## Stage 2 — code quality

**R1 — substance / high / T-01:** `tests/integration/test-check-state-inv26.py:712`, `case_x`, is a newly introduced grade-1 test function, below the test bar of 3. The pinned grader measured cyclomatic **48**, cognitive **38**, ABC **124.9**; driver **cyclomatic+cognitive+abc**; `RESULT: FAIL`, `SEVERITY: high`. This is the mandatory complexity-gate failure, not an inferred runtime bug. Split the six independent scenario bodies into coherent case functions while retaining every assertion and shared fixture; do not weaken the scenarios to reduce the score.

Executed only the required grading command: `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base 4a05030d401593003209f525fd06e00802eccd36 --head 556a23ffea8dafcf5110e80fe25a42ee2542ff2b`. Exit **1**; 11 passing records and the single high record above. No grade-2 reasons required. No additional correctness finding from fail-open/error-path inspection. No tests, builds, lint, formatting or mutants executed; baseline/final test claims in build evidence were read, not independently exercised.

## Principles applied

- Model the Domain — assessed the repository/board group key against overlapping issue numbers rather than treating issue numbers as global identity.
- Delete First — confirmed the obsolete owner-union/read/compare helpers were removed, with no surviving callers found.

## Open questions

None. No source or tests changed. QA owns the final signed integration command and configured unit floor.
