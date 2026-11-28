# FEAT-2641 plan c2 — panel cycle 2 applied (pm, apply)

**BLUF.** All five substance findings were checked against the source and all five premises held.
Each remedy is now in plan.yaml through `plan-merge.py amend`, `set-key` or `set-panel`, and in
BRIEF SC-08, SC-17 and SC-18. No reader has read any of these changes yet. The form finding (task
order) stays open because plan-merge has no verb that reorders tasks.

- `record-panel --cycle 2` exited 0. `check` exited 0 both before and after the dispositions (10
  tasks, 62 anchors, 0 failures).
- No verb printed `APPROVAL-RESET:`, so `gh-sync.py status` was not run.
- `approval.status` is still `pending`, and BRIEF `## Approval` is still `pending`.
- Captured verb stdout is in `/tmp/feat2641-c2/amend-stdout.log`. The driver script is
  `/tmp/feat2641-c2/apply.py`; it asserted each replaced passage verbatim, exactly once.

## Premises verified at source (control-plane checkout, HEAD 68a332c2)

1. `gh-sync.py main()` calls `load_config(root, feat_dir, cmd)` before any command is dispatched.
   `_sync_off` calls `skip()` (exit 0) unless the command is a local `status`, and `_require_gh`
   skips when `gh` is unauthenticated or cannot launch. A skip-distill added only as a dispatch arm
   would therefore exit 0 having done nothing. **Holds.**
2. `_commit_terminal_station` commits `plan.yaml` and `feature.json` together. Its docstring says
   it is "LOUD BUT NEVER FATAL": on a failed commit it prints a WARNING and returns. **Holds.**
3. Three facts:
   - `dest_for` uses the `--id` verbatim.
   - `_artifact_id` maps a short id to its slugged feature directory only inside one features
     directory, and `test-feature-worktree.py case_short_id_resolves_to_the_flow_directory`
     covers the `FEAT-72` worktree holding `FEAT-72-a-slugged-name`.
   - `harness_boundary.resolve_root(bin_dir, strict=True)` requires `bin_dir`. It returns the root
     of the script's own checkout, which for a linked worktree is not the owner.

   Since `clean_argv` passes the full basename, a short-id worktree is never found. **Holds.**
4. `merge-gate.py distill_main` catches `(DistillRefusal, feature_corpus.CorpusError)` as `REFUSED
   ... return 3`. A `CorpusError` raised by `owner_root` after the merge would therefore report a
   landed merge as refused. **Holds.**
5. These `decisions_affected` reasons were wrong, as the finding said:
   - The DEC-253 row read "Only the reconstructed Expertise is committed".
   - The DEC-238 "ship keeps ..." row read "every terminal path removes", which includes ship.
   - D-05 `because` also said "every terminal path". **Holds**, and the D-05 wording was fixed in
     the same pass (G-13).

## Per finding

|Finding|Disposition|Changed|
|---|---|---|
|PF-171caabf… high: skip-distill can silently SKIP|resolved_by T-05|T-05 step 7 dispatches before `load_config` and never prints SKIP, with tests for sync off and no `gh`. T-09 step 5 confirms each decline from git (log subject, clean status) and the ledger (exactly one judgement). D-11 and D-12 choice. BRIEF SC-18|
|PF-294f4395… high: failed decline commit permits cleanup|resolved_by T-05|T-05 (d)/(e)/(f): `_commit_terminal_station` gains `paths`/`message` parameters and a bool return, and ship's behaviour is unchanged. skip-distill commits `feature.json` alone, and a failed commit exits 1 with nothing removed. A re-run commits the recorded decline without a second judgement. A `feature.json` already dirty before the decline is refused. New tests: hook refusal, then retry; dirty `plan.yaml` left out of the commit. D-11 and D-05 choice. BRIEF SC-18|
|PF-05ce8bbd… high: clean reaches the wrong checkout|resolved_by T-03|T-03 2(b): owner = `feature_corpus.owner_root(...)`, never a bare `resolve_root`. The worktree copy is chosen among the owner's linked worktrees, matching the short or full id either way round; two matches exit 5. New CLI cases: full id, short id, run with `HARNESS_PROJECT_DIR` naming the linked worktree, ambiguity, and remove after clean. T-05 tests: skip-distill and the printed retry command against a short-id retained worktree. D-05 choice. BRIEF SC-08 and SC-18|
|PF-85f4dfb7… med: post-merge lookup failure reported as refusal|resolved_by T-06|T-06 step 2: `_clean_after_merge` catches errors from the lookups and the clean alike. Its result adds `cleanup_retry`, with a `<repo>` placeholder when the directory did not resolve, and the message says "do not re-run merge-distill". Step 6 has two new fault cases asserting exit 4 and never REFUSED. BRIEF SC-17|
|PF-cdd37b93… med: two amendment reasons direct obsolete behaviour|resolved_by T-08|`decisions_affected` reasons for DEC-253 ("reconstruction with original receipts …") and DEC-238 ("ship keeps the passing validate runs …"), written by `set-key`. T-08 step 3 guidance for DEC-238 and DEC-253. D-05 `because`. DEC-257's strike and the DEC-230 rows are untouched|
|PF-527a9700… low form: task list not topological|**open**, not remedied|plan-merge has no reorder verb: `apply` keeps base order and appends new ids, and `set-key` refuses `tasks`. Deleting and re-adding T-05 to T-09 would re-serialise five tasks just to change their order. The scheduler reads `depends_on` only (teams/build.yaml `from_task_depends_on`), and the graph is acyclic (the reviewer confirmed this), so list order carries no meaning|

**Adjacent change, one boundary past PF-85f4.** T-05's `_clean_after_terminal` used to receive
`owner_root` from its callers, and `feature_corpus.owner_root` could raise after the abandon
station had landed. It now resolves the owner root inside its own try and catches `CorpusError`,
with a new unit case. T-10 already caught `CorpusError`.

**T-07 unchanged, though PF-05ce names it.** Its documented `clean --repo <repo> --id <FEAT>
--yes` now works for both spellings, so no text in T-07 directs the broken behaviour.

## Text changed in this step (after the c2 reader saw it)

- **Tasks:** T-03 intent, T-05 intent, T-06 intent, T-08 intent and T-09 intent.
- **Decisions:** D-05 choice and because, D-11 choice, D-12 choice.
- **decisions_affected:** DEC-253 "reconstruction with original receipts before merge…" reason;
  DEC-238 "ship keeps the passing validate runs, abandon keeps nothing" reason.
- **BRIEF:** SC-08, SC-17 and SC-18.
- **Panel:** recorded at cycle 2, with five findings resolved and PF-527a and PF-9bc6 open.
- **Goal-check note:** departures A and B only.

## Open

- PM-C2-01: the five declines are recorded post-merge and are not graded at the pin. They are now
  confirmed per feature at landing (T-09 step 5).
- PM-C2-02: cleanup after a distill that applied no Expertise op stays a `clean` step.
