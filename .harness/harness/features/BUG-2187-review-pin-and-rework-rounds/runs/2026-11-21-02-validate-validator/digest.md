# ESCALATE — BUG-2187 validation

Pin: `1b35414bfc865786baffe0418528deeeef141272`; base: `5bd9efd411a4b4a7a6a09dcf7517946c75c5f220`. Implementation inspection passes, but explicit SC-01/02 regression obligations remain incomplete and QA's independent return hook exits 1 without identifying its failing case. No clearance to ship.

## Criteria and execution
- **SC-01 partial:** station/serialization regressions genuinely fail at production-identical `ee550318` and pass at pin (44 integration cases). Nested-task status and three named silences/placeholder lack assertions. `notes/review-harness-qa-c0.md` contains measured subjects, mutations and reproduction; goalcheck c1 explains literal acceptance.
- **SC-02 partial:** absent-verb base-red and exact-pin green (128 unit tests), default/ref/full-id/refusal behavior and guidance verified. Shared-writer and unrelated-field safety remain unbound by tests.
- **SC-03 met:** direct-fix/multiple/boundary/replace-not-sum authentic base-red to pin-green; boundary mutant fails. Defensive timezone branch remains advisory.
- QA ran literal T-01 verify at pin: exit 0, **52.6s**. Canonical-reader audit: exit 0, **0 unresolved / 100 Python files**; structure locks: **ALL PASS**; exact-range code grade: **31/31 PASS**. Standing kind executions: unit **61 files**, integration **87 files**, both exit 0 in QA's isolated execution.
- All five requested implementation claims are supported by code/security inspection: byte fast path, loaded-document shallow lifecycle exclusion and legacy/load-error byte fallback; full commit resolution before shared writer; regates or fallback never summed; unchanged documented seam; `_inv33_reviewed` inventory exemption. This is present correctness, not proof every boundary is regression-defended.

## Ranked, deduplicated disposition (all T-01)
1. **med / substance / must-fix:** `tests/unit/test-feature-record.py:1278` and `.claude/skills/harness/bin/feature-record.py:607-619`: unrelated-field destruction and shared-writer bypass mutants stay green. Add the explicitly promised preservation/writer-contract regression assurance. QA gap 4 + PM SC-02.
2. **low / substance / must-fix:** `tests/integration/test-check-state-records.py:489-510`, `.claude/skills/harness/bin/check_state/feature_record.py:71-72,197`: task-nested status stripping survives; three named silences and placeholder lack assertions. Complete the explicitly promised SC-01 regression boundaries. QA gaps 2/3 + PM SC-01.
3. **med / substance / advisory:** `.claude/skills/harness/bin/check_state/feature_record.py:84-89`: legacy/unloadable byte fallback mutants survive (QA gap 1). Real test-strength weakness, not an independent new acceptance demand.
4. **low / substance / advisory:** `.claude/skills/harness/bin/feature-record.py:673`: timezone-comparability guard untested (QA gap 5a); not an added SC-03 criterion.
5. **none / form / resolved:** `notes/receipts/red-inv33.txt:1` and `red-feature-record.txt:1`: historical red detail weakness supplied by QA's own reproduction (gap 5b).
6. **med / substance / resolved:** `notes/receipts/green-verify.txt:1`: PM G-01 provenance concern closed by QA exact-pin green and production-identical base-red. Original receipts are not retroactively strengthened.

**Assessment:** QA calls gaps advisory; PM identifies literal task clauses. I adopt PM's bounded SC-01/02 ruling: plan intent explicitly requests the existing silence boundaries and asserts unrelated-field preservation; SC-02 names the shared writer. Matrix satisfaction and natural reds do not establish those untested clauses. This is not a style gate or a demand to kill every mutant. No production defect was observed. Complete unit safety assertions first, then integration boundary assertions; remedies share no production dependency. Source/test remediation remains Main's DEC-174 lane, not a delegated fix author.

## Open question and reader bounds
- **Q-GATE:** QA c2 records hook `run-unit-tests.py` exit 1, while its reported tail says integration ALL PASSED. No failing case/raw log was supplied; cause and environment are unknown. `validate-digest.py:2044-2107` runs against the artifact-holder checkout with inherited environment, not QA's managed pin with `HARNESS_AGENT_TYPE` removed. This bounds comparability; it does not establish an environment cause or waive the failure. Recover existing full failure/environment evidence; do not rerun merely to confirm a known failure.
- Reader outcomes: QA **ESCALATE** (`notes/review-harness-qa-c2.md`, c0 execution, c1 severity); code **PASS**; security **PASS** (static inspection only); UI **PASS / scoped out** after measuring 20 changed paths and zero rendered surfaces; PM **FAIL** (`notes/research-BUG-2187-review-pin-and-rework-rounds-goalcheck-validate-c1.md`). Both declared perspectives remain partial. All readers terminal; two evidence/form send-backs, no implementation rework round spent.

Authority: signed T-01/accepted inventory amendment; `docs/PRINCIPLES.md` — “Verification is the product”, “No more specific than necessary”, “Never falsify the record”. Review gate `advisory_unless_high` does not remove explicit acceptance obligations. Severity maximum **med**; must-fix nonempty; independent QA escalation takes precedence over FAIL.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: Pin 1b35414b implements the contracts, but SC-01/02 regression obligations
    remain partial and QA's independent hook exits 1 without an identified failing
    case.
  open_questions:
  - id: Q-GATE
    question: 'Recover independent run-unit-tests.py failure details and environment:
      QA''s isolated exact-pin runners exited 0, but the return hook exited 1 and
      exposed only an integration ALL PASSED tail. Cause remains unknown; do not assume
      an environment defect or rerun merely to confirm the known failure. See notes/review-harness-qa-c2.md
      and validate-digest.py:2044-2107.'
    blocking: true
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 2
  members:
  - step: qa
    persona: harness-qa
    verdict: ESCALATE
    headline: Exact-pin verify and authentic base-red reproduced; independent return-hook
      exit 1 remains unexplained.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: SC-01..03 implementation inspection passes; no code findings.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Static inspection finds no exploitable regression.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 20 changed paths and zero rendered/UI surfaces; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Provenance resolved; SC-01/02 partial on explicit regression obligations,
      SC-03 met.
    files_touched: []
  must_fix:
  - 'T-01 / SC-02: Complete tests/unit/test-feature-record.py:1278 regression assurance
    for unrelated-field preservation and the shared locked/schema-checked writer contract;
    destructive-field and writer-bypass mutants survive.'
  - 'T-01 / SC-01: Complete tests/integration/test-check-state-records.py:489-510
    coverage for task-nested status and the explicitly preserved no-git, unresolved-pin,
    absent-disk-plan and placeholder boundaries.'
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed 5bd9efd411a4b4a7a6a09dcf7517946c75c5f220..1b35414bfc865786baffe0418528deeeef141272.
    All five readers terminal; no production edits or merges performed.
  - 'QA ran literal T-01 verify at exact pin: exit 0, 44 integration cases and 128
    unit tests, 52.6 seconds. Canonical-reader audit: exit 0, 0 unresolved sites across
    100 Python files. Structure locks: ALL PASS. Exact-range code grade: 31/31 PASS.'
  - 'Each red is authentic: QA measured ee550318 production identical to immutable
    branch-base production, overlaid pinned tests, and reproduced two integration
    STALE failures plus eight unit AssertionErrors, not setup/import failures.'
  - 'All five implementation claims are supported by code/security inspection: shallow
    loaded-document comparison and byte fast path/fallback; preserved silences; commit
    resolution before shared writer; regates or fallback never summed; documented
    seam and accepted classification.'
  - 'QA''s matrix floor is satisfied, not unconditional suite clearance: its independent
    return hook subsequently exited 1. Hook source selects the artifact-holder checkout
    with inherited environment; comparability with QA''s managed pin remains unestablished.'
  - 'QA calls gaps advisory; PM identifies explicit signed obligations. Lead adopts
    PM''s bounded SC-01/02 ruling: signed intent requests silence-boundary coverage
    and unrelated-field assertions, while SC-02 names the shared writer. This is not
    a style gate or demand that every mutant die.'
  - Prioritize SC-02 safety assertions, then SC-01 boundary assertions. Fallback/timezone
    gaps remain advisory. Main retains remediation under DEC-174; no new scope or
    approval requested.
  - PM G-01 and historical receipt-detail weakness are resolved by QA's independent
    reproduction. Original records remain unchanged.
  - Two evidence/form send-backs counted; no implementation rework round spent. Both
    declared perspectives remain partial. Severity maximum med; nonempty must_fix
    fails acceptance, and QA ESCALATE takes precedence.
  - 'Reader bounds: QA supplied execution and falsification evidence; code/security
    were inspection-only for behavior; UI measured its census and correctly scoped
    out. Detailed rationales are in the durable digest.'
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated integration plus pinned inspection
    evidence: 'notes/review-harness-qa-c0.md: inv33.e/f genuinely fail at ee550318
      and pass at pin; 44 integration cases pass. Task-nested-status mutant survives;
      three named silences/placeholder lack assertions. Goalcheck c1 records the explicit
      acceptance gap.'
  - id: SC-02
    verdict: partial
    method: automated unit plus pinned inspection
    evidence: 'notes/review-harness-qa-c0.md: four PinReviewTest base failures and
      exact-pin 128 passing unit tests; HEAD/ref/refusal and guidance exercised. Unrelated-field
      destruction and shared-writer-bypass mutants survive. Goalcheck c1 records the
      explicit acceptance gap.'
  - id: SC-03
    verdict: met
    method: automated unit plus pinned inspection
    evidence: 'notes/review-harness-qa-c0.md: four genuine SpendTest base assertions
      fail and pass at pin; direct fixes, multiple rounds, equality boundary, exclusions,
      replacement-not-sum and fallback covered. Boundary mutant fails; defensive timezone
      coverage remains advisory.'
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - 'SC-02: unrelated-field preservation and shared-writer contract not regression-bound;
    must-fix.'
  - 'SC-01: task-nested status and three named silences/placeholder lack assertions;
    must-fix.'
  - 'Advisory: unloadable/legacy PLAN.md byte fallback mutants survive.'
  - 'Advisory: naive/aware timestamp guard mutant survives.'
  - Independent hook exit 1 unexplained despite green isolated executions; overall
    suite clearance withheld.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: harness-qa; harness-pm
    summary: 'T-01 / SC-02 must-fix: tests/unit/test-feature-record.py:1278 and .claude/skills/harness/bin/feature-record.py:607-619
      leave unrelated-field preservation and shared-writer safety unbound.'
    why: Mutants bumping cycles_used, wiping judgements/mission or bypassing the shared
      writer retain 128 passing tests. Signed intent requires preservation assertions;
      SC-02 names the writer contract.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa; harness-pm
    summary: 'T-01 / SC-01 must-fix: tests/integration/test-check-state-records.py:489-510
      and .claude/skills/harness/bin/check_state/feature_record.py:71-72 lack task-nested-status
      regression protection.'
    why: A mutant stripping task-nested status survives. Arbitrary nested status preservation
      is explicitly named; current inspection does not provide regression assurance.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa; harness-pm
    summary: 'T-01 / SC-01 must-fix: .claude/skills/harness/bin/check_state/feature_record.py:197
      lacks assertions for three named silences and placeholder handling.'
    why: No-git, unresolved-pin, absent-disk-plan and placeholder boundaries are inspected
      as preserved but untested. Pre-existing, not a production regression; signed
      T-01 nevertheless requests the retained boundary coverage.
  - kind: substance
    scope: none
    severity: med
    reader: harness-qa
    summary: 'T-01 advisory: .claude/skills/harness/bin/check_state/feature_record.py:84-89
      legacy/unloadable byte fallback lacks regression protection.'
    why: Fallback-to-None mutants survive and could hide malformed-plan edits. Retained
      as an advisory weakness, not an independent added acceptance demand.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01 advisory: .claude/skills/harness/bin/feature-record.py:673 timezone-comparability
      guard is untested.'
    why: Removing the guard leaves tests green. Not an additional SC-03 acceptance
      case; reader corrected the original merged classification in notes/review-harness-qa-c2.md.
  - kind: form
    scope: none
    severity: none
    reader: harness-qa
    summary: 'Resolved: notes/receipts/red-inv33.txt:1 and notes/receipts/red-feature-record.txt:1
      omit full historical failure details.'
    why: QA's independent immutable-subject reproduction supplies actual STALE violations
      and assertion differences. Assessed and dismissed as an outstanding gate; historical
      receipts remain unchanged.
  - kind: substance
    scope: none
    severity: med
    reader: harness-pm
    summary: 'Resolved G-01: notes/receipts/green-verify.txt:1 did not bind inherited
      green execution to the final pin.'
    why: QA subsequently executed the exact pin and reproduced production-identical
      base-red with pinned tests. PM closed provenance in its c1 goalcheck.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2187-review-pin-and-rework-rounds/.harness/harness/features/BUG-2187-review-pin-and-rework-rounds/runs/2026-11-21-02-validate-validator/digest.md
```
