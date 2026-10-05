# CODE review — FEAT-2081 — validate-c0

**FAIL: SC-01..08 compliance passes inspection/existing evidence; five mandatory production complexity gates fail. These block draft UAT becoming ready. SC-09/10 remain pending user UAT, not CODE failures.**

Pinned range: `e8d868f78a6ec43880598af5c5873f5daa8ba985..fc942ec4ebb0783f61e9809e3fc329b7f53be3e6`. Merge-base observed; feature.json agrees; tracked tree clean; full commit list feature-attributed; human commits none. No source edits or tests/build/lint/format runs. Prescribed pinned code-grade assessment executed, exit 1.

## Stage 1 — compliance (completed before grading)

| SC | Assessment and pinned pointer |
|---|---|
| SC-01 | PASS: runner `_partition`:171 descending duration/path, least-load/index ties; discovery independent of weights; unknown files default. Argument/empty-shard/partition red-first: evidence-T-01.md. Updated provenance approved by amendment 3. |
| SC-02 | PASS: check-integration-shards.py:98–111 requires exact success for both conclusions; evidence-T-02.md supplies each non-success rejection plus positive control. |
| SC-03 | PASS: validator :194–252 checks actual completion, exact multiset equality, duplicates, independently discovered tested git tree, nonempty expected suite. CLI fixture separates tested commit, HEAD and untracked corpus; evidence-T-02.md records independent mutants. |
| SC-04 | PASS: literal `git show fc942ec4:.github/workflows/tests.yml` inspected. Single non-matrix `integration`, no name override (:417), ubuntu-latest/needs both jobs (:418–419), job always (:424), validator always (:447). Four parallel ubuntu matrix shards, fail-fast false (:359–368). Trigger asymmetry (:19–22), concurrency/main no-cancel (:28–29) unchanged. Literal results/github.sha (:450–454); download failure remains red (:460–465). Whole-run cancellation excluded. |
| SC-05 | PASS: seven checks individually traced below; all original command bodies unchanged in pinned diff, no optional/continue-on-error gate. |
| SC-06 | PASS: invocation-local `_AuditSession` caches physical reads/index/errors; one BFS index and ordered subtree references; each public entry fresh. evidence-T-03.md/qa-structure-audit-equivalence.md record 53-input both-path equivalence, independent witnesses and red-first traversal. d89f9b23..fc942ec4 diff empty for audit implementation and both integration audit tests. Retained test-side parse cache approved; instrumentation does not install it. |
| SC-07 | PASS: unsharded unit globs and attributed pool/failure propagation retained; evidence-T-01.md supplies discovery/attribution/masked-failure mutants. |
| SC-08 | PASS: integration/all complete globs and actual futures retained; mutation verdict precedes manifest write; integration omission/failure mutants in evidence-T-01.md and retained structure fixtures. |

SC-05 chain for **each** gate: `checks` -> workflow needs :419 -> CHECKS_RESULT :450 -> validator exact-success :98. Unit suite :106; Validate feature execution state :115; Plan-route :165 (summary and examined>0); Canonical-reader :227 (summary and scanned>0); Instruction-path :245 (summary and explicit exit propagation); Layout :271 (summary, all three nonempty census counts and exit); Repository-state :337 (git-tracked feature>0 and checker exit). Default step failure prevents subsequent execution and checks success. No command semantics weakened.

T-05 SPEC §9.2 matches shipped sharding, weight default/provenance, actual completion, independent coverage and cancellation boundaries. No BRIEF/D-01 scope creep, omission or mismatch; all three amendments honored. Local performance evidence does not discharge live user UAT; draft explicitly records fixed-corpus timing gap.

## Stage 2 — ranked findings

These measured policy failures are **not observed runtime bugs**. Specific maintenance scenario: modifying the named CLI/validation/result logic requires following newly introduced or worsened below-bar control/data flow. Remedy is cohesive simplification to production grade >=4 while preserving errors/completion/mutation checks—not meaningless helper splitting.

| Kind / severity / owner | Pinned function | CC / cognitive / ABC; driver | Remedy |
|---|---|---|---|
| substance / high / T-02 | check-integration-shards.py:275 `_parse` | 10 / 10 / 17.0; CC+cognitive; grade 3 | Separate coherent argument validation from option collection. |
| substance / high / T-01 | run-unit-tests.py:97 `_tokens` | 6 / 11 / 12.3; cognitive; grade 3 | Flatten option handling, retain repeated/missing diagnostics. |
| substance / high / T-01 | run-unit-tests.py:126 `_parse` | 8 / 10 / 10.8; cognitive; grade 3 | Simplify constrained-option validation. |
| substance / high / T-01 | run-unit-tests.py:155 `_load_weights` | 10 / 10 / 23.8; all metrics; grade 3 | Cohesively organize document/weight validation. |
| substance / high / T-01 | run_pool.py:147 `main` | 7 / 5 / 21.8; ABC; grade 3 | Simplify result publication/verdict without weakening completion or mutation evidence. |

**substance / med / T-01,T-02,T-03:** seven grade-2 test functions, nonblocking; individual reasons:
- aggregation `manifest_cases`:142 and `coverage_cases`:164 each enumerate independent CLI defect witnesses; keep adjacent to their shared corpus.
- shard `case_manifest`:183 keeps one execution's complete identity and actual failing results together.
- shard `case_checked_in_document`:201 keeps independent provenance, positive-duration and median assertions on one document.
- unit validator `manifest_set_cases`:78 enumerates independent identity/shape defect cases.
- index `case_index_facts_match_ast_walk`:66 compares all buckets with an independent traversal.
- index `case_subtree_queries_match_ast_walk`:87 compares subtree ordering and literal/resource/symbol semantics on one corpus.
Splitting these assertion inventories would add indirection; accepted with those reasons. No behavioral fail-open defect found by inspection. Grader selector reports new/worsened records, not untouched inherited debt; aggregate code_grade is fail.

## UAT readiness / open questions

Open questions: none. **Ready is blocked by the five high records and outstanding final QA/main prerequisite receipts, not pending user UAT.** After fixes/new pin, refresh review and QA final evidence; populate draft's pin and inspection ledger. SC-09/10 still require user observation, fixed-corpus structure timing and three consecutive passing sub-100s live runs; no waiver or claim they are met.

## Principles applied

- Migrate Callers, Then Delete Legacy APIs: indexed callers replace old traversal helpers without compatibility shims; public audit contracts remain the seam.
- Delete First: require cohesive simplification of measured below-bar logic, not speculative abstraction or unrelated cleanup.
