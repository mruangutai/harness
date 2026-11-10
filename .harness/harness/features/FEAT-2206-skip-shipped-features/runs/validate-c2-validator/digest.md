# BLOCKED — 4a351faea95ad3776f130d0f42f303a4eee3e4b9

Both c1 must-fixes are independently closed; 146 files pass. One newly measured branch-comparison gap needs an operator acceptance/scope ruling, not another unapproved fix cycle. Severity maximum **med**. SC-01/02/04 met; literal SC-03 not met. Operator perspective partial; code-maintainer perspective pass. No source edits, commits or pin changes by the panel.

## One consolidated finding; no assigned must-fixes

**F-1 / substance — strict-invalid shipped records lose usable INV-52 branch claims.** QA executed shipped `feat/dup` with parent `²`, 4,301 digits or `x`, alongside another same-branch landed feature (active and shipped variants): no collision. Parent 5 control reports it. Strict census refuses the whole mapping, and INV-52 skips document=None (`feature_corpus.py:225-239,445-456`; `check_state/corpus.py:153-160`). QA c4:34 is execution evidence; code c3 supplies the source trace.

Deduplicated code **med** and QA **low** reports into this one observation; neither original rating/kind is revised. Medium is the conservative panel maximum: ownership protection can disappear silently, while baseline `x` already skipped and baseline `²`/oversized crashed, so this is not evidence of a newly introduced general branch-population regression. The low rating's non-regression rationale is retained, not averaged away.

**Q-02 (blocking):** BRIEF SC-03's unqualified shipped-branch protection conflicts in scope with T-01's explicit preservation of INV-52 “as they already operate.” Its raw salvage rule specifically names INV-24. DEC-252 preserves all three comparisons but expressly describes usable factory claims for INV-24. No approved ruling settles malformed-record branch salvage. Remedy seams `check_state/corpus.py`/`feature_corpus.py` are outside T-01.files; changing the shared accessor instead would broaden active strict-record semantics. Therefore **must_fix is empty pending a scope ruling**, not because F-1 was dismissed. Code c4 retracts c3's unsupported automatic T-01 assignment; PM c4 supersedes c3's unconditional SC-03/operator pass. Both original notes remain intact.

Recommendation: ask the operator to choose explicitly between preservation-only acceptance acknowledging this pre-existing gap (PM's recommendation) and broader malformed-shipped branch retention with approved seam files and a regression (code's recommendation: upgrade plan). The lead recommends the latter for full literal SC-03 protection, but grants neither scope expansion nor acceptance waiver. Repeating tests cannot answer this question. BLOCKED rolls up PM BLOCKED above code ESCALATE.

## Evidence and adequacy

- QA c4 independently ran both c1 tests at baseline/c1/pin: oversized shipped number FAIL/FAIL/PASS; active Arabic-Indic digit PASS/FAIL/PASS. Superscript remains contained. `opt_int` is unchanged; documented accessor refusal remains. Both c1 dispositions are closed, not carried forward.
- Exact-pin QA: **60 unit + 86 integration files = 146**, exit 0; shipped unit **15 passing assertions**, integration **18 tests**, real corpus **7 shipped / 21 passing assertions**, owner main `b7af829c0207522b43f978b5275a2ebdc96b3210`. Fresh baseline has 10 unit failures, 10/18 integration failures and 21 corpus failures. Every automated SC has named natural fail-first evidence. Existing collision cases already green at baseline are not claimed newly red. No regression covers F-1; additional mutation was refused, so no independent mutation guarantee is claimed.
- QA measured b5b6fa70→pin: only feature.json review_sha/regate metadata differs. The retained verify-exit=0 log is equivalent-code historical evidence, not literal exact-pin verification. Fresh component execution at pin passes suite/schema/routes/anchors/index; check-state exits 1 on disclosed three INV-26 board mismatches only. No clean verbatim chained verify is asserted. QA's git-branch/log-write guard deviations remain in its report.
- Code independently graded **60 passing gated records**; Stage 2 qualitative approval remains withheld pending Stage 1 scope resolution. Security is source-inspection-only, with no exploitable regression identified; it is not another execution pass. UI measured **51 objects / zero visual surfaces**, correctly scoped out.
- Product spec/decision/architecture documents remain absent as disclosed. **Q-01 (nonblocking)** remains T-01 YAML-mapping wording versus DEC-252 text-line classification; retain adopted behavior and reconcile prose through the owner. Known station drift and superseded regate text are disclosures, not additional findings.

## Durable reader paths

Under feature `notes/`: QA `review-harness-qa-c4.md`; code `review-harness-code-reviewer-c3.md` corrected by `-c4.md`; security `review-harness-security-reviewer-c3.md`; UI `review-harness-ui-reviewer-c3.md`; goalcheck `research-FEAT-2206-skip-shipped-features-goalcheck-validate-c3.md` corrected by `-c4.md`. Five logical steps, two same-run adequacy send-backs, all terminal. Checkpoint: this run's state.yaml. Main retains commit/pin/remediation authority; Q-02 must reach the operator.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: '4a351fae: both c1 fixes verified and 146 files pass; malformed-shipped
    branch protection requires an acceptance/scope ruling.'
  team: validate
  steps_run: 5
  cycles_used: 2
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Both c1 regressions closed; matrix passes; branch-loss gap reproduced.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: ESCALATE
    headline: Medium branch-loss observation retained; task ownership unresolved.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Source inspection found no exploitable security regression.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 51 changed objects and zero visual surfaces; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: BLOCKED
    headline: Literal SC-03 not met; preservation-only acceptance requires operator
      ruling.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/notes/research-FEAT-2206-skip-shipped-features-goalcheck-validate-c4.md
  must_fix: []
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer; harness-qa
    summary: 'F-1: strict-invalid shipped records silently lose usable INV-52 branch
      claims.'
    why: QA reproduced missing branch collisions with malformed shipped parents; valid-parent
      controls collide. Code rated med, QA low; both original ratings are retained.
      Baseline garbage already skipped, while superscript/oversized values crashed.
      Automatic T-01 assignment was withdrawn because remedy seams are outside its
      files and preservation-only intent conflicts with unqualified SC-03. Pending
      Q-02, this is not an assigned must-fix.
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - No regression covers INV-52 branch retention from strict-invalid shipped records.
  - Additional comparison mutation evidence was unavailable; existing baseline-green
    collisions are not claimed newly red.
  - 'No clean verbatim exact-pin T-01 verify: check-state exits 1 on disclosed INV-26
    board mismatches.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'QA c4: classification/open-order assertions pass; fresh baseline has
      10 unit failures.'
  - id: SC-02
    verdict: met
    method: automated
    evidence: 'QA c4: CLI/read-boundary assertions pass; 7 shipped records yield 21
      passing corpus assertions versus 21 baseline failures.'
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: QA c4:34 reproduces lost malformed-shipped INV-52 branch claims. Both
      c1 INV-24 regressions are closed; preservation-only acceptance remains conditional
      on Q-02.
  - id: SC-04
    verdict: met
    method: automated
    evidence: 'QA c4: retirement assertions fail at baseline and pass at pin; adjacent
      controls remain green.'
  adequacy_notes:
  - QA independently verified oversized-number FAIL/FAIL/PASS and active Unicode-digit
    PASS/FAIL/PASS across baseline/c1/pin.
  - 'Exact-pin suite: 60 unit plus 86 integration files, exit 0; shipped unit 15 assertions
    and integration 18 tests pass. Every automated SC has fail-first evidence.'
  - 'Real-corpus provenance: owner main b7af829c0207522b43f978b5275a2ebdc96b3210;
    7 shipped records, 21 passing assertions.'
  - b5b6fa70 differs only in feature.json metadata; its retained green verify log
    is equivalent-code historical evidence, not literal exact-pin execution.
  - Code grading independently passed 60 gated records; qualitative Stage 2 remains
    withheld. Security assurance is source-only; UI correctly scoped out.
  - Code c4 corrects unsupported automatic task assignment; PM c4 supersedes unconditional
    SC-03/operator approval. Operator perspective partial; code-maintainer perspective
    passes.
  - Two same-run adequacy send-backs; all readers terminal. No source edits, commits
    or pin changes.
  open_questions:
  - id: Q-01
    question: Reconcile T-01 YAML-mapping wording with DEC-252 text-line classification
      while retaining adopted behavior.
    blocking: false
  - id: Q-02
    question: Does SC-03 require branch salvage from strict-invalid shipped records,
      or preservation of existing strict-census coverage? PM recommends explicit preservation-only
      acceptance acknowledging lost protection; code recommends upgrading the approved
      plan to authorize comparison-seam changes and a regression. Lead recommends
      the broader guarantee for literal SC-03 compliance. Operator ruling is required;
      no scope expansion or waiver is granted.
    blocking: true
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/notes/research-FEAT-2206-skip-shipped-features-goalcheck-validate-c4.md
  branch: none
  needs_approval: true
  escalations: []
  expertise_update: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/runs/validate-c2-validator/digest.md
```
