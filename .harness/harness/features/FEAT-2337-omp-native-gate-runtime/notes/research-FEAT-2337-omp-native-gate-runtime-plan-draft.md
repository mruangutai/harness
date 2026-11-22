# FEAT-2337 — pending draft receipt

**Ready for independent plan readers, not approved or implemented.** BRIEF.md has 10 SCs (8 automated, 2 pinned inspections); plan.yaml has 3 serialized main-session-direct tasks, 2 decisions and 11 verbatim dispositions. Required plan check: exit 0, 23 anchors, no failures. No build, tests, lint, formatter, benchmark or commit ran.

## Authority and product guidance

- FIRST read runs/r-20261122-1-plan-product/acceptance.md. Applied its binding requirements and send-back criteria.
- Intake: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-omp-native-gate-runtime-b-2026-11-22.md. Preserved Destination, Settled, Mission=plan and Out of scope.
- PRODUCT/write root: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime. inflight_registry.py feature-root returned this exact root. Observed source HEAD: dd04e52a898109fdbe09cf5fa14e1148161734d0.
- docs/spec.md, docs/decisions.md, docs/architecture.md are absent (directory and tracked-path inventory). Product CLAUDE.md imports AGENTS.md; its Project map explicitly names this product's .harness/harness/docs/SPEC.md and DECISIONS.md. Read relevant test/manifest/return sections. No architecture document exists; absence is disclosed in BRIEF and every task intent, never replaced with an unrelated product's guidance.
- Consulted DEC sections: 100, 120, 174, 179, 182, 187, 202, 205, 232, 234, 254. Every one has a five-field verbatim decisions_affected row: DEC-100 amend -> D-01, owner T-03; ten keep rows. No strike. D-02 is a NEW receipt ruling, proposed DEC-255, with unused-number recheck at implementation; not a false amendment to DEC-209.
- Read harness-brief/spec-driven/handoff/grilling/verification-rules/tdd-enforcement/simplify and plan/brief templates. Panel/simplification dispatches and recording remain lead-owned, not fabricated here.

## Complete standing caller/doc inventory — swept before drafting

Queries at dd04e52a, before BRIEF:

    git grep -n -E 'RUN_UNIT_TESTS_BIN|check_qa_matrix_claim|spawnSync|runPolicy|#919|independent.*re.?run|re.?runs? .*suite|suite.*re.?run' -- tests .omp .claude/skills README.md .harness/harness/docs
    git grep -n -E '_resolve_run_unit_tests_bin|_reverify_suite|_print_independent_run|_claimed_kinds' -- tests .claude/skills/harness
    git grep -n -i -E '#919|independent re.run|rerun.*qa|qa.*rerun|re.run.*matrix|matrix.*re.run' -- . ':!*.html' ':!.harness/*/features/**' ':!.harness/*/expertise/**' ':!.harness/expertise/**' ':!.harness/notes/**'
    git grep -n -i -E 're.?run|independent|#919|manifest' -- .omp/agents/harness-qa.md .omp/agents/harness-validator-lead.md .claude/skills/harness-verification-rules .claude/skills/harness/teams/validate.yaml .harness/harness/docs/SPEC.md README.md .harness/README.md

Paths are PRODUCT-relative authored paths. All affected standing files are owned, not just the new tests.

| File | Findings / disposition |
|---|---|
| .omp/extensions/harness-hooks.ts | Synchronous runPolicy/PolicyRunner/reportingRunner; fileDomain/preDomain/postDomain; releaseClaim; resolveFeature/startRun/openRun/settleRun; featureRoot/rootCall/authorizationRefusal; digest destination, expertise merge/appliedPost/mainMergeGate; startup/revival/reconcile/injection; five sequential preGate calls; dispatch attach/rollback, yield, result cleanup, registry root/stamp-tokens/spend/post gates. T-01 migrates all direct/indirect callers. Unrelated git spawnSync stays out of Python policy scope. |
| tests/unit/omp-hooks.test.ts | Injected synchronous runners throughout; spawnSync outcome fixtures, Python gate invocations, expertise/apply and real-default-runner tests. T-01 migrates awaited policy consumers, preserving fixture git execution and every standing regression assertion. |
| tests/integration/test-omp-native-gate-runtime.py | DRIVER calls runPolicy without await; plant_unexecutable names spawnSync; real copied-process adapter matrix and both applicability corpora. T-01 migrates driver/comments and adds bounded-process/performance tests without dropping default suite. |
| .claude/skills/harness/bin/validate-digest.py | Module #919 rerun docstring and comments; _qa_claims_unconditional_pass, _artifact_holder/_resolve_run_unit_tests_bin/RUN_UNIT_TESTS_BIN, _claimed_kinds, _reverify_suite, check_qa_matrix_claim; _run_pool_file_lines/_print_independent_run. T-02 removes rerun-only implementation/comments and migrates retained trigger/kind policy. _artifact_holder remains only if another live caller needs it. |
| tests/integration/test-validate-digest.py | _bug919_stub_script/_bug919_fire; agreement/disagreement/non-PASS/missing-runner/red wiring group; BUG-1756 kinds/default/first-failure/spawn/timeout/direct matrix claim; #1185 fallback and #1883 artifact-worktree resolver; source mutant QA wiring; all-persona/FEAT-2274 unavailable matrix old rerun site; #2253 stub/buried/echoed/quiet group; HOOK_HANG_BUDGET_S=30. T-02 owns entire standing file and migrates every affected fixture/group. |
| tests/unit/test-validate-digest-run-pool-lines.py | Old rerun docstring and direct pooled parser/reporter calls; failing names, spaces/duplicates, misleading echo and buried-tail tests. T-02 converts in place to receipt refusal diagnostics, deleting dead pooled implementation rather than preserving it for tests. |
| .claude/skills/harness/bin/check_state/feature_record.py | INV-47 comment says #919 rerun fires only on qa PASS. T-02 corrects comment only, no INV-47 logic change. |
| .claude/skills/harness/bin/check-integration-shards.py | discover_expected already reads tested-commit git tree; evidence_defects shares types, identity, Counter and exact coverage. Integration-only constants need optional-kind extension; T-02 owns reuse and preserves four-shard CLI defaults. |
| tests/unit/test-integration-shard-validation.py | Direct evidence_defects caller with schema/kind/shard/completion defects. T-02 adds explicit unit/default regression coverage. |
| tests/integration/test-integration-shard-aggregation.py | Real CLI git-history discriminator against later HEAD/untracked working tree. T-02 preserves it and covers reused kind behavior. |
| tests/integration/test-run-unit-tests-shards.py; tests/unit/test-runner-unsharded.py | Existing runner/manifest producer unchanged, no removed validator-seam caller. Final QA runs them; no edits needed. |
| tests/unit/test-omp-hooks.py | Already runs Bun omp-hooks.test.ts and propagates status. No edit; supplies active unit-runner discovery. Backlog #2329 was read, not treated as proof this wrapper is absent. |
| tests/unit/test-code-grade.py | Existing SELF_GRADED_FILES/ALLOWLIST/check_self_grading does not automatically cover all changed tests. T-03 adds cumulative fixed-base test grading without exemptions, including itself and grade-2 mutant. |
| .omp/agents/harness-qa.md; .omp/agents/harness-validator-lead.md | No existing #919 rerun rule, but new receipt-production/repair contract must be integrated. T-03 owns both roles. No corresponding role SKILL.md exists; actual authored paths are roles. |
| .claude/skills/harness-verification-rules/SKILL.md | Existing matrix/managed-pin/fail-first protocol, no #919 clause. T-03 adds receipt commands/destination while preserving that protocol. |
| .claude/skills/harness/teams/validate.yaml; fix.yaml | QA correctly runs/re-runs its matrix. T-03 preserves this and adds manifest destination/production/handoff; it is not the removed validator duplicate execution. |
| .harness/harness/docs/SPEC.md | Schema-1 manifests, tested-tree discovery, CI aggregation under Test guardrails/Sharded integration. No #919 ruling. T-03 adds concise runtime/receipt guidance and decision pointer, preserving CI. |
| README.md | Runtime/Guardrails, no old #919 clause. T-03 adds bounded/parallel runtime and receipt trust boundary. |
| .harness/harness/docs/DECISIONS.md; DECISIONS-INDEX.md | No #919 ruling. T-03 amends DEC-100 in place, adds NEW receipt decision, regenerates index; new ruling tail <=30 words. |
| .harness/team-config.yaml; .claude/skills/harness/templates/team-config.yaml | QA has tests/notes grants, not runner manifests. T-03 adds manifest-*.json only. Existing template uses unsegmented feature paths; retain established layout convention, no unrelated template migration. |
| tests/integration/test-check-domain-grant.py | Actual grant-path standing suite. T-03 adds narrow receipt grant/refusals. test-check-domain.py was inspected but primarily covers closed run-state schema; not owned or changed. |
| .claude/skills/harness-simplify/SKILL.md; references/angle-efficiency.md; .omp/commands/harness.md | Generic deliberate post-change/boundary reruns, not #919 return-hook requirements. No edits. |
| .harness/harness/docs/BUILD.md; .harness/README.md | Historical suite/maintenance-audit reruns, not live #919 rule. No edits. Historical feature/run records and expertise excluded, not rewritten. |

No file overlaps: T-01 owns 3 files, T-02 owns 7, terminal T-03 owns 13.

## Performance and review-pin verification choice

- SC-04: parallel median <=0.75 of sequential median on the same host/pin, 3 warmups + 15 alternating pairs, real five-gate handler/processes with ls -la/harness-backend-dev. The historical ~180 ms is context, not a brittle absolute 135 ms claim. Fixture-local serial adapter supplies counterfactual and serial mutant must fail. Raw samples, medians, ratio, host/runtime versions/source SHA become durable QA evidence.
- Benchmark lives in existing real-process integration suite with supplemental --benchmark/--feat2337 and unchanged default complete execution.
- Unit SCs: 01, 03, 05, 08. Integration: 02, 04, 06, 07. SC-09/10 inspect git show <review_sha>:<path>. No UAT/operator-only pass.
- OWN validate deliberately uses PRE-EXISTING installed/control-plane #919 rerun behavior; no host redeploy is implied. Candidate receipt behavior is tested from committed review_sha. Installed invocation-time launcher path/version/hash is recorded separately from source SHA. QA still produces candidate manifests; main force-adds them with the committed run.
- A receipt can be uncommitted at QA yield: commit with the closed run afterward, not inside its own tested_commit. tested_commit identifies tested source, not the evidence-storage commit.
- typecheck unresolved/null: no static proof claimed; Bun unit + real integration + pinned review carry coverage, #2257 tracks runner gap. component/ui null kinds have no interaction surface here; functional/eval stay decision-excluded. No criterion rests on these.
- All new/changed Python test functions grade >=3 via test-code-grade.py self-grading, including its own additions, no new allowlist exemption. TypeScript runs through Python-to-Bun wrapper, never falsely Python-graded.

## Authored paths and complete lane resolution

.agents/skills is ../.claude/skills; every task anchor uses real authored .claude paths, not duplicate aliases. Roles live in .omp/agents. Realpaths of every file below were resolved before ownership; all stay physically inside PRODUCT.

For EACH path: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-domain.py --resolve <absolute PRODUCT/path>. All 23 returned exit 0. Resolver manifest: /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml at dd04e52a898109fdbe09cf5fa14e1148161734d0. Plan check also resolves against worktree manifest; no deviation reported.

| Exact file | Resolver stdout | Planned lane |
|---|---|---|
| .omp/extensions/harness-hooks.ts | NOBODY | main-session-direct |
| tests/unit/omp-hooks.test.ts | harness-backend-dev; harness-dev-ops; harness-qa | main-session-direct |
| tests/integration/test-omp-native-gate-runtime.py | harness-backend-dev; harness-dev-ops; harness-qa | main-session-direct |
| .claude/skills/harness/bin/validate-digest.py | harness-backend-dev; harness-dev-ops | main-session-direct |
| .claude/skills/harness/bin/check-integration-shards.py | harness-backend-dev; harness-dev-ops | main-session-direct |
| .claude/skills/harness/bin/check_state/feature_record.py | harness-backend-dev; harness-dev-ops | main-session-direct |
| tests/integration/test-validate-digest.py | harness-backend-dev; harness-dev-ops; harness-qa | main-session-direct |
| tests/unit/test-validate-digest-run-pool-lines.py | harness-backend-dev; harness-dev-ops; harness-qa | main-session-direct |
| tests/unit/test-integration-shard-validation.py | harness-backend-dev; harness-dev-ops; harness-qa | main-session-direct |
| tests/integration/test-integration-shard-aggregation.py | harness-backend-dev; harness-dev-ops; harness-qa | main-session-direct |
| tests/unit/test-code-grade.py | harness-backend-dev; harness-dev-ops; harness-qa | main-session-direct |
| tests/integration/test-check-domain-grant.py | harness-backend-dev; harness-dev-ops; harness-qa | main-session-direct |
| .harness/team-config.yaml | NOBODY | main-session-direct |
| .claude/skills/harness/templates/team-config.yaml | NOBODY | main-session-direct |
| .omp/agents/harness-qa.md | NOBODY | main-session-direct |
| .omp/agents/harness-validator-lead.md | NOBODY | main-session-direct |
| .claude/skills/harness-verification-rules/SKILL.md | NOBODY | main-session-direct |
| .claude/skills/harness/teams/validate.yaml | NOBODY | main-session-direct |
| .claude/skills/harness/teams/fix.yaml | NOBODY | main-session-direct |
| .harness/harness/docs/SPEC.md | harness-documentor | main-session-direct |
| .harness/harness/docs/DECISIONS.md | harness-documentor | main-session-direct |
| .harness/harness/docs/DECISIONS-INDEX.md | harness-documentor | main-session-direct |
| README.md | harness-documentor | main-session-direct |

Consult-when was not confused with grants: backend/ops own process/gate implementations, QA owns tests and documentor docs, but DEC-174 selects direct execution across the cutover. Direct tasks omit execution_agent and carry execution_reason; lanes explain granted-path deviations.

## Controlled writes and check receipts

- Read control-plane plan-merge.py help/apply/amend/check and union code. Current apply replaces named fields; older expertise saying all replacements conflict is superseded by observed interface.
- Initial inline proposal was rejected BEFORE execution by bash-write-guard treating a >=3 prose expression as redirect to =3. Destination directory confirmed no plan afterward. Temporarily staged proposal in this requested note, applied through plan-merge only, then replaced it with this research receipt; no extra plan convention/file remains.
- First executed apply: APPLIED <feature>/plan.yaml; PLAN-APPLY-EXIT: 0. Its own check-state stderr exposed unsupported leading timeout verify shape. Corrected to recognized bash command with a single 55-second deadline around each whole verify.
- Second apply: PRESERVED D-01/D-02; REPLACED T-01.verify, T-02.verify, T-03.verify; APPLIED <feature>/plan.yaml; PLAN-APPLY-EXIT: 0. Both task-changing invocations captured AND printed stdout. Neither emitted APPROVAL-RESET:, so NO gh-sync status call.
- Automatic check-state warns unsigned BRIEF/pending plan and absent Build-entry receipt. Expected at pending planning; no signature, Build receipt, GitHub mirror or run state forged.
- Reported writer seeding an unloadable pending verify while returning APPLIED/0 through report_issue; response: Noted, thanks! This is a harness defect observation, not product scope.
- Required command executed:

    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime/.harness/harness/features/FEAT-2337-omp-native-gate-runtime/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime

Observed:

    OK T-01 3 anchor(s) resolved
    OK T-02 7 anchor(s) resolved
    OK T-03 13 anchor(s) resolved
    CHECK <feature>/plan.yaml against <PRODUCT>: 3 task(s), 23 anchor(s) resolved, 0 failure(s)
    PLAN-CHECK-EXIT: 0

Subsequent BRIEF grant-continuation adds no SC id or file and leaves trace/anchor result unchanged. No extra audit or suite run.

## Principles applied

- Experience First — visible actionable timeout/receipt-repair feedback and measurable hot-path improvement without a new timeout control.
- Redesign From First Principles — one async runner and one reused git-tree verifier, migrating all standing callers/docs instead of a rerun shim.
- Outcome-Oriented Execution — three file-owned cutovers, complete final QA; focused modes supplement, never replace, standing suites.

## Open questions and next handoff

- No blocking product unknown. Performance threshold and own-validate bootstrap are explicit pending proposals, not observed behavior.
- Lead owns independent three-reader wave, panel-c1.md fan-in/record; PM then applies findings and an independent exit goal-check against grilling intent. No panel/approval authored here.
- Only main records operator approval. Nothing implemented or committed. After signature, run literal task verifies and full final unit/integration production manifests; planning check is not behavioral evidence.
