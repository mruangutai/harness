# Final independent code review — FEAT-1928

**PASS with medium advisories; not ship clearance.** The former high containment finding is resolved at the exact pin. The original medium unfinished-fence finding remains unchanged and nonblocking. Independent mechanical result is **grade_2**, not `pass`.

## Scope and evidence

Reviewed `af2a958ab06c0d6fc026b363b59fc3147e3982f1..83746a425d692f2096f53d343594f1ee9ed8890c`; feature.json:5 agrees with the dispatch pin. Git status emitted no changes before review. Full commit inventory and 692-path inventory: `artifact://596`, `artifact://617`; core pinned diff: `artifact://607`; supporting diff: `artifact://648`. No tests/builds/linters/formatters/probes/mutations ran. Correctness scenarios below are **REASONED**, not measured reproductions. The explicitly requested control-plane grader was the sole executed code-quality check (`artifact://641`, exit 0): 230 functions meet their bars, eleven grade-2 requirements, no high records. Reasons in notes/code-risk-current.md match all eleven exact qualified functions; its earlier totals are historical.

The clean executed `98b6c38332bf270f4c88dbc89d7b9d044c7b858d` differs from the review pin only in STATE.md, feature.json, plan.yaml, code-risk-current.md, current live receipt and current transcript (`artifact://617`). No executable, assertion, schema, import or fixture changed. This independently binds that run's source to this pin; it does not claim this reader executed the run. Current origin/main merge-base is **5a2657371d5641a3022a800947c7c9ab0f863164**, not the mandated base; the requested range is preserved, never repinned. Retirement commits 69568c5a/d25ece38 and FEAT-495 bookkeeping are merged-main provenance, not invented digest-contract tasks.

## Stage 1 — SC-01–08 / decisions

Read BRIEF and plan decisions before the diff. Build simplify-eng/digest.md:130 has `amendments: []`; signed plan reconciliation allocates DEC-237 instead of occupied DEC-236 and adds final proof T-05. No blocking specification departure found; SC-07 has the retained medium limitation below.

- **SC-01 / D-02:** harness-hooks.ts:309-340,1078-1088 refuses authored controls at top level and every batch item, injects persona-specific strict bundles before claims, and does not exempt Main from schema policy.
- **SC-02 / D-01:** harness-hooks.ts:1153-1177 consumes the object itself; malformed nonterminal values receive the object instruction. Null/absent terminal `type: result` is deliberately delegated to native strict YieldTool, not accepted as a digest. Eight persona definitions and three shared skills cut over to object examples; historical YAML remains a disk format.
- **SC-03 / D-02:** sixteen persona schemas plus common.json; digest_schema.py:84-139 validates canonical files directly. digest-schema.ts:113-280 resolves contained references, detects cycles, refuses unsupported projection, derives structural bundles, then freezes/caches by root and persona for extension lifetime (:293-315). Provider suites recorded at notes/verification-current.md:30-36 are 111/0/221 across four suites; that upstream source SHA is not installed runtime identity.
- **SC-04 / D-04:** actual transcript seq19 has bare JSON null and type=result; seq20 begins native yield execution; seq21 rejects it; seq26–31 accepts the following object and completes the SAME job. Probe predicates at probe-digest-object-contract.py:618-661 require native execution, schema rejection, same-child retry and structured valid completion. Historical hook-only proof is not substituted; native-red receipt records the earlier 17/18 failure.
- **SC-05 inspection / T-05:** notes/live-digest-object-probe-current.md:7-18 names clean Harness98b6, installed omp18.6.0, launcher/hash, separate release-tag metadata provenance, actual OpenAI Main/child identities, invocation, null/refusal/retry/completion/exit0 and transcript hash. Seq19–31 substantiate behavior, and the six-file diff binds source to review83746. Anthropic STRINGnull attempts remain failures, not native-null successes.
- **SC-06 / T-02:** immutable baseline/object results and P0000–P0290 fixtures retain the approved 291-case comparison and fourteen explicitly enumerated deltas (validator-parity.md:169-189), without regeneration or waiver. object-results.json:3-18 records THREE unsuccessful historical groups; parity-group-error-disclosure.md explicitly discloses them. Do not claim those groups ran successfully. This is historical pre-deletion comparison, not a fresh current-pin parity execution; final regression evidence is separately recorded by main/QA.
- **SC-07 / D-03:** digest_record.py:33-76 selects the last safely loaded fenced mapping without live validation or writes. check_state/ctx.py:512, run_state.py:234-310 and plan_merge/panel.py:408-430 consume that mapping; record-amendments shares _lead_digest. Writer authorization and correction/idempotency cases bind actual hook calls (test-validate-digest.py:1548-1699). Retained F2 below remains.
- **SC-08 inspection / T-02,T-03:** pinned core diff deletes text extraction/parser, TS rendering, last-assistant fallback, echo-shadow and hollow repair, PASSTHROUGH/DOCUMENTED_OPTIONAL tables; live-tree sweep found none of those digest implementations under .omp or .claude/skills. Positive replacements: harness-hooks.ts:1165-1177, validate-digest.py:1110-1132 and DECISIONS.md:7753-7824 (DEC-237). Four obsolete decision headings are removed; historical references remain historical. DEC-208's append-only ruling is retained rather than rewritten into a live compatibility route.

## Stage 2 — correctness and quality

**c3 F1, high substance, T-02: resolved, not downgraded.** digest_destination.py:90-146 now requires exact runtime/parent/feature binding, one open registered run and domain grant, exact registered destination, and descriptor-relative O_NOFOLLOW on every parent and final component. The former relative parent-symlink escape cannot reach the target handle. Tests :1620-1699 check relative/absolute parent escape and cross-run/squad/feature refusal, victim bytes and selected mapping. No inherited high finding is carried without rederivation.

**F2, original med substance/task, T-02 (cross_module, main-session-direct; execution_agent absent), SC-07 mismatch: still present.** validate-digest.py:1851-1871 appends without checking fence state; digest_record.py:33-46 remains inside an unclosed text fence. A lead's existing human prose ending in an unclosed triple-backtick text fence → valid correction is written and reported successful → new YAML opener/body belongs to that text fence, so successor reads no mapping or the stale earlier mapping. Source changed destination authorization, not this behavior. Narrow recommendation: refuse byte-unchanged or establish that the actual last mapping equals the submitted object while preserving old bytes. This is the same unusual malformed-prose state and same medium severity, never promoted by repetition; no must_fix under advisory-unless-high policy.

**Eleven mechanical med substance/task findings, nonblocking.** CC/COG/ABC below are independently observed; each row is a separate named maintainability cost with its written behavioral reason accepted, not an assertion of broken behavior. All T-02 except schema walker T-01; both main-session-direct, execution_agent absent. Retain correlation and refusal predicates, not artificial one-use helpers.

| Path:function | CC/COG/ABC; driver | Reason / concrete regression to preserve |
|---|---|---|
| bin/digest_destination.py:90 authorized_destination | 10/11/29.7; ABC | Keep runtime identity, checkout, open-run and exact destination as one authorization proof; dropping a conjunct authorizes another run. |
| tests/manual/probe-digest-object-contract.py:400 _task_dispatch | 16/7/25.4; CC | Correlate authored/executed task and result; wrong pairing attributes strict schema to the wrong dispatch. |
| same:416 _yields | 13/19/28.7; all | Pair calls/results in one child session; wrong pairing falsely accepts a rejected null. |
| same:541 _native_yield_started | 13/8/20.6; CC | Require event/job/phase/tool/call identity together; weaker matching calls hook-only refusal native. |
| same:687 run_live | 4/4/26.4; ABC | One RPC session owns request/event pump/cleanup; splitting lifetime can leak the process. |
| same:903 verify | 11/10/30.0; CC+ABC | Keep transcript/runtime/Harness/outcome checks explicit; omission permits unsupported receipts. |
| same:926 main | 9/13/35.9; ABC | Keep dry/verify/live routing and exit status together; conflation mislabels synthetic proof. |
| tests/manual/probe-inflight-claim-lifecycle.py:553 run_live | 8/15/33.1; ABC | Session, sentinel claim and run record share mandatory finally cleanup; separation can leak or release wrong claims. |
| same:594 receipt_header | 5/9/35.6; ABC | Assemble provenance coherently; conflating release source and launcher misidentifies executed runtime. |
| tests/unit/test-digest-dev-skill.py:115 check_refusal | 6/4/30.7; ABC | Concrete refusal/schema/ownership guidance share one invariant; constants alone fail to bind actual instructions. |
| tests/unit/test-digest-schemas.py:146 _object_shape_violations | 12/21/24.2; CC+COG | One closed/required/no-null conjunction over actual schemas; weakening a clause admits open or nullable contracts. |

No extra gated derive or panel-refusal finding: derive now grade3 meets its test bar; panel helper improved versus base and is not gated. Eleven matching reasons are in notes/code-risk-current.md:25-58. Existing hook_guard loud fail-open and non-governed/stop-active handling are retained baseline policy, not misrepresented as new unconditional fail-closed enforcement. Schema projection fails dispatch closed; authorized file-opening errors refuse before append. Historical reader fallback over an invalid fenced block is explicit D-03 behavior, not a live yield repair.

## Principles applied

- Model the Domain: one schema authority and distinct historical record module replace scattered text assumptions.
- Migrate Callers, Then Delete Legacy APIs: live callers migrate without old text shims; historical disk consumption is a different contract, not compatibility transport.
- Delete First: retired parser/renderer/fixture paths are actually removed rather than wrapped.

## Open questions / handoff

Q1 nonblocking: control-plane legacy validator recomputes current merge-base5a265737, while this assignment mandates af2a958; recommend main explicitly reconcile range-binding before routing this exact-range digest, without repinning. Q2 nonblocking: check-domain refused my permitted agent:// lead coordination message as agent:/ filesystem path; no workaround attempted. Main/QA own end-phase gates; no new suite rerun by this reader. Only this namespaced review artifact was written.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Final object cutover passes blocking code gates; retained medium fence advisory and eleven justified grade-2 costs."
  severity_max: med
  findings:
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-02 F2 persists: unclosed prose fence hides a successfully appended mapping.", why: "validate-digest.py:1851 and digest_record.py:33; malformed prose yields stale or absent successor record; original med retained."}
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-02 has ten named grade-2 maintainability costs with sufficient reasons.", why: "Independent artifact://641 and eleven-row table above bind each gated function and preserved behavior; ten belong to T-02."}
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-01 _object_shape_violations grades 2; closed-object conjunction reason accepted.", why: "tests/unit/test-digest-schemas.py:146; CC12/COG21/ABC24.2; weakening conjunction loses open/null contract detection."}
  must_fix: []
  spec_violations:
    - {kind: mismatch, path: .claude/skills/harness/bin/validate-digest.py, ref: SC-07}
  code_grade: grade_2
  reviewed: af2a958ab06c0d6fc026b363b59fc3147e3982f1..83746a425d692f2096f53d343594f1ee9ed8890c
  human_commits_in_scope: [27ea22063047a4ea1776eef05a64e05d0a6417b1, 4379809b1ce7e37e89407b2ade7912abc898fed9, 828b3605d6334b96a6d21bfc8f93140b6b26a9c2, 10a9594cae75d241185ecde8745762ec7cd3e5a5]
  grade_2_reasons:
    - "digest_destination.py::authorized_destination keeps exact runtime, checkout, registered-run and destination proof together."
    - "probe-digest-object-contract.py::_task_dispatch preserves correlation of authored and executed task frames."
    - "probe-digest-object-contract.py::_yields pairs yield calls and results within the same child."
    - "probe-digest-object-contract.py::_native_yield_started binds job, event phase, tool and call identity together."
    - "probe-digest-object-contract.py::run_live owns one RPC session lifecycle and cleanup."
    - "probe-digest-object-contract.py::verify keeps transcript, runtime, Harness and outcome refusal checks explicit."
    - "probe-digest-object-contract.py::main keeps dry/verify/live modes and exit statuses visibly distinct."
    - "probe-inflight-claim-lifecycle.py::run_live shares mandatory resource, claim and run-record cleanup."
    - "probe-inflight-claim-lifecycle.py::receipt_header keeps launcher identity separate from release metadata provenance."
    - "test-digest-dev-skill.py::check_refusal binds concrete refusal, canonical schema and instruction ownership."
    - "test-digest-schemas.py::_object_shape_violations expresses the full closed/required/no-null invariant."
  open_questions:
    - {id: Q1, question: "Current merge-base is 5a265737 but mandated review base is af2a958; reconcile legacy digest range-binding without repinning.", blocking: false}
    - {id: Q2, question: "check-domain rejects agent:// coordination as a filesystem path; recommend owner repair outside this feature.", blocking: false}
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-code-reviewer-final.md
```
