# Receipt — harness-backend-dev — FEAT-38 — T-12 audit (which task removed `strip_ruling_prose`) — run 2026-08-29-07-eng

Read-only audit. No source file touched.

## (a) Which task removed it

**T-06, committed at `204b469`** (`[harness:t-06,t-17] FEAT-38 build eng segment A: generator
supersession removal and the anchor-rot checker`). NOT T-12, and NOT uncommitted.

Evidence:
- `git log -S 'strip_ruling_prose' --oneline -- <file>` shows the string's last touch was
  `204b469`; `git show HEAD:<file> | grep strip_ruling_prose` finds nothing — i.e. the removal is
  already baked into HEAD, not sitting in the uncommitted working tree.
- `git diff -- <file>` (uncommitted half, currently T-10 cycle-1 + T-12's comment sweep) does not
  touch `strip_ruling_prose` at all — it isn't there to touch, it was gone before either task ran.
- `git show 204b469 -- <file>` quotes the exact hunk:
  ```
  -def strip_ruling_prose(s):
  -    """Drop all trailing '— SUPERSEDED BY DEC-N' clauses ... """
  -    ...
  -            stripped = strip_ruling_prose(ruling)
  +            non_ws = re.sub(r"\s+", "", ruling)
  ```
  a `def` deletion plus its one call site, alongside deletion of the two supersession regexes,
  `compute_supersession_target`, the `superseded_by` dict/loop, and the em-dash row suffix — the
  commit message calls this "T-06 deletes the supersession machinery ... the strip-before-cap
  step ... " explicitly. This is a documented, deliberate, whole-mechanism removal, not a
  comment-sweep slip.

T-12's own diff (the uncommitted half attributable to T-12, per its receipt) is disjoint from this
— T-12 never had the string to remove.

## (b) `ast.parse` result

`AST_PARSE_OK` — file parses cleanly.

## (c) Full suite census (verbatim)

```
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_refs_graph_omits_ids_with_no_live_heading
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
FAIL - test_committed_index_matches_a_fresh_regeneration: generator exited 1 — the committed index cannot be reproduced: ORPHAN: DEC-19 '...SUPERSEDED BY DEC-84 — SUPERSEDED BY DEC-85' has a ruling in the index but no live heading in .harness/harness/d...
FAIL - test_committed_index_is_complete_and_within_budget: 3 row(s) in .../DECISIONS-INDEX.md exceed the 30-word ruling cap — shorten the ruling after ' :: ' on each listed row: DEC-92 (36), DEC-102 (34), DEC-37 (33)
ok - test_orphaned_ruling_is_reported_not_silently_dropped
FAIL - test_root_resolves_through_harness_boundary_not_the_retired_variable (a): a markerless HARNESS_PROJECT_DIR override exited 1: harness_boundary: discarding HARNESS_PROJECT_DIR=... it does not carry .harness/team-config.yaml. Falling back to the derived root ...
ok - test_no_amendment_construct_survives_in_the_authority
```

Exit code 1 (expected — the suite runner exits nonzero on any FAIL).

Exactly the three expected FAILs by name — `test_committed_index_matches_a_fresh_regeneration`,
`test_committed_index_is_complete_and_within_budget`,
`test_root_resolves_through_harness_boundary_not_the_retired_variable` — no fourth FAIL, no
NameError/AttributeError, no abort.

## (d) Is the property `strip_ruling_prose` served still pinned?

Two distinct things `strip_ruling_prose` stripped, and they diverged:

1. **Trailing `— SUPERSEDED BY DEC-N` clauses.** This property is *not* pinned by anything now —
   but nothing needs to pin it. The same commit (`204b469`) that deleted `strip_ruling_prose`
   also deleted the *only* thing that ever produced that clause: the supersession machinery
   (`compute_supersession_target`, the `superseded_by` dict/loop, the em-dash row suffix). A
   freshly-generated row can no longer carry a SUPERSEDED clause, so there is nothing left for
   the budget-cap test to strip before counting words. The 3 rows currently over-cap
   (DEC-92/102/37) are exactly the ones the commit message predicts as red-by-construction until
   T-11 regenerates `DECISIONS-INDEX.md` — that's `test_committed_index_is_complete_and_within_budget`,
   already accounted for above. Deletion is coherent: the appender and the stripper went together.

2. **Trailing `<!-- ok-stale -->` markers.** This property survives, pinned by a *different*
   mechanism than `strip_ruling_prose` ever was: the generator itself strips the inline
   `ok-stale` marker before writing a regenerated row (not via this test file's helper), and that
   is asserted end-to-end by `test_strips_inline_ok_stale_marker_on_a_row` (still `ok` above,
   confirmed present at line 246 of the current file, unmodified by 204b469's diff for this
   assertion's body/logic).

No hole. No property was silently dropped by the removal — verified by the fact that the sole
producer of the one property that lost its stripper was deleted in the same hunk, and the second
property retained its own independent guard.

## Verdict basis

Removal accounted for (T-06, `204b469`, committed, documented) + suite shows exactly the three
expected FAILs + no property lost → PASS.
