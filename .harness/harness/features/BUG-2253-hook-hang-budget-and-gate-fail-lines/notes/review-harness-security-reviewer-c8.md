# BUG-2253 security c8 — PASS

Retained gate diagnostics do not weaken refusal; removing SC-02 probe machinery changes no real safety calls. No must-fix; accepted Low and excluded Info advisories remain.

Reviewed immutable `3dd8bb677bb2936361e3952030fc24f15bf9afc6..7e590f735af90220baec7013c7ce8eafc2163bce`, run `2026-11-22-07-validate-validator`. Current BRIEF, plan, feature.json, operator reduction and prior assessment were consulted. PRODUCT `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` were confirmed absent; no substitute guidance assumed.

## Scope and evidence

- **IN:** validator diagnostics, integration fixtures/budget and unit loader/assertions (three Python paths). **OUT:** other 98 changed paths: feature requirements, metadata, approvals, evidence and review/run records, not executable controls. Full pinned diff credential-pattern inspection found no introduced credential matches. No new dependency, request, authentication or cross-user data surface.
- Independently compared previous PASS `3ba8dd4b..7e590f73`: production validator and unit file have **zero diff**; integration changes are the scoped helper/probe deletion and three-case selection. Inspected source also has zero working-tree diff against the pin. Production equivalence is established, not assumed.
- **SC-01 / T-01:** `.claude/skills/harness/bin/validate-digest.py:2431–2550` preserves runner selection, 1800s timeout and policy: completed nonzero runs return 2, independently of extracted text. Parser header membership only grows, so echoed headers/PASS/close lines cannot erase real failures; mutation adjacency, ordered duplicates and original tail remain. Output is printed, not executed or used as an authorization decision. Three retained integration cases exercise real refusal via RUN_UNIT_TESTS_BIN; seven unit assertions call actual parsers/reporting. Unit loading derives its fixed repository-local path from `__file__`, not payload/output (`tests/unit/test-validate-digest-run-pool-lines.py:14–20`).
- **SC-02 inspection / T-01:** rationale and `HOOK_HANG_BUDGET_S = 30` at `tests/integration/test-validate-digest.py:1025–1030`; all six actual calls use it at `3033,3066,3286,3288,3316,3318`. Base-to-pin diff changes no unrelated timeout or real FIFO/symlink/deep-JSON refusal behavior. Removed site-observation/blocker/watchdog/containment helpers have no remaining references; retained fixture helpers are used. No removed behavioral regression is re-demanded.

## Nonblocking findings

1. **substance / low / scope none / T-01 SC-01 / operator-accepted:** a test author already able to execute code can echo a matching header plus `FAIL victim.py`, or a mutation-note-shaped block, and over-list a filename (`validate-digest.py:2494–2536`). Gain is misleading refusal attribution, not acceptance or privilege. STRIDE T/R remains unmitigated; monotone listing preserves genuine failures.
2. **substance / info / scope none / outside T-01:** missing runner, launch failure or timeout still produces None and warning-plus-return-0 (`validate-digest.py:2431–2480`), leaving an unconditional QA PASS unverified. This base-existing policy is explicitly excluded, not a BUG-2253 blocker. STRIDE T remains unmitigated.

## Verification capabilities and limits

Used read-only source inspection, immutable git comparisons, targeted reference search, full-diff credential-pattern inspection and supplied receipt/assessment review. `red-c4.txt` records exact-base exit 1; `discriminate-c4.txt` records cycle-2 exit 1; prior QA c7 records 17 integration + 7 unit passing before reduction, not current selected-group execution. Main supplies current grading exit 0, PASSING 21; not rerun here. No tests, probes, grader, build, lint, formatter or broad suite executed. QA alone executes current T-01: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases && python3 tests/unit/test-validate-digest-run-pool-lines.py`.

Open questions: none.
