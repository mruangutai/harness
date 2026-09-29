# Grilling — long-file wave 2: plan-merge.py becomes the `plan_merge/` package — 2026-09-28

## Destination
`.claude/skills/harness/bin/plan-merge.py` (3,854 lines, 214 functions at 9e531b34fc04f752cedf51586dc13c460580901a,
the base of this feature's worktree) is a ~250-line entry (docstring, `VERBS` table, the four
registrars, `main`) over a `bin/plan_merge/` package of ten modules. Every verb's output and every
byte it writes is identical before and after; every function in the entry and the package is at
code-grade bar 4 (twelve below-bar functions fixed in scope); the `record-amendments` block-scalar
crash is fixed in the text primitive that causes it.

## Mission
mission: plan
reason: cause known and diff bounded, but a new importable surface (the package), twelve grade fixes
in shared text primitives, and a behaviour fix — the patch rule fails on all three.
confirmed-by: operator

Every task is `execution_mode: main-session-direct` (DEC-174: plan-merge.py gates every plan write
and is itself enforcement; the main session writes the diff).

## Settled
- Which long file second → plan-merge.py (3,854; verb-shaped, no structural lock keyed on it, no
  DECISIONS.md line anchors). Baseline pinned at the worktree's base 9e531b34, not the root checkout.
- Bar → (a): SC-01 file-wide, every function in `plan-merge.py` and `plan_merge/**` at grade ≥4 after
  the pin. The twelve below-bar functions at 9e531b34 are fixed in the module they land in:
  grade 2 `_task_status_line` (1387; cyc 15/cog 28), `_verify_spliced` (545; 15/22), `cmd_amend`
  (3079; ABC 32.2), `cmd_amend.transform` (3108; ABC 31.1); grade 3 `_item_range` (2735),
  `_index_list_items` (297), `_find_field_line` (2834), `_parsed_value` (2995), `_index_top_keys`
  (271), `_print_apply_receipt` (1364), `_panel_own_end` (1744), `_replace_fields` (757).
  Moved code proves itself by grade identity against the pre-image; new glue graded new at bar 4.
- Modules → (b), ten under `bin/plan_merge/` with `__init__.py`, by what each verb family writes,
  text primitives shared as core:
  `text.py` (index/splice/render primitives — `_index_top_keys`, `_index_list_items`, `_field_lines`,
  `_item_range`, `_field_block`, `_render_field`, `_structured_field_lines`, `_reindent`, `_splice_out`,
  `_item_delete_end` and the regexes; already shared by apply, amend, panel, record-amendments) ·
  `guards.py` (`_resolve_plan`, `_legal_stations`, `_refuse_illegal_station`, `_reload_or_refuse`,
  `_schema_error`, `_die`, `_locked_plan_update`, `_replace_bytes`, `_restore_plan`,
  `_refuse_governed_agent`, anchors) · `union.py` (apply/add-tasks, `MergeResult`, `_verify_spliced`) ·
  `approval.py` (sign/revoke, rework, signed task hashes incl. public `signed_task_hash`, approval
  reset) · `stations.py` (set-task-station/set-feature-station + station classification) ·
  `panel.py` (panel/lanes validators, byte-preserving panel splice, record-panel, AND set-key/
  set-panel/set-lanes — keys folded in so `KEY_VALIDATORS`' forward binding stays in one module) ·
  `amend.py` · `amendments.py` (record-amendments; keeps the plan+ledger all-or-nothing write) ·
  `delete.py` · `check.py`. Placement rule: the delete-first bullet (put it where its inputs are).
  No separate discretion module: the entry's `VERBS` table is the one dispatch point, unchanged.
- Entry keeps the hyphenated name and path every forker uses (gh-sync ×2, feature-record,
  test-plan-merge's 107 subprocess cases, plan-sign-gate basename, check-domain denial text,
  test-check-domain-approval's isfile). `signed_task_hash` stays importable from the entry for
  check_state's INV-40 loader.
- Evidence (SC-02) → (a): test-plan-merge.py's 107 cases green at baseline and pin, PLUS over a
  scratch copy of every feature's plan.yaml (this feature's own record excluded, as ruled for
  FEAT-69) baseline vs pin byte-for-byte: `check` output, and the bytes after a fixed script of
  idempotent-shaped mutations (`set-feature-station` to the current station, `set-task-station`
  likewise, `amend --show`). `record-amendments` excluded from the scratch script (crashes at
  baseline); its fix has a red-first test instead (SC-03 analogue). Clean detached checkouts of
  base and pin; only the root normalisation; every other byte ledgered; receipt scripts committed.
- The crash → in scope: `_render_field` (2888) returns a multi-line block scalar as ONE list
  element (`["".join(out)]`, 2911), so `_splice_amendments` (2543) re-locates the next entry over
  a list shorter than the document. Fix the return-shape contract in `text.py`; red test = a
  record-amendments digest with two entries where the first amends a block-scalar field.
- Free consolidations taken: `TASK_ID_RE` (1382) and `ITEM_ID_RE` (2731) are one regex.
- Mechanical costs accepted: 15 `canonical-reader-classification.json` rows re-keyed to
  `plan_merge/<module>.py::symbol` and `scanned_files` updated; the test suite gains a tree-copy
  helper (as `check_state_support.copy_check_state`) so `PLAN_MERGE_BIN` mutation proofs copy the
  package, not one file; the three test-flipped switches (`UNION_MERGE`, `PRESERVE_BASE_BYTES`,
  `APPROVAL_REFUSAL`) live in the module whose source the proofs mutate.
- Comments and banners move byte-for-byte; no renames beyond what the package forces.

## Not yet specified
- Whether the approval-reset family (`_maybe_reset_approval` and helpers, 789-950) sits in
  `approval.py` or `stations.py` — its inputs are task statuses (stations) and its output is the
  approval block; pm decides by the placement rule.
- The exact decomposition of `_task_status_line` and `_verify_spliced`; the destination only
  requires ≥4 with identical behaviour.

## Out of scope
- `plan-merge.py amend` writing a field without a ledger entry (INV-40 then fires) — behaviour
  change, issue.
- `gh-sync ship` refusing to run from a clone that is not the root checkout — issue.
- validate-digest.py, check-domain.py, gh-sync.py as long files — later waves; the dispatcher wave.
