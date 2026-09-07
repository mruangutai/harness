# Receipt — T-01 — DEC-174 gate-evidence correction — harness-documentor — 2026-09-06-05-product

**PASS.** DEC-174's evidence sentence now states current truth; `DECISIONS-INDEX.md` regenerated
(anchor-only churn). T-01's `verify:` block ran verbatim and exited 0, all 14 index tests ok.
Two repo files changed, both named in T-01 `files:`. Nothing staged, committed or pushed.

## The exact final text of the rewritten sentence

`.harness/harness/docs/DECISIONS.md`, DEC-174, lines 4308-4317 (locate by `The evidence, all from
2026-08-03`), verbatim including markup and line breaks:

```markdown
**The evidence, all from 2026-08-03 and all on this repo.** `run-unit-tests.sh`, `check-docs.sh` and
`check-state.sh` were green, and the fourth gate recorded that day, `gen-decisions-index.py --check`,
was no gate at all: `--check` was never a supported mode. Before argv validation landed at commit
`ffbdbfa1` (2026-08-05, "perf(140): validate argv so `--help` stops rewriting the index"), `main()`
read `stdout_mode = "--stdout" in sys.argv[1:]`, so an unrecognized `--check` fell through to the
WRITE path: the run regenerated `DECISIONS-INDEX.md` in place and exited 0, and a regeneration
overwrites exactly the drift a check would have reported, so it could not prove index drift one way
or the other. The read-only form is
`gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`. Those three
real gates were green while:
```

The prior text (2 lines) claimed `Every gate was green — run-unit-tests.sh, check-docs.sh,
check-state.sh, gen-decisions-index.py --check — while:`. The sentence still ends `while:`, so the
three defect bullets read as its continuation; heading, bullets, the *Self-hosting caught none of
these* paragraph and the carve-out table are untouched. No dated sub-section, no `**Amendment` line,
no appended note (DEC-205; the amendment construct is also rejected mechanically).

## Verify — T-01's block, verbatim, observed output

`python3 .agents/skills/harness/bin/gen-decisions-index.py` → no output, exit 0. Then the block:

```
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_refs_graph_omits_ids_with_no_live_heading
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
ok - test_committed_index_matches_a_fresh_regeneration
ok - test_committed_index_is_complete_and_within_budget
ok - test_orphaned_ruling_is_reported_not_silently_dropped
ok - test_root_resolves_through_harness_boundary_not_the_retired_variable
ok - test_no_amendment_construct_survives_in_the_authority
ok - test_dec_210_entry_names_both_enforcement_points
ok - test_dec_210_entry_states_the_bash_write_route_for_plan_yaml
ok - test_dec_210_index_row_names_the_compatibility_host_in_the_ruling
EXIT=0
```

The stale-claim guard and all five `grep -qF` strings passed silently (the loop prints only on
failure); exit 0 is the pass signal for them.

## Tree state — observed

`git status --porcelain`:

```
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/features/BUG-148-gate-record-correction/feature.json
 M .harness/harness/features/BUG-148-gate-record-correction/plan.yaml
```

The two doc paths are mine; `feature.json` and `plan.yaml` are this feature's own run state, not
written by me. No `notes/` artifact other than this receipt; no historical artifact touched.

`git diff --numstat -- .harness/harness/docs/`: `42 42 DECISIONS-INDEX.md` and
`10 2 DECISIONS.md`. The `DECISIONS.md` diff is a single hunk,
`@@ -4305,8 +4305,16 @@`, 2 deletions / 10 insertions — every `+`/`-` line is inside DEC-174's
evidence paragraph, nothing else in the file moved.

Index churn is anchor-only, proved rather than asserted: normalising `@<line>` → `@N` in both the
committed and the regenerated index makes them byte-identical (`diff` empty). DEC-174's own
hand-written ruling after ` :: ` is unchanged; the 42 changed rows are later entries whose
source-line anchor shifted by +8.

## Open

None. T-02 (FEAT-05 `STATE.md`) restates the same mechanism in the same terms — the sentence quoted
above is the binding reference for it, and the T-02 verify's five strings differ only in the date
(`2026-09-06`).
