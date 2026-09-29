# Research — plan-merge package plan

## Baseline and live surface

- The binding baseline is `9e531b34fc04f752cedf51586dc13c460580901a` in the FEAT-70 worktree. Its `.claude/skills/harness/bin/plan-merge.py` is 3,854 lines and 214 functions.
- The existing scoped integration suite completed green in 29.88 seconds in that worktree. The binding record fixes its baseline/pin evidence set at 107 subprocess cases.
- The hyphenated entry is a compatibility surface for `gh-sync.py` at two call sites, `feature-record.py`, `plan-sign-gate.py`, `check-domain.py`, and the owning tests. `check_state` also imports public `signed_task_hash` from that entry for INV-40.
- The canonical-reader fixture has exactly 15 rows sourced from `plan-merge.py`; the package cutover must change only their source-derived `file` and `id` values and update `scanned_files` to the entry plus complete package.

## Decisions that grilling left to planning

### Approval reset belongs with station inputs

Move the complete reset/resume family from `_now_iso` through `_maybe_reset_approval`, including `RESET_FIELDS`, `_RESET_LINE_RE`, `_approval_status`, `_replace_approval_reset`, `_reset_approval_lines`, `_task_statuses`, `_review_complete`, `_WORK_STARTED`, `_work_started`, `_resume_station`, `_verify_reset`, and `_approval_reset_context`, to `stations.py`. Its discriminating inputs are task and feature stations and its central decision is the resume station; `approval.py` may call that family for revoke but does not own the classification. This follows the settled delete-first placement rule: put behavior where its inputs are.

### Grade-2 decompositions preserve current edge behavior

In `stations.py`, split `_task_status_line` into `_task_search(lines, lo, hi, task_id)` and `_status_in_task(lines, start, indent)` plus the small coordinator. `_task_search` must preserve the current append-before-break behavior, including the same-indented terminator id in `ids_present` after a found task; `_status_in_task` must retain the current scan-to-end and first deeper-indented `status:` semantics. The coordinator remains scoped by `_index_top_keys` to the `tasks` range and returns the same tuple shapes and id order.

In `union.py`, split `_verify_spliced` into `_reload_spliced`, `_verify_schema_preserved`, `_expected_union_ids`, and `_verify_union_ids`, leaving `_verify_spliced` as their coordinator followed by `_verify_replaced`. Preserve its signature, including currently unused `added_ids`, exact refusal codes/messages, mapping requirement, valid-base-only schema rule, `UNION_KEYS`/`out_order` filtering, base-first unseen-proposal id order, replacement verification, and returned document.

## Proof design

- The first implementation task owns the red-first block-scalar regression before production edits, the package split, package-aware test copying, and the 15 classification moves. Keeping those together prevents a task boundary from making the suite unable to load the new package.
- The second task starts only after the implementation is committed, names that commit as the immutable pin, and adapts the FEAT-69 receipt pattern. Clean detached baseline and pin checkouts run the same 107 cases and the fixed scratch-plan script over every feature `plan.yaml` except FEAT-70 itself. Only checkout-root bytes may be normalized; every other difference is ledgered.
- `record-amendments` is deliberately absent from the baseline/pin scratch script because baseline crashes. A dedicated two-entry regression, with the first entry amending a block scalar, proves the corrected `_render_field` list-of-lines contract and atomic plan-plus-ledger outcome.
- All implementation and receipt work is main-session-direct because the canonical plan writer, its source classifications, its owning tests, and its proof artifacts are one DEC-174 enforcement surface.

## Principles applied

- Outcome-Oriented Execution: each task ends in an independently checkable state—first the working package and regression gate, then immutable-pin receipts—rather than stopping at file movement.
- Redesign From First Principles: module boundaries follow the state each verb family writes, while the shared text and guard primitives remain deep common modules; no compatibility layer or second dispatcher is introduced.
