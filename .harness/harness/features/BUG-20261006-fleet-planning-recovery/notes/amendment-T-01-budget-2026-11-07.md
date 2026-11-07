# T-01 amendment — DEC-182 machine-line budget (2026-11-07)

The CI route gate (`check-plan-routes.py`) refused PR #2177 with "VIOLATION T-01: 56 machine-field
lines — budget is 50 per task (DEC-182)". Four `T-01.files` amendments on 2026-10-18 had added
eight consumer files, which took T-01 past its signed 48 lines. T-01 is done. Following the
advisor ruling (KayaBlockersAdvisor, 2026-11-07, option a), one canonical `record-amendments`
call trims it to 48. No scope or behaviour changes.

## Moved verbatim out of `T-01.verify`

```text
# Expect exit 0 and all assertions passing, including fleet cases with BOTH FACTORY_GH and GH_SYNC_GH bound to the shared fake, shared contents responses, and a complete call log proving no Harness mutation or real-gh escape. The 60-second focused ceiling is unmeasured; record first-green wall time and move the slowest case to the full matrix if exceeded, rather than inflate the claim. Full matrix runs exactly once at pinned review_sha after T-02 and before T-03 activation.
```

## Removed from `T-01.files`

T-01 did touch these seven consumer-test surfaces. The plan's `lanes` rows still route them
main-session-direct (`tests/unit/**`, `tests/integration/**`):

- tests/unit/omp-hooks.test.ts
- tests/unit/test-digest-schemas.py
- tests/integration/test-feature-corpus.py
- tests/integration/test-hooks-install.py
- tests/integration/test-factory-integration.py
- tests/integration/test-station-argument-spelling.py (deleted by T-01)
- tests/integration/test-gh-backlog-issue-types.py#check

## Known consequence

This feature's own completed mirror recovery `ca38c84b` bound `plan_sha256 77ac2d59…`. If
`recover-mirror` were run again on this feature, it would now refuse ("replacement operands
differ") rather than do nothing. Nothing needs that replay. No static gate re-verifies the hash.
Kaya's plan is untouched.

## Amendment record

```yaml
{
  "VERDICT": "PASS",
  "DIGEST": {
    "amendments": [
      {
        "task": "T-01",
        "field": "verify",
        "was": "python3 tests/unit/test-feature-record.py && python3 tests/unit/test-digest-record.py && python3 tests/unit/test-gh-sync-build-entry.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-check-state-records.py\n# Expect exit 0 and all assertions passing, including fleet cases with BOTH FACTORY_GH and GH_SYNC_GH bound to the shared fake, shared contents responses, and a complete call log proving no Harness mutation or real-gh escape. The 60-second focused ceiling is unmeasured; record first-green wall time and move the slowest case to the full matrix if exceeded, rather than inflate the claim. Full matrix runs exactly once at pinned review_sha after T-02 and before T-03 activation.\n",
        "now": "python3 tests/unit/test-feature-record.py && python3 tests/unit/test-digest-record.py && python3 tests/unit/test-gh-sync-build-entry.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-check-state-records.py\n",
        "reason": "DEC-182: the comment only justifies the command; moved verbatim to notes/amendment-T-01-budget-2026-11-07.md"
      },
      {
        "task": "T-01",
        "field": "files",
        "was": [
          ".claude/skills/harness/bin/gh-sync.py#main",
          ".claude/skills/harness/bin/feature_schema.py#recovery_command_for",
          ".claude/skills/harness/bin/feature-schema.json#github",
          ".claude/skills/harness/bin/feature-record.py#cmd_close_run",
          ".claude/skills/harness/bin/digest_record.py#load_record",
          ".claude/skills/harness/bin/validate-digest.py#cli_object",
          ".claude/skills/harness/bin/check_state/feature_record.py#inv_7",
          ".claude/skills/harness/bin/check_state/run_state.py#inv_15",
          ".claude/skills/harness/bin/check_state/table.py#INVARIANTS",
          ".claude/skills/harness/bin/check_state/board.py#inv_37",
          ".claude/skills/harness/bin/merge-gate.py#_enforce_receipt",
          ".claude/skills/harness/bin/post-merge-sweep.py#_receipt_allows_removal",
          ".claude/skills/harness/bin/board_lifecycle.py#_status_findings",
          "tests/unit/test-feature-record.py#CloseRunTest",
          "tests/unit/test-digest-record.py#DurableRecord",
          "tests/unit/test-gh-sync-build-entry.py#base_doc",
          "tests/unit/test-feature-schema-build-entry.py#write_plan",
          "tests/integration/gh_sync_support.py#stage_station",
          "tests/integration/test-gh-sync-open.py#main",
          "tests/integration/test-gh-sync-start-task.py#main",
          "tests/integration/test-gh-sync-ship.py#main",
          "tests/integration/test-gh-sync-abandon.py#main",
          "tests/integration/test-gh-sync-record.py#main",
          "tests/integration/test-gh-issue-types.py#check",
          "tests/integration/test-gh-backlog-issue-types.py#check",
          "tests/integration/test-board-lifecycle.py#write_root",
          "tests/integration/test-merge-gate.py#fixture",
          "tests/integration/test-post-merge-sweep.py#main",
          "tests/integration/test-check-state-records.py#main",
          "tests/integration/test-check-state-table.py#two_feature_tree",
          "tests/integration/test-check-state-feat59.py#_in_era",
          "tests/integration/test-validate-feature-json.py#full_doc",
          "tests/integration/test-validate-digest.py",
          ".claude/skills/harness/bin/digest-schemas/harness-backend-dev.json",
          "tests/unit/omp-hooks.test.ts",
          "tests/manual/probe-inflight-claim-lifecycle.py",
          "tests/unit/test-digest-schemas.py",
          "tests/integration/test-feature-corpus.py",
          "tests/integration/test-hooks-install.py",
          "tests/integration/test-factory-integration.py",
          "tests/integration/test-station-argument-spelling.py"
        ],
        "now": [
          ".claude/skills/harness/bin/gh-sync.py#main",
          ".claude/skills/harness/bin/feature_schema.py#recovery_command_for",
          ".claude/skills/harness/bin/feature-schema.json#github",
          ".claude/skills/harness/bin/feature-record.py#cmd_close_run",
          ".claude/skills/harness/bin/digest_record.py#load_record",
          ".claude/skills/harness/bin/validate-digest.py#cli_object",
          ".claude/skills/harness/bin/check_state/feature_record.py#inv_7",
          ".claude/skills/harness/bin/check_state/run_state.py#inv_15",
          ".claude/skills/harness/bin/check_state/table.py#INVARIANTS",
          ".claude/skills/harness/bin/check_state/board.py#inv_37",
          ".claude/skills/harness/bin/merge-gate.py#_enforce_receipt",
          ".claude/skills/harness/bin/post-merge-sweep.py#_receipt_allows_removal",
          ".claude/skills/harness/bin/board_lifecycle.py#_status_findings",
          "tests/unit/test-feature-record.py#CloseRunTest",
          "tests/unit/test-digest-record.py#DurableRecord",
          "tests/unit/test-gh-sync-build-entry.py#base_doc",
          "tests/unit/test-feature-schema-build-entry.py#write_plan",
          "tests/integration/gh_sync_support.py#stage_station",
          "tests/integration/test-gh-sync-open.py#main",
          "tests/integration/test-gh-sync-start-task.py#main",
          "tests/integration/test-gh-sync-ship.py#main",
          "tests/integration/test-gh-sync-abandon.py#main",
          "tests/integration/test-gh-sync-record.py#main",
          "tests/integration/test-gh-issue-types.py#check",
          "tests/integration/test-board-lifecycle.py#write_root",
          "tests/integration/test-merge-gate.py#fixture",
          "tests/integration/test-post-merge-sweep.py#main",
          "tests/integration/test-check-state-records.py#main",
          "tests/integration/test-check-state-table.py#two_feature_tree",
          "tests/integration/test-check-state-feat59.py#_in_era",
          "tests/integration/test-validate-feature-json.py#full_doc",
          "tests/integration/test-validate-digest.py",
          ".claude/skills/harness/bin/digest-schemas/harness-backend-dev.json",
          "tests/manual/probe-inflight-claim-lifecycle.py"
        ],
        "reason": "DEC-182 machine-line budget (56>50); dropped surfaces stay lane-routed main-session-direct; full touched set in notes/amendment-T-01-budget-2026-11-07.md; T-01 done, no scope change"
      }
    ]
  }
}
```
