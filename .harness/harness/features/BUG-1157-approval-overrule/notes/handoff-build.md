## Next

Push `fix/1157-approval-overrule` and open a pull request for issue #1157 from commit `5d3c0c33`. No formal code review was requested. The implementation and focused verification are complete.

## Trust

- `python3 tests/integration/test-plan-merge.py` passes, including repeatable `--overrule`, current-finding validation, required attribution/date/reason, and byte-identical refusals.
- `python3 tests/integration/test-check-state.py` passes, including risk acceptance for high, critical, unrated, and absent-severity findings without a `ruling: overrule` discriminator.
- Changed production Python functions grade 4 or 5 with `code-grade.py --base origin/main --head HEAD`.
- The canonical `check-state.sh` was run before commit. It remains red only on two unrelated existing FEAT-51 conditions: missing `notes/handoff-validate.md` and a standing terminal worktree.

## Dead ends

- `approval.rulings` could not previously be written by any sanctioned route; direct editing and `amend` are intentionally unavailable.
- Keeping `ruling: overrule` as a discriminator was rejected. A complete ruling entry is itself the operator's accepted-risk record.
- `disposition: overruled` was removed from the template contract because it did not satisfy INV-32 and duplicated the approval record.

## Working set

- `.claude/skills/harness/bin/plan-merge.py` — repeatable `sign-approval --overrule PF-ID:<reason>` writer and validation.
- `.claude/skills/harness/bin/check-state.sh` — INV-32 complete-entry validation and accepted-risk behavior.
- `tests/integration/test-plan-merge.py` — writer regression coverage.
- `tests/integration/test-check-state.py` — INV-32 regression coverage.
- `.claude/skills/harness/templates/plan.yaml` — ruling and disposition contract.
- `.claude/skills/harness/SKILL.md` — operator acceptance route.
- `.claude/skills/harness/bin/panel_findings.py` — accepted-risk terminology.
- `issue://1157` — defect report and intended writer shape.
