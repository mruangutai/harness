# BUG-2190 validation — FAIL

Pinned review: `33c0c181e62c5e75692c8320fc01aaaaf06fa40b`; base `c6bd42d20fa9bf58e4c1dd3ede417caefc23a853`. Unrelated FEAT-71 merge excluded. Runtime intent is implemented and both suites pass, but two explicit signed acceptance clauses remain unasserted. Severity maximum: **med**. Main owns remediation under DEC-174; no scope change or new approval is needed.

## Ranked must-fix — T-01

1. **SC-03 · substance · med:** Cover non-mapping `factory` through the real unit gate and integration entrypoint, asserting invalid-authoritative-binding, no traceback, no owner fallback and zero remote reads. Both builders currently always supply a mapping (`tests/integration/test-check-state-inv37-offline.py:157`, `tests/unit/test-check-state-inv37-local-binding.py:123`). QA's mapping-guard-removal mutant M4 survives.
2. **SC-02 · substance · med:** Assert recovery guidance uses the factory repository for missing, mismatched and unproven receipt cases, excluding owner-based recovery selection. Classification assertions alone do not protect this (`integration:126-154`, `unit:110-120`); QA's owner-based recovery mutant M6 survives. Assert the actual command/selection rather than assuming its formatting contains a repository argument.

Both findings are independently reported by code and goalcheck and falsified by QA. Deduplicated to two findings, retaining code review's `substance`/`med` classification. Fix order reflects invalid-input boundary risk; fixes are otherwise independent.

## Evidence and adjudication

- **QA PASS (matrix only):** exact pin executed in a managed checkout because the feature worktree had advanced only in metadata. Literal verify exit 0, **3.06 s**, 13 unit assertions and 11 integration cases. Configured unit/integration kinds exit 0; pool census 59/85 files. QA reproduced semantic pre-fix red witnesses for every SC and killed local-validation, membership, owner-fallback, unbound-routing and online-resolver mutants. See `notes/review-harness-qa-c0.md`.
- **Code FAIL:** Stage 1 finds the two omissions; Stage 2 deferred, mandatory mechanical grades pass. **Security PASS:** reasoning-only trust-boundary audit, no actionable issue. **UI PASS/scoped out:** measured 13 final feature paths plus retired basename, no visual UI. **Goalcheck FAIL:** operator partial; maintainer pass. See corresponding `notes/review-harness-{code-reviewer,security-reviewer,ui-reviewer}-c0.md` and `notes/research-BUG-2190-inv37-offline-binding-goalcheck-validate-c0.md`.
- QA's green matrix does not override literal SC assertions. Its nonblocking accept-or-fix question is resolved here: complete the already-approved clauses; no operator question remains. `gates.review=advisory_unless_high` does not waive signed acceptance omissions: the nonempty must-fix list gates this run independently of severity.
- Assessed, not additional blockers: retained mutation code is not required by “QA records”; SC-04's offline twin supplies the intended paired red; syntax-only mutant survival is not a demonstrated independent defect; the table row has no separate signed assertion requirement. Build receipt's 14-vs-observed-13 unit count and runner PASS-line/pool-count discrepancy do not alter measured execution or discovery; no whole-suite count precision beyond pool census is claimed. Embedded mutation FAIL lines are not runner failures.

SC-01/04/05/06: **met**. SC-02/03: **partial**. No source/tests changed by this lead. All five children terminal; cycles used 0. **Open questions: none.**

```yaml
VERDICT: FAIL
DIGEST:
  headline: '33c0c181: suites pass, but SC-02 recovery-guidance and SC-03 malformed-factory
    assertions remain missing.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Matrix green; reproduced fail-first evidence; two required-clause mutants
      survive.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Two signed acceptance assertions missing; quality stage deferred.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No actionable security issue.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured feature diff contains no visual UI surface.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator perspective partial; maintainer perspective passes.
    files_touched: []
  must_fix:
  - 'T-01 / SC-03: Add non-mapping factory regressions asserting invalid binding,
    no traceback, no owner fallback and zero remote reads.'
  - 'T-01 / SC-02: Assert factory-based recovery guidance for missing, mismatched
    and unproven receipts; reject owner-based recovery selection.'
  files_touched: []
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Reviewed pinned 33c0c181e62c5e75692c8320fc01aaaaf06fa40b; unrelated FEAT-71 merge
    excluded.
  - 'QA executed the exact pin: literal verify exit 0 in 3.06 seconds; configured
    unit and integration suites exit 0, with pool discovery counts 59 and 85 files.'
  - QA independently reproduced semantic pre-fix failures for all six SCs. Mapping-guard-removal
    and owner-based-recovery mutants survived.
  - QA PASS describes matrix execution, not complete acceptance. Code and goalcheck
    FAIL agree on two explicit omissions; no severity disagreement remains.
  - 'QA''s accept-or-fix question is resolved: complete existing signed criteria through
    main-session-direct remediation; no new approval required.'
  - Mutation retention, syntax-only mutant survival and separate table-row assertions
    add no demonstrated acceptance blocker. Count discrepancies do not invalidate
    measured execution.
  - Security assurance is inspection-only; UI is scoped out, not visually verified.
    Code quality stage remains deferred until spec compliance passes.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: Integration i.1/i.2; unit u.1; QA reproduced baseline red and pinned
      green.
  - id: SC-02
    verdict: partial
    method: automated
    evidence: Classification covered by i.3-i.5/u.2; recovery-guidance assertion absent;
      mutant M6 survives.
  - id: SC-03
    verdict: partial
    method: automated
    evidence: Invalid repo values and bypass mutant covered; non-mapping factory case
      absent; mutant M4 survives.
  - id: SC-04
    verdict: met
    method: automated
    evidence: Offline/online paired cases i.1/i.7/i.8/u.4; online-resolver mutant
      killed.
  - id: SC-05
    verdict: met
    method: automated
    evidence: Owner, legacy, sync-off and no-plan controls i.9-i.11/u.5; baseline
      red reproduced.
  - id: SC-06
    verdict: met
    method: automated
    evidence: Real-gate unit cases u.1-u.5; independent unit red and final green reproduced.
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - 'SC-03: malformed non-mapping factory input is untested.'
  - 'SC-02: factory-based recovery guidance is unasserted.'
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer; corroborated by qa and goalcheck
    summary: 'T-01 / SC-03: malformed factory shapes lack regression coverage.'
    why: Fixtures always construct a mapping. Removing its guard survives tests, leaving
      malformed input capable of raising rather than producing the required invalid-binding
      finding.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer; corroborated by qa and goalcheck
    summary: 'T-01 / SC-02: recovery guidance lacks authoritative-repository assertions.'
    why: An owner-based recovery selection survives while provenance classification
      remains correct; QA mutant M6 demonstrates the missing protection.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2190-inv37-offline-binding/.harness/harness/features/BUG-2190-inv37-offline-binding/runs/2026-11-08-02-validator/digest.md
```
