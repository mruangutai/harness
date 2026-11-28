# Research — FEAT-2516 plan revision, cycle 2 (run 2026-11-27-01-plan-product, draft step)

**BLUF.** I narrowed the plan to B-9 (#2524) under the operator's rulings of 2026-11-27. Tasks are
exactly T-03 and T-05, `source_issues: [2524]`, and `approval.status` stays pending. T-03 now
points at the `feature_record/` package that FEAT-2581 introduced. The planned `code_repository`
and `planning_root` move to `feature_record/binding.py`. `plan-merge.py check` exits 0 with 2
tasks, 14 anchors and 0 failures. The cycle-1 history of this note is in git
(`671f03a7:<this path>`).

## Removed and kept

- **Tasks.** I deleted T-01, T-02 and T-04 (`delete-items`). T-03 and T-05 remain.
- **Decisions.** I deleted D-01 (absent class, used only by T-01 and T-02) and D-03 (canonical-reader
  runner, used only by T-04). D-02, the fix receipt, stays.
- **SCs.**
  - SC-01 to SC-08 are gone: they covered the classifier, the sweep, the canonical-reader guard and
    the CI comment.
  - SC-09 stays, reduced to a regression check over T-03's surface: the canonical-reader audit,
    `canonical_reader_live_audit_is_zero`, and test-check-plan-routes, test-checker-structure-locks,
    test-validate-digest and test-check-state-table. I dropped test-worktree-terminal and
    test-post-merge-sweep.
  - SC-10 to SC-12 stay, re-pathed. SC-10 names `feature_record.evidence.run_evidence_problems`.
    In SC-12 the close-run synopsis now lives in `SKILL.md` step 6.
- **Perspectives.**
  - **operator**: removed. Only SC-04 to SC-06 served it.
  - **code maintainer**: reduced to the SC-09 promise.
  - **orchestrator**: kept as written.
- **Lane rows.**
  - Dropped `.github/workflows/**`, which only T-04 used.
  - Added `.claude/skills/harness/SKILL.md` for the synopsis retarget. check-domain resolves it to
    NOBODY.
  - Kept `bin/**`, `schemas/**`, `references/**`, `tests/**` and `.harness/harness/docs/**`, with
    their reasons rewritten for T-03 and T-05.
  - Re-resolved at 3e979ae3. team-config.yaml has not changed since 101779cc.
- **decisions_affected.**
  - Dropped DEC-180 and DEC-238, which only the stamp sweep needed.
  - Kept DEC-157 (amend, successor D-02), DEC-174, DEC-191, DEC-226, DEC-159, DEC-221, DEC-227 and
    DEC-230. I checked every clause as an exact substring of the current DECISIONS.md (a Python
    substring check over each row). Only DEC-174's reason was reworded.

## Where code_repository and planning_root live: feature_record/binding.py

- binding.py describes itself as owning "a feature's repository binding". It already holds
  `has_repository_binding`, which `_qa_code_repository` calls, and `_bound_mirror_binding`, which
  reads fleet.yaml through `artifact_accessors.load_fleet` the same way. evidence.py stays the
  evidence_ref protocol, and runs.py imports binding to resolve the commit.
- validate-digest.py, as it stands at 3e979ae3:
  - `_repo_root_for_feature` still has the same shape: realpath of four `..`.
  - It has three in-module callers, and test-validate-digest.py calls it as well, so it stays as a
    thin delegate to `record_binding.planning_root`.
  - `_qa_code_repository` has exactly one call site, in `_qa_policy`.
  - It returns `(planning_root, planning_root, None)` for an unbound feature. The moved body keeps
    that.
  - It used the module-global `artifact_accessors`, and imported `factory_config` and `binding`
    locally. In binding.py both become local imports, as in `_bound_mirror_binding`.
  - New in cycle 2: validate-digest gets a module-level
    `from feature_record import binding as record_binding` beside the existing `record_read`
    import. This is a cheap, reversible choice.
- **canonical-reader row.** The row `validate-digest.py::_qa_code_repository::load_fleet#1` still
  exists. Cycle 1's copy-source id, `feature_schema.py::_bound_mirror_binding::load_fleet#1`, no
  longer exists. It is now `feature_record/binding.py::_bound_mirror_binding::load_fleet#1`, with
  `dec174_category: none` and `execution_route: team`. The new row copies those fields, so its route
  changes from validator/main-session-direct to none/team: same-file rows classify alike, and
  `_route_finding` allows none/team. binding.py is already in `scanned_files`.

## Other re-checks against current code at 671f03a7

- **Still present.** `_is_refused`, `_close_run_options` and the close-run run-end stage argv are in
  runs.py. `_owed_regate` is in runs.py. `_judgements_of` is in judgements.py. `_not_before` and
  `DISTILL_RUN` are in spend.py. `code_grade.commit_oid` is unchanged, and budget.py's `_commit_id`
  shows the local-import precedent. `digest_record` is already a module import in runs.py and a
  local import in evidence.py.
- **Changed, so the intent changed.**
  - `_run_end_digest(args, entry, changed, runs)` has no `doc`. Intent B.4 threads `doc` through
    `_record_attribution` and `_attach_digest`.
  - `cycle_evidence` is written in `_attach_digest`, so B.5 puts the replay rule there.
  - `run_evidence_problems` now takes `feature_id`, and its source branch is in
    `_check_cycle_evidence`.
  - `_check_digest_record` gains `expected`. Cycle 1 said the receipt "replaces the equality check";
    the verdict and artifact check is now kept explicitly.
- **SKILL.md.** The rebase removed the close-run synopsis from ledger.md and pointed it at the
  playbook. It is in `.claude/skills/harness/SKILL.md` step 6, so T-03 now owns SKILL.md through a
  quoted anchor, and G.1 edits it there.
- **Probes I ran.**
  - `LEAD_DIGEST` with `VERDICT: FAIL` passes `validate-digest.py -- harness-eng-lead` (exit 0,
    `digest ok`).
  - The bound-feature fleet.yaml fixture loads and `workspace_path` gives `<ws>/product`.
  - Every existing SpendTest run is PASS, so the existing cases still go through the timestamp
    rule.

## Not touched (left for the scope re-read)

I carried PF-d0e16ad5 (receipt contract) and PF-3a8e31e4 (fleet commit resolution) to their new
homes unchanged. I left PF-590e7bb6 (strict cutoff) as it was. The panel findings on removed tasks
are for the apply step to mark moot.

## Check output

```
OK T-03 12 anchor(s) resolved
OK T-05 2 anchor(s) resolved
CHECK .../FEAT-2516-stamp-sweep-hardening/plan.yaml against .../FEAT-2516-stamp-sweep-hardening: 2 task(s), 14 anchor(s) resolved, 0 failure(s)
exit=0
```

`check-plan-routes.py <plan.yaml>`: 0 violations. It prints a TASK DEVIATION for T-05: the
DECISIONS files are granted to the documentor but declared main-session-direct, which is the
expected DEC-174 carve-out.

No task-changing call printed `APPROVAL-RESET:`, so I made no gh-sync call.

## Cycle-2 apply step (after the one scope re-read)

**BLUF.** I applied the reader's four must-fix remedies to T-03 and decisions_affected, recorded
the cycle-2 panel, and set the dispositions. `plan-merge.py check` exits 0 with 2 tasks, 14
anchors and 0 failures. **No reader has read any of these remedies.** They landed after the single
re-read (review-harness-code-reviewer-plan-c2.md), and operator ruling 3 allows no further panel.
The plan stays pending.

### Remedies applied (unread)

- **PF-d0e16ad5 (receipt contract).** Two changes:
  - B.3 now refuses, whatever flags are given, any `--verdict` other than FAIL on an entry whose
    cycle_evidence source is main-session-fix. A bare same-count run-end keeps the receipt in
    `_record_attribution` without entering `_attach_digest`, so the guard has to sit in
    `_record_run_end`.
  - A.2 `verify_fix_receipt` now requires the authenticated digest itself to carry `VERDICT: FAIL`
    and an `artifact` key, the same record shape `_check_digest_record` requires. INV-7 reaches it
    through C.
  - Tests in F.2: a bare `run-end --verdict PASS --cycles-used 1` after an accepted receipt is
    refused (stderr `stays FAIL`, bytes unchanged). A reader problem containing `VERDICT FAIL` is
    raised for a FAIL ledger with a receipt over a PASS digest.
- **PF-3a8e31e4 (fleet commit resolution).** B.4 adds `runs.py::_require_checkout_root`. It
  requires `git -C <code_root> rev-parse --show-toplevel` to realpath-equal `code_root` before
  `code_grade.commit_oid` runs.
  - I put it in runs.py, not binding.py, so that neither the validator nor check_state (which
    loads `feature_record.binding` via board.py) gains a git spawn.
  - Tests in F.2, each on a fresh pre-attribution record:
    - A plain `ws/product` directory nested under the planning repo, refused with
      `is not a git checkout root`.
    - A planning-only `fix_commit`, refused with `fix receipt names no commit in` and asserted NOT
      to contain `conflicts with the recorded receipt`.
- **PF-7265e1a2 (unsegmented layout).**
  - A.3's `code_repository(record, planning_root)` now takes the root from its caller.
  - The new `binding.feature_repository_root(feature_dir)` resolves both `FEATURE_JSON_TAIL`
    layouts: `REPO/.harness/features/FEAT` and `REPO/.harness/SEG/features/FEAT`.
  - validate-digest.py passes its own unchanged four-level `_repo_root_for_feature`. This reverts
    the cycle-2 draft's delegation to `planning_root`, so the validator's checkout contract is
    untouched.
  - Test in F.2: unsegmented acceptance on the base fixture's
    `self.tmp/.harness/features/FEAT-77-record`.
  - verify gains greps for `def feature_repository_root` and `def _require_checkout_root`.
- **PF-78bdb915 (DEC-256).** Added a decisions_affected `keep` row for DEC-256. The clause is the
  single-line exact substring from its QA review-pin exception D-01 bullet; I checked it with a
  count==1 substring check against the current DECISIONS.md.
- **D-02.** Its choice text now also says: the code repository must be its own checkout root, in
  either layout; a receipt-attributed run stays FAIL; INV-7 checks that the digest records FAIL.

### Calls (stdout captured in the run; abridged)

- `apply` (D-02.choice, T-03.intent, T-03.verify): `REPLACED` ×3, `APPLIED`, exit 0.
- `set-key decisions_affected`: `APPLIED`, exit 0.
- `record-panel --cycle 2`: CARRIED PF-d0e16ad5 and PF-3a8e31e4; ADDED PF-7265e1a2 and
  PF-78bdb915; exit 0.
- `set-panel`: `PANEL cycle 2`, `APPLIED`, exit 0.
- No call printed `APPROVAL-RESET:`, so I made no gh-sync call.
- `check`: `OK T-03 12 anchor(s)`, `OK T-05 2 anchor(s)`, 0 failures, exit 0.

The check-state lines after each write (BRIEF unapproved, INV-25/29 on a scratchpad worktree, INV-37
receipt) existed before this step and are not caused by it.

### Dispositions

**Resolved, resolved_by T-03:**

- PF-d0e16ad5, PF-3a8e31e4, PF-7265e1a2: remedied in this step, unread.
- PF-590e7bb6, PF-92bcdbb1: the re-read graded both closed.
- PF-6cf433c1: G.2 qualifies exact equality, G.1 adds the flags to the synopsis, and G.3 shows both
  command forms and the recommended-versus-required note name. The stamp-containment half is moot by
  ruling 1.

**Resolved, no task:**

- PF-94a4029f: DEC-159, DEC-221, DEC-227 and DEC-230 keep rows are present, and the re-read found
  them sound.
- PF-78bdb915: the plan-text row, unread.

**Open:** PF-4901fed0 (T-01), PF-f289edde (T-02), PF-980581d8 (D-03) and PF-06e545e7 (T-04). All
four are moot by ruling 1, not fixed.
