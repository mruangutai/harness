# BRIEF — FEAT-70 long-file plan-merge package

## Problem

The operator and code maintainers must currently trust and change 3,854 lines and 214 functions in one `.claude/skills/harness/bin/plan-merge.py`, even though its verbs write distinct plan surfaces and share only a smaller set of text and guard primitives. Twelve functions fall below code grade 4, and `record-amendments` crashes when the first of two amendments targets a block-scalar field because `_render_field` returns that multi-line value as one list element. A mechanical split alone would hide those liabilities behind imports and could weaken the byte-preserving writer contract.

## Done when — by perspective

**operator** — I can continue invoking the unchanged hyphenated entry and receive the same exit status, stdout, stderr, and written bytes from every pre-existing command, while the two-entry block-scalar `record-amendments` case now succeeds atomically instead of crashing. Reproducible receipts compare the baseline and immutable implementation pin from clean detached checkouts without normalizing away any difference except their absolute roots.

**code maintainer** — I find a thin entry over exactly the settled ten-module `plan_merge/` package, with each verb family and shared primitive in its declared owner, public `signed_task_hash` still reachable from the entry, package-aware tests and canonical-reader identities, and every function across entry and package at code grade 4 or better.

## Success criteria

- SC-01 (code maintainer): At the immutable implementation pin, `.claude/skills/harness/bin/plan-merge.py` is the unchanged hyphenated forked interface and a thin roughly 250-line dispatcher containing the docstring, imports/re-exports, four argument registrars, unchanged `VERBS` dispatch table, and `main`; `.claude/skills/harness/bin/plan_merge/` contains `__init__.py` plus exactly `text.py`, `guards.py`, `union.py`, `approval.py`, `stations.py`, `panel.py`, `amend.py`, `amendments.py`, `delete.py`, and `check.py`. Automated grading reports every function on that complete surface at grade 4 or better, explicitly including baseline grade-2 `_task_status_line`, `_verify_spliced`, `cmd_amend`, and `cmd_amend.transform` and grade-3 `_item_range`, `_index_list_items`, `_find_field_line`, `_parsed_value`, `_index_top_keys`, `_print_apply_receipt`, `_panel_own_end`, and `_replace_fields`. Every moved function is matched by identity to its baseline pre-image and has both grades recorded: unchanged bodies retain grade identity, while those twelve improve to the bar. Genuinely new glue is graded as new without exemption, and importing `signed_task_hash` from the entry still succeeds.
  verify: automated
  evidence: integration
- SC-02 (operator): The baseline checkout at `9e531b34fc04f752cedf51586dc13c460580901a` runs all 107 pre-existing `test-plan-merge.py` cases green against its monolith, and the immutable implementation pin runs package-aware versions of those same 107 cases green against its entry plus package; the pin relocates private-helper imports and source-wiring assertions to their real package owners rather than retaining monolith assertions through entry re-exports or source padding. A committed comparison driver separately captures every behavioral CLI subprocess observation exercised by those 107 cases and produces identical exit status, stdout bytes, stderr bytes, and written plan bytes between clean detached baseline and pin checkouts after replacing only each checkout's absolute root with one common token. The same exact comparison covers a fixed scratch-copy script over every repository feature `plan.yaml` except FEAT-70 itself: for each scratch plan it records `check`, idempotent-shaped `set-feature-station` to the current station, `set-task-station` for each task to its current-or-default station, and `amend --show` for eligible fields. Monolith source-text checks and private in-process helper calls are suite assertions, not identity inputs; their package-aware pin equivalents must pass, while `record-amendments` is excluded from the identity comparison because baseline crashes. Raw bytes and hashes are retained, each measurement runs once per checkout, every non-root difference is ledgered as exact old and new bytes, and any unledgered difference fails the criterion. The unchanged entry path remains usable by all existing consumers, the test mutation harness copies entry plus package through one shared integration-support operation, and the 15 canonical-reader rows and `scanned_files` identify their real package sources.
  verify: automated
  evidence: integration
  fail-first: the baseline-versus-pin byte comparison is this semantics-preserving refactor's fail-first equivalent; the pin side does not exist before implementation.
- SC-03 (operator): A committed red-first integration case supplies `record-amendments` a two-entry digest whose first entry amends a block-scalar field. It fails at baseline on the `_render_field`/`_splice_amendments` list-shape defect and passes at the immutable pin, where both requested amendments land, the block scalar reloads with the requested value, the amendment ledger validates, the plan and ledger update atomically, and no traceback is emitted.
  verify: automated
  evidence: integration

## Verification gaps

- none; the owning integration runner is active, and the immutable-pin scripts retain chronology, raw evidence, normalization, and exact-difference records for review.

## Constraints

- Preserve the exact package ownership settled in grilling. `text.py` owns indexing, splicing, rendering, reindentation, item deletion boundaries, and the shared regexes; `guards.py` owns plan resolution, legal-station refusal, reload/schema refusal, locking, byte replacement/restoration, governed-agent refusal, and anchors; `union.py` owns apply/add-tasks, `MergeResult`, and merge verification; `approval.py` owns sign/revoke, rework, signed-task hashes, and approval-signature helpers; `stations.py` owns station verbs, station classification, and the complete approval reset/resume family; `panel.py` owns validators, byte-preserving panel splice, record-panel, set-key, set-panel, set-lanes, and the single-module `KEY_VALIDATORS` forward binding; the remaining verb families live in `amend.py`, `amendments.py`, `delete.py`, and `check.py`.
- Put the reset/resume family in `stations.py` because its discriminating inputs are task and feature stations. Move the complete family from `_now_iso` through `_maybe_reset_approval`, including its constants and helpers; `approval.py` calls it for revoke rather than duplicating classification.
- Decompose `_task_status_line` in `stations.py` into `_task_search`, `_status_in_task`, and the coordinator. Preserve task-key scoping, append-before-break id collection, same-indent boundaries, scan-to-end behavior, first deeper-indented `status:` selection, tuple shapes, id ordering, and every refusal observed by callers.
- Decompose `_verify_spliced` in `union.py` into `_reload_spliced`, `_verify_schema_preserved`, `_expected_union_ids`, `_verify_union_ids`, and the coordinator. Preserve the current signature including `added_ids`, exact refusal codes and text, mapping check, valid-base-only schema check, output-order filtering, base-first unseen-proposal id order, replacement verification, and return value.
- Fix the crash at its source: `_render_field` in `text.py` returns a multi-line block scalar as the line-list shape consumed by `_splice_amendments`, without special-casing the digest. Consolidate `TASK_ID_RE` and `ITEM_ID_RE` into one shared regex. Move all comments and banners byte-for-byte; make no gratuitous rename.
- Preserve `.claude/skills/harness/bin/plan-merge.py` for every existing caller and keep `signed_task_hash` importable from it for check-state INV-40. There is one CLI and one `VERBS` table, with no shim, alias, family entry point, or second dispatch layer.
- Re-key exactly the 15 affected canonical-reader fixture rows to their real `plan_merge/<module>.py::symbol` identities and update `scanned_files`. Refactor `check_state_support.copy_check_state`'s existing executable-plus-sibling-package behavior into one generalized `copy_executable_package(entry, package_name, dst_bin)` integration-support operation: it copies the entry with executable mode retained and its complete sibling package without caches. Both `copy_check_state` and the plan-merge copy caller delegate to that operation; the latter passes the entry selected by `PLAN_MERGE_BIN` and resolves sibling `plan_merge` from it. No independent second copy implementation, dead private re-export, or source padding is permitted. Keep `UNION_MERGE`, `PRESERVE_BASE_BYTES`, and `APPROVAL_REFUSAL` in the owner module whose source the proof mutates.
- Baseline is `9e531b34fc04f752cedf51586dc13c460580901a`. Pin and receipt chronology follow FEAT-69: implementation is committed first; receipt scripts and receipt files are committed later; all name full SHAs. Only raw checkout-root bytes may be normalized.
- DEC-174 BLOCKS team execution of the canonical plan writer, its owning tests, classifications, and proof collection; every task is `main-session-direct`. DEC-182 SUPPLIES package-glob ownership so task machine fields remain within the 50-line limit. DEC-232 BLOCKS line-number anchors; only path, path#symbol, and `{path, quote}` anchors are legal.
- Approval remains pending. At signature, recommend—but do not sign—a rework ruling of 2 rounds and 480 wall-clock minutes, following FEAT-69 precedent.

## Out of scope

- Making `plan-merge.py amend` write an amendment ledger entry; that is a separate behavior issue.
- Making `gh-sync ship` refuse a clone that is not the root checkout; that is a separate issue.
- Refactoring `validate-digest.py`, `check-domain.py`, or `gh-sync.py`; they are later long-file waves.
- A file-length ratchet, a compatibility shim, renamed commands, changed output, or any normalization beyond detached-checkout root replacement.

## Approval

status: pending
