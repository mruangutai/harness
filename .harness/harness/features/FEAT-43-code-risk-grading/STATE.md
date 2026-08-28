# STATE

## Current

- feature: FEAT-43-code-risk-grading
- run: .harness/harness/features/FEAT-43-code-risk-grading/runs/validate-final-panel-validator/state.yaml
- squad: validator
- status: Review — BLOCKED at the final validator panel. Cycle budget exhausted (13/13).

The operator authorized SIMPLIFY's single warranted apply (`answers/Q5-simplify-apply-authorization.md`),
which superseded the previous handoff's "do not apply R-01". R-01 was applied: `code_grade.commit_oid`
is now the repository's single commit-resolution seam, with `code-grade.py` and
`validate-digest.py:resolve_reviewed_commit` as thin adapters. Observable behaviour is unchanged and
the leading-dash guard was proven live by mutation with a byte-identical restore
(`runs/validate-fix-c13-r01-eng/digest.md`).

Every gate then ran. QA re-gate green at baseline: unit 29/29, integration 28/28, non-vacuous binding
across all seven changed files (`runs/validate-regate-c13-r01-validator/digest.md`). Four-angle
SIMPLIFY re-run returned `must_fix: []` with six non-gating backlog rows
(`runs/validate-final-simplify-eng/digest.md`). The canonical suite recorded 955 passing suites and
exit 1 from exactly one failure, `test-hooks-install.py` case `(e-green) SC-14`, which is PRE-EXISTING
and independent of this feature: it reproduces identically on the main checkout at `3952814`, which
does not contain `code_grade.py` at all. `check-state.sh` exits 0. The seven source/test files were
committed as `94383e671e51f95d142f3220f97c8e453721d516`, `review_sha` was re-pinned to that commit,
and `gh-sync.py status Review` moved the parent #924 and all ten sub-issues to Review.

**The full panel then returned FAIL, and it is terminal.** Three reviewers failed independently on
four blocking findings. The central one is verified by direct measurement, not accepted on report:
`code-grade.py` exits 1 over this feature's own pinned range, with 21 of 119 gated functions below
their bar — six grade-3 PRODUCTION functions against a bar of 4, two of them inside `code_grade.py`
itself. T-01's unconditional acceptance line, "the tool must pass its own bar", is unmet, and the
code reviewer searched the BRIEF's out-of-scope section, D-01 through D-12 and the plan constraints
for an exemption and found none. The security reviewer separately found that a reviewer's
`code_grade` claim is self-attested and never bound to `review_sha`, so a digest naming a no-op range
has `n_a` accepted and bypasses the gate this feature exists to add.

No source fix is authorized after this panel and `cycles_used` is 13 of 13, so remediation is the
operator's decision. Everything is preserved: the branch, the commit, the pin, and every artifact.
Goal-check, documentation, UAT, ship, merge and deploy did not run and remain prohibited. The
briefing addressed to the operator is `notes/ship-review-validate-final-panel-validator.md`.

`runs` now stands at 21 against an INFORMATIONAL 20-run budget (INV-22). Cycles count rework only, so
the count is not itself a defect; it is surfaced rather than hidden.

## Open Questions

- Q1 (settled, recorded for the successor): a read-only engineering assessment had no legal way to
  report its suite — `validate-digest.py` rejects `dev` + `suite: n/a` + PASS by design, while
  `dev-ops` is allowed. Resolution: an assessment-only member RUNS the suite and reports the real
  value, since executing tests is not a source edit. The asymmetry itself is a harness-contract
  wart, carried as backlog row B7.
- Q2 (blocking, for the operator): the feature's own change does not pass the gate it ships. Accept
  the six grade-3 production functions by a recorded decision, or authorize a remediation cycle
  beyond the exhausted 13. This cannot be resolved inside the harness.
