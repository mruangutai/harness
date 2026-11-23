# Observations — harness-orchestrator — FEAT-2397-omp-native-cleanup

- 2026-11-23: task-tool dispatch to a harness lead is refused when tasks[].outputSchema or schemaMode is supplied; the hook injects the persona schema itself. Omit both.
- 2026-11-23: plan team returned with pm leaving BRIEF '## Approval' block empty (no status: pending fields); INV-1 grades it identically to pending, main session writes the block at signature.
- 2026-11-23: pre-signature simplify pass = two runs after the plan run (simplify-eng flag-only via eng-lead, four readers; simplify-apply-product via product lead, pm folds), both closed --code-grade n_a, 0 cycles; mirrors FEAT-2337.
