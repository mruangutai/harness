# FAIL — 688c5ef5e3b6e0dd694afb3d6476c915934501d4

Both c0 reproducers are closed; two uncovered conversion behaviors still violate T-01. Severity maximum **med**. SC-01/02/04 met; SC-03 not met. Operator perspective fails; code-maintainer perspective passes as graded by PM. No source edits, commits, or pin changes by this team.

## One ranked must-fix list

1. **Med / substance / T-01 / SC-03 — unusable ASCII numbers still crash comparisons.** `check_state/board.py:154` calls `int(s)` without containing ValueError. QA independently ran a shipped parent containing 4,301 ASCII digits beside a usable issue-11 collision: the full CLI raises a traceback and loses that collision. Skip the unusable claim without losing usable claims; add a discriminating CLI regression. Preserve `feature_json_write.opt_int` and #2151's refusal contract. Reporters: QA F-1, code, PM G-01; all med. Gate despite medium severity because this is an explicit malformed-historical-field requirement, not a style preference.
2. **Low / substance / T-01 active-validation preservation — ASCII restriction changes active behavior.** The same helper is shared by active claims. QA c3 ran the same two-active-feature fixture at baseline and pin: Arabic-Indic `"٣"` versus integer `3` previously reports the cross-feature collision; the pin replaces it with a malformed-number finding and loses the collision. ASCII `"3"`/3 and 3/3 controls are unchanged. Preserve previously accepted active-number behavior while containing unusable conversion failures; add regression coverage. Reporter: QA F-2, unchanged low severity. QA considers it advisory; lead requires correction because T-01 explicitly says “Keep active-record validation unchanged.” This is a measured behavioral mismatch, not a new scope decision. Pin is **not silent**: c2's broader wording is withdrawn. Address both findings together at the shared conversion seam; rerun shipped and active controls after that remedy.

## Evidence and adequacy

- QA independently executed **60 unit + 86 integration files**, exit 0; shipped unit has 15 passing assertions, integration 16 tests. Fresh real corpus: candidate code at pin; owner main **b7af829c0207522b43f978b5275a2ebdc96b3210**, 9 landed / **7 shipped / 21 passing assertions**. Green matrix does not cover either new finding.
- Fail-first exists for every automated SC. Original baseline: 10 unit failures, 9 integration failures with current tests; rework baseline fe49c8df: 2 unit assertion failures and 2 CLI regression failures. Existing collisions/INV-29/INV-52 already passed and are not claimed newly red. Corpus behavioral red is retained in c0 and `/private/tmp/f2206-qa-evidence/base-real.txt` (21 actual failures, read by PM, QA and lead). QA c2's ImportError attempt proves nothing; c3 explicitly retracts the feature-wide “discrimination unshown” claim.
- Original duplicate-status bypass is closed by key counting, including quoted/list/empty/number-first cases. Original superscript-² crash is closed at INV-24 and the strict census accessor; QA's reverted-accessor mutant fails. `opt_int` remains unchanged; #2151 integration is green, but QA was refused a new made-total mutation, so no independent new LABEL-mutation proof is claimed.
- Code independently graded **58 functions PASS**. Qualitative Stage 2 remains deferred while compliance fails. Security is source-inspection-only with no independently exploitable finding; its PASS does not override QA's reliability counterexample. UI measured **42 total changed objects / 21 specified implementation objects / zero visual objects** and correctly scoped out.
- QA and code measured **602c81a3→688c5ef5 changes only feature.json review_sha**. The 146-file, verify-exit=0 log at 602c81a3 is equivalent-code historical evidence, **not** literal verification at the pin. QA ran components separately; exact-pin check-state exits 1 on disclosed INV-33 stale metadata and three INV-26 live-board mismatches. Literal verify was not rerun wholesale; no new clean literal result is asserted. Superseded regate text and station drift remain disclosures, not findings.

## Dispositions and pointers

No reviewer finding silently dropped or re-rated. Duplicate F-1 reports merge into item 1. QA's F-2 acceptability question is resolved by existing T-01 preservation text, not escalated as scope approval. One same-run QA evidence/classification correction; five logical steps, one send-back. QA c3 carries c2's measured 60/86 counts; its return's `named_tests: 2` is not used as discovery evidence. Product guidance remains absent as disclosed.

**Nonblocking Q-01 remains:** align T-01's YAML-mapping/invalid-YAML wording with DEC-252's text-line classification decision; no implementation ruling is invented here.

Reader artifacts under feature `notes/`: `review-harness-qa-c2.md`, `review-harness-qa-c3.md`, `review-harness-code-reviewer-c2.md`, `review-harness-security-reviewer-c2.md`, `review-harness-ui-reviewer-c2.md`, and `research-FEAT-2206-skip-shipped-features-goalcheck-validate-c2.md`. State checkpoint: this run's `state.yaml`. Main-session orchestrator owns remediation and the next pin.

```yaml
VERDICT: FAIL
DIGEST:
  headline: '688c5ef5: both c0 reproducers are closed, but oversized shipped numbers
    crash comparisons and active Unicode-number behavior regresses.'
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: Matrix passes; two uncovered conversion defects reproduced.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Oversized shipped-number conversion violates SC-03; 58 functions pass
      mechanical grading.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No independently exploitable security regression identified.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured census contains no visual UI.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator perspective fails SC-03; code-maintainer perspective passes.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/notes/research-FEAT-2206-skip-shipped-features-goalcheck-validate-c2.md
  must_fix:
  - 'T-01: Contain ValueError from oversized ASCII issue strings in _inv24_issue_number;
    skip unusable shipped claims while preserving usable collision detection. Add
    regression coverage without changing opt_int''s contract.'
  - 'T-01: Preserve previously accepted active Unicode-digit claims and their collision
    detection; add baseline/pin regression coverage.'
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01: oversized shipped issue strings still crash INV-24.'
    why: QA reproduced a 4,301-digit shipped parent raising ValueError at board.py:154
      and losing a usable issue-11 collision. QA, code and PM concur. This blocks
      the explicit SC-03 malformed-field contract.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01: ASCII-only conversion changes active-record validation.'
    why: "Identical baseline/pin CLI fixtures show Arabic-Indic '\u0663' versus integer\
      \ 3 loses its collision and gains a malformed-number finding. Severity remains\
      \ low; lead requires repair because T-01 explicitly preserves active-record\
      \ behavior."
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - No regression test covers oversized shipped issue-number strings.
  - No regression test preserves active Unicode-digit collision behavior.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: QA independently confirmed classification/open-order assertions and
      duplicate-status baseline failures.
  - id: SC-02
    verdict: met
    method: automated
    evidence: CLI selection assertions pass; fresh real corpus contains 7 shipped
      records and 21 passing assertions. Retained baseline capture contains 21 behavioral
      failures.
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: Oversized shipped parent crashes comparison and loses the surviving
      usable collision.
  - id: SC-04
    verdict: met
    method: automated
    evidence: Retirement assertions fail at baseline and pass at pin; adjacent controls
      remain green.
  adequacy_notes:
  - Both original c0 reproducers are closed, including the strict-census superscript-digit
    path.
  - QA independently ran 60 unit and 86 integration files successfully; fail-first
    evidence exists for every automated SC.
  - 'Fresh corpus provenance: implementation at review pin; owner main b7af829c0207522b43f978b5275a2ebdc96b3210;
    7 shipped records.'
  - 602c81a3 differs from the pin only in feature.json review_sha. Its green full-verify
    log is equivalent-code historical evidence, not literal verification at the pin.
  - Exact-pin check-state exits 1 on disclosed stale metadata/live-board mismatches;
    no fresh clean literal verify is asserted.
  - Mechanical grading passed 58 functions; qualitative Stage 2 remains deferred.
    Security was reasoning-only; UI correctly scoped out.
  - One QA correction supplied valid finding classifications, end-to-end active-number
    evidence and reconciled retained corpus reds. QA's active-number acceptability
    question is resolved by T-01's existing preservation requirement.
  open_questions:
  - id: Q-01
    question: Align T-01's YAML-mapping/invalid-YAML wording with DEC-252's text-line
      classification decision.
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/notes/research-FEAT-2206-skip-shipped-features-goalcheck-validate-c2.md
  branch: none
  needs_approval: false
  escalations: []
  expertise_update: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/runs/validate-c1-validator/digest.md
```
