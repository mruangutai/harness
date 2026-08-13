# STATE

## Current

- feature: FEAT-18-board-truth
- run: .harness/features/FEAT-18-board-truth/runs/2026-08-13-03-eng/state.yaml
- squad: eng
- status: building

**T-01 and T-05 are DONE and committed at `1fd6f9a`** on `feat/FEAT-18-board-truth` (branched from
`e61e081`, created with a plain `git checkout -b` — D-08 struck, no `gh issue develop`). Both tasks
are marked `status: done` in `plan.yaml` and their sub-issues #327 and #331 are closed on the mirror.
Milestone #10, parent #326, subs #327–#332. Each task's signed `verify:` string was re-run by me
independently of the squad's claim and both exit 0.

**One rework cycle spent, 1 of 10.** T-05 first returned BLOCKED: `change_type: logic` requires a
`unit` kind and the task's signed `files:` list named no test file, so the member had no honest PASS.
I settled it without granting the Iron Law exemption — `check-domain.sh --resolve` returns
`harness-backend-dev` for `test-branch-create-gate.py`, so the surface was already granted and no
human grant was needed. The deletion was reverted, `test-branch-create-gate.py` was written and seen
**red on the absence assertion alone** against the restored file, then the deletion was re-applied
and the file came back byte-identical. The gate now has the unit test it has never had in its life.

**BLOCKED ON THE MAIN SESSION: T-02, a DEC-174 carve-out by content.** No team work exists until it
lands — T-03 needs T-01+T-02, T-04 needs T-02+T-03, T-06 needs T-03. **T-02 must also register
`test-branch-create-gate.py` in `run-unit-tests.sh`'s `UNIT_SCRIPTS`, beside its own
`test-gh-board.py`.** Until that one array append lands, `run-unit-tests.sh` exits 2 with
`MISCONFIGURED` — declared, transient, and mine, not a defect anyone should "fix" elsewhere.

## Open Questions

- Q1 and Q3 were both answered at signature and are recorded in `BRIEF.md`'s `## Approval` block.
  D-05's three board keys stay in `harness.json` and their placement is knowingly temporary (`#206`
  moves `github`, `test_matrix` and `test_kinds` together). Do not reopen either.
- Q2 was overtaken by the 2026-08-13 revision and is not in force.
- New, non-blocking: extending T-05's surface with a test file was **my** execution-time call, not
  pm's re-plan and not the operator's exemption. `plan.yaml`'s T-05 `files:` list still names one
  file and is now one file short of the truth. Nothing gates on it — `check-plan-routes.py` validates
  the declared list, never the diff — so it is a record-accuracy question for the ship review, not a
  blocker.
