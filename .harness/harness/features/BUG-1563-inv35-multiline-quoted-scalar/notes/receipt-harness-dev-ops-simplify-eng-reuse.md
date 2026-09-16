# Reuse receipt — BUG-1563

**Conclusion: no duplicate constant, helper, fixture, or procedure found.**

Reviewed commit `c1e85b64d9871e07bdf3b6994ab8e4ee7a36ba11` against its parent, limited exactly to:

- `.claude/skills/harness/bin/check-state.sh`
- `tests/integration/test-check-state-plans.py`

## Findings

None. The new `_quoted_scalar_closed` helper is local to the INV-35 scanner and no existing importable equivalent exists in the scoped surrounding search. The added cases reuse the pre-existing INV-35 fixture and output-filter helpers at `tests/integration/test-check-state-plans.py:729` and `tests/integration/test-check-state-plans.py:741`; they add distinct double-quoted, single-quoted, and unquoted-positive-control procedures rather than duplicate fixtures or procedures.

No validation commands were run.
