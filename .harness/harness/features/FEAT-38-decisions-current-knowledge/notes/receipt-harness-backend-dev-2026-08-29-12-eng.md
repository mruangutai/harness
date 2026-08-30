# Receipt — harness-backend-dev — FEAT-38 — live-authority guard cases

## What changed
Two files only, per assignment:
- `.claude/skills/harness/bin/test-check-decision-anchors.py`: added `test_live_authority_anchors_all_resolve`, registered in `TESTS`, corrected the module docstring (no longer claims every case is synthetic).
- `.claude/skills/harness/bin/test-check-decision-claims.py`: added `test_live_authority_claims_all_hold`, registered in `TESTS`, same docstring correction.

Both new cases invoke each checker's existing `run_checker(path)` helper against the live authority, resolved via `importlib.util.spec_from_file_location` reading the checker's own `DECISIONS_REL_PATH` constant (mirrors `test-gen-decisions-index.py`'s `gdi.DECISIONS_PATH` precedent). No existing case touched.

## Verification — each test file directly
```
$ python3 <WT>/.claude/skills/harness/bin/test-check-decision-anchors.py
ok - test_in_range_anchor_reports_nothing_and_exits_zero
ok - test_missing_file_is_reported_and_exits_one
ok - test_out_of_range_line_is_reported_and_exits_one
ok - test_zero_anchors_exits_zero_and_says_so
ok - test_unreadable_target_exits_two_not_zero
ok - test_default_file_is_dev_null_readable_zero_anchors
ok - test_live_authority_anchors_all_resolve
exit: 0

$ python3 <WT>/.claude/skills/harness/bin/test-check-decision-claims.py
ok - test_matching_claim_exits_zero
ok - test_mismatching_claim_reports_heading_and_exits_one
ok - test_disallowed_first_token_is_refused_and_exits_one
ok - test_zero_markers_exits_zero_and_says_so
ok - test_nonexistent_path_in_command_is_a_failure_not_a_crash
ok - test_unreadable_target_exits_two_not_zero
ok - test_checker_source_never_uses_shell_true
ok - test_live_authority_claims_all_hold
exit: 0
```

## Mutation proof — anchors (temp-copy method, never touched live DECISIONS.md)
Copied live `DECISIONS.md` to a tempdir, appended a line with a rotted anchor
(`` `does-not-exist-anywhere-xyz123.py:1` ``), ran the CHECKER (not the test) directly on the copy:

```
$ python3 <WT>/.claude/skills/harness/bin/check-decision-anchors.py --file <tmp>/decisions-copy.md
`does-not-exist-anywhere-xyz123.py:1`: file not found in the tree
examined 21 anchor(s), 1 failed
exit: 1
```
RED confirmed: exactly 1 failure, attributable to the planted line (live authority currently has 20 clean anchors; the copy has 21, 1 failing).

## Mutation proof — claims (temp-copy method)
Live authority's first claim marker: `<!-- claim: grep -F "CRAFT_LINE_BUDGET = 150" .claude/skills/harness/bin/check-expertise.sh :: CRAFT_LINE_BUDGET = 150 -->`.
Copied `DECISIONS.md` to a tempdir, mutated ONLY the expected substring to `CRAFT_LINE_BUDGET = 999999` (command unchanged, so it still runs and still returns real stdout that no longer contains the new expected text). Ran the checker on the copy with `cwd=<WT>` (required — the claim commands are repo-relative):

```
$ cd <WT> && python3 <WT>/.claude/skills/harness/bin/check-decision-claims.py --file <tmp>/decisions-copy.md
DEC-145 — Expertise v2: observations mid-run, Expertise only at distillation: `grep -F "CRAFT_LINE_BUDGET = 150" .claude/skills/harness/bin/check-expertise.sh` :: 'CRAFT_LINE_BUDGET = 999999': expected substring 'CRAFT_LINE_BUDGET = 999999' not found in stdout: 'CRAFT_LINE_BUDGET = 150\n'
examined 11 claim(s), 1 failed
exit: 1
```
RED confirmed: exactly 1 failure, attributable to the planted mutation (live authority currently has 11 clean claim markers, 0 failing).

(First attempt at the claims mutation was run without `cwd=<WT>`, which spuriously failed two unrelated DEC-205 markers because their `grep` commands are repo-relative — that run is not evidence and is not counted here; the corrected run above with `cwd=<WT>` isolates exactly the one planted mutation.)

Both temp copies and their tempdirs were discarded (`rm -rf`) after use — never planted into the live file. Confirmed below the live `DECISIONS.md`/`DECISIONS-INDEX.md` diffstat is empty.

## Green transcripts — new cases re-run against the untouched live authority
```
$ python3 <WT>/.claude/skills/harness/bin/test-check-decision-anchors.py | grep live_authority
ok - test_live_authority_anchors_all_resolve

$ python3 <WT>/.claude/skills/harness/bin/test-check-decision-claims.py | grep live_authority
ok - test_live_authority_claims_all_hold
```

## `run-unit-tests.sh` — measured, not the stated baseline
```
$ out=$(bash <WT>/.claude/skills/harness/bin/run-unit-tests.sh 2>&1); echo $?
exit: 0
$ echo "$out" | grep -c '^FAIL'
0
```
`grep -n "check-decision-anchors\|check-decision-claims"` on the captured output shows both scripts registered and PASS (`PASS test-check-decision-anchors.py`, `PASS test-check-decision-claims.py`), each printing its new `ok - test_live_authority_*` line inline before the script-level PASS. The runner's own "PASS `<script>`" tally, not a single global "N passed" line, is what this script emits — 61 script-level `PASS <name>` lines, 0 `FAIL` lines anywhere in the transcript, exit 0. I report this as my own measurement; the dispatch's stated "1117 PASS" baseline uses a counting convention I could not locate a matching summary line for in this script's actual output, so I did not force a match to it — the load-bearing fact is 0 FAIL and exit 0.

## `git status --porcelain` (full list)
```
 M .claude/skills/harness/bin/gen-decisions-index.py
 M .claude/skills/harness/bin/test-check-decision-anchors.py
 M .claude/skills/harness/bin/test-check-decision-claims.py
 M .claude/skills/harness/bin/test-no-distribution.py
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/qa-2026-08-29-10-validator.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-backend-dev-2026-08-29-11-eng-simplify-apply.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-backend-dev-2026-08-29-11-eng-simplify-reuse.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-backend-dev-2026-08-29-11-eng-simplify-simplification.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-dev-ops-2026-08-29-11-eng-simplify-altitude.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-dev-ops-2026-08-29-11-eng-simplify-efficiency.md
?? .harness/notes/grilling-decisions-current-knowledge-2026-08-24.md
```
Exactly the two files I own plus the two pre-existing SIMPLIFY uncommitted edits (`gen-decisions-index.py`, `test-no-distribution.py`) and pre-existing untracked notes from sibling runs. No stray writes.

## `DECISIONS.md` / `DECISIONS-INDEX.md` diffstat — explicitly empty
```
$ git -C <WT> diff --stat -- .harness/harness/docs/DECISIONS.md .harness/harness/docs/DECISIONS-INDEX.md
(no output)
```
Empty. Neither file was touched.

## Acceptance checklist
- Both new cases exist, registered, GREEN against live authority — yes.
- Both assert non-zero examined + zero failed, parsed from the summary line — yes (`examined (\d+) anchor(s), (\d+) failed` / `examined (\d+) claim(s), (\d+) failed`).
- Neither pins an exact count — yes.
- Both docstrings corrected — yes.
- No existing case weakened/renamed/deleted — yes, verified by diff shape (pure insertions plus the docstring block replacement).
- Mutation transcripts for both, red-then-restored/untouched-green — yes, above.
- `DECISIONS.md`/`DECISIONS-INDEX.md` diffstat empty — yes, stated explicitly above.
- Nothing committed — yes.

## Mutation proof — the vacuity branch (`examined == 0`) — CYCLE 2
Cycle 1's mutation proof reddened the CHECKER on a mutated temp copy, which only ever
exercises the `returncode != 0` and `failed != 0` branches of the two live-authority
cases. The `examined == 0` guard — the vacuity assertion the orchestrator specifically
demanded — had never been observed firing. This closes that gap without touching the
live authority or the checkers.

### The stub
Both test files resolve `CHECKER` from an env var (`CHECK_DECISION_ANCHORS_BIN` /
`CHECK_DECISION_CLAIMS_BIN`) before both the `importlib` load and the `subprocess.run`
call, so pointing that var at a stub reaches both. Wrote two stub scripts to a tempdir
(outside the repo, never in the worktree):

`stub-check-decision-anchors.py` — defines `DECISIONS_REL_PATH = os.path.join(".harness", "harness", "docs", "DECISIONS.md")` at module scope (so the import in the test file still resolves `LIVE_DECISIONS` to a readable path), and under `__main__`, ignoring argv, prints `examined 0 anchor(s), 0 failed` and exits 0.

`stub-check-decision-claims.py` — identical shape, prints `examined 0 claim(s), 0 failed` and exits 0.

Each is a checker that has gone silently blind and reports success anyway — the exact failure the vacuity guard exists to catch.

### RED — anchors, stubbed
```
$ CHECK_DECISION_ANCHORS_BIN=<tmp>/stub-check-decision-anchors.py python3 <WT>/.claude/skills/harness/bin/test-check-decision-anchors.py
FAIL - test_in_range_anchor_reports_nothing_and_exits_zero: did not report examining the one anchor: 'examined 0 anchor(s), 0 failed\n'
FAIL - test_missing_file_is_reported_and_exits_one: expected exit 1, got 0: 'examined 0 anchor(s), 0 failed\n' ''
FAIL - test_out_of_range_line_is_reported_and_exits_one: expected exit 1, got 0: 'examined 0 anchor(s), 0 failed\n' ''
ok - test_zero_anchors_exits_zero_and_says_so
FAIL - test_unreadable_target_exits_two_not_zero: expected exit 2 for an unreadable target, got 0: 'examined 0 anchor(s), 0 failed\n' ''
ok - test_default_file_is_dev_null_readable_zero_anchors
FAIL - test_live_authority_anchors_all_resolve: examined 0 anchors — the checker or its path resolution is broken, not proven clean: 'examined 0 anchor(s), 0 failed\n'
exit: 1
```
The load-bearing line is `FAIL - test_live_authority_anchors_all_resolve: examined 0 anchors — …` — the vacuity branch, reached and reddened. The five other FAILs are collateral: they assert real checker behaviour (exit codes, specific messages) that a checker only printing a fixed zero-summary line cannot satisfy, and are expected, not evidence of anything new.

### RED — claims, stubbed
```
$ CHECK_DECISION_CLAIMS_BIN=<tmp>/stub-check-decision-claims.py python3 <WT>/.claude/skills/harness/bin/test-check-decision-claims.py
FAIL - test_matching_claim_exits_zero: did not report examining 1 claim: 'examined 0 claim(s), 0 failed\n'
FAIL - test_mismatching_claim_reports_heading_and_exits_one: expected exit 1, got 0: 'examined 0 claim(s), 0 failed\n' ''
FAIL - test_disallowed_first_token_is_refused_and_exits_one: expected exit 1, got 0: 'examined 0 claim(s), 0 failed\n' ''
ok - test_zero_markers_exits_zero_and_says_so
FAIL - test_nonexistent_path_in_command_is_a_failure_not_a_crash: expected exit 1 (failure, not a crash or skip), got 0: 'examined 0 claim(s), 0 failed\n' ''
FAIL - test_unreadable_target_exits_two_not_zero: expected exit 2 for an unreadable target, got 0: 'examined 0 claim(s), 0 failed\n' ''
ok - test_checker_source_never_uses_shell_true
FAIL - test_live_authority_claims_all_hold: examined 0 claims — the checker or its path resolution is broken, not proven clean: 'examined 0 claim(s), 0 failed\n'
exit: 1
```
Load-bearing line: `FAIL - test_live_authority_claims_all_hold: examined 0 claims — …`. Same collateral-failure note applies to the other five.

Both live-authority cases reddened on exactly the predicted branch, on the first attempt — no exception was swallowed, no import crash, no differently-worded FAIL. No test-file change was needed; the guard as written is genuinely reachable and correct.

### GREEN — unstubbed re-runs
```
$ python3 <WT>/.claude/skills/harness/bin/test-check-decision-anchors.py
ok - test_in_range_anchor_reports_nothing_and_exits_zero
ok - test_missing_file_is_reported_and_exits_one
ok - test_out_of_range_line_is_reported_and_exits_one
ok - test_zero_anchors_exits_zero_and_says_so
ok - test_unreadable_target_exits_two_not_zero
ok - test_default_file_is_dev_null_readable_zero_anchors
ok - test_live_authority_anchors_all_resolve
exit: 0

$ python3 <WT>/.claude/skills/harness/bin/test-check-decision-claims.py
ok - test_matching_claim_exits_zero
ok - test_mismatching_claim_reports_heading_and_exits_one
ok - test_disallowed_first_token_is_refused_and_exits_one
ok - test_zero_markers_exits_zero_and_says_so
ok - test_nonexistent_path_in_command_is_a_failure_not_a_crash
ok - test_unreadable_target_exits_two_not_zero
ok - test_checker_source_never_uses_shell_true
ok - test_live_authority_claims_all_hold
exit: 0
```

### `run-unit-tests.sh` — no override, measured
```
$ out=$(bash <WT>/.claude/skills/harness/bin/run-unit-tests.sh 2>&1); echo $?
exit: 0
$ echo "$out" | grep -c '^FAIL'
0
```

### `git status --porcelain` and diffstat — unchanged from cycle 1
Same file set as cycle 1's list (the two SIMPLIFY-pending edits, sibling untracked notes, this receipt) plus nothing new — no stub file exists inside the worktree, the tempdir was outside the repo and removed (`rm -rf`) after use.
```
$ git -C <WT> diff --stat -- .harness/harness/docs/DECISIONS.md .harness/harness/docs/DECISIONS-INDEX.md
(no output)
```
Empty. Neither file was touched.

### Cycle 2 acceptance
- Both live-authority cases observed RED on `examined == 0`, FAIL line quoted verbatim above — yes.
- Both observed green again with no override — yes.
- No assertion weakened; test files unmodified (no defect exposed) — yes.
- `run-unit-tests.sh` exit 0, 0 FAIL — yes, measured above.
- `DECISIONS.md`/`DECISIONS-INDEX.md` diffstat empty — yes, stated explicitly.
- Nothing committed — yes.
