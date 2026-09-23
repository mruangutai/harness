# FEAT-64 goal-check — validate c1

## Verdict

**FAIL.** The code and retained test matrix satisfy the maintainer and reader perspectives, and the operator no-hook condition is met. The operator perspective remains **partial** because the two pinned records intended to prove exact output equivalence contradict each other for `tests/unit/test-harness-yaml-corpus.py`: `notes/byte-evidence.md` records `101/.harness=97 -> 104/.harness=100` with digest `3a1860010aa8ff56`, while `notes/build-divergences.md` §A4 records `101/.harness=97 -> 103/.harness=99` and attributes the increase only to `plan.yaml` and `feature.json`. That evidence defect is **GC-64-04** and leaves SC-01 partial even though the pinned unit and integration matrices pass.

Review pin: `50dd75c4b97a51f6a3fe7ffb5f27d3c5e2889a31`

Baseline: `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983`

## Evidence provenance and canonical scope

QA derived and broadcast the ordered baseline-to-pin set once. I used that exact **59-path** set and did not substitute a different diff range:

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

All six required shared artifacts were independently inspected. The immutable pin contains `runs/validate-validator/digest.md`, `notes/red-first-receipts.md`, `notes/byte-evidence.md`, `notes/build-divergences.md`, and `notes/research-FEAT-64-gc-64-02-evidence-kinds.md`. `runs/build-main-direct/digest.md` is absent from the immutable pin and from the canonical set; I inspected its working-tree copy only as contextual history and did not use it as evidence for a pin-level claim.

## c0 remedy remeasurement

### CR-64-01 / GC-64-03 — closed

- `.claude/skills/harness/bin/board_lifecycle.py` is baseline-identical under the operator ruling; the baseline-to-pin object comparison is empty.
- GitHub defect [#1897](https://github.com/mruangutai/harness/issues/1897) exists and remains open. It records the one-argument `GhError` construction that becomes a `TypeError` at raise time and keeps the repair outside FEAT-64.
- Pinned `notes/build-divergences.md` §B2 measures the old and new observable bytes: the baseline returns after printing the `GhError.__init__()` missing-arguments diagnostic, while the narrowed path propagates that `TypeError` and prints nothing. This is defect exposure, not an in-scope repair.
- The changed `tests/integration/test-board-lifecycle.py` coverage belongs to the in-scope `factory_gh.run_gh` boundary; it does not restore the reverted production change.

### GC-64-01 — original category gap closed; new exactness defect GC-64-04

- Pinned `notes/byte-evidence.md` supplies 27 per-suite raw and normalized stdout/stderr digests and prints every normalized differing line verbatim.
- Its removal summary totals exactly eight lines: one board-station line, one check-omp-port line, two check-skill-weight lines, and one each for upgrade-config, gh-cost-log, handoff-policy, and harness-yaml-corpus.
- Pinned `notes/build-divergences.md` §A likewise classifies exactly eight removed lines.
- The records nevertheless disagree on the harness-yaml-corpus new byte/count result (`104/100` versus `103/99`). The original “category-only” omission is fixed, but the replacement ledger is not exact enough to discharge the criterion.

### GC-64-02 — closed

- Pinned `BRIEF.md` and `notes/research-FEAT-64-gc-64-02-evidence-kinds.md` separate shared-library/unit behavior from the eight tool/integration behaviors, and route-discovery/integration behavior from handoff-authority/unit behavior. No behavior clause was dropped.
- Pinned `plan.yaml` traces T-01 to the library, route, and handoff criteria; T-02 to the library and tool criteria; and T-03 to all four.
- The pre-fix records were signed `2026-09-22`; the pinned BRIEF and plan are re-signed `2026-09-23`. The pin commit records the revocation/re-sign action while adding the split criteria and traces. No intermediate pending object is committed, but the immutable before/after records and pin commit establish the required re-sign rather than silently retaining the earlier approval.

## Perspective grades

1. **Operator — PARTIAL.** The no-hook criterion is met by the empty pinned hook-path diff and absence of hook files from the canonical set. The exact-output criterion remains partial because GC-64-04 makes one suite's authoritative new bytes ambiguous despite the passing test matrix.
2. **Code maintainer — MET.** QA's pinned c1 matrix passes 42 unit files and 69 integration files; it cites the census ceiling/mutants, shared-library typed-boundary tests, and eight-tool boundary tests. The census permits exactly the two deliberate `harness_boundary.py` broad catches and zero others in scope.
3. **Reader — MET.** Pinned §C/comment inspection preserves moved rationales and marks new FEAT-64 prose; the route and handoff one-parse behaviors have retained red-first receipts and passing pinned tests. Divergences are traceable, subject to the operator-facing exact-count defect already isolated as GC-64-04.

## Success-criterion grades

| SC | Perspective | Verdict | Method | Carrying tasks | Evidence |
|---|---|---|---|---|---|
| SC-01 | operator | **partial** | automated | T-01, T-02, T-03 | QA c1 confirms both required pinned matrices pass and cites the 27-suite appendix plus §A; however, pinned `byte-evidence.md` and `build-divergences.md` §A4 disagree on harness-yaml-corpus `104/100` versus `103/99`. See GC-64-04. |
| SC-02 | code maintainer | **met** | automated | T-01, T-02, T-03 | QA c1: `tests/unit/test-broad-catch-census.py:83-96` and `tests/integration/test-check-plan-routes.py:2912-2922`; retained REDs in `notes/red-first-receipts.md` §2. |
| SC-03 | code maintainer | **met** | automated | T-01, T-02, T-03 | QA c1: `tests/unit/test-harness-boundary.py:1004-1023` and `tests/unit/test-handoff-done-when.py:462-508`; retained library/hook REDs in `notes/red-first-receipts.md` §2. |
| SC-04 | operator | **met** | inspection | T-03 | No `.claude/hooks/*` or `.omp/extensions/harness-hooks.ts` path occurs in the 59-path canonical set; pinned hook-path comparison is empty and `hook_guard` has zero callers. |
| SC-05 | reader | **met** | inspection | T-01, T-02, T-03 | Pinned `notes/build-divergences.md` §C and the owning narrowed-handler comments preserve pre-existing rationales; new explanatory prose is marked FEAT-64. Code-review c1 independently reaches the same pinned inspection result. |
| SC-06 | reader | **met** | automated | T-01, T-03 | QA c1: `tests/integration/test-check-plan-routes.py:2807-2960`; retained double-route-load REDs in `notes/red-first-receipts.md` §2. |
| SC-07 | code maintainer | **met** | automated | T-02, T-03 | QA c1 cites `test-board-station.py:270-293`, `test-check-omp-port.py:279-304`, `test-post-merge-sweep.py:1041-1065`, `test-run-unit-tests-layout.py:142-164`, `test-upgrade-config.py:112-137`, `test-gh-sync-ship.py:245-268`, and tool-family counterparts; retained tool REDs are in §2. |
| SC-08 | reader | **met** | automated | T-01, T-03 | QA c1: `tests/unit/test-handoff-done-when.py:462-501`; retained handoff single-parse RED in `notes/red-first-receipts.md` §2. |

Automated evidence pointer: `.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-qa-c1.md` at the pinned-matrix receipt. Inspection evidence pointers name the pinned paths/symbols above. There are no UAT criteria.

## Findings

### GC-64-04

- **Kind:** substance
- **Severity:** high
- **Owner/task:** T-03
- **Concrete scenario:** An operator or reviewer uses pinned `notes/build-divergences.md` §A4 as the exact ruling ledger and concludes that the harness-yaml corpus grew from `101/.harness=97` to `103/.harness=99`, caused only by `plan.yaml` and `feature.json`. The pinned exact appendix instead records `104/.harness=100` with digest `3a1860010aa8ff56`. One added YAML object/count is therefore unaccounted for, so the ledger cannot currently prove that every intentional output byte is exact and ruled.
- **Remedy:** Re-run or otherwise verify the harness-yaml-corpus result at immutable review pin `50dd75c4b97a51f6a3fe7ffb5f27d3c5e2889a31`; make §A4 and `byte-evidence.md` agree on the exact new totals and digest; identify and rule the third added YAML contributor if `104/100` is correct. Do not change production behavior merely to match either record.
- **Reader:** harness-pm
- **Artifact:** `.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c1.md`

## Dismissed and advisory items preserved

- **CR-64-01 / GC-64-03 — dismissed as resolved.** The out-of-scope board-lifecycle source repair is absent, baseline identity is proven, defect #1897 exists, and §B2 measures the old/new observable behavior.
- **GC-64-01 — original finding dismissed as remedied, with a new bounded finding.** The missing per-suite raw/normalized evidence, verbatim differences, and eight-line accounting now exist. The newly discovered contradiction is separately tracked as GC-64-04 rather than reopening the broader category-only defect.
- **GC-64-02 — dismissed as resolved.** Evidence kinds, task traces, and the `2026-09-23` re-sign align without dropping behavior.
- **QA-64-01 — retained advisory, low/form.** Required shared `runs/build-main-direct/digest.md` is absent from the immutable pin. Its mutable worktree copy cannot substantiate a pin-level claim; future review pins should retain required shared validation inputs.
- **Future `hook_guard` fail-open/disclosure concern — dismissed at this pin.** Exception text and an open result could matter when wired, but the pin has zero callers and therefore no actor/capability delta. FEAT-65 must reassess at wiring.
- **Propagated board-lifecycle `TypeError` — dismissed.** It exposes pre-existing #1897 as required by the signed fail-loud policy; no privilege or data boundary changes, and the repair is explicitly out of scope.
- **`FACTORY_GH` executable selection — dismissed.** Environment-based executable selection predates the diff, list-form argv prevents shell injection, and the change only types launch `OSError`.
- **UI scope — advisory dismissed.** Changed diagnostics are unstyled line-oriented CLI text, not a rendered or DESIGN.md-governed surface; accessibility/theme review is not applicable.

## Open questions

None. GC-64-04 has a deterministic evidence-only remedy and does not require a product decision.
