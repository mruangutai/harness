# QA review c4 — FEAT-54 handoff Done when

## BLUF

**PASS.** At immutable candidate `f05e1e6cd74c7d91580dd6ef565a00432faac1ad`, both configured required kinds pass with non-empty discovery (25 unit files and 44 integration files), all five focused FEAT-54 checks pass with named, subject-binding assertions, and exact repository-root SC-04 exits 0 with zero `Done when` findings and zero `VIOLATION` lines. C3 F-04 is therefore closed at the current pin. F-01–F-03 and F-05–F-09 remain closed on independently re-read current-pin code and freshly executed evidence. SEC-F-08 remains a medium, non-gating advisory under `gates.review: advisory_unless_high`.

The inspected worktree HEAD was exactly `f05e1e6cd74c7d91580dd6ef565a00432faac1ad`; `git diff --quiet HEAD -- <the exact 16 paths below>` exited 0 before this note was authored.

## Phase 1 expectations and matrix inference

Before source access, the approved BRIEF and plan required unit coverage for the shared parser's one-to-four authority AND semantics, non-empty ordered Scope, four typed pointer grammars, write-time resolution versus persisted grammar-only mode, strict heading boundaries, strict approval headings, and fail-closed authority reads. Integration coverage was required through both real gates for Write/Edit refusal before mutation, frozen-baseline behavior, persisted non-resolution, whole-file 60/61 boundary, absence of a per-section cap, and manual-probe registration/exclusion. Review-time inspections were required for SC-04, SC-07, SC-08, and SC-11; SC-10 is operator UAT and was expressly not run.

Plan change types are `logic` (T-01/02/03/04/06/07/12), `config` (T-05), `docs` (T-08/10/11), and `scaffolding` (T-09). `.harness/harness.json` requires `unit` for every `logic` task. T-05 changes config shape by adding a list/note and a `test_kinds` mapping entry, so `config.when: touches_config_shape` requires `integration`; the shared module/two-real-gate contract independently warrants integration. Docs and scaffolding add no configured kind. `handoff_comprehension` is registered `locally_run`, is absent from `test_matrix`, and is reporting-only; no credentialled run was substituted for the release gate.

## Exact configured matrix

Both configured commands were run from repository root with only `HARNESS_AGENT_TYPE` unset to prevent the documented governed-agent identity leak; the command portion is byte-for-byte the configured `test_kinds.<kind>.cmd`.

- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` — exit 0; runner reported `pool: 8 workers, 25 files`; non-zero discovery; it executed both FEAT-54 unit files.
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` — exit 0; runner reported `pool: 8 workers, 44 files`; non-zero discovery; it executed all three FEAT-54 integration files.

No assertion, import, collection, syntax, load, or discovery failure occurred. Required-kind states are therefore `unit: satisfied` and `integration: satisfied`; `matrix_ok: true`.

## Focused FEAT-54 checks and non-vacuity

- `python3 tests/unit/test-handoff-done-when.py` — exit 0, **54/54 named assertions**. Negative and positive controls bind returned problem content, not labels alone: resolving/unresolving pairs exist for all four pointer types; four-good versus one-dangling distinguishes AND from ANY; `resolve=False` is paired against the same dangling inputs; unsafe finding and approval paths are independent; nested and duplicate headings and both invalid ATX forms each have their own negative case beside valid controls.
- `python3 tests/unit/test-probe-handoff-comprehension.py` — exit 0, **6/6 test methods**. Every rejected outside/traversal/symlink/directory/wrong-name/oversized subject asserts the actual model-call log is empty; the valid control asserts exactly two calls, so deleting all calls cannot satisfy the suite.
- `python3 tests/integration/test-check-domain.py` — exit 0, **41/41 FEAT-54 handoff outcomes**. Cases invoke the real hook and bind exit plus diagnostic; invalid reconstructed and invalid-UTF-8 Edit cases also bind byte identity, and the valid controls prevent an always-refuse implementation from passing.
- `python3 tests/integration/test-check-state.py` — exit 0, **17/17 FEAT-54 outcomes**. The same fixture subjects distinguish baselined/non-baselined presence, malformed shape, absent target non-rot, grammar enforcement, nested/duplicate headings, corpus byte/mtime identity, and the positive 60-line long-section case.
- `python3 tests/integration/test-run-unit-tests-kinds.py` — exit 0, **5/5 named checks**. The real config is asserted positively; empty-detect and removed-kind mutants each become loud; a failing sentinel manual probe is demonstrably not executed by `--kind all`, while unit and integration sentinels do execute.
- `python3 .claude/skills/harness/bin/code-grade.py --base 0ec44965a961d19177de871c3bb1f02b701e646b --head f05e1e6cd74c7d91580dd6ef565a00432faac1ad` — exit 0, `PASSING: 86`; every production identity meets bar 4 and every test/manual-probe identity meets bar 3.

No perturbation was authored in this gate-only dispatch. Discrimination claims above are measured from the tests' paired observable controls and, for probe registration, the checked-in mutant mappings; claims about direct source mechanics are explicitly inspection evidence.

## SC-04 and required inspections

- **SC-04 PASS:** exact root command `bash .claude/skills/harness/bin/check-state.sh` exited **0**. Search of its complete 812-line capture found **0** case-sensitive `Done when` matches and **0** `VIOLATION` matches. The output consists only of advisory `note` rows. This independently closes c3 F-04; the previous FEAT-51 missing-handoff violation is absent at this pin.
- **SC-07 PASS (inspection):** `check-domain.sh:1561-1566` imports and calls `handoff_done_when.problems(..., resolve=True)` and fails closed; `check-state.sh:53-56,1243-1251` imports and calls the same implementation with `resolve=False`. Neither gate contains a second Done-when block parser or target resolver.
- **SC-08 PASS (inspection):** template/playbook, DEC-159/214, and both gate implementations state five sections and name `## Done when`. The surviving four-heading statements at `check-state.sh:1194-1202,1215-1219` are the BRIEF-authorized, commit/feature-bound historical observations, not current-contract claims.
- **SC-11 PASS:** with `BASE=0ec44965a961d19177de871c3bb1f02b701e646b`, the prescribed historical-note intersection printed nothing. The positive-control arm was non-empty with four paths and equaled the added-only arm set-for-set: FEAT-51 `handoff-validate.md` plus FEAT-54 `handoff-build.md`, `handoff-plan.md`, and `handoff-validate.md`. No base-existing handoff was touched.

## Exact 16-path inspection census

1. `.claude/skills/harness/bin/handoff_done_when.py`
2. `tests/unit/test-handoff-done-when.py`
3. `tests/unit/test-probe-handoff-comprehension.py`
4. `tests/integration/test-check-domain.py`
5. `.claude/skills/harness/bin/check-domain.sh`
6. `.harness/harness.json`
7. `tests/integration/test-check-state.py`
8. `.claude/skills/harness/bin/check-state.sh`
9. `.claude/skills/harness/templates/HANDOFF.md`
10. `.claude/skills/harness/SKILL.md`
11. `tests/manual/probe-handoff-comprehension.py`
12. `.harness/harness/docs/DECISIONS.md`
13. `.harness/harness/docs/DECISIONS-INDEX.md`
14. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md`
15. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md`
16. `tests/integration/test-run-unit-tests-kinds.py`

Authorities/evidence also read: approved `BRIEF.md`, approved `plan.yaml`, c3 validator `digest.md`, and all four c3 reader notes, including `review-harness-qa-c3.md`. Current-pin claims above were re-measured rather than inherited.

## C3 finding reassessment at the current pin

- **F-01 closed.** Failure scenario excluded: absolute/traversal/control-bearing finding or approval authorities, symlink escapes, and special files cannot authorize an external or blocking target. `_unsafe_rel_path` and `_read_target` enforce grammar, containment, regular-file, size, and UTF-8 bounds (`handoff_done_when.py:63-101`); resolver exceptions become refusal messages (`:241-252`). Fresh parser and real-hook cases independently bind finding and approval subjects and preserve resolving controls. Owner lane if regressed: Main direct gate/module lane under DEC-174.
- **F-02 closed.** Failure scenario excluded: a rejected local path cannot reach the credentialled model. Admission precedes `ask` (`probe-handoff-comprehension.py:54-109`); fresh tests bind all rejection classes to zero calls and a valid note to two calls. Owner lane if regressed: harness-dev-ops via harness-eng-lead.
- **F-03 closed.** Failure scenario excluded: an invalid or non-UTF-8 handoff Edit cannot mutate before the refusal. Fresh real-hook tests require exit 2 and byte identity for both candidates (`test-check-domain.py:4138-4190`). Owner lane if regressed: Main direct gate lane.
- **F-04 closed.** The exact root SC-04 command now exits 0 with zero Done-when findings and zero violations. Owner lane of the repaired external corpus item was harness-orchestrator/Main.
- **F-05 closed.** Blank/whitespace-only Scope values are refused by `_scope_problems` and fresh unit/write/state cases (`handoff_done_when.py:187-192`). Owner lane if regressed: Main direct shared-module/gate tests.
- **F-06 closed.** Authority-before-Scope is refused by `_order_problems`; fresh unit/write/state cases bind the approved order while valid ordering passes (`handoff_done_when.py:209-221`). Owner lane if regressed: Main direct.
- **F-07 closed.** Current base/head complexity measurement passes all 86 changed function identities at the applicable bars. Owner lane if regressed: engineering owner of the failing identity.
- **F-08 closed.** Nested H3 prose cannot truncate the body and duplicate Done-when H2 sections are refused; fresh unit/write/state negatives bind both subjects (`handoff_done_when.py:24-35,272-287`). Owner lane if regressed: Main direct shared-module/gate tests.
- **F-09 closed.** `#Approval` and seven-hash lookalikes are separately refused beside a valid `## Approval` target (`handoff_done_when.py:154-171`; fresh unit/write-gate cases). Owner lane if regressed: Main direct shared module/tests.
- **SEC-F-08 survives, med advisory (reasoned current-pin inspection).** Repository/model-controlled path, fact, provider-error, and answer text still reach raw `print` sinks (`tests/manual/probe-handoff-comprehension.py:86-98,157-197`). Concrete scenario: ESC/OSC bytes in an admitted note or model response can rewrite visible terminal evidence or terminal state during the locally-run probe. This does not gate under `.harness/harness.json` `review: advisory_unless_high`. Owner lane: harness-dev-ops via harness-eng-lead.

## Ranked findings and adequacy limits

1. **SEC-F-08 — med, advisory:** neutralize terminal control bytes before printing repository/model-controlled probe output. No high or policy-gating issue remains.

Adequacy limits: the credentialled nondeterministic comprehension run was not performed and cannot decide release; SC-10 UAT was not performed; no PM goal-check was performed. The QA gate proves deterministic contract enforcement and registration/isolation, not the model-comprehension uplift or the operator's subjective message/actionability judgment. Authority-reader oversize and invalid-UTF-8 outcomes are enforced by the inspected bounded reader; the focused permanent cases directly exercise path containment, symlink, FIFO, and exception failures but do not carry separate authority-target oversize/non-UTF-8 fixtures. This is an advisory test-depth limit, not a BRIEF/matrix gap and not a reopening of the original F-01 containment defect.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Configured unit/integration, all focused FEAT-54 checks, and exact SC-04 pass at f05e1e6; c3 F-04 is closed and only SEC-F-08 remains a medium advisory."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 25 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 44 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-domain.py:4033-4042" }
    - { id: SC-02, test: "tests/integration/test-check-domain.py:4043-4064" }
    - { id: SC-03, test: "tests/integration/test-check-domain.py:4067-4085" }
    - { id: SC-05, test: "tests/integration/test-check-domain.py:4235-4244" }
    - { id: SC-06, test: "tests/integration/test-check-domain.py:4138-4190,4216-4232" }
    - { id: SC-09, test: "tests/integration/test-run-unit-tests-kinds.py:21-98" }
    - { id: SC-12, test: "tests/unit/test-handoff-done-when.py:127-132" }
    - { id: SC-13, test: "tests/integration/test-check-domain.py:4086-4091" }
    - { id: SC-14, test: "tests/integration/test-check-domain.py:4235-4247; tests/integration/test-check-state.py:2281-2295" }
    - { id: SC-15, test: "tests/integration/test-check-state.py:2211-2260" }
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-qa-c4.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-qa-c4.md
```
