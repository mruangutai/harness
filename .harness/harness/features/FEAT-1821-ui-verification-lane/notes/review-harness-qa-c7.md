# QA c7 final matrix — review pin b8f96ab8e9c8168ed8389ccf4732a958e84828fd

**FAIL.** The configured unit and component kinds are green and UI discovery is exactly 23 tests in 6 files, but the real evidence gate produces 11 structural full-contract refusals for the pinned c7 client diff. These are separate from the intended FEAT-53 RED and prevent clearance.

## Phase 1 coverage floor

BRIEF/plan-only derivation: logic plus frontend work with interaction flow requires `unit`, `component`, and `ui`; automated SCs require fail-first proof for SC-01..SC-06 and SC-10..SC-11. The c7 package/reporter change also requires focused contract/reporter enforcement proof.

## Commands at the pin

- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` — exit 0; includes `test-ui-verification-contract.py` (24/24), `test-suite-layout.py`, and `test-ui-reviewer-policy.py`.
- `npm --prefix .claude/skills/harness/bin/dashboard/client run test` — exit 0; 5 files, 27/27 tests.
- `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=qa-c7-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list` — exit 0; exactly 23 tests in 6 files.
- `node --experimental-strip-types --test .claude/skills/harness/bin/dashboard/client/ui-reporter.probe.spec.ts` — exit 0; 7/7 named probes. The parser-error traceback is the deliberate no-DESIGN fixture.
- Exact gate: `python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json --feature FEAT-53-metrics-dashboard --run-id FEAT-1821-initial-red --served-bundle-commit 153909c71e8ca3f02be6fcbcfe48781718953b1d --repo-root . --client-package .claude/skills/harness/bin/dashboard/client --changed .claude/skills/harness/bin/dashboard/client/package.json --changed .claude/skills/harness/bin/dashboard/client/package-lock.json --changed .claude/skills/harness/bin/dashboard/client/ui-reporter.ts --changed .claude/skills/harness/bin/dashboard/client/ui-reporter.probe.spec.ts` — exit 1. It correctly reports 18 honest predicate failures and all 4 inspection setup failures, but also reports 11 structural `client package changed and no spec carries the title ...` reasons.

The structural false refusals arise because `ui_contract.py:252-259` scans only literal `test("title")` calls; 11 real specs register dynamically as `test(check.spec_title, ...)` after `checkFor(...)` (for example `dashboard/client/e2e/tables-a11y.e2e.spec.ts:37-41`). This contradicts D-04/SC-11's complete-contract gate on the actual c7 client diff. Keyboard is the one literal-title exception.

## Evidence classification

The committed bundle uses the required provenance subject `served_bundle_commit=153909c71e8ca3f02be6fcbcfe48781718953b1d`, not the review SHA. Direct census: 18 `failed`, 4 inspection records with non-empty setup errors, 1 `passed`, and 41 committed WebPs. The hardened gate rejects all four errored inspection rows as `inspection setup failed, so its screenshots are not evidence`; predicate and setup reasons account for 22 of the gate reasons. The remaining 11 are the structural scanner defect above; there are no other observed structural categories.

## Fail-first audit

- SC-01: present — `notes/receipt-harness-frontend-dev-T-03-c0.md:5` records the exact UI list command red before `test:ui` existed.
- SC-05/SC-06: c7 receipt has red mutations for missing predicates/inspection manifest and inspection setup errors (`notes/receipt-main-direct-T-01-c7.md:9-15`), but does not document a pre-fix red for every SC-specific results/accounting mutant.
- SC-10/SC-11: no pinned red receipt covers missing runner or the actual dynamic-title complete-client check; the c7 red receipt names only the two gate-evidence cases above.
- SC-02/SC-03/SC-04: no complete pinned behavioral fail-first receipt was found. The T-03 pre-lane missing-script red is runner evidence, not a red proof of screenshot/record cardinality, committed initial RED behavior, or pixel-baseline opt-in.

## Findings

1. **substance / high / T-01 main-session-direct:** full-client SC-11 enforcement scans only static test titles. A client package change with the existing dynamic manifest-driven specs is structurally refused despite all 23 declared executions being listable.
2. **form / medium / T-01 main-session-direct:** fail-first remains incomplete for automated SC-02..SC-06 and SC-10..SC-11; current green commands and broad receipts do not supply each required pre-fix behavioral failure.

`matrix_ok: false`. FEAT-53's honest product RED is not a FEAT-1821 defect; the 11 scanner refusals and fail-first gaps are.
