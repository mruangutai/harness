# T-02 build: plan_merge's amendment pair on the journaled core

Built main-session-direct under DEC-174 by BuildE_T02, the ungoverned builder for the main session. Worktree HEAD `8eaf4298`, base `2491336e`. The only git writes were the C3 detached base worktree (`git worktree add --detach` / `git worktree remove`). HARNESS_AGENT_TYPE and CLAUDE_PROJECT_DIR were unset for every run. Every receipt is whole stdout+stderr with its exit code, kept in `notes/` and `notes/t02-build/` (C6).

## Files changed
- `.claude/skills/harness/bin/feature_json_write.py`: adds `schema_checked_transform(path, transform, tail_regex=None)`. It returns `(resolved, wrapped)` and writes nothing. `write_feature_json` now calls it, then `locked_update`, then the relay; its signature and behaviour are unchanged. The module docstring no longer claims an fsync. It now says `locked_update` performs none and only harness_merge's intent journal is fsync'd.
- `plan_merge/amendments.py`: `write_plan_and_ledger` makes one `harness_merge.locked_pair_update` call. The outcome comes from the exception type alone. The post-commit feedback is advisory. The docstring is rewritten, `_record_amendment_judgements` is deleted, the `_replace_bytes`/`_restore_plan` imports are dropped, and `harness_boundary` is imported.
- `plan_merge/guards.py`: `_replace_bytes`, `_restore_plan` and the `tempfile` import are deleted. Two additions:
  - `_resolve_plan(file_path, recover=True)` recovers journals inside the same `try`.
  - `_pending_replay_lines` holds item 2's two replay lines. It has one home, shared by `_resolve_plan` and `write_plan_and_ledger`.
- `plan_merge/check.py`: `_check_inputs` calls `_resolve_plan(args.file, recover=False)`.
- `plan_merge/amend.py`: the `APPROVAL_RESET_LINE` import, the `result` dict and argument, `result["reset"] = False`, the two-line reset print, the `result`/`base_doc` parameters of `_amended_text`, and its docstring sentence are all removed. The transform's own `base_doc` stays. `_load_structured_value`, `_ledgered_target` and `cmd_amend.transform` keep their names.
- `plan_merge/approval.py`: `_write_brief_signature` writes through `harness_merge.replace_bytes(brief_path, signed.encode("utf-8"))`. The docstring is reworded per C2 and the `tempfile` import is dropped. Behaviour is unchanged.
- `plan-merge.py`: the exit-5 contract gains the intent-journal clause.
- `tests/integration/test-plan-merge.py`: nine new cases (a)–(j), with (d) folded into (a)–(c). All are registered in CASES. The three SC-05 cases are migrated.
- `notes/red-t02-plan-merge-base.txt`: the red receipt.

The forbidden surfaces were not touched: `check-plan-routes.py`, `test-check-plan-routes.py`, `check_state/` and `union.py` (`t02-build/07-changed-files.txt`, C4).

## Red (C3)
`red-t02-plan-merge-base.txt` was captured before any production edit. The edited test file was copied into a detached worktree of `2491336e` under `/tmp` and run there with the variables unset; the worktree was removed afterwards. Exit code 1.
- **Fail as required:**
  - (a) both verbs: the ledger never gets its judgement, and the journal stays.
  - (b): exit 0 instead of 6, the judgement is ledgered twice, and the journal stays.
  - (c) both verbs: the journal stays.
  - (e): the judgement is missing and the journal stays.
  - (f): exit 6 instead of 5.
  - (h): `write_plan_and_ledger` raises, because base restores the plan on a feedback failure.
  - (i): fails on its outcome only. Its reached-the-seam check PASSES at base, and the base diagnostic says "restored … nothing landed" instead of naming the journal.
  - (j): the base `_resolve_plan` never reaches the seam, there are no replay lines, and the re-run exits 0.
  - The three migrated cases fail too, because base says "restored byte for byte".
- **Pass, as required:** (g), all three stdout locks. This is SC-04's baseline. Every fixture `_sign` and twin-verb setup check passes at base, so each red is behavioural.

## Green
- `t02-build/01-green-test-plan-merge.txt`: `PASS test-plan-merge.py`, 769 checks, exit code 0. The red run had 765 checks because (j)'s four preflight checks are graded only after its reached-the-seam check passes.
- SC-07 suites (`t02-build/02-*.txt`), each exit code 0:
  - test-harness-merge: 28/28
  - test-feature-json-merge: 41/41
  - test-observations-merge: PASS
  - test-expertise-merge: PASS
  - test-inflight-registry: 168/168
  - test-check-state-feat59: 112 `ok`, 0 `not ok`
  - test-harness-merge-journal: 101/101
- SC-05 (`t02-build/03-…`): the successors carry 1 + 4 + 3 = 8 `check()` calls, equal to the base's 8. Each "restored byte for byte" assertion became "stderr says nothing was written and no `plan.yaml.harness-merge.journal` exists". These are kept: LOCKED, PermissionError, no-Traceback, nonzero exit, both-files-byte-identical, and released-then-lands.
- SC-02 (`t02-build/03-…`): `rg 'mkstemp|os\.replace' .claude/skills/harness/bin/plan_merge/` returns 0 hits (rg exit 1). There is no `def _replace_bytes`, no `def _restore_plan`, and no journal name or suffix in any plan_merge module.

## Verify (literal, from plan.yaml)
`t02-build/06-verify-T-02.txt` exits 0. The command text is in `06-verify-T-02.command.sh`.
- run_pool: all 11 files PASS (4 workers, 27.35s).
- Audit: `0 unresolved reader site(s) across 101 Python file(s)`.
- Inline assertions: `PASS no rename primitive or journal handling in plan_merge; reset bookkeeping and false fsync claim gone`.

## Grade
`t02-build/04-code-grade-base-to-worktree.txt` uses the T-01 script, retitled, with base `2491336e` and the head taken from the working tree. Result: `gated=114 high=0 reason_required=0 result=pass`.
- New production functions grade 4–5 against a bar of 4. `_pair_failure` and `_resolve_plan` are at 4.
- Test functions grade 3–5 against a bar of 3. These four are at 3 on ABC:
  - `case_1985_amend_writes_nothing_when_the_ledger_fails`
  - `case_b1716_record_amendments_writes_nothing_on_a_ledger_io_error`
  - `case_2488_a_failed_replay_stays_pending`
  - the unchanged-grade `case_b1716_record_amendments_is_all_or_nothing`
- Legacy functions (informational): `write_plan_and_ledger` went from 4 to 5, `_write_brief_signature` from 4 to 5, and `write_feature_json`, `cmd_amend`, `cmd_amend.transform` and `_check_inputs` are unchanged.

## Choices inside the shapes (C5: no new journal surface)
- **Helpers:** `_ledger_transform`, `_pair_failure` and `_relay_after_commit` in amendments, and `_recover_plan_journals` in guards. Each converts or relays only; none reads, lists or deletes a journal. `_recover_plan_journals` raises a MergeRefusal for JournalPending (replay lines, exit 2) and for any other Exception ("no file was changed; this command wrote nothing.", exit 2). `_resolve_plan`'s single `try` then prints the lines and exits the code, so no recovery failure prints a Traceback.
- **What `write_plan_and_ledger` catches:** `Exception`, as item 2 specifies. Base caught `BaseException` in order to restore. A KeyboardInterrupt now propagates unchanged, and if it lands after the publish the journal is kept, as the core documents.
- **The `schema_checked_transform` call** sits inside the same `try` as `locked_pair_update`. A destination refusal from it is therefore reported with "nothing was written.", which is true.
- **The signed-off wording wart is not tightened.** A plain pre-member-write Exception from the pair's initial recovery is still worded "the ledger write to … failed". The load-bearing line "nothing was written." is true.
- **Left as found (not in T-02's items):** the plan-merge.py docstring still says "Every mutating verb goes through harness_merge.locked_update". That was already inexact at base, where `write_plan_and_ledger` used `guards._replace_bytes`.
