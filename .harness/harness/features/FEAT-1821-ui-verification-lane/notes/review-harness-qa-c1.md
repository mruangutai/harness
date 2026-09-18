```yaml
VERDICT: FAIL
DIGEST:
  headline: "All four original T-03 verification-lane findings remain open; the configured matrix is unsatisfied and UI is misconfigured."
  matrix_ok: false
  suite: fail
  failures: 4
  kinds:
    - { kind: unit, state: missing, cmd: "no changed unit test discharges this lane", named_tests: 0 }
    - { kind: component, state: missing, cmd: "no changed component test discharges this lane", named_tests: 0 }
    - { kind: ui, state: misconfigured, cmd: "null", named_tests: 0 }
  sc_evidence: []
  fail_first:
    - { sc: SC-02, evidence: "GAP — receipt-harness-frontend-dev-fix-c1.md:11-14 contains only non-behavioral source-string probes." }
    - { sc: SC-04, evidence: "GAP — receipt-harness-frontend-dev-fix-c1.md:11-14 contains only non-behavioral source-string probes." }
    - { sc: SC-05, evidence: "GAP — no pre-fix failing results-schema or applicability test is recorded." }
    - { sc: SC-06, evidence: "GAP — no pre-fix failing WebP behavioral test is recorded." }
  findings:
    - { kind: substance, scope: task, severity: high, reader: qa, summary: "Objective predicates are materially narrower than DESIGN.", why: "The live header RED reaches only the first predicate; the remaining geometry, placement, state, route, and accessibility clauses are not asserted." }
    - { kind: substance, scope: task, severity: high, reader: qa, summary: "C3 keyboard validation aborts before the signed transition sequence.", why: "Zero KPI links at feat-53.e2e.spec.ts:84 prevent downstream restoration, retained-focus, Back, and disclosure transitions from being exercised." }
    - { kind: substance, scope: task, severity: high, reader: qa, summary: "Copied fixtures do not drive the 22 signed inspection states.", why: "No client consumer selects fixture_state or fixture-states; qa-inspection captured one setup and aborted before the other 21." }
    - { kind: substance, scope: task, severity: high, reader: qa, summary: "Reporter, parser, and gate contracts cannot accept a complete dynamic-spec run.", why: "Producer fields and parser fields disagree, literal-title extraction misses dynamic titles, and no negative run proves unlisted-test reporter refusal." }
  must_fix:
    - "Repair the producer/parser field and title contracts."
    - "Make every signed fixture state selectable by the served data path."
    - "Make each objective and C3 predicate reach and assert its complete DESIGN contract."
    - "Record a pre-fix red behavioral run for each automated success criterion."
  coverage_gaps:
    - "No changed unit test discharges the frontend interaction-flow lane."
    - "No changed component test discharges the frontend interaction-flow lane."
    - "The UI kind command is unresolved; the task-local command cannot satisfy the configured UI matrix kind."
    - "Twenty-one of twenty-two signed inspection setups were not captured."
    - "Behavioral fail-first evidence is absent for SC-02, SC-04, SC-05, and SC-06."
  open_questions: []
  files_touched: ["/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c1.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c1.md
```

# QA gate — T-03 fix c1

**BLUF: FAIL.** The list command is live (12 exact titles, 23 applicable executions) and source-only plus WebP paths work, but all four original findings remain open: objective and keyboard runs abort on the FEAT-53 product, fixture/inspection state is not realized, and the producer/parser/gate contract cannot accept a complete dynamic-spec run. Fail-first evidence is incomplete.

## Required command and focused evidence

- PASS — exact T-03 command: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=plan-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list` listed **23 tests in one file**, matching the parser's 12 checks / 23 applicable project-check executions.
- FAIL (browser product, predicate reached) — `qa-header` directly reached `feat-53.e2e.spec.ts:174`; committed FEAT-53 has no `header` on overview. This is an honest RED, not proof that T-03 is complete.
- FAIL (browser product that prevents full sequence) — `qa-keyboard` directly reached `feat-53.e2e.spec.ts:84` and found zero KPI links, so all downstream C3 restoration/retained-focus/Back/disclosure transitions were not exercised.
- PASS — `qa-source` ran `SRC-TOKENS` against `client/src` and captured a 244342-byte `RIFF....WEBP` CDP screenshot. It is only one of 23 executions; its results correctly record the remaining ids missing.
- PASS (negative) — malformed DESIGN `/dev/null` is refused by `ui_contract.py`; no-match runner created `qa-no-match/results.json` with empty observations, all ids missing, and `summary.status: failed`; its contract gate returned FAIL.
- FAIL — `qa-inspection` captured only `VIS-DENSITY/overview-default`, then aborted before setup 2/11 at desktop-1440 (`body` hidden). It never reaches the other ten desktop-1440 or any eleven desktop-1920 inspection setups.

## Original must-fix disposition

1. **OPEN — kind: verification-lane omission (with live browser-product RED).** Objective dispatch is reachable, but predicates are materially narrower than DESIGN: header checks no right/footer edge or left composition; identity/status only assert marker counts rather than computed placement/exclusion; hatch/table/a11y omit the required state and route coverage. `qa-header` proves only the first predicate reaches production.
2. **OPEN — kind: verification-lane omission (with live browser-product RED).** `keyboard()` encodes part of C3, but its zero-KPI abort at line 84 prevents the complete signed sequence. The path therefore does not exercise the downstream keyboard transitions required by DESIGN.
3. **OPEN — kind: verification-lane omission.** `fixture.ts:20-26` creates copied feature directories and sidecars, but client source has no consumer of `fixture_state`/`fixture-states`; it cannot select the signed unavailable, source-error, request-error, overflow, or long-content states. The 22 manifest entries exist (11/project), but `qa-inspection` establishes only one capture and aborts.
4. **OPEN — kind: verification-lane omission.** Source traversal and a WebP are real, and malformed-contract/missing-accounting negatives fail closed. However producer/consumer schemas disagree: reporter emits `screenshot_evidence` and per-project `observed_check_ids` (`ui-reporter.ts:28-44`), while `ui_contract.py:247,306-320` reads a flat observed list and `screenshots`. In addition `spec_titles()` can only extract literal titles, while the spec's titles are dynamically supplied at `feat-53.e2e.spec.ts:271-279`; the gate reports all 12 required specs absent for any changed client package. No direct negative run demonstrates unlisted-test reporter error handling.

## Matrix and fail-first

T-03 is `frontend` and contains interaction flow, so the configured floor is unit + component + ui (`.harness/harness.json:180-190`). The signed seven-file diff changes only the e2e spec and runtime support: no changed unit or component test discharges this lane. `test_kinds.ui` is still `cmd: null`, `status: unresolved` (`.harness/harness.json:333-338`), so the matrix's UI kind is misconfigured even though the task-local package command runs.

- Credible fail-first only for runner existence: original digest `runs/build-eng-t03-eng/digest.md:39` records the exact list command exited 1 before `test:ui` existed.
- Receipt claims red checks for objective/keyboard/source/reporter at `receipt-harness-frontend-dev-fix-c1.md:11-14`, but source-string probes are not credible fail-first evidence for SC-02/04/05/06 behavior; no pre-fix failing results-schema/WebP/applicability test is recorded.

## Required repair evidence

Repair the producer/parser field and title contracts; make every signed fixture state selectable by the served data path; and make each objective/C3 predicate reach and assert its complete DESIGN contract. Then record a pre-fix red behavioral run per automated SC and rerun all 23 executions with 22 inspection captures.
