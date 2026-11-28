# QA test-matrix gate — FEAT-2581 — run 2026-11-27-01-validate-validator (c1)

**BLUF: PASS.** `matrix_ok: true`. Both required kinds (`unit` and `integration`) are satisfied at review_sha
`62da450182282b05b25a127528f9223ac90fc6c8`, and each has a runner receipt. All three plan verifies exit 0.
SC-03 and SC-04 each have their designated fail-first equivalent: the committed baseline-side
suite records. Those records exist, are bound to the pin, and I recomputed them myself. No findings.
There is one info-level note on the evidence tier (below).

## Matrix floor (read at the pin)

- Policy blob: `git show 62da4501…:.harness/harness.json`. The feature is in the Harness repository and unbound.
- T-01 is `cross_module` → always `unit` + `integration`. T-02 is `docs` → none. T-03 is `cross_module` → always `unit` + `integration`.
- No `when:` clauses apply. `cross_module` has none.
- The baseline→pin diff outside the feature dir touches no `.ts`/`.tsx`, `tests/manual/**`, `evals/**`, `*.spec.*` or e2e path. So `typecheck`, the three `locally_run` probes, `eval`, `component` and `ui` are untouched and none is required.

| kind | status | state | cmd | runner exit | files |
|---|---|---|---|---|---|
| unit | active | satisfied | `run-unit-tests.py --kind unit --shard 1/1 --manifest …/qa/manifest-unit.json` | 0 | 68/68 exit 0 |
| integration | active | satisfied | `run-unit-tests.py --kind integration --shard 1/1 --manifest …/qa/manifest-integration.json` | 0 | 94/94 exit 0 |

## How I ran at the pin

- The worktree HEAD is `13ee3de8`, not the pin. Its two commits after the pin (`f81bde5f`, `13ee3de8`) change only this feature's `feature.json` and `plan.yaml`.
- **Suites:** ran from a managed checkout, `pinned-checkout.py add --feature FEAT-2581-feature-record-package --run-id 2026-11-27-01-validate-validator --persona harness-qa --sha 62da4501…`. HEAD there was `62da4501…` and the tree was clean. `bun install --frozen-lockfile` ran first, per repo gotcha G-12. Both suites ran with `env -u HARNESS_AGENT_TYPE`, once per kind. I removed the checkout afterwards (`remove`, rc 0).
- **Plan verifies:** ran from the worktree root, as instructed. They read through `git show` at `review_sha`. T-01 reads the working tree, which is byte-identical to the pin outside the feature dir.
- **Receipts** (runner-written, not edited). Both carry `tested_commit` `62da450182282b05b25a127528f9223ac90fc6c8` and `runner_exit` 0:
  - `runs/2026-11-27-01-validate-validator/qa/manifest-unit.json`, sha256 `855cf729…bfe18`, 68 selected and 68 completed, all `returncode` 0.
  - `runs/2026-11-27-01-validate-validator/qa/manifest-integration.json`, sha256 `cb7802f3…8378`, 94 selected and 94 completed, all `returncode` 0.

## Plan verify blocks (literal, from `git show 62da4501…:…/plan.yaml`)

| task | exit | last output line |
|---|---|---|
| T-01 | 0 | `0 unresolved reader site(s) across 110 Python file(s)` (first line: `T-01 structure and smoke PASS; …`) |
| T-02 | 0 | `T-02 decisions PASS` (then `gen-decisions-index.py --stdout \| diff` was empty) |
| T-03 | 0 | `0 unresolved reader site(s) across 110 Python file(s)` (prior: `T-03 receipts PASS at 62da450182282b05b25a127528f9223ac90fc6c8`, `verifying at … (review_sha)`) |

## SC evidence and fail-first

- **SC-03 (unit)**
  - Pin run: all 68 files exit 0, runner exit 0, and there are no `FAIL <file>` verdict lines.
  - The only `FAIL`-token lines are the four from `tests/unit/test-factory-claim-mutation.py`: BUG-1290 5a, 5b, 5c, 5b. They are byte-identical to that file's FAIL lines in the baseline measurement record `suite#tests/unit/test-factory-claim-mutation.py`, which also shows 4 lines at exit 0.
- **SC-04 (integration)**
  - Pin run: all 94 files exit 0, runner exit 0, and no `FAIL` line at all.
  - It includes `test-check-state-feat59.py` (INV-40). The T-01 verify separately proves the `plan_merge/approval.py` observer seam is live (`INV-40 CANNOT RUN … plan_merge/approval.py did not import`).
  - `test-feature-json-merge.py` is absent, as planned.
  - `test-typescript-typecheck.py` exits 0 here because of `bun install`. It is baseline-failing in the receipts (`baseline_failing: … 1 1`), so it is listed, not compared.
- **Fail-first equivalent (named by the BRIEF):** `notes/measurements/baseline.jsonl.gz` at `62da4501`, with 163 suite records. I recomputed per-file exit status and FAIL-line counts from the raw base64 streams:
  - Baseline: the only nonzero exit is `test-typescript-typecheck.py` (1); the only FAIL-bearing exit-0 file is `test-factory-claim-mutation.py` (4).
  - The pin side shows the same.
  - The 94 integration files measured at baseline are exactly the 94 my pin run executed. The 69 unit entries are my 68 plus `omp-hooks.test.ts`, which is not a Python file and not run by `--kind unit`.
- **Binding to the pin:**
  - The receipt's `implementation_pin` is `c91df7a5`. `git diff --stat c91df7a5 62da4501 -- . ':(exclude)<feature dir>'` is empty.
  - The T-03 verify, which I ran, asserts ancestor order baseline→pin→receipt commit `c65ceb81`→review_sha→HEAD. It also asserts that every verdict line is PASS, and that 631 divergences are RULED with by/date/reason. That set includes 11 `cases#` divergences, so no unruled recomputed divergence remains.
- **Tier (info, not a finding):** this is identity evidence, not a natural RED. The change preserves semantics, so no pre-fix failure exists. The BRIEF names this evidence as the equivalent, and the operator signed it.
  - What it proves: the same files pass, with the same FAIL lines, on both sides.
  - What it does not show: that the suites would redden on a behaviour change. Discrimination was not demonstrated; I am not claiming it is absent.

## Executed vs reasoned

- **Executed:**
  - both suites, once each, at the pin
  - the three verify blocks
  - the recompute from the gz measurements
  - the diff checks for pin binding and the touched-kind surfaces
  - the FAIL-line byte comparison
- **Reasoned only:**
  - that the worktree working tree is equivalent to the pin for T-01. This rests on `git diff 62da4501 HEAD` touching only the feature dir. The untracked `runs/` dir is also inside the feature dir.

## Per-file results at the pin (runner `----- <file> (exit N, …)` headers)

- **unit (68, all exit 0):** answers-provenance, check-state-corpus-rules, broad-catch-census, config-shape-matrix, check-state-inv26-routing, check-state-inv37-local-binding, artifact-accessors, digest-record, check-state-shipped-ctx, digest-dev-skill, expertise-ops, check-state-inv35, decision-disposition-schema, factory-cli, factory-claim, factory-gh, factory-land, factory-claim-mutation, factory-config, factory-workspace, feature-json-budget, feature-corpus-discovery, feature-json-reader, corpus-regression, fleet-product-config, feature-schema-build-entry, gh-board-item-add, gen-craft-index, gate-policy, feature-corpus-gates, gh-sync-build-entry, gh-cost-log, gh-sync-abandon-sources, digest-schemas, handoff-policy, gh-board, handoff-done-when, instruction-workflow-gate, integration-shard-validation, issue-types, harness-yaml-corpus, harness-boundary, code-grade, lead-stop-and-wake, orchestrator-playbook, harness-merge-journal, plan-merge-first-station, plan-merge-union-head, harness-config, probe-handoff-comprehension, no-distribution, run-identity, session-accessor-probe, structure-audit-index, plan-depends-on, check-skill-refs, team-catalog, runner-unsharded, validate-digest-run-pool-lines, suite-layout, worktree-state-rules, worktree-state-hooks-rules, prune-run-evidence, lead-start-preflight, suite-independence, wayfind, omp-hooks, feature-record. The runner reported `pool: 8 workers, 68 files, 48.52s wall` and exit 0.
- **integration (94, all exit 0):** check-decision-anchors, board-station, check-domain-approval, check-domain-claims, check-domain-artifact, branch-create-gate, check-expertise, check-fixture-secrets, check-instruction-paths, check-domain, check-domain-grant, check-domain-worktree, check-skill-weight, check-domain-worktree-parity, check-domain-post, check-omp-port, check-state-entry, check-state-corpus, check-state-inv51, check-state-inv37-offline, check-state-handoff, bash-write-guard, board-lifecycle, check-state-inv26, check-state, check-state-table, checker-structure-locks, code-grade-cli, check-state-worktrees, corpus-non-regression, check-state-plans, check-state-feat59, check-state-shipped, factory-issue-types, corpus-real-owner, feature-corpus-census, check-state-records, gen-decisions-index, factory-integration, check-plan-routes, factory-decompose, expertise-merge, gh-sync-board-add, gh-backlog-issue-types, dispatch-guard, feature-worktree, gh-issue-types, gh-close-gate, gh-sync-record, harness-config-readers, harness-constraints, harness-config-upgrade, feature-corpus, harness-yaml, gh-sync-start-task, harness-merge, inflight-registry, inject-expertise, layout-migration, integration-shard-aggregation, member-expertise, merge-gitignore, hooks-install, observations-merge, onboarding-split, panel-findings, gh-sync-ship, pinned-checkout, lead-start-return, gh-sync-open, plan-team, gh-sync-abandon, plan-sign-gate, plan-merge, run-unit-tests-kinds, post-merge-sweep, station-argument-spelling, run-pool, run-unit-tests-layout, typescript-typecheck, run-unit-tests-shards, structure-audit-single-pass, harness-config-fixtures, upgrade-config, validate-feature-json, validate-digest-shadows, suite-claim-preservation, omp-native-gate-runtime, worktree-state-hooks, worktree-terminal, merge-gate, plan-decision-dispositions, worktree-state, validate-digest. The runner reported `pool: 8 workers, 94 files, 197.72s wall` and exit 0.

## Findings

None.

## Principles applied

- harness-verification-rules (skill): the matrix floor was read from the pin blob, kind states were resolved from the runner exit and the per-file verdict lines, and fail-first evidence was graded by tier.
