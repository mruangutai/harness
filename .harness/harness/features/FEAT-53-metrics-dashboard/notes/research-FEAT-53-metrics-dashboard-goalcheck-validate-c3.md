# FEAT-53 pinned goal-check — validation c3

## Verdict and boundary

**FAIL at immutable pin `ffd9fb0204701cdae968ef0febc86943fb4829bd`.** The implementation is broadly present and the five authorized frontend c2 findings are technically closed, but this is not a clean technical validation: the active integration matrix has three assertion failures, the frontend unit-kind floor is unbound, a high-severity Host/DNS-rebinding defect remains, and the canonical code grade has four actionable high records. Seven UAT criteria have not been executed. T-17 documentation is deliberately planned after a clean technical gate and is recorded only as planned-post-gate work, not as emergent scope or a new finding.

Evidence is pinned or same-pin: `review-harness-qa-c3.md`, `review-harness-code-reviewer-c3.md`, `review-harness-security-reviewer-c3.md`, and `review-harness-ui-reviewer-c3.md` all name `ffd9fb0204701cdae968ef0febc86943fb4829bd`. The BRIEF and plan are byte-identical to that pin.

## Done when — exactly one grade per declared perspective

1. **operator dashboard `/`: PARTIAL.** SC-26 is still `not_met` because no operator UAT has run. The technical surface improved: the same-pin Chrome evidence closes regional failure isolation, focus, fixed-dark painting, and 1440/831 geometry (`review-harness-ui-reviewer-c3.md:11-25`). It cannot be graded pass while the signed end-to-end UAT is absent and the active integration/static-route and performance checks remain red (`review-harness-qa-c3.md:20-24`).
2. **operator KPI `/kpi/$n`: FAIL.** SC-11 has not had UAT. In-app KPI navigation, disclosure, and row drill work in same-pin Vite/Chrome evidence (`review-harness-ui-reviewer-c3.md:13-17`), but direct use of the committed Flask surface still has inherited V-01 mechanics: `client/dist/index.html:7` uses `./assets/index-Kjo9UJkL.js`, so a nested URL resolves that request beneath `/kpi/`; `dashboard/serve.py:96-108` serves only `/assets/...` and otherwise returns HTML. A bookmarked or reloaded KPI route can therefore receive HTML instead of JavaScript. This is the concrete unmet behavior, not a new scope class.
3. **operator work list on `/`: PARTIAL.** SC-27 is `not_met` until the operator exercises the complete Kanban/Table, filter, field, count, and inline-expansion script. Same-pin browser evidence proves the root preserves the usable work region under KPI failure and renders/operates a real work row (`review-harness-ui-reviewer-c3.md:13-14`), while component tests pass 23/23 (`review-harness-qa-c3.md:13-16`). That is technical evidence, not the missing full UAT.
4. **operator work item `/work/$id`: FAIL.** SC-28 has not had UAT, and the same inherited relative-asset behavior above applies to a direct `/work/$id` load. In-app row navigation reaches the route title (`review-harness-ui-reviewer-c3.md:14`), but a reload/bookmark resolves `./assets/...` below `/work/` and the catch-all returns HTML (`client/dist/index.html:7`; `dashboard/serve.py:96-108`). The signed route is therefore not reliably usable.
5. **orchestrator: PARTIAL.** SC-29's observable exact-token, null, phase aggregation, unmeasured-run, and no-dollar behavior is implemented and its T-30 direct lane remains closed; the current bindings are `tests/unit/omp-hooks.test.ts` and `tests/integration/test-work-dashboard.py:149-193` (`review-harness-qa-c3.md:26-30`). It is not a full pass because QA retains missing durable criterion-binding red evidence as inherited/non-actionable gate debt, and T-31's `_tokens` remains a high canonical grade failure (`review-harness-code-reviewer-c3.md:25-36`). This does not reopen T-30.
6. **code maintainer: PARTIAL.** SC-23's lifecycle transitions, invariant, and corpus migration are implemented; T-25's direct fixes `84a07a81` and `701ec6d8` brought the previously failed T-25 functions/tests above the grade bar, so V-10 and V-11 stay closed. QA still records SC-23's absent criterion-binding red execution as inherited/non-actionable evidence debt (`review-harness-qa-c3.md:26-30,38-43`). This is a partial verification grade, not reopened T-25 scope.

## Success-criterion inventory

`met` means the pinned evidence directly exercises the criterion. `partial` means the behavior is green but required evidence or the deliberately sequenced documentation is incomplete. `not_met` means the signed method has not run or a concrete clause/gate is red.

| SC | Verdict | Pinned evidence |
|---|---|---|
| SC-01 | partial | Runtime prerequisite and payload branches have integration bindings, but the documented entry point is T-17 planned-post-gate; the active integration file is also red on its static asset assertions (`review-harness-qa-c3.md:20-24,43`). |
| SC-02 | not_met | No user UAT result; T-17 must first provide the documented command. |
| SC-03 | not_met | `test-metrics-dashboard.py:251-258` checks root, name, and one feature id, not every KPI against this repository. That test surface is unchanged from V-07's pinned finding (`research-FEAT-53-metrics-dashboard-goalcheck-validate-c0.md:65,104`). |
| SC-04 | partial | Hand-labelled KPI assertions are green, but QA retains missing criterion-binding red evidence for T-06 (`review-harness-qa-c3.md:26-30`). |
| SC-05 | partial | Grade-share and named outlier behavior is green, but QA retains missing criterion-binding red evidence for T-07 (`review-harness-qa-c3.md:26-30`). |
| SC-06 | met | Live file-mix change and committed-source mutation proof remain bound (`research-FEAT-53-metrics-dashboard-goalcheck-validate-c0.md:68`). |
| SC-07 | not_met | The pinned test asserts unavailable/not-zero only for `cycle_time_days`, not every trend KPI (`tests/integration/test-metrics-trend.py:121-129`); V-19's concrete coverage gap is unchanged. |
| SC-08 | not_met | No user UAT result for a pre-capability feature's stated absence/no-zero chart behavior. |
| SC-09 | not_met | The pinned test preserves sequential append bytes and reads merged duplicates, but creates no two separate worktrees and performs no two-branch merge (`tests/integration/test-metrics-trend.py:56-81`); V-08 remains mechanically uncovered. |
| SC-10 | met | Two-touchpoint and zero-touchpoint outcomes retain integration and fail-first evidence (`review-harness-qa-c3.md:26-30`). |
| SC-11 | not_met | No user UAT; nested committed-bundle reload remains concretely broken by the relative asset/catch-all combination described above. |
| SC-12 | met | Byte-identical no-write behavior retains its integration binding and red evidence (`review-harness-qa-c3.md:26-30`). |
| SC-13 | partial | Escaped-defect count/rule behavior is green, but QA retains missing criterion-binding red evidence for T-08 (`review-harness-qa-c3.md:26-30`). |
| SC-14 | met | Two model tiers plus explicit unattributed usage retain unit and fail-first evidence (`review-harness-qa-c3.md:26-30`). |
| SC-15 | met | Pinned source uses the Astryx three-route shell and the UI reader passes the inspected browser surface (`review-harness-code-reviewer-c3.md:5-11`; `review-harness-ui-reviewer-c3.md:27-42`). |
| SC-16 | not_met | Current full-repository KPI request measured 8.214s, failing the signed `< 8.0s` ceiling (`review-harness-qa-c3.md:23`). |
| SC-17 | met | Exact zero versus unavailable/null behavior retains its integration binding and fail-first evidence (`review-harness-qa-c3.md:26-30`). |
| SC-18 | met | Component matrix passes 5 files/23 tests, and the mounted-chart binding retains its red record (`review-harness-qa-c3.md:13-16,26-30`). |
| SC-19 | met | Weekly count, null-PR, gaps, reasons, and segmentation retain integration/fail-first binding (`review-harness-qa-c3.md:26-30`). |
| SC-20 | met | Adjacent keyboard-operable disclosures and KPI-4/KPI-7 sourcing-rule selection are present at the pin; browser disclosure/drill operation passes (`review-harness-code-reviewer-c3.md:9-11`; `review-harness-ui-reviewer-c3.md:14-21`). |
| SC-21 | met | Fleet/worktree collection remains bound; c3 code review confirms the former two collector fail-open defects were repaired and are not re-raised (`review-harness-code-reviewer-c3.md:15-18`). |
| SC-22 | partial | Exact 44:59/45:00 and 6d23:59/7d boundaries plus ORDER mutation are present (`tests/integration/test-work-dashboard.py:288-353`); closed T-24/V-16/V-20 is not reopened. QA nevertheless retains the old missing durable red receipt as inherited/non-actionable gate debt (`review-harness-qa-c3.md:26-30,38-43`). |
| SC-23 | partial | Lifecycle/invariant/backfill behavior and T-25 grade repairs are present; missing durable red evidence remains inherited/non-actionable, as reflected in the code-maintainer grade. |
| SC-24 | not_met | No user UAT result for cards, filters, four work kinds, source locations, and no-GitHub operation. |
| SC-25 | not_met | The active integration gate gets 404 for the stale expected asset in both fixture and work-API route cases, so the signed retained-static-route clause is red (`review-harness-qa-c3.md:20-24`; `test-metrics-dashboard.py:261-270`; `client/dist/index.html:7`). |
| SC-26 | not_met | No user UAT result; same-pin browser evidence closes only the authorized technical/UI findings. |
| SC-27 | not_met | No user UAT result for the complete work-list contract. |
| SC-28 | not_met | No user UAT result, and direct nested-route bundle loading remains broken as stated above. |
| SC-29 | partial | Exact/null token aggregation behavior is green and T-30 stays closed, but inherited missing red evidence plus the T-31 high grade prevent complete verification (`review-harness-qa-c3.md:26-30`; `review-harness-code-reviewer-c3.md:25-36`). |

Totals: **10 met · 7 partial · 12 not_met = 29**.

## Technical blockers and dispositions

These retain the originating reader's severity and kind; no finding is reclassified here.

- **Open/actionable — high, integration, QA — T-16/T-12/T-27:** stale expected bundle asset produces two 404 assertions (`review-harness-qa-c3.md:20-24`). Concrete failure: the active fixture and work-API route tests cannot load the asset they assert.
- **Open/actionable — high, integration, QA — T-12:** SC-16 measures 8.214s against `<8.0s` (`review-harness-qa-c3.md:23`). Concrete failure: a repository-scale KPI request exceeds the signed ceiling.
- **Open/actionable — high, unit, QA — T-13/T-14/T-15/T-21/T-28:** the configured frontend unit kind selects Python tests only and binds no changed client behavior (`review-harness-qa-c3.md:24`).
- **Open/actionable — high, substance, security-reviewer — T-12:** arbitrary Host acceptance permits DNS rebinding to unauthenticated local JSON (`review-harness-security-reviewer-c3.md:10-13,23-40`).
- **Open/actionable — four high, substance, code-reviewer — T-06/T-31/T-27/T-26:** `kpi.compute`, `work._tokens`, the work-API integration test, and the worktree integration case remain below their canonical grade bars, with concrete maintenance failure scenarios preserved at `review-harness-code-reviewer-c3.md:23-49`.
- **Open signed-criterion mechanics — inherited V-01/V-07/V-08/V-19:** direct nested routes still resolve the relative bundle path incorrectly; SC-03 does not assert every KPI's project isolation; SC-09 does not exercise separate-worktree merge survival; SC-07 does not assert every trend field. The concrete evidence is cited in the SC rows above.
- **Inherited/non-actionable:** QA's missing durable fail-first records for SC-04/05/13/22/23/29 remain gate debt (`review-harness-qa-c3.md:26-30,38-43`). Closed direct-lane V-09 for T-24/T-25/T-30, V-10, V-11, V-16, and V-20 are not reopened.
- **Resolved:** V-02, V-03, V-17, V-18, and fixed-dark are closed by same-pin browser evidence (`review-harness-qa-c3.md:32-40`; `review-harness-ui-reviewer-c3.md:11-25`).
- **Planned-post-gate:** T-17 only — `.harness/harness/docs/METRICS.md` and README documentation remain `ready` in the approved plan. Their absence explains SC-01's partial state and blocks SC-02 UAT setup, but is the operator's known sequencing, not an emergent technical finding.

## REQ coverage

No approved requirement was dropped: c3 code review passes full spec compliance over the complete merge-base-to-pin range and finds the implementation traced to the signed tasks and D-01..D-31 (`review-harness-code-reviewer-c3.md:5-13`). REQ-01 through REQ-22 therefore retain shipped code carriers; T-17 is the sole deliberately unfinished documentation carrier. Trace presence does not override the SC verdicts or failed technical gates above.

## Open questions

None. The blockers are concrete and classified; the remaining UAT needs execution rather than a product decision.