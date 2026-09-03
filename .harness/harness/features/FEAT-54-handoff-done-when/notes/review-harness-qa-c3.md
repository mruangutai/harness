# QA review c3 — FEAT-54 handoff Done when

## BLUF

**FAIL.** The configured unit and integration kinds pass with non-empty discovery (25 and 44 files), all named non-UAT repair seams have adequate discriminating coverage, the pinned complexity gate passes 86 changed functions, and all five repaired lead digests validate. The mandatory literal SC-04 repository-root command nevertheless exits 1 on one remaining FEAT-51 violation. Its output names no `Done when` violation, but SC-04 requires the command itself to succeed and cannot be waived.

Reviewed immutable SHA `39602414e1cfe792655b7e68bce367e92790c32a` against base `0ec44965a961d19177de871c3bb1f02b701e646b`. `git diff --quiet` confirmed that every named reviewed file's worktree bytes equal the pinned SHA.

## Phase 1 expectations and matrix

Before source access, BRIEF/plan required unit coverage for the one-to-four authority AND contract, non-empty ordered Scope, typed pointer grammar/resolution, resolve-on/off separation, nested/duplicate-heading rejection, strict approval headings, and bounded fail-closed target reads. Integration coverage was required through both real gates for Write/Edit refusal before mutation, invalid UTF-8 existing bytes, frozen-baseline behavior, no persisted target re-resolution, whole-file cap, and probe registration/exclusion. Review-time inspections were required for SC-04/07/08/11; SC-10 remains operator UAT.

The plan's logic tasks require `unit`. The shared module/two-gate seam warrants `integration`, and the added baseline/config kind structure fires `config.when: touches_config_shape`, also requiring `integration` (DEC-212). Docs and scaffolding add no kind. `handoff_comprehension` is `locally_run`, absent from the matrix, and was not run; this gate inspected admission, registration, and suite exclusion only.

| Kind | Configured command | Discovery | Exit/outcome |
|---|---|---:|---|
| unit | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 25 files | 0, satisfied |
| integration | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 44 files | 0, satisfied |

Both commands ran once from the exact repository root with `CLAUDE_PROJECT_DIR` set to that root. Unit executed `test-handoff-done-when.py` and `test-probe-handoff-comprehension.py`; integration executed `test-check-domain.py`, `test-check-state.py`, and `test-run-unit-tests-kinds.py`. No assertion, import, collection, syntax, or load failure occurred.

## Named repair seams and adequacy

- **Contained/fail-closed finding and approval authorities:** `_unsafe_rel_path`, `_read_target`, and `_resolution_problems` reject traversal/control paths, root escapes, non-regular/oversized/non-UTF-8 reads, and unexpected resolver exceptions (`handoff_done_when.py:63-101,241-252`). Finding and approval each have independent absolute/traversal cases in both resolution modes and symlink/FIFO cases under resolution (`test-handoff-done-when.py:91-103,169-192`); the real write gate repeats approval absolute/traversal and both pointer types over symlink/FIFO, plus an injected validator exception (`test-check-domain.py:4108-4134,4193-4213`). Resolving controls for both remain green (`test-handoff-done-when.py:105-118`).
- **Probe admission and suite exclusion:** every rejected outside/traversal/symlink/directory/wrong-name/oversized input asserts an empty model-call log, while a valid note requires exactly two calls (`test-probe-handoff-comprehension.py:45-101`). Registration removal and empty-detect mutants fail, and a sentinel probe under `tests/manual/` is not executed by `--kind all` (`test-run-unit-tests-kinds.py:21-98`).
- **Pre-mutation Edit and invalid UTF-8:** actual PreToolUse Edit reconstruction must exit 2 before mutation; both an invalid candidate and invalid UTF-8 existing bytes are compared byte-for-byte after refusal (`test-check-domain.py:4138-4190`).
- **Non-empty ordered Scope:** blank Scope and Authority-before-Scope are separate unit, write-gate, and persisted-state cases (`test-handoff-done-when.py:83-89`; `test-check-domain.py:4043-4064`; `test-check-state.py:2190-2200,2243-2247`).
- **Nested/duplicate truncation:** separate nested `###` and duplicate `## Done when` fixtures require refusal in the unit, write, and state layers (`test-handoff-done-when.py:57-70`; `test-check-domain.py:4054-4064`; `test-check-state.py:2201-2207,2253-2258`). Accepting only the first truncated body makes these cases fail.
- **Strict ATX approvals:** `#Approval` and `####### Approval` are separately refused, beside a normal `## Approval` control (`test-handoff-done-when.py:27-29,134-145`; `test-check-domain.py:4026-4029,4092-4105`).
- **Complexity:** `python3 .claude/skills/harness/bin/code-grade.py --base 0ec44965a961d19177de871c3bb1f02b701e646b --head 39602414e1cfe792655b7e68bce367e92790c32a` exited 0 with `PASSING: 86`; production records met bar 4 and test/probe records met bar 3.

## Mandatory inspections

- **SC-04 FAIL:** from the exact repository root, literal `bash .claude/skills/harness/bin/check-state.sh` exited **1**. It emitted exactly one `VIOLATION`: `FEAT-51-claude-code-lifecycle-safety: status is 'done' but notes/handoff-validate.md is missing — the validate seam was crossed without a handoff; the successor is on the disk-only path (DEC-159).` No output line names `Done when`. Informational `note` lines are not additional violations.
- **SC-07 PASS:** `check-domain.sh:1561-1566` imports/calls `handoff_done_when.problems(..., resolve=True)` and fails closed; `check-state.sh:53-56,1243-1251` imports/calls the same implementation with `resolve=False`. Neither gate contains another Done-when body parser or pointer resolver.
- **SC-08 PASS:** template/playbook, DEC-159/214, and both gates state the five-section contract and name `## Done when`. The only four-heading gate prose is the authorized FEAT-31 historical measurement/incident (`check-state.sh:1194-1202,1215-1219`); DEC-160's first-live-handoff sentence is likewise historical, not a current-contract assertion.
- **SC-11 PASS:** merge-base is exactly the supplied base. The prescribed primary intersection printed nothing. The positive control printed `handoff-build.md` and `handoff-plan.md`, exactly equal to the added-only set.
- **Approval authorities PASS:** plan and BRIEF approval blocks are approved by Mike Ruangutai on 2026-09-02 (`plan.yaml:3-6`, `BRIEF.md:199-203`). Both new handoffs have a non-empty immediate-action Scope and point to the existing BRIEF `## Approval` heading (`handoff-plan.md:53-55`, `handoff-build.md:34-37`). The four product rulings and their authorities remain recorded in `notes/signature-inputs-c3.md:27-61` and are consistent with D-10/DEC-214.

## Prior F-01–F-09 disposition

- **F-01 closed / assessed-and-dismissed:** independent finding/approval containment and fail-closed coverage now exists as cited above.
- **F-02 closed / assessed-and-dismissed:** rejected probe inputs make zero model calls and the valid control makes two.
- **F-03 closed / assessed-and-dismissed:** invalid candidate and invalid-UTF-8 Edit paths refuse before mutation with byte identity.
- **F-04 surviving, high, must-fix:** literal SC-04 exits 1 on the exact violation above. Failure scenario: Harness entry at the pin reports a state violation, so the clean repository-corpus criterion is false even though Done-when-specific output is clean. **Owner lane:** Main direct corpus/state reconciliation; FEAT-51 ownership, not FEAT-54 source or fixture mutation.
- **F-05 closed / assessed-and-dismissed:** blank/whitespace Scope is refused at all three layers.
- **F-06 closed / assessed-and-dismissed:** Scope must precede every Authority at all three layers, consistent with the product ruling.
- **F-07 closed / assessed-and-dismissed:** pinned changed-function grade passes 86 records at their applicable bars.
- **F-08 closed / assessed-and-dismissed:** nested and duplicate headings no longer truncate validation and have independent three-layer regression cases.
- **F-09 closed / assessed-and-dismissed:** invalid ATX approval forms are refused with a valid heading control.

## Repaired lead digests

Each command `python3 .agents/skills/harness/bin/validate-digest.py lead <path>` exited 0 and printed `digest ok`:

- `runs/2026-09-03-qa-validation-c2-validator/digest.md`
- `runs/2026-09-03-validation-c1-eng/digest.md`
- `runs/2026-09-03-validation-c2-eng/digest.md`
- `runs/2026-09-03-qa-post-simplify-c2-validator/digest.md`
- `runs/2026-09-02-validation-c1-eng/digest.md`

SC-10 was not run or claimed. No tests, fixtures, source, state, plan, ledger, pin, formatter, linter, or unrelated validation were authored or changed.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Unit/integration and every named repair seam pass, but literal SC-04 exits 1 on one remaining FEAT-51 violation."
  suite: pass
  failures: 1
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 25 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 44 }
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
    - { id: SC-15, test: "tests/integration/test-check-state.py:2178-2258" }
  open_questions:
    - { id: Q1, question: "SC-04 is false at the pin because FEAT-51 is done without notes/handoff-validate.md; Main must reconcile that corpus/state violation before ship.", blocking: true }
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-qa-c3.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-qa-c3.md
```
