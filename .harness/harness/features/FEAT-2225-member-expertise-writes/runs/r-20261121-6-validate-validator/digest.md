# FEAT-2225 validate — BLOCKED; substantive gates independently FAIL

**Pin `130592528844321c27fbb628fdc05f6f17f86d0d`, base `594af2a8`. Three distinct must-fixes; severity_max high.** QA recorded green matrix execution but could not submit an accepted digest after one form-only recovery. BLOCKED outranks the source FAILs; it does not dismiss them. Five readers, one source panel; no second review/goal-check/gate execution. Form corrections consume no rework cycles: cycles_used 0.

## Ranked must-fix set / F1 ruling

1. **F1 — substance; T-04; code high, security/PM/QA med (ratings preserved).** `.omp/extensions/harness-hooks.ts:1146-1198` and `.claude/skills/harness/bin/dispatch-guard.py:827-833`: a valid child of an ordinary registered run can carry the distill marker and apply its own Expertise plus receipt. **Real, not compensated.** Own-file grants bound security impact, explaining security's med; code's high records violation of the explicit pre-write SC-03 authority boundary. Maximum remains high, not an averaged rating. Yield refusal is late; empty reports and integrity-only replay do not prove distill authority. Bind permission to registered distill authority, preserving legitimate orchestrator distillation. Add marker/non-distill-run refusal tests in T-04 host/dispatch tests. No exploit execution claimed: all readers source-traced this scenario.
2. **F2 — high/substance; T-01 + T-04; code.** `.claude/skills/harness/bin/expertise-merge.py:1462-1470,1540-1552` and `.claude/skills/harness/bin/validate-digest.py:2250-2269`: after receipted P-01 add, removing unrelated pre-existing G-01 leaves verification green because only recorded keys are compared. Verify complete authorized resulting content during live and durable close; preserve ordered/superseded semantics. Merge-time blob reconstruction catches this later, not at required close. Lead inspected this exact seam; source-derived, not executed. This qualifies PM's SC-02 met/orchestrator-pass judgment: their named tests cover changed recorded targets, not this unrelated-key scenario. Preserve PM's grades as the single goal-check; **panel does not accept SC-02 closure**.
3. **F3 (PM F2) — med/substance; T-04; PM.** `tests/integration/test-member-expertise.py:162-215` and `tests/unit/omp-hooks.test.ts:1840-1984`: representative flows call the core directly; host uses canned core receipts; repository flows only add. Supply SC-01 representative real host-to-core application/receipt proof for craft/repository add/replace/drop. Author clarified original noncanonical “verification” kind to substance, without changing grades or findings. Lead confirmed representative CLI seam. Address shared regression harness after F1/F2 to avoid duplicated test work; preserve all 16 config/grant assertions and five representative classes.

T-03/T-04 are main-session-direct (DEC-174); **no squad dev owns T-04 remediation**. T-01 core remediation has the backend owner. These are existing-task defects, not new scope questions. PM's F1/F2 questions are resolved as routing classification, retained here rather than escalated as operator scope choices.

## Reader blocks — artifacts under feature directory

- **qa — BLOCKED (contract violation), observed matrix green.** `notes/review-harness-qa-c1.md`: unit 61 files/1129 PASS lines, integration 88 files/2922 PASS lines, both configured runners exit 0 under `env -u HARNESS_AGENT_TYPE`; T-01/T-02/T-04 verifies also exit 0. Unit's four captured FAIL tokens are a passing mutation fixture, not suite failures. Both original and single form-only recovery exhausted six rejected yields; no accepted QA receipt. Transcripts: `history://Feat2225Validate3.PermanentKingfisher.PetitePanda` and `.BizarreBlackbird`. Recovery even shows a wrapped data attempt refused; reported via `xd://report_issue`. No rerun used to conceal it.
- **code — FAIL/high.** `notes/review-harness-code-reviewer-c1.md`: F1/F2, spec stage fails; quality stage intentionally not started. Existing 414/0 code-grade evidence is not a completed stage-2 review.
- **security — FAIL/med.** `notes/review-harness-security-reviewer-c1.md`: independent F1, bounded own-file impact, no additional concrete defect. Its clean receipt-surface assessment is bounded by code's specific unrelated-key counterexample, not a rebuttal to it.
- **ui — PASS/not in scope.** `notes/review-harness-ui-reviewer-c1.md`: measured 74 changed files; no UI surface.
- **goalcheck — FAIL.** `notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c1.md`: operator partial, orchestrator pass, code maintainer fail; grades preserved, with panel SC-02 qualification above. One classification-only clarification; no second grading.

## Matrix, fail-first and adequacy

**matrix_ok: true as observed execution, NOT an accepted QA handoff.** cross_module T-01/T-04 requires unit+integration; docs T-02/T-03 adds none. QA's per-kind table reports both satisfied, nonzero discovery, exact commands/exits. No typecheck success claimed (null runner). Credentialled probe was already recorded: `notes/probe-handoff-comprehension-2026-11-21.md`, as-written 4/4, stripped 0/4; not rerun.

| Automated SC | Covering test and pre-fix failure evidence |
|---|---|
| SC-01 | host/member/core tests; `notes/red-first-T-04-host.md` 9 failures; T-01 receipt records 63 integration/12 unit failures. 16-config 28-failure claim is receipt-only, not retained capture. |
| SC-02 | digest leaf/lead/supersession and schema tests; `notes/red-first-T-04-digest.md` 22 digest/2 schema failures. Does not cover F2 unrelated-key deletion. |
| SC-03 | host/guard/digest/core boundaries; host 9, `notes/red-first-T-04-guard.md` 51, digest note dispatch 16 failures. No marker-on-non-distill-run regression (F1). |
| SC-04 | replay/collision/supersession tests; `notes/receipt-harness-backend-dev-T-01-c1.md` records 63 integration/12 unit failures and 17 mutants; raw red logs `/tmp/t01/red-{int,unit}.txt` remain volatile. |
| SC-05 | merge-gate/Main hook; `notes/red-first-t04-merge-gate.md` 23 failures, then green. |

QA G1/G2 evidence-durability notes remain coverage qualifications, not new canonical findings or silent waivers: receipt lines satisfy recorded-red form, but volatile/uncaptured logs weaken replayability. QA's blocked reproduction attempt is not falsification evidence. Green matrix is adequate for existing cases only, not F1/F2/F3 acceptance. Only QA executed tests; code/security/PM reasoned from pin; UI measured scope. No reader executed the F1/F2 counterexamples.

## Goal-check SC status (verbatim verdicts; qualifications explicit)

SC-01 **partial** (representative composition gap); SC-02 **met** (PM's tested subset; panel rejects closure due F2); SC-03 **not_met** (F1); SC-04 **met** (replay evidence); SC-05 **met** (merge evidence); SC-06 **met** (pinned inspection of SPEC/skills/personas, DEC-86 strike/DEC-253, five corrections, unchanged DEC-18/145/199/219 and index). Detailed methods/pointers are in goalcheck and QA notes.

## Open question / blocker

**QA-RETURN:** How should the orchestrator recover an accepted persona-bound QA receipt when the original and one form-only recovery were both refused by the yield interface? Recommendation: repair/route the return-contract failure and recover existing execution evidence, **not a second panel or gate run over this SHA**. The source must-fixes remain independently gating. No source, tests, product guidance, or Expertise was edited by this panel.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: 'Pin 130592528844321c27fbb628fdc05f6f17f86d0d: three substantive must-fixes;
    observed matrix green, QA return contract blocked after one form-only recovery.'
  open_questions:
  - id: QA-RETURN
    question: 'Original QA and one form-only recovery both exhausted rejected yields,
      including a wrapped-data attempt. Recommendation: resolve the return-interface
      failure and recover an accepted persona-bound receipt from existing notes/review-harness-qa-c1.md
      evidence, not a second panel or gate run over this SHA.'
    blocking: true
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c1.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: BLOCKED
    headline: Required matrix observed green; no accepted QA return after original
      and one form-only recovery.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Stage 1 fails: non-distill application and incomplete whole-file close
      verification; both high/substance.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: 'F1 real and med/substance: own-file limits impact but downstream integrity
      gates do not authorize application.'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 74 changed files at pin; no UI surface, correctly scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator partial, orchestrator pass, code maintainer fail; SC-01 partial
      and SC-03 not_met. Classification-only clarification preserves grades.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c1.md
  must_fix:
  - "F1 / T-04 \u2014 .omp/extensions/harness-hooks.ts and .claude/skills/harness/bin/dispatch-guard.py:\
    \ require registered distill authority before application, preserving legitimate\
    \ orchestrator authority; add marker/non-distill-run refusal regressions in tests/unit/omp-hooks.test.ts\
    \ and tests/integration/test-dispatch-guard.py. Main-session-direct, no squad\
    \ dev."
  - "F2 / T-01 + T-04 \u2014 .claude/skills/harness/bin/expertise-merge.py and .claude/skills/harness/bin/validate-digest.py:\
    \ verify complete authorized resulting destination content at live yield and durable\
    \ close, rejecting unrelated unreceipted edits while preserving ordered/superseded\
    \ batches. T-01 backend; T-04 Main."
  - "F3 / T-04 \u2014 tests/integration/test-member-expertise.py and tests/unit/omp-hooks.test.ts:\
    \ supply representative real host-to-core application/receipt coverage for craft\
    \ and repository add/replace/drop, preserving all-16 configuration assertions\
    \ and capability-class representatives. Main-session-direct."
  branch: none
  escalations:
  - id: GOALCHECK-ROUTING
    raised_by: harness-pm
    question: Are PM F1/F2 operator scope questions or existing-task fixes, and what
      is F2's canonical kind?
    domain: validation finding classification
    routed_to: harness-pm
    resolution: Author clarified F2 med/substance and both issues in-scope T-04 fixes.
      F1 deduplicated with code/security; PM F2 becomes consolidated F3. No goal re-grade
      or user scope decision.
    decided_by: harness-pm
    recorded_as: notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c1.md
  adequacy_notes:
  - Reviewed exact SHA 130592528844321c27fbb628fdc05f6f17f86d0d against 594af2a8.
    Five original readers; subsequent QA/PM dispatches repaired return form/classification
    only, without another review, test execution or goal grading. cycles_used 0.
  - 'F1 explicitly real and not compensated. Code high and security/PM/QA med are
    preserved: own-file impact explains security''s med; code rates the explicit pre-write
    authority violation high. severity_max remains high; no reader rating rewritten.'
  - QA artifact records configured unit runner exit 0 over 61 files/1129 PASS lines
    and integration exit 0 over 88 files/2922 PASS lines, under env -u HARNESS_AGENT_TYPE.
    T-01/T-02/T-04 verifies also exit 0. matrix_ok true describes observed execution,
    not accepted QA receipt.
  - 'Fail-first: SC-01 host red note 9 failures plus T-01 receipt; SC-02 red-first-T-04-digest.md
    22 digest/2 schema failures; SC-03 host/guard/digest red notes 9/51/16 failures;
    SC-04 T-01 receipt 63 integration/12 unit failures and mutants; SC-05 red-first-t04-merge-gate.md
    23 failures. Covering tests and paths in run digest/QA artifact.'
  - 'PM SC-02 met and orchestrator pass remain the sole goal-check grades, but panel
    rejects closure: code''s unrelated-key deletion counterexample is outside their
    tested subset. Whole-file verification is not established by recorded-key checks
    or later merge-time blob comparison.'
  - Code spec stage failed; stage-2 quality review did not run. Existing 414 PASS/0
    FAIL grading is not stage-2 clearance. F1/F2 counterexamples are source-derived,
    not executed exploits. Security's general receipt assessment does not rebut code's
    specific F2.
  - 'Credentialled probe cited, not rerun: notes/probe-handoff-comprehension-2026-11-21.md,
    as-written 4/4, stripped 0/4. Null typecheck remains disclosed, not passed.'
  - 'QA G1/G2 remain evidence-durability qualifications: 16-persona red is receipt-only;
    T-01 raw red logs volatile under /tmp/t01. Receipt lines provide recorded-red
    evidence, not durable raw captures. QA''s refused reproduction is not falsification
    evidence.'
  - No shipped source, tests, guidance or Expertise changed. PM file touch is classification-only
    in required artifact. QA yield inconsistency reported via xd://report_issue. Required
    artifact contains per-reader blocks, ranked F1/F2/F3 and fail-first table.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated / integration
    evidence: 'PM: all-16 tool/Write/grant checks and five core representatives exist,
      but test-member-expertise.py:162-215 calls core directly; omp-hooks.test.ts
      uses canned receipts. F3 leaves real host-to-core proof incomplete.'
  - id: SC-02
    verdict: met
    method: automated / integration
    evidence: 'PM grade preserved: digest leaf/lead/supersession groups and red-first-T-04-digest.md
      establish tested refusals. Panel qualification: F2 shows unrelated unreceipted
      deletion passes live/durable close; acceptance not cleared.'
  - id: SC-03
    verdict: not_met
    method: automated / integration; pinned counterexample inspection
    evidence: 'F1: marker-only host permission plus dispatch preflight skipping ordinary
      registered runs violates non-distill-cannot-apply. Other boundary reds omit
      this mismatch; F2 adds close-integrity gap.'
  - id: SC-04
    verdict: met
    method: automated / integration
    evidence: 'PM: test-expertise-merge.py replay/collision/independent-caller/changed-main/cap/supersession;
      T-01 receipt records pre-change failures and mutants; simplify evidence retains
      behavior.'
  - id: SC-05
    verdict: met
    method: automated / integration
    evidence: 'PM: test-merge-gate.py FEAT-2225 and Main routing; red-first-t04-merge-gate.md
      records 23 initial failures then 65 ok/0 FAIL, including DEC-220 and stale/refused
      evidence.'
  - id: SC-06
    verdict: met
    method: inspection
    evidence: 'PM/code pinned git show/diff: SPEC, procedure, skills and 16 personas
      consistent; DEC-86 struck to DEC-253, five corrections, DEC-18/145/199/219 unchanged,
      index/live references corrected.'
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'T-04: marker/non-distill-run write refusal lacks regression (F1).'
  - 'T-01/T-04: no unrelated unreceipted deletion regression for live/durable close
    (F2).'
  - 'T-04: representative host-to-real-core proof and repository replace/drop incomplete
    (F3).'
  - QA execution recorded but native return never passed; one form-only recovery also
    failed.
  - T-04 16-persona red capture receipt-only; T-01 raw reds /tmp-local. No new red
    reproduction claimed.
  - Static TypeScript typecheck has no configured runner; no success claimed.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; security-reviewer; pm; qa
    summary: 'F1 / T-04: marker-only authority permits Expertise application under
      a non-distill registered run.'
    why: Host harness-hooks.ts:1146-1198 trusts prose; dispatch-guard.py:827-833 skips
      preflight without bound distill run. Independent source tracing shows ordinary-run
      child writes own Expertise and receipt. Late yield/replay do not enforce pre-write
      authority. Original code high and security/PM/QA med retained; high is panel
      maximum.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'F2 / T-01 + T-04: receipt verification misses unrelated unreceipted
      edits during live and durable close.'
    why: expertise-merge.py:1462-1470,1540-1552 compares active-op keys only; validate-digest.py:2250-2269
      trusts success. Receipted P-01 add plus unrelated G-01 deletion can close successfully.
      Merge catches it later. Lead inspected seam; source-derived, not executed.
  - kind: substance
    scope: none
    severity: med
    reader: pm
    summary: 'F3 / T-04: representative tests omit actual host-to-core application
      across both tiers/all verbs.'
    why: test-member-expertise.py:162-215 invokes CLI directly and repository only
      adds; omp-hooks.test.ts:1840-1984 mocks receipts. PM clarified original F2 kind
      to substance without re-grading; SC-01 remains partial.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-6-validate-validator/digest.md
```
