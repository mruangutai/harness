# CODE review — FEAT-2081 — validate-c2

**PASS: all five high complexity blockers close; no helper regression or new gating risk found. No changed-code/spec blocker prevents UAT-ready.** Ordinary final pin/inspection/readiness receipts and the final QA gate remain required; SC-09/10 remain pending user UAT, not claims of acceptance.

Canonical range: `e8d868f78a6ec43880598af5c5873f5daa8ba985..f2791446c294abb5b26e6bcf663b25ee86b6dcce`; scoped delta: `fc942ec4ebb0783f61e9809e3fc329b7f53be3e6..f2791446c294abb5b26e6bcf663b25ee86b6dcce`. Tracked tree clean, merge-base agrees, full commit list feature-attributed, human commits none. Explicit dispatch pin governs this assessment; recorded feature.json still names fc942ec4 and Main must refresh final review_sha as already required.

## Stage 1 — delta compliance (before grading)

T-01/T-02 extraction preserves SC-01/02/03/07/08 and D-01: identical option acceptance/refusal conditions, diagnostic order, weight checks, completion publication and exit policy. T-06 removes Main waiver/discretion: `notes/uat.md:56,64,310` requires user-executed L-01 for SC-10, without requiring execution before ready. No scope creep, omission or mismatch.

SC-04/SC-05 inspection remains valid from cycle 1: literal pinned delta does not touch `.github/workflows/tests.yml`; retained pointers are sole aggregation :417, dependencies :419, always :424, exact checks-result :450; Unit :106, feature-state :115, plan-route :165, canonical-reader :227, instruction-path :245, layout :271, repository-state :337. No unrelated re-review.

## Stage 2 — measured closure and semantic inspection

Managed isolated pin used and removed. Prescribed `code-grade.py --base e8d868f78a6ec43880598af5c5873f5daa8ba985 --head f2791446c294abb5b26e6bcf663b25ee86b6dcce` exited 0: **135 passing**, zero high records; aggregate **code_grade: grade_2**, not `pass`, because seven accepted test exceptions remain. Supplementary static path grading supplies pool main (canonical selector omits it because it is no longer new/worsened versus base). No tests/builds/linters/formatters or mutations executed.

| Prior blocker / owner | Pinned location | CC / cognitive / ABC | Closure |
|---|---|---|---|
| `_tokens` / T-01 | run-unit-tests.py:110 | 2 / 1 / 4.1 | grade 5 |
| `_parse` / T-01 | run-unit-tests.py:138 | 3 / 2 / 4.4 | grade 5 |
| `_load_weights` / T-01 | run-unit-tests.py:179 | 1 / 0 / 4.5 | grade 5 |
| `main` / T-01 | run_pool.py:153 | 5 / 4 / 18.1 | grade 4 |
| `_parse` / T-02 | check-integration-shards.py:289 | 4 / 1 / 9.5 | grade 4 |

New helpers all pass: runner `_take_option` :97 grade 4, `_check_combinations` :130 grade 4, `_check_provenance` :164 grade 4, `_check_weights` :171 grade 4; pool `_record_completed` :147 grade 5; validator `_missing_options` :275 grade 5 and `_value_problems` :280 grade 4. No new/worsened below-bar function beyond the unchanged seven exceptions.

Helpers group coherent work, not pass-through wrappers: one token's consumption, cross-option constraints, document identity versus numeric contents, completed-result projection, missing fields versus malformed values. Local interfaces add no speculative adapter or duplicated validation. REASONED semantic closure: missing/repeated runner options and shard constraints keep identical predicates; object validation precedes dict access; positive finite nonboolean durations remain mandatory. Pool completion still derives from finished futures, then mutation verdict/summary/exits, then runner manifest publication; no selected-only synthetic success, reordered mutation guard, changed failure result or fail-open branch introduced. Validator option errors remain ordered unknown → missing → invalid, and result conclusions remain separately fail-closed.

## Retained nonblocking exceptions and assurance limits

Seven unchanged grade-2 tests retain their accepted individual reasons (substance/med, T-01/T-02/T-03): aggregation `manifest_cases` :142 and `coverage_cases` :164 keep independent CLI witnesses adjacent to one corpus; shard `case_manifest` :183 keeps execution identity/failing completions together; shard `case_checked_in_document` :201 keeps provenance/positive-duration/median assertions together; unit validator `manifest_set_cases` :78 keeps identity/shape cases together; index `case_index_facts_match_ast_walk` :66 keeps independent bucket comparison together; index `case_subtree_queries_match_ast_walk` :87 keeps ordering/literal/resource/symbol comparison together. Splitting inventories adds indirection. These are retained, not newly discovered blockers.

Cycle-1 SC-01..08 adjudications, fail-first receipts and evidence limitations stand. Preserve approved test-only parse cache, both existing audit entry paths/no check-state wiring, automated cancelled-result rejection without live per-job cancellation, and no workflow deletion-proof claim. Author-recorded mutant evidence is not independently re-proved here. Timing and live scheduling/context assurance remain user-only; lower same-corpus medians in both paths and three consecutive sub-100s Actions runs remain mandatory. Main fills final pin/current inspection/readiness ledger; QA alone runs its mandated final matrix at this pin.

Open questions: none.
