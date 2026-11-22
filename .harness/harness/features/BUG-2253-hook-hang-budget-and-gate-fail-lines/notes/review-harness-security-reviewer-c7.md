# BUG-2253 security c7 — PASS

No new exploitable gate bypass, privilege change or unsafe unit-loading boundary. Two operator-disposed advisories remain; no must-fix or open questions.

Reviewed exactly `3dd8bb677bb2936361e3952030fc24f15bf9afc6..3ba8dd4bf65392a1dd4fe99dddfebb14fe68d01d` for run `2026-11-22-06-validate-validator`. Read BRIEF, plan, feature.json and cycle-3 digest. PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md remain absent; no substitute requirements assumed.

## Scope and security conclusions

Measured 92 changed paths: **IN** the validator, integration test and new unit test; **OUT** the other 89 specifications, metadata, approvals, run records and evidence paths, which add no executable security policy. Full-diff credential-pattern sweep found explanatory prose only, not introduced credentials. No new dependency, network, authentication or cross-user data surface.

- **SC-01:** runner output crosses into human diagnostics, not acceptance authority. Header membership only grows; echoed PASS/header/close lines cannot erase genuine failures. Mutation-note adjacency, ordering, duplicates and last-20-line tail remain intact. Completed nonzero independent runs still return 2 (`.claude/skills/harness/bin/validate-digest.py:2453–2550`).
- **New unit execution:** `tests/unit/test-validate-digest-run-pool-lines.py:14–20` derives a repository-local absolute module path from its own resolved location and uses the existing `harness_boundary.load_repo_module` (`harness_boundary.py:532–578`). Neither payload text nor runner output chooses code. The non-main module name leaves CLI/hook entrypoints dormant (`validate-digest.py:2847`); seven tests call real parser/report functions with literal expected outputs. stderr redirection is context-managed. `run_pool.py:60–71` runs each test file in a separate subprocess, containing import/path/global state to that file. A repository writer already has test execution capability; this grants no additional privilege.
- **SC-02:** six call sites read the shared test-only 30s budget. Private temporary executable fixtures use repository-authored source and repr-encoded data, not shell interpolation. Both real helpers use list-form argv and subprocess timeout handling (`test-validate-digest.py:1062–1074,3411–3416`). The watchdog targets this process's direct children, excludes its own ps process, and stops/joins in finally; authored blockers launch no descendants (`:6578–6679`). This is direct-child fixture containment, not a sandbox guarantee for arbitrary process trees.

## Nonblocking findings

1. **substance / low / accepted:** a test author can echo a matching header and `FAIL victim.py` (or a mutation-note-shaped block), causing misleading filename attribution in a refused run. They already execute test code; gain is diagnostic spoofing, not acceptance or privilege. Monotone over-listing is explicitly operator-accepted (STRIDE T/R; unmitigated).
2. **substance / info / outside patch:** unchanged `_reverify_suite` returns None on missing runner, spawn failure or timeout, and `check_qa_matrix_claim` warns then returns 0 (`validate-digest.py:2431–2480`). Runner unavailability leaves an unconditional QA PASS unverified. BRIEF and operator exclude policy changes (STRIDE T; unmitigated).

## Evidence and limits

Independent git comparisons produced no differences: production validator from `3c6fb908` to the review pin; validator plus integration test from that fix to pin; all three changed Python subjects from `d9026b74` to pin; and those subjects plus loader/run_pool from pin to later HEAD. Equivalence is derived, not assumed; later records are not reviewed code.

Inspected supplied `unit-red.txt` and both stderr streams: exact base has seven missing-parser/report AttributeErrors (not seven behavioral assertion failures); cycle-2 `b228c3a2` has exactly the echoed-header behavioral failure. `green-c5.txt/stdout` reports 17 integration cases passing and unit stderr reports seven tests OK on code-equivalent `d9026b74`. These are supplied receipts, not reviewer executions. Main supplies grading exit 0, PASSING 38, no FAIL. No tests, probes, grader, build, lint or formatter were executed here. QA alone owns final literal verification: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases && python3 tests/unit/test-validate-digest-run-pool-lines.py`.
