# QA review c2 — FEAT-54 handoff Done when

## BLUF

**FAIL.** The configured unit and integration kinds both pass with non-empty discovery (25 and 44 files), but the literal SC-04 repository-root check exits 1 and the permanent authority-containment tests do not exercise approval pointers for absolute, traversal, symlink, or special-file targets. The implementation currently routes both finding and approval targets through the shared containment reader, but that approval leg is not independently pinned. SC-10 remains pending operator UAT.

Reviewed immutable SHA `53e1745462b75e1c54967b43e2f4fbdfc7037e23` against base `0ec44965a961d19177de871c3bb1f02b701e646b`. Before scope judgment I inspected every file in the named reviewed set: both gates and the shared module, playbook/template/config/decision records, both handoffs, all five permanent test/probe files, and the cited prior authorities and validator digest.

## Phase 1 expectations and delta

Before source access, BRIEF/plan required unit coverage for fixed ordered shape, non-empty Scope, four typed authority grammars/resolvers, AND semantics, resolve-on/off separation, and fail-closed bounded target handling; integration coverage through both real gates for write/Edit refusal, invalid candidate bytes, frozen baseline, persisted grammar without target re-resolution, whole-file cap, and SC-09 registration/exclusion. It also required review-time SC-04/07/08/11 inspections and left SC-10 to UAT.

Phase 2 found every expected contract except independent approval-target containment cases. Existing unsafe-target fixtures use finding pointers for absolute, traversal, symlink, and special files; approval appears only in resolving/unresolvable cases and one control-byte unsafe case. A regression narrowing `_pointer_path()` or `_read_target()` to contain only finding targets could therefore leave the suite green while approval reads outside the repository.

## Matrix and commands

Diff-inferred change types: `logic`, `cross_module` (one new parser imported by two gates), `config` with `touches_config_shape` (new baseline list and locally-run kind mapping), `docs`, and `scaffolding`. The `.harness/harness.json` floor requires `unit` for logic/cross-module and `integration` for cross-module/config-shape. Docs/scaffolding add no active kind. `handoff_comprehension` is `locally_run`, absent from the matrix, and deliberately not executed under this dispatch.

| Kind | State | Configured command run | Discovery | Exit/outcome |
|---|---|---|---:|---|
| unit | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 25 files | 0; all executed files passed |
| integration | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 44 files | 0; all executed files passed |
| handoff_comprehension | locally-run, not executed | `tests/manual/probe-handoff-comprehension.py` | n/a | n/a; credentialled probe prohibited here |

The unit transcript names `test-handoff-done-when.py` exit 0 and `test-probe-handoff-comprehension.py` exit 0 (`Ran 6 tests`, `OK`). The integration runner's 44-file non-empty bucket includes the named `test-check-domain.py`, `test-check-state.py`, and `test-run-unit-tests-kinds.py`; the overall command exited 0. `matrix_ok: false` because a required high-risk authority leg lacks permanent regression coverage despite both required kinds being green.

## Literal inspections

- **SC-04 FAIL:** from repository root, exact command `bash .claude/skills/harness/bin/check-state.sh` exited **1**. No output line named `Done when`. Actual violations included the unrelated FEAT-51 missing `notes/handoff-validate.md` and five malformed lead-digest-contract records under FEAT-54 run directories. Per the criterion, no absence-of-`Done when` observation can override the nonzero exit.
- **SC-07 PASS:** `check-domain.sh:1562-1563` imports/calls `handoff_done_when.problems(..., resolve=True)`; `check-state.sh:54,1251` imports/calls the same implementation with `resolve=False`. The reviewed gates carry no second Done-when target resolver.
- **SC-08 PASS:** template `HANDOFF.md:4-16`, playbook `SKILL.md:310-316`, DEC-159 `DECISIONS.md:3698-3727`, DEC-214 `:6696-6716`, and both gate heading lists/messages state five sections and name `## Done when`; only the authorized historical measurements remain four-section prose.
- **SC-11 PASS:** merge base was exactly `0ec44965a961d19177de871c3bb1f02b701e646b`; primary intersection was empty. The positive control contained exactly `handoff-build.md` and `handoff-plan.md`, identical to the added-only set; set diff exited 0.

## Permanent contract coverage

- SC-01/02: `tests/integration/test-check-domain.py:4033-4058`.
- SC-03: `tests/integration/test-check-domain.py:4061-4079` covers resolving/unresolvable pairs for all four authority types.
- SC-05: `tests/integration/test-check-domain.py:4211-4223` covers 60 allowed and 61 refused.
- SC-06: `tests/integration/test-check-domain.py:4114-4166,4192-4208` and `tests/integration/test-check-state.py:2178-2223`.
- SC-09: `tests/integration/test-run-unit-tests-kinds.py:20-98` positively checks the real locally-run entry, removal/empty-detect mutants, non-empty unit/integration controls, and `--kind all` exclusion of the manual probe.
- SC-12: `tests/unit/test-handoff-done-when.py:110-115` distinguishes AND from ANY.
- SC-13: `tests/integration/test-check-domain.py:4080-4085`.
- SC-14: `tests/integration/test-check-domain.py:4211-4223` and `tests/integration/test-check-state.py:2244-2258`.
- SC-15: `tests/integration/test-check-state.py:2178-2223` pairs no target re-resolution with continued shape/grammar enforcement.
- F-02 zero-call admission: `tests/unit/test-probe-handoff-comprehension.py:41-101` binds every rejected path to `self.calls == []` and the valid control to exactly two calls.
- F-03 pre-mutation Edit refusal: `tests/integration/test-check-domain.py:4114-4166` requires exit 2 and byte identity for an invalid candidate and invalid UTF-8 existing bytes.
- Scope label/order: `tests/unit/test-handoff-done-when.py:68-74`, `tests/integration/test-check-domain.py:4043-4058`, and `tests/integration/test-check-state.py:2189-2221` cover blank Scope and Authority-before-Scope separately.
- Authority containment gap: `tests/unit/test-handoff-done-when.py:76-86,139-159` and `tests/integration/test-check-domain.py:4088-4110` cover finding absolute/traversal/symlink/special paths, with only approval control-byte coverage; no approval absolute/traversal/symlink/special fixture exists.

## Changed-function risk grade

The prescribed whole-file command over the six Python files exited 1 with `passing: 314`; unchanged legacy records outside the FEAT-54 changed-function census cause that aggregate exit and are not substituted for the scoped result. A current extraction showed all 24 functions in the newly added `handoff_done_when.py` at grade 4 or 5 against bar 4. The repaired test helpers are `_handoff_valid_pre_edit_cases` grade 4/bar 3, `_handoff_invalid_utf8_pre_edit_case` grade 4/bar 3, `_handoff_pre_edit_cases` grade 5/bar 3, and manual-probe `measure_note` grade 4/bar 3. The exact prior 62-pair changed-function identity assertion at `notes/qa-validation-c2.md:29-48`, repeated post-simplify at `notes/qa-validation-post-simplify-c2.md:19-37`, exited 0 with 20 production and 42 test functions and minimum grade 3. F-07 is therefore closed; the whole-file legacy exit is recorded, not waived as though it were green.

## F-01–F-07 reassessment

- **F-01 — LIVE as a verification gap (high, must_fix):** current implementation is contained/fail-closed through `_pointer_path`, `_unsafe_rel_path`, `_read_target`, and the caller exception boundary, but permanent tests do not independently exercise approval absolute/traversal/symlink/special targets. **Scenario:** a future edit removes `approval:` from the common path-containment route; every existing unsafe-target test remains green while an authored approval pointer reads a file outside the repository. **Owner:** Main direct test lane under DEC-174.
- **F-02 — assessed-and-dismissed/closed:** explicit/default outside, traversal, symlink, directory, wrong-name, and oversized probe inputs all assert zero model calls; a valid note asserts two calls (`tests/unit/test-probe-handoff-comprehension.py:41-101`). Owner lane complete: harness-dev-ops.
- **F-03 — assessed-and-dismissed/closed:** actual PreToolUse Edit reconstruction refuses before mutation, including invalid UTF-8, and asserts byte identity (`test-check-domain.py:4114-4166`). Owner lane complete: Main direct/DEC-174.
- **F-04 — LIVE (high, must_fix):** literal SC-04 command exits 1. **Scenario:** Harness entry at the reviewed tree reports state violations and cannot establish the clean-corpus criterion. **Owner:** Main direct corpus/state reconciliation; do not repair or waive in this review.
- **F-05 — assessed-and-dismissed/closed:** blank and whitespace-only Scope labels are rejected by unit and both real gates; valid controls remain (`test-handoff-done-when.py:68-74`, gate cases above). Owner lane complete: Main direct/DEC-174.
- **F-06 — assessed-and-dismissed/closed:** product ruling requires Scope before all Authority lines; implementation and both gates reject reversed order (`research-FEAT-54-validation-order-c1.md:5-23`; tests above). Owner lane complete: product ruling plus Main direct.
- **F-07 — assessed-and-dismissed/closed:** current changed production functions meet bar 4 and changed tests/probe meet bar 3; repaired helper grades are recorded above. Owner lanes complete: Main direct and harness-dev-ops.

## Findings

### F-QA-C2-01 — approval containment is not independently regression-tested

- **Severity:** high
- **Concrete failure scenario:** removing approval pointers from the shared containment path leaves all current absolute/traversal/symlink/special fixtures green while an approval authority can open an out-of-repository or special target.
- **Evidence:** named permanent tests and missing approval fixtures listed above; current source safety is reasoned from `handoff_done_when.py:_pointer_path/_read_target`, not mutation-proven for this leg.
- **Owner lane:** Main direct test mutation under DEC-174.
- **Disposition:** must_fix.

### F-QA-C2-02 — literal SC-04 root state check remains red

- **Severity:** high
- **Concrete failure scenario:** the required review-time command exits 1, so a later reader cannot treat the repository as state-clean at the pin even though no output names `Done when`.
- **Evidence:** exact root command and actual violations recorded above.
- **Owner lane:** Main direct corpus/state reconciliation.
- **Disposition:** must_fix.

No files other than this reviewer note were authored or edited. The credentialled probe, SC-10 UAT, formatters, linters, unrelated validation, and project-wide suites were not run.
