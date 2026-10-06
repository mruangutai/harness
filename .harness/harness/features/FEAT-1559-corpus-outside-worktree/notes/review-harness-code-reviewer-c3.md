# Code review — c3

PASS with bounded medium advisories; no must-fix. The c2 directory-identity defect is closed. Stage 1 correspondence/inspection completed before the previously deferred Stage 2 general code-quality review. Mechanical code grade remains grade_2 (12 retained records, no high records).

Reviewed e8d868f78a6ec43880598af5c5873f5daa8ba985..6c11ab626ed568236978b1640928162b8cf0139f. Fix delta: 42856abb91a3a87b9f27ebc933cc363a900afd3d..6c11ab626ed568236978b1640928162b8cf0139f. Independent merge-base(origin/main, pin) is the stated baseline. Read BRIEF, plan decisions, feature.json, prior aggregate and reviewer digests, fix receipts, non-regression receipt/erratum; inspected complete source/test/document diffs and changed-path inventory, including human changes without inherited approval. No source/test/fixture edits or full-suite executions. Current feature.json's Harness-record modification is not an unpinnable source edit; cycles_used=2 denotes main-session fix rounds, not reader sendbacks.

## Stage 1 — specification and inspection

The `(segment,id)` key is used in both population maps; checkout-local entries override only the same pair. Sorting is `(id,segment)`. Consumers retain their documented entry shape. The context's separate active-id exclusion is guarded by pre-context duplicate-segment refusal; no second provider or sibling lookup introduced. Prior six c1 closures remain bounded by the earlier evidence and inspected current code.

SC-11 inspection: complete baseline-to-pin path inventory contains no other feature-directory change; notes/non-regression-receipt.md:7-46 freezes code-final/pre-change endpoints and manifest bytes, and :104-120 corrects 54/86 output-line counts to 52/80 files. Its historical claims are not current-pin suite executions, and the current fix changes production after that receipt.

SC-14 inspection: AGENTS.md:10, .claude/skills/harness/SKILL.md:12, .claude/skills/harness-verification-rules/SKILL.md and .harness/README.md:50-139 distinguish local active writes from absolute landed owner reads, prohibit sibling providers, and explain repair/verify, dirty skips and clone hooksPath limitations. The harness-simplify source-note pointer also now names the control-plane root.

SC-10 is deferred-by-ruling to #2101, T-06 abandoned, not omitted. DEC-174/INV-17 direct-execution exemptions, SC-13 historical fail-first limitation, and QA G-1 advisory/G-4 inconclusive are retained; none is a new must-fix.

## Exercised current-pin evidence

Managed exact-SHA pin: .claude/worktrees/.pins/FEAT-1559-corpus-outside-worktree--validate-c2-validator--harness-code-reviewer. Created and removed only with the control-plane pinned-checkout.py helper. No clone fallback, no sibling checkout mutation.

- `python3 -B tests/integration/test-feature-corpus.py SegmentIdentity MergeGate.test_one_id_claimed_from_two_segments_is_two_owners_and_denies BoardStatus.test_one_id_active_in_two_segments_is_audited_in_both`: four tests, 2.428s, OK, exit 0. These exercise both population modes, pair-local override, permissionDecision denial and both board cards.
- Read-only in-memory id-only `_directory_key` mutant: SegmentIdentity.test_a_shared_id_is_two_entries_from_a_worktree_and_from_a_clone fails because harness/FEAT-2-beta disappears; mutant_rejected=True. No source bytes changed.
- Control-plane `code-grade.py --base e8d868f78a6ec43880598af5c5873f5daa8ba985 --head 6c11ab626ed568236978b1640928162b8cf0139f`: 338 passing function records, 12 medium grade-2 records, no high records (artifact://1848).

## Stage 2 — general quality: new bounded advisories

Both findings are substance, scope none, native severity med; neither adds a must-fix. They describe unlikely boundary states, not a claim that ordinary owner audits or gates now fail.

1. **T-02 / SC-04: structural Git errors are mistaken for unborn HEAD.** check_state/corpus.py:128-131 catches every CorpusError from tracked_dirs and returns a preflight with no refusal. tracked_dirs already treats genuinely unborn HEAD as empty. In a real disposable plain fixture, injecting `CorpusError("git ls-tree failed: corrupt tree object")` produced refusal=[], notes=[], keep=None, just like the healthy control. Thus a census query failure skips name-set completeness rather than refusing before context/invariants. A subsequent selected runner probe returned exit 1 for the fixture's unrelated INV-32/INV-43 era fields; **no end-to-end false-green result was observed**. Narrow the catch to legitimate unborn state or propagate a named structural refusal. Native medium because it needs a Git structural/query failure, and other downstream checks may independently deny.

2. **T-01/T-02 / SC-05: historical exemption erases claimant multiplicity.** feature_corpus.py:431 looks up `frozenset(ids)`. Concrete pure-function probe: historical FEAT-02 and FEAT-03-subissue-mirror plus a third directory in another segment also named FEAT-02, all on feat/harness-native-foundation, yielded claims=['FEAT-02','FEAT-02','FEAT-03-subissue-mirror'] but collisions=[]. A distinct-id third claimant correctly collided. Directory identity is now preserved by population, but exemption matching still collapses it. Require the exact two claimant entries, not just their unique basename set. Native medium: restricted to duplication of this historical pair across segments; the merge gate's independent multiple-owner denial remains intact.

## Retained mechanical findings

All rows: substance, scope none, native severity med; accepted retention reasons, not new blockers. Metrics are cyclomatic/cognitive/ABC. Production paths are under .claude/skills/harness/bin/.

| Function:line | Metrics | Task/criterion and retention reason |
|---|---|---|
| check_state/corpus.py:preflight:102 | 15/14/30.6 | T-02 SC-03/04/09; ordered pre-Ctx refusal boundary |
| feature_corpus.py:verify_report_findings:335 | 15/7/23.2 | T-03 SC-09; closed fail-closed report parser |
| feature_corpus.py:select:573 | 10/12/32 | T-01 SC-01/13; classification/cone orchestration |
| worktree-state.py:divergent_paths:155 | 20/20/34.6 | T-01 SC-07; complete safety classification before mutation |
| worktree-state.py:diagnose:197 | 13/12/36.4 | T-01 SC-07; retains all diagnostic categories |
| worktree-state.py:main:318 | 5/8/27.6 | T-01 SC-07; CLI/report orchestration |
| tests/integration/f58_sparse_fixture.py:snapshot:237 | 6/10/27.1 | T-01/T-05 SC-07; filesystem/index/config witness |
| tests/integration/test-feature-corpus-census.py:Resolver.components:60 | 19/25/26.7 | T-03 SC-04/13; closed AST path grammar |
| same:statement_lines:116 | 7/18/9.4 | T-03 SC-04/13; marker/statement association |
| same:detected_sites:139 | 12/18/26.9 | T-03 SC-04/13; aliases/site enumeration |
| same:findings:176 | 8/19/15.6 | T-03 SC-04/13; scope vocabulary/owner seam |
| tests/unit/test-corpus-regression.py:tree_digest:47 | 11/10/25.8 | T-05 SC-02/13; deterministic non-mutation witness |

Human commits in scope: 29b1a7dbb28b, 61326cff2a78, c4f5fa82ed19, 13b72d560cbe, 2f50604fa796, 9ae5c0627bfb.

## Principles applied

Read model-the-domain, migrate-callers-then-delete and delete-first. The fix models directory identity directly at the existing seam; no compatibility population or provider hierarchy. Receipts contain no actionable Principles-applied claim under settled direct-execution exemptions; absence is not a finding. The new identity test exercises literal behavior and rejects the id-only mutant.

Current-pin general suites, real-owner checks and census remain the validator/main agent's verification responsibility. This review neither inherits their current result nor reopens settled historical limitations.
