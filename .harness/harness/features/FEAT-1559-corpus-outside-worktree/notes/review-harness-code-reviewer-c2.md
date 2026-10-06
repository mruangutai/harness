# Code review — cycle 2

FAIL: original c1 defects closed; population silently drops distinct directories sharing a basename across segments (SC-04). Kind substance; scope none; severity high. Mechanical code grade grade_2; no high complexity records.

## Identity and evidence

Reviewed e8d868f78a6ec43880598af5c5873f5daa8ba985..42856abb91a3a87b9f27ebc933cc363a900afd3d; fix delta 0e8301a58a7de7dc23a067005c9aa8b3ee528de0..42856abb91a3a87b9f27ebc933cc363a900afd3d.

Control-plane pinned-checkout.py created /Users/molchairuangutai/GitHub/harness/.claude/worktrees/.pins/FEAT-1559-corpus-outside-worktree--validate-c1-validator--harness-code-reviewer. HEAD independently returned the full review SHA; initial porcelain empty. No clone fallback. Removed that exact pin using the control-plane helper (exit 0); subsequent .pins directory read showed only the QA sibling, no reviewer pin. No sibling touched.

Read BRIEF, plan decisions, fix receipt, runs/validate-validator/digest.md, c1 notes, non-regression receipt and appended erratum; independently inspected full source/test/document diff and changed-path list. Historical receipts are not current-pin suite executions.

Mandatory code-grade.py --base e8d868f78a6ec43880598af5c5873f5daa8ba985 --head 42856abb91a3a87b9f27ebc933cc363a900afd3d exited 0: 331 passing function records, 12 medium grade-2 records, no high records (artifact://1764). No general suites executed.

Read-only falsification: monkeypatched reached_feature_dirs to return harness/FEAT-7-shared and sample-product/FEAT-7-shared, then executed real population and real entry construction outside Git. Observed input_directory_names=2 output_entries=1, retaining only sample-product. No fixture/source/test files authored. Consumer failure consequences below are source-derived [INFERENCE], not executed gate tests.

## Stage 1 — specification

### Must-fix: directory census becomes incomplete population

SC-04, T-01/T-03. .claude/skills/harness/bin/feature_corpus.py:234 keys local entries by fid alone; :282 repeats that for landed records. The completeness census correctly distinguishes segment/id, but population erases the segment afterward.

Concrete state: tracked harness/FEAT-7-shared and sample-product/FEAT-7-shared both exist. Both pass landed_dirs; population silently returns only the lexically later segment. board_lifecycle.py:459 never audits the discarded directory. If its record alone owns feat/harness-only, merge-gate.py:206 cannot find it; if both records own one branch, that consumer sees one owner instead of two and bypasses multiple-owner refusal.

**Exact existing control path:** tests/unit/test-factory-claim.py, not tests/integration/test-factory-claim.py. Its shared builder at :337-391 creates both .harness/sample-product/features/FEAT-99-seg (:381-384) and .harness/harness/features/FEAT-99-seg (:386-389) beneath the SAME harness_root allocated at :343. They have different DAGs and issue maps. Case 5b at :1291-1346 uses both repositories in one fleet and asserts segment-specific claim/refusal results. This is a same-basename, two-segment corpus, not two isolated corpus roots. The fixture supports the validity of that identity shape; it does not itself prove tracked-owner completeness or population behavior. The independent falsification proves the dictionary collision; tracked-owner effects follow from the same basename key at :282.

Required fix: key local and landed population by segment/id (or equivalent full directory identity), replacing an owner's record only with the SAME checkout-local directory identity. Update affected callers and add a discriminating two-segment same-basename control. Do not reject valid cross-repository IDs or erase one as fallback.

Original c1 closure: check-plan-routes.py:799 calls require_landed before default walking; feature_corpus.py:253 checks actual landed names and produces N-of-M plus missing names. Explicit argv paths remain separate at check-plan-routes.py:2518-2526. Real CLI missing-owner/full-clone controls are test-feature-corpus.py:338,352. test-check-plan-routes.py:1540 now uses a Git-initialised fixture. These close the old default-plan defect, not population key loss.

Inspection: SC-11 — complete changed-path list contains no other feature's record changes. SC-14 — AGENTS.md:10 and .claude/skills/harness/SKILL.md:12 distinguish landed owner reads from checkout-local writes and prohibit sibling reads; .harness/README.md:50-139 documents repair and dirty refusal. SC-10 deferred by ruling #2101, not omitted. DEC-174/INV-17 exemptions, T-05 adopted code-final and QA G-1/G-4 rulings retained without new scope.

Stage 1 fails. General Stage-2 approval withheld. Mandatory mechanical grading below is independent of specification approval.

## Mechanical grading and c1 closures

All nine c1 high-grade failures no longer produce high records: check-instruction-paths._classify; feature_corpus.reached_feature_dirs, population, identity, claiming_segments, derive_cone; worktree-state.render; test-corpus-non-regression.manifest_findings; test-feature-corpus-census.glob_names. Small classifier delegation and extracted helpers preserve inspected call relationships; population retains the behavioral defect above.

Each following record is substance, scope none, medium, mechanically nonblocking. Metrics are cyclomatic/cognitive/ABC.

| Pinned function and line | Metrics | SC/task; bounded reason |
|---|---|---|
| check_state/corpus.py:preflight:102 | 15/14/30.6 | SC-03/04/09 T-02; ordered pre-Ctx refusal boundary |
| feature_corpus.py:verify_report_findings:327 | 15/7/23.2 | SC-09 T-03; closed fail-closed report parser |
| feature_corpus.py:select:565 | 10/12/32 | SC-01/13 T-01; classification/cone orchestration |
| worktree-state.py:divergent_paths:155 | 20/20/34.6 | SC-07 T-01; complete safety classification before mutation |
| worktree-state.py:diagnose:197 | 13/12/36.4 | SC-07 T-01; retains every diagnostic category |
| worktree-state.py:main:318 | 5/8/27.6 | SC-07 T-01; CLI/report orchestration |
| tests/integration/f58_sparse_fixture.py:snapshot:237 | 6/10/27.1 | SC-07 T-01/T-05; filesystem/index/config witness |
| tests/integration/test-feature-corpus-census.py:Resolver.components:60 | 19/25/26.7 | SC-04/13 T-03; closed AST path grammar |
| tests/integration/test-feature-corpus-census.py:statement_lines:116 | 7/18/9.4 | SC-04/13 T-03; marker/statement association |
| tests/integration/test-feature-corpus-census.py:detected_sites:139 | 12/18/26.9 | SC-04/13 T-03; aliases/site enumeration |
| tests/integration/test-feature-corpus-census.py:findings:176 | 8/19/15.6 | SC-04/13 T-03; scope vocabulary/owner seam |
| tests/unit/test-corpus-regression.py:tree_digest:47 | 11/10/25.8 | SC-02/13 T-05; deterministic non-mutation witness |

Unqualified production paths above are under .claude/skills/harness/bin/.

Human commits included without inherited approval: 29b1a7dbb28b, 61326cff2a78, c4f5fa82ed19, 13b72d560cbe, 2f50604fa796, 9ae5c0627bfb.

## Principles applied

Read model-the-domain.md: segment/id is actual identity, not basename. Read migrate-callers-then-delete.md: correct one population seam and migrate consumers, without compatibility population. Read delete-first.md: no extra provider hierarchy/fallback. Dev receipts have no actionable Principles-applied claim under settled direct-execution exemptions; absence is not a finding.
