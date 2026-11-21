# Pre-signature simplify pass — BUG-2239 plan — 2026-11-21

Four read-only reviewer angles over BRIEF.md and plan.yaml at `0ab7706c` (reuse, simplification, efficiency, altitude). Full payloads: agent://PlanReuse, agent://PlanSimplification, agent://PlanEfficiency, agent://PlanAltitude.

## Must-fix (apply)
1. **Roots.** Intent says "appropriate checkout and manifest roots". Call `routes.cpr.process_plan_yaml(resolved_plan, findings, root, routes.manifest_root)`, where `root` is `--root` (never `--code-root` or `anchor_root`). Reuse the loaded `routes.cpr` and `routes.manifest_root`; don't reload. Add one served-repo-plan regression.
2. **Duplicate NOBODY.** `_route_faults` already FAILs a NOBODY team path; `process_plan_yaml._routing_rule` adds `VIOLATION <tid>: <path> ungranted (NOBODY)`. Both are expected (different rules): render each VIOLATION as `FAIL <violation text>`, count it in the summary, never dedupe or filter cpr findings, and update `case_f59_check_lists_each_failure_on_its_own_line`'s count from 7 to 8 with an assertion naming the VIOLATION line.
3. **Routing red.** Routing already exits 1 before the fix, so its red is the absence of the shared VIOLATION line, not the exit code. Budget and status cases carry the exit-code red. Align SC-01 to "previously missed violations", as SC-04 does.
4. **Processor returns None.** `process_plan_yaml` returns None (stderr only) when `validate_plan_doc` refuses a YAML-valid plan (e.g. a duplicate task id). `check` must exit non-zero, using exit 5 like `_check_inputs`' "does not load", with a refusal naming the load failure. Add a regression.
5. **SC-06 intake sentence.** Delete "No regression runs during intake." from SC-06 and the matching intent sentences (lines 68–69). Keep the single statement in Verification gaps.

## Optional (adopt)
- Extend the existing FEAT-1928 injection tests (flat ~1650, batch ~1626) with the exact `additionalContext`, rather than writing parallel ones; the no-note case reuses the scout/no-injection fixture.
- Name the existing helpers: `_check_root`/`_check_task`/`run_verb`, and `_load_owner("check")` for the delegation proof; size the budget fixture from `cpr.MACHINE_LINES_PER_TASK`; pick the illegal status outside `cpr.legal_task_statuses()`.
- Drop `tests/integration/test-check-plan-routes.py` and `tests/unit/test-omp-hooks.py` from `files:`/lanes (no change assigned); keep them in verify.
- BRIEF operator perspective: the note arrives with the task call's result, not "at dispatch time" (OMP delivers `additionalContext` after tool results).
- Drop the #2241 fresh-id constraint (no durable state here).
- Point the intent at SC-02/SC-06 instead of restating their exact sentence and SHA.

## Declined
- Folding SC-04 into SC-01 and SC-05 into SC-02: SC-01 is the operator perspective and SC-04 the maintainer's test evidence; separate seats, kept.
