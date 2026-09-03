# QA validation c3 — FEAT-54 handoff Done when

## BLUF

**PASS for the FEAT-54 c3 QA gate.** The configured unit and integration kinds passed with non-empty discovery (25 and 44 files), the current repairs are behaviorally bound through the shared module and both real gates, Main's supplied focused/risk evidence covers the changed-function scope, and all five repaired run digests satisfy the lead contract. FEAT-51 still makes literal repository-root SC-04 fail and remains an external ship blocker; it is not a FEAT-54 c3 matrix failure.

## Phase 1 expectations and matrix

Before source access, BRIEF/plan required unit coverage for Done-when shape, typed pointer grammar/resolution, AND semantics and resolve-mode separation; integration coverage through the write and persisted-state gates; the whole-file cap; locally-run probe registration/exclusion; and preservation of the prior blank-Scope, Scope-order, fail-closed Edit, and probe-admission repairs. The repair dispatch additionally required nested/duplicate section rejection, strict ATX approval headings, and approval containment parity for absolute, traversal, symlink-escape and special targets.

The plan carries `logic`, `config`, `docs`, and `scaffolding`; the complete feature also crosses the shared-module/two-gate seam and changes config shape. The applicable floor is therefore unit plus integration. `.harness/harness.json:263-295` configures both as active. `handoff_comprehension` is locally-run and credential-gated, not an active matrix command; it was not executed as required by this dispatch.

## Matrix execution

Both commands ran exactly once from the absolute worktree with `CLAUDE_PROJECT_DIR` set and `HARNESS_AGENT_TYPE` unset:

| Kind | Configured command | Discovery | Exit |
|---|---|---:|---:|
| unit | `env -u HARNESS_AGENT_TYPE CLAUDE_PROJECT_DIR=/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 25 files | 0 |
| integration | `env -u HARNESS_AGENT_TYPE CLAUDE_PROJECT_DIR=/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 44 files | 0 |

The unit transcript includes 54 named PASS assertions from `test-handoff-done-when.py`. The integration transcript includes the changed `test-check-domain.py` and `test-check-state.py`, with all focused FEAT-54 cases green. Discovery was non-vacuous in both kinds.

## Discrimination and prior-repair preservation

- Nested heading: unit `tests/unit/test-handoff-done-when.py:57-70`, write gate `tests/integration/test-check-domain.py:4054-4064`, and state gate `tests/integration/test-check-state.py:2201-2207,2253-2258` put stray prose after `### hidden`; a parser that truncates at `###` returns clean and fails these assertions.
- Duplicate Done-when: the same ranges place a second `## Done when` after an otherwise valid first block and require refusal/count text; accepting the first block alone fails.
- Strict ATX approval heading: `tests/unit/test-handoff-done-when.py:134-145` and `tests/integration/test-check-domain.py:4092-4105` separately refuse `#Approval` and `####### Approval`; the ordinary `## Approval` fixture at unit lines 27-29 and integration lines 4026-4029 is the positive control.
- Approval containment: unit lines 91-103 reject absolute/traversal for finding and approval under both resolve modes; lines 169-192 reject symlink escape and FIFO targets for both pointer kinds. The real write gate repeats approval absolute/traversal at integration lines 4108-4119 and both pointer kinds over symlink/FIFO at lines 4120-4134. Each case requires refusal and an `unsafe` diagnostic, while resolving approval controls remain green.
- Prior F-01–F-07: F-01 approval parity is now closed above; F-02 exact zero-call admission plus the two-call valid control ran in `tests/unit/test-probe-handoff-comprehension.py`; F-03 pre-Edit refusal requires exit 2 and byte identity, including invalid UTF-8 (`test-check-domain.py:4138-4184`); F-05 blank Scope and F-06 Scope-before-Authority require their specific messages in unit and both gates; F-07 is covered by the reconciled risk evidence below. F-04 is the external SC-04 item below, not silently counted green.

## Changed-function risk evidence

The current uncommitted production diff changes `_done_when_indices`, `_body`, adds `_atx_heading_text` and `_resolve_all`, and changes `problems`; test changes are confined to the named FEAT-54 regression helpers/cases. Main supplied and already executed the focused unit validator plus `test-check-domain.py` and `test-check-state.py` together at exit 0 and reported zero relevant changed-function grade failures. That evidence covers the current parser and test-helper repair scope, so no additional grade run was warranted and the prohibited historical whole-helper census was not run.

## Repaired lead digests

Each was invoked separately as `python3 .agents/skills/harness/bin/validate-digest.py lead <path>`; each printed `digest ok` and exited 0:

- `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-03-qa-validation-c2-validator/digest.md`
- `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-03-validation-c1-eng/digest.md`
- `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-03-validation-c2-eng/digest.md`
- `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-03-qa-post-simplify-c2-validator/digest.md`
- `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-validation-c1-eng/digest.md`

## External blocker

FEAT-51's missing repository-root `notes/handoff-validate.md` remains known to make the literal SC-04 `check-state.sh` review command nonzero. Per dispatch it was neither rerun nor repaired here. The five FEAT-54 digest-contract failures previously co-reported by that command are independently closed above; FEAT-51 remains an external blocker to claiming SC-04 and shipping, not a failure of either configured FEAT-54 matrix kind.

```yaml
VERDICT: PASS
DIGEST:
  headline: "FEAT-54 c3 passes both non-vacuous matrix kinds and all repaired-contract checks; FEAT-51 remains the external SC-04 ship blocker."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE CLAUDE_PROJECT_DIR=<absolute-worktree> .agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 25 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE CLAUDE_PROJECT_DIR=<absolute-worktree> .agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 44 }
    - { kind: handoff_comprehension, state: locally-run, cmd: "tests/manual/probe-handoff-comprehension.py", named_tests: 0 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-domain.py:4033-4042" }
    - { id: SC-02, test: "tests/integration/test-check-domain.py:4043-4064" }
    - { id: SC-03, test: "tests/integration/test-check-domain.py:4067-4085" }
    - { id: SC-05, test: "tests/integration/test-check-domain.py:4235-4244" }
    - { id: SC-06, test: "tests/integration/test-check-domain.py:4138-4184" }
    - { id: SC-09, test: "tests/integration/test-run-unit-tests-kinds.py:20-98" }
    - { id: SC-12, test: "tests/unit/test-handoff-done-when.py:127-132" }
    - { id: SC-13, test: "tests/integration/test-check-domain.py:4086-4091" }
    - { id: SC-14, test: "tests/integration/test-check-domain.py:4235-4247" }
    - { id: SC-15, test: "tests/integration/test-check-state.py:2184-2200,2233-2252" }
  open_questions:
    - { id: Q1, question: "FEAT-51 still causes the literal repository-root SC-04 state check to exit nonzero; resolve it outside FEAT-54 before claiming SC-04 or shipping.", blocking: true }
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/qa-validation-c3.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/qa-validation-c3.md
```
