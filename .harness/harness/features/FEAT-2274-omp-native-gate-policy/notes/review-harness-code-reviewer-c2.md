# Code review c2 — PASS with risk advisories

**No remaining must-fix found at `242f9714d426415611bea796dd30a807f14c4193`. V1–V5 close in this lens; four individually justified grade-2 test functions remain nonblocking.** QA owns executable acceptance, not this static clearance.

Reviewed full implementation `1e0b014917125bc9aae1f30a2f6fd53ed239f3bc..242f9714` and remediation `649612d8..242f9714`; source claims use `git show` at the pin. Live feature.json agrees. Initial status was clean; commit census contains only feature work and no `[harness:human]` commits. Mandatory grading uses actual merge-base `c1724230c4d931ad46d433c8ba93df8cf312f898`, not the implementation baseline.

## Stage 1 — specification, before quality

BRIEF/approved plan D-01 read before diff; product AGENTS.md maps authority to product SPEC §4.2 and DECISIONS. Changes serve SC-01–09/D-01; no independent behavior or unrelated cleanup found. Additional classification/skill paths have disposition accounting. No spec violations remain identified.

- **SC-04 inspection:** pinned `dispatch-guard.py:344–350` replaces the deleted spawns parser with the unchanged claim-root flow, not another allowlist/parity check. Complete `.omp/agents` diff changes guidance only: native spawns frontmatter remains unchanged against baseline. Guidance: `harness-product-lead.md:57`, `harness-eng-lead.md:59`, `harness-validator-lead.md:59`. External provenance, NOT pinned source: owner-checkout `.harness/notes/grilling-omp-native-enforcement-a-2026-11-21.md`, “Facts I verified”, records published OMP **19.1.0** shared `runStructuredSubagent`/`assertDepthAndSpawnAllowed` paths for task/eval/workpool.
- **SC-08 inspection:** pinned `DECISIONS.md:1372–1406` retains DEC-100's broad default and adds visible unavailable/bounded closed exceptions; `:2227`, `:2680`, `:6501`, `:6717`, `:7858` amend DEC-118/127/204/208/234 in place. `SPEC.md:740–778` and changed index rows agree. `notes/t03-decision-dispositions.md` accounts for all cited decisions, including retained DEC-193 and DEC-205's rewrite policy.

## Stage 2 — correctness and c1 closures

- **V1 (original high/substance, T-01) closed:** `gh-close-gate.py:239–253` and `branch-create-gate.py:155–175` refuse failed config reads and nonmapping github blocks after applicability. Missing/truncated/duplicate-key configuration can no longer authorize `gh issue close 728` or branch creation as sync-off. Pinned config-fault cases bind named exit-2 refusals, unrelated-command silence and readable exemption controls; fail-first receipt `fix-c1-v1-red-green.md` supports regression discrimination.
- **V2 (original med/substance, T-01) closed:** `dispatch-guard.py:324–326,448–450` emits unavailable for failed vocabulary and unreadable grants. Independent cases at `test-dispatch-guard.py:588,603,616` distinguish both failures from legitimate quiet controls; V2 receipt explains the corrected single-fault persona fixture.
- **V3 (original med/substance, T-01) closed:** `harness-hooks.ts:1874–1878` appends collected notices to the refusal **reason**, preserving deny precedence. `omp-hooks.test.ts:2205` requires both denial and notice. This is effective delivery, not an additionalContext claim: external type/binary evidence in `fix-c1-v3-red-green.md` establishes that OMP 19.1.0 drops blocked-call additionalContext and exposes reason. Normal input/env/schema/result composition and multiplicity remain covered.
- **V4 (original high/substance, T-01) closed statically:** `test-lead-start-preflight.py:381` now asserts successful Python preflight plus one claim, not deleted allowlist authorization; no native-policy simulation added.
- **V5 (original high/substance, T-01) closed:** required pinned grader reports **104 passing functions, four med grade-2 records, no high/grade-1 records**, exit 0. Diff preserves the digest/boundary cases and conjuncts through focused fire/predicate helpers; no grade-1 waiver. Standing self-grading execution belongs to QA.
- **V6/V7 (T-03) close in inspection:** named index tails are shortened; disposition ledger covers DEC-193 and all cited decisions. Generator/budget execution remains QA-owned.

Fail-open hunt traced guarded exits, dependency misses, structured-deny precedence, route registration independent of caller identity, digest absent/null/non-object refusal and deliberate non-governed passthroughs. No further concrete defect identified. RED receipts and simplify receipt inspected; no tests, builds, linters, formatters, mutants, live delivery or compiler run here. Accepted #2257 and documented native-rule delivery limitations remain unchanged.

## Mandatory grade-2 advisories — all med/substance, T-01

Metrics are CC/cognitive/ABC; each is a test-bar-3 grade-2 record, not a production waiver. Maintenance scenario: extending these fault matrices requires reading a larger fixture/assertion aggregation; locality justifies retaining the current grouping.

1. `test-bash-write-guard.py:1094#run_feat65_guard_cases` **11/8/27.5**, driver CC/ABC. Reason: one retained crash/control matrix keeps the four exception-policy contrasts adjacent.
2. `test-bash-write-guard.py:1152#run_feat2274_unavailable_cases` **7/6/32.9**, driver ABC. Reason: one gate-specific unavailable/quiet matrix shares its checkout and command fixture; separating it would scatter the outcome contrasts.
3. `test-check-domain.py:111#_feat2274_cases` **8/6/33.5**, driver ABC. Reason: linear fixture/result collection keeps unavailable, normal pass and deliberate denial comparisons local.
4. `test-dispatch-guard.py:515#case_f2274_unavailable_outcome` **8/9/29.9**, driver ABC. Reason: one dispatch fault/control matrix shares checkout cleanup; the newly fixed dependency branches remain separate rather than growing this matrix.

## Principles applied

**Migrate Callers, Then Delete Legacy APIs** — verified the deleted Python allowlist has no compatibility shim, its skill guidance names native authority, and V4 migrates the remaining obsolete caller assertion. `harness-code-review` test-subject checks distinguish real gate execution from adapter doubles and configuration inspection.

Open questions: none. Must fix: none. Source files touched: none. Checks for QA: assigned task commands plus final standing unit/integration and self-grading/index-budget gates; do not rerun the supplied baseline canonical-reader failures on this reviewer's account.
