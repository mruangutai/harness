# Handoff — FEAT-43 blocked at authorized SIMPLIFY

## Next

Return the SIMPLIFY blocker to the operator. Do not run the canonical state gate, commit, re-pin,
Review sync, or validator panel under the current authorization.

If and only if the operator authorizes another source-fix cycle, route R-01 through engineering:
make `code_grade.py:_commit_oid` the single commit resolver, call it from `code-grade.py`, and adapt
its `ValueError` to `validate-digest.py`'s existing `None`/reporting contract. Preserve commit-only
resolution, `--end-of-options`, option-like revision rejection, and both callers' observable error
behavior. After that source edit, configured QA and four-angle SIMPLIFY must run again before the
canonical state gate, explicit source/test commit, immutable review re-pin, Review sync, and full
validator panel.

The full panel must be told that grade-2-only grading uses `code_grade: grade_2` with a non-empty
`grade_2_reasons` list, while `code_grade: fail` remains grade-1/blocking. Product goal-check,
documentation, UAT, ship, merge, and deploy remain outside this validation mission.

## Trust

- Configured integrated QA passed unit 29/29 and integration 28/28 with seven changed surfaces bound — `runs/validate-fix-c13-qa-validator/digest.md` — verified-at uncommitted integrated working tree on 2026-08-28.
- Digest grade-state coverage includes PASS-compatible `grade_2` with non-empty reasons and blocking `fail` — `notes/qa-validate-fix-c13-qa-validator.md` — verified-at uncommitted integrated working tree on 2026-08-28.
- Reuse and simplification independently found three commit-resolver implementations that warrant consolidation — `runs/validate-fix-c13-simplify-eng/digest.md` — verified-at uncommitted integrated working tree on 2026-08-28.
- The duplicated implementations exist at the three cited symbols — `.claude/skills/harness/bin/code_grade.py`, `code-grade.py`, and `validate-digest.py` — verified-at uncommitted integrated working tree on 2026-08-28.
- SIMPLIFY touched only receipts and run artifacts, not source/tests — `runs/validate-fix-c13-simplify-eng/digest.md` plus post-run `git status --short` — verified-at uncommitted integrated working tree on 2026-08-28.
- Current immutable review pin predates the preserved B-01 through B-08 work — `feature.json.review_sha` — verified-at `45328d7a280d251a94b09672a7b6724d55a79f83`.

## Dead ends

- Do not apply R-01 under the current no-additional-source-fix authorization.
- Do not treat green configured QA as permission to skip mandatory SIMPLIFY.
- Do not run the canonical state gate or commit after a blocking SIMPLIFY result.
- Do not review the inherited pin; it does not contain the preserved remediation.
- Do not discard or redo the seven preserved source/test files.
- Do not represent grade-2-only as `code_grade: pass`.
- Do not continue to product, documentation, UAT, ship, merge, or deploy.

## Working set

- `.harness/harness/features/FEAT-43-code-risk-grading/feature.json`
- `.harness/harness/features/FEAT-43-code-risk-grading/STATE.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/runs/validate-fix-c13-qa-validator/digest.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/runs/validate-fix-c13-simplify-eng/digest.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/answers/Q3-cycle-13-overrun.md`
