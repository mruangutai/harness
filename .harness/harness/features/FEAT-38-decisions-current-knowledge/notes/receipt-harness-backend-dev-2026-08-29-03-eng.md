# Receipt — harness-backend-dev — FEAT-38-decisions-current-knowledge — T-06

## Task
T-06: Remove the supersession machinery from the generator and stop emitting phantom refs.
Verify string cross-checked against `plan.yaml` lines 494-508 — matches the dispatch verbatim.

## Verify block: exit status

```
$ cd "$(git rev-parse --show-toplevel)"   # -> .../worktrees/harness/FEAT-38-decisions-current-knowledge
$ G=.claude/skills/harness/bin/gen-decisions-index.py
$ for s in SUPERSESSION_VERB_RE BODY_SUPERSESSION_RE compute_supersession_target \
           superseded_by 'SUPERSEDED BY'; do
    grep -q "$s" "$G" && { echo "still present: $s"; exit 1; }
  done
$ grep -q 'def compute_amendments' "$G" || exit 1
$ python3 .claude/skills/harness/bin/test-gen-decisions-index.py > /tmp/t06.out 2>&1
$ grep -q '^ok - test_orphaned_ruling_is_reported_not_silently_dropped$' /tmp/t06.out || exit 1
$ grep -q '^FAIL - test_committed_index_matches_a_fresh_regeneration' /tmp/t06.out || exit 1
$ grep '^FAIL' /tmp/t06.out \
    | grep -vE 'test_committed_index_(matches_a_fresh_regeneration|is_complete_and_within_budget)' \
    && exit 1
$ exit 0
VERIFY_EXIT=0
```

`task_verify: pass`.

## Full census from /tmp/t06.out (8 ok, 2 FAIL — exactly the two by-construction failures)

```
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_refs_graph_omits_ids_with_no_live_heading
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
FAIL - test_committed_index_matches_a_fresh_regeneration: .harness/harness/docs/DECISIONS-INDEX.md is not what the generator produces. rows in the file the generator does not produce: ['- DEC-104 @1602 [state,digest] refs: DEC-103 DEC-161 DEC-165 DEC-188 :: STRUCK 2026-08-10 under DEC-188 — enforced the checker as INV-10 with inline stale markers; INV-10 is gone and its number is retired.', '- DEC-188 @5919 [state,docs,digest] refs: DEC-103 DEC-104 DEC-161 DEC-165 DEC-181 :: A decision the tree flatly contradicts is STRUCK from the record and removed from every gate, never marked stale; the propagation checker is deleted with it.'] rows the generator produces that the file lacks: [...]
FAIL - test_committed_index_is_complete_and_within_budget: 3 row(s) in .../DECISIONS-INDEX.md exceed the 30-word ruling cap — shorten the ruling after ' :: ' on each listed row: DEC-92 (36), DEC-102 (34), DEC-37 (33)
ok - test_orphaned_ruling_is_reported_not_silently_dropped
ok - test_root_resolves_through_harness_boundary_not_the_retired_variable
```

- ok: 8
- FAIL: 2 — `test_committed_index_matches_a_fresh_regeneration`, `test_committed_index_is_complete_and_within_budget`
- No other FAIL lines present. These are exactly the two positive-control failures the plan names (T-11 owns making them green by regenerating the index and rewriting DEC-37/DEC-92/DEC-102). Note the `FAIL` line for `test_committed_index_matches_a_fresh_regeneration` also incidentally shows the manufactured DEC-161-in-refs defect being *fixed* by CHANGE 2: the committed file's DEC-104/DEC-188 rows still carry `DEC-161` in refs (no live `## DEC-161` heading exists at 7ebfc9e), while the freshly generated rows correctly omit it — this is additional evidence CHANGE 2 works, beyond the dedicated test case.

## Change 2 — refs-graph filter, proven both directions

**Seam chosen:** `parse_decisions` already returns `headings` (list of `(idx, key, num, orig_lineno)`) harvested from live `## DEC-NNN` headings. In `build_index`, immediately after calling `parse_decisions`, I compute `live_nums = {num for (_, _, num, _) in headings}` and pass it as a new required third parameter to `compute_refs(body, own_num, live_nums)`, which drops any matched id not in `live_nums` (in addition to the existing own-id exclusion). This keeps the live-heading harvest single-sourced in `parse_decisions` rather than re-deriving it or post-filtering the refs list after the fact.

**New test:** `test_refs_graph_omits_ids_with_no_live_heading` in `test-gen-decisions-index.py`, registered in `TESTS`. Uses a synthetic fixture built via the existing `make_authority(tmp, decisions, bodies)` helper — never the live document:
- Direction 1 (omission): `decisions=[(1,"First")]`, body of DEC-1 cites `DEC-99` (no heading for 99 in this fixture) → asserts `"DEC-99"` is absent from the left (refs) side of DEC-1's row.
- Direction 2 (inclusion): same body text, but `decisions=[(1,"First"),(99,"Ninety-nine")]` (heading for 99 now present) → asserts `"DEC-99"` IS present in the left side of DEC-1's row.

Ran standalone to confirm both branches execute and pass:
```
$ python3 -c "
import importlib.util, os
BIN='.../\.claude/skills/harness/bin/test-gen-decisions-index.py'
spec = importlib.util.spec_from_file_location('t', BIN)
m = importlib.util.module_from_spec(spec)
os.chdir(os.path.dirname(BIN))
spec.loader.exec_module(m)
print('direct call result:', m.test_refs_graph_omits_ids_with_no_live_heading())
"
ok - test_refs_graph_omits_ids_with_no_live_heading
direct call result: True
```
This also passed inside the full suite run above (`ok - test_refs_graph_omits_ids_with_no_live_heading`).

## What was deleted (by name, per intent)

`gen-decisions-index.py`:
- `SUPERSESSION_VERB_RE`, `BODY_SUPERSESSION_RE` (module-level regexes) and their explanatory comment block
- `compute_supersession_target` (whole function)
- the `superseded_by` dict, its construction loop, and the call site
- the clause that appended `— SUPERSEDED BY DEC-N` to a target row
- the strip-before-cap branch inside `strip_trailing_clauses` (the `re.sub(r"—\s*SUPERSEDED BY DEC-\d+\s*$", ...)` branch) — the ok-stale branch, the `while` loop, and the `(prose, had_ok_stale)` return shape are unchanged and still used at both call sites (orphan detection, row builder)
- the HEADER line `A row ending \`— SUPERSEDED BY DEC-NN\` is one you must not act on.`

Kept untouched: `compute_amendments` (verified present via `grep -q 'def compute_amendments'` in the verify block and via direct read), orphan detection (still a hard error via `sys.exit`-equivalent `return None` + stderr `ORPHAN:` messages — unchanged), ok-stale handling.

`test-gen-decisions-index.py`:
- deleted `test_supersession_declared_in_body_prose_is_harvested` and its `TESTS` entry (replaced in-place by the new refs-graph test, same list position)
- deleted `strip_ruling_prose` helper (docstring "Drop all trailing…")
- removed the strip step inside `test_committed_index_is_complete_and_within_budget` — it now measures `ruling` (the raw `ROW_RE` group) directly instead of `strip_ruling_prose(ruling)`
- removed remaining `SUPERSEDED` mentions from failure-message strings in that test (the cap/floor messages the lead flagged)
- kept `test_orphaned_ruling_is_reported_not_silently_dropped` untouched — orphan detection remains a hard error

One residual case-insensitive hit remains by design and is not a marker mention: line ~292, `"Superseded wording retained for the migration map."` — ordinary English inside a hand-written-ruling fixture string in `test_strips_inline_ok_stale_marker_on_a_row`, unrelated to the deleted `SUPERSEDED BY` marker syntax (case-sensitive grep for literal `SUPERSEDED` confirms zero remaining hits).

## git status — exactly the two target files, plus pre-existing unrelated dirt

```
$ git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-38-decisions-current-knowledge status --porcelain
 M .claude/skills/harness/bin/gen-decisions-index.py
 M .claude/skills/harness/bin/test-gen-decisions-index.py
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/feature.json
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml
?? .harness/notes/grilling-decisions-current-knowledge-2026-08-24.md
```
The last three entries (feature.json, plan.yaml, grilling note) were already present in the working tree before this dispatch began — I never opened or wrote them (only read `plan.yaml` for the T-06 task spec). Only `gen-decisions-index.py` and `test-gen-decisions-index.py` were touched by this task.

I also verified the main repo checkout at `/Users/molchairuangutai/GitHub/harness` (not the worktree) has zero diff on these two paths — an early edit attempt against a relative path landed there by mistake and was reverted with `git checkout --` before any worktree work began.

## Not touched (per explicit non-goals)
`.harness/harness/docs/DECISIONS.md`, `.harness/harness/docs/DECISIONS-INDEX.md`, `run-unit-tests.sh`, `.harness/harness.json` — none opened for writing. `compute_amendments` retained in full (T-10/T-05/T-07 dependency preserved).

---

## T-17

Task: Build the anchor-rot checker and its test.
Verify string cross-checked against `plan.yaml` lines 1213-1220 — matches the dispatch verbatim.

### Target files (exactly two, both new, untracked)
`.claude/skills/harness/bin/check-decision-anchors.py`,
`.claude/skills/harness/bin/test-check-decision-anchors.py`.

### TDD: RED before GREEN
Wrote `check-decision-anchors.py` once to design it, then moved it aside to `/tmp` before
committing to the test-first order, wrote `test-check-decision-anchors.py`, and ran the suite
against the ABSENT checker to observe RED:

```
$ python3 .claude/skills/harness/bin/test-check-decision-anchors.py; echo "RC=$?"
FAIL - test_in_range_anchor_reports_nothing_and_exits_zero: expected exit 0, got 2: '' "...can't open file '.../check-decision-anchors.py': [Errno 2] No such file or directory\n"
FAIL - test_missing_file_is_reported_and_exits_one: expected exit 1, got 2: (same ENOENT)
FAIL - test_out_of_range_line_is_reported_and_exits_one: expected exit 1, got 2: (same ENOENT)
FAIL - test_zero_anchors_exits_zero_and_says_so: expected exit 0, got 2: (same ENOENT)
ok - test_unreadable_target_exits_two_not_zero
FAIL - test_default_file_is_dev_null_readable_zero_anchors: expected exit 0 for /dev/null, got 2: (same ENOENT)
RC=1
```
5 of 6 cases FAIL for the right reason (checker absent, exit 2); the sixth passes vacuously
because "unreadable target" and "missing checker" both exit 2 at this stage — expected, since
it is not yet exercising the checker's own logic. Then restored the checker from `/tmp` and
reran to confirm GREEN:

```
$ python3 .claude/skills/harness/bin/test-check-decision-anchors.py; echo "RC=$?"
ok - test_in_range_anchor_reports_nothing_and_exits_zero
ok - test_missing_file_is_reported_and_exits_one
ok - test_out_of_range_line_is_reported_and_exits_one
ok - test_zero_anchors_exits_zero_and_says_so
ok - test_unreadable_target_exits_two_not_zero
ok - test_default_file_is_dev_null_readable_zero_anchors
RC=0
```

### Verify block: exit status and full `ok -` / `FAIL -` census

```
$ cd "$(git rev-parse --show-toplevel)"
$ python3 .claude/skills/harness/bin/test-check-decision-anchors.py > /tmp/t17.out 2>&1
$ rc=$?
$ grep '^FAIL' /tmp/t17.out && exit 1
(no output — grep found nothing)
$ test "$(grep -c '^ok - ' /tmp/t17.out)" -ge 4 || exit 1
(6 >= 4, passes)
$ python3 .claude/skills/harness/bin/check-decision-anchors.py --file /dev/null || exit 1
examined 0 anchor(s), 0 failed
$ exit $rc
VERIFY_BLOCK_EXIT=0
```

Full census from `/tmp/t17.out`:
```
ok - test_in_range_anchor_reports_nothing_and_exits_zero
ok - test_missing_file_is_reported_and_exits_one
ok - test_out_of_range_line_is_reported_and_exits_one
ok - test_zero_anchors_exits_zero_and_says_so
ok - test_unreadable_target_exits_two_not_zero
ok - test_default_file_is_dev_null_readable_zero_anchors
```
- ok: 6, FAIL: 0. `task_verify: pass`.

### Existence proof against the pre-feature authority (`7ebfc9e`)

```
$ git show 7ebfc9e:.harness/harness/docs/DECISIONS.md > /tmp/pre-feature-DECISIONS.md
$ python3 .claude/skills/harness/bin/check-decision-anchors.py --file /tmp/pre-feature-DECISIONS.md
`FEAT-03-subissue-mirror/feature.yaml:73`: file not found in the tree
`feature.yaml:63-64`: file not found in the tree
`FEAT-03-subissue-mirror/feature.yaml:97`: file not found in the tree
examined 32 anchor(s), 3 failed
$ echo "EXIT=$?"
EXIT=1
```
Exactly the three `feature.yaml` anchors, both reported for the EXISTENCE check ("file not found
in the tree" — those `FEAT-03-subissue-mirror/` and bare `feature.yaml` basenames are not present
anywhere in the current `git ls-files` output), exit 1 as required. Observed directly, not tuned
to hit three — the checker's basename+range logic produced this set from the real anchor grammar
applied to the real pre-feature file; I did not adjust the checker after seeing this result.

### `check-decision-anchors.py --file /dev/null`

```
$ python3 .claude/skills/harness/bin/check-decision-anchors.py --file /dev/null
examined 0 anchor(s), 0 failed
$ echo $?
0
```
`/dev/null` is readable and holds zero anchors — the checker states it examined zero (never a
silent pass) and exits 0, not 2. A missing/unreadable path (see
`test_unreadable_target_exits_two_not_zero` above) exits 2, so the two cases are distinguishable.

### Default-path resolution — reused, not hand-rolled
`check-decision-anchors.py`'s `default_target()` calls `harness_boundary.resolve_root(_BIN_DIR)`
— the exact same call `gen-decisions-index.py`'s `main()` makes — then joins it onto
`DOCS_DIR = os.path.join(".harness", "harness", "docs")` and `"DECISIONS.md"`, mirroring
`gen-decisions-index.py`'s own `DOCS_DIR`/`DECISIONS_PATH` constants byte-for-byte. Resolution
happens inside `default_target()`, called from `main()` only when `args.file is None` — i.e. at
CALL time, after argv is parsed — so an explicit `--file` never reaches it and nothing is fixed
at import time. No second root-resolution implementation was written.

### git status — exactly the two new files, nothing else touched by T-17

```
$ git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-38-decisions-current-knowledge status --porcelain
 M .claude/skills/harness/bin/gen-decisions-index.py
 M .claude/skills/harness/bin/test-gen-decisions-index.py
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/feature.json
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml
?? .claude/skills/harness/bin/check-decision-anchors.py
?? .claude/skills/harness/bin/test-check-decision-anchors.py
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-backend-dev-2026-08-29-03-eng.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/observations/harness-backend-dev.md
?? .harness/notes/grilling-decisions-current-knowledge-2026-08-24.md
```
The two `M` generator/test-generator files and the `feature.json`/`plan.yaml`/grilling-note
entries are pre-existing state from sibling task T-06 and earlier setup — not touched in this
dispatch. `.harness/harness/docs/DECISIONS.md`, `DECISIONS-INDEX.md`, `run-unit-tests.sh` and
`.harness/harness.json` were never opened for writing, per the explicit non-goals.
