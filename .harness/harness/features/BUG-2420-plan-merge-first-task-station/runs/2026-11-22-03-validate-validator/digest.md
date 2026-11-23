# BUG-2420 validate c0 — PASS with medium advisory

Pin `c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df`, base `d5be53927009df8e7848f860f9d0b4b03b89f9ad`. All five readers PASS; SC-01–03 met; no must-fix. Review policy is `advisory_unless_high` (control-plane `.harness/harness.json`). No source changed by this panel.

## Evidence and assessment
- QA: `../../notes/review-harness-qa-c0.md`; final production receipts `qa/manifest-unit.json` (66 files) and `qa/manifest-integration.json` (95 files) both bind the pin and report runner_exit 0. Literal T-01 verify exits 0, including 12 passing grades. Fail-first reproduced for every SC; nested-prose and approval-reset mutants redden their unit assertions. This is falsification evidence, not merely green discovery.
- Code: `../../notes/review-harness-code-reviewer-c0.md`; spec and quality pass. **Rank 1, med / substance / T-01:** membership-based line comparisons can miss reordered or duplicated unchanged lines. Preserve the reader's rating/kind. It is an oracle weakness, not observed production corruption, so advisory, not must-fix. Complete expected-output comparison is the suggested remedy; no dependent fixes or re-gates ordered.
- QA's CRLF mutant surviving is a related assurance limit, retained as QA-OBS-1 rather than inventing a classification. It does not contradict code's finding: several critical mutants die, but full byte preservation is not exhaustively regression-pinned. Source inspection plus existing integration controls support delivered compliance; no claim that every byte-corruption mutant is killed.
- QA-OBS-2 is assessed as intent-satisfied: the insertion row catches real nested-prose corruption; SC-02 and SC-03 independently reproduce the filed rc=3 symptom. Nothing is dismissed silently.
- QA-ENV-1 remains recorded: initial timeout/dependency failures were not passed; final receipts follow dependency installation and quiet serial reruns. Literal verify took 106s under load (plan expectation 60s); no SC states a latency gate. Do not erase initial failures or infer general load stability.
- Security: `../../notes/review-harness-security-reviewer-c0.md`; in-scope tampering/approval/write-boundary audit, no defect. UI: `../../notes/review-harness-ui-reviewer-c0.md`; seven-path census proves no visual UI, valid scope-out. These readers inspected evidence and executed no checks; their clean results are not independent execution claims.
- PM: `../../notes/research-BUG-2420-plan-merge-first-task-station-goalcheck-validate-c0.md`; operator and maintainer perspectives pass, all SCs met, zero decision dispositions. Goalcheck's historical green evidence is now supplemented by QA's pinned execution.

## Open questions
QA-OBS-1 asks whether byte-level test strengthening is desired; QA-OBS-2 and QA-ENV-1 are nonblocking reader observations/process cautions, preserved in the returned digest. No blocking question, scope change, approval request or remediation cycle is needed. Receipts and run records still require main's normal durable commit; this verdict is validation, not merge execution.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pin c0c3f1b9 passes SC-01\u201303 and both runner kinds; one medium advisory\
    \ test-oracle weakness, no must-fix."
  open_questions:
  - id: QA-OBS-1
    question: 'Advisory: the unit file reads results with read_text (universal newlines)
      and diffs lines by membership, so a CRLF vs LF difference in the inserted line
      is invisible (mutant M8 stays green). Production appends an explicit LF, so
      there is no known defect. Does main want a byte-level compare as a follow-up?
      Not blocking.'
    blocking: false
  - id: QA-OBS-2
    question: 'Advisory: SC-01 row 1 fails at base via a wrong-line rewrite of the
      nested verify prose, not the filed rc=3 symptom; rc=3 is reproduced by the SC-02
      and SC-03 tests. The BRIEF requirement that the insertion row fail pre-fix is
      met. Not blocking.'
    blocking: false
  - id: QA-ENV-1
    question: 'Process note: QA''s first runner receipts exited 1 under concurrent
      host load (test-omp-hooks.py 5s timeouts, test-check-plan-routes.py 60s timeout)
      and no node_modules in the fresh pin (typescript typecheck). QA installed with
      bun install --frozen-lockfile and reran each kind alone; both are now green
      and overwrote the receipts. Do not run the runner kinds in parallel on one host.'
    blocking: false
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: All automated SCs fail at base and pass at pin; unit 66 files and integration
      95 files green; literal T-01 verify exits 0.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Pinned writer conforms; one nonblocking medium byte-preservation test-oracle
      weakness in T-01.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Station mutation preserves approval and narrows nested-status matching;
      no exploitable security defect identified.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Seven-path pinned census confirms no changed visual UI; valid scope-out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: "Both signed perspectives pass; SC-01\u201303 met with zero decision\
      \ dispositions."
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df against d5be53927009df8e7848f860f9d0b4b03b89f9ad.
    All readers completed; no source edits.
  - 'QA final production receipts bind the pin, each runner_exit 0: runs/2026-11-22-03-validate-validator/qa/manifest-unit.json
    (66 files) and manifest-integration.json (95 files). Main must commit receipts
    with the durable run record.'
  - QA independently reproduced fail-first evidence for every SC and killed nested-prose
    and approval-reset mutants. Code/security/PM inspected rather than executed checks;
    UI scope-out rests on a measured seven-path census.
  - 'Retain code''s med/substance finding unchanged, nonblocking under advisory_unless_high:
    line-membership assertions do not comprehensively prove byte preservation. QA''s
    surviving CRLF mutant is a related assurance limit, not observed production corruption;
    no classification invented.'
  - 'QA-OBS-2 is intent-satisfied: SC-01 insertion row catches nested-prose corruption,
    while SC-02 and SC-03 reproduce rc=3. No requirement was silently narrowed.'
  - Initial environmental runner failures remain recorded in QA's note; final green
    receipts followed dependency installation and serial reruns. Literal verify took
    106s under load versus the plan's 60s expectation; no SC defines a latency gate.
  - 'Goalcheck artifact: notes/research-BUG-2420-plan-merge-first-task-station-goalcheck-validate-c0.md.
    Both perspectives pass; no decision-disposition landing failures.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: "tests/unit/test-plan-merge-first-station.py:91\u2013138; notes/red-first-T-01.md\
      \ and notes/review-harness-qa-c0.md reproduce failing insertion/nested-prose\
      \ checks at base; final pinned unit receipt green. Existing rewrite and genuine\
      \ absence controls pass."
  - id: SC-02
    verdict: met
    method: automated
    evidence: "tests/unit/test-plan-merge-first-station.py:144\u2013152 requires insertion\
      \ success and complete approved block preservation. QA reproduces rc=3 red at\
      \ base and an approval-reset mutant failure; pinned unit receipt green."
  - id: SC-03
    verdict: met
    method: automated
    evidence: "tests/integration/test-plan-merge.py:5142\u20135162 exercises empty\
      \ tasks, apply without seeded status, first station and reload. QA reproduces\
      \ station/reload red at base; pinned integration receipt green."
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: "T-01: membership-based line differences do not prove unchanged bytes\
      \ (tests/unit/test-plan-merge-first-station.py:84\u201387,108)."
    why: 'Reasoned scenario: swapping T-01/T-02 title lines while correctly rewriting
      T-02 status passes the row''s changed_lines assertion, although each task acquires
      the other''s title. Line membership ignores order and multiplicity. Compare
      complete expected output and exact original refusal bytes instead. No production
      corruption or executed mutant is claimed.'
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/runs/2026-11-22-03-validate-validator/digest.md
```
