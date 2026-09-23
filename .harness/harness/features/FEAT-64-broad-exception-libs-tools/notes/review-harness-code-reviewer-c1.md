# FEAT-64 code review — c1

## Disposition

**PASS.** Reviewed immutable `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983..50dd75c4b97a51f6a3fe7ffb5f27d3c5e2889a31`. The canonical baseline-to-pin set received from QA contains **59 files** (exact identity below). The only working-tree modification is the Harness-owned `feature.json`; all code claims use the pin. No `[harness:human]` commit is in range.

## Stage 1 — spec compliance: PASS

All changes serve SC-01..SC-08 and D-01..D-04; no scope creep, omission, or mismatch remains. SC-04 inspection finds none of the eleven hook entry scripts or `.omp/extensions/harness-hooks.ts` in the canonical set. SC-05's moved/copy rationales remain attached to their narrowed handlers and new explanations are separately marked FEAT-64. The approved T-01/T-02/T-03 traces now include SC-07 on T-02/T-03 and SC-08 on T-01/T-03; BRIEF and plan approval were revoked and re-signed `2026-09-23` without weakening a behavior clause.

The three c0 remedies independently close:

- **CR-64-01 / GC-64-03:** `git diff --quiet` proves `board_lifecycle.py` byte-identical to the baseline. Issue **#1897** exists and is open. Ledger B2 records the actual old/new observable bytes: the baseline prints the `GhError.__init__()` missing-arguments line and returns, while the pin raises the same `TypeError` and prints nothing; the operator ruling identifies this as T-02's intended defect exposure, not an in-scope repair.
- **GC-64-01:** `byte-evidence.md` supplies per-suite raw and normalized stdout/stderr digests and verbatim zero-context differences for all 27 suites. Ledger §A enumerates exactly eight removed lines: board-station retitle; check-omp-port count; two check-skill-weight stderr lines; upgrade-config, gh-cost-log, handoff-policy, and harness-yaml-corpus counts. Every other normalized difference is additive; the two allowed normalizations are stated.
- **GC-64-02:** the research note separates shared-library/unit SC-03 from tool/integration SC-07 and route/integration SC-06 from handoff/unit SC-08, names the T-01/T-02/T-03 trace additions, and requires the reapproval present at the pin.

All six required shared artifacts were inspected. `runs/build-main-direct/digest.md` is absent from the immutable pin (and consequently absent from the canonical set); its worktree copy was also inspected and is treated only as a non-pinned historical receipt, not evidence overriding the pin.

## Stage 2 — code quality: PASS

Started only after Stage 1 passed. The production diff narrows all scoped broad handlers to owning boundary errors, preserves deliberate fail-open outcomes only for documented environmental cases, lets unrelated defects escape, and does not introduce a silent catch. `factory_gh` centralizes launch/decode typing; consumers do not duplicate it. Both plan caches are execution-scoped and cleared at their command/note entry, so they remove duplicate reparses without stale cross-execution state. The census default is zero, retains exactly two `harness_boundary.py` catches, and its independent increase/reduction mutants cover drift. Pinned `code-grade.py` reports 48 passing changed functions and no failure or grade-2 waiver.

### Dismissed / advisory items preserved

- **c0 CR-64-01 / GC-64-03:** dismissed as resolved: the out-of-scope repair and its dedicated test were reverted; baseline identity and #1897 were independently verified.
- **c0 GC-64-01:** dismissed as resolved: exact stream evidence plus the eight-line §A accounting closes the prior category-only gap.
- **c0 GC-64-02:** dismissed as resolved form issue: evidence kinds, traces, and approval now align.
- **Potential B2 fail-open regression:** dismissed. The new traceback is the specified exposure of an unrelated programming defect; the ledger records the concrete old/new behavior and the actual repair remains in #1897's separate lane.
- **Potential cache fail-open/staleness:** dismissed. `_PLAN_LOADS` and `_PLAN_MEMO` clear at their public execution boundaries and cached parse failures are re-raised rather than converted to clean results.
- **Build-the-Lever / Test-Behavior receipt claims:** no finding; the build digest contains no `## Principles applied` section, so there is no affirmative claim to falsify.

## Canonical file set (59, exact ordered identity)

```text
.claude/skills/harness/bin/board-station.py
.claude/skills/harness/bin/check-omp-port.py
.claude/skills/harness/bin/check-plan-routes.py
.claude/skills/harness/bin/check-skill-weight.py
.claude/skills/harness/bin/factory_decompose.py
.claude/skills/harness/bin/factory_gh.py
.claude/skills/harness/bin/feature_schema.py
.claude/skills/harness/bin/gh-sync.py
.claude/skills/harness/bin/gh_cost_log.py
.claude/skills/harness/bin/handoff_done_when.py
.claude/skills/harness/bin/handoff_policy.py
.claude/skills/harness/bin/harness_boundary.py
.claude/skills/harness/bin/harness_yaml.py
.claude/skills/harness/bin/post-merge-sweep.py
.claude/skills/harness/bin/run-unit-tests.py
.claude/skills/harness/bin/run_identity.py
.claude/skills/harness/bin/upgrade-config.py
.claude/skills/harness/bin/worktree_terminal.py
.harness/harness/features/FEAT-64-broad-exception-libs-tools/BRIEF.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/STATE.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/feature.json
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/build-divergences.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/byte-evidence.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/handoff-plan.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/red-first-receipts.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-plan.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-c0-resolution.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-gc-64-02-evidence-kinds.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-code-reviewer-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-code-reviewer-plan-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-qa-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-security-reviewer-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-ui-reviewer-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-ui-reviewer-plan-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/plan.yaml
.harness/harness/features/FEAT-64-broad-exception-libs-tools/runs/validate-validator/digest.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/runs/validate-validator/state.yaml
tests/integration/test-board-lifecycle.py
tests/integration/test-board-station.py
tests/integration/test-check-omp-port.py
tests/integration/test-check-plan-routes.py
tests/integration/test-check-skill-weight.py
tests/integration/test-factory-decompose.py
tests/integration/test-gh-sync-ship.py
tests/integration/test-harness-yaml.py
tests/integration/test-post-merge-sweep.py
tests/integration/test-run-unit-tests-layout.py
tests/integration/test-upgrade-config.py
tests/integration/test-worktree-terminal.py
tests/unit/test-broad-catch-census.py
tests/unit/test-factory-gh.py
tests/unit/test-feature-schema-build-entry.py
tests/unit/test-gh-cost-log.py
tests/unit/test-handoff-done-when.py
tests/unit/test-handoff-policy.py
tests/unit/test-harness-boundary.py
tests/unit/test-run-identity.py
```

## Findings

None.

## Principles applied

- No craft leaf changed the disposition; the review is grounded in the signed criteria, pinned diff, direct artifact inspection, and mechanical grade.
