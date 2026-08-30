# Receipt — validate-t01-c25 — T-01 self-bar closure

BLUF: both grade-2 functions in `code_grade.py` are now grade 4+, achieved by decomposing
nesting into six named module-level helpers (each independently measured grade 4-5), with
no allowlist replacement. All acceptance items below are verified with literal commands and
output. One anomaly is reported honestly: HEAD advanced during the task via commits made by
a concurrent process, not by any git action I ran.

## Files touched (exactly the two named)

- `.claude/skills/harness/bin/code_grade.py` — decomposed `_body_hashes.collect` and
  `gated_set` into: `_qualname`, `_strip_docstring`, `_hash_body` (used by `_body_hashes`),
  and `_resolve_base_source`, `_resolve_pre_image`, `_gate_file_records` (used by
  `gated_set`). `gated_set` itself is now a thin loop calling `_gate_file_records` and
  extending two accumulators.
- `.claude/skills/harness/bin/test-code-grade.py` — added `_grade_stub`,
  `check_pre_image_resolution_priority`, `check_base_source_rename_fallback` (registered in
  `main()`'s runner tuple); deleted the two `SELF_GRADING_ALLOWLIST` entries for
  `_body_hashes.collect` and `gated_set`.

## 1. TDD — RED before the production edit

Added `check_pre_image_resolution_order` (later split, see below) referencing
`code_grade._resolve_pre_image` / `_resolve_base_source`, which did not yet exist.

```
$ python3 test-code-grade.py
Traceback (most recent call last):
  ...
  File ".../test-code-grade.py", line 428, in check_pre_image_resolution_order
    resolved = code_grade._resolve_pre_image(head, before_names, before_hashes, head_hashes)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'code_grade' has no attribute '_resolve_pre_image'
EXIT:1
```
Confirmed RED for a real behavioural assertion, not a syntax typo.

## 2. Production edit, then GREEN

After the extraction, `python3 test-code-grade.py` initially reported the two allowlist
entries as stale (expected, since the functions were now grade 4) and the new test itself
below its grade-3 bar (ABC 31.9 in one oversized function). Split into two smaller test
functions (`check_pre_image_resolution_priority`, `check_base_source_rename_fallback`) and
deleted the stale allowlist lines. Final run:

```
$ python3 test-code-grade.py
PASS test-code-grade
EXIT:0
```

## 3. Self-grade of `code_grade.py` — every function grade 4+

```
$ python3 code-grade.py code_grade.py
... (53 FUNCTION blocks, all RESULT: PASS) ...
PASSING: 53
EXIT:0
```
Programmatic check of every `GRADE:` line: **0 functions below grade 4**, 0 `RESULT: FAIL`.

Target functions and new helpers, final measurements:

| qualname | cyc | cog | abc | grade | driver |
|---|---|---|---|---|---|
| `_body_hashes.collect` | 4 | 5 | 8.8 | **4** | cognitive+abc |
| `gated_set` | 2 | 1 | 10.0 | **4** | abc |
| `_qualname` | 1 | 1 | 1.0 | 5 | all |
| `_strip_docstring` | 5 | 3 | 5.0 | **4** | cyclomatic |
| `_hash_body` | 2 | 0 | 6.3 | 5 | all |
| `_resolve_base_source` | 3 | 3 | 4.9 | 5 | all |
| `_resolve_pre_image` | 2 | 2 | 4.1 | 5 | all |
| `_gate_file_records` | 4 | 8 | 13.5 | **4** | cognitive+abc |

Before: `_body_hashes.collect` was cyc 9 / cog 18 / abc 17.3 (grade 2, cognitive-driven);
`gated_set` was cyc 8 / cog 25 / abc 24.9 (grade 2, cognitive-driven). Both metrics now
inside the grade-4 band on both functions.

## 4. Allowlist entries deleted; staleness assertion passes

`test-code-grade.py:216-217`'s two lines
(`("code_grade.py", "_body_hashes.collect"): 2` and `("code_grade.py", "gated_set"): 2`) are
removed. `check_self_grading` (which asserts every remaining allowlist entry still matches a
real below-bar record) passed inside the green run above — no replacement entries were
added for the fixed functions or the six new helpers.

## 5. Five focused suites — all pass

```
$ python3 test-code-grade.py            → PASS test-code-grade            EXIT:0
$ python3 test-code-grade-cli.py        → PASS test-code-grade-cli        EXIT:0
$ python3 test-gate-policy.py           → 27/27 ok lines, no FAIL          EXIT:0
$ python3 test-check-plan-routes.py     → ALL PASS                        EXIT:0
$ python3 test-validate-digest.py       → ALL PASSED (66+14+24+2+18 cases) EXIT:0
```

## 6. Behaviour preservation — proven, not asserted

The seven cases inside `check_changed_function_resolution` (`worsened` gated, `newly_added`
gated, `improved` not gated, `renamed_new` not gated, `reformatted` not gated,
`signature_changed` not gated, `moved` not gated, plus `already_bad` gated/informational
path) all passed individually inside the green run in §5 — `check()` prints only on
mismatch, and the suite reported zero failures, so every one of those assertions held.

**Mutation experiment.** Checksum before: `md5sum code_grade.py` →
`c5db829f96b3b8dc8d144a1466392e4d`. Edited `_resolve_pre_image` to check `before_hashes`
first and `before_names` second (swapping the resolution order):

```python
def _resolve_pre_image(record, before_names, before_hashes, head_hashes):
    matches = before_hashes.get(head_hashes[record.qualname], [])
    if matches:
        return matches[0]
    return before_names.get(record.qualname)
```

```
$ python3 test-code-grade.py
FAIL gated set: expected {'worsened', 'newly_added'}, got {'newly_added'}
FAIL qualname match wins over hash match: expected True, got False
2 failures
EXIT:1
```
The named case **"qualname match wins over hash match"** (inside
`check_pre_image_resolution_priority`, the new characterization test) failed exactly as
designed, alongside the pre-existing `check_changed_function_resolution`'s "gated set"
assertion — direct proof the extracted helpers cannot silently disagree on priority.

Restored byte-identically:
```
$ md5sum code_grade.py
c5db829f96b3b8dc8d144a1466392e4d   # identical to pre-mutation
```
```
$ git status --porcelain
 M .claude/skills/harness/bin/code_grade.py
 M .claude/skills/harness/bin/test-code-grade.py
 (+ 3 pre-existing unrelated files, see §7)
```
Re-ran to green:
```
$ python3 test-code-grade.py
PASS test-code-grade
EXIT:0
```

## 7. Tree state

`git -C <worktree> status --porcelain` shows only the two intended files modified plus three
files that were **already modified before this task started** and that I never touched:
`.harness/harness/features/FEAT-43-code-risk-grading/feature.json`,
`.harness/harness/features/FEAT-43-code-risk-grading/notes/uat-sc11-c21.md`, and an untracked
`answers/Q9-sc11-maxima-and-t01-no-exemption.md`. These are the operator's Q9 ruling
artifacts (STATE.md's "Current" section is dated the same day), not mine.

`git -C /Users/molchairuangutai/GitHub/harness status --porcelain` shows **no tracked
modification** — only pre-existing untracked feature/notes directories under `.harness/`.
Main checkout is clean.

**HEAD anomaly — reported, not caused by me.** `git rev-parse HEAD` in the worktree returned
`ea61b5eaa3e3690ff1060e964599d912a631bea4`, not the pinned
`d2e3b5eb47c84fdfac5371b924b7ce1bb8fc37ba`. `git log --oneline -5` shows two `chore:` commits
(`f3b31d8`, `ea61b5e`) landed on top of `d2e3b5e` during this task — I ran no `commit`,
`checkout`, `reset`, or any other HEAD-moving command; the worktree is shared by concurrent
sibling agents in this cycle (visible in the hub roster) and one of them committed.
`git merge-base --is-ancestor d2e3b5eb HEAD` confirms **d2e3b5eb is still an ancestor** of
the current HEAD, so the pinned review basis is intact and none of my own changes are
committed — they remain uncommitted working-tree edits on top of whatever HEAD the
worktree carries at read time. Flagged as `open_questions` for the orchestrator, since HEAD
movement in a shared worktree during an in-flight task is outside this task's control
surface.

## Verdict basis

Every acceptance item is met: RED observed, production edit made, GREEN measured, zero
functions below grade 4 in `code_grade.py` (53/53 pass), both allowlist entries deleted, all
five focused suites green, behaviour preservation proven via the seven-case suite plus a
named mutation-experiment failure and byte-identical restore. The only deviation from the
literal contract is that HEAD is no longer the pinned SHA — caused by a concurrent
committer, not by this task, and the pinned SHA remains an ancestor.

## 8. T-01's declared `verify:` command

`plan.yaml`'s T-01 declares `verify: .claude/skills/harness/bin/run-unit-tests.sh --kind unit`.

```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit
... (full unit corpus, including PASS test-code-grade.py and PASS test-gate-policy.py) ...
EXIT:0
```
`task_verify: pass`.
