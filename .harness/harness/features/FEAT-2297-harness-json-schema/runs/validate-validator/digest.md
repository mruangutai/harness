# FEAT-2297 validation — ESCALATE; not ship-ready

Pin `47d2e50243ad7fb080e13ef48115756d7d3b7c61`; measured merge-base `9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568` supersedes the supplied 837e7096 attribution. No product source edited.

## Ranked gate and routing
1. **High, substance, T-09 / SC-08 — operator decision.** All lenses agree: Kaya PR29 merged `b9dec8df`, with delegated advisor authorization; the UAT receipt explicitly disclaims operator-personal review. Authorization is established, literal personal acceptance is not. Main must obtain personal review/acceptance or an explicit signed amendment; this is not an unauthorized-merge accusation.
2. **High, substance, real-owner integration — Main owns ordering/disposition.** QA's production receipts report unit **65/65**, integration **94/95**. `test-corpus-real-owner.py` fails against installed owner v2; candidate and linked caller are v3. QA verified attribution, not a waiver or demonstrated green-after-upgrade. No task owns the external owner-state remedy. Do not weaken the test or edit the receipt.
3. **Medium, substance, T-01 / SC-01 D-03.** Code review's terminal-newline concern was independently reproduced by QA: both `github.repo="acme/repo\n"` and excluded-kind `signed="DEC-187\n"` are accepted. Fix whole-string validation and add rejection regressions through Main's DEC-174 path before schema sign-off.

## Retained nonblocking notes
- **Low, form, T-08:** change receipt cites nonexistent `receipts/t09-kaya.txt` and overstates operator review; point to `notes/uat-kaya-migration.md` and describe delegation honestly. Main was notified; validator has no authorship authority.
- **Low, form, T-10:** committed reduction measurement is historical. QA reran the scratch checker at the actual pin/base: Gate A **-583**, **152** rows disposed, **67** files assessed; new files **+1557**, total **+974**. Signed Gate A/B passes. PM withdrew its missing-current-measurement concern; stale committed record remains a form note, not a failed reduction gate.
- **Low, substance, T-01:** no named regression assertions for non-object config roots or missing/unparseable upgrade sources/no-write. QA probes show correct behavior today; keep as two coverage advisories, not invented implementation failures.

## Adequacy and dispositions
QA supplied fail-first evidence for all eight automated SCs; SC-05 uses present-state negative controls, explicitly not a natural pre-fix red. The canonical reader audit passed (101 files, zero unresolved) separately from suite discovery. Security found no exploitable regression by static inspection; UI correctly scoped out after a 163-object census. Code Stage 2 remains withheld because Stage 1 failed; mechanical Python grade passes, not complete code-quality clearance. Integration initially lacked node_modules; QA installed the prerequisite and reran, retaining the final red receipt. No unconditional green matrix claim is made.

Final PM: SC-02/04/05/06 met; SC-01/03/07/09/10 partial; SC-08 not_met. DEC-221 and DEC-254 disposition landings both met. All three perspectives remain partial. Signed D-01..D-08/amendments, INV-13 retirement and #2393 deferral are not findings. Runtime refusal on messaging a completed PM was repaired by fresh registered reconciliation; no capability blocker remains. One supplemental send-back, no source rework.

## Reader artifacts
Under this feature's `notes/`: `review-harness-qa-c1.md` (FAIL; includes measured probe supplement), `review-harness-code-reviewer-c1.md` (ESCALATE), `review-harness-security-reviewer-c1.md` (PASS), `review-harness-ui-reviewer-c1.md` (PASS, scoped out), `research-FEAT-2297-harness-json-schema-goalcheck-validate-c1.md` (final FAIL). QA manifests: `runs/validate-validator/qa/manifest-{unit,integration}.json`.

**Open questions:** Main must route SC-08 acceptance and the external-owner integration sequencing/disposition. ESCALATE preserves the operator decision above the otherwise failing technical gate; it is not clearance.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: '47d2e502 not ship-ready: personal Kaya acceptance unmet, integration
    94/95, and confirmed schema identifier defect.'
  open_questions:
  - id: OQ-ACCEPTANCE
    question: Will the operator personally review/accept Kaya PR29 or explicitly amend
      SC-08? Delegated authorization and landing are established; personal review
      is explicitly disclaimed.
    blocking: true
  - id: OQ-OWNER
    question: "How should Main resolve the integration failure against the installed\
      \ owner\u2019s v2 config? Attribution is verified; no waiver or task-owned external-state\
      \ remedy is inferred."
    blocking: true
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/notes/research-FEAT-2297-harness-json-schema-goalcheck-validate-c1.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: Unit 65/65; integration 94/95 with verified owner-v2 attribution; automated
      SC fail-first recorded.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: ESCALATE
    headline: Personal acceptance unproven; medium newline schema defect; Stage 2
      withheld.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No exploitable security regression found by pinned static review.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Scoped out after 163-object census; no implemented UI surface.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Reduction passes; personal acceptance, invalid-input acceptance and
      integration red prevent completion.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/notes/research-FEAT-2297-harness-json-schema-goalcheck-validate-c1.md
  must_fix:
  - 'T-09 / SC-08: obtain operator-personal review/acceptance or an explicit signed
    amendment; delegated authorization alone does not satisfy the literal criterion.'
  - 'Main: resolve test-corpus-real-owner.py integration red through authorized owner-state
    sequencing/disposition; preserve truthful runner evidence.'
  - 'T-01 / SC-01 D-03: reject terminal-newline repository and signed-DEC identifiers
    with whole-string validation and regression assertions.'
  branch: none
  escalations:
  - id: E-ACCEPTANCE
    raised_by: harness-pm, harness-code-reviewer, harness-qa, harness-security-reviewer
    question: Can delegated advisor review satisfy SC-08 despite explicit operator-personal
      wording?
    domain: acceptance and approved scope
    routed_to: Main
    resolution: Unresolved; literal criterion not_met. Authorization and merge are
      not disputed.
    decided_by: none
    recorded_as: runs/validate-validator/digest.md
  - id: E-OWNER
    raised_by: harness-qa
    question: Required integration fails against external real owner v2; no feature
      task owns that state remedy.
    domain: control-plane migration sequencing
    routed_to: Main
    resolution: Attribution verified, failure not waived; Main disposition required.
    decided_by: none
    recorded_as: runs/validate-validator/digest.md
  adequacy_notes:
  - Reviewed 47d2e50243ad7fb080e13ef48115756d7d3b7c61; measured merge-base 9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568
    supersedes supplied 837e7096 attribution.
  - matrix_ok=true means floor evaluation/mapping, not green suite. QA-owned manifests
    record unit runner_exit 0 and integration runner_exit 1.
  - Integration initially lacked node_modules; QA installed prerequisite and reran.
    Final receipt remains red; no unconditional PASS claimed.
  - "QA independently reproduced both newline cases. Code review\u2019s medium severity\
    \ retained; security\u2019s clean static result does not contradict a contract\
    \ defect."
  - 'Scratch reduction passes signed Gate A/B: existing -583; 152 rows disposed; 67
    files assessed; new +1557; reported total +974. PM withdrew missing-current-measurement
    concern; stale committed record remains form debt.'
  - All eight automated SCs have fail-first evidence. SC-05 uses present-state negative
    controls, not a natural pre-fix red.
  - Code Stage 2 withheld after Stage 1 failure; mechanical Python grade passes, not
    complete quality clearance. Security static-only; UI scoped out by actual census.
  - 'Low coverage gaps concern regression assurance: QA probes show root refusal and
    upgrade-source diagnosis currently work.'
  - 'Canonical reader audit passed separately: zero unresolved sites across 101 Python
    files, outside unit/integration discovery.'
  - 'Signed D-01..D-08 amendments, INV-13 retirement and #2393 deferral are settled.
    DEC-221 and DEC-254 amendments landed.'
  - Completed-PM messaging capability refusal repaired by fresh registered reconciliation;
    one supplemental send-back, no remaining runtime blocker.
  - All three goal perspectives partial. ESCALATE preserves acceptance decision above
    otherwise failing technical gate; not clearance.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated
    evidence: QA unit green/fail-first; confirmed terminal-newline acceptance and
      missing root-refusal assertion. notes/review-harness-qa-c1.md
  - id: SC-02
    verdict: met
    method: automated
    evidence: Reader refusal cases and fail-first pass; external owner red separately
      recorded. notes/review-harness-qa-c1.md
  - id: SC-03
    verdict: partial
    method: automated
    evidence: Upgrade/fail-first passes; missing/unparseable-source no-write assertions
      absent.
  - id: SC-04
    verdict: met
    method: automated
    evidence: Fixture suite passes; census reproduces five baseline bypasses.
  - id: SC-05
    verdict: met
    method: automated
    evidence: 'Scratch checker actual 47d2e502/9fd1f6b4: Gate A -583;152 rows;67 files;new
      +1557;total +974. Signed amendment governs.'
  - id: SC-06
    verdict: met
    method: automated
    evidence: Baseline wrong-route red; candidate zero unresolved across 101 Python
      files; GenericReads passes.
  - id: SC-07
    verdict: partial
    method: inspection
    evidence: Contract docs align; changes-config-contract.md cites absent receipts/t09-kaya.txt
      and overstates personal review.
  - id: SC-08
    verdict: not_met
    method: uat
    evidence: notes/uat-kaya-migration.md establishes PR29/b9dec8df landing/delegated
      authorization, explicitly not personal review.
  - id: SC-09
    verdict: partial
    method: automated
    evidence: Unit 65/65/fail-first; required integration qualified by owner failure.
  - id: SC-10
    verdict: partial
    method: automated
    evidence: Integration94/95; test-corpus-real-owner.py fails on installed owner
      v2, attribution verified not waived.
  - id: DEC-221
    verdict: met
    method: inspection
    evidence: "47d2e502:.harness/harness/docs/DECISIONS.md:7311\u20137315; amend D-08\
      \ landed."
  - id: DEC-254
    verdict: met
    method: inspection
    evidence: "47d2e502:.harness/harness/docs/DECISIONS.md:8357\u20138367; amend D-02\
      \ landed."
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'SC-01: no named non-object harness.json root rejection assertion; probes show
    correct refusal.'
  - 'SC-03: no missing/unparseable upgrade-source diagnosis/no-write regression assertion.'
  - Code quality Stage 2 unperformed because spec compliance did not clear.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-pm, harness-qa
    summary: 'T-09: SC-08 personal operator acceptance not established.'
    why: Pinned receipt explicitly documents delegated advisor review instead; landing
      and authorized merge cannot certify personal conduct.
  - kind: substance
    scope: none
    severity: high
    reader: harness-qa
    summary: Required integration red against installed real owner v2.
    why: Runner manifest94/95; test-corpus-real-owner.py refuses owner schema_version2.
      Attribution verified, not waived; external owner-state remedy unowned by feature
      tasks.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01: repository and DEC regexes admit terminal newlines.'
    why: QA measured github.repo="acme/repo\n" and excluded signed="DEC-187\n" accepted,
      confirming Python dollar-anchor behavior violates complete identifiers/no-whitespace
      contract.
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'T-08: change receipt links nonexistent Kaya evidence and overstates
      personal review.'
    why: changes-config-contract.md cites receipts/t09-kaya.txt; actual uat-kaya-migration.md
      describes delegation, not personal review. Main notified; validator cannot author
      repair.
  - kind: form
    scope: none
    severity: low
    reader: harness-qa, harness-pm
    summary: 'T-10: committed reduction measurement names historical review/base.'
    why: Current scratch measurement passes. Missing-current-measurement concern resolved;
      stale historical block must not masquerade as current pinned receipt.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01: non-object config-root refusal lacks named regression assertion.'
    why: SC-01 names it. QA probes show current correct refusal; nonblocking regression-assurance
      gap.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01: missing/unparseable upgrade-source diagnosis lacks regression
      assertions.'
    why: SC-03 requires diagnosis without fabricated replacement. Probes show current
      correct behavior; no named test preserves it.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/runs/validate-validator/digest.md
```
