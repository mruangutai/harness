# Integrated upstream code review — FEAT-1928

**PASS with the original medium advisories; no new integration blocker and no ship authorization.** Independently derived canonical range is `91e8865346a7bf4e2b8a5bf2033b17f01f8d6b14..3c1923cf2475c1e976b5b941a5b5c7fc445f9e19`, not either obsolete af2/5a range. Seven human commits are enumerated below from the actual range (`artifact://742`, `artifact://789`). The only dirty tracked path observed was this feature's feature.json, in the allowed Harness ledger domain; no dirty source was observed.

## Stage 1 — specification first

Read approved BRIEF, signed decisions D-01–05 and prior final review before diff. Earlier build amendments remain empty (runs/simplify-eng/digest.md:130). Reviewed current-main→pin core diff and prior83746→pin merge delta (`artifact://780`, `artifact://758`). Incoming BUG1016 source/decision changes are upstream provenance, not undocumented feature additions against current main. SC-01–03 retain strict injection, schema-control refusal and object-only canonical validation (harness-hooks.ts:365–410,1190–1207,1268–1287); rooting never rewrites task/yield inputs. SC-06's approved historical 291 rows/exact14 deltas and three failed historical generator groups remain historical evidence, not regenerated or waived here. SC-07/D-03 preserves historical reads and authorized append, with the original mismatch below.

**SC-05 inspection:** notes/live-digest-object-probe-current.md:7–18 and transcript seq19–31 name clean executed c81, runtime identity, real native null rejection, same-job retry and valid completion. `c81→3c` changes exactly STATE.md, feature.json, code-risk-current.md and three receipt/transcript files: no executable, test, probe, schema, fixture, import or config changes (`artifact://742`). This independently establishes source equivalence; it is not a live run by this reader. Actual pinned receipt says **OMP18.6.1**, launcher sha256 `348d0987f05eab2f56b6f543933ca6bbb964d8d069cca9a55be3a5efffad041a`, release source `2a2c6dcbbb558c0f8145f67f28b3370984f2bf60` explicitly metadata provenance, rather than dispatch shorthand18.6.0. OpenAI-only native proof; two Anthropic STRINGnull17/18 failures remain failures. Canonical provider111PASS is prior evidence, not native Anthropic proof.

**SC-08 inspection:** harness-hooks.ts:1268–1287 positively uses digest_object, and :1456–1461 contains no digest fallback; live .omp/.claude/skills sweep found no retired last-assistant extractor/cache, YAML renderer, text digest parser, echo-shadow/hollow repair, PASSTHROUGH or DOCUMENTED_OPTIONAL implementation. DECISIONS-INDEX.md:231,234 retains DEC237 and incoming DEC251; full merged decision delta retains object-only policy and append-only DEC208. No generator was run.

## Stage 2 — integrated correctness and quality

- **Independent lifetimes remain correct:** openRun clears digestBinding AND featureRootCache (:994–1008); agent_end clears run readiness/cache ONLY (:1456–1461), without restoring SubagentStop/lastAssistantText fallback. Bound digest identity survives claim settlement for append but is cleared before a new run, preventing cross-run reuse.
- **Authorization precedes rooting:** ast_edit joins the mutation set, every target crosses the same pre/post domain decision; revised inputs and original post inputs root idempotently (:214–225,1106–1157,1425–1434). Resolver refusal/exception/multiline/relative output blocks, never guesses; success cache is run-keyed and cannot bypass readiness/authorization (:937–975). Bash remains unrevised except existing persona env, carries feature to pre/post policy, and uses feature-specific sweep stamps; ambiguous worktree keeps full sweep (check-domain.py:2624–2679). No new fail-open/silent-loss integration path found by source reasoning.
- **Tests merged, not amputated:** rooting tests :1232–1558 and object tests :1560–1698 remain within lifecycle describe; it closes :1698, and distinct schema describe starts :1701. Positive literal revised-input/refusal assertions accompany absence assertions; object tests call the registered hook. No tests/mutants executed here.
- **Former high containment remains resolved:** digest_destination.py:90–146 requires matching runtime/parent/feature, registered open run/grant/exact destination, and O_NOFOLLOW descriptor-relative traversal. Incoming lexical rooting does not bypass the validator-owned handle.
- **Original F2, med substance/task, SC-07 mismatch remains:** validate-digest.py:1851–1871 appends without checking fence state; digest_record.py:33–46 consumes an unfinished prose text fence. Existing prose ending in an unclosed triple-backtick text fence → valid append reports success → successor sees absent/stale mapping. REASONED, not reproduced; same unusual malformed-prose case, same severity, no must_fix.
- **All eleven original med substance/task grade-2 costs remain accepted:** authorized_destination; object probe _task_dispatch, _yields, _native_yield_started, run_live, verify, main; lifecycle probe run_live, receipt_header; check_refusal; _object_shape_violations. Independent OLD absolute grader over canonical base→exact pin exited0, **230 passing, eleven reason requirements, zero high** (`artifact://785`). Exact metrics match prior final review table; notes/code-risk-current.md's reasons apply unchanged. Ten T-02 and one T-01 costs are retained, not hidden by a mechanical pass.

## Principles applied

- Model the Domain: keep successful root-cache lifetime separate from trusted digest-binding lifetime; neither reset is redundant state.
- Migrate Callers, Then Delete Legacy APIs: historical disk mappings are a separate seam, not grounds to revive text live-return compatibility.

No source edits, build/lint/test/formatter/probe/receipt-verification runs. Only explicitly authorized metadata grading executed. Main/QA own final verification; this bounded review adds no new check requirement. Required artifact only written; open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Integrated upstream preserves both contracts; original medium fence advisory and eleven justified grade-2 costs remain."
  severity_max: med
  findings:
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-02 F2 persists: unclosed prose fence hides a successfully appended mapping.", why: "validate-digest.py:1851 and digest_record.py:33; malformed prose yields stale or absent successor record; original med retained."}
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-02 retains ten named grade-2 maintainability costs with sufficient reasons.", why: "Independent exact-pin artifact://785 reproduces all ten original gated functions and costs; reason applicability unchanged."}
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-01 _object_shape_violations grades 2; closed-object conjunction reason accepted.", why: "tests/unit/test-digest-schemas.py:146; CC12/COG21/ABC24.2; weakening conjunction loses open/null contract detection."}
  must_fix: []
  spec_violations:
    - {kind: mismatch, path: .claude/skills/harness/bin/validate-digest.py, ref: SC-07}
  code_grade: grade_2
  reviewed: 91e8865346a7bf4e2b8a5bf2033b17f01f8d6b14..3c1923cf2475c1e976b5b941a5b5c7fc445f9e19
  human_commits_in_scope: [3c1923cf2475c1e976b5b941a5b5c7fc445f9e19, c81a57b6c7d62a63b52614e4bcb64a07f7d9fa47, 9e910a4ee31a9c9ce2c3a3e08b2f8ddf4c48e250, 10a9594cae75d241185ecde8745762ec7cd3e5a5, 828b3605d6334b96a6d21bfc8f93140b6b26a9c2, 4379809b1ce7e37e89407b2ade7912abc898fed9, 27ea22063047a4ea1776eef05a64e05d0a6417b1]
  grade_2_reasons:
    - "digest_destination.py::authorized_destination keeps exact runtime, checkout, registered-run and destination proof together; dropping a conjunct authorizes another run."
    - "probe-digest-object-contract.py::_task_dispatch preserves correlation of authored and executed task frames; wrong pairing misattributes strict schema."
    - "probe-digest-object-contract.py::_yields pairs yield calls and results within the same child; wrong pairing falsely accepts rejected null."
    - "probe-digest-object-contract.py::_native_yield_started binds job, event phase, tool and call identity together; weakening it mislabels hook-only refusal native."
    - "probe-digest-object-contract.py::run_live owns one RPC session lifecycle and cleanup; splitting lifetime can leak resources."
    - "probe-digest-object-contract.py::verify keeps transcript, runtime, Harness and outcome refusal checks explicit; omission permits unsupported receipts."
    - "probe-digest-object-contract.py::main keeps dry/verify/live modes and exit statuses visibly distinct; conflation mislabels synthetic proof."
    - "probe-inflight-claim-lifecycle.py::run_live shares mandatory resource, claim and run-record cleanup; separation can release the wrong claim."
    - "probe-inflight-claim-lifecycle.py::receipt_header keeps launcher identity separate from release metadata provenance; conflation misidentifies executed runtime."
    - "test-digest-dev-skill.py::check_refusal binds concrete refusal, canonical schema and instruction ownership; constants alone do not bind guidance."
    - "test-digest-schemas.py::_object_shape_violations expresses the full closed/required/no-null invariant; weakening it admits open or nullable contracts."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-code-reviewer-upstream.md
```
