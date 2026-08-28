# FEAT-43 validation is blocked before commit and panel

## Decision

Stop under the current authorization. Configured Homebrew-Python QA passed, but mandatory
four-angle SIMPLIFY found a warranted source consolidation across three security-sensitive commit
resolvers. The operator authorized no additional source-fix cycle, so the change was not applied.
The canonical state gate, source/test commit, immutable re-pin, Review sync, and validator panel did
not run. The preserved source/test working tree remains uncommitted.

A future continuation requires explicit authorization for another source-fix cycle. Its bounded
change is R-01: make `code_grade.py:_commit_oid` authoritative, reuse it from `code-grade.py`, and
adapt its `ValueError` to `validate-digest.py`'s existing `None`/reporting contract without changing
commit-only resolution, option-like revision rejection, or caller-visible error behavior. That
continuation must repeat configured QA and SIMPLIFY before any commit or review pin.

## Gate evidence

- QA PASS: unit 29/29 and integration 28/28 under Homebrew Python, with named non-vacuous coverage
  across all seven changed source/test files. The digest-grade contract explicitly covers
  PASS-compatible `code_grade: grade_2` with non-empty `grade_2_reasons` and blocking
  `code_grade: fail` (`runs/validate-fix-c13-qa-validator/digest.md`).
- SIMPLIFY BLOCKED: reuse and simplification independently found the resolver duplication;
  efficiency found no runtime waste and altitude recommended the existing responsibility seams
  otherwise remain (`runs/validate-fix-c13-simplify-eng/digest.md`).
- Source premise checked: resolver implementations are present at
  `.claude/skills/harness/bin/code_grade.py:_commit_oid`,
  `.claude/skills/harness/bin/code-grade.py:_commit_oid`, and
  `.claude/skills/harness/bin/validate-digest.py:resolve_reviewed_commit`.
- No SIMPLIFY source/test edit was applied. The inherited `review_sha`
  `45328d7a280d251a94b09672a7b6724d55a79f83` predates the preserved remediation and must not be
  reviewed.

## Feature record

Planning and the original build passed. Earlier configured QA initially blocked before discovery,
then passed after Homebrew-Python selection. The first full panel found twelve defects; the first
remediation and its QA/SIMPLIFY passed. The second panel found B-01 through B-08. Engineering
preserved the authorized remediation, and the current integrated QA passed. The current SIMPLIFY
blocker is new validation evidence and cannot be fixed within `cycles_used: 13` /
`max_total_cycles: 13`.

The T-06/T-09 owner-resolution escalation was resolved by the operator and recorded at
`answers/Q1-t09-owner-resolver.md`. Product goal-check, documentation, UAT, ship, merge, and deploy
were intentionally not run in this mission.

## Open question

A nonblocking harness-contract question remains from the efficiency reader: what canonical suite
value should a read-only engineering assessment report when a receipt is required but validation is
expressly prohibited? This did not cause R-01 and does not change the terminal feature blocker.

## Proposed backlog

| ID | Nature | Residual finding |
|---|---|---|
| B-1 | chore | Define the canonical engineering digest suite value for assessment-only runs where validation is prohibited. |
| B-2 | chore | Audit stale `.agents/` guidance paths identified during planning; keep only paths that intentionally resolve through the compatibility seam. |
| B-3 | bug | Reconcile the domain-manifest grant for `.harness/harness.json` with the signed route record that classified it as main-session-direct. |
| B-4 | bug | Decide and test whether `check-plan-routes.py` must reject tasks whose files are writable only by the union of disjoint agents. |
| B-5 | chore | Resolve or signed-exclude the `component`, `ui`, `eval`, and `typecheck` test-kind statuses noted during planning. |

## Sources

No report round was spawned. This briefing was assembled from every run digest recorded in
`feature.json`:

- `runs/plan-product/digest.md`
- `runs/t01-t07-eng/digest.md`
- `runs/t02-eng/digest.md`
- `runs/t03-eng/digest.md`
- `runs/t10-product/digest.md`
- `runs/t06-eng/digest.md`
- `runs/build-qa-validator/digest.md`
- `runs/build-qa-validator-rerun/digest.md`
- `runs/build-simplify-eng/digest.md`
- `runs/validate-review-validator/digest.md`
- `runs/validate-fix-eng/digest.md`
- `runs/validate-fix-qa-validator/digest.md`
- `runs/validate-fix-simplify-eng/digest.md`
- `runs/validate-review-final-validator/digest.md`
- `runs/validate-fix-c11-eng/digest.md`
- `runs/validate-fix-c13-qa-validator/digest.md`
- `runs/validate-fix-c13-simplify-eng/digest.md`
