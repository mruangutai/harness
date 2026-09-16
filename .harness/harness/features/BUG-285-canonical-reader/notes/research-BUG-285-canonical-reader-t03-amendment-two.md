# Research — BUG-285 canonical reader T-03 amendment two

## Conclusion

The operator ruling is fully represented in the plan by narrow T-02 and T-03 intent amendments. T-02 and T-03 are ready, and the controlled T-02 task-field amendment reset approval.status to pending.

## Ruling source

- Source: `.harness/harness/features/BUG-285-canonical-reader/notes/answers-2026-09-15-t03-eng.md`
- Ruling: generalize the existing accessors. `parse_gh_json` returns any strict JSON value and leaves shape validation to each consumer. `load_feature_json` accepts mutually exclusive path and keyword-only text sources through one strict parser and typed-error contract. No separate accessor, exemption, or temporary-file bridge is allowed.

## Plan amendments

- T-02.intent now requires the existing public `parse_gh_json(text, context)` to return mappings, lists, or scalars; reject nested duplicate keys and NaN, Infinity, and -Infinity; preserve caller context; and raise the existing typed accessor error. It assigns mapping, list, scalar, entry, and field shape validation to consumers and plans focused accessor tests for all result shapes, strictness, context, and typed failures.
- T-02.intent now requires the existing public `load_feature_json` to accept either a path or explicit keyword-only text, mutually exclusively. Both modes share the strict parser, feature mapping and field validation, caller context, and typed errors. Focused tests cover both modes, mutual exclusion, strictness, mapping and field validation, context, and typed failures.
- T-02 forbids new public accessors, exemptions, caller-local wrappers or adapters, compatibility aliases, temporary-file bridges, and reader temporary files. Its existing focused files and verify command already cover `test-artifact-accessors.py` and `test-feature-json-reader.py`, so those fields were not changed.
- T-03.intent now requires `gh-sync.py::_record_pr` and `gh-sync.py::cmd_ship.first_open_child` to call `parse_gh_json` while retaining consumer-owned list, entry, and field shape checks.
- T-03.intent now requires `worktree_terminal.py::_read_landed_feature_json` to call `load_feature_json` with decoded git-show feature.json content as `text` and the landed source as `context`, retaining feature mapping and field validation.
- Every other T-03 bypass remedy and caller contract remains in place. Its existing files and verify command already target `gh-sync.py`, `worktree_terminal.py`, `test-gh-sync-record.py`, and `test-worktree-terminal.py`, so those fields were not changed.

## State and validation

- T-02 status: ready, changed from done with `plan-merge.py set-task-station`.
- T-03 status: ready, unchanged.
- approval.status: pending, reset automatically by the controlled T-02 task-field amendment; approval was not edited directly.
- The required sole check exited 0: `plan-merge.py check` resolved 9 tasks and 145 anchors with 0 failures.

## Scope confirmation

This run changed only `plan.yaml` and this research note. Production files, tests, BRIEF.md, panel history, classification data, decisions, routes, dependencies, unrelated tasks, approval fields directly, and all other planning artifacts were untouched. No formatter, linter, build, test, suite, git-wide validation, or other non-planning validation ran.
