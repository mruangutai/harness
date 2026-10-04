# FEAT-1928 pre-review code-risk dispositions

Base: current-main reconciliation `e0bb9814`. Production target: grade 4; test target: grade 3. Grade-2 dispositions below are explicit reasons, not a claim that the grader exits zero. Existing below-bar functions untouched by this feature are not a touch-it-fix-it ratchet.

The new probe's four grade-1 functions were separated into named protocol/evidence phases without changing public signatures, evidence fields, or predicates. An actual 43-frame live transcript produced exactly the same derived evidence and all 18 predicates/details before and after the refactor. Its recorded receipt passed all 33 verification checks after the refactor; that receipt binds the earlier commit, not the uncommitted refactor. A clean-tree live rerun is required before review.

Schema walkers now share depth-first reference traversal. The list-entry test was separated by actual schema family, preserving its positive and negative cases. `python3 tests/unit/test-digest-schemas.py`: 32 tests passed. The panel refusal helper preserves all eight refusal assertions and the final byte-identical-plan assertion; `python3 tests/integration/test-plan-merge.py` passed. Historical parity generators were throwaway capture scaffolds: removed after capture, with all fixtures/results/table retained and source provenance documented in `validator-parity.md`.

Final code-only candidate `4379809b1ce7e37e89407b2ade7912abc898fed9`: changed-function grading against `e0bb9814` reports 203 passing functions, eight grade-2 reason requirements, and no high findings. All eight requirements are named below; the reduced existing panel-fixture function is also documented. A throwaway comparison exercised the original and split tests against the actual validator and preserved all 36 schema-validation inputs and accept/reject outcomes.

The clean-tree live rerun at that candidate passed 18/18 checks, and its fresh receipt passed 33/33 verification checks. The complete Python pool passed all 120 files with eight workers in 112.95 seconds; source no longer awaits the live rerun described in the earlier refactor paragraph.

## Grade-2 reasons

- `tests/manual/probe-digest-object-contract.py::_task_dispatch`: one ordered fold correlates task arguments, execution revisions, and dispatch errors. Splitting those correlated events would obscure which dispatch actually ran.
- `tests/manual/probe-digest-object-contract.py::_yields`: one ordered fold pairs yield arguments with their tool results in the same child session; preserving that correlation is the behavior under test.
- `tests/manual/probe-digest-object-contract.py::derive`: explicitly assembles the evidence record from separately named dispatch, job, child, and yield phases. Remaining assignments describe the recorded contract rather than nested control flow.
- `tests/manual/probe-digest-object-contract.py::run_live`: the coherent RPC lifecycle opens one session, requests one task, pumps its events, and closes resources; separating resource ownership would reduce clarity.
- `tests/manual/probe-digest-object-contract.py::verify`: coordinates independently named transcript, runtime identity, Harness identity, and outcome checks, retaining the two early missing-input failures and all original reported checks.
- `tests/manual/probe-digest-object-contract.py::main`: CLI selection and exit-status handling are kept together so dry run, verification, and actual live execution remain visibly distinct.
- `tests/unit/test-digest-schemas.py::_object_shape_violations`: the local conjunctions describe the complete closed-object invariant and the three equivalent JSON-null spellings; recursion is already isolated in the shared walker.
- `tests/integration/test-plan-merge.py::case_f59_record_panel_refuses_a_finding_without_kind`: one fixture demonstrates eight independent consumer-visible refusals followed by the shared atomicity invariant. Its ABC fell from 49.2 (grade 1) to 31.4 (grade 2), below the pre-feature 38.8; refusal checking is centralized without dropping an assertion.
- `tests/unit/test-digest-dev-skill.py::check_refusal`: one cohesive documentation-contract check validates the concrete BLOCKED example against the actual dev schema, keeps the receipt rule in digest-dev rather than TDD, and checks the dev personas load that skill without inline schemas. These checks share the single refusal-guidance ownership invariant.
