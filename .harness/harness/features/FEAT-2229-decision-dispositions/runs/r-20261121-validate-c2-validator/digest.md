# FEAT-2229 — validate c2

**FAIL: QA is green, but SC-02 remains not_met; one medium T-01 substance fix is required.** Reviewed `dfa52536..a8b8df6196c6107b76cbd941bf2266b3e71476d6`. All five c2 notes exist; no source, plan or feature record was changed by this panel.

## One ranked must-fix

1. **F3 / SEC-C2-01 — substance / med / T-01 / SC-02**, raised by code-reviewer and security-reviewer, independently acceptance-graded by pm. At pinned `.claude/skills/harness/bin/plan_merge/check.py:279-320`, fence closure ignores the non-whitespace suffix: a literal three-backtick `python` content line ends an existing three-backtick `text` fence in the scanner, although Markdown keeps it open. A following example DEC heading can therefore precede and impersonate its real section. Require correct fence boundaries plus a discriminating CLI regression rejecting the spoof clause and accepting the genuine section. This is a **static counterexample, not executed**. Existing plain/nested-fence tests do not cover it.

**Reconciliation:** both specialist readers retain PASS with a medium advisory; neither severity nor kind is changed. Their one shared defect violates SC-02's explicit own-section guarantee, so pm's terminal reader perspective is partial and the lead gates on unmet acceptance, not on severity. One fix addresses both reports; no dependent task changes are requested.

## Evidence and dispositions

- QA `notes/review-harness-qa-c2.md`: unit 62 files and integration 89 files, both runner exits 0; signed T-01/T-02/T-03 verifies exit 0. SC-01/02/03/07 have reproduced natural-RED evidence at immutable base/pre-fix sources. F1 creation refusal/no-write, original F2 plain/nested-fence examples, and F-01 owner-scoped deletion assertion are red-then-green and **closed**, not silently dropped. QA verified c8a8e174-to-pin source equivalence but executed at the actual pin.
- `notes/review-harness-code-reviewer-c2.md`: Python grading passes; F3 is inspection-only. `notes/review-harness-security-reviewer-c2.md`: integrity boundary in scope; same static defect, no additional must-fix. No runtime falsification claimed for either lens.
- `notes/review-harness-ui-reviewer-c2.md`: measured 38 changed objects, no rendered UI; scoped-out PASS, not visual assurance.
- `notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c2.md` terminal correction: operator pass, reader partial, code maintainer pass; SC-01/03/04/05/06/07 met, SC-02 not_met, DEC-188 amendment met at pinned DECISIONS.md:5313-5336 (owner T-03). Original E-01 pending-QA assessment is preserved and **closed** after terminal QA collection; it is not an operator question.
- Settled LEAVE boundaries, simplify L-1..L-4 and B-1/B-2 remain assessed-and-dismissed as already ruled; no new scope class. Target integration runtime under full-suite load was 34s versus the task's 30s intent: advisory only, no acceptance override.

Five steps ran; one same-run pm evidence-completion send-back, so **cycles_used = 1**. No c1-pin reader rerun. Open questions: none. Only surviving coverage gap: no suffix-bearing fence-content regression. Lead verdict is FAIL despite green matrix; remediation belongs to T-01.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'a8b8df6196c6107b76cbd941bf2266b3e71476d6: QA green, but SC-02 fails on
    one medium T-01 fence-suffix defect; reader perspective partial.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Pinned unit/integration and signed verifies pass; automated SC fail-first
      reproduced.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Original F1/F2 repaired; medium T-01 F3 fence-closing advisory remains;
      Python grade passes.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: SEC-C2-01 reports the same medium T-01 fence-section identity defect.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 38 changed objects with no UI surface; Mode B scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Terminal QA closes E-01; SC-02 not_met, reader perspective partial;
      other SCs and DEC-188 met.
    files_touched: []
  must_fix:
  - '1. T-01 / SC-02 / substance / med / F3=SEC-C2-01 (code-reviewer, security-reviewer;
    acceptance confirmed by pm): correct fence-closing recognition at .claude/skills/harness/bin/plan_merge/check.py:279-320
    so a suffix-bearing content line cannot expose a fenced DEC heading as authority.
    Add an actual-CLI regression rejecting the spoof clause with a genuine-section
    positive control and fail-first evidence.'
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed range dfa52536..a8b8df6196c6107b76cbd941bf2266b3e71476d6. All five c2
    notes exist. QA independently verified c8a8e174-to-pin differences are only feature.json/plan.yaml
    and ran gates at the actual pin.
  - Deduplicated F3 and SEC-C2-01 into one T-01 defect. Preserve both readers' substance/med
    classifications and advisory PASS verdicts. Lead gates because literal SC-02 remains
    unmet, not because medium severity alone blocks.
  - QA full unit and integration runners discovered 62 and 89 files respectively;
    both exited 0. Signed T-01/T-02/T-03 verifies exited 0. Existing tests do not
    bind suffix-bearing fence-content behavior.
  - 'F1 creation validation/no-write and original F2 plain/nested-fence examples closed
    by QA red/green plus reviewer inspection. F-01 canonical Mode 2 assertion closed
    by owner-scoped mutation: old assertion green, new assertion red.'
  - One same-run pm evidence-completion send-back closed the original E-01 pending-QA
    timing gap; original assessment is preserved. Exact cycles_used is 1, not the
    panel number.
  - 'Terminal perspectives: operator pass, reader partial, code maintainer pass. DEC-188
    amendment landed; seven keep rows intentionally ungraded.'
  - Residual suffix counterexample is static source reasoning, not executed falsification.
    QA supplies runtime and mutation evidence for existing regressions; code/security
    supply inspection-only assurance for the residual.
  - Settled LEAVE boundaries, simplify L-1..L-4 and B-1/B-2 remain assessed-and-dismissed
    as already ruled. Full-suite targeted integration duration 34s versus task intent
    30s is advisory only.
  - No source fixes, commits, plan edits, feature edits, or c1-pin reader reruns.
    UI PASS means measured not-in-scope, not visual verification.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: a8b8df6196c6107b76cbd941bf2266b3e71476d6:tests/unit/test-decision-disposition-schema.py:71-180
      and tests/integration/test-plan-decision-dispositions.py:436-449; notes/review-harness-qa-c2.md
      records green 40/40 and 98/98, natural RED at dfa52536, creation refusal/no-file
      red-then-green.
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: a8b8df6196c6107b76cbd941bf2266b3e71476d6:.claude/skills/harness/bin/plan_merge/check.py:203,279-320,350-363;
      F3/SEC-C2-01 suffix-bearing fence-content static counterexample exposes a spoof
      DEC section. Existing CLI cases green per notes/review-harness-qa-c2.md; counterexample
      not executed. Owner T-01.
  - id: SC-03
    verdict: met
    method: automated
    evidence: a8b8df6196c6107b76cbd941bf2266b3e71476d6:tests/integration/test-plan-decision-dispositions.py:343-378,406-434,493-554;
      notes/review-harness-qa-c2.md records green boundary/provenance/legacy cases
      and natural RED at dfa52536.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: a8b8df6196c6107b76cbd941bf2266b3e71476d6:.claude/skills/harness/teams/plan.yaml:59-66,103-108;
      .claude/skills/harness/templates/plan.yaml:75-86; .claude/skills/harness/references/patch-lane.md:16-25;
      independently inspected by code reviewer and pm.
  - id: SC-05
    verdict: met
    method: inspection
    evidence: a8b8df6196c6107b76cbd941bf2266b3e71476d6:.omp/agents/harness-pm.md:58-82;
      .claude/skills/harness/teams/validate.yaml:115-121; .omp/agents/harness-validator-lead.md:100-105;
      per-row pinned evidence, keep skipping and owning-task failure preservation
      present.
  - id: SC-06
    verdict: met
    method: inspection
    evidence: a8b8df6196c6107b76cbd941bf2266b3e71476d6:.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326;
      DECISIONS-INDEX.md DEC-188/254; SPEC.md:2009-2043,2287-2302. QA index regeneration
      verify exits 0 with no diff.
  - id: SC-07
    verdict: met
    method: automated
    evidence: a8b8df6196c6107b76cbd941bf2266b3e71476d6:tests/integration/test-plan-team.py:424-509,
      especially :484-486,500-506; notes/review-harness-qa-c2.md records 184/184 green,
      natural RED at dfa52536, canonical successor-alternative mutation old-green/new-red.
  - id: DEC-188
    verdict: met
    method: inspection
    evidence: a8b8df6196c6107b76cbd941bf2266b3e71476d6:.harness/harness/docs/DECISIONS.md:5313-5336;
      decisions_affected[0] amendment replaces human-only enforcement with bounded
      drafting and pinned landing checks; successor D-01 resolves to DEC-254:8253;
      owner T-03.
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - 'T-01 / SC-02: existing fenced-heading regressions omit an info-string-bearing
    content line mistaken for a closing fence; residual counterexample is not runtime-tested.'
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer; security-reviewer; harness-pm
    summary: 'F3 / SEC-C2-01 / T-01 / SC-02: fence-closing recognition accepts a non-whitespace
      suffix and permits fenced DEC authority impersonation.'
    why: At a8b8df6196c6107b76cbd941bf2266b3e71476d6:.claude/skills/harness/bin/plan_merge/check.py:279-287,
      a three-backtick python content line closes an existing three-backtick text
      fence in the scanner although Markdown keeps it open. A subsequent fenced DEC-10
      heading and spoof clause are selected before genuine DEC-10 by :290-320 and
      accepted by :350-363. Static counterexample, not executed. Requires decision-document
      write access; retain medium severity. Explicit SC-02 own-section guarantee and
      reader perspective remain unmet, so this is one acceptance-blocking T-01 fix.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-validate-c2-validator/digest.md
```
