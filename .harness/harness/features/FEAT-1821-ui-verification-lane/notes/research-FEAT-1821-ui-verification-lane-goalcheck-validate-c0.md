# FEAT-1821 pinned goal-check — validation c0

## Verdict and boundary

**FAIL at immutable review pin `711ba16227eda39ddb397ed574e4ca199fbc5984`.** The lane and its 23 Playwright executions exist, the committed run preserves the intended FEAT-53 RED product signal, and the routing/CI mechanisms are substantially present. It is not ready to validate-exit because the committed inspection bundle fails open, its served-bundle pin is refused by the exact same-pin gate, and the required component kind cannot collect tests.

`sc_status: fail`. `needs_approval: true`: the inspection producer/gate and missing dependency are repairs inside T-01/T-03/T-06, but reconciling committed evidence with strict `served_bundle_commit == review_sha` is self-referential and needs an approved provenance rule rather than another evidence-only commit.

Evidence is pin-bound: QA and UI review both name `711ba16227eda39ddb397ed574e4ca199fbc5984` (`review-harness-qa-c0.md:4-5`; `review-harness-ui-reviewer-c0.md:1,7`). No source, test, fixture, BRIEF, or plan file was changed by this goal-check.

## Done when — exactly one grade per declared perspective

1. **operator — FAIL — SC-01, SC-02, SC-03, SC-04.** The configured lane lists 23 browser executions and the committed bundle records the intended RED result, but the operator cannot rely on the screenshots: four inspection records say `status: evidence` while their own errors report every signed setup/capture failed, and the referenced images are blank or depict the wrong state (`review-harness-ui-reviewer-c0.md:14-20`). The exact same-pin gate also refuses `served_bundle_commit=0ef52107…` against `711ba162…` (`review-harness-qa-c0.md:29-32`). SC-03's honest FEAT-53 product RED and SC-04's opt-in-only baseline policy remain valid; they do not cure structurally untrustworthy evidence.
2. **code maintainer — PARTIAL — SC-05, SC-06, SC-07.** DESIGN carries 12 unique exact-title rows and a 22-row inspection manifest (`.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md:860-915`); results carry the versioned fields and the fixture/config pin deterministic inputs (`ui-reporter.ts:82-92`; `fixture.ts:11-49`; `playwright.config.ts:13-24`). SC-05 is not discharged because non-empty but blank/wrong-state files satisfy completeness despite failed setups, so the single contract does not fail closed on semantically absent inspection evidence.
3. **reader (QA / ui-reviewer) — FAIL — SC-08, SC-09.** Mode B did read 41/41 WebPs and correctly returned FAIL (`review-harness-ui-reviewer-c0.md:7-20`), and the check table/spec inventory covers the declared automated-versus-inspection split. But the committed evidence cannot grade the built states: the lane labels failed inspection setup as evidence, and the reader accepted ancestor `0ef52107…` as the required bundle pin even though the canonical Mode B rule requires equality with the pinned review SHA (`.omp/agents/harness-ui-reviewer.md:65-71`; `review-harness-qa-c0.md:29-32`).
4. **orchestrator — PARTIAL — SC-10, SC-11, SC-12.** The `ui` kind is active (`.harness/harness.json:333-337`), the complete-client-contract branches and tests exist (`ui_contract.py:213-309`; `tests/unit/test-ui-verification-contract.py:286-303`), and CI installs package-resolved Chromium immediately after dashboard npm ci (`.github/workflows/tests.yml:89-93`). The final matrix is nevertheless blocked: component collection fails because `@testing-library/react`'s required `@testing-library/dom` peer is absent, the unit runner was contaminated by the concurrently mutated watched Vite cache, and the exact UI gate refuses the evidence pin (`review-harness-qa-c0.md:14-32,51-58`).

## Success-criterion inventory

`met` means pinned evidence directly discharges every clause. `partial` means implementation is present but same-pin verification or one clause is missing. `not_met` means a concrete clause fails.

| SC | Verdict | Pinned evidence |
|---|---|---|
| SC-01 | partial | The configured list exits 0 with 23 tests, and the committed run is RED, but its bundle pin is `0ef52107…`, not the immutable review pin; only the pre-lane list-command fail-first is recorded (`review-harness-qa-c0.md:24-32,42-44`). |
| SC-02 | not_met | There are 23 records and 41 non-empty WebPs, with SRC-TOKENS once and the other applicable rows at both projects, but multiple required inspection images are blank or wrong-state after setup failures; file presence is not the promised per-execution evidence (`review-harness-ui-reviewer-c0.md:8-20`). |
| SC-03 | met | The committed run has 22 non-green executions (18 `failed` plus four inspection records carrying failures), one green SRC-TOKENS record, `missing_check_ids: []`, overall `failed`, and no FEAT-53 `src`, `dist`, or `serve.py` production diff. This is the intentionally honest FEAT-53 product RED, not a lane finding (`results.json:6,18-77,1088-1092`; `review-harness-ui-reviewer-c0.md:22-24`). |
| SC-04 | met | DESIGN declares `pixel-baseline` explicit opt-in and says no FEAT-53 row uses it (`DESIGN.md:865-866`); the lane contains no default `toHaveScreenshot` gate. |
| SC-05 | not_met | The table, exact titles, projects, and arithmetic accounting exist, but the gate accepts four inspection records whose setup/capture failed because non-empty mismatched WebPs exist. Required evidence is therefore fail-open (`review-harness-ui-reviewer-c0.md:14-20,33-36`). |
| SC-06 | met | `results.json` carries schema, feature/run/design/pin, both project viewports, listed/applicable/observed/missing accounting, 23 per-check records, screenshot metadata, errors, and summary (`results.json:1-1092`; `ui-reporter.ts:13,69-92`). The false completeness is graded under SC-05 rather than hiding these present fields. |
| SC-07 | met | Fixture rows cover attention, grilling, worktree, unavailable, filtered-zero, source/request error, overflow, and long content with fixed clock (`fixture.ts:11-49`); config fixes locale, UTC, dark scheme, reduced motion, scale 1, both viewports, and `serve.py --root` (`playwright.config.ts:13-24`). |
| SC-08 | partial | The canonical rule requires every WebP, exact pin equality, declared project/accounting/state fields, configured-lane-only rerun, and FAIL on stale/mismatched/incomplete evidence (`.omp/agents/harness-ui-reviewer.md:60-74`). The reader correctly fails the bundle for wrong pixels, but accepted ancestor `0ef52107…` as the required pin while QA's exact same-pin gate refuses it (`review-harness-ui-reviewer-c0.md:7-20`; `review-harness-qa-c0.md:29-32`). |
| SC-09 | met | DESIGN assigns all ten executable predicate families and two inspection-only families with exact titles/projects/predicates plus route/state/interaction/viewport manifests (`DESIGN.md:860-915`); configured discovery finds the intended 23 executions (`review-harness-qa-c0.md:24-28`). The FEAT-53 predicate failures are expected results, not missing assignments. |
| SC-10 | partial | Active command/detect and fail-closed missing-runner/table/bundle rules are present (`.harness/harness.json:333-337`; `.claude/skills/harness-qa-gate/SKILL.md:80-105`), but the same-pin unit evidence did not complete and QA's required gate is structurally red (`review-harness-qa-c0.md:14-32`). |
| SC-11 | partial | Source and named tests require every spec title for a dashboard-client change (`ui_contract.py:286-293`; `tests/unit/test-ui-verification-contract.py:286-291`), but the configured same-pin unit runner did not produce a clean result and no pinned fail-first receipt demonstrates this branch (`review-harness-qa-c0.md:42-54`). |
| SC-12 | met | Pinned workflow lines 89-93 place `Install the dashboard Chromium`, with `npx playwright install --with-deps chromium`, immediately after dashboard-client npm ci; the task digest records its exact assertion red-before/green-after (`runs/build-eng-t04-eng/digest.md`, adequacy notes). |

Totals: **5 met · 4 partial · 3 not_met = 12**.

## Findings

1. **GC-01 — substance · critical · T-06 / main-session-direct.** Inspection setup failures are published as complete evidence.
   - Concrete failure scenario: a reviewer sees `status: evidence`, `missing_check_ids: []`, and non-empty WebPs and approves density, prototype fidelity, focus, overflow, error-state, or accessibility behavior even though the required route/state/interaction never rendered.
   - Evidence: all four inspection records report every signed setup/capture failed yet retain `status: evidence`; blank and generic wrong-state captures are documented at `review-harness-ui-reviewer-c0.md:14-20` and `results.json:491-546,733-766,864-917,1010-1042`.
   - Required repair: T-06/main-session-direct must commit state-matching evidence, while the T-03 producer or T-01 gate rejects any inspection record whose setup failed instead of treating any non-empty WebP as proof.

2. **GC-02 — substance · high · T-01/T-05/T-06 / main-session-direct.** The committed evidence cannot satisfy strict equality to the immutable review SHA.
   - Concrete failure scenario: QA invokes the documented gate at review pin `711ba162…`; it refuses the committed run because `results.json:6` names ancestor `0ef52107…`. Rerunning at the current commit and committing the result changes the review SHA again, so an evidence-only retry cannot resolve strict self-equality.
   - Evidence: `results.json:6`; equality check at `ui_contract.py:238-241`; canonical reviewer rule at `.omp/agents/harness-ui-reviewer.md:65-71`; exact failing invocation/output at `review-harness-qa-c0.md:29-32,53-58`.
   - Scope change recommendation: approve one immutable provenance subject that can be committed after execution, such as the served bundle tree/blob digest plus its source commit, and make T-01 gate, T-05 reader policy, BRIEF language, and T-06 evidence agree. Do not waive pinning or compare against moving HEAD.

3. **GC-03 — substance · high · T-03 / harness-frontend-dev.** Required component coverage cannot collect.
   - Concrete failure scenario: any dashboard-client change requiring the configured component kind loads five Vitest suites, but every suite stops before collection because `@testing-library/dom` is absent; no component assertion can catch a regression.
   - Evidence: QA output at `review-harness-qa-c0.md:14-23,51-56`; `package.json:24` declares `@testing-library/react`, while its lock entry declares the unresolved `@testing-library/dom` peer at `package-lock.json:832-845`.
   - Required repair: T-03/harness-frontend-dev must pin/install the peer through the package manifest and lock, then return a clean configured component result.

4. **GC-04 — form · medium · T-01 / main-session-direct.** Automated discrimination evidence is incomplete.
   - Concrete failure scenario: a future green suite is credited for SC-02..SC-06 or SC-10..SC-11 even if the named checks never distinguished the pre-lane state, because only SC-01 has a pinned red-before receipt.
   - Evidence: QA fail-first inventory at `review-harness-qa-c0.md:42-54` identifies gaps for SC-02 through SC-06 and SC-10 through SC-11.
   - Required repair: record pinned mutation or pre-change executions for the named contract branches; do not substitute source presence or current-green assertions.

## Expected FEAT-53 RED kept separate

The FEAT-53 run's 22 non-green executable outcomes and green SRC-TOKENS are the required honest product signal. Header/KPI geometry, identity/status colour, keyboard/focus, contrast, hatch, tables, and accessibility remaining RED do not count against FEAT-1821 (`review-harness-ui-reviewer-c0.md:22-24`). FEAT-1821 fails only on its own structural delivery: failed setups accepted as evidence, same-pin provenance disagreement, broken component collection, and missing fail-first proof.

## Trace and approval disposition

Every SC-01..SC-12 is traced by at least one signed task in `plan.yaml`; nothing was dropped by trace presence. Trace presence does not override the three `not_met` or four `partial` outcomes above. GC-01 and GC-03 are repairs within signed task intent. GC-02 changes the signed provenance contract and therefore requires approval; `needs_approval: true`. No UAT criterion exists in this BRIEF.
