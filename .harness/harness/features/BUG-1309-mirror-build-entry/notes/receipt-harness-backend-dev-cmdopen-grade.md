# Receipt — harness-backend-dev — BUG-1309 — cmd_open grade fix

## BLUF
`cmd_open` is at GRADE 4 (bar met) after extracting the ISSUE-TYPES labeling seam into a
new helper `_open_ensure_labels`, which itself measures GRADE 5. No behaviour changed:
same calls, same order, same branching, `record_build_entry(feat_dir, "opened")` remains
the unconditional last statement of the successful path. Both plan verify blocks pass;
`tests/integration/test-gh-sync.py` untouched.

## Seam chosen and why
Extracted lines 1194–1198 (the original `cmd_open`) — the `state == "available"` branch
that either refuses an undeclared issue type then labels `harness`, or sweeps every
task's change-type label when typed issues aren't available — into
`_open_ensure_labels(repo, tasks, rec, parent_arg, issue_types, state, declared)`,
inserted immediately above `cmd_open` in `.claude/skills/harness/bin/gh-sync.py`.

This is the "ISSUE-TYPES concern" named in the dispatch: it exists solely because
GitHub's typed-issues feature may or may not be present on a given repo — a different
reason to change than "create the milestone, the parent and the sub-issues", which is
what the remainder of `cmd_open` does. The bottom half of that same concern
(`_backfill_issue_types`, guarded by `if state == "available":` near the end of
`cmd_open`) was already a one-line call to an existing helper before I started — nothing
further to extract there.

**Deletion test:** inlining `_open_ensure_labels` back into `cmd_open` reproduces the
exact if/else, the `_refuse_undeclared_issue_types` call, `ensure_labels` calls, and the
walrus comprehension — i.e. deleting the helper makes the complexity *reappear* in its
sole caller, not vanish. That is what a real (non-pass-through) extraction looks like.

## Grades — before / after (code-grade.py, verbatim numbers)

| Function | Cyclomatic | Cognitive | ABC | Grade |
|---|---|---|---|---|
| `cmd_open` — before | 7 | 5 | 20.1 | 3 |
| `cmd_open` — after | 4 | 3 | 15.8 | **4** |
| `_open_ensure_labels` — new | 4 | 2 | 5.4 | **5** |

Orchestrator's pre-measurement (cyclomatic 7, cognitive 5, ABC 20.1, grade 3, driver ABC)
was confirmed exactly, before any edit.

## Verify — both blocks, verbatim from plan.yaml T-02/T-03

Cross-checked byte-for-byte against `plan.yaml`'s T-02 (lines 265–269) and T-03
(lines 392–398) `verify:` bodies before running — identical to the dispatch's text.

- T-02 verify → final line: `VERIFY-PASS`. All 8 named `ok    T-02 …` cases present, no
  `^FAIL` line.
- T-03 verify → final line: `VERIFY-PASS`. All 7 named `ok    T-03 …` cases present, no
  `^FAIL` line.

## `cmd_start_task` untouched, proven

Two Edit calls made this session, both anchored strictly inside `cmd_open`'s own
lines (original 1184–1198):
1. `PUT <1184:` — pure insertion of `_open_ensure_labels` immediately above `cmd_open`,
   at the gap before line 1184 (which was the blank line preceding `def cmd_open`).
2. `PUT 1194.=1198:` — replaced the 5 original lines of `cmd_open`'s issue-types branch
   with the single `_open_ensure_labels(...)` call.

Neither anchor falls anywhere near `cmd_start_task` (which lives later in the file, well
past `cmd_recover_terminal`/`cmd_ship`). `git diff -U0` on `gh-sync.py` shows exactly two
hunks: the new function insertion at original line 1183/1184, and the line-1194–1198
replacement inside `cmd_open` — no other hunk exists in the file, i.e. no
`cmd_start_task` hunk is present from my edits (any such hunk appearing later from the
concurrently-running main session is theirs, not mine, and is expected per the dispatch).

## Test file

`tests/integration/test-gh-sync.py` was not touched — no edit was needed; both verify
blocks pass unmodified.

## Files touched
- `.claude/skills/harness/bin/gh-sync.py`
