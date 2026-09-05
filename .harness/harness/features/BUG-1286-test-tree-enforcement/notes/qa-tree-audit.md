# QA Tree Audit — BUG-1286-test-tree-enforcement

BLUF: at commit 5f76d6b139c9cd5fc3cc7d4011f063335210cb8e, `tests/manual/suite-census.py tree-audit --ref HEAD` measured TOTAL 85, OUTSIDE 9, VIOLATIONS 0.

Instrument output (verbatim, one fence, do not edit):

```
.harness/harness/features/FEAT-10-software-factory/notes/probe-board-limits.md	out-of-vocabulary
.harness/harness/features/FEAT-10-software-factory/notes/probe-edge-idempotence.md	out-of-vocabulary
.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-delivery-channel.md	out-of-vocabulary
.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-payload-identity.md	out-of-vocabulary
.harness/harness/features/FEAT-40-harness-writes-done/notes/probe-done-closes.md	out-of-vocabulary
.harness/harness/features/FEAT-40-harness-writes-done/notes/probe-sweep-fires.md	out-of-vocabulary
.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors-out.jsonl	out-of-vocabulary
.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts	documented-exception
.harness/notes/probe-746-foreground-dispatch-2026-08-26.md	out-of-vocabulary
tests/integration/test-anchor-directions.py	in-tests-tree
tests/integration/test-bash-write-guard.py	in-tests-tree
tests/integration/test-board-lifecycle.py	in-tests-tree
tests/integration/test-board-station.py	in-tests-tree
tests/integration/test-branch-create-gate.py	in-tests-tree
tests/integration/test-check-decision-anchors.py	in-tests-tree
tests/integration/test-check-domain.py	in-tests-tree
tests/integration/test-check-expertise.py	in-tests-tree
tests/integration/test-check-fixture-secrets.py	in-tests-tree
tests/integration/test-check-instruction-paths.py	in-tests-tree
tests/integration/test-check-omp-port.py	in-tests-tree
tests/integration/test-check-plan-routes.py	in-tests-tree
tests/integration/test-check-state.py	in-tests-tree
tests/integration/test-code-grade-cli.py	in-tests-tree
tests/integration/test-dispatch-guard.py	in-tests-tree
tests/integration/test-expertise-merge.py	in-tests-tree
tests/integration/test-factory-decompose.py	in-tests-tree
tests/integration/test-factory-integration.py	in-tests-tree
tests/integration/test-feature-json-merge.py	in-tests-tree
tests/integration/test-feature-worktree.py	in-tests-tree
tests/integration/test-gen-decisions-index.py	in-tests-tree
tests/integration/test-gh-close-gate.py	in-tests-tree
tests/integration/test-gh-sync.py	in-tests-tree
tests/integration/test-harness-merge.py	in-tests-tree
tests/integration/test-harness-yaml.py	in-tests-tree
tests/integration/test-hooks-install.py	in-tests-tree
tests/integration/test-inflight-registry.py	in-tests-tree
tests/integration/test-inject-expertise.py	in-tests-tree
tests/integration/test-layout-migration.py	in-tests-tree
tests/integration/test-merge-gitignore.py	in-tests-tree
tests/integration/test-merge-settings.py	in-tests-tree
tests/integration/test-observations-merge.py	in-tests-tree
tests/integration/test-panel-findings.py	in-tests-tree
tests/integration/test-plan-merge.py	in-tests-tree
tests/integration/test-plan-panel.py	in-tests-tree
tests/integration/test-plan-sign-gate.py	in-tests-tree
tests/integration/test-post-merge-sweep.py	in-tests-tree
tests/integration/test-quarantine.py	in-tests-tree
tests/integration/test-run-pool.py	in-tests-tree
tests/integration/test-run-unit-tests-kinds.py	in-tests-tree
tests/integration/test-run-unit-tests-layout.py	in-tests-tree
tests/integration/test-sync-agent-adapters.py	in-tests-tree
tests/integration/test-upgrade-config.py	in-tests-tree
tests/integration/test-validate-digest.py	in-tests-tree
tests/integration/test-validate-feature-json.py	in-tests-tree
tests/integration/test-worktree-terminal.py	in-tests-tree
tests/manual/probe-handoff-comprehension.py	in-tests-tree
tests/manual/probe-omp-session-accessor.py	in-tests-tree
tests/unit/omp-hooks.test.ts	in-tests-tree
tests/unit/test-answers-provenance.py	in-tests-tree
tests/unit/test-code-grade.py	in-tests-tree
tests/unit/test-config-shape-matrix.py	in-tests-tree
tests/unit/test-factory-claim.py	in-tests-tree
tests/unit/test-factory-cli.py	in-tests-tree
tests/unit/test-factory-config.py	in-tests-tree
tests/unit/test-factory-gh.py	in-tests-tree
tests/unit/test-factory-land.py	in-tests-tree
tests/unit/test-factory-workspace.py	in-tests-tree
tests/unit/test-feature-json-budget.py	in-tests-tree
tests/unit/test-gate-policy.py	in-tests-tree
tests/unit/test-gh-board.py	in-tests-tree
tests/unit/test-gh-cost-log.py	in-tests-tree
tests/unit/test-handoff-done-when.py	in-tests-tree
tests/unit/test-harness-boundary.py	in-tests-tree
tests/unit/test-harness-yaml-corpus.py	in-tests-tree
tests/unit/test-instruction-workflow-gate.py	in-tests-tree
tests/unit/test-lead-stop-and-wake.py	in-tests-tree
tests/unit/test-no-distribution.py	in-tests-tree
tests/unit/test-omp-hooks.py	in-tests-tree
tests/unit/test-orchestrator-playbook.py	in-tests-tree
tests/unit/test-probe-handoff-comprehension.py	in-tests-tree
tests/unit/test-render-brief.py	in-tests-tree
tests/unit/test-suite-independence.py	in-tests-tree
tests/unit/test-suite-layout.py	in-tests-tree
tests/unit/test-team-catalog.py	in-tests-tree
tests/unit/test-wayfind.py	in-tests-tree
TOTAL 85 OUTSIDE 9 VIOLATIONS 0
```

Outside-`tests/` dispositions (9 rows):

- `.harness/harness/features/FEAT-10-software-factory/notes/probe-board-limits.md` — out-of-vocabulary: a probe write-up captured as a Markdown record; its basename matches the agnostic `probe-*` pattern but carries no `.py`/`.ts`/`.js` source extension, so it falls outside the D-01 vocabulary.
- `.harness/harness/features/FEAT-10-software-factory/notes/probe-edge-idempotence.md` — out-of-vocabulary: same class, a Markdown probe write-up, not a source-tree test file.
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-delivery-channel.md` — out-of-vocabulary: a Markdown probe write-up, out of the D-01 vocabulary.
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-payload-identity.md` — out-of-vocabulary: a Markdown probe write-up, out of the D-01 vocabulary.
- `.harness/harness/features/FEAT-40-harness-writes-done/notes/probe-done-closes.md` — out-of-vocabulary: a Markdown probe write-up, out of the D-01 vocabulary.
- `.harness/harness/features/FEAT-40-harness-writes-done/notes/probe-sweep-fires.md` — out-of-vocabulary: a Markdown probe write-up, out of the D-01 vocabulary.
- `.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors-out.jsonl` — out-of-vocabulary: a captured JSONL probe output record, not a source-extension file, so it falls outside the D-01 vocabulary.
- `.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts` — documented-exception: this is the FEAT-44 evidence file that Decision D-05 declares an allowed documented exception at its exact current path, and it is the live consumer reference read by `tests/manual/probe-omp-session-accessor.py` lines 54-55. The classification authority is `suite_layout.DOCUMENTED_EXCEPTIONS`, which lists this exact path; the tree-audit instrument imports that registry rather than re-declaring it, so this row's disposition can never drift from the guard's own.
- `.harness/notes/probe-746-foreground-dispatch-2026-08-26.md` — out-of-vocabulary: a captured probe write-up under repository-level notes, out of the D-01 vocabulary.

Closing: no row above is unexplained. All 9 outside-`tests/` rows are accounted for — 1 documented exception (D-05, `suite_layout.DOCUMENTED_EXCEPTIONS`) and 8 out-of-vocabulary probe records — and VIOLATIONS is 0.
