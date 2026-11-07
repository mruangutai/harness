# Receipt: harness-dev-ops, BUG-2161 SIMPLIFY efficiency reader

**BLUF: no efficiency findings (empty result).** Read-only; no checks, tests or edits run.

## Diff inspected
`git diff 5094e854 21bfa01d` limited to `.claude/skills/harness/bin/gh-sync.py` (+110/-31), `tests/integration/test-gh-sync-abandon.py` (+378), `tests/unit/test-gh-sync-abandon-sources.py` (+417). Angle: `harness-simplify/references/angle-efficiency.md`.

## Costed observations (all advisory, none flagged)
- `cmd_abandon` adds one `_feature_station` read (one `plan.yaml` YAML parse, gh-sync.py:318) and, only under `--close-sources`, one `parse_source_issues` parse (:474). A one-shot operator command; each parse is local disk and milliseconds. No loop, no hot path, no startup work added.
- Guard `if not already_abandoned: _record_station(...)` (:1769) skips a `plan-merge.py` subprocess on re-entry; net work removed, not added.
- `ensure_labels` is now gated on `if plan:`, so an unopened record with nothing to close skips a gh call. Reduction.
- `_abandon_plan` sources loop: `set(rec["issues"].values())` is built once outside the loop; `dict.fromkeys` dedupe is O(n) over a handful of tickets. `_ABANDON_COMMENT_TARGET` is a module constant, no closure capture; `_report_abandon_gaps` `any(...)` over a plan of at most tens of tuples.
- Writes per source: reason comment plus one close/reseat, same per-issue shape as existing task issues; a source that is also a task is closed once (no duplicate close).
- Tests: about 18 new `run([...])` subprocesses over per-case tempdirs with the fake shell gh, the same pattern and per-case cost as the existing cases in the file; the unit file uses an in-process stub, so no subprocess. Not a plan or suite re-run surface. The signed T-01 verify chain runs three suites at a boundary step, which is evidence, not waste (P-16 and the angle's rule).

## Findings
none

## Flag-only candidates
none
