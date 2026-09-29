# Simplify pass — FEAT-70 — over `git diff 9e531b34..dbba18f7`, new/changed lines only

Four read-only readers (reuse, simplification, efficiency, altitude), 2026-09-28. Applied in the
commit that follows dbba18f7 and precedes the pin; skipped items carry their reason.

## Applied
- Entry `plan-merge.py`: six dead stdlib imports and `import yaml` removed (only `argparse`, `os`,
  `sys` are used); the docstring paragraph claiming `import yaml` survives in this file corrected
  to say the package; a paragraph naming the package added; the VERBS comment gained the sentence
  saying WHY the table and four registrars stay in the entry (altitude 1/2, simplification 1/2,
  efficiency 2).
- `amend.py`: `_amend_preflight` no longer re-imports `hashlib` (module-level import exists);
  `first, last, _ = located` for the unread indent; `_amend_rendered` takes `f2, l2, ind2` instead
  of a re-packed tuple (reuse 4, efficiency 1, simplification 4/5).
- `text.py`: `_half_open_ranges` docstring no longer claims `_index_list_items` uses it (reuse 6).
- `amendments.py`: `_amendment_against_plan` uses `text._item_by_id` instead of its own inline
  scan — the one other caller of the predicate the new helper extracted (reuse 3).
- `stations.py`: `TASK_ID_RE` deleted; the module uses `text.ITEM_ID_RE`, the byte-identical
  pattern — the consolidation the grilling named (reuse 5, altitude).
- Tests: `import shutil` hoisted to `check_state_support`'s module imports; `copy_plan_merge`'s
  import hoisted to `test-plan-merge.py`'s header; `copy_executable_package`'s docstring says "the
  two tools" rather than "every tool" (simplification 6/7, altitude 7).

## Skipped, with reason
- Reuse 1 (delete `_task_search`, route `_task_status_line` through `_item_range_within`): T-01
  prescribes `_task_search` and `_status_in_task` by name and behaviour (append-before-break id
  list, scan-to-end for a final task); the two scans also differ in their terminator test (`==`
  vs `<=` indent). Kept as planned.
- Reuse 2 (`_task_search` should call `_closes_item`): the match object is already in hand there;
  re-matching to share a two-line predicate is not smaller.
- Simplification 3 / altitude (merge the two `from plan_merge.approval import` lines): the
  second line's `# noqa: F401  INV-40's import` is what documents the re-export; kept separate.
- Efficiency 3 (`copy_plan_merge` has no caller in the suite): T-01 names it as the one way a
  proof copies the tool; the mutation campaigns that use it are QA's, not suite cases. Kept.
- Simplification (`_verify_schema_preserved` nests two ifs / `_item_closed_by_range` has four
  parameters): both at grade 5; the nesting is the moved comment block's shape; not smaller.
