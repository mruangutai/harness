# FEAT-53 pinned goal-check — validation c0

## Gate record

- review_sha: `9b34c65246136666bc69f220824bb262965e75c0`
- default branch derived from repository history: `refs/remotes/origin/main`
- merge_base: `a18d6a9f1f832084df84be22097a409d73bf4f61`
- comparison: `a18d6a9f1f832084df84be22097a409d73bf4f61...9b34c65246136666bc69f220824bb262965e75c0` only
- diff: 279 paths, +25,506/-44
- verdict: `FAIL`
- severity_max: `high`
- cycles_used: `0`
- files_touched: [`.harness/harness/features/FEAT-53-metrics-dashboard/notes/research-FEAT-53-metrics-dashboard-goalcheck-validate-c0.md`]

**BLUF:** The feature is not delivered at the immutable pin. Pinned QA reports the unit, integration, and component commands green, but its verification gate still fails on missing durable criterion-binding fail-first evidence. More decisively, pinned browser inspection found the root unusable, both nested product routes blank on direct load, and the KPI/disclosure surface absent. Six automated or inspection SCs are unmet, seven UAT SCs remain unexecuted, and T-17 documentation is the operator-authorized deferred completion task.

All source, test, BRIEF, plan, DESIGN, and receipt citations below were read from the immutable pin or from reader artifacts explicitly bound to that pin. Mutable HEAD and later ledger changes are not review evidence.

## Done when — one verdict per perspective

- **operator (dashboard `/`): FAIL** — SC-26 still awaits UAT, while pinned browser evidence already shows `/` omitting Repository KPIs and then entering the TanStack error boundary (`review-harness-ui-reviewer-c0.md:17`).
- **operator (KPI `/kpi/$n`): FAIL** — SC-11 still awaits UAT, and a direct `/kpi/1` load is blank; source also renders only a label rather than the required panel/chart/table (`review-harness-ui-reviewer-c0.md:15,23`).
- **operator (work list on `/`): FAIL** — SC-27 still awaits UAT, and the broken root never exposes the required rows, layouts, filters, counts, or inline expansion (`review-harness-ui-reviewer-c0.md:17`).
- **operator (work item `/work/$id`): FAIL** — SC-28 still awaits UAT, and a direct work-detail load is blank because its relative asset request receives HTML (`review-harness-ui-reviewer-c0.md:15`).
- **orchestrator: PARTIAL** — SC-29's exact/null token and null-aware aggregation outcomes are green, but QA's high F-01 records no durable criterion-binding fail-first evidence for that SC (`review-harness-qa-c0.md:64-76`).
- **code maintainer: PARTIAL** — SC-23's lifecycle/invariant/backfill outcomes are green and T-25 remains operator-ratified, but QA's high F-01 records the same missing fail-first proof for the lifecycle criterion (`review-harness-qa-c0.md:62,65-76`).

## Requirement trace coverage

Every requirement has a shipped-code task carrier; this establishes non-drop coverage, not successful delivery. T-17 is separately deferred and does not erase the code carriers.

| Requirement | Pinned task/code carriers |
|---|---|
| REQ-01 | T-02/T-03/T-04/T-12/T-16; T-17 documentation deferred |
| REQ-02 | T-06/T-12/T-16 and T-23/T-26 fleet collection |
| REQ-03 | T-06 KPI core; T-14 presentation |
| REQ-04 | T-06 KPI core; T-14 presentation |
| REQ-05 | T-08 sourcing/count; T-14 presentation; T-17 documentation deferred |
| REQ-06 | T-11 event counter; T-20 call sites |
| REQ-07 | T-07/T-14/T-15/T-18/T-21/T-22 |
| REQ-08 | T-07 live file mix; T-14 caveat; T-17 documentation deferred |
| REQ-09 | T-09 attribution join |
| REQ-10 | T-03/T-10/T-15/T-19/T-21 |
| REQ-11 | T-05/T-06/T-10/T-11/T-14/T-15/T-18/T-21 |
| REQ-12 | T-01/T-05/T-13/T-21/T-22/T-28 |
| REQ-13 | T-12 read-only server and integration status checks |
| REQ-14 | T-04/T-12 prerequisite gate; T-17 documentation deferred |
| REQ-15 | T-10 weekly series; T-14/T-21 presentation |
| REQ-16 | T-23/T-26 collector; T-27 API; T-28 client |
| REQ-17 | T-24 attention derivation; T-28 client |
| REQ-18 | T-25 grilling lifecycle and invariant |
| REQ-19 | T-23/T-26 reconciliation; T-27/T-28 exposure |
| REQ-20 | T-23 disk-only/error preservation; T-27 API |
| REQ-21 | T-05/T-13/T-14/T-21/T-28 |
| REQ-22 | T-30 host measurement; T-31 aggregation; T-27/T-28 exposure |

## SC-01 through SC-29 inventory

Status vocabulary is exactly `met`, `unmet`, `deferred`, or `awaiting UAT`. A green suite is not treated as evidence for a clause the cited test does not exercise.

| SC | Status | Method | Evidence at pin |
|---|---|---|---|
| SC-01 | deferred | automated/integration | Runtime prerequisite branches are green (`test-metrics-dashboard.py:50-84,99-106`; QA artifact lines 45), but the required documented entry point is T-17 and no pinned `METRICS.md` exists. |
| SC-02 | awaiting UAT | UAT | No user UAT result; T-17 must first supply the documented command, and the pinned browser surface currently fails. |
| SC-03 | unmet | automated/integration | `test-metrics-dashboard.py:251-258` checks project root/name and one feature id only; it never compares each KPI with the repository value as the criterion requires. |
| SC-04 | met | automated/unit | QA's pinned unit run passed 42 files; individual carriers are `test-metrics-kpi.py:42-80,83-97,297-390`. QA F-01 still blocks verification quality because durable fail-first is missing. |
| SC-05 | met | automated/unit | `test-metrics-kpi.py:137-141` rejects central tendency; QA's unit command passed. QA F-01 records missing durable fail-first. |
| SC-06 | met | automated/unit | Live file-mix change and committed-source mutation proof at `test-metrics-kpi.py:83-97,143-155`; QA cites T-07 fail-first. |
| SC-07 | unmet | automated/unit | The cited case `test-metrics-trend.py:121-129` asserts unavailable/not-zero for `cycle_time_days` only, not every trend KPI individually. |
| SC-08 | awaiting UAT | UAT | No user UAT result; the shipped surface is currently unreachable after runtime failure. |
| SC-09 | unmet | automated/integration | `test-metrics-trend.py:56-81,208-230` proves sequential append, duplicate read resolution, and ship commit, but creates no separate worktrees and performs no two sequential merges; concurrent records can still be dropped or reordered undetected. |
| SC-10 | met | automated/integration | Two events ship as two (`test-metrics-trend.py:153-159`) and post-instrumentation absence is measured zero (`:131-137,179-196`); QA integration passed and cites T-11 fail-first. |
| SC-11 | awaiting UAT | UAT | No user UAT result; direct KPI/work routes are blank in pinned browser inspection. |
| SC-12 | met | automated/integration | Fixture views and full-repository KPI request preserve byte-identical git status (`test-metrics-dashboard.py:99-106,169-179`); QA integration passed. |
| SC-13 | met | automated/unit | Human-labelled escaped-defect rule and complete payload rule are asserted at `test-metrics-kpi.py:297-331`; QA unit passed. QA F-01 records missing durable fail-first. |
| SC-14 | met | automated/unit | Two model tiers plus unattributed commits at `test-metrics-kpi.py:342-390`; QA unit passed with T-09 fail-first. |
| SC-15 | unmet | inspection/browser | UI reviewer FAIL: detail routes blank, root unusable, focus contract broken, geometry wrong, and KPI panel absent (`review-harness-ui-reviewer-c0.md:15-23,51`). |
| SC-16 | met | automated/integration | Real repository `/api/kpis` passed the 8.0s ceiling (`test-metrics-dashboard.py:169-179`); QA integration passed. |
| SC-17 | met | automated/integration | Post-epoch zero, pre-epoch unavailable, no-epoch unavailable, and transition reasons at `test-metrics-trend.py:131-151,179-205`; aggregate not-tracked count at `test-metrics-kpi.py:63-71`; QA commands passed. |
| SC-18 | met | automated/integration | Pinned integration bridge and component command passed; `test-metrics-client-render.py:65-76`, with both required red states recorded in `receipt-harness-frontend-dev-2026-09-17-09-eng-T-21-c0.md:5-19`. |
| SC-19 | met | automated/integration | Hand-labelled weekly buckets, null-PR count, empty gaps, partial reason, sum, and segmentation at `test-metrics-trend.py:83-119`; QA integration passed. |
| SC-20 | unmet | inspection/browser | UI reviewer FAIL: tiles/disclosures never render and `/kpi/$n` lacks the panel needed for disclosure/drill-down (`review-harness-ui-reviewer-c0.md:23,52`). |
| SC-21 | met | automated/integration | Fleet rows, primary/orphan/terminal worktrees, worktree-wins paths, and no-GitHub behavior at `test-work-dashboard.py:123-133,195-246`; QA integration passed. |
| SC-22 | unmet | automated | `test-work-dashboard.py:301-325` samples 44/46 minutes rather than 44:59/45:00, has no 6d23:59 boundary, and carries no mutation proof for changing a threshold or rank; QA independently records missing fail-first. |
| SC-23 | met | automated/integration | Creation/intake/abandonment/invariant/backfill checks at `test-grilling-status.py:33-52,74-102`; QA integration passed. T-25 is operator-ratified and not relitigated; QA F-01 is a verification-process blocker. |
| SC-24 | awaiting UAT | UAT | No user UAT result; root runtime failure prevents the scripted interaction today. |
| SC-25 | met | automated/integration | Shared filters/defaults, live recompute, schema, errors, and retained routes at `test-metrics-dashboard.py:108-167`; QA integration passed. |
| SC-26 | awaiting UAT | UAT | No user UAT result; UI review already found the root unusable and geometry/route clauses violated. |
| SC-27 | awaiting UAT | UAT | No user UAT result; root failure prevents work-list exercise. |
| SC-28 | awaiting UAT | UAT | No user UAT result; direct `/work/$id` is blank in pinned browser inspection. |
| SC-29 | met | automated/unit+integration | Host exact/null token cases in `tests/unit/omp-hooks.test.ts` and null-aware item/phase aggregation at `test-work-dashboard.py:149-193`; QA unit/integration passed. QA F-01 records missing durable fail-first. |

Totals: **15 met · 6 unmet · 1 deferred · 7 awaiting UAT = 29**.

## Findings

These are goal-check findings. Each is independently accepted here as `reader: harness-pm`; UI-runtime evidence is cited rather than silently re-tested.

1. **PM-F01** — kind: `substance`; task: `T-16`; reader: `harness-pm`; severity: `high`. Evidence: `review-harness-ui-reviewer-c0.md:15`. Failure scenario: an operator reloads or bookmarks `/kpi/1` or `/work/FEAT-53-metrics-dashboard`; the relative bundle URL resolves under the nested route, Flask returns HTML, and the page is blank.
2. **PM-F02** — kind: `substance`; task: `T-14/T-28`; reader: `harness-pm`; severity: `high`. Evidence: `review-harness-ui-reviewer-c0.md:17`. Failure scenario: an operator starts the real server and `/` first shows a partial 500 shell, then crashes into the error boundary, exposing none of the contracted KPI or work surface.
3. **PM-F03** — kind: `substance`; task: `T-13`; reader: `harness-pm`; severity: `high`. Evidence: `review-harness-ui-reviewer-c0.md:19`. Failure scenario: a keyboard user receives the browser-default 1px outline and loses focus to body/error UI rather than seeing the specified ring and route landing.
4. **PM-F04** — kind: `substance`; task: `T-13/T-28`; reader: `harness-pm`; severity: `med`. Evidence: `review-harness-ui-reviewer-c0.md:21`. Failure scenario: the 1200px container removes hundreds of pixels of scan width at 1440/1920 and halves the required narrow gutter.
5. **PM-F05** — kind: `substance`; task: `T-14/T-28`; reader: `harness-pm`; severity: `high`. Evidence: `review-harness-ui-reviewer-c0.md:23`. Failure scenario: an operator cannot open the escaped-defect or merged-PR sourcing rule or use the required KPI panel drill-down because the root never renders tile links and the KPI route is only a label.
6. **PM-F06** — kind: `substance`; task: `T-12`; reader: `harness-pm`; severity: `high`. Evidence: pinned `test-metrics-dashboard.py:251-258` against BRIEF SC-03. Failure scenario: one or more KPI values leak from the Harness repository into another project while the integration test remains green because it checks only root/name and one feature id, not every KPI against both projects.
7. **PM-F07** — kind: `substance`; task: `T-10`; reader: `harness-pm`; severity: `med`. Evidence: pinned `test-metrics-trend.py:121-129` against BRIEF SC-07. Failure scenario: a missing ship record reports one trend KPI honestly but fabricates zero or interpolation for another, while the sole cycle-time assertion remains green.
8. **PM-F08** — kind: `substance`; task: `T-10`; reader: `harness-pm`; severity: `high`. Evidence: pinned `test-metrics-trend.py:56-81` and plan T-10's explicit three-worktree/two-merge requirement. Failure scenario: concurrent feature branches append separate records and a merge drops or reorders one; the sequential same-file test cannot detect it.
9. **PM-F09** — kind: `substance`; task: `T-24`; reader: `harness-pm`; severity: `med`. Evidence: pinned `test-work-dashboard.py:301-325` against BRIEF SC-22. Failure scenario: an off-by-one at exactly 45:00 or seven days, or a changed precedence rank, ships while the 44/46-minute sample and non-mutated order assertion remain green.

External QA finding retained without reclassification: `review-harness-qa-c0.md:70-76` records **F-01, substance, high**, tasks T-06/T-07/T-08/T-24/T-25/T-30, reader `harness-qa`: SC-04/05/13/22/23/29 lack durable criterion-binding fail-first evidence. This is not a relitigation of T-25.

## Known deferred completion work

- **T-17 only:** `.harness/harness/docs/METRICS.md` plus README documentation remains `ready` and is deliberately sequenced after clean validation. `METRICS.md` is absent at the pin. This is expected completion work, not a code finding and not a scope change.
- SC-01 is therefore `deferred`; SC-02 remains `awaiting UAT` until the documented command exists and the runtime blockers are repaired.

## Assessed and dismissed

- T-25 was operator-ratified. Its implementation and corpus decision are not relitigated; only QA's missing fail-first evidence is retained as the verification record states.
- The pinned QA commands themselves are green: unit 42 files, integration 77 files, component 5 files/20 tests. They do not override uncovered SC clauses or browser-observed failure.
- Exact registration of `/`, `/kpi/$n`, and `/work/$id` is present, but registration does not discharge direct-load usability.
- Prototype Chrome observations are accepted design evidence, not evidence that the shipped committed bundle works; they do not discharge UAT.
- The pre-review receipt at `b2f41726...` applies to byte-identical production/test code at the pin, but final SC outcomes above use the pinned QA and UI artifacts rather than treating that receipt as a blanket pass.
- Light-theme parity is not applicable because DESIGN contracts dark-only. No separate finding is raised.

## Open questions

None. The failures are reproducible and routable; no classification ambiguity remains.
