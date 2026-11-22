# FEAT-2229 validation

FAIL at 1ef1edbf4cd13eed110e5a187fe45b2ce0438d43: matrix passes, but T-01 has malformed-creation and fenced-section gaps and T-02 lacks deletion-sensitive strike-alternative coverage. No fixes or commits; cycles 0.

## Readers
All paths below are feature-relative.
- qa PASS — notes/review-harness-qa-c1.md. Required unit/integration rerun at pin; red-first reproduced for SC-01/02/03/07.
- code FAIL — notes/review-harness-code-reviewer-c1.md. Stage 1 failed; quality stage withheld; static grade 83 pass. Findings are reasoned, not runtime reproductions.
- security PASS — notes/review-harness-security-reviewer-c1.md. Full 31-path trust-boundary inspection, no exploits found; no execution.
- ui PASS — notes/review-harness-ui-reviewer-c1.md. Measured 31-object census: no UI; valid self-scope-out.
- goalcheck FAIL — notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c1.md. Every perspective graded once; DEC-188 met; SC-07 partial.

## Ranked remediation
1. T-01/main-session-direct, substance/high, code F1: creation bypasses disposition schema validation (union.py:329-346); malformed present rows are written before the loader rejects them. Reject before write with no-file/refusal coverage (SC-01).
2. T-01/main-session-direct, substance/med, code F2: fenced example headings can impersonate the real DEC section (check.py:277-305). Make heading discovery fence-aware and add wrong-section CLI coverage (SC-02). Original reviewer treated this as advisory medium; synthesis makes it required because the literal SC forbids neighboring-section text satisfying a clause. Severity/kind unchanged.
3. T-02/main-session-direct, substance/med, pm F-01: test-plan-team.py:481-483 does not protect pm Mode 2:78-79 justified deletion/named successor/repointed citations alternative. Add owner-scoped independent assertion and deletion witness (SC-07).
These are distinct defects; T-01 source corrections precede regression verification. No T-03 remedy: pinned DEC-188 amendment landed.

## Adequacy and reconciliation
QA's green suite establishes execution and fail-first, not completeness. Its no-gap assessment is bounded by code F1/F2 and pm F-01, which identify counterexamples outside fixtures. Security's clean exploit assessment does not refute code's correctness defects. All three retain their original classifications/severities; no finding discarded.

PM's missing-QA Q-01 was a parallel-availability issue, resolved by the terminal QA artifact above, not an operator question. Original pm perspective grades were operator/reader/maintainer partial; QA closes their execution-evidence uncertainty, but code counterexamples and SC-07 still prevent acceptance. Synthesis SC-01 and SC-02 partial, SC-03 met after QA, SC-04/05/06 met, SC-07 partial. DEC-188 met by inspection at 1ef1edbf4cd13eed110e5a187fe45b2ce0438d43:.harness/harness/docs/DECISIONS.md:5313-5327 (retained distinction :5329-5336; D-01 successor DEC-254 :8253-8326). Seven keep rows skipped.

QA recorded an initial integration timeout followed by isolated and full rerun success; no failure erased. No extra gate is inferred. Exact classification fixture is tests/integration/canonical-reader-classification.json; test-plan-merge.py is unchanged in the range but inspected by readers. No new-class/unowned findings or unresolved questions.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'Pin 1ef1edbf fails acceptance: T-01 creation/section defects and T-02
    deletion-regression gap; matrix green, DEC-188 met.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Matrix and fail-first pass; notes/review-harness-qa-c1.md
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Creation and fenced-section defects; notes/review-harness-code-reviewer-c1.md
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Trust-boundary inspection clean; notes/review-harness-security-reviewer-c1.md
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured non-UI census; notes/review-harness-ui-reviewer-c1.md
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: SC-07 partial, DEC-188 met; notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c1.md
    files_touched: []
  must_fix:
  - 'T-01 / main-session-direct / SC-01: reject malformed present decisions_affected
    before creation writes using shared schema; add actual CLI refusal/no-file coverage
    and valid controls.'
  - 'T-01 / main-session-direct / SC-02: ignore fenced example headings when resolving
    authoritative decision sections; add wrong-section CLI counterexample.'
  - 'T-02 / main-session-direct / SC-07: independently protect pm''s justified deletion/named
    successor/repointed citations alternative with an owner-scoped assertion and deletion
    witness.'
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed dfa52536..1ef1edbf4cd13eed110e5a187fe45b2ce0438d43; no fixes/commits;
    cycles 0.
  - PM Q-01 closed by terminal pinned QA PASS, confirmed in its evidence-arrival qualification;
    no repeat goal-check. Original perspectives partial; QA resolves evidence absence
    but SC-01/02/07 gaps prevent acceptance.
  - QA green execution and reproduced red do not establish fixture completeness. Code/PM
    counterexamples qualify QA's no-gap assessment. Security found no exploit, not
    proof of correctness.
  - Code F2 remains substance/med as reported; synthesis requires remediation because
    literal SC-02 forbids neighboring-section clause satisfaction.
  - Code/PM findings are static reasoned counterexamples, not runtime reproductions.
    Code quality stage withheld after spec failure; static grade 83 pass. UI census
    measured 31 objects.
  - QA recorded first integration timeout, isolated success and full rerun success;
    no failure erased. Required discovery 62 unit files and 89 integration script
    blocks.
  - T-03 accepted; seven keep rows skipped. Exact fixture tests/integration/canonical-reader-classification.json;
    test-plan-merge.py unchanged in range but inspected.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated
    evidence: '1ef1edbf4cd13eed110e5a187fe45b2ce0438d43: QA notes/review-harness-qa-c1.md
      reports schema 40/40 and reproduced red; code F1 union.py:329-346 identifies
      malformed creation bypass. T-01.'
  - id: SC-02
    verdict: partial
    method: automated
    evidence: '1ef1edbf4cd13eed110e5a187fe45b2ce0438d43: QA reports dispositions 91/91
      and reproduced independent red; code F2 check.py:277-305 identifies fenced neighboring-section
      bypass. T-01.'
  - id: SC-03
    verdict: met
    method: automated
    evidence: '1ef1edbf4cd13eed110e5a187fe45b2ce0438d43: notes/review-harness-qa-c1.md
      confirms green and reproduced era/provenance red; PM inspected tests/integration/test-plan-decision-dispositions.py:297-335,360-493.
      QA closes original evidence-only partial. T-01.'
  - id: SC-04
    verdict: met
    method: inspection
    evidence: 1ef1edbf4cd13eed110e5a187fe45b2ce0438d43:.claude/skills/harness/teams/plan.yaml:59-66,103-108;
      templates/plan.yaml:75-86 and references/patch-lane.md:16-25 under same skill
      prefix.
  - id: SC-05
    verdict: met
    method: inspection
    evidence: 1ef1edbf4cd13eed110e5a187fe45b2ce0438d43:.omp/agents/harness-pm.md:58-82;
      .claude/skills/harness/teams/validate.yaml:120-121; .omp/agents/harness-validator-lead.md:104-105.
  - id: SC-06
    verdict: met
    method: inspection
    evidence: 1ef1edbf4cd13eed110e5a187fe45b2ce0438d43:.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326;
      DECISIONS-INDEX.md:188,237; SPEC.md:2009-2043,2287-2302. QA index regeneration
      verify green. T-03.
  - id: SC-07
    verdict: partial
    method: automated
    evidence: '1ef1edbf4cd13eed110e5a187fe45b2ce0438d43: QA test-plan-team 182/182
      and reproduced red; PM F-01 tests/integration/test-plan-team.py:481-483 omits
      deletion sensitivity for .omp/agents/harness-pm.md:78-79. T-02.'
  - id: DEC-188
    verdict: met
    method: inspection
    evidence: 1ef1edbf4cd13eed110e5a187fe45b2ce0438d43:.harness/harness/docs/DECISIONS.md:5313-5327
      replaces decisions_affected[0] human-only enforcement clause; :5329-5336 preserves
      distinction; :8253-8326 records successor D-01 as DEC-254. T-03.
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - T-01 SC-01 malformed creation refusal/no-file CLI coverage missing.
  - T-01 SC-02 fenced impersonated heading counterexample missing.
  - T-02 SC-07 strike deletion/successor/repointed citations alternative lacks independent
    deletion-sensitive assertion.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'F1 / T-01 / main-session-direct: creation writes malformed disposition
      rows.'
    why: 'Pinned union.py:329-346 parses and checks anchors without shared disposition
      shape validation; [{dec: DEC-10}] reaches creation bytes then fails loader.
      Static control-flow finding; SC-01.'
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'F2 / T-01 / main-session-direct: fenced headings impersonate authoritative
      decision sections.'
    why: Pinned check.py:277-305 discovers headings without fence state, allowing
      neighboring-section fenced text to satisfy a clause. Original advisory medium
      retained; literal SC-02 makes remediation required.
  - kind: substance
    scope: none
    severity: med
    reader: pm
    summary: 'F-01 / T-02 / main-session-direct: strike-deletion alternative lacks
      independent regression.'
    why: Pinned test-plan-team.py:481-483 remains matched when pm Mode 2:78-79 justified
      deletion/named successor/repointed citations alternative is removed. Static
      inference; violates SC-07.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-validate-validator/digest.md
```
