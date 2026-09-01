# Handoff — BUG-1055, build → validate — written at e353c7e, seq-2

## Next

The panel has already run against `review_sha` e353c7e, base 9f2a070, and returned
**PASS** at `severity_max: med` with an empty `must_fix`. Its one substantive finding
(F1/F2, one shared remedy) was folded in rather than filed, because it pinned this fix's
own only guard and the edit was test-only in a file the diff already touched. What remains
is the merge and the board move — no further review cycle is owed.

## Trust

- The defect is fixed at the reported symptom: the standalone reproduction that raised
  `RuntimeError` at `code_grade.py:323` now reports the previously-masked finding,
  `messy` at `RESULT: FAIL / SEVERITY: med` — verified-at e353c7e
- Both tests were observed RED before the fix and for the intended reasons — the unit check
  raised the ticket's exact `RuntimeError`, the CLI check failed its no-crash, masked-finding
  and verdict assertions — verified-at 9f2a070 + working tree
- The CLI check's exit-code assertion **passed while the tool was crashing**, which is why
  the binding assertions are on stdout and stderr; the exit code is 1 either way
  — verified-at 9f2a070
- `--literal-pathspecs` is load-bearing, not decorative: dropping it makes `ls-tree` exit 0
  with empty output for a path genuinely present as `:colon.py`, so a present path reads as
  absent and `_git_show` returns None — the ticket's own fail-open in a new place
  — verified-at e353c7e, reproduced directly against git
- The new assertion kills that mutant, and independently kills qa's `_tree_has_path ->
  return False` mutant, which previously died to exactly one assertion. Both mutants
  measured; source restored byte-identically after each — verified-at working tree
- No other production site in `bin/` matches git's English; the old
  `"exists on disk, but not in"` string is gone from production code and survives only in
  unrelated prose — verified-at e353c7e
- `_git_show` and `_tree_has_path` both self-grade 5, above the bar of 4 — verified-at e353c7e
- unit 473 PASS, integration 588 PASS, both exit 0; `check-state.sh` 0 violations
  — verified-at working tree

## Dead ends

- Folding F1's fixture through `_git_show` rather than `_tree_has_path` — `git show` succeeds
  on `<ref>::colon.py`, so the call returns at the happy path and never reaches the probe;
  the guard can only be pinned by calling `_tree_has_path` directly — verified-at e353c7e
- Filing F1 as a follow-up ticket, which the panel offered as Q2 — the remedy is one
  assertion in a file this diff already edits, and deferring it leaves the guard against
  this very bug unpinned while the ticket queues — source: operator judgement, 2026-08-31

## Working set

- `.claude/skills/harness/bin/code_grade.py` — `_tree_has_path`, `_git_show` (313-336)
- `.claude/skills/harness/bin/test-code-grade.py` — `check_base_source_absent_from_worktree`
- `.claude/skills/harness/bin/test-code-grade-cli.py` — `test_absent_new_path_grades_the_range`
- `notes/review-harness-*-c0.md` — the four panel notes; the lead digest is under `runs/`,
  which `.gitignore:7` keeps local by design
- `issue://1055` — the filed defect
