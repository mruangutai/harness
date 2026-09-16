# QA matrix gate — FEAT-1714 c1

Pinned review: `8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125`; range `33f45262a9346b62a0e81d3a21786ab2b761cf4e..8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125` (46 paths). The feature worktree HEAD was not the pin, so both required commands ran in a detached `qa-1714-pin` worktree at the pin; it was removed afterward. `git worktree list` contains no `qa-1714-pin` entry.

## Phase 1 — requirements-derived inventory

Before source inspection: reject-digest acceptance/refusal (SC-01); first-run provenance/BRIEF preservation and zero-cycle terminal shape (SC-02); numeric and `none` dry-run/confirmed lifecycle, ordered mutations, and write-failure refusal (SC-03); every INV-44 dimension (SC-04); and shared terminal vocabulary (SC-05). Plan task types `api`, `feature`, and `cross_module` require `unit`; `feature` and `cross_module` also require `integration`. No UI/AI predicate fired.

## Matrix results

- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` — exit 0; 40 discovered test files; `pool: 8 workers, 40 files, 5.98s wall`.
- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` — exit 0; 72 discovered test files; `pool: 8 workers, 72 files, 79.31s wall`.

The runner environment required unsetting the inherited `HARNESS_AGENT_TYPE` before each command (repository QA guidance); the executed runner invocations above are otherwise exact. No formatter, linter, build, or other suite ran.

## Reconciliation and coverage

- **VAL-03 — closed.** The unit matrix is green and includes `test-code-grade.py` (unit output); the former `_reject_judgement_errors` grade gate no longer rejects.
- **VAL-01 — closed.** `gh-sync.py:1886-1919` derives first-sync steps from `plan.yaml.source_issues`; `test-gh-sync-abandon.py:716-750` exercises no-parent first sync, reports/acts on source ticket #1714, returns its card to backlog, and neither closes nor labels it.
- **VAL-02 — implementation closed, coverage incomplete.** `_run_reject_steps` stops on the first `_RejectHalt` and exits 1 before either station writer (`gh-sync.py:1932-1967`); numeric label failure asserts the stop, partial-progress report, skipped backlog/milestone, and no station (`test-gh-sync-abandon.py:689-709`). The `none` path uses the same routine, but has no direct failed-write regression.
- **VAL-06 — retained as QA-C1-01.** The c1 test's claimed provenance check does not assert byte or parsed equality of `source_issues`: it only selects *new* post-run lines (`test-gh-sync-abandon.py:742-744`). Removing the original `source_issues: [1714]` during station recording leaves that one-way comparison green. Drafted-BRIEF byte equality is directly asserted at `:745-746`.

## Findings

- **QA-C1-01 — medium · substance · owner T-02/T-05.** A future final station mutation that deletes or rewrites `plan.yaml.source_issues` can ship green: the first-sync fixture verifies that `status: rejected` was added but never verifies that every pre-existing source issue remains. Replace the one-way added-line check with a parsed/byte baseline assertion that proves `source_issues == [1714]` alongside the required status transition.
- **QA-C1-02 — medium · substance · owner T-02/T-05.** SC-03's no-successor failure and exact final-station order lack discriminating tests. The only failure fixture is numeric label failure (`:689-709`); `none` has no failing comment/backlog/milestone arm. Both successful fixtures call the final-state reader after the subprocess (`:667-674`, `:740-746`), so moving station recording before a later successful remote write still leaves them green. Add event-sequence assertions, including a `none` required-write failure proving exit 1 and no caller-permitted station.

## Automated-SC evidence and fail-first

- SC-01: `tests/integration/test-validate-digest.py:1404-1443`; fail-first `notes/receipt-main-session-T-01-fail-first.md:6-30`.
- SC-02: `tests/integration/test-gh-sync-abandon.py:711-750`, `tests/integration/test-check-state-feat59.py:464-521`, `tests/integration/test-worktree-terminal.py` FEAT-1714 case; fail-first `notes/receipt-main-session-T-03-fail-first.md:7-18`.
- SC-03: `tests/integration/test-gh-sync-abandon.py:645-709`; fail-first `notes/receipt-harness-backend-dev-T-02-fail-first.md:35-41`. Coverage gap QA-C1-02 remains.
- SC-04: `tests/integration/test-check-state-feat59.py:464-521`; fail-first `notes/receipt-main-session-T-03-fail-first.md:7-16`.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Pinned unit and integration matrices pass, but the first-sync provenance and lifecycle failure/order regressions remain non-discriminating."
  suite: pass
  failures: 0
  matrix_ok: true
  reviewed_sha: 8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125
  reviewed_range: 33f45262a9346b62a0e81d3a21786ab2b761cf4e..8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 40, evidence: "exit 0; pool: 8 workers, 40 files, 5.98s wall" }
    - { kind: integration, state: satisfied, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 72, evidence: "exit 0; pool: 8 workers, 72 files, 79.31s wall" }
  coverage_gaps:
    - "SC-02: source_issues preservation assertion is one-way and permits deletion (QA-C1-01)."
    - "SC-03: no direct none-path required-write failure or event-sequenced final-station assertion (QA-C1-02)."
  findings:
    - { id: QA-C1-01, severity: medium, kind: substance, owner: "T-02/T-05", scenario: "A final station write deletes source_issues; the current added-lines-only assertion remains green." }
    - { id: QA-C1-02, severity: medium, kind: substance, owner: "T-02/T-05", scenario: "A none-path required write fails or a successful station write moves before a later remote mutation; current fixtures remain green." }
  dispositions:
    - { id: VAL-01, disposition: closed }
    - { id: VAL-02, disposition: implementation_closed_coverage_gap_QA-C1-02 }
    - { id: VAL-03, disposition: closed }
    - { id: VAL-06, disposition: retained_as_QA-C1-01 }
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-validate-digest.py:1404-1443" }
    - { id: SC-02, test: "tests/integration/test-gh-sync-abandon.py:711-750; tests/integration/test-check-state-feat59.py:464-521" }
    - { id: SC-03, test: "tests/integration/test-gh-sync-abandon.py:645-709" }
    - { id: SC-04, test: "tests/integration/test-check-state-feat59.py:464-521" }
  fail_first:
    - { sc: SC-01, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-30" }
    - { sc: SC-02, evidence: "notes/receipt-main-session-T-03-fail-first.md:7-18" }
    - { sc: SC-03, evidence: "notes/receipt-harness-backend-dev-T-02-fail-first.md:35-41" }
    - { sc: SC-04, evidence: "notes/receipt-main-session-T-03-fail-first.md:7-16" }
  qa_pin_worktree: removed; none remains
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-qa-c1.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-qa-c1.md
```
