# Clause fix — D-17 and T-13 intent step 6 (FEAT-33)

Both falsified clauses are corrected. **Neither conclusion changed**: D-17 still leaves
`gh_board.derive_station` exactly as it is and adds the explicit status write beside it; step 6 still
says `derive_station` is NOT changed. Only the stated REASON changed.

Why they were false: `BRIEF.md:93-101` lists FOUR untouched enforcement files
(`check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-plan-routes.py`) — `check-state.sh`
is not among them (ruling 4, 2026-08-23). And `plan.yaml` D-24 has T-22 editing `check-state.sh` by
main-session-direct cutover under the DEC-174 carve-out. So "cannot be edited under DEC-174" and
"forbidden by SC-10" were both false.

## D-17 `because` (plan.yaml:114)

BEFORE:
> check-state.sh INV-26 grades the parent card against derive_station's return, and check-state.sh cannot be edited under DEC-174 and is forbidden by SC-10, so removing the review branch would silence INV-26's parent comparison instead of improving it. The derivation stops being the only path to Review; it does not stop being the expectation INV-26 reads.

AFTER:
> check-state.sh INV-26 grades the parent card against derive_station's return, so removing the review branch would silence INV-26's parent comparison instead of improving it. T-22 does edit check-state.sh, by main-session-direct cutover under the DEC-174 carve-out (D-24), but that edit is a bounded INV-26 widening for the done-task-with-open-sub-issue case and does not touch the parent comparison - so the file being editable here does not license this change. The derivation stops being the only path to Review; it does not stop being the expectation INV-26 reads.

## T-13 intent, step 6 (plan.yaml:1185-1192)

BEFORE:
> 6. gh_board.derive_station is NOT changed (D-17). It keeps returning the building station, the review station, or None, and _apply_parent_rule keeps calling it. check-state.sh INV-26 grades the parent card against that return and check-state.sh cannot be edited under DEC-174 or under SC-10, so removing the review branch would silence INV-26's parent comparison rather than improve it. The derivation stops being the ONLY path to Review; it does not stop being the expectation INV-26 reads.

AFTER:
> 6. gh_board.derive_station is NOT changed (D-17). It keeps returning the building station, the review station, or None, and _apply_parent_rule keeps calling it. check-state.sh INV-26 grades the parent card against that return, so removing the review branch would silence INV-26's parent comparison rather than improve it. T-22 does edit check-state.sh, but that edit is a bounded INV-26 widening for the done-task-with-open-sub-issue case and does not touch the parent comparison, so an editable file does not license this change. The derivation stops being the ONLY path to Review; it does not stop being the expectation INV-26 reads.

## Verification (worktree root, after the edit)

- `python3 .claude/skills/harness/bin/check-plan-routes.py` -> `0 violation(s) across 2 plan(s)`, exit 0.
- `.claude/skills/harness/bin/check-state.sh` -> exit 1, exactly ONE violation, the pre-existing and
  intended one: `FEAT-33-board-lifecycle-native/BRIEF.md is NOT approved`. Approval is the operator's.
- `yaml.safe_load` parses plan.yaml: 22 tasks, 24 decisions, `approval.status: pending` untouched.

## Untouched, deliberately

D-17's `choice`, steps 1-5 and 7-8 of the intent, T-22's substance and its ordering paragraph
(:1736-1740), `approval:`, BRIEF.md, and `notes/rulings-2026-08-23.md` (the record).

## Open questions

None.
