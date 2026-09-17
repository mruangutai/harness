# QA c3 — FEAT-53 metrics dashboard

**BLUF: FAIL at immutable `ffd9fb0204701cdae968ef0febc86943fb4829bd`.** The full active matrix was run at that pin: unit and component pass, but integration has three real assertion failures. Independently, the signed frontend matrix floor requires a unit binding which the Python-only unit runner cannot provide. The fail-first record remains incomplete for six automated criteria. No formatter or linter was run.

## Phase 1 — requirement-derived coverage

Before source inspection, the automated criteria required separate executable proof for: entry/prerequisite branches and project isolation (SC-01/03); individually-labelled KPI and exclusion cases (SC-04–07, 13–14); append/merge, touchpoint and read-only boundaries (SC-09–12, 16–17, 19); mounted chart output (SC-18); fleet collection/attention/grilling/API filtering (SC-21–23, 25); and transcript-to-null-aware token aggregation (SC-29). Frontend tasks also require `unit` and `component`, plus `ui` when the interaction-flow predicate applies.

## Matrix at pin

| kind | requirement and discovery | command | result |
|---|---|---|---|
| unit | `logic`, `api`, `feature`, `cross_module`, and `frontend` all require it; runner enumerates `tests/unit/test-*.py` | `env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | **PASS**, 42 files, 9.01s. This does **not** bind changed client behaviour. |
| integration | `cross_module` and `feature` require it; API runtime surfaces and config-shape also require it; runner enumerates `tests/integration/test-*.py` | `env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | **FAIL**, 77 files, 150.96s; `test-metrics-dashboard.py` has 3 assertion failures. |
| component | `frontend.always` requires it; client test files match the configured client detect glob | `npm --prefix .claude/skills/harness/bin/dashboard/client run test` | **PASS**, 5 files / 23 tests / 1.61s (the jsdom `Window.scrollTo()` notices are non-fatal). |
| ui | frontend/feature interaction predicate fires, but `ui` is configured `cmd: null`, `status: unresolved`; BRIEF verification-gap record assigns this to UAT/inspection | no command | **unresolved signed coverage limitation**, not counted as an active runnable kind. |

`matrix_ok: false`. The first two rows are grounded in `.harness/harness.json:174-202,284-345` and runner discovery in `run-unit-tests.py:82-99`; the configured active command coverage is therefore real, not a detect-glob inference.

### Active integration failures — actionable

**F-QA-01 — severity: high; kind: integration; tasks: T-16, T-12, T-27.** **Scenario:** `tests/integration/test-metrics-dashboard.py:261-270` requests `/assets/index-hkwR5g06.js` after serving the dashboard and receives 404 in both fixture and work API route tests. The pin’s `client/dist/index.html:7` instead references `index-Kjo9UJkL.js`; a consumer following the tested static asset route receives no JavaScript. The committed bundle asset contract is stale.
**F-QA-02 — severity: high; kind: integration; task: T-12.** **Scenario:** `test_repository_api_request_is_kpi_payload_under_ceiling` measured `/api/kpis?window=all` at **8.214s**, above its signed `< 8.0s` assertion (`tests/integration/test-metrics-dashboard.py:169-179`). This is a real measured assertion failure, not collection/configuration failure.
**F-QA-03 — severity: high; kind: unit; tasks: T-13, T-14, T-15, T-21, T-28.** **Scenario:** `frontend.always` explicitly names `unit` and `component` (`.harness/harness.json:180-184`), but the unit runner selects only `tests/unit/test-*.py` (`run-unit-tests.py:82-88`); a regression in any changed `.tsx` dashboard path can pass the required unit command because no client behaviour runs there. The passing Vitest component suite and integration render wrapper cannot satisfy a distinct `unit` kind under the signed config. This is the c1/c2 gap retained, not a claim that the Python unit command failed.

## Fail-first provenance

Current green test bindings and durable red evidence are: SC-01/03/12/16 — `tests/integration/test-metrics-dashboard.py`, `receipt-harness-backend-dev-2026-09-17-07-eng-T-12-c0.md:9`; SC-06 — `tests/unit/test-metrics-kpi.py`, `receipt-harness-backend-dev-T-07-c0.md:11`; SC-07/19 — `tests/integration/test-metrics-trend.py`, `receipt-harness-backend-dev-T-10-c0.md:25-27`; SC-09 — trend integration test, `receipt-harness-backend-dev-T-19-c0.md:5-18`; SC-10/17 — trend integration test, `receipt-harness-backend-dev-T-11-c0.md:5-16`; SC-14 — KPI unit test, `receipt-harness-backend-dev-T-09-c0.md:6-8`; SC-18 — client render integration test, `receipt-harness-frontend-dev-2026-09-17-09-eng-T-21-c0.md:5-10`; SC-21 — work-dashboard integration test, `receipt-harness-backend-dev-T-23-c0.md:5-23`; SC-25 — dashboard integration test, `receipt-harness-backend-dev-2026-09-17-08-eng-T-27-c0.md:9`.

**Missing durable criterion-binding red evidence remains:** SC-04, SC-05, SC-13 (T-06/T-07/T-08), SC-22 (T-24), SC-23 (T-25), and SC-29 (T-30). This is the same c0 fail-first gap (`review-harness-qa-c0.md:47-69`); no c1/c2 receipt supplies a red run for these criteria. It independently prevents PASS. T-24/T-25/T-30 are closed direct-lane work and are recorded here as inherited/non-actionable evidence debt, not reopened.

## V-02 ruling — resolved

**Governing criterion:** independent regional query isolation: a failed `/api/kpis` must leave work usable and a failed `/api/work` must leave KPI content usable. The current two observable assertions are `routes.test.tsx:95-109` and `:111-123`; the browser independently confirms both directions in `review-harness-ui-reviewer-c2.md:11`.

The c1 red in `receipt-harness-frontend-dev-fix-c1.md:14` is sufficient fail-first provenance for this *single signed behaviour*: the concrete mutant/failure scenario is a shared/combined error boundary (or equivalent coupled query state) in which rejecting either independent request hides the settled other region. With `/api/kpis` rejected, the c1 test failed because the required `Repository KPIs unavailable` isolated state was absent and the usable Work List was not retained. That red discriminates the coupling mutant. Current green assertions establish both input directions, including `/api/work` rejection retaining the KPI heading and Escaped Defects link. A converse-only historical red is not required retroactively: it would prove a second defect, whereas the signed criterion excludes coupled regional failure; it does not require two historically distinct regressions. The fact that the converse assertion passes at `7dbb025` means that direction was already correct, not that the repaired coupled failure lacks a discriminating red.

## Dispositions and limits

- **Resolved:** V-02 as above; V-03/V-17/V-18/fixed-dark are supported by current browser evidence in `review-harness-ui-reviewer-c2.md:11-15` and their cited red/green receipts. Closed V-09, V-10, V-11, V-16 and V-20 were not reopened.
- **Open/actionable:** the three kind-bearing findings above.
- **Inherited/non-actionable:** the six fail-first provenance gaps, including direct-lane T-24/T-25/T-30; they remain gate failures, not newly reopened implementation scope.
- **Planned post-gate:** T-17 documentation, deliberately scheduled after clean technical validation.
