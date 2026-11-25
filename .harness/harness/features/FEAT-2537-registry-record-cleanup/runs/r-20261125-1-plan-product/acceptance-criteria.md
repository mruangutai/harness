# Send-back criteria for pm intake (written before dispatch)

Send back (once) if any fails:
1. BRIEF.md <= 120 lines; sections Problem, perspectives, SCs, Verification gaps, Constraints, Out of scope, Approval (pending) all present.
2. plan.yaml: exactly one task T-01; approval.status pending; top-level status: plan; plan-merge.py check exit 0 reported with output.
3. T-01 execution_mode: main-session-direct (not team); traces every SC; change_type exists in configured test matrix and is not bugfix.
4. T-01 files: excludes tests/integration/fixtures/prior-validate-digest.py.fixture and tests/integration/test-validate-digest.py.
5. decisions_affected: five-field block naming DEC-199, DEC-204, DEC-218; amendments-before-code ordering stated inside T-01.
6. SCs 1-4 class-shaped; case 18 both directions asserted; hooks diff comment-only; restated behavior class replaces "zero behavior change".
7. Non-goals: no LEGACY_FEATURE removal, no _parse/_read_strict renames, no inventory change, no fixture edits.
8. Rework 1 round / 45 min recorded under constraints, unsigned.
