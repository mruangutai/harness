# FEAT-64 code review — c0

**BLUF:** FAIL at Stage 1. The pinned range includes an operator-visible repair in `board_lifecycle.py` and its test outside the approved eighteen-file production scope. The divergence ledger discloses B2, but a ledger entry is not signed scope authority. Per the two-stage protocol, Stage 2 did not start.

- Baseline: `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983`
- Review pin: `dc71e09e0647882c63f66ab0b6d6048bc6dd2688`
- Reviewed range: `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983..dc71e09e0647882c63f66ab0b6d6048bc6dd2688`
- Source basis: pinned Git objects (`git show` / `git diff`), not mutable working-tree source.
- Canonical scope: all 39 paths supplied in the dispatch were considered; no hook entry script or `.omp/extensions/harness-hooks.ts` changed in the pinned range.

## Stage 1 — spec compliance: FAIL

### CR-64-01 — Out-of-plan `board_lifecycle` behavior change

- reader: `code-reviewer`
- kind: `substance`
- severity: `high`
- classification: `scope_creep`
- ownership: scope change; no signed task owns it. Return to PM/operator to remove it from FEAT-64 or explicitly amend the approved scope and behavioral contract before rebuilding.
- failure scenario: when `audit_findings()` runs with a declared board but no `github.repo`, baseline construction of `GhError` raises `TypeError`, which the ship audit path reports as an internal audit failure; the pin instead raises a valid `GhError`, changing the operator-visible failure classification/message. That is a shipped behavior change in a production module outside the ten libraries and eight tools, without a corresponding signed SC or D authorizing this module.
- evidence anchors: `BRIEF.md` Constraints (the exhaustive ten-library/eight-tool lists); `BRIEF.md` Out of scope; `plan.yaml` T-01/T-02/T-03 `files`; `plan.yaml` D-03; `.claude/skills/harness/bin/board_lifecycle.py@dc71e09:922-938`; `notes/build-divergences.md` B2; `tests/integration/test-board-lifecycle.py` pinned diff.
- disposition: must fix. Disclosure in B2 is useful and explicit, but amendments/divergences are a map of departures, not authority for expanding signed scope.

SC-04 inspection passed: the pinned range changes none of the eleven named hook entry scripts and does not change `.omp/extensions/harness-hooks.ts`.

## Stage 2 — code quality: NOT STARTED

The protocol requires Stage 1 to pass before code-quality review. Therefore no conclusions are made here about fail-open branches, silent failure paths, narrowing correctness, typed-boundary ownership, duplicate reparses, exception-chain preservation, comment-byte obligations, or no-hook wiring beyond the Stage-1 SC-04 inspection above. Mechanical grading was not used to override the Stage-1 stop.

## Review record

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 fails: divergence B2 changes board_lifecycle behavior outside FEAT-64's signed production scope; Stage 2 was not started."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      summary: "CR-64-01: board_lifecycle.py and its test implement an unapproved behavior change outside T-01..T-03."
      why: "With github.board declared and github.repo absent, the pin emits a valid GhError instead of the baseline TypeError/internal-audit-failure path; B2 records the departure but does not authorize scope expansion. Owner: PM/operator scope change, then builder if approved. Evidence: BRIEF Constraints; plan T-01..T-03 files and D-03; board_lifecycle.py@dc71e09:922-938; build-divergences.md B2."
  must_fix:
    - "Remove the board_lifecycle.py/test-board-lifecycle.py B2 repair from FEAT-64, or obtain an explicit signed scope/behavior amendment and rebuild the pinned change before review."
  spec_violations:
    - kind: scope_creep
      path: .claude/skills/harness/bin/board_lifecycle.py
      ref: D-03
    - kind: scope_creep
      path: tests/integration/test-board-lifecycle.py
      ref: D-03
  code_grade: pass
  reviewed: "a4a3d7f8e9b91181fb6cc3ae058df8e02275d983..dc71e09e0647882c63f66ab0b6d6048bc6dd2688"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-code-reviewer-c0.md
```
