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

## Current-main final pre-pin check

The final comparison against integrated main `af2a958ab06c0d6fc026b363b59fc3147e3982f1` found two high blockers: production `prune-run-evidence.py::_load_record` graded 3, and the current native probe's `derive` graded 1. Main alone applied behavior-preserving refactors under DEC-174: isolate the review-pin predicate, correlate the task result separately, and isolate the native null-yield event evidence.

The actual changed boundaries now grade: `_has_review_pin` 5, `_load_record` 4, `_task_result_job` 4, `_null_rejection` 5, and `derive` 3. `_native_yield_started` grades 2: it intentionally checks one event's type, owning job, tool execution phase, tool name, and call identity together; weakening or scattering that correlation would obscure the exact native execution proved by the receipt.

Before and after refactoring, the actual pruning CLI regression suite passed every check. The actual recorded native transcript independently re-derived identical evidence and passed all 33 receipt checks after the refactor. No assertion or evidence predicate was removed or weakened. That receipt identifies clean executed HEAD `9359457d`, not the subsequent uncommitted refactor; a new clean-tree native run remains required before pinning.

Additional grade-2 reasons in the current-main range:

- `digest_destination.py::authorized_destination`: identity, linked-checkout, registered-run and exact-destination checks form one complete authorization proof; splitting it would hide their coupled fail-closed boundary.
- `probe-inflight-claim-lifecycle.py::run_live`: resource creation and mandatory session, claim and run-record cleanup share one lifetime and its `try/finally`.
- `probe-inflight-claim-lifecycle.py::receipt_header`: assemble the provenance envelope together so executed launcher identity and release-source metadata remain visibly distinct.

The earlier numeric totals and candidate SHAs above remain historical evidence, not the final current-main grading result. Final changed-function totals and the clean-source native rerun must be recorded after the source commit.

Final committed source candidate `98b6c38332bf270f4c88dbc89d7b9d044c7b858d`, compared with `af2a958ab06c0d6fc026b363b59fc3147e3982f1`: grader exit 0; 241 gated functions, 230 meeting their bars, 11 grade-2 functions with the written reasons above, zero high findings, zero ungraded files. The fresh actual OpenAI native run at that clean candidate passed 18/18; its receipt independently verified 33/33. The final complete Python pool passed all 120 files using eight workers in 130.15 seconds (`artifact://570`). Subsequent receipt, plan-station, and review-pin commits are metadata only; this paragraph does not claim independent validation or ship acceptance.

## Latest upstream integration

Integrated source `c81a57b6`, compared with current upstream `91e88653`: the pre-cutover control-plane grader exited 0, with 230 functions meeting their bars and the same 11 grade-2 reason requirements named above; no high findings. The complete integrated Python pool passed all 120 files with eight workers in 141.82 seconds (`artifact://710`). The fresh clean-tree native OpenAI YieldTool probe passed 18/18 and its receipt independently verified 33/33. Four separate merge-resolution quality angles passed without an apply or new rework cycles. These are execution and quality evidence, not a substitute for independent validation of the new review pin.
