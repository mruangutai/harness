# QA validation c1 — FEAT-54 handoff Done when

## BLUF

**FAIL.** Both configured required kinds pass with non-empty discovery: unit discovers 25 files and integration discovers 44. The repair tests discriminate F-01/F-02/F-03/F-05/F-06, including unsafe authority paths and validator exceptions failing closed, pre-mutation Edit refusal for invalid candidates and invalid UTF-8 existing bytes, blank/reversed Scope, and rejected probe inputs making zero model calls. Mandatory Python risk grading nevertheless fails one c1-changed test helper: `tests/integration/test-check-domain.py::_handoff_pre_edit_cases` is grade 2 against the test-code bar of 3 (ABC 28.0). SC-04 remains a separate, unrelated FEAT-51 root-state blocker and is not a repair-matrix failure.

## Phase 1 expectations and matrix

Before source access, the approved BRIEF/plan required unit coverage for Done-when shape, typed authority grammar/resolution, resolve-on/off separation, AND semantics, and invalid authority types; integration coverage through both real gates for write/edit refusal, malformed and valid blocks, frozen-baseline behavior, whole-file cap, no persisted target re-resolution, and manual-probe registration/isolation. The c1 repair additionally required regression coverage for the five returned findings. Phase 2 found coverage for every expectation and named repair; no observable-contract test was missing, so QA authored no test.

The current repair diff touches logic and unit/integration tests; `logic.always` requires `unit` (`.harness/harness.json:152-156`), and the changed real gate seams warrant `integration` as the matrix floor extension. The changed manual probe is registered `locally_run` and absent from `test_matrix` (`.harness/harness.json:284-295`); per dispatch it was not credential-executed. Its repair is exercised deterministically by the unit kind.

| Kind | State | Exact command | Exit | Discovery |
|---|---|---|---:|---:|
| unit | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 25 files (`pool: 8 workers, 25 files`) |
| integration | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 44 files (`pool: 8 workers, 44 files`) |
| handoff_comprehension | locally-run, not executed | `tests/manual/probe-handoff-comprehension.py` | n/a | n/a |

The unit runner executed `test-handoff-done-when.py` (44 named checks) and `test-probe-handoff-comprehension.py` (6 unittest cases). The integration runner executed the real `test-check-domain.py` and `test-check-state.py` repair cases. There were zero test assertion, import, load, collection, or syntax failures.

## Repair discrimination audit

- **F-01 — authority resolver containment/fail-closed:** `tests/unit/test-handoff-done-when.py:76-86,139-159` separately rejects absolute, traversal, NUL/control, symlink-escape, and special-file pointers, including grammar-only `resolve=False`; `tests/integration/test-check-domain.py:4088-4110,4160-4180` reaches the real write gate and requires exit 2 for those paths and for an injected unexpected validator exception. Removing `_unsafe_rel_path`, root containment/regular-file checks, or the caller exception boundary makes the corresponding exit/message assertion fail.
- **F-02 — comprehension-probe local-file disclosure:** `tests/unit/test-probe-handoff-comprehension.py:49-101` requires outside absolute/repository/traversal, explicit/default symlink, directory, wrong-name, and oversized inputs to leave the model-call recorder empty; the positive control at lines 93-95 requires exactly two calls for a valid note. This is discriminating rather than vacuous: accepting a rejected path produces two recorded calls, while deleting all measurement calls breaks the positive control. The engineer's recorded pre-fix RED measured two calls for outside and symlink inputs (`notes/receipt-harness-dev-ops-validation-c1-F-02.md:12-28`).
- **F-03 — pre-mutation Edit refusal:** `tests/integration/test-check-domain.py:4114-4157` invokes actual PreToolUse `Edit`, requires exit 2 and the specific refusal, and compares before/after bytes. It separately covers an invalid reconstructed candidate and an existing file containing invalid UTF-8, with both files unchanged. Returning early for handoff Edit, using replacement decoding, or validating only PostToolUse makes these assertions fail.
- **F-05/F-06 — Scope value and order:** `tests/unit/test-handoff-done-when.py:68-74`, `tests/integration/test-check-domain.py:4043-4058`, and `tests/integration/test-check-state.py:2178-2224` require a non-empty trimmed Scope and Scope before Authority through the shared parser and both gates. Removing either `_scope_problems`' value check or `_order_problems` makes its named unit assertion and both gate assertions fail while the valid control remains green.

## Mandatory Python risk grading

Worktree-scoped grading was used because c1 is uncommitted and `--base/--head` would grade committed c0 rather than the repair bytes. Exact command:

`python3 .claude/skills/harness/bin/code-grade.py --json .claude/skills/harness/bin/handoff_done_when.py tests/integration/test-check-domain.py tests/integration/test-check-state.py tests/manual/probe-handoff-comprehension.py tests/unit/test-handoff-done-when.py tests/unit/test-probe-handoff-comprehension.py`

Exit **1**, with **311 passing functions**. Filtering the records to functions added or changed by the c1 hunks found all applicable production functions at grade 4 or better, the manual-probe functions at grade 3 or better, and all c1 test functions at grade 3 or better except:

- `tests/integration/test-check-domain.py:4114` `_handoff_pre_edit_cases`: **FAIL**, grade 2, bar 3; cyclomatic 3, cognitive 2, ABC 28.0.

The unchanged legacy failures printed by whole-file grading are outside the c1 function set and are not charged to this repair. `check-domain.sh` is shell and is not graded under the risk-grading skill. No grade-2 exception was supplied or justified for the changed helper, so mandatory grading does not clear.

Risk grading left the worktree bytes and index unchanged. Before and after, SHA-256 values were identical: status census `f3d9e47b1044ba2c61bc7ca175b8b58e5ce539687a8db39c634b30e40978c3b5`, unstaged binary diff `2eaf140981a110b32eee8bc56016ef7978c79a2c3cde122a47ef27de6286ed54`, staged binary diff `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty index diff).

## Automated SC evidence

- SC-01/02: `tests/integration/test-check-domain.py:4033-4058`.
- SC-03: `tests/integration/test-check-domain.py:4061-4079`.
- SC-05: `tests/integration/test-check-domain.py:4202-4214`.
- SC-06: `tests/integration/test-check-domain.py:4114-4157,4183-4199` and `tests/integration/test-check-state.py:2178-2224`.
- SC-09: `tests/integration/test-run-unit-tests-kinds.py:21-40,69-98` (executed within the 44-file integration kind; the live probe was not run).
- SC-12: `tests/unit/test-handoff-done-when.py:110-115`.
- SC-13: `tests/integration/test-check-domain.py:4080-4085`.
- SC-14: `tests/integration/test-check-domain.py:4202-4214` and `tests/integration/test-check-state.py:2244-2258`.
- SC-15: `tests/integration/test-check-state.py:2178-2224`.

## Separate external blocker

SC-04's exact repository-root `check-state.sh` check remains blocked by the unrelated FEAT-51 `status is 'done' but notes/handoff-validate.md is missing` defect already established in the c0 QA evidence. Per dispatch, QA did not rerun or repair FEAT-51 and does not count it among the c1 unit/integration matrix failures. It remains an external ship blocker independent of the c1 risk-grade failure.
