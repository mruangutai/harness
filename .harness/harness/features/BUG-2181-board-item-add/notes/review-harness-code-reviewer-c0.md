# BUG-2181 · T-01 · code review c0

PASS — no substantive, form, or proportionality findings in the pinned patch. Spec compliance completed before the quality assessment.

Reviewed `5f935b55..5d78ffc3ccf4d1c49aae47b9183a2c305c0be6a7`; canonical merge-base is `b7af829c0207522b43f978b5275a2ebdc96b3210`. Inspected all commits from that merge-base: earlier changes are feature intake records, not additional Python changes. No `[harness:human]` commits; no modified tracked files. Dispatch and feature.json pins agree. No task-field amendments found.

## Stage 1 — spec compliance

- **SC-01:** `tests/integration/test-gh-sync-board-add.py:68-92` invokes real gh-sync through the shared fake transport. The absent #326 assertion requires exactly one add with board 3, owner mruangutai, canonical issue URL, lookup/add/edit order, returned ADDED_326 and Building. Positive parent #40 and both-present edits accompany the no-add assertions. Both transports bind the same fake (`gh_sync_support.py:200-217`). Pre-fix behavioral failure is recorded in pinned `notes/build-evidence-2026-11-08.md:25-32`; independent execution belongs to QA.
- **SC-02:** `tests/unit/test-gh-board-item-add.py:77-107` calls real set_station with recording factory_gh functions. Exact complete logs bind owner, number, URL, field, capitalized column, returned/existing identity, ordering and no duplicate add. Lookup/add/set errors (including set after each item path) require BoardError, original #17, lowercase ready, and no downstream calls. Removing add, using the wrong id/arguments, unconditional addition, swallowing an exception or continuing after it violates these assertions by inspection. Fail-first witnesses are pinned in `notes/build-evidence-2026-11-08.md:13-23`.
- **SC-03 — inspected using the required `git show 5d78ffc3ccf4d1c49aae47b9183a2c305c0be6a7:.claude/skills/harness/references/repo-board-provisioning.md`:** step 5, lines **39–41**, says Auto-add to project is not required because gh-sync/set_station adds missing cards before setting station. Lines **32–37** retain unchanged the three hard-gate requirements: Item closed, Auto-close issue, Pull request merged, operator enablement and successful re-audit. The diff adds only this paragraph.
- Every production/test/doc change serves SC-01/02/03; feature metadata/evidence records support T-01. No factory_decompose, audit, registration gate or caller edits. Optional PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md remain absent; no guidance invented.

## Stage 2 — code quality

`gh_board.py:387-400` adds only on `item_id is None`, uses the returned id, preserves station conversion/field arguments, and encloses lookup/add/set in the existing GhError-to-BoardError handler with original issue and station. A lookup/add failure cannot fall through into a field write. The obsolete absence-refusal fixture now explicitly fails addition (`test-board-station.py:97-110,193-200`). No additional interface or parallel policy was introduced.

Static-only review: no tests, lint, formatter or grader process executed by this reviewer. Pinned build evidence reports changed-function grades 4/5 at 317db504; `git diff 317db504..5d78ffc3 -- '*.py'` is empty, and the earlier merge-base-to-plan range has no Python changes. `code_grade: pass` is supported by that recorded result, not an independent grader run; canonical recomputation remains validator-owned. No grade-2 reasons.

## Principles applied

- **Delete First:** the local guarded addition replaces the obsolete refusal at the existing shared seam; no wrapper, threaded flag or caller-specific branch is needed.

## Open questions

None. QA owns independent fail-first/green verification; this PASS is the static code-review assessment, not a test-run claim.
