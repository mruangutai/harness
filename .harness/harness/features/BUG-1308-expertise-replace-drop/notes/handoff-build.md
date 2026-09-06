# Handoff — BUG-1308, build → validate — administrative recovery

## Next

Validate the `ops` subcommand at the pinned `review_sha` in `feature.json`. Grade every approved
success criterion, with particular attention to SC-13 cap preservation across the line-boundary
alphabet derived from `str.splitlines()` and SC-14 target identity by round-trip through `ENTRY_RE`.
The final panel and goal-check have already passed; this note restores the disk-only seam record that
the worktree-relative handoff writer could not create.

## Trust

- Unit suite: exit 0, zero `FAIL`, 29 files on the merged tree — verified-at 433df520
- Integration suite: exit 0, zero `FAIL`, 46 files on the merged tree — verified-at 433df520
- Final review panel cycle 4: PASS, no `must_fix`; VL-01 through VL-06 closed — verified-at b70d57b4
- Final goal-check: SC-01 through SC-12 MET; the operator-adopted SC-13 and SC-14 are MET by the same existing case21/case22/u17/u18 and case23/case25/case26/u19-u22 evidence — verified-at b70d57b4
- The merged branch contains origin/main 0f885a0a with no conflict, and `apply` remains untouched under REQ-07 — verified-at 433df520

## Dead ends

- Do not re-type `ENTRY_RE` or the `str.splitlines()` boundary alphabet; both validations are derived from their parser source to prevent drift.
- Do not edit the pre-existing `apply` path; REQ-07 requires add-only compatibility.
- Do not reopen closed VL-01 through VL-06 without a new failing reproduction.

## Working set

- .harness/harness/features/BUG-1308-expertise-replace-drop/BRIEF.md
- .harness/harness/features/BUG-1308-expertise-replace-drop/feature.json
- .harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-c4-validator/digest.md
- .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c4.md
- .claude/skills/harness/bin/expertise-merge.py
- tests/unit/test-expertise-ops.py
- tests/integration/test-expertise-merge.py

## Done when

Scope: the review panel has graded the approved criteria at the pinned review_sha and no must-fix remains
Authority: brief-sc:SC-13
Authority: brief-sc:SC-14
Authority: approval:.harness/harness/features/BUG-1308-expertise-replace-drop/BRIEF.md#Approval
