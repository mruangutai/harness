```yaml
VERDICT: PASS
DIGEST:
  headline: "83746a425d692f2096f53d343594f1ee9ed8890c passes final validation; medium fence advisory and eleven accepted grade-2 costs remain nonblocking."
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
    - {step: qa, persona: qa, verdict: PASS, headline: "120-file pool binds the pin; literal SC-06 291/14/zero-unplanned and all automated SC RED evidence established.", files_touched: []}
    - {step: code, persona: code-reviewer, verdict: PASS, headline: "Containment high closed; medium unfinished fence and eleven reasoned grade-2 costs retained at the mandated range.", files_touched: []}
    - {step: security, persona: security-reviewer, verdict: PASS, headline: "Prior high unauthorized-append finding closed at the pin; no actionable residual security finding.", files_touched: []}
    - {step: ui, persona: ui-reviewer, verdict: PASS, headline: "High contrast finding closed; low stale-host wording and source-only accessibility limits retained.", files_touched: []}
    - {step: goalcheck, persona: pm, verdict: PASS, headline: "All eight approved SCs and four perspectives pass; not ship authorization.", files_touched: []}
  severity_max: med
  matrix_ok: true
  findings:
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-02 F2: an unfinished prose fence hides a successfully appended mapping.", why: "review-harness-code-reviewer-final.md Stage 2: validate-digest.py:1851 and digest_record.py:33 can leave a successor stale or without a mapping. Original severity retained; no must_fix under advisory_unless_high. Remedy before adjacent append changes: refuse without changing bytes or verify the appended object is the selected mapping."}
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-02 retains ten accepted grade-2 maintainability costs, not ten behavior failures.", why: "review-harness-code-reviewer-final.md eleven-row table and artifact://641: authorized_destination; digest-object probe _task_dispatch, _yields, _native_yield_started, run_live, verify, main; lifecycle probe run_live, receipt_header; test-digest-dev-skill check_refusal. Preserve authorization, correlation, lifecycle and provenance predicates; written reasons accepted, no cosmetic split demanded."}
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-01 _object_shape_violations grades 2; its closed-object conjunction reason is accepted.", why: "review-harness-code-reviewer-final.md: tests/unit/test-digest-schemas.py:146 CC12/COG21/ABC24.2. Weakening closed/required/no-null conjunction loses contract detection. This is the eleventh accepted cost, not a new gate failure."}
    - {kind: substance, scope: task, severity: low, reader: qa, summary: "T-02 F1: native terminal-null delegation lacks a CI-resident unit case.", why: "review-harness-qa-final.md F1: harness-hooks.ts:1160 is exercised by the successful live native probe, not a unit input with type=result/data=null. Add that pass-through case alongside the existing nonterminal-null refusal if addressed; SC-04 evidence is present, so advisory only."}
    - {kind: form, scope: task, severity: low, reader: qa, summary: "T-02 F2: agent prose enum legends have no schema-drift guard.", why: "review-harness-qa-final.md F2: three reviewer legends match today, but deleted severity/documented-contract groups have only a partial successor. Pin legends to canonical enums; no current mismatch or regression established."}
    - {kind: form, scope: task, severity: low, reader: ui-reviewer, summary: "T-02 F-UI-02: specialist field rules still attribute rejection to SubagentStop.", why: "review-harness-ui-reviewer-final.md: .claude/skills/harness-digest-dev/SKILL.md:80 contradicts current OMP object-gate attribution. Documentation only; no enforcement failure or re-gate claimed."}
  must_fix: []
  coverage_gaps:
    - "QA F1: terminal-null native-delegation branch has live coverage, not a CI unit regression guard."
    - "QA F2: prose enum legends match now but lack a drift guard."
  sc_status:
    - {id: SC-01, verdict: met}
    - {id: SC-02, verdict: met}
    - {id: SC-03, verdict: met}
    - {id: SC-04, verdict: met}
    - {id: SC-05, verdict: met}
    - {id: SC-06, verdict: met}
    - {id: SC-07, verdict: met}
    - {id: SC-08, verdict: met}
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/runs/validate-final-validator/state.yaml
  branch: none
  open_questions:
    - {id: code-Q1, question: "Reader's exact reviewed range remains af2a958ab06c0d6fc026b363b59fc3147e3982f1..83746a425d692f2096f53d343594f1ee9ed8890c; current origin/main merge-base is 5a2657371d5641a3022a800947c7c9ab0f863164. Legacy mechanical checks derive a different range. Main owns any required range-binding reconciliation; exact non-repin repair is below, and no metrics for the other range are asserted.", blocking: false}
    - {id: code-Q2, question: "Code reviewer reports check-domain misclassified agent:// coordination as an agent:/ filesystem path; owner repair is outside this feature. No claim of independent lead reproduction.", blocking: false}
    - {id: qa-Q1, question: "QA notes handoff_comprehension runner_note requests a live run before a handoff-contract ship, while its detect surface is untouched and the rule does not require one here. Does the operator want that additional advisory run?", blocking: false}
    - {id: qa-Q2, question: "Native raw-null proof is OpenAI-only; both Anthropic string-null attempts remain 17/18 failures. SC-04 does not require Anthropic live proof; wider proof, if desired, is separate from the two low guard recommendations already retained.", blocking: false}
    - {id: qa-Q3, question: "QA's locally_run results are in its durable report rather than kinds[] because the legacy independent rerunner accepts only unit/integration/all. inflight_claim_lifecycle_live 28/28 and digest_object_contract_live 18/18 plus verification 33/33 are recorded; owner should reconcile this transport/policy mismatch without relabeling them as CI runs.", blocking: false}
  escalations: []
  expertise_update: []
  adequacy_notes:
    - "QA bound 46 unit plus 74 integration files to the pin through the six metadata/evidence-only changes from clean executed 98b6c383; no source/test equivalence is merely assumed. This assessment executed no checks and reopened no reader."
    - "Literal SC-06 is met: all 291 retained rows compared, exact 14 approved deltas, 277 unchanged, no null new outcome and zero unplanned. All three unsuccessful historical groups remain failures; two contributed zero rows and T-08's three explicit fixture replays reject on both sides. Not a claim of successful generator groups or a new pin-time parity capture."
    - "Automated SC-01/02/03/04/06/07 have retained RED evidence. Final SC-03 module-absence RED is not an assertion mutation; historical QA c3 separately records thirteen constructed schema assertion failures and a failing whitelist. Current owning suites are green. Native SC-04 has actual 17/18 RED, then 18/18 live success and QA's independent 33/33 receipt verification."
    - "PM's SC-07 met judgement covers owning append/idempotency/correction/refusal and historical-reader evidence, not every malformed prose state. Code F2 remains a real SC-07 mismatch and constrains this PASS; no reviewer kind/severity was revised or defect dismissed."
    - "Security/code containment and UI contrast highs are closed, not downgraded. UI ratios 7.204:1 light and 7.788:1 dark are source/luminance calculations, not rendered accessibility proof; layout, size and keyboard-overflow access remain human/UAT limitations. Inherited loud hook-guard fail-open policy is not newly closed."
    - "All five original readers returned PASS, must_fix is empty and severity_max is med under control-plane advisory_unless_high. Transport/schema recovery incurred no source rework or send-back: cycles_used=0 under DEC-157. Ledger run-end and any ship/merge authorization remain Main's responsibility."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/runs/validate-final-validator/digest.md
```

## Assessment and evidence pointers

**PASS with the six ranked advisory groups above; not a blanket SC-07, browser-accessibility, multi-provider live-proof or ship all-clear.** All five reports and canonical original returns were read. Relative note pointers resolve under this feature's `notes/`. Each original report is checkpointed by its absolute path in `state.yaml`. No new source, test, grader, probe or reader wave ran in this recovery.

SC-06 is accepted on the literal approved BRIEF, not a waiver: QA independently re-derived both 291-row files and fixture inventory, exact approved row set, zero unplanned outcomes, and permanent boundary RED/current-green evidence. PM independently agrees. The object comparison's earlier source identity satisfies the required pre-parser-deletion chronology; permanent tests bind the final implementation. `validator-parity.md:169-189` distinguishes duplicate-key P0000's syntax counterpart from the fourteen changed row verdicts. `parity-group-error-disclosure.md` and QA's final SC-06 section preserve the three unsuccessful groups rather than converting exceptions into successes.

The genuine disagreement is adequacy breadth, not severity: PM says SC-07 met while code retains a concrete unfinished-prose-fence mismatch. I preserve both, rank the silent/stale-record hazard ahead of accepted maintainability costs, and qualify PASS under the repository's advisory-unless-high rule. Security's authorization closure does not repair that parsing-state hazard. QA's native-null CI gap is distinct from successful live null evidence, and its enum drift guard is distinct from UI's actual stale host wording; none are duplicates. Remedy order if Main elects advisory work: append-record hazard first, then native-null CI regression guard, then independent documentation/drift corrections; do not split justified grade-2 proofs merely to improve a score. This follows PRINCIPLES headings “Verification is the product” and “Never falsify the record.”

## Legacy range-binding: exact repair boundary

The measured code-review result is `grade_2`, 230 functions meeting bars and eleven accepted grade-2 requirements on **af2a958..83746a42 only** (`review-harness-code-reviewer-final.md`, `artifact://641`). No canonical-range totals are fabricated. The OLD control-plane `validate-digest.py:1729-1768` binds only the reported range's head to the pin; it does not require rewriting the reported base. Its `:1000-1027,1198-1244,1097-1117` independently derives mechanical grade, reason coverage and human-commit census from `origin/HEAD`'s merge-base. Our lead contract carries neither `code_grade` nor `reviewed`; no replacement base is needed for this lead return. The original code reader's canonical return already reached PASS.

If a subsequent legacy mechanical check refuses the code report, Main's exact repair is to measure the canonical mechanical-only range in the target worktree with the control-plane grader:

`python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base 5a2657371d5641a3022a800947c7c9ab0f863164 --head 83746a425d692f2096f53d343594f1ee9ed8890c --json`

Then measure `[harness:human]` commits over that same canonical range and reconcile only the mechanically checked grade, required function reasons and human-commit set to actual outputs, explicitly labeling that provenance separately. Keep the independently reviewed **af2a958..83746a42** range, original eleven exact-range cost records, review pin and failure history unchanged. Do not move origin refs, falsify the reviewed base, substitute unmeasured counts, or redispatch the five readers. Any refusal remains a disclosed mechanical record repair, not an invented source-rework cycle.
