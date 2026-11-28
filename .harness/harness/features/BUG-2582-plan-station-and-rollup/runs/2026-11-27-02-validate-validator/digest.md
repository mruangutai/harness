# Validate c1: BUG-2582-plan-station-and-rollup at c1171867

**ESCALATE. Not ship-ready.** I found three gating defects.
- The T-02 carve-out grants relief to an incomplete or relabelled reader roster. Both reviewers, working independently, landed on the same fix.
- The pin turns four CI files red that are green at base.
- The new test's `main` fails the DEC-209 grade.

One of the CI fixes needs a plan amendment, because no task's `files:` covers it. That is why the verdict is ESCALATE and not FAIL.

The other part of the work is sound. pm's goal-check finds the three perspectives discharged on the happy path. SC-01 to SC-04 and SC-07 to SC-11 are met, and fail-first is reproduced independently.

- Reviewed: `e6960865..c1171867`. QA's `git diff --stat b8a639c7 c1171867` shows only `feature.json` and `plan.yaml` changed, so the two commits are code-identical (confirmed).
- `gates.review` is `advisory_unless_high`, so `severity_max: high` gates.

## Must-fix, in fix order

1. **MF-1 · substance · high · T-02 (`validate-digest.py` `_carveout_plan`/`_plan_reader_carveout`, plus the unit test).** Bind the carve-out to the trusted plan-team roster.
   - **Sources.** This merges code-reviewer #1 and security #1.
   - **(a) Absent reader slot.** Today only duplicate reader steps are rejected; a missing one is not. Code-reviewer *executed* this through full `validate()` at both base and pin: the real panel, `design` omitted, `scope` at FAIL with resolved rows. Base refuses; the pin accepts PASS. That breaks SC-05's literal conjunct "exactly one member entry per reader step". A `status: skipped` entry still counts as present.
   - **(b) Lead-chosen slot↔persona pairing.** The step/persona pairing comes from the lead's digest. Security's account is reasoning-only, not a live run: a lead could re-attribute a persona-labelled open row to another member. Fix it by requiring each reader slot's persona to equal the one declared in `teams/plan.yaml`.
   - **(c) Non-plan dispatch.** This is security #2, also reasoning-only. The relief must never apply when the live hook's dispatch mission is not `plan`, for example a product `distill` run on a feature whose mission is still `plan`.
   - **Acceptance.** Each of (a), (b) and (c) gets one discriminating case. Each case must be red at c1171867 and green after the fix, and the red for (b) and (c) must be shown by execution. Every existing (R) denial must still refuse exactly what it refused before (O-02).
2. **MF-2 · substance · high · T-02.** Narrow the two `except Exception: # noqa: BLE001` in `_carveout_plan` (`validate-digest.py:2087,2094`) to the real error classes.
   - FEAT-63 sets the ceiling for these catches at 0.
   - Two files are red at the pin and green at base: `tests/unit/test-broad-catch-census.py` and `tests/integration/test-checker-structure-locks.py`.
   - Trigger: every CI run.
   - Acceptance: both files exit 0. `deny-no-plan` and `deny-unloadable-plan` still refuse with the not-applied reason.
3. **MF-3 · substance · high · T-02 plus a file in no task (ESCALATED, OQ-1).** `tests/integration/test-check-plan-routes.py` has 8 `canonical_reader_*` failures.
   - Cause: the new `load_feature_json` and `load_plan` call sites in `_carveout_plan` are absent from `tests/integration/canonical-reader-classification.json`, and the test prints "PLAN AMENDMENT REQUIRED".
   - That inventory file is in no task's `files:`.
   - Order: do it **after** MF-1 and MF-2, because the inventory rows key on the final call sites.
4. **MF-4 · form · high, CI-blocking · T-03.** The DEC-123 ruling in `DECISIONS-INDEX.md` is 38 words; the cap is 30, and `tests/integration/test-gen-decisions-index.py` is red.
   - Fix: shorten the ruling in `DECISIONS.md` and regenerate the index.
   - The shortened ruling must still name the carve-out (SC-08 bullet 4).
   - T-03's verify never checked the cap.
5. **MF-5 · substance · high · T-02 test.** `tests/unit/test-validate-digest-plan-rollup.py:282` `main` grades 1 against the test bar of 3 (ABC 67.1).
   - Re-grade it **after** MF-1 adds its cases.

## Assessed: advisory, or dismissed from must-fix (operator triage rule, 2026-11-27)

- **Code-reviewer #2 (raiser: high): a numeric `summary` on a resolved row satisfies the carve-out. Dismissed from must-fix; recorded as advisory.**
  - The lead cannot write `plan.yaml`: security executed `check-domain` and got exit 2.
  - A row with a numeric `summary` is a shape that the repo's own `shape_faults` and `set-panel` accept. It can come only from trusted pm or a hand edit.
  - The row must still be `resolved`, and its PF id is identical under `str()`.
  - So no relief over an *unresolved* finding is possible. The gate's definition of "malformed" is a consistency nit.
- **Code-reviewer #4 (med): converting a stub with a bare `approval:` (null) seeds no mapping. Advisory.**
  - The trigger is an operator hand-writing a contrived stub.
  - Base trapped that stub at exit 5. At the pin it converts, and INV-3 flags the missing approval visibly.
  - The fix is cheap and inside T-01's files (`isinstance(approval, dict)`). It is optional within the fix round and not a reason for one.
- **Code-reviewer #5 (low): an indented comment right after the marker is dropped. Advisory.**
- **Code-reviewer #6 and QA #5 (low; deduplicated): non-candidate denials carry no "carve-out not applied" reason.**
  - This covers team≠plan, a non-reader FAIL, and ESCALATE or BLOCKED.
  - The outcome is identical to base. SC-06's closing sentence, read literally, is unmet for those bullets (OQ-2).
- **QA #4 (low): SC-07's other-lead cases do not discriminate the product-lead gate. Advisory.**
  - Mutant M6 stays 27/27, because the fixtures use step `build`.
  - The code is correct today. MF-1 reopens this file, so adding an eng-lead `team: plan` reader-step case costs one fixture.
- **QA mutant M1 (exact versus folded disposition check) is equivalent.** `shape_faults` enforces the enum upstream. This is informational.

## Reconciliation

- pm graded SC-05 and SC-06 `met`; code-reviewer and security say they are mismatched.
  - I side with code-reviewer for SC-05, because it executed a counterexample against SC-05's literal conjunct. pm's evidence is the tests, which never omit a slot.
  - SC-06 is graded `partial`: its listed cases all pass, but the closing sentence is unmet for non-candidate denials, and the roster-spoof leg is unproven.
- pm's SC-09 `met` stands. The four named suites are green at the pin, confirmed by both QA and pm.
  - QA's four red files are regressions *outside* SC-09's list. They gate anyway, as regressions; no SC carries them. Every task's literal verify missed them (P-10, G-14).
- Security's two findings come from inspection, not live bypass runs (P-09). I keep their severity because both come from a lead-controlled trigger at the relaxed gate's trust boundary. MF-1's acceptance turns them into measurements.

## Assurance

- **QA.** Both required runners ran from the managed pin (`suite: fail`, unit 71/71 files, integration 95/95, 4 red). The receipts are in `qa/manifest-{unit,integration}.json` and are unedited.
- **Fail-first.** Natural red was reproduced against base blobs for SC-01, 03, 05, 06, 10 and 11. SC-02 has mutation-tier evidence (M5). SC-07 has none (M6 stays green). SC-09 is non-regression by construction.
- **`harness_yaml.py`** is byte-identical to base (exit 0).
- **The four build deviations** are correct (code-reviewer).
- **UI** scoped itself out on a measured census of 31 changed paths, none of them UI.

## Pointers

- QA: `notes/review-harness-qa-c1.md`
- Code review: `notes/review-harness-code-reviewer-c1.md`
- Security: `notes/review-harness-security-reviewer-c1.md`
- UI: `notes/review-harness-ui-reviewer-c1.md`
- Goal-check: `notes/research-BUG-2582-plan-station-and-rollup-goalcheck-validate-c1.md`

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'BUG-2582 is not ship-ready at c1171867. The T-02 carve-out grants relief
    to an incomplete or relabelled reader roster, and the pin turns 4 CI files red
    that are green at base. One of those fixes, the canonical-reader inventory, needs
    a plan amendment, which is why this is ESCALATE. pm found the happy path met:
    SC-01..04 and SC-07..11.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: 'matrix_ok true and fail-first reproduced, but both runners are red:
      4 files fail at the pin that pass at base (broad catches, reader inventory,
      DEC-123 index word cap)'
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-02-validate-validator/qa/manifest-unit.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-02-validate-validator/qa/manifest-integration.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'The plan roll-up accepts a missing reader slot (executed: base refuses,
      pin accepts) and the new test main grades 1. SC-04 and SC-08 are met by inspection.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: 'From inspection only: a lead-controlled roster can detach an open row
      from its reader, and a non-plan product dispatch can claim plan-team relief'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Scoped out: none of the 31 changed paths is a UI surface'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All three perspectives pass and the DEC-123/254/228 amends landed as
      signed. The lead regrades SC-05 and SC-06 on executed counter-evidence.
    files_touched: []
  must_fix:
  - 'MF-1 (T-02, substance, high): bind the carve-out to the trusted plan-team roster.
    (a) Require exactly one member entry per reader slot; a skipped entry counts as
    present. (b) Bind each slot''s persona to the one teams/plan.yaml declares, rather
    than the lead''s pairing. (c) Refuse relief when the live dispatch mission is
    not plan. Each leg gets a case that is red at c1171867 and green after the fix,
    and every existing (R) denial still refuses what it did. Reported by code-reviewer
    and security-reviewer.'
  - 'MF-2 (T-02, substance, high): narrow the two `except Exception` in `validate-digest.py`
    `_carveout_plan` (:2087, :2094) to real error classes. test-broad-catch-census.py
    and test-checker-structure-locks.py must exit 0, and deny-no-plan and deny-unloadable-plan
    must keep their reason. Reported by qa.'
  - 'MF-3 (T-02 plus a file outside every task, ESCALATED as OQ-1): add the `_carveout_plan`
    load_feature_json and load_plan call sites to tests/integration/canonical-reader-classification.json
    so that test-check-plan-routes.py passes. Do this after MF-1 and MF-2. Reported
    by qa.'
  - 'MF-4 (T-03, form, high, CI-blocking): shorten the DEC-123 ruling to 30 words
    or fewer, still naming the carve-out, and regenerate DECISIONS-INDEX.md so that
    test-gen-decisions-index.py passes. Reported by qa.'
  - 'MF-5 (T-02 test, substance, high): split tests/unit/test-validate-digest-plan-rollup.py
    main (grade 1, bar 3) after MF-1 adds its cases. Reported by code-reviewer.'
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-02-validate-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-02-validate-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-02-validate-validator/qa/manifest-integration.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/observations/harness-qa.md
  branch: none
  open_questions:
  - id: OQ-1
    question: 'MF-3''s only known remedy edits tests/integration/canonical-reader-classification.json,
      which is in no task''s files:, and the test itself prints ''PLAN AMENDMENT REQUIRED''.
      Should T-02''s files: be amended to include it, which changes the signed task
      hash, or should a new task carry it? pm owns the amendment and the operator
      signs it. MF-1, MF-2, MF-4 and MF-5 are fixable inside existing tasks while
      this is decided.'
    blocking: true
  - id: OQ-2
    question: 'Read literally, SC-06''s closing sentence (''The refusal names why
      the carve-out did not apply'') is unmet for the non-candidate denials: team
      not plan, a non-reader FAIL, and ESCALATE or BLOCKED. The outcome is identical
      to base, and the signed T-02 text asserts the reason only for the (R) cases.
      Should SC-06 be read as covering candidates only, or should the letter be applied
      now? The lead recommends applying the letter fix for product-lead digests in
      the T-02 round MF-1 already opens, since it is cheap and inside T-02''s files.'
    blocking: false
  - id: OQ-3
    question: MF-1(c) adds a dispatch-mission conjunct that SC-05 does not list. It
      is a stricter, fail-closed condition, but it narrows SC-05's sufficiency clause
      in hook context. Confirm this is acceptable without re-wording SC-05. The lead
      recommends yes; offline validation can keep feature.json's mission as the sole
      condition.
    blocking: false
  escalations:
  - id: ESC-1
    raised_by: harness-qa
    question: 'Add the _carveout_plan reader call sites to tests/integration/canonical-reader-classification.json,
      a file outside every task''s files: (MF-3)'
    domain: plan amendment
    routed_to: harness-orchestrator
    resolution: pending
    decided_by: none
    recorded_as: runs/2026-11-27-02-validate-validator/digest.md#must-fix-in-fix-order
  adequacy_notes:
  - Each of the four red CI files is green at base and was missed by every task's
    literal verify. SC-09's four named suites are green, so SC-09 is met, but it did
    not cover these regressions.
  - Security's two findings come from source inspection, not live runs. MF-1's acceptance
    requires executed red at c1171867 for legs (b) and (c).
  - 'SC-07''s other-lead cases do not discriminate the product-lead gate (mutant M6
    stays 27/27). The code is correct today. Adding an eng-lead team: plan reader-step
    case while MF-1 reopens the file costs one fixture.'
  - 'Code-reviewer #2 (a numeric summary on a resolved row, rated high by the raiser)
    is dismissed from must_fix. A lead cannot write plan.yaml (check-domain exit 2,
    executed), the row must still be resolved, and the PF id is identical, so no relief
    over an unresolved finding is possible.'
  - 'Code-reviewer #4 (a bare `approval:` null is not seeded, med) is advisory: it
    needs a contrived operator stub, base trapped that stub, and INV-3 flags it visibly.
    The one-line fix is optional inside T-01''s files.'
  - The four disclosed build deviations are correct (code-reviewer). harness_yaml.py
    is byte-identical to base. b8a639c7 and c1171867 are code-identical (QA, measured).
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: test-plan-merge-station-convert.py; QA natural red code 5 at base union.py
  - id: SC-02
    verdict: met
    method: automated
    evidence: the same file's guard cases; mutant M5 turns them red; harness_yaml.py
      diff exits 0
  - id: SC-03
    verdict: met
    method: automated
    evidence: bug2582-inv34-remedy-line is red at CHECK_STATE_REV=e6960865
  - id: SC-04
    verdict: met
    method: inspection
    evidence: 'code-reviewer: approval.py byte-identical; check_state/plan.py hunks
      are INV-34 only; _inv3 reports pending; _eligibility grades the stamped draft'
  - id: SC-05
    verdict: not_met
    method: automated
    evidence: 'code-reviewer executed full validate(): with design absent and scope
      FAIL resolved, base refuses and the pin accepts PASS, violating ''exactly one
      member entry per reader step'' (MF-1)'
  - id: SC-06
    verdict: partial
    method: automated
    evidence: a dedicated case for each bullet (QA); the closing reason sentence is
      unmet for non-candidate denials (OQ-2); the roster-spoof leg is unproven (MF-1b)
  - id: SC-07
    verdict: met
    method: automated
    evidence: bug2582-other-lead-eng and bug2582-other-lead-validator pass; lead-gate
      discrimination is unshown (M6)
  - id: SC-08
    verdict: met
    method: inspection
    evidence: 'code-reviewer and pm: all five bullets hold at c1171867 and the index
      regenerates byte-equal; the 30-word cap breach is MF-4, outside SC-08''s text'
  - id: SC-09
    verdict: met
    method: automated
    evidence: the four named suites exit 0 at the pin with HARNESS_AGENT_TYPE unset
      (QA, pm)
  - id: SC-10
    verdict: met
    method: automated
    evidence: test-lead-start-return.py BUG-2582 cases; stub-convert-after-start is
      red with apply exit=5 at base
  - id: SC-11
    verdict: met
    method: automated
    evidence: apply prompt order is [891,1024,1657] at the pin against [891,-1,1000]
      at base; bug2582-producer-witness is red at base
  - id: DEC-123
    verdict: met
    method: inspection
    evidence: 'pm: DECISIONS.md:2480,2491-2501 at c1171867'
  - id: DEC-254
    verdict: met
    method: inspection
    evidence: 'pm: DECISIONS.md:8464-8468'
  - id: DEC-228
    verdict: met
    method: inspection
    evidence: 'pm: DECISIONS.md:7646-7649'
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'SC-07: the other-lead fixtures cannot reach the product-lead gate (M6 stays green)'
  - 'SC-06: no case asserts reason text for non-candidate denials'
  - 'SC-05: no case omits a reader slot (the defect behind MF-1a)'
  - every task's literal verify missed 4 CI regressions outside SC-09's named suites
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer, harness-security-reviewer
    summary: 'T-02: the carve-out accepts an absent reader slot and a lead-chosen
      slot/persona pairing (MF-1a/b)'
    why: 'Lead-controlled roster at the relaxed gate''s trust boundary. Executed:
      base refuses, pin accepts PASS with design omitted'
  - kind: substance
    scope: none
    severity: high
    reader: harness-security-reviewer
    summary: 'T-02: plan-team relief is not bound to the live dispatch mission (MF-1c)'
    why: 'A product distill run on a mission: plan feature can present team: plan;
      the hook knows the dispatch mission but the carve-out ignores it. Inspection-only'
  - kind: substance
    scope: none
    severity: high
    reader: harness-qa
    summary: 'T-02: two broad catches in _carveout_plan break the FEAT-63 ceiling
      of 0 (MF-2)'
    why: test-broad-catch-census.py and test-checker-structure-locks.py are red at
      the pin and green at base on every CI run
  - kind: substance
    scope: none
    severity: high
    reader: harness-qa
    summary: 'T-02: the new reader call sites are missing from the canonical-reader
      inventory (MF-3, escalated)'
    why: test-check-plan-routes.py has 8 failures at the pin and is green at base;
      the inventory file is outside every task's files
  - kind: form
    scope: none
    severity: high
    reader: harness-qa
    summary: 'T-03: the DEC-123 index ruling is 38 words against a 30-word cap (MF-4)'
    why: test-gen-decisions-index.py is red at the pin and green at base
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'T-02: the new roll-up test main grades 1 against bar 3 (MF-5)'
    why: The DEC-209 mechanical audit refuses a code-review pass
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'T-02: a numeric summary on a resolved row satisfies the carve-out. Assessed
      and dismissed from must_fix'
    why: Only pm or a hand edit can write such a row (lead write refused, exit 2);
      the row is still resolved and its PF id identical, so no unresolved relief
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01: conversion leaves a null approval unseeded. Advisory'
    why: Contrived operator stub; base trapped it at exit 5; INV-3 flags it visibly
  - kind: substance
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'T-01: an indented comment right after the marker is dropped on conversion.
      Advisory'
    why: Cosmetic loss on a record base refused to convert
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer, harness-qa
    summary: 'T-02: non-candidate denials carry no carve-out reason (OQ-2)'
    why: Outcome identical to base; SC-06's closing sentence is unmet when read literally
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-02: SC-07 fixtures do not discriminate the product-lead gate. Advisory'
    why: Mutant M6 stays green; the code is correct today
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-02-validate-validator/digest.md
```
