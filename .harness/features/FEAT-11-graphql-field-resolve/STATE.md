# STATE

## Current

- feature: FEAT-11-graphql-field-resolve
- run: .harness/features/FEAT-11-graphql-field-resolve/notes/ship-review-close.md
- squad: none
- status: awaiting-user

Mission SHIP is COMPLETE up to the operator's gate. Build, validate and close-out are all done and
the briefing is written. **Eleven of twelve success criteria are met; SC-01 is `uat` and stays that
way — it is the live cost measurement against a Projects v2 board and no agent in this flow may run
it.** The work is committed on the feature branch and nothing is pushed; no PR is open.

The headline outcome: a station move cost 104 GraphQL points and now costs 2, which is the
difference between a factory that exhausts its hourly budget mid-run and one that does not.

Both defects the gates caught were assertions that could not fail rather than bugs in the shipped
code, and both fixes were watched failing before they were believed. 11 of 12 cycles spent, 15 runs
against an informational budget of 20. Distillation is complete across 11 Expertise files with no
wipes. Ship-refresh was skipped and the reason recorded: this repo has no codebase map, so none can
be stale.

**Next action is the operator's, and it is three things:** run the SC-01 UAT (read its step 0 first
— `factory_decompose` takes its board from `fleet.yaml`, which says board 3, not the board 6 the
ruling protects); rule on SC-01's total clause; and strike whatever should not enter the backlog.

## Open Questions

- Q1 (blocking, operator only): **SC-01's total clause may be arithmetically unmeetable as written.**
  A four-task decompose also pays `gh project item-list` at 31 points per task, a call this feature
  never touched, so an all-`partial` run floors around 133 regardless. Measuring the total instead on
  an all-new run creates board items the restore cannot undo, spending the fixture. My
  recommendation: accept the per-move clause (2 vs 104) as the proof and record the total as
  mis-specified. Amending a criterion is the operator's alone.
- Q2 (non-blocking, recommend accept): a GraphQL partial-success envelope makes `project_field_set`
  complete its write on a call `gh` reported as failed. It is signed D-03 behaving exactly as
  written, so no engineering cycle can legitimately close it, and it does not violate SC-07. pm and
  I both recommend accepting it as a recorded residual rather than amending D-03.
- Q3 (harness defect, operator only): `bash-write-guard.sh` reads the redirect target of
  `cp … 2>/dev/null` as the `cp` destination and blocks a legitimate in-domain write. A fail-closed
  hook with a false positive, and a DEC-174 carve-out file no agent may fix.
- Q4 (backlog): the expertise format gate is red on `harness-documentor.md` (53 words against a
  50-word cap). Pre-existing — that file is untouched by this feature — and two leads independently
  declined to spawn documentor to trim it, on wipe-risk grounds. I endorsed both refusals.
- Q5..Q16: the remaining residuals are the briefing's backlog table B-1..B-16. Anything the operator
  does not strike becomes an issue on acceptance; anything not in that table dies silently.
