# BUG-2399 code review c0

**FAIL — compliance passes; the exact pinned Python quality gate reports three high failures.**

Reviewed `59289ad1..3835fde4f16d1b34d8711fc8607b5153545bfaec`. No `[harness:human]` commits. Working-tree dirt is confined to this feature's metadata/run records; reviewed production bytes are pinned.

## Stage 1 — compliance: PASS

SC-01..03 are represented by canonical repository/snippet tracking assertions, historical-rule migration and operator command composition, distill refusal/commit/merge, and interrupted-run removal refusal/preservation. The pinned red/green receipts record failures before production changes and subsequent zero exits; these are inspected records, not executions by this reviewer. No gate predicates or historical run backfill appear in the diff.

**SC-04 inspection:** `git show 3835fde4:<path>` confirms DEC-257 at `.harness/harness/docs/DECISIONS.md:8536`, unchanged DEC-238 at `:8046`, SPEC commit policy at `.harness/harness/docs/SPEC.md:252`, operator review/staging/commit at `.claude/skills/harness/references/checkout-upgrade.md:38`, distill commit/push before merge at `.claude/skills/harness/references/distillation.md:49`, and the build-time zero-inventory receipt in `notes/research-BUG-2399-run-records-tracked-draft.md` under “Dirty-tree inventory.” The decision diff only appends DEC-257; SPEC 8.6 and INV-7/INV-36 semantics are not changed.

Deviation judgments: retaining `PYTHONUSERBASE` while isolating Git configuration is an environment correction, not weakened assertions. An interrupted `in_progress` run with partial digest models the stated aborted-work consequence without inventing a run status. The role/team/README corrections are explicit T-03 scope additions serving SC-04/D-01, not independent behavior changes; the T-02 feature-worktree comment correction likewise changes no predicate. The panel-record correction changes bookkeeping, not acceptance. The reported `case_landed_differs` failure is not re-executed or independently diagnosed here.

## Stage 2 — quality: FAIL

Executed only `code-grade.py --base 59289ad1 --head 3835fde4f16d1b34d8711fc8607b5153545bfaec` (exit 1). No tests, builds, lint or formatters ran. The following are measured maintainability-gate failures, not claimed runtime failures:

| Severity | Owner | Pinned function | CC / cognitive / ABC | Result / driver |
|---|---|---|---|---|
| high | T-02 | `.claude/skills/harness/bin/merge-gitignore.py:95` `_without_obsolete` | 10 / 14 / 16.4 | grade 3 < production bar 4; CC+cognitive |
| high | T-02 | `.claude/skills/harness/bin/merge-gitignore.py:171` `_merge` | 9 / 11 / 21.7 | grade 3 < production bar 4; all metrics |
| high | T-01 | `tests/integration/test-merge-gitignore.py:305` `case_bug2399_operator_checklist_commands_compose` | 6 / 2 / 50.3 | grade 1 < test bar 3; ABC |
| med | T-01 | `tests/integration/test-feature-worktree.py:1038` `case_remove_refuses_aborted_run_evidence` | 12 / 5 / 40.4 | grade 2; CC+ABC |
| med | T-01 | `tests/integration/test-merge-gate.py:722` `case_bug2399_distill_records_commit_before_merge` | 7 / 3 / 35.6 | grade 2; ABC |
| med | T-01 | `tests/integration/test-merge-gitignore.py:238` `case_bug2399_merge_replaces_broad_rules` | 7 / 4 / 30.2 | grade 2; ABC |

Grade-2 reasons: `case_remove_refuses_aborted_run_evidence` keeps the landed setup, refusal and byte-preservation observations in one lifecycle scenario; `case_bug2399_distill_records_commit_before_merge` must observe the same candidate both before and after committing/pushing records; `case_bug2399_merge_replaces_broad_rules` applies the same migration/idempotence contract to the three shipped-rule combinations. These advisory records do not themselves block.

**Must fix:** simplify the three high functions to their applicable bars without weakening acceptance or hiding complexity behind pass-through helpers. No additional concrete fail-open or silent-failure defect was established by static inspection.

## Principles applied

- Delete First: assessed additions in the existing merger rather than requiring another migration layer; remediation should reduce reader load, not manufacture wrappers.
- Migrate Callers, Then Delete Legacy APIs: inspected both shipped broad-rule spellings and caller instructions together; no compatibility API was introduced.

## Open questions

None. QA owns required gate executions after review; the next review must bind the grader to the new pin.
