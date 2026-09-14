# STATE

## Current

- feature: BUG-285-yaml-loader-pin
- run: .harness/harness/features/BUG-285-yaml-loader-pin/runs/2026-09-11-planpanelc4-validator/state.yaml
- squad: none
- status: stopped

**PLANNING STOPPED BY THE OPERATOR, mid-flight, 2026-09-11.** A scope and cost decision, not a
quality judgement on the run. Nothing further was dispatched after the stop landed, no finding was
closed, and nothing inconsistent was reconciled — the tree is committed exactly as it stood.

**Last completed step:** plan panel cycle 4 (`runs/2026-09-11-planpanelc4-validator/`). Both readers
ran. Verdict FAIL, `severity_max: med`, three must_fix items — all of them plan-TEXT defects, none
touching a task's file set, a decision's direction or either operator ruling. Both readers
independently cleared the behaviour the five tasks would build.

**In progress when the stop landed:** the fix cycle for those three must_fix items had NOT been
dispatched. They stand open and unaddressed:
1. SC-15 part two lists duplicate-key and YAML-only as classes the readers "deliberately do NOT
   treat identically" while part one lists the same two as treated identically — a self-contradiction
   in the criterion that mandates the docstring.
2. T-04 item 3 orders the docstring to cite gh-sync.py lines 578, 588-594 and 613, all displaced by
   its own ~30-line insertion at :528; SC-13's numeric anchors are displaced by the same edit.
3. D-16 licenses the deliberate second copy of `_opt_int` on a drift claim T-05's value rows cannot
   support: its only rows are `"7"` and `true`, so dropping `str(v).strip()` diverges on `" 7 "`
   with the suite green.

**The plan as it stands:** five tasks (T-01..T-05), sixteen decisions (D-01..D-16), REQ-01..REQ-12,
SC-01..SC-16. Panel record in plan.yaml is CYCLE 2 — cycles 3 and 4 ran but were never transcribed,
so `panel:` understates what was read. Nine rework cycles of ten used.
- record that stands: notes/research-BUG-285-parity-survey.md (13 input classes, 4 SAME / 9 DIFFERENT / 6 malformed-read-as-empty), named by the operator

## Open Questions

- Both artifacts are UNSIGNED and stay that way. plan.yaml's `approval.status: approved`
  (mruangutai, 2026-09-09) is a stale record covering a one-task plan that no longer exists. It is
  issue #1675 and it is NOT to be fixed here. BRIEF.md reads `pending`.
- Three panel must_fix items open, listed above. Unaddressed by operator instruction.
- Known-open divergence, verified at source, left open under the budget ceiling: `issues` key
  admission. `gh-sync.py:613` admits only `T-\d+` keys and strips them; `factory_decompose.py:139-141`
  admits any key with an int value. So `{"issues": {"X-1": 5}}` reads as `{}` on one side and
  `{"X-1": 5}` on the other. Both readers judged leaving it open defensible; the advisor noted the
  two readers consume disjoint document blocks, so "divergence" may overstate it.
- Panel findings from cycles 3 and 4 exist only in their run digests, never transcribed into
  plan.yaml's `panel:` key.
- `notes/handoff-plan.md` fails the shape gate at 63 lines against a cap of 60, and is stale — it
  describes the three-task plan. Left as-is under the stop instruction.
- Harness defect, raised twice by the validator lead: a reviewer dispatched against an
  approved-but-unbuilt plan can never return a validated digest. `validate-digest.py` accepts
  plan-review mode only when `approval.status == pending`, and non-plan mode needs a `review_sha`
  that resolves; this plan carries the stale `approved` and `review_sha` is the literal `none`, so no
  `(code_grade, reviewed)` pair is satisfiable and the reviewer's job exits 1 with its artifact
  complete on disk.
