# Fix c2 — FEAT-1559 (validate c2 FAIL at 42856abb) — main-session-direct (DEC-174)

The lead's digest is in `runs/validate-c1-validator/digest.md`. It confirmed that all six
cycle-1 must-fixes are closed, and raised one new must-fix: high, substance, SC-04, citing T-01
and T-03.

## The finding

`feature_corpus.population` kept two id-keyed maps: this checkout's own entries
(`_local_entries`) and the landed records merged over them. Two segments may hold the same
feature id, as #2077's fixture does, and in that case one directory overwrote the other in the
map, so a gate never saw it. Two consumers were affected:

- `board_lifecycle._feature_dirs` dropped one feature from the board audit;
- `merge-gate.feature_for` counted one owner where there were two, so the multiple-owner deny
  could not fire.

## Fix

- Entries are keyed by `_directory_key(entry) = (segment, id)` in both maps. This checkout's copy
  replaces a landed entry only when segment and id both match.
- `population` sorts by id, then segment; the order among distinct ids is unchanged.
- The return shape and every caller are unchanged:
  - `board_lifecycle` and `validate-feature-json` read `path`;
  - `merge-gate` iterates entries;
  - `branch-create-gate` tests id membership.

## Tests, in `tests/integration/test-feature-corpus.py`

- **`SegmentIdentity.test_a_shared_id_is_two_entries_from_a_worktree_and_from_a_clone`.** Run
  from both a sparse worktree and a full clone: `harness/FEAT-2-beta` and `kaya/FEAT-2-beta` are
  both present, no key repeats, and there are 5 entries in total.
- **`SegmentIdentity.test_this_checkouts_copy_replaces_only_its_own_directory`.** The active
  directory resolves to the worktree path; both FEAT-2-beta directories resolve to owner paths.
- **`MergeGate.test_one_id_claimed_from_two_segments_is_two_owners_and_denies`.** The gate
  denies with "claimed by more than one feature record (FEAT-2-beta, FEAT-2-beta)".
- **`BoardStatus.test_one_id_active_in_two_segments_is_audited_in_both`.** Cards #501
  (harness) and #601 (kaya) are both compared against the plan.

**Red.** With `feature_corpus.py` at 42856abb and these tests in place, all four fail (3 FAIL,
1 ERROR: a `KeyError` for the dropped kaya entry). All four pass with the fix.

## Not changed, with reason

`check_state/ctx.py` `population()` excludes a landed record whose id equals the active
feature's. That exclusion is unreachable for a different-segment directory: before the context
is built, the check-state preflight refuses a record-bearing linked checkout whose active id is
claimed by more than one segment (`active_paths`: "the active record's segment is ambiguous").
The rest of the context (`feat_dirs`) is id-keyed on `main`, before this feature, so it is
outside this fix.

## Verification

- `code-grade.py` on the touched functions: `population` 4, `_local_entries` 5,
  `_directory_key` 5.
- Canonical-reader audit: clean.
- Both suites and check-state: results are in STATE.md and the commit that records this
  receipt.
