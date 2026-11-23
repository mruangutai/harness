# BUG-2420 validate c1 — PASS; c0 oracle finding closed

Pin `2b5b8b2aa7f411d515641ef0c73c0e6f7a7e07cd`, delta from c0 `c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df`. QA and code PASS; SC-01–03 met; no must-fix, no remaining findings, severity none. This is validation, not merge authorization or execution.

## Assessment and evidence
- **Closed, not dismissed:** c0 code-reviewer's med/substance T-01 oracle finding. `../../notes/review-harness-code-reviewer-c1.md` independently establishes complete expected output for all three rows, real writer execution, unchanged refusal bytes and retained four checks per row. Raw fixture I/O plus strict UTF-8 decoding performs no newline normalization; equality is byte-equivalent for these valid fixture bytes. This closes ordering, multiplicity and newline blindness without claiming coverage of arbitrary input encodings.
- **Independent falsification:** `../../notes/review-harness-qa-c1.md` reproduces insertion-byte and approval failures with pre-fix module SHA256 `ceef2a6b42eb2129c0d1a7bae071404287911ad10002738fb85623bf19738b9a`; rewrite/refusal controls stay green. Previously surviving M8 now fails precisely the complete-file assertion; fixed control passes. Code's closure reasoning and QA's executed kill agree; no severity reconciliation or dependent fixes remain.
- **Pinned runners:** QA installed frozen dependencies, then ran production kinds serially: `qa/manifest-unit.json` (66 files, runner exit 0) and `qa/manifest-integration.json` (95 files, runner exit 0), both bind the pin. Literal T-01 verify passes with base `d5be53927009df8e7848f860f9d0b4b03b89f9ad`, routes/audit clean and all 12 changed-function grades meeting their actual bars. No lead rerun. QA records an accidental silent first verify execution followed by its captured successful execution; neither is concealed.
- **Scope:** independent reader censuses confirm only the unit oracle changed outside feature records; production stations.py, integration test and BRIEF are unchanged since c0. Plan's top-level station advanced building→review; no SC/task/approval amendment. SC-03 fail-first and c0 product/security judgements are inherited, not represented as fresh executions.
- **Skipped by binding ruling:** security, UI and goal-check were not re-run: Python test-only delta, unchanged SCs, c0 already completed these readers. Their c0 evidence remains at `../2026-11-22-03-validate-validator/digest.md`. Only QA and code are members of this c1 panel.
- QA's write guard prevented scratch-file mutation; its in-memory real-module substitution supplied base/M8/fixed evidence without source edits. The note records this assurance boundary. Evidence-only report amendment requests no additional checks.

## Open questions
None. Main retains normal responsibility for committing receipts/run records and any merge decision. No second remediation round requested.

## Completed evidence-only amendment
QA's note now preserves the exact wrapper command and recorded base/M8 output/status in appendices A–C; fixed control is documented in D. Appendix F retains both verify executions honestly: unmatched output was filtered, while full-block exit 0 was retained. This one form send-back used the existing transcript and ran no further checks; it is not another remediation round. Both members are terminal, state.yaml is complete, and the PASS assessment above is unchanged.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pin 2b5b8b2a passes c1: c0 byte-oracle finding closed, M8 killed, both\
    \ runner kinds green; SC-01\u201303 met, no must-fix."
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 2
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Pre-fix byte/approval assertions fail, M8 now fails, serial unit 66
      files and integration 95 files pass; literal T-01 verify exits 0.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: C0 med/substance T-01 finding closed by complete-file byte-equivalent
      comparisons; production unchanged, no new findings.
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed exact pin 2b5b8b2aa7f411d515641ef0c73c0e6f7a7e07cd, with c1 judgement
    restricted to delta from c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df. Both readers
    independently confirm production stations.py and integration test unchanged; plan
    only advanced its top-level station.
  - 'C0 med/substance finding is closed, not dismissed or re-rated: strict raw-byte
    I/O and complete expected-file equality bind order, multiplicity and newlines
    for the valid UTF-8 fixture. QA independently killed previously surviving CRLF
    mutant M8; code supplied complementary static closure reasoning.'
  - DEC-255 runner receipts in runs/2026-11-22-04-validate-validator/qa/manifest-unit.json
    and manifest-integration.json bind the pin, exit 0, with 66 and 95 discovered/completed
    files respectively. QA installed frozen dependencies and ran kinds serially; lead
    did not rerun checks.
  - Literal T-01 verify passes with BUG2420_BASE=d5be53927009df8e7848f860f9d0b4b03b89f9ad,
    including routes, reader audit and all 12 changed-function grades meeting their
    actual bars.
  - 'Security, UI and goalcheck were skipped by binding delegated ruling: Python test-only
    delta, unchanged SCs, c0 already completed those readers. Their earlier results
    are retained, not represented as fresh c1 reviews.'
  - SC-03 pre-fix red is inherited from c0 after readers established unchanged integration/production
    bytes; current integration green is freshly executed at c1.
  - One evidence-only form send-back added raw wrapper/red/M8 commands and outputs
    from the existing transcript without reruns. cycles_used 1 denotes this documentation
    send-back, not another source-remediation round.
  - QA records an accidental silent first literal verify and a successful captured
    second execution; unmatched output was filtered, while full-block exit 0 was retained.
    Scratch-write restrictions required in-memory real-module substitution for base/M8/fixed
    controls.
  - No source changes by this panel. Main must commit receipts and closed run records
    through its normal durable-record process; this verdict does not perform a merge.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: "tests/unit/test-plan-merge-first-station.py three-row oracle; notes/review-harness-qa-c1.md\
      \ appendices A\u2013D reproduce pre-fix insertion failure with passing rewrite/refusal\
      \ controls, M8 CRLF failure at whole-file equality, and fixed green. Code c1\
      \ note confirms exact expected splices and no newline translation."
  - id: SC-02
    verdict: met
    method: automated
    evidence: notes/review-harness-qa-c1.md records pre-fix signed insertion rc=3
      and approval-proof failure; pinned unit and literal verify pass. Code confirms
      complete approved block comparison requires successful insertion.
  - id: SC-03
    verdict: met
    method: automated
    evidence: tests/integration/test-plan-merge.py drafting-path case unchanged from
      c0; inherited fail-first in notes/review-harness-qa-c0.md, freshly green c1
      integration receipt and literal T-01 verify including all four 2420 checks.
  needs_approval: false
  severity_max: none
  matrix_ok: true
  coverage_gaps: []
  findings: []
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
    status: skipped
    persona: harness-security-reviewer
    reason: 'Binding c1 scope ruling: Python test-only delta, unchanged SCs, c0 security
      review already completed.'
  - reader: ui
    status: skipped
    persona: harness-ui-reviewer
    reason: 'Binding c1 scope ruling: Python test-only delta, unchanged SCs, c0 UI
      scope-out already completed.'
  - reader: goalcheck
    status: skipped
    persona: harness-pm
    reason: 'Binding c1 scope ruling: Python test-only delta, unchanged SCs, c0 goalcheck
      already completed.'
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/runs/2026-11-22-04-validate-validator/digest.md
```
