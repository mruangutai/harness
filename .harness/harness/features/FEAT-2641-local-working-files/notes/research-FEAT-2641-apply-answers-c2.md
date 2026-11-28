# FEAT-2641 plan c2 — operator rulings applied (apply-answers)

**BLUF.** Every ruling in `notes/answers-plan-product.md` is now in plan.yaml and BRIEF.md. Cleanup
on `rejected` lives inside `plan-merge.py set-feature-station` (new T-10). The new verb
`gh-sync.py skip-distill` (D-11, built in T-05, with the judgement kind `distill` added in T-04)
records a declined distill and then cleans. The five undistilled features are declined with no
preservation step, and each decline is recorded post-merge (D-12, T-09 step 5).
`plan-merge.py check` exited 0 (10 tasks, 62 anchors, 0 failures). No verb printed
`APPROVAL-RESET:`, so no gh-sync call was made. plan.yaml `approval.status: pending` and BRIEF
`## Approval status: pending` are untouched.

## Which `set-feature-station`, and where skip-distill lives

- `set-feature-station` is the plan-merge.py verb (`plan_merge/stations.py cmd_set_feature_station`). It is
  the only implementation: `gh-sync.py _record_station` calls it as a subprocess, and `reject-path.md`
  step 4 tells the caller of the none path to run it. Cleaning inside it after `_locked_plan_update`
  returns covers both reject paths at the one point where the station is known to have landed. A
  refusal (exit 4, 5 or 9, or a lock refusal) exits before cleanup. Exit 10 is new and means
  "station landed, cleanup failed" (codes 2/3/4/5/7/8/9 are taken). The owner root is resolved
  only when `project_notes` is non-empty, so non-git fixtures still pass.
- skip-distill is in gh-sync.py (T-05), and its rejected alternatives are recorded in D-11. Three
  reasons. (1) gh-sync already hosts the terminal verbs, the `--yes` preview, the landed-record
  worktree refusal and the local commit `_commit_terminal_station`. (2) T-05 already depends on
  T-03 and T-04, so the schema enum needs no new ordering; putting the verb in feature-worktree.py
  would have made T-03 and T-04 depend on each other. (3) It cleans by running `feature-worktree.py
  clean --yes`, the same routine and deletion-copy resolution. The record is a `feature.json`
  judgement of the new kind `distill` with decision `declined`, written through
  `feature-record.py judgement`.
- OQ-02's declines run **after the merge** in the owner checkout (D-12, T-09 step 5). The feature
  worktree is sparse: it holds only its own feature directory (`git sparse-checkout list`), and
  FEAT-1559 forbids writing other features from it. D-10 already places this feature's own
  post-merge acts on main's new code. This leaves a gap, disclosed in BRIEF `## Verification gaps`:
  no SC grades the five declines at the pin.

## Traceability — answer → ids

|Answer|Carried by|
|---|---|
|GC-01|D-05 (choice and because rewritten), D-11 (new), T-10 (new), T-03, T-04, T-05, T-07, T-08, T-09; SC-06, SC-16, SC-17 changed, SC-18 new; decisions_affected: DEC-230 reject row reason, DEC-238 "Abandon prunes" row reason, DEC-230 "The seven kinds are exhaustive" row (new)|
|OQ-02|D-12 (new), D-10 (choice now names the D-12 declines), T-09 step 5, T-08 (DEC-260 body names them); BRIEF Constraints disclosure, Out of scope, Verification gaps. No preservation or snapshot step anywhere|
|OQ-01|D-07 kept; its `because` records the departure from the grilling; BRIEF Constraints has a new "Departure from the grilling" bullet|
|OQ-03|T-07 (checkout-upgrade.md bullet gains the in-flight-branch repair; verify greps `rm -r --cached --sparse`), SC-16, BRIEF Constraints disclosure|
|OQ-04|No plan step recorded this feature's notes (only T-07's general playbook rule). BRIEF Out of scope now names both notes as unclaimed; T-09 step 5 forbids claiming them|
|OQ-05|nothing to apply|
|ORCH-01|nothing to apply (no ruling)|
|LEAD-01|nothing to apply in the plan. The lead's re-read set is T-03, T-05, T-06, T-07 and T-09, plus T-10, T-04 and T-08, which the rulings also changed|

## Every id added or changed

- **Tasks:**
  - Added: T-10.
  - Changed: T-03 (intent), T-04 (intent, traces, files, verify), T-05 (title, intent, traces,
    depends_on, files, verify), T-07 (intent, verify, depends_on), T-08 (intent, depends_on) and
    T-09 (intent, depends_on).
  - Unchanged: T-01, T-02, T-06.
- **SCs:**
  - Added: SC-18.
  - Changed: SC-06, SC-16, SC-17.
  - Also changed in BRIEF: the operator perspective line ("the decline itself is on the record").
- **Decisions:**
  - Added: D-11, D-12.
  - Changed: D-05, D-07, D-10.
- **decisions_affected:**
  - Added: DEC-230 amend "The seven kinds are exhaustive" (successor D-11).
  - Changed reasons: DEC-230 "`rejected` last on the numeric-successor path." and DEC-238
    "**Abandon prunes.**".

## Residual caller-run text, checked by grep

None for reject or declined distill. Remaining `feature-worktree.py clean` mentions are:

- the retry after a failed cleanup;
- the distill that changed no Expertise (not covered by the ruling);
- the rejected alternative in D-05 `because`.

