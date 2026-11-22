# Patch intake acceptance

Accept only BRIEF.md (at most 120 lines) and plan.yaml left pending, one T-01 main-session-direct task citing DEC-174, resolved lanes and complete files list. No readers or goal-check. Preserve all settled grilling intent and exclusions.

Every SC requires a genuine base-failing behavioral regression, not source-text or wording assertions. Gate coverage uses RUN_UNIT_TESTS_BIN with every FAIL/MUTATED line above 20 passing tail lines and retains tail-only fallback. Budget coverage exercises all six calls using one HOOK_HANG_BUDGET_S = 30 and proves actual blocked hook execution is terminated within budget; removal of timeouts must fail the test. Testing strategy must be practical and bounded without weakening the real-hang assertion.

Task machine fields remain within DEC-182's 50-line cap. Required intake receipts: plan-merge.py check --file <plan> --root <worktree>, check-plan-routes.py, and check-plan-routes.py --canonical-reader-audit, each exit 0. Planning only: no implementation or regression execution. PM records exact checks and outcomes in notes/research-patch-intake.md.
