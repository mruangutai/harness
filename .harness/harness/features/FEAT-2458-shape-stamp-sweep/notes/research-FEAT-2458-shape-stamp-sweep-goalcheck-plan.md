# Goal-check (plan) — FEAT-2458-shape-stamp-sweep — 2026-11-23

**BLUF: yes, the applied pending plan delivers the operator's stated intent.** Both declared
perspectives pass. On the fleet point, the plan departs from the grilling artifact's wording
(`_planning_segment`), but it delivers what that wording was for: FEAT-01-kaya-platform resolves
under `kaya`. Two additions go beyond the grilling, and the operator should see both at signature
(see "Departures").

Graded against `.harness/notes/grilling-shape-stamp-sweep-2026-11-23.md` (main checkout), with the
BRIEF and `plan.yaml` read at the worktree at b788e9da. The plan is pending.

## Per perspective

- **operator — PASS.** SC-03, SC-04 and SC-05 are carried by T-02 (B1–B7, tests C(1)–C(8)).
  - Finished features' stamps are deleted on `terminal` only (B4, C(4)). The plain stamp is never
    examined or deleted (B2, C(5), and C(1) for the dry run).
  - Live stamps are silent and kept (B6, C(6)). Unresolved stamps, absent ones included, are kept
    and named on exactly one line with the reason (B5, C(3), C(7), C(8)).
  - `--dry-run` is honoured (B4, C(1)–C(2)), and the step is called from `main()` beside the pin
    and node_modules steps (B1).
  - "Finished" rests on T-01's `classify_feature` → `_landed_classification`, the existing rule
    (Settled R1, R3).
  - Every grilling "Settled" line for the operator is covered. Every "Out of scope" line is kept:
    no deletion in `feature-worktree.py remove`, absent stamps are never auto-deleted (C(7)), and
    `check-domain.py` is untouched.
- **code maintainer — PASS.** SC-01, SC-02, SC-08, SC-09 and SC-10 are carried by T-01; SC-06,
  SC-07, SC-08, SC-09 and SC-10 by T-02.
  - There is one public predicate, `classify_feature`, on the existing landed rule. T-01's verify
    uses AST to assert it calls `_landed_classification`.
  - The hook decides from `klass` alone (B3, SC-06).
  - The duplicate `_repo_arg_for_segment` is deleted and its caller is repointed to
    `worktree_terminal.repo_arg_for_segment`. Its registry key and inventory row are retired (T-02
    A1–A4, SC-07).
  - The docstring names `classify_feature` and `repo_arg_for_segment` (T-01 step 3, SC-08).
  - Tests live in `test-worktree-terminal.py`, as R3 asks.

No perspective is unserved, and no task serves no SC.

## The fleet-lookup point (answered, not resolved)

**The operator's wording.** The grilling's "Facts I verified" says `classify_feature` "must use the
fleet planning-segment fallback that `_resolve_landed` applies (`_planning_segment` …), or a fleet
feature reads as absent".

**What the plan does.** Plan D-03 and T-01 steps 1c–1d forbid calling `_planning_segment`. Instead,
T-01 looks up the id in the harness features directory first. When it is not there, T-01 loops
over `_fleet_segments` and calls `_landed_dir_names` with an exact `in` test.

**Does it depart from the wording?** Yes. It names and calls a different function from the one the
grilling names.

- `_planning_segment` matches through `_match_landed_id`, the unique-prefix matcher. This is
  confirmed in `worktree_terminal.py#_planning_segment` at b788e9da.
- The plan's loop copies that function's segment walk, including skipping a segment that has no
  landed features directory. Only the matching predicate differs.

**Does it still deliver the intent?** Yes.

- The sentence's purpose clause is "or a fleet feature reads as absent". The exact walk still finds
  a fleet feature: SC-02, T-01 cases (g), (h) and (j).
- Exact identity also guards an operator ruling. Under prefix matching, a never-landed stamp would
  be deleted whenever a longer finished id exists. That would break the Out-of-scope rule "Absent
  means a human decides" (T-01 case (i), T-02 C(7)).
- **Measured on the real population** (main = b788e9da, in the main checkout's `.harness/`): every
  per-feature stamp gave the same match under exact identity as under prefix matching.
  FEAT-01-kaya-platform matches exactly under `kaya` only, with 0 prefix hits in
  `harness/features`. The absent set is BUG-2110, BUG-2451, FEAT-1559, FEAT-2081 and FEAT-2452,
  plus FEAT-2458 itself, which is new since the grilling.
- So D-03 changes no stamp's outcome today. It changes only the hypothetical prefix-collision case.

**The cost to note.** The plan adds a second, roughly 6-line copy of the segment walk inside
`worktree_terminal.py`, next to `_planning_segment`. It is not a second landed rule, so the code
maintainer's "no second copy of that rule … in the hook" still holds. It is still a parallel walk
that a future maintainer may try to merge back into the prefix matcher. D-03 records that rejected
alternative, which is the right place for it.

**At signature.** The operator should see D-03 as a choice that replaces their named mechanism. It
should not slip by as an implementation detail.

## Departures from the grilling (not grade-changing)

1. **T-01 step 2 adds scope the grilling did not name.** It catches `UnicodeDecodeError` in
   `_landed_blob_text`. This changes `classify` and `classify_all` (the INV-29 gate path) as well
   as `classify_feature`: an undecodable landed record becomes `unresolved` and no longer raises.
   It came from panel finding PF-dd345693…, it serves the operator's "nothing else is touched /
   the hook never aborts", and plan row DEC-252 `keep` covers it. Even so, it is a behaviour change
   to a gate-imported reader that the operator did not ask for.
2. **SC-01's exact-id clause and SC-02's prefix-collision clause** add the D-03 guarantees above.
   They are consistent with the intent.
3. **Panel record.** `panel.findings` still lists PF-9ad7c484… (high, the prefix match) and
   PF-dd345693… (med, undecodable records) as `disposition: open`. The applied plan text addresses
   both (D-03, T-01 step 2), but the open dispositions are for the panel re-run to settle. This
   goal-check does not close them.

## Open questions

- None block. The operator decides at signature whether D-03 (exact identity, replacing
  `_planning_segment`) and T-01 step 2 (the UTF-8 seam fix in the gate-shared reader) are accepted
  as scope.
