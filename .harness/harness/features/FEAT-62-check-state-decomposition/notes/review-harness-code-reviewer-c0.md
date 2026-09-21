# FEAT-62 pinned code review — cycle 0

## BLUF

**FAIL. Spec stage failed; stage 2 code-quality review was not performed.** The pinned implementation broadens the default checker's observable ordering beyond the only allowed INV-3/INV-15/INV-26 and named-marker exceptions, and it adds a 48th `except Exception` site despite SC-09/D-08 freezing the 47-site census. No source was edited.

## Stage 1 — specification compliance

| Criterion | Status | Inspection conclusion |
|---|---|---|
| SC-01 | **FAIL** | The eight recorded suite receipts are identical (`notes/build-divergences.md:30-51`), but the default live checker is not byte-identical within the allowed exception: D-1 records reordered rows for INV-17, INV-22/INV-8, INV-32, and the FEAT-59 family (`notes/build-divergences.md:57`), while D-3 admits additional error-state ordering changes (`:59`). |
| SC-02 | PASS | Ordered rows and retired identities are in `.claude/skills/harness/bin/check-state.py:4401-4547`; selector intersection and deterministic runner behavior are at `:4565-4842`; red-against-baseline selector coverage is recorded in `tests/integration/test-check-state-table.py:4-9,90-228`. |
| SC-03 | PASS | The module-body/reparse lock is implemented at `check-plan-routes.py:1761-1883`; isolated loop/conditional/try/read and reparse mutants are asserted at `test-check-plan-routes.py:2572-2605`. |
| SC-04 | PASS | Declared-read audit and transitive helper walk are at `check-plan-routes.py:1911-2022`; file, git, gh, helper, and declared-control mutants are at `test-check-plan-routes.py:2612-2647`; dirty/untracked/rename and conservative external-input selection are covered at `test-check-state-table.py:157-213`. |
| SC-05 | PASS | Live/non-struck authority resolution is at `check-plan-routes.py:2025-2054`; missing, struck, struck-in-index, and unreadable-index mutants are at `test-check-plan-routes.py:2650-2681`. |
| SC-06 | PASS | Workflow/hook posture scan is at `check-plan-routes.py:2061-2093`; workflow and hook mutants plus the full CI assertion are at `test-check-plan-routes.py:2684-2707`. The pinned name/status diff changes no workflow, hook, or command-entry path. |
| SC-07 | PASS | Path-derived, environment-independent feedback and stderr relay are at `harness_boundary.py:284-367`; both writer calls occur after `locked_update` returns (`plan-merge.py:2482-2487`, `feature_json_write.py:210-211`). |
| SC-08 | PASS | `.harness/README.md:108-112` distinguishes automatic mid-edit `--changed` feedback from the full pre-commit/CI table. `AGENTS.md:37` remains the unchanged “canonical state checker before committing” instruction (the pinned diff for `AGENTS.md` is empty). The complete pinned name/status diff contains no `SKILL.md`, preload-set, workflow, hook, or command-entry change; only `.harness/README.md` changes guidance. |
| SC-09 | **FAIL** | The ordered table and one function per registered row are visible at `check-state.py:856-4401,4401-4547`; runner-owned shared context begins at `:451` and feeds `run_table` at `:4762-4777`. The terminal grade run over exactly `16ee44f0..1380727c` reports **318 passing, 0 below bar**, matching `notes/build-divergences.md:16-17`. Handler-scoped base/pin inspection found every known baseline clause/body preserved under extraction, but the known-positive census is **47 at base and 48 at pin**: the added `_dirty_paths` catch at `check-state.py:4610-4614` violates the frozen 47-site contract. No package split or report-format rewrite was found. |

### Perspectives

- **Operator: FAIL.** Selective verbs and writer feedback are present, but default output can reorder non-authorized invariant rows (`build-divergences.md:57,59`).
- **Code maintainer: FAIL.** Registry/context/locks and grades pass, but the broad-handler census increased from 47 to 48 (`check-state.py:4613`).
- **Reader: PASS.** Authority auditing and bounded guidance are present; no forbidden guidance/preload/hook/workflow surface changed.

The `OMP-PORT` numbering and duplicate `INV-37` label remain parked operator anomalies exactly as recorded at `notes/build-divergences.md:74-80`; this review does not resolve or reclassify them.

## Findings

1. **CR-01 — high · substance · T-01 · `.harness/harness/features/FEAT-62-check-state-decomposition/notes/build-divergences.md:57,59` / `.claude/skills/harness/bin/check-state.py:4745-4777`.** The default runner sorts every feature and emits shared context findings first, although the approved exception is limited to INV-3, INV-15, INV-26, and named BEGIN/END sub-blocks. **Failure scenario:** on a multi-feature checkout whose filesystem order differs from lexical order, findings for INV-17, INV-22/8, INV-32, or FEAT-59 print in a different byte sequence; on a malformed-plan tree with an earlier finding, the context-load finding moves to the front. An operator comparing or consuming the established default receipt gets an unapproved changed receipt. **Fix:** preserve baseline ordering outside the expressly allowed rows, or obtain an approved BRIEF/decision amendment that names these additional divergences and their red-first proof.

2. **CR-02 — med · substance · T-01 · `.claude/skills/harness/bin/check-state.py:4610-4614`.** `_dirty_paths` introduces a new `except Exception`, increasing the base-to-pin census from the required 47 to 48. **Failure scenario:** if a future edit makes the `subprocess.run` call raise a programming error such as `TypeError`, the broad catch converts that defect into a conservative full-table run, hiding the broken changed-mode implementation instead of surfacing it. **Fix:** catch the narrow process-launch failure type required by this boundary and restore the census to 47.

## Stage 2

Not run: the protocol requires stage 1 to pass before code quality is assessed. Accordingly this review makes no stage-2 claims about selector internals, fail-open behavior, NUL parsing, writer behavior, or other quality dimensions beyond the spec evidence necessary above.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Spec stage failed: default output has unapproved reorderings and the frozen broad-handler census increased from 47 to 48."
  severity_max: high
  findings:
    - id: CR-01
      kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      owning_task: T-01
      location: ".harness/harness/features/FEAT-62-check-state-decomposition/notes/build-divergences.md:57,59; .claude/skills/harness/bin/check-state.py:4745-4777"
      summary: "Default output reorders invariant rows beyond the approved INV-3/INV-15/INV-26 and marker exceptions."
      why: "On a multi-feature or malformed-plan tree, non-authorized rows move, breaking the operator's byte-level default receipt contract."
    - id: CR-02
      kind: substance
      scope: task
      severity: med
      reader: code-reviewer
      owning_task: T-01
      location: ".claude/skills/harness/bin/check-state.py:4610-4614"
      summary: "A new broad catch increases the frozen except-Exception census from 47 to 48."
      why: "A programming error in changed-mode process launch can be hidden as a conservative full run, and SC-09/D-08 explicitly freeze the census."
  must_fix:
    - "CR-01: preserve the baseline default ordering outside approved exceptions, or secure an explicit spec amendment."
    - "CR-02: narrow the new _dirty_paths handler and restore the census to 47."
  spec_violations:
    - kind: mismatch
      path: ".claude/skills/harness/bin/check-state.py"
      ref: SC-01
    - kind: mismatch
      path: ".claude/skills/harness/bin/check-state.py"
      ref: SC-09
  code_grade: pass
  reviewed: "16ee44f0..1380727cc6a866627595a267b9b681fc3f7026bc"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-62-check-state-decomposition/.harness/harness/features/FEAT-62-check-state-decomposition/notes/review-harness-code-reviewer-c0.md
```
