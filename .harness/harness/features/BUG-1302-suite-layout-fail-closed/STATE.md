# STATE

## Current

- feature: BUG-1302-suite-layout-fail-closed
- squad: none
- status: review

Validation is COMPLETE and PASSES at the pinned `review_sha`. The four-seat panel
(qa, code-reviewer, security-reviewer, ui-reviewer) returned PASS with `must_fix: []` and
`severity_max: low`; the qa test-matrix hard gate passes; the goal-check grades all ten success
criteria met. Every one of the five B-rows was mutation-proven to discriminate the defect it names,
in a disposable probe worktree, so the two DEC-174 files stayed byte-identical to the pin throughout
validation. The feature is ready for the operator's ship decision; the briefing is in
`notes/ship-review-2026-09-05-validate.md`. Nothing here is merged, shipped or PR'd.

## Open Questions

- The `run-unit-tests.sh` carve-out question is unchanged: DEC-174 does not enumerate it by name and
  the Advisor ruled its carve-out binds both gate test files by category. Amending DEC-174's
  enumeration is an explicit non-goal of this feature and remains an operator question.
- The B-6 hard-failure remedy and its fixture-maintenance red stand as the Advisor's recommended
  tradeoff; the failure message names both repairs. The residual blind spot — a well-formed
  `test_kinds` change that blinds the gate to a real offending path — is caught by neither the
  positive control nor the hygiene certification, and is recorded in BRIEF.md as the accepted price.
- Structural AST pins may need main-session fixture maintenance after a legitimate refactor, under a
  FAIL name that misdescribes the cause. Recorded in BRIEF.md; the ui reviewer re-raised it as two
  low advisories and it is a briefing row, not a gate.
- `runs/2026-09-05-1-eng/digest.md` fails the DEC-156 lead-digest contract and CANNOT be repaired:
  `check-domain.sh` refuses any Write to a run digest that already holds one. A malformed digest is
  therefore permanent. This is a harness defect, carried to the operator as a briefing row.
- Harness tooling defects observed during planning and validation remain outside this issue's scope
  and are carried as briefing rows, not fixed here.
