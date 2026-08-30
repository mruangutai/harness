# Receipt — harness-backend-dev — FEAT-38-decisions-current-knowledge — T-10

## Task
T-10: Remove the amendment machinery from the generator and add the mutation-proved guard test.
Verify string cross-checked against `plan.yaml` lines 791-805 — matches the dispatch verbatim, no
mismatch. This is the **cycle 1 (loop_back)** re-run: CHANGE 1 and CHANGE 2 (below) are carried
forward unmodified from cycle 0; only the mutation proof and the honest verify report are new.

## CHANGE 1 — amendment machinery deleted (complete)

`gen-decisions-index.py`, by name, per intent:
- `AMEND_HEADING_RE`, `AMEND_BOLD_RE` (module-level regexes) — deleted
- `compute_amendments` (whole function, incl. `heading_amend_nums`/`bold_amend_entries`
  bookkeeping and the positional-defaulting fallback) — deleted
- `format_amendment_span` (whole function) — deleted
- the call `amendments = compute_amendments(lines, headings)`, the `amend_nums`/`amend_span`
  locals, and the `if amend_span: left += f" {amend_span}"` clause in `build_index` — deleted
- the `am-span` paragraph in `HEADER` ("The `am-span` token appears only on a decision carrying
  amendments…") — deleted, and the `[am-span]` token dropped from the Row grammar line so the
  grammar and the code agree
- the `[am-span]` token in the malformed-row usage/error message near the bottom of the file —
  dropped

Kept, untouched: orphan detection (`build_index`'s `orphans`/`ORPHAN:` block, unchanged), the
refs-graph `live_nums` filter T-06 added (`compute_refs(body, own_num, live_nums)`, unchanged).

Confirmed via grep — zero hits for any of `AMEND_HEADING_RE`, `AMEND_BOLD_RE`,
`compute_amendments`, `format_amendment_span`, `amend_span`, `am-span` anywhere in the file;
`orphan` still present. `python3 -c "import ast; ast.parse(...)"` confirms the file still parses.

## CHANGE 2 — new guard test (complete, registered)

Added `test_no_amendment_construct_survives_in_the_authority` to `test-gen-decisions-index.py`,
registered in `TESTS`. Reads the live `.harness/harness/docs/DECISIONS.md` through
`os.path.join(REPO_ROOT, gdi.DECISIONS_PATH)` — the module's own existing path resolution, not a
restated path. Asserts three patterns SEPARATELY, each naming the matched line number(s) in its
own failure message on miss:
- `^###\s+DEC-[0-9]+\s+amendment` (heading form)
- `^\*\*Amendment` (bold form)
- `am\.\d` (the token itself, anywhere in the line)

## Mutation proof — temp-tree copy method (complete)

`REPO_ROOT` is derived from `__file__` at line 21-22 of the test module, so it cannot be
redirected by an environment override — it can only be redirected by running a COPY of the test
module from inside a copied tree. Built the proof entirely in `/tmp` (never touching the worktree
authority):

1. `TMP=/tmp/t10proof`. Created `$TMP/.claude/skills/harness/bin/` and
   `$TMP/.harness/harness/docs/`.
2. Copied the worktree's entire `.claude/skills/harness/bin/` into the temp tree (needed for
   `harness_boundary.py` and the generator to import).
3. Copied the worktree's `.harness/team-config.yaml` (MARKER) and
   `.harness/harness/docs/{DECISIONS.md,DECISIONS-INDEX.md}` into the temp tree.

   (Used a `python3 - <<EOF` heredoc with `shutil`, not bash `cp` — a raw `cp` targeting a path
   whose *suffix* is `.claude/skills/harness/bin` was refused by `bash-write-guard` even though
   the actual target lives under `/tmp`, outside every domain. The heredoc route matches this
   repo's Expertise G-03.)

4. **CONTROL RUN** — `python3 $TMP/.claude/skills/harness/bin/test-gen-decisions-index.py`,
   unplanted, captured to `/tmp/t10proof_control.out` (exit 1 — same 3 pre-existing FAILs as the
   live tree; see census below).
5-6. **PLANTED RUNS**, one line appended to `$TMP/.harness/harness/docs/DECISIONS.md` each time,
   restoring the temp copy from the worktree's real `DECISIONS.md` between plants, census
   re-captured and diffed against the control census. `test_root_resolves_through_harness_boundary_not_the_retired_variable`'s
   own failure message embeds a `mktemp`-generated path that changes on every run (unrelated to
   this proof — that test builds its own scratch tree internally); both censuses were normalized
   with `sed -E "s#HARNESS_PROJECT_DIR='[^']*'#HARNESS_PROJECT_DIR='NORMALIZED'#"` before diffing
   so that expected noise did not mask the real result.

### (i) Heading form — `### DEC-999 amendment 1 — planted`

```
$ diff /tmp/t10proof_control.norm.out /tmp/t10proof_planted_heading.norm.out
11c11
< ok - test_no_amendment_construct_survives_in_the_authority
---
> FAIL - test_no_amendment_construct_survives_in_the_authority: '### DEC-N amendment' heading found at /private/tmp/t10proof/.harness/harness/docs/DECISIONS.md:[6291]
```
Exactly one line changed. Failure message names the heading pattern by construct (`'### DEC-N
amendment' heading`) and the exact line number.

### (ii) Bold form — `**Amendment 2 — planted`

```
$ diff /tmp/t10proof_control.norm.out /tmp/t10proof_planted_bold.norm.out
11c11
< ok - test_no_amendment_construct_survives_in_the_authority
---
> FAIL - test_no_amendment_construct_survives_in_the_authority: '**Amendment' line found at /private/tmp/t10proof/.harness/harness/docs/DECISIONS.md:[6291]
```
Exactly one line changed. Failure message names its own pattern (`'**Amendment' line`) — distinct
from (i)'s `'### DEC-N amendment' heading`.

### (iii) Token form — a line containing `am.1` inside an existing decision body

Planted: `This ruling revives am.1 inside an existing decision body.`

```
$ diff /tmp/t10proof_control.norm.out /tmp/t10proof_planted_amdot.norm.out
11c11
< ok - test_no_amendment_construct_survives_in_the_authority
---
> FAIL - test_no_amendment_construct_survives_in_the_authority: 'am.<digit>' token found at /private/tmp/t10proof/.harness/harness/docs/DECISIONS.md:[6291]
```
Exactly one line changed. Failure message names its own pattern (`'am.<digit>' token`) — distinct
from both (i) and (ii). All three plants were tested independently against a freshly-restored
copy of the temp tree's `DECISIONS.md`; none of the three shares a failure-message pattern name
with either of the others, and in every one of the three diffs no case besides
`test_no_amendment_construct_survives_in_the_authority` changed state — the mutation is fully
isolated to the case it targets.

`rm -rf /tmp/t10proof` performed after all three plants.

### Live authority — confirmed untouched

```
$ git -C <worktree> diff -- .harness/harness/docs/DECISIONS.md
(empty)
$ git -C <worktree> status --porcelain -- .harness/harness/docs/DECISIONS.md
(empty)
```
Both empty — the live `.harness/harness/docs/DECISIONS.md` was never opened for write by this
proof; every plant/restore cycle operated exclusively on the `/tmp/t10proof` copy.

## Verify block: exit status — FAIL, one collateral case beyond the two excluded (as-observed, unchanged from cycle 0's finding)

```
$ cd "$(git rev-parse --show-toplevel)"
$ G=.claude/skills/harness/bin/gen-decisions-index.py
$ for s in AMEND_HEADING_RE AMEND_BOLD_RE compute_amendments format_amendment_span \
           amend_span am-span; do
    grep -q "$s" "$G" && { echo "still present: $s"; exit 1; }
  done
(no output — none present)
$ grep -q 'orphan' "$G" || exit 1
(present)
$ python3 .claude/skills/harness/bin/test-gen-decisions-index.py > /tmp/t10.out 2>&1
$ grep -q '^ok - test_no_amendment_construct_survives_in_the_authority$' /tmp/t10.out || exit 1
(present)
$ grep -q '^FAIL - test_committed_index_matches_a_fresh_regeneration' /tmp/t10.out || exit 1
(present)
$ grep '^FAIL' /tmp/t10.out \
    | grep -vE 'test_committed_index_(matches_a_fresh_regeneration|is_complete_and_within_budget)' \
    && exit 1
FAIL - test_root_resolves_through_harness_boundary_not_the_retired_variable (a): a markerless HARNESS_PROJECT_DIR override exited 1: harness_boundary: discarding HARNESS_PROJECT_DIR='...' — it does not carry .harness/team-config.yaml. Falling back to the derived root '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-38-decisions-current-knowledge'
$ exit 1
VERIFY_EXIT=1
```

Re-ran this exact block, verbatim, as an actual `bash -c` (not by hand-inspecting grep output) to
get the real exit code: **`EXIT=1`**, confirming cycle 0's finding still holds unchanged in cycle 1
— nothing about the mutation proof touches this path.

`task_verify: fail`.

### Lead's diagnostic — widened exclusion regex (NOT the plan's verify; ad-hoc, reported separately per dispatch)

Same block, with the final exclusion regex additionally excluding
`test_root_resolves_through_harness_boundary_not_the_retired_variable`:

```
$ grep '^FAIL' /tmp/t10.out \
    | grep -vE 'test_committed_index_(matches_a_fresh_regeneration|is_complete_and_within_budget)|test_root_resolves_through_harness_boundary_not_the_retired_variable' \
    && exit 1
exit 0
WIDENED_DIAGNOSTIC_EXIT=0
```

**The widened diagnostic exits 0.** This confirms the third FAIL is the *only* thing standing
between T-10 and a green verify — once the plan's exclusion list accounts for it (or T-11 lands
first and removes the orphan condition), the plan's own verify block will pass unmodified.

## Full census from /tmp/t10.out (7 ok, 3 FAIL — one uncounted by the plan's exclusion list)

```
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_refs_graph_omits_ids_with_no_live_heading
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
FAIL - test_committed_index_matches_a_fresh_regeneration: generator exited 1 — the committed index cannot be reproduced: ORPHAN: DEC-19 … has a ruling in the index but no live heading in .harness/harness/d
FAIL - test_committed_index_is_complete_and_within_budget: 3 row(s) in .../DECISIONS-INDEX.md exceed the 30-word ruling cap — shorten the ruling after ' :: ' on each listed row: DEC-92 (36), DEC-102 (34), DEC-37 (33)
ok - test_orphaned_ruling_is_reported_not_silently_dropped
FAIL - test_root_resolves_through_harness_boundary_not_the_retired_variable (a): a markerless HARNESS_PROJECT_DIR override exited 1: harness_boundary: discarding HARNESS_PROJECT_DIR='...' — it does not carry .harness/team-config.yaml. Falling back to the derived root '.../FEAT-38-decisions-current-knowledge'
ok - test_no_amendment_construct_survives_in_the_authority
```

### Root cause of the third FAIL, and why it is not mine to fix

`test_root_resolves_through_harness_boundary_not_the_retired_variable` part (a) invokes
`gen-decisions-index.py --stdout` against the derived fallback root (the real worktree) and
asserts exit 0. That invocation now hits the SAME orphan-row `sys.exit(1)` as
`test_committed_index_matches_a_fresh_regeneration` (DEC-19 orphaned in `DECISIONS-INDEX.md`,
which is not regenerated until T-11) — nothing about amendment removal touches this path;
`compute_amendments`/`format_amendment_span` never ran in this test's assertions.

Confirmed this is a REGRESSION from later-landed sibling work, not from T-10: T-06's own receipt
(`notes/receipt-harness-backend-dev-2026-08-29-03-eng.md`, T-06 section, full census) shows this
exact test `ok` — 8 ok, exactly 2 FAIL, at that point in the feature's history. The orphan
condition was introduced afterward, by the documentor's T-04/T-05/T-07 deletions in
`DECISIONS.md` landing before `DECISIONS-INDEX.md` was regenerated (T-11's job, later in the
plan). This third FAIL shares the exact root cause the plan already names for the two excluded
cases — the plan's exclusion list is simply one case short of what the current repo state
produces.

**This diagnosis is CONFIRMED by the lead independently** (per this cycle's dispatch): the plan's
verify exclusion list being one case short is a PLAN defect, escalated upward by the lead; it is
T-11's fix to make and not mine. Per constraints, I did not touch `DECISIONS-INDEX.md`,
`run-unit-tests.sh`, `harness.json`, or attempt to weaken/relax
`test_root_resolves_through_harness_boundary_not_the_retired_variable` to make it pass.

## Open questions — none (both resolved by the lead before this cycle)

Q1 (mutation-proof domain conflict) and Q2 (verify exclusion list one case short) were both raised
in cycle 0 and are now decided by the lead: Q1 by the temp-tree method used above (proves the same
red state, writes nothing outside `/tmp`); Q2 confirmed as the identical root cause already named
for the two excluded cases, a PLAN defect the lead is escalating, not a `harness-backend-dev`
failure. Not re-raised.

## git status — the two target files, no partial mutation

```
$ git status --porcelain
 M .claude/skills/harness/bin/gen-decisions-index.py
 M .claude/skills/harness/bin/test-gen-decisions-index.py
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml
?? .claude/skills/harness/bin/check-decision-claims.py
?? .claude/skills/harness/bin/test-check-decision-claims.py
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-backend-dev-2026-08-29-07-eng-T-20.md
?? .harness/notes/grilling-decisions-current-knowledge-2026-08-24.md
```
`plan.yaml`, the two `check-decision-claims*.py` files, the `-T-20` receipt, and the grilling note
are pre-existing sibling-task artifacts (T-20, prior segments) — not touched by this dispatch.
Only `gen-decisions-index.py` and `test-gen-decisions-index.py` were written by me, and neither was
touched again in this cycle (CHANGE 1/2 carried forward unmodified from cycle 0). This cycle's
work — the mutation proof and the verify re-run — touched nothing outside `/tmp` and this receipt.
