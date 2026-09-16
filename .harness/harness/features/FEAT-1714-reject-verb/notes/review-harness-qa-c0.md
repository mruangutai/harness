# FEAT-1714 QA gate — cycle 0

Reviewed range: `origin/main...82bdef1a6f7cd89005f661a06296725f5b1ad9b1` (merge base `33f45262a9346b62a0e81d3a21786ab2b761cf4e`). `git diff --name-only` reported 46 paths, matching the caller's enumerated scope. The checkout has only feature metadata changes after the pin; reviewed source and tests are pin-equivalent.

## Phase 1: requirements-derived test inventory

Before reading implementation, the required evidence was:

1. Reject digest accepts only `kind: reject`, exactly one nonempty one-line reason, and a positive ASCII issue number or `none`; every malformed variant is rejected.
2. A first-run reject flow preserves `source_issues` and the drafted BRIEF, writes the zero-run rejection shape, performs no panel/lead/signature work, and performs terminal cleanup.
3. Numeric successor reject dry run writes nothing; confirmed execution closes and reseats the parent, comments, labels, milestones, has no sub-issue operations, and records the terminal station last. `none` follows its distinct no-successor path.
4. State validation accepts the valid zero-cycle first-run shape and independently rejects every INV-44 violation.
5. All terminal consumers use the shared `abandoned`/`rejected` vocabulary; `TERMINAL_MARKER` is gone.

Phase 2 found direct coverage for the digest, state, gh-sync, worktree, and shared-vocabulary portions. It did not find a rejection-flow test for source-issue/drafted-BRIEF preservation, nor an assertion that the gh-sync station write is ordered after every other numeric-successor mutation.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Required unit matrix command fails; two specified rejection-flow assertions have no direct coverage.
  suite: fail
  failures: 1
  matrix_ok: false
  reviewed_range: origin/main...82bdef1a6f7cd89005f661a06296725f5b1ad9b1
  reviewed_paths: 46
  kinds:
    - kind: unit
      state: failed
      cmd: .agents/skills/harness/bin/run-unit-tests.py --kind unit
      named_tests: 40
      evidence: "exit 1; tests/unit/test-code-grade.py reports validate-digest.py:_reject_judgement_errors grade >= 4: expected True, got False"
    - kind: integration
      state: satisfied
      cmd: .agents/skills/harness/bin/run-unit-tests.py --kind integration
      named_tests: 72
      evidence: "exit 0; pool: 8 workers, 72 files, 76.13s wall"
    - kind: ui
      state: not applicable
      reason: "No plan task has a UI predicate or user-interface change type."
    - kind: e2e
      state: not applicable
      reason: "No plan task declares an end-to-end predicate."
    - kind: ai_behavior
      state: not applicable
      reason: "No AI behavior change type is declared."
    - kind: security
      state: not applicable
      reason: "No security predicate is declared; a separate security reader is assigned."
    - kind: performance
      state: not applicable
      reason: "No performance predicate is declared."
  task_matrix:
    - task: T-01
      change_type: api
      required: [unit]
      integration_predicate: false
    - task: T-02
      change_type: feature
      required: [unit, integration]
    - task: T-03
      change_type: cross_module
      required: [unit, integration]
    - task: T-04
      change_type: docs
      required: []
    - task: T-05
      change_type: docs
      required: []
  task_verify_literals:
    - "T-01: python3 tests/unit/test-feature-record.py && python3 tests/integration/test-validate-digest.py"
    - "T-02: python3 tests/unit/test-factory-config.py && python3 tests/unit/test-handoff-done-when.py && python3 tests/unit/test-gh-board.py && python3 tests/integration/test-board-lifecycle.py && python3 tests/integration/test-gh-sync-abandon.py"
    - "T-03: python3 tests/unit/test-factory-config.py && python3 tests/integration/test-plan-merge.py && python3 tests/integration/test-check-plan-routes.py && python3 tests/integration/test-check-state-feat59.py && python3 tests/integration/test-worktree-terminal.py && python3 tests/integration/test-check-state-worktrees.py && python3 tests/integration/test-station-argument-spelling.py && python3 tests/integration/test-gh-sync-abandon.py"
    - "T-04: python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md"
    - "T-05: python3 tests/integration/test-station-argument-spelling.py"
  coverage_gaps:
    - "SC-02: no reject-orchestration test preserves source_issues and the drafted BRIEF."
    - "SC-03: no test proves numeric-successor station recording is the final mutation."
  sc_evidence:
    - id: SC-01
      test: "tests/integration/test-validate-digest.py:1404-1443; tests/unit/test-feature-record.py:221-234,575-576"
    - id: SC-02
      test: "tests/integration/test-check-state-feat59.py:454-517; tests/integration/test-worktree-terminal.py:850-880"
      limitation: "Does not exercise source_issues or drafted-BRIEF preservation."
    - id: SC-03
      test: "tests/integration/test-gh-sync-abandon.py:617-688"
      limitation: "Checks final station value, but not that its mutation follows comment, label, and milestone operations."
    - id: SC-04
      test: "tests/integration/test-check-state-feat59.py:454-517"
    - id: SC-05
      test: "tests/unit/test-factory-config.py:531-539; tests/unit/test-handoff-done-when.py:298-305; tests/unit/test-gh-board.py:453-461; tests/integration/test-board-lifecycle.py:1068-1072; tests/integration/test-plan-merge.py:1244-1248; tests/integration/test-station-argument-spelling.py:39-46,107-138; tests/integration/test-worktree-terminal.py:850-880"
  fail_first:
    - sc: SC-01
      evidence: "notes/receipt-main-session-T-01-fail-first.md:6-19,27-30"
    - sc: SC-02
      evidence: "notes/receipt-main-session-T-03-fail-first.md:7-15"
    - sc: SC-03
      evidence: "notes/receipt-harness-backend-dev-T-02-fail-first.md:35-41"
    - sc: SC-04
      evidence: "notes/receipt-main-session-T-03-fail-first.md:7-16"
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-qa-c0.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-qa-c0.md
```

## Findings

- **QA-01** — severity: high; kind: substance; reader: harness-qa; owner: T-01. The required unit matrix command exits 1 because the new `validate-digest.py:_reject_judgement_errors` is not represented in `tests/unit/test-code-grade.py`'s self-grading allowlist and therefore fails its production grade floor. Concrete failure: any ship gate invoking the configured unit command fails before accepting the feature. Evidence: unit matrix output, `tests/unit/test-code-grade.py:279-289`; the allowlist ends at `validate-digest.py:hook_mode` in `:254-260`.

- **QA-02** — severity: medium; kind: substance; reader: harness-qa; owner: T-05. The stated first-run reject contract requires preserving both provenance and drafted BRIEF, but no changed rejection-flow test names `source_issues`, a drafted BRIEF, or preservation. Concrete failure: a future reject-flow cleanup that clears provenance or overwrites the draft can pass the current SC-02 state/worktree checks. Evidence: Phase-2 scan of assigned SC tests; `tests/integration/test-check-state-feat59.py:454-517` validates record shape only.

- **QA-03** — severity: medium; kind: substance; reader: harness-qa; owner: T-02. The numeric-successor test proves the resulting station is `rejected`, not that recording it is last. Concrete failure: moving `_record_station(..., "rejected")` before milestone/comment operations violates SC-03 while `tests/integration/test-gh-sync-abandon.py:617-688` still sees the same final station. Evidence: its order assertion covers close-before-backlog; the station assertion is final-state-only.

## Dismissed candidates

- **INV-43**: dismissed from this review; the signed answer assigns it to BUG-1723.
- **TERMINAL_MARKER removal**: dismissed as a defect; its deletion is intentional and Phase-2 consumers use `TERMINAL_STATIONS`.
- **Universal preload word count and eng-lead budget pressure**: dismissed as feature defects; universal preload is within its 1895/1900 limit, and the eng-lead overage predates this range on main.
- **T-04/T-05 standalone commands**: not run here because their `docs` change type adds no configured matrix kind; their plan literals were checked above. No formatter, linter, build, or project-wide suite was run.
