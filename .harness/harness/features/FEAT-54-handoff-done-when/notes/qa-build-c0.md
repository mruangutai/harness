# FEAT-54 build QA gate — c0

## Verdict

**FAIL.** The configured unit and integration commands are correctly configured, discover the FEAT-54 tests, and pass with zero test failures. The build still cannot receive a QA PASS: the required contemporaneous RED evidence is not durable for all three mandated TDD pairs, and several integration-evidence criteria assert only a weaker substring than the signed criterion requires.

Inspected range: approved base `b7956fc4` through HEAD `ec0f897903c85d70c6b377cf8fde44f5bb58af74`. The complete range diff was read, including changes merged after the approved base; no changed surface raises a hard kind beyond unit and integration. For SC-11 only, its own prescribed dynamic merge-base command currently resolves `main`/HEAD to `0ec44965a961d19177de871c3bb1f02b701e646b`; its primary intersection was empty and its positive control was the two newly added FEAT-54 handoff notes, exactly equal to the added-note arm.

## Phase 1 expected coverage and matrix derivation

Before source access, BRIEF.md and plan.yaml implied these required checks:

- `logic` (T-01, T-02, T-03, T-04, T-06, T-07, T-12) -> `unit` always; the gate-to-module and persisted-state seams additionally require integration from the actual changed surfaces.
- `config` (T-05) changes top-level config shape and T-09 adds a nested `test_kinds` entry -> `integration` through `touches_config_shape` (DEC-212).
- `docs` (T-08, T-10, T-11) and `scaffolding` (T-09) add no matrix floor, but their observable contract needs the task-scoped documentation, corpus, dry-run, registration, and isolation checks.
- `handoff_comprehension` is configured `locally_run`; it is reporting-only and is not a hard matrix kind.

Phase 2 delta: unit and integration tests exist and run the changed code. Coverage is broad and non-vacuous, but the signed integration assertions for SC-01, SC-02, SC-13, and SC-15 are weaker than Phase 1 required. No production or test file was edited.

## Required kinds

| Kind | Exact configured command | Result | Discovery / coverage evidence | Gate disposition |
|---|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | exit 0; 24 files; zero failed scripts | `tests/unit/test-handoff-done-when.py` ran and printed 32 named PASS cases. It covers missing/present shape, 0/2 Scope, 0/5 Authority, all four resolving/unresolving types, both illegal-authority forms, AND-vs-ANY, and resolve=False boundaries (`tests/unit/test-handoff-done-when.py:45-116`). | satisfied |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 0; 44 files; zero failed scripts | The runner executed `test-check-domain.py`, `test-check-state.py`, and `test-run-unit-tests-kinds.py`. FEAT-54 named cases exercised the real write gate (`test-check-domain.py:3994-4075`), real state gate over fixtures (`test-check-state.py:2141-2225`), and probe registration/isolation with config mutants (`test-run-unit-tests-kinds.py:21-102`). | **missing signed assertion detail; hard gate FAIL** |

`HARNESS_AGENT_TYPE` was unset for both matrix invocations to avoid the repository's known unrelated plan-merge test contamination. This changes no configured command argument or suite selection.

## Changed-contract evidence

- T-01/T-02 direct unit command: exit 0, all 32 named cases passed.
- T-03/T-04 direct write-gate integration command: exit 0; all FEAT-54 handoff cases passed, including 60/61 whole-file boundaries and the 60-line/25-line-Trust no-per-section-cap case.
- T-05 literal verify: exit 0, `ok 141`; baseline is present, unique, every path exists, and none carries `## Done when`.
- T-06/T-07 literal GREEN/live-corpus clause: integration test exit 0; source positive control found `done when`; live `check-state.sh` returned 1 for unrelated state notes and emitted no `Done when` line (`ok rc=1`).
- T-08 literal verify: exit 0; template carries `## Done when`, `Scope:`, `Authority:`, playbook says five sections, and neither file says four sections.
- T-09 literal verify: exit 0; both dry runs named the two arms and planned two unexecuted calls, the audit hook reported `ok: dry run made no model call`, config registration passed, and layout check passed.
- T-10: durable receipt `notes/receipt-harness-documentor-t10.md:10` records the exact plan verify at the landed task and exit 0, including byte-identical decision-index regeneration. It was not rerun because its generator writes the governed documentation and this QA dispatch forbids edits.
- T-11 literal verify: exit 0, `ok 2 notes compliant`; both notes are non-baselined, within 60 lines, shaped correctly, and their authorities resolve at write-time semantics.
- T-12 literal verify: exit 0, `ok`; registration-mutant test and planted-layout positive control both passed.
- SC-07 inspection: `check-domain.sh:1562,1567` and `check-state.sh:54,1251` are the two imports/calls into the single `handoff_done_when` implementation; neither gate contains another `Scope:`/`Authority:` parser.
- SC-08 inspection: no live `four sections`, `four fixed`, old cap enumeration, or `HANDOFF_HEADINGS` match remains in the specified template, playbook, decision record, or gate scripts.
- SC-11 inspection: primary historical-note intersection empty; positive control contains exactly `handoff-build.md` and `handoff-plan.md`, equal to the added-note set.

## TDD audit

The three RED verify clauses in the dispatch match plan.yaml literally at T-01 lines 153-155, T-03 lines 299-301, and T-06 lines 454-456; the corresponding GREEN clauses match T-02 lines 231-232, T-04 lines 357-358, and T-07 lines 527-534. No paraphrased command was substituted and RED was not recreated by modifying this worktree.

| Pair | Repository order | Durable actual RED/GREEN evidence | Disposition |
|---|---|---|---|
| T-01 -> T-02 | Test and module both first appear in `157377d9`; the same commit also marks/lands both tasks. | Current GREEN is measured. No earlier commit or durable receipt records the literal T-01 RED execution. | inadequate |
| T-03 -> T-04 | Test changes and `check-domain.sh` implementation both land in `157377d9`. | Current GREEN is measured. No earlier commit or durable receipt records the literal T-03 RED execution. | inadequate |
| T-06 -> T-07 | Test lands first in `9d4d03c4`; production gate lands later in `fd98b163`. | Commit order is test-first and current GREEN is measured, but no durable receipt records the literal T-06 RED output/exit. | inadequate for the requested actual-red audit |

## Locally-run reporting status

`.harness/harness.json:284-289` registers `handoff_comprehension` with `status: locally_run`, and detect/cmd both `tests/manual/probe-handoff-comprehension.py`; it is absent from `test_matrix`. The dry-run safety and normal-suite isolation checks passed. A real scored probe was **not run**: `omp` exists at `/Users/molchairuangutai/.bun/bin/omp`, but the process environment exposes no Anthropic/OpenAI model credential variable (only `CLAUDECODE`), so credentialled host support could not be established. This reporting-only kind is not promoted into unit/integration and its absent score is not a must-fix.

## Coverage gaps

1. SC-01 requires the integration refusal to name both the missing section and template. `test-check-domain.py:4027` asserts only `## Done when`; only the unit test checks `templates/HANDOFF.md` (`test-handoff-done-when.py:47-49`).
2. SC-02 requires each integration refusal to name the broken count. `test-check-domain.py:4029-4038` checks only `Scope` or `Authority`, while the stronger numeric assertions exist only in unit (`test-handoff-done-when.py:56-65`).
3. SC-13 requires the integration refusal to list all four legal prefixes. `test-check-domain.py:4053-4055` checks only `plan-task:`; the all-four assertion exists only in unit (`test-handoff-done-when.py:82-87`).
4. SC-15 requires the persisted-state malformed block report to name the broken count. `test-check-state.py:2178-2194` establishes a report but does not assert the `2` Scope count.

## Ranked must-fix

1. **Provide contemporaneous durable execution evidence for the exact T-01, T-03, and T-06 RED clauses and their subsequent GREENs.** History cannot prove T-01/T-02 or T-03/T-04 ordering because each pair co-landed in `157377d9`; T-06/T-07 has correct commit order but no durable RED execution record was found. Per dispatch, do not manufacture this by recreating RED in the completed worktree; if no contemporaneous record exists, the TDD acceptance condition needs an explicit operator disposition.
2. **Strengthen the integration tests to bind their signed subjects:** template name for SC-01, exact counts for SC-02, all four legal prefixes for SC-13, and the exact Scope count for SC-15. Re-run the configured integration command afterward.
