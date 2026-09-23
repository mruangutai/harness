# Pinned QA gate — FEAT-64 c1

Pin `50dd75c4b97a51f6a3fe7ffb5f27d3c5e2889a31`; baseline `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983`. I derived and broadcast this canonical ordered 59-file set:

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

## Matrix and evidence

All T-01/T-02/T-03 tasks are `cross_module`; `.harness/harness.json:174-179` requires unit and integration. In detached pin worktree, `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` ran 42 named files and exited 0; the equivalent integration command ran 69 and exited 0.

SC-01: `byte-evidence.md` records 27 raw/normalised pairs and all normalised differing lines; `build-divergences.md §A` accounts for eight removals. SC-02: `test-broad-catch-census.py:83-96` and `test-check-plan-routes.py:2912-2922`. SC-03: `test-harness-boundary.py:1004-1023` and `test-handoff-done-when.py:462-508`. SC-06: `test-check-plan-routes.py:2807-2960`. SC-07: `test-board-station.py:270-293`, `test-check-omp-port.py:279-304`, `test-post-merge-sweep.py:1041-1065`, `test-run-unit-tests-layout.py:142-164`, `test-upgrade-config.py:112-137`, and `test-gh-sync-ship.py:245-268`. SC-08: `test-handoff-done-when.py:462-501`.

`red-first-receipts.md §2` supplies retained pre-fix REDs: SC-01 across T-01/T-02/T-03; SC-02’s ceiling/mutant rows; SC-03’s library and hook rows; SC-06’s double route-load rows; SC-07’s T-02 tool rows; and SC-08’s handoff single-parse row.

## Independent c0 remedy regrade

- CR-64-01/GC-64-03 closed: `git diff --quiet baseline..pin -- board_lifecycle.py` exited 0; B2 says baseline-identical and names #1897.
- GC-64-01 FAIL / GC-64-04: `byte-evidence.md` records `101/.harness=97 → 104/.harness=100` for `test-harness-yaml-corpus.py`, while `build-divergences.md §A4` states `101/.harness=97 → 103/.harness=99` and attributes only two new files. The conflicting ledger cannot establish SC-01's complete, exact-byte divergence accounting.
- GC-64-02 closed: pin BRIEF/plan split SC-03/SC-07 and SC-06/SC-08; pin commit records revocation/re-signing and plan approval is approved on 2026-09-23.

Finding GC-64-04 (substance, high; owner T-03): when the corpus adds three files, the ledger reports two, so a real unlisted byte difference can be treated as accounted for; regenerate the §A4 old/new bytes and ruling from the recorded raw evidence. Advisory QA-64-01 (form, low; validate evidence record): required shared `runs/build-main-direct/digest.md` is absent at the pin, so cannot be inspected via `git show`; retain it in future pins when required as validation input. CR-64-01/GC-64-03 and GC-64-02 remain dismissed for the closure evidence above.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Pinned matrix passes, but GC-64-04 leaves SC-01's exact-byte divergence ledger contradictory."
  suite: pass
  failures: 1
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 42 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 69 }
  coverage_gaps: ["SC-01 exact-byte ledger: build-divergences.md §A4 conflicts with byte-evidence.md for test-harness-yaml-corpus.py (103/99 versus 104/100)."]
  sc_evidence:
    - { id: SC-01, test: "partial — notes/byte-evidence.md conflicts with notes/build-divergences.md §A4" }
    - { id: SC-02, test: "tests/unit/test-broad-catch-census.py:83-96; tests/integration/test-check-plan-routes.py:2912-2922" }
    - { id: SC-03, test: "tests/unit/test-harness-boundary.py:1004-1023; tests/unit/test-handoff-done-when.py:462-508" }
    - { id: SC-06, test: "tests/integration/test-check-plan-routes.py:2807-2960" }
    - { id: SC-07, test: "tests/integration/test-board-station.py:270-293 and tool-family integration counterparts" }
    - { id: SC-08, test: "tests/unit/test-handoff-done-when.py:462-501" }
  fail_first:
    - { sc: SC-01, evidence: "notes/red-first-receipts.md §2 T-01/T-02/T-03 REDs" }
    - { sc: SC-02, evidence: "notes/red-first-receipts.md §2 T-03 ceiling and mutant REDs" }
    - { sc: SC-03, evidence: "notes/red-first-receipts.md §2 T-01 boundary/hook REDs" }
    - { sc: SC-06, evidence: "notes/red-first-receipts.md §2 T-03 double-route-load REDs" }
    - { sc: SC-07, evidence: "notes/red-first-receipts.md §2 T-02 tool-family REDs" }
    - { sc: SC-08, evidence: "notes/red-first-receipts.md §2 T-01 handoff single-parse RED" }
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-qa-c1.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-qa-c1.md
```