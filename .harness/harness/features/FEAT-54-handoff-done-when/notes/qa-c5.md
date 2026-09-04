# QA gate c5 — FEAT-54 handoff Done when

## BLUF

**FAIL.** At immutable review SHA `4690f724cdbbdf03649f0cbea07efe7be3c03ce0`, the configured unit and integration matrix is non-vacuous and green (25 and 44 files), all focused changed-contract checks pass, SC-15's repaired caller-mode proof observes `real=0, mutant=1`, and the probe argv test proves exactly one `--no-tools` and no `--auto-approve`. The literal SC-04 command nevertheless exits **1** because one unrelated INV-29 violation names the standing `BUG-1157-approval-overrule` worktree. Its complete output contains **0** lines naming case-sensitive `Done when`, but the required command is not clean, so this gate cannot PASS.

The checkout HEAD was exactly `4690f724cdbbdf03649f0cbea07efe7be3c03ce0`. `git diff --quiet HEAD -- <the exact 16 paths below>` exited 0; the only pre-existing worktree modification was feature-local `feature.json`, outside that scope.

## Phase 1 expectations and matrix derivation

Before source access, the approved BRIEF and plan required unit coverage of the shared parser: fifth-section presence, exact/non-empty/ordered Scope, one-to-four Authorities, four typed pointer grammars, per-type resolve/refuse pairs, AND-not-ANY behavior, strict section and ATX-heading boundaries, bounded fail-closed target reads, and the `resolve=False` versus `resolve=True` split. Integration coverage was required through both real gates for Write/Edit pre-mutation refusal, the 60/61 whole-file boundary, no per-section cap, frozen baseline behavior, absent-target non-rot, grammar enforcement, clean-corpus non-mutation, and probe registration/exclusion. Review-time evidence was required for SC-04, SC-07, SC-08, and SC-11. SC-10 UAT and PM goal-check were excluded.

Plan change types are logic (T-01/02/03/04/06/07/12), config (T-05), docs (T-08/10/11), and scaffolding (T-09). The authoritative `.harness/harness.json` matrix requires unit for logic. T-05 changes config shape, firing `config.when: touches_config_shape` and requiring integration; the shared module/two-gate seam independently warrants integration. Docs and scaffolding add no configured kind. `handoff_comprehension` is `locally_run`, absent from the matrix, and reporting-only.

## Configured matrix and focused execution

Commands were run from repository root with only `HARNESS_AGENT_TYPE` unset; the command portions are exactly `test_kinds.<kind>.cmd`.

- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` — exit 0; `pool: 8 workers, 25 files`; non-zero discovery and execution.
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` — exit 0; `pool: 8 workers, 44 files`; non-zero discovery and execution.
- `python3 tests/unit/test-handoff-done-when.py` — exit 0; 54/54 printed named assertions.
- `python3 tests/unit/test-probe-handoff-comprehension.py` — exit 0; `Ran 7 tests`; the captured actual argv assertion requires `argv.count("--no-tools") == 1` and rejects `--auto-approve` (`tests/unit/test-probe-handoff-comprehension.py:71-80`).
- `python3 tests/integration/test-check-domain.py` — exit 0; 41/41 printed FEAT-54 handoff outcomes.
- `python3 tests/integration/test-check-state.py` — exit 0; 18/18 printed FEAT-54 outcomes. Both absent-target cases reject every reported line naming `handoff-plan.md` because they pass `needles=()` (`tests/integration/test-check-state.py:2162-2171,2234-2239`). The checked-in production-caller mutant changes the sole `resolve=False` call to `resolve=True`; observed output was `FEAT-54 state caller-mode mutation (real=0, mutant=1)` (`:2299-2348`).
- `python3 tests/integration/test-run-unit-tests-kinds.py` — exit 0; 5/5 named registration/isolation checks.

No assertion, import, collection, syntax, load, or discovery failure occurred. Required-kind states are `unit: satisfied` and `integration: satisfied`; `matrix_ok: true`.

## Literal SC-04 and inspections

- **SC-04 FAIL:** from repository root, literal `bash .claude/skills/harness/bin/check-state.sh` exited **1**. Its complete capture contains **0** case-sensitive lines naming `Done when` and **1** `VIOLATION` line. The line is INV-29 for `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1157-approval-overrule`: terminal status could not be determined because its landed feature.json is missing. This is not a Done-when defect, but acceptance requires the command itself to be clean.
- **SC-07 PASS by inspection:** `check-domain.sh:1546-1566` imports the single module and calls `problems(..., resolve=True)`; `check-state.sh:53-56,1243-1251` imports it and calls `problems(..., resolve=False)`. Neither gate carries a second Done-when body parser or target resolver.
- **SC-08 PASS by inspection:** template, playbook, DEC-159/214, and both gates state five sections and name `## Done when`. The surviving `four headings` statements in `check-state.sh:1194-1219` are commit/feature-bound historical observations expressly exempted by SC-08.
- **SC-11 PASS by inspection:** base is `0ec44965a961d19177de871c3bb1f02b701e646b`. The handoff diff contains four additions and no modified/deleted base-existing note: FEAT-51 `handoff-validate.md` and FEAT-54 `handoff-build.md`, `handoff-plan.md`, and `handoff-validate.md`. Thus the historical intersection is empty and the positive control is non-empty and equals the added-only set.

## Full shared 16-path inspection

All shared paths were inspected at the pinned bytes: `.claude/skills/harness/bin/handoff_done_when.py`; `tests/unit/test-handoff-done-when.py`; `tests/unit/test-probe-handoff-comprehension.py`; `tests/integration/test-check-domain.py`; `.claude/skills/harness/bin/check-domain.sh`; `.harness/harness.json`; `tests/integration/test-check-state.py`; `.claude/skills/harness/bin/check-state.sh`; `.claude/skills/harness/templates/HANDOFF.md`; `.claude/skills/harness/SKILL.md`; `tests/manual/probe-handoff-comprehension.py`; `.harness/harness/docs/DECISIONS.md`; `.harness/harness/docs/DECISIONS-INDEX.md`; `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md`; `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md`; `tests/integration/test-run-unit-tests-kinds.py`.

## Findings reassessed at c5

- **F-01 closed:** contained, regular, bounded UTF-8 authority reads and unsafe finding/approval paths remain pinned by unit and real-hook cases.
- **F-02 closed:** probe admission rejects outside, traversal, symlink, directory, wrong-name, and oversized inputs before model calls; the valid control reaches two arms.
- **F-03 closed:** invalid and unreadable Edit candidates are refused before mutation with byte identity asserted.
- **F-04 reopened/external:** the earlier FEAT-51 Done-when violation remains repaired and the literal output has zero `Done when` lines, but SC-04 is red again on the unrelated INV-29 worktree violation above.
- **F-05 closed:** blank Scope is refused across module, write gate, and state gate.
- **F-06 closed:** Authority-before-Scope is refused across all three layers.
- **F-07 closed:** the configured unit suite's code-grade test passes; no c5 code-quality claim relies on a fresh project-wide grader run.
- **F-08 closed:** nested H3 prose cannot truncate validation and duplicate Done-when H2 sections are refused.
- **F-09 closed:** `#Approval` and seven-hash lookalikes are refused beside valid ATX controls.
- **F-10 closed:** SC-15 absence checks now inspect every state-check line naming the fixture note, and the exact caller mutant produces `real=0, mutant=1`.
- **SEC-F-10 closed:** actual probe argv contains exactly one `--no-tools` and no `--auto-approve`, pinned by the focused behavioral unit test.
- **SEC-F-08 survives, med advisory:** repository/model/provider strings still reach terminal print sinks without control-byte neutralization. This remains non-gating under `review: advisory_unless_high`.

## Test-first evidence and adequacy

The contemporaneous executor record (`notes/tdd-executor-record.md`) records RED-before-GREEN for T-01→T-02, T-03→T-04, and T-06→T-07. The c5 engineering digest (`runs/2026-09-03-sec-f10-c5-eng/digest.md`) records the new argv test RED with zero `--no-tools`, followed by GREEN after the production edit. The SC-15 c5 repair is a test-strengthening change whose checked-in caller mutant is executed on every focused/full integration run and discriminates at the current pin.

No coverage gap exists for the deterministic automated criteria. Adequacy limits: the credentialled nondeterministic comprehension benchmark was not run; SC-10 UAT and PM goal-check were not performed; no formatter, linter, project-wide build, or unselected suite ran. The sole blocking item is the live SC-04 INV-29 violation, owned outside FEAT-54's source/test repair scope.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Configured unit/integration and both c4 blocker repairs pass falsifiably at 4690f724, but literal SC-04 exits 1 on an unrelated INV-29 standing-worktree violation."
  suite: fail
  failures: 1
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
    - { id: SC-14, test: "tests/integration/test-check-domain.py:4235-4247; tests/integration/test-check-state.py:2282-2296" }
    - { id: SC-15, test: "tests/integration/test-check-state.py:2162-2171,2234-2239,2299-2348" }
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/qa-c5.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/qa-c5.md
```
