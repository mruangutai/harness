# Validation — BUG-2295 — c2

PASS at 7d76c1cea576822760e8bc42432f8c01fc3c8031 against dd04e52a898109fdbe09cf5fa14e1148161734d0. The single consolidated T-01 substance defect in [c1](../2026-11-22-02-validate-validator/digest.md) is closed. Five readers PASS; no must-fix, no open questions, severity_max none. Zero send-backs hosted.

## Closure and assurance

- QA independently reproduced c1-fix RED using pinned tests over 253cdf2a production: rc=1, 105 ok, exactly 12 assertion failures. Build-c1, build-C1 and VALIDATE-C12 each fail Write/Edit refusal and exact lowercase canonical-path assertions. Pin GREEN: rc=0, 117 ok, zero FAIL. Lowercase build-c1/validate-c12/plan-c305, canonical build/validate/plan acceptance, cap/sections/Done when all execute green. SC-01/02 fail-first also includes original six lowercase Write/Edit failures against dd04e52a executed in c1; c2 does not claim to rerun that original RED. See ../../notes/review-harness-qa-c2.md and ../../notes/review-harness-qa-c1.md.
- Matrix: unit rc=0 (63 files), integration rc=0 (91 files); required kinds satisfied. Registered suite and dedicated regression establish executed mixed-case closure, not merely static inspection.
- Code confirms fix c4c93ef1 ancestry and empty source/test delta to pin. Detector uses _I; canonical diagnostic is lowercased; Write/Edit routing intact. SC-03 corrected comment and SC-04 byte-identical ship predicate/exemption plus untouched specified FEAT-2225/2229 history pass pinned inspection. Complexity grades pass. See ../../notes/review-harness-code-reviewer-c2.md.
- Security independently withdraws its c1 bypass concern after static inspection; no remaining security findings. UI measured the 18-path diff and validly scoped out. Their notes are ../../notes/review-harness-security-reviewer-c2.md and ../../notes/review-harness-ui-reviewer-c2.md. Only QA supplies runtime falsification; other lenses do not add execution assurance.
- Operator PASS (SC-01/04); code maintainer PASS (SC-02/03). DEC-174/225/252/254 keep dispositions preserved; canonical Mode 2 skips landing grades for keep. See ../../notes/research-BUG-2295-handoff-one-per-phase-goalcheck-validate-c2.md.

## Assessment and dismissals

No conflicting or surviving findings. C1 high correctness/low security ratings described one now-closed defect; neither reader's original rating is rewritten. Baseline-green canonical/unchanged-file controls do not prove refusal; explicit exit/message assertions do. Separate diagnostic-only mutation was not executed, but exact-path assertions executed green and failed in QA's natural RED, sufficient for the signed criteria. This is an assurance limit, not a new requirement. Previously dismissed dedicated-unit-coverage concern remains nonblocking because the assigned integration evidence and registered unit gate both ran. Pre-existing DEC-252 commentary discrepancy remains outside T-01, assessed-and-dismissed as instructed; no policy edit or scope expansion is proposed.

No source changes, test authoring, commits, fix hosting, pinning, shipping or close-run actions by this lead.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pin 7d76c1cea576822760e8bc42432f8c01fc3c8031 closes c1 mixed-case bypass;\
    \ SC-01\u201304 met, five readers PASS."
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
    headline: Independent 12-failure RED; 117-ok GREEN; matrix satisfied.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: C1 closure, ancestry, SC-03/04 and complexity confirmed.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Prior bypass closed; no security findings.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 18-path diff has no UI; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives pass; all SCs met and keep dispositions preserved.
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed pin 7d76c1cea576822760e8bc42432f8c01fc3c8031 against dd04e52a898109fdbe09cf5fa14e1148161734d0.
    Sole consolidated c1 T-01 defect closed; prior verdict runs/2026-11-22-02-validate-validator/digest.md.
  - 'fail_first SC-01/02: QA independently reproduced pin tests over 253cdf2a production:
    rc=1, 105 ok, 12 assertion failures. Build-c1/build-C1/VALIDATE-C12 each failed
    Write/Edit refusal and exact lowercase canonical-path assertions. Pin GREEN rc=0,
    117 ok, zero FAIL, including lowercase stems and canonical build/validate/plan
    acceptance. notes/review-harness-qa-c2.md.'
  - 'Original lowercase fail_first: six Write/Edit failures against dd04e52a executed
    in c1; notes/review-harness-qa-c1.md and notes/red-first-T-01.md. Not rerun in
    c2. Mixed-case RED is independent QA execution, not receipt transcription.'
  - Matrix unit rc=0 (63 files), integration rc=0 (91 files). Cap/sections/Done when
    retained. Only QA supplies runtime falsification; code/security are static lenses.
    Code measured c4c93ef1 ancestry and empty source/test delta to pin.
  - Operator PASS SC-01/04; code maintainer PASS SC-02/03. DEC-174/225/252/254 keep
    dispositions preserved; canonical Mode 2 skips landing grades for keep.
  - 'Assessed-and-dismissed: pre-existing DEC-252 commentary discrepancy outside T-01;
    prior dedicated-unit concern nonblocking because assigned integration evidence
    and registered unit gate ran. Canonical/unchanged-file controls are baseline-green,
    not refusal proof; exit/message assertions provide refusal evidence. Diagnostic-only
    mutation not separately executed; no additional requirement inferred.'
  - No surviving findings or disagreements; original c1 high correctness/low security
    ratings describe one closed defect without rewriting reader ratings. Five c2 notes
    recorded in complete run state. Zero send-backs; no source edits, test authoring,
    fixes hosted, commits, pinning or close-run actions.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c2.md: independent 12-failure mixed-case RED
      and 117-ok pin GREEN; original lowercase RED in notes/review-harness-qa-c1.md.
      Canonical acceptance and exact lowercase supersede guidance executed.'
  - id: SC-02
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c2.md: Write/Edit lowercase and mixed-case
      failing-then-passing assertions; cap/sections/Done when retained.'
  - id: SC-03
    verdict: met
    method: inspection
    evidence: "notes/review-harness-code-reviewer-c2.md: pinned gh-sync.py:2586\u2013\
      2590 correctly distinguishes preventive prerequisite and DEC-252 exemption."
  - id: SC-04
    verdict: met
    method: inspection
    evidence: "notes/review-harness-code-reviewer-c2.md: predicate/exemption :2594\u2013\
      2602 byte-identical to base; comment-only diff; specified FEAT-2225/FEAT-2229\
      \ historical notes untouched."
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/runs/2026-11-22-03-validate-c2-validator/digest.md
```
