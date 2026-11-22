# FEAT-2229 — validate c3

**FAIL: suffix F3 is repaired and QA gates pass, but SC-02 still fails on one medium T-01 indentation variant.** Reviewed dfa52536..ab1e42460b5310a9473724edfb574454d39f6ca8. Five readers completed; cycles_used 0.

## One ranked must-fix

1. **F3-I / SEC-C2-01 residual / GC-C3-01 — substance / med / T-01 / SC-02.** At pinned `.claude/skills/harness/bin/plan_merge/check.py:203,279-325`, unrestricted indentation lets four spaces plus a closing-looking backtick run close an open fence. Markdown retains that line as content; the scanner instead selects a following spoof DEC-10 heading before its genuine section. Bound fence indentation and add actual-CLI spoof-rejection plus genuine-section control, red before fix and green afterward. One remedy addresses code, security, pm and QA's overlapping reports.

## Assessment

- QA `notes/review-harness-qa-c3.md`: full unit 62 files and integration 89 files, both exit 0; all signed T-01/T-02/T-03 verifies exit 0; code-grade PASSING 90. Actual-pin execution and station equivalence measured. F3 `case_info_string_run_does_not_close_a_fence` measured RED 99/100 at 48cc5b6a, GREEN 100/100 at pin. Prior F1/F2/F-01 remain closed; prior reds carried with explicit source-equivalence reasoning, not newly executed.
- QA independently executed the indentation spoof on synthetic pure-function input, not CLI. Code `notes/review-harness-code-reviewer-c3.md`, security `notes/review-harness-security-reviewer-c3.md`, and pm `notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c3.md` independently identify the same static acceptance failure. Existing suite lacks that regression; green matrix is not complete assurance.
- Preserve QA's low advisory classification and code/security's medium substance classifications unchanged. Consolidated priority is medium: decision-document write access is required, with no privilege escalation, but the explicit SC-02 own-section guarantee is bypassed. QA's Q-C3-01 (fold or backlog) is resolved here: same T-01 boundary and signed SC, not a new scope class. Medium alone is advisory under gates.review; unmet acceptance and security/pm FAIL gate this run.
- Operator pass; reader partial; code maintainer pass. SC-01/03/04/05/06/07 met. DEC-188 amend row met at pinned DECISIONS.md:5313-5336; D-01 resolves to DEC-254:8253-8326, owner T-03; seven keep rows skipped.
- UI `notes/review-harness-ui-reviewer-c3.md`: measured 43 changed objects, no rendered UI; PASS means scoped out, not visual assurance. QA's other fence probes (tilde, longer/shorter runs, suffixes, 1–3-space indentation and trailing whitespace) behaved correctly. Live corpus has no indented fence lines, which does not discharge adversarial acceptance.
- All LEAVE rulings remain closed; full-suite target duration 36.9s is the already-ruled advisory. No source changes or same-run send-backs. Open questions: none. Last-round disposition belongs to the orchestrator; this panel neither fixes nor waives SC-02.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'ab1e42460b5310a9473724edfb574454d39f6ca8: suffix F3 repaired and QA green;
    SC-02 still fails on medium T-01 over-indented fence spoofing.'
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
    headline: Gates green; F3 RED at 48cc5b6a then GREEN at pin; notes/review-harness-qa-c3.md.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Medium indentation residual; notes/review-harness-code-reviewer-c3.md.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: SC-02 indentation spoof remains; notes/review-harness-security-reviewer-c3.md.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 43 objects, no rendered UI; notes/review-harness-ui-reviewer-c3.md.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Reader partial, SC-02 not_met, DEC-188 met; notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c3.md.
    files_touched: []
  must_fix:
  - "1. F3-I / SEC-C2-01 residual / GC-C3-01 \u2014 substance / med / T-01 / SC-02\
    \ (code, security, pm; QA corroborates): restrict fence indentation at .claude/skills/harness/bin/plan_merge/check.py:203,279-325\
    \ so over-indented content cannot close an open fence and expose a spoof DEC heading.\
    \ Add actual-CLI spoof-negative/genuine-positive regression with red-first evidence."
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed dfa52536..ab1e42460b5310a9473724edfb574454d39f6ca8. Five readers complete;
    no same-run send-back, cycles_used 0.
  - QA measured all signed verifies green, full unit 62 files and integration 89 files
    exit 0; code-grade PASSING 90. Station code equivalence measured; actual pin executed.
  - F3 case_info_string_run_does_not_close_a_fence independently RED 99/100 at 48cc5b6a,
    GREEN 100/100 at pin. F1/F2/F-01 closed; previous reds carried by documented source
    equivalence, not freshly executed.
  - Deduplicated reports into one remedy. Preserve QA low advisory and code/security
    medium substance ratings unchanged; medium consolidated priority reflects integrity
    bypass requiring document write access, not privilege escalation.
  - 'QA Q-C3-01 resolved: fold into existing T-01/SC-02 acceptance, not backlog/new
    scope. Medium alone is advisory under gates.review; unmet SC-02 and security/pm
    FAIL block acceptance.'
  - QA synthetic pure-function spoof executed; specialist counterexamples inspection-only.
    No actual-CLI regression binds indentation. Current corpus has no indented fence
    lines; absence does not discharge acceptance.
  - UI measured no rendered surface; no visual assurance. Other fence probes behaved
    correctly. LEAVE rulings retained; 36.9s integration duration previously ruled
    advisory. No source fixes or old-pin reader reruns.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: ab1e4246:tests/unit/test-decision-disposition-schema.py:71-180; QA c3
      40/40; c2 RED 13/40 at dfa52536 retained.
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: ab1e4246:.claude/skills/harness/bin/plan_merge/check.py:203,279-325,355-368;
      indentation spoof independently inspected and QA synthetic probe corroborated.
      F3 suffix regression :317 RED 99/100 at 48cc5b6a, GREEN 100/100 at pin misses
      indentation. T-01.
  - id: SC-03
    verdict: met
    method: automated
    evidence: ab1e4246:tests/integration/test-plan-decision-dispositions.py:373-408,436-464,523-584;
      QA c3 100/100; historical natural RED retained.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: ab1e4246:.claude/skills/harness/teams/plan.yaml:59-66,103-108; templates/plan.yaml:75-86;
      references/patch-lane.md:16-25; code/pm inspection.
  - id: SC-05
    verdict: met
    method: inspection
    evidence: ab1e4246:.omp/agents/harness-pm.md:58-82; .claude/skills/harness/teams/validate.yaml:115-121;
      .omp/agents/harness-validator-lead.md:100-105.
  - id: SC-06
    verdict: met
    method: inspection
    evidence: ab1e4246:.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326; SPEC.md:2009-2043,2287-2302;
      DECISIONS-INDEX.md:188,237. QA regeneration no diff.
  - id: SC-07
    verdict: met
    method: automated
    evidence: ab1e4246:tests/integration/test-plan-team.py:424-509; QA c3 184/184;
      prior RED and F-01 mutation retained. Static instructions, not agent conduct.
  - id: DEC-188
    verdict: met
    method: inspection
    evidence: ab1e42460b5310a9473724edfb574454d39f6ca8:.harness/harness/docs/DECISIONS.md:5313-5336
      replaces human-only clause; decisions_affected[0], successor D-01->DEC-254:8253-8326;
      T-03. Keep rows skipped.
  - id: perspective:operator
    verdict: met
    method: inspection
    evidence: PM c3 operator pass; notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c3.md;
      SC-01/03/04/05/06/07 and DEC-188 landed.
  - id: perspective:reader
    verdict: partial
    method: inspection
    evidence: PM c3 reader partial; SC-02 own-section guarantee bypass, T-01.
  - id: perspective:code-maintainer
    verdict: met
    method: inspection
    evidence: PM c3 code maintainer pass; existing machinery reused; SC-03/06/07 met.
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - T-01/SC-02 lacks actual-CLI over-indented-closer spoof rejection and genuine-section
    control; green matrix misses demonstrated synthetic authority-selection failure.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer; security-reviewer; harness-pm
    summary: "F3-I / SEC-C2-01 residual / GC-C3-01 \u2014 T-01/SC-02: over-indented\
      \ closers expose fenced DEC examples as authority."
    why: At ab1e4246:check.py:203,279-325 four-space indentation closes a fence although
      Markdown retains content; following spoof DEC-10 is selected first. QA synthetic
      execution corroborates static reports. Acceptance unmet.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'QA advisory: 4+-space/tab-indented closer, T-01/SC-02; deduplicated
      into F3-I.'
    why: Preserve original low advisory rating. Fold-or-backlog question resolved
      against existing SC; consolidated with medium specialist finding, not a second
      remedy. Synthetic execution only.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-validate-c3-validator/digest.md
```
