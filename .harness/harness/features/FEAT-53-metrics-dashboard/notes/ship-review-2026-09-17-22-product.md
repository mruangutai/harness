# Ship review — FEAT-53 metrics dashboard

## Decision

**Awaiting user acceptance, not yet ready to ship.** The implementation, inspection, broad automated gate, component gate, canonical code grade, and documentation are green. The remaining gate is the operator-run UAT for SC-02, SC-08, SC-11, SC-24, SC-26, SC-27, and SC-28.

- reviewed implementation pin: `93785232ac32ae4fecc0a456d286e772ad15eb82`
- documentation commit: `db1b5ac51c6ad224737a52adf673eb3312ffeb61`
- UAT: `.harness/harness/features/FEAT-53-metrics-dashboard/notes/uat.md`

## Done when — graded by perspective

| Perspective | Signed done condition | Verdict | SCs | Evidence |
|---|---|---:|---|---|
| Operator — dashboard `/` | Shared window/repository controls, centred 4+3 KPI geometry, then Status-driven work list | **unmet — awaiting user** | SC-26 | Technical UI review passed in `notes/review-harness-ui-reviewer-c3.md`; operator step U-05 remains blank in `notes/uat.md`. |
| Operator — KPI `/kpi/$n` | One KPI panel; row drill reaches `/work/$id`; selections persist | **unmet — awaiting user** | SC-11 | Browser drill/disclosure evidence is in `notes/review-harness-ui-reviewer-c3.md`; the repaired payload disclosure is in `notes/review-harness-ui-reviewer-c6.md`; operator step U-03 remains blank. |
| Operator — work list on `/` | Kanban/Table, Station/Status/Kind filters, full operational fields | **unmet — awaiting user** | SC-27 | Component suite is 23/23 green; operator step U-06 remains blank. |
| Operator — work item `/work/$id` | Feature/bug operational header then KPI content; grilling/worktree inline only | **unmet — awaiting user** | SC-28 | Browser/component evidence is green; operator step U-07 remains blank. |
| Orchestrator | Exact-or-null run tokens survive item and phase aggregation without invented zero/cost | **met** | SC-29 | `runs/2026-09-17-17-validator/digest.md` keeps T-30 closed; `runs/2026-09-17-19-validator/digest.md` reports canonical grade 396/396; the final broad runner passed 119/119 files. |
| Code maintainer | Grilling lifecycle is explicit, invariant-checked, and the corpus is migrated honestly | **met** | SC-23 | `notes/research-FEAT-53-metrics-dashboard-goalcheck-validate-c3.md` confirms the behavior; the direct-lane T-25 repairs remain closed and the final broad runner passed. |

## Latest evidence

- **Engineering:** the build segments delivered KPI computation, trend persistence, loopback API, React/Astryx client, fleet work collection, charts, runner integration, and committed bundle. The terminal build repair passed 42 unit files, 77 integration files, and 20 component tests at the time (`runs/2026-09-17-13-eng/digest.md`).
- **Validation:** the frontend fix closed the five authorized UI defects (`runs/2026-09-17-16-validator/digest.md`). Backend c4/c5 closed Host validation, performance, project isolation, trend/worktree coverage, and every canonical grade record; c5 passed with 396/396 graded records (`runs/2026-09-17-18-validator/digest.md`, `runs/2026-09-17-19-validator/digest.md`).
- **REQ-15 follow-up:** the weekly merged-PR payload now carries its complete sourcing rule in available and unavailable states, and the client test proves the disclosure consumes payload content rather than a fallback (`runs/2026-09-17-21-validator/digest.md`). Code, security, and UI readers passed. The administrative QA block is superseded by the operator-observed broad result: `run-unit-tests.py --kind all` passed 119/119 files with exit 0; the component suite passed 23/23. The lone pooled SC-16 timing miss passed 3/3 in isolation and is classified as CPU-contention sensitivity, not a product defect; that resolution is recorded in `feature.json` judgements.
- **Documentation:** T-17's exact verifier, `git diff --check`, `serve.py --check`, and a loopback root smoke passed; only `METRICS.md` and its README pointer changed (`runs/2026-09-17-22-product/digest.md`).

## UAT hand-off

UAT is ready: **7 steps, about 10–15 minutes**.

Run `.harness/harness/features/FEAT-53-metrics-dashboard/notes/uat.md`, fill each `result:`, and return either `passed` or the observed failure text. Shipping remains blocked until the user records that result.

## Open question

1. **Q1 — blocking:** Do the seven UAT steps pass? If any step fails, return its `U-NN` and observation verbatim; if all pass, return `UAT passed`.

## Resolved escalations

| Escalation | Resolution |
|---|---|
| Frontend runtime, live payload, focus, geometry, and fixed-dark defects | Closed together at `ffd9fb02`; browser/UI review passed. |
| Host rebinding, KPI performance, project isolation, trend/worktree coverage, and grade failures | Closed across `3b78eb83`, `d1d9a44e`, and `ae5970d9`; c5 passed. |
| T-17 could not truthfully document the merged-PR sourcing rule | Production payload and client-consumption proof fixed at `93785232`; T-17 then passed at `db1b5ac5`. |
| c6 QA required a broad runner despite a targeted dispatch | Resolved by the final broad measurement: 119/119 files and 23/23 components passed. |
| Repeated fix-review stale pins | Main advanced the pin after c2, c4, c5, and c6; the interventions are recorded in `feature.json`. The process defect remains backlog B-1. |

## Spend and run budget

| Measure | Actual | Budget |
|---|---:|---:|
| Runs | 43 | 20 |
| Rework cycles | 35 | 40 |
| Wall clock | 927 minutes | — |
| Measured tokens | 2,995,756 | — |
| Judgements | 74 | — |

The run count exceeded its informational budget by 23. The long plan review, segmented multi-lane build, repeated full/fix validation, and stale-pin/tool-contract interventions account for the excess; the later runs each closed a concrete signed blocker, but the coordination overhead is material and should inform backlog B-1.

## Amendments made during build

| At | Decision | Reason | Overruled |
|---|---|---|---:|
| 2026-09-17T00:20:58.551210+00:00 | T-03.verify | Retired shell runner/check-kinds replaced by direct assertions. | no |
| 2026-09-17T00:20:58.551368+00:00 | T-06.files | Native directory-selected tests replaced retired registration. | no |
| 2026-09-17T00:20:58.551370+00:00 | T-06.intent | Native test migration preserved coverage without retired tooling. | no |
| 2026-09-17T00:20:58.551371+00:00 | T-06.verify | Native test migration preserved coverage without retired tooling. | no |
| 2026-09-17T00:20:58.551372+00:00 | T-23.files | Integration tests moved to native directory discovery. | no |
| 2026-09-17T00:20:58.551373+00:00 | T-23.verify | Native integration discovery preserved collector proof. | no |
| 2026-09-17T01:07:06.829852+00:00 | T-07.files | Migrated unit path plus signed fixture expectation. | no |
| 2026-09-17T01:07:06.830015+00:00 | T-07.verify | Runs migrated unit suite without retired registration. | no |
| 2026-09-17T01:07:06.830018+00:00 | T-08.files | KPI tests moved to native unit discovery. | no |
| 2026-09-17T01:07:06.830019+00:00 | T-08.verify | Runs migrated unit suite without retired registration. | no |
| 2026-09-17T01:07:06.830020+00:00 | T-09.files | KPI tests moved to native unit discovery. | no |
| 2026-09-17T01:07:06.830021+00:00 | T-09.verify | Runs migrated unit suite without retired registration. | no |
| 2026-09-17T01:07:40+00:00 | T-30-accepted | BUG-1724 host stamping supplies measured-or-null tokens; no cost field. | no |
| 2026-09-17T05:13:20.135420+00:00 | T-10.files | Runner conversion moved integration tests to native discovery. | no |
| 2026-09-17T05:13:20.135771+00:00 | T-10.verify | Layout plus direct script preserves scoped proof. | no |
| 2026-09-17T05:13:20.135773+00:00 | T-10.intent | Native runner replaced the shell array. | no |
| 2026-09-17T05:13:20.135774+00:00 | T-26.files | Work-dashboard integration harness moved paths. | no |
| 2026-09-17T05:13:20.135775+00:00 | T-26.verify | Migrated command preserves signed worktree case. | no |
| 2026-09-17T05:54:45.707924+00:00 | T-11.files | Runner migration relocated tests and required fixture cases. | no |
| 2026-09-17T05:54:45.708069+00:00 | T-11.verify | Integration test moved to native path. | no |
| 2026-09-17T05:54:45.708071+00:00 | T-13.files | DESIGN-required Neutral theme dependency was added. | no |
| 2026-09-17T05:54:45.708073+00:00 | T-31.files | Integration test moved to native path. | no |
| 2026-09-17T05:54:45.708074+00:00 | T-31.verify | Migrated command preserves both signed cases. | no |
| 2026-09-17T06:35:24.453078+00:00 | T-12.files | Native runner cutover removed shell registry editing. | no |
| 2026-09-17T06:35:24.453246+00:00 | T-12.verify | Layout plus scoped integration replaced retired commands. | no |
| 2026-09-17T06:35:24.453248+00:00 | T-14.files | Focused render tests bind observable gap/link behavior. | no |
| 2026-09-17T06:35:24.453250+00:00 | T-14.verify | Forbidden-route scan excludes tests that name retired routes. | no |
| 2026-09-17T06:35:24.453251+00:00 | T-19.files | Trend/KPI tests moved to native paths. | no |
| 2026-09-17T06:35:24.453254+00:00 | T-19.verify | Migrated suites plus AST call-site proof preserve scope. | no |
| 2026-09-17T07:05:02.096447+00:00 | T-06.verify | Removed unrelated frontend layout preflight from scoped KPI proof. | no |
| 2026-09-17T07:05:02.096599+00:00 | T-12.verify | Removed unrelated frontend layout preflight from scoped API proof. | no |
| 2026-09-17T07:21:02.123820+00:00 | T-27.files | Native runner relocated the integration test. | no |
| 2026-09-17T07:21:02.123983+00:00 | T-27.verify | Scoped proof invokes the native integration path. | no |
| 2026-09-17T07:42:35.542074+00:00 | T-21.verify | Vitest 5 JSON file carrier replaced stale stdout parsing. | no |
| 2026-09-17T08:35:08.449836+00:00 | T-22.files | Native discovery required classifier and focused regression files. | no |
| 2026-09-17T08:35:08.449999+00:00 | T-22.verify | Native discovery plus Vitest file carrier and CI exit retained. | no |

**Overrule rate: 0/36.**

## Proposed backlog

| ID | Nature | Residual |
|---|---|---|
| B-1 | chore | Make fix-team review pinning a deterministic post-fix/pre-reader hand-off so Main never has to repair stale `review_sha` mid-run. |
| B-2 | chore | Isolate SC-16's wall-clock KPI ceiling from parallel worker CPU contention or give that test a serial runner lane. |
| B-3 | chore | Bind the configured frontend `unit` kind to an actual client unit command, or explicitly define the unit/component split so future QA does not report the old F-QA-03 ambiguity. |
| B-4 | chore | Stop successful mutation-proof tests from printing unqualified `FAIL` lines that mislead log-only triage while the file exits zero. |
| B-5 | chore | Reduce `feature.json` below the 300-line state-file budget; current truth has grown to 653 non-run-ledger lines. |

## Source disclosure

No report round was spawned. This briefing was assembled from the signed BRIEF, `feature.json`, the goal-check, review artifacts, and every available run digest on disk.

Digest paths read:

- `runs/2026-09-01-01-product/digest.md`, `runs/2026-09-01-02-product/digest.md`, `runs/2026-09-01-01-eng/digest.md`, `runs/2026-09-01-01-validator/digest.md`, `runs/2026-09-01-03-product/digest.md`, `runs/2026-09-01-04-product/digest.md`, `runs/2026-09-01-05-product/digest.md`, `runs/2026-09-01-05-validator/digest.md`, `runs/2026-09-01-06-validator/digest.md`, `runs/2026-09-01-07-product/digest.md`, `runs/2026-09-01-08-validator/digest.md`, `runs/2026-09-01-09-product/digest.md`.
- `runs/2026-09-02-1-product/digest.md`, `runs/2026-09-02-2-product/digest.md`, `runs/2026-09-02-01-validator/digest.md`, `runs/2026-09-02-02-validator/digest.md`, `runs/2026-09-02-03-product/digest.md`, `runs/2026-09-02-04-product/digest.md`, `runs/2026-09-02-05-validator/digest.md`, `runs/2026-09-02-06-product/digest.md`, `runs/2026-09-02-07-product/digest.md`, `runs/2026-09-02-08-validator/digest.md`, `runs/2026-09-02-09-product/digest.md`.
- `runs/2026-09-16-01-product/digest.md`, `runs/2026-09-16-02-eng/digest.md`.
- `runs/2026-09-17-03-eng/digest.md` through `runs/2026-09-17-13-eng/digest.md`.
- `runs/2026-09-17-14-validator/digest.md` through `runs/2026-09-17-19-validator/digest.md`, `runs/2026-09-17-20-product/digest.md`, `runs/2026-09-17-21-validator/digest.md`, and `runs/2026-09-17-22-product/digest.md`.

Ledger run `2026-09-17-14-validate` has no digest file; no claim was drawn from it. Superseded/duplicate on-disk digests were read rather than silently omitted.
