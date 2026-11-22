# Validate c5 — BLOCKED, not ship-cleared

Pin: c163d5ea0fb17da27b3455559f317d67852981c7; base dfa52536. **SC-02 is met, but required security-owned actual-CLI acceptance could not execute.** No observed production defect or product must_fix. This is a capability escalation, not another dev round.

## Gate evidence and reader verdicts
- QA PASS — independently reproduced M6 both directions red 128/130, each direction 129/130; M8 129/130; pre-fix identifier matcher 122/130. Restored pin 130/130. Actual-CLI mutation-tier fail_first, not a natural pre-fix checkout. T-01 literal verify exits 0 (unit 40/40, integration 130/130); configured runners exit 0 across 62 unit and 89 integration files. ../../notes/review-harness-qa-c5.md.
- Code PASS — required code-grade base dfa52536/head c163d5ea exits 0, 101 passing function records; lookahead correct by inspection. Measured branch-tip difference is feature.json only. ../../notes/review-harness-code-reviewer-c5.md.
- Security BLOCKED — SEC-C4-01 statically addressed; zero of 107 planned CLI observations executed. bash-write-guard refused temporary-fixture Python writes. Refusal confirmed in reviewer history; role grants Bash for git diff, not an override. QA's successful spoof mutation cannot stand in for this required lens's format/CRLF controls. ../../notes/review-harness-security-reviewer-c5.md.
- UI PASS — own measured 57-path census, no visual surface; independent decline, not visual approval. ../../notes/review-harness-ui-reviewer-c5.md.
- PM PASS after same-run correction — QA fan-in discharges its initial partial/FAIL evidence hold. All seven SCs and DEC-188 met; SC-01/03–07 and DEC-188 explicitly retain c4 judgments because delta does not change their subjects. ../../notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c5.md.

## One ranked set, no product must_fix
1. Blocking question SEC-C5-EXEC: establish an authorized execution path for the security reviewer's actual-CLI identifier/format controls at this same pin. Do not claim closure or bypass the guard. No additional source remediation is justified by the refusal.
2. Low substance advisory, QA, T-01/SC-02: tilde closer-length assertion gap; X2/X5/X6 survive 130/130 and are live in scanner probes.
3. Low substance advisory, QA, T-01/SC-02: tilde closer-with-info assertion gap; X3 survives 130/130 and is live. These are two unique gaps, not four defects. Outside the authorized M6/M8 repair; not gating.
4. Retain security's two low substance historical Unicode/list-container advisories as operator-backlogged, not re-derived or promoted. C4-QA-CONTRACT, SIMPLIFY B-1/B-2 and create:true remain backlog; not reopened.

No severity/kind changed by lead; QA corrected its noncanonical labels to substance/low. Two same-run receipt send-backs (QA classification; PM evidence fan-in), zero source-fix cycles. PM's unclaimed peer-revival correction failed; a governed task corrected the durable note. All hosted work is terminal. Open questions: SEC-C5-EXEC only. severity_max low; matrix_ok true; needs_approval true for execution-path resolution. BLOCKED rolls up the security receipt despite the four PASS verdicts.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: 'c163d5ea: SC-02 met, M6/M8 killed and required checks green; security-owned
    CLI acceptance remains guard-blocked.'
  open_questions:
  - id: SEC-C5-EXEC
    question: Establish an authorized execution path for the security reviewer's actual-CLI
      identifier and format controls at c163d5ea; its temporary-fixture command was
      guard-refused before any observation. No additional product fix is established.
    blocking: true
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 2
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: M6 both directions, M8 and identifier spoof killed; verify and runners
      green; two low advisory coverage gaps.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Full-identifier lookahead correct by inspection; code-grade exits 0
      with 101 passing records.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: BLOCKED
    headline: SEC-C4-01 statically addressed; guard refused actual-CLI probes, zero
      observations executed.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Independent decline: measured 57 changed paths, no visual UI surface.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 'Corrected goalcheck: all seven SCs and DEC-188 met; separate security
      runtime acceptance undetermined.'
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - Security BLOCKED governs roll-up despite four PASS verdicts. This is an execution-capability
    blocker, not an observed product failure or another dev round.
  - 'QA independently reproduced actual-CLI mutation reds: M6 both directions 128/130,
    each separately 129/130; M8 129/130; pre-fix identifier matcher 122/130. Restored
    pin 130/130. Evidence is mutation-tier, not natural pre-fix checkout execution.'
  - 'T-01 literal verify exits 0: unit 40/40 and integration 130/130. Configured runners
    exit 0 over 62 unit and 89 integration files. Code-grade --base dfa52536 --head
    c163d5ea exits 0, 101 passing records.'
  - Security's zero executed CLI observations cannot be replaced by adjacent QA evidence.
    Its refusal is confirmed in history; reviewer Bash grant is limited to git diff.
  - 'Two same-run receipt corrections counted: QA finding classification and PM incorporation
    of completed QA evidence. PM''s unclaimed revival was resolved with a governed
    task and corrected durable note; no production fix dispatched.'
  - All unchanged SCs and DEC-188 retain c4 judgments with explicit delta relevance
    in PM's note. Operator-backlogged issues are not reopened. No prior-pin rereview,
    new pin, push, PR or merge.
  - Finding scope normalized to none for substance per live contract; T-01 ownership
    remains explicit. All five readers ran; UI independently declined visual scope.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: Retained c4 QA unit/schema and fail-first evidence; c163d5ea changes
      no schema/writer paths. PM goalcheck c5.
  - id: SC-02
    verdict: met
    method: automated
    evidence: c163d5ea0fb17da27b3455559f317d67852981c7; notes/review-harness-qa-c5.md:5-23
      independently reproduces M6/M8 and identifier fail-first with actual CLI and
      green controls; corrected PM goalcheck c5.
  - id: SC-03
    verdict: met
    method: automated
    evidence: Retained c4 QA era/provenance evidence; c163d5ea changes no eligibility/creation/provenance
      behavior. PM goalcheck c5.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: Retained c4 PM authoring/scope instruction inspection; no c163d5ea instruction
      delta. PM goalcheck c5.
  - id: SC-05
    verdict: met
    method: inspection
    evidence: Retained c4 PM pinned-grading/delegation/failure-routing inspection;
      no c163d5ea contract delta. PM goalcheck c5.
  - id: SC-06
    verdict: met
    method: inspection
    evidence: 'Retained c4: 46d0c4bce7cec18e0aabec56a490981496970cc0:.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326;
      c163d5ea changes no authority/index/SPEC subject. PM goalcheck c5.'
  - id: SC-07
    verdict: met
    method: automated
    evidence: Retained c4 QA team-regression green/base-red evidence; c163d5ea changes
      no canonical prompt or test-plan-team.py obligation. PM goalcheck c5.
  - id: DEC-188
    verdict: met
    method: inspection
    evidence: 'Retained c4: 46d0c4bce7cec18e0aabec56a490981496970cc0:.harness/harness/docs/DECISIONS.md:5313-5336;
      successor DEC-254:8253-8326; decisions_affected[0], owner T-03. No c163d5ea
      amendment delta.'
  needs_approval: true
  severity_max: low
  matrix_ok: true
  coverage_gaps:
  - Required security-owned actual-CLI identifier/format controls did not execute;
    static inspection is not runtime acceptance.
  - 'Advisory T-01/SC-02: tilde closer-length assertions absent; live X2/X5/X6 survive
    130/130.'
  - 'Advisory T-01/SC-02: tilde closer-with-info assertion absent; live X3 survives
    130/130.'
  findings:
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: T-01 / SC-02 advisory tilde closer-length regression gap.
    why: Live X2/X5/X6 survive 130/130; backtick equivalent covered. Outside authorized
      M6/M8 set, backlog not must_fix.
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: T-01 / SC-02 advisory tilde closer-with-info regression gap.
    why: Live X3 survives 130/130; backtick equivalent covered. Outside authorized
      M6/M8 set, backlog not must_fix.
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: T-01 / SC-02 retained Unicode whitespace/line-break advisory.
    why: Operator expressly backlogged; historical evidence retained without re-audit
      or promotion to must_fix.
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: T-01 / SC-02 retained list-container phantom-fence advisory.
    why: Operator expressly backlogged; historical evidence retained without re-audit
      or promotion to must_fix.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261122-validate-c5-validator/digest.md
```
