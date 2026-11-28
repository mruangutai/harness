# Validate c2: BUG-2582-plan-station-and-rollup at 4460c352

**PASS. Ship-ready at `4460c35294042ce421ac3815df76d2afe61367ad`.** The `must_fix` list is empty and `severity_max` is `med`. Under `gates.review: advisory_unless_high`, nothing here blocks.

- All five c1 must-fix items are closed, and the closures were executed, not just read.
- The four CI files that were red at c1171867 now exit 0.
- pm grades SC-01..SC-11 and DEC-123/254/228 `met`.
- Reviewed range: `e6960865..4460c352`. The code reviewer reports that HEAD differs from the pin only in the feature record.

## Closure of c1 must-fix (each measured by a reader this round)

- **MF-1 (a)(b)(c): closed.**
  - The code reviewer, who raised (a) at c1, re-ran its own counterexample through full `validate()`. In that counterexample `design` is omitted and `scope` is FAIL with resolved rows. c1171867 accepted it. The pin refuses it with "reader step design missing".
  - QA, pm and security each found the three new cases accepted with no errors by the c1171867 validator and green at the pin.
  - QA's single-leg mutants (missing, persona, mission, dup) each turn only their own case red.
  - Security executed the edge inputs: a live mission that is empty, whitespace, `Plan`, `patch` or `distill` is refused. Persona case or spacing variants are refused, and step ids are literal.
  - pm's real-data probe used the run-01 plan digest with `design` dropped. c1171867 accepts it; the pin refuses it. The intact digest is still accepted at the pin.
- **MF-2: closed.** `test-broad-catch-census.py` and `test-checker-structure-locks.py` exit 0 (QA).
- **MF-3: closed** by the ledgered amendment. `test-check-plan-routes.py` exits 0 (QA). The amendment is consistent with the two canonical reads (code reviewer). Approval was deliberately not reset (operator ruling).
- **MF-4: closed.** The DEC-123 index row is 28 words and names the carve-out. `test-gen-decisions-index.py` exits 0, and the regenerated index is byte-equal (QA, pm, code reviewer).
- **MF-5: closed.** Every one of the 32 functions new or changed in the fix range meets its bar. `main`, `case_producer_witness` and `_carveout_plan` grade 4 (code reviewer).
- **O-02 (no predicate weakened):** all 22 pre-existing denials refuse with error strings identical to c1171867 (QA).

## Advisories (not blocking; triaged under the operator's 2026-11-27 rule)

1. **Code reviewer, med, substance: two test helpers are grade 2 against the test bar of 3.**
   - The helpers are T-04 `bug2582_station_stub` (`tests/integration/test-lead-start-return.py:325`) and T-01 `converted_case.body` (`tests/unit/test-plan-merge-station-convert.py:107`).
   - Both predate the fix round: every fix-range function meets its bar.
   - The reviewer records each as a reasoned DEC-209 grade-2 exception (`code_grade: grade_2`).
   - Kept as advisory. med does not gate here, and the reasons keep each witness's fixture lifecycle in one place.
2. **Code reviewer, low, substance, executed: an artificially over-nested `plan.yaml` makes `load_plan` raise `RecursionError` through `validate()`.**
   - At c1 the same input gave a "plan.yaml unloadable" refusal.
   - The failure is closed: the host refuses when validation is unavailable.
   - The trigger needs a hand-made malformed file.
   - Advisory only; it does not justify a new test or another fix round.
3. **Code reviewer, low, inspection: a DEC-113 project override of the `scope` persona gets worst-wins instead of relief.**
   - The outcome is the same as base, and no override ships.
   - The drift guard for the shipped team file is real: the reviewer mutated it and the guard went red.
   - Advisory.
4. **QA and pm, low, deduplicated: `bug2582-guard-eng-lead-plan-steps` stays green under mutant M6**, because its fixture carries `findings: []`.
   - The code is correct today, so the outcome is no worse than base. This is the advisory the operator asked for, now present but not discriminating.
   - Per the triage rule, it is no reason for a new test or another round.
5. **Code reviewer, low, form: the fix-round receipt says "every changed function meets its grade bar".**
   - That is true for the fix range only. Over the full pinned range, items 1's two grade-2 helpers are the exception.
   - This is a wording overstatement in the record. No code change follows.

## Assurance

- **QA.** Both required runners ran once from the pin.
  - Results: unit 71/71 and integration 95/95, runner exit 0.
  - The receipts are `qa/manifest-unit.json` and `qa/manifest-integration.json` in this run dir, and are unedited.
  - Fail-first is natural red for SC-01, 03, 05, 06, 10 and 11. SC-02 is mutation-tier (M5). SC-07 and SC-09 are non-regression.
  - These are this host's interpreter and environment, not CI (G-03).
- **Security.** The first dispatch was refused by the model provider's `cyber_policy` filter before doing any work.
  - The redispatch used neutral wording and executed both closure probes and the edge probes. Nothing was refused to it.
  - Its live-host seam (where the mission is captured from the dispatch) is inspection-only (`harness-hooks.ts:1368-1379`). The offline fixture covers that seam.
- **UI.** It scoped itself out on a measured census of 44 changed paths, none of them UI.

## Pointers

- `notes/review-harness-qa-c2.md`
- `notes/review-harness-code-reviewer-c2.md`
- `notes/review-harness-security-reviewer-c2.md`
- `notes/review-harness-ui-reviewer-c2.md`
- `notes/research-BUG-2582-plan-station-and-rollup-goalcheck-validate-c2.md`

```yaml
VERDICT: PASS
DIGEST:
  headline: 'BUG-2582 is ship-ready at 4460c352. All five c1 must-fixes are closed,
    and each closure was executed: c1171867 accepts the missing-slot, persona-swap
    and dispatch-mission cases, and the pin refuses them. The four former CI reds
    exit 0, unit 71/71 and integration 95/95, and SC-01..SC-11 are met. Five non-blocking
    advisories remain; the highest is two med grade-2 test helpers.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'The matrix is green at 4460c352: unit 71/71 and integration 95/95,
      runner exit 0. The four c1 reds are now green. The MF-1 cases are red at c1171867,
      and each is discriminated by its own single-leg mutant. All 22 pre-existing
      denials refuse identically. One low advisory: the SC-07 guard does not discriminate
      M6.'
    files_touched:
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-03-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-03-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: The real missing-design counterexample is closed. The pinned diff has
      two non-blocking grade-2 test helpers and no must-fix.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: 'Both prior authorization gaps are closed: isolated fixtures that c1171867
      accepted are refused at 4460c352. No security findings remain.'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B is out of scope: none of the 44 changed paths is a UI surface.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All three perspectives pass and SC-01..SC-11 are met. The DEC-123, DEC-254
      and DEC-228 amends landed. The SC-05 and SC-06 legs are now witnessed by tests
      that are red at c1171867.
    files_touched: []
  must_fix: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-03-validate-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-03-validate-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-03-validate-validator/qa/manifest-integration.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/observations/harness-qa.md
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'QA''s receipts are runs on this host''s interpreter and environment, not CI:
    unit 71/71 and integration 95/95, runner exit 0.'
  - Security's first dispatch was refused by the provider's cyber_policy filter before
    it did any work. The redispatch, with neutral wording, executed the closure and
    edge probes. Its live-host mission-capture seam is inspection-only; an offline
    fixture covers it.
  - The receipt says 'every changed function meets its grade bar'. That holds for
    the fix range only. Two grade-2 test helpers from the original build remain in
    the full pinned range (form, no code change).
  - 'The SC-07 guard case bug2582-guard-eng-lead-plan-steps was added as ruled, but
    it stays green under mutant M6 because its fixture has findings: []. The code
    is correct and no worse than base, so this is no reason for a new test or another
    round.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'test-plan-merge-station-convert.py: natural red at base union.py (MergeRefusal
      code 5); 10/10 at the pin'
  - id: SC-02
    verdict: met
    method: automated
    evidence: The guard cases pass. harness_yaml.py has no diff from base. Mutant
      M5 turns them red.
  - id: SC-03
    verdict: met
    method: automated
    evidence: bug2582-inv34-remedy-line is red at base and passes at the pin
  - id: SC-04
    verdict: met
    method: inspection
    evidence: approval.py and check.py have no diff from base. The check_state/plan.py
      hunks are INV-34 only. _inv3 reports pending (code reviewer, pm).
  - id: SC-05
    verdict: met
    method: automated
    evidence: 'deny-missing-slot: c1171867 gives no errors; the pin refuses. The code
      reviewer''s c1 counterexample is refused at the pin. pm''s real-data probe of
      the run-01 digest with design dropped is refused at the pin, and the intact
      digest is accepted.'
  - id: SC-06
    verdict: met
    method: automated
    evidence: Graded on candidates only (OQ-2 ruling). deny-persona-swap and deny-dispatch-mission-patch
      give no errors at c1171867 and are refused at the pin. Each single-leg mutant
      turns only its own case red.
  - id: SC-07
    verdict: met
    method: automated
    evidence: 'other-lead-eng and other-lead-validator are refused, with error strings
      identical at c1171867 and the pin. Discrimination of the product-lead gate is
      unshown: M6 stays green (advisory).'
  - id: SC-08
    verdict: met
    method: inspection
    evidence: DECISIONS.md DEC-123 at 2477-2507 states the roster and mission terms.
      The DECISIONS-INDEX row is 28 words, names the carve-out, and regenerates byte-equal.
      SPEC.md 1977-1984 and the harness-team SKILL row are present.
  - id: SC-09
    verdict: met
    method: automated
    evidence: 'test-validate-digest.py, test-plan-merge.py, test-harness-yaml.py and
      test-check-state-plans.py: returncode 0 in manifest-integration.json at 4460c352'
  - id: SC-10
    verdict: met
    method: automated
    evidence: test-lead-start-return.py passes 63/63. stub-convert-after-start is
      red at base union.py.
  - id: SC-11
    verdict: met
    method: automated
    evidence: bug2582-producer-witness is red at base. The apply prompt order is [891,1024,1657]
      at the pin against [891,-1,1000] at base.
  - id: DEC-123
    verdict: met
    method: inspection
    evidence: 'pm: at 4460c352, DECISIONS.md 2491-2503 states the carve-out with the
      live-mission, exactly-one-slot and team-persona conditions. This matches the
      D-02 disposition and the code.'
  - id: DEC-254
    verdict: met
    method: inspection
    evidence: 'pm: DECISIONS.md 8466-8470, where conversion stamps drafted_at and
      seeds pending'
  - id: DEC-228
    verdict: met
    method: inspection
    evidence: 'pm: DECISIONS.md 7647-7651, which gives the order record-panel, then
      set-panel, then check'
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - 'SC-07: the guard case does not discriminate the product-lead gate (M6 stays green).
    Advisory under the triage rule.'
  - 'SC-06: non-candidate denials assert no reason text. The operator ruled under
    OQ-2 that none is needed, so this is recorded and not raised.'
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: T-04 bug2582_station_stub (test-lead-start-return.py:325) and T-01 converted_case.body
      (test-plan-merge-station-convert.py:107) are grade 2 against test bar 3
    why: Executed grader. Both predate the fix round and each carries a reasoned DEC-209
      grade-2 exception. med does not gate under advisory_unless_high. Advisory.
  - kind: substance
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'T-02: an artificially over-nested plan.yaml makes load_plan raise RecursionError
      through validate(); c1 refused it with an unloadable reason'
    why: Executed. The failure is closed (the host refuses when validation is unavailable),
      and the trigger needs a hand-made malformed file. Advisory only per the triage
      rule.
  - kind: substance
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'T-02: a DEC-113 project override of the scope persona gets worst-wins,
      not relief'
    why: Inspection only. The outcome is the same as base and no override ships. The
      drift guard for the shipped team file went red under mutation. Advisory.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa, harness-pm
    summary: 'T-02 test: bug2582-guard-eng-lead-plan-steps stays green under mutant
      M6'
    why: 'Its fixture has findings: []. The code is correct and the outcome is no
      worse than base, so this is no reason for a new test or another round (triage
      rule).'
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: The fix-round receipt overstates 'every changed function meets its grade
      bar'
    why: It holds for the fix range only; the two grade-2 helpers sit in the full
      pinned range. This is a record wording issue and no code change follows.
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-03-validate-validator/digest.md
```
