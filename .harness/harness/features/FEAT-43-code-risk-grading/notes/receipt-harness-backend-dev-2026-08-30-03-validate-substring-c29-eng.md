# Receipt — validate-substring-c29 — harness-backend-dev — cycle 29

## BLUF

Fixed. The negative assertion in `case_root_resolves_through_harness_boundary_not_the_retired_variable()`
now calls a shared, module-level predicate `reports_exactly_one_file()` (word-boundary regex
`\b1 file\(s\)`) instead of a plain substring test. Added a permanent, synthetic-input control case
`case_reports_exactly_one_file_rejects_substring_match()` that proves the helper rejects `"41
file(s)"`/`"21 file(s)"`/`"11 file(s)"`/`"0 file(s)"` and accepts `"1 file(s)"`, registered in
`main()`, reading nothing from disk and running no sweep — so it cannot pass vacuously as the live
tree's feature-directory count drifts. Exactly one file changed:
`.claude/skills/harness/bin/test-validate-feature-json.py`. `--kind unit` is green. Mutation-sensitivity
proven by hand: reverting the helper's body to the old substring form makes the named control fail
(and reproduces the original live-assertion failure too), restoring it by hand-edit reproduces the
diff byte-for-byte.

**One discrepancy to flag, not caused by this change:** `git rev-parse HEAD` in the worktree reports
`f9a4233c47fced65c2a7eb63ff3949884b65ccdb`, not the `1d292c2b2e22486fd7ad47fa9021ddec880dabcb` the
dispatch and Q13 state as the pinned merge commit. `f9a4233` is one commit ahead of `1d292c2` —
`chore: record the FEAT-43 merge-delta review and its one blocking finding`, authored
2026-08-30T07:42:48-07:00, committing only `feature.json` + three `notes/*mergedelta*.md` review
artifacts, no source. This commit predates my dispatch (I never ran `commit`, `checkout`, `reset`,
`merge`, `rebase`, `stash`, or any HEAD-moving command — only `read`/`grep`/`git diff`/`git apply` of
a patch I authored and fully reversed for the mutation test, verified byte-identical below). The
working-tree `feature.json` diff on top of `f9a4233` (`cycles_used`/`max_total_cycles` 28→29) matches
Q13's own statement verbatim ("both become 29"), so this is consistent with normal cross-cycle state,
just not the exact SHA text my dispatch asserted. Reporting as observed rather than silently treating
`1d292c2` as current.

## Evidence for every acceptance item

### 1. `git diff --stat` — exactly one file *I* touched

```
$ git -C <worktree> diff --stat
 .../harness/bin/test-validate-feature-json.py      | 27 +++++++++++++++++++++-
 .../FEAT-43-code-risk-grading/feature.json         |  4 ++--
 2 files changed, 28 insertions(+), 3 deletions(-)
```

The `feature.json` hunk (`cycles_used`/`max_total_cycles` 28→29) was already present in the worktree
before I made any edit and was never touched by me — confirmed by re-diffing it in isolation:

```
$ git diff -- .harness/harness/features/FEAT-43-code-risk-grading/feature.json
-  "cycles_used": 28,
-  "max_total_cycles": 28,
+  "cycles_used": 29,
+  "max_total_cycles": 29,
```

Per the contract ("Exactly ONE file may change: `test-validate-feature-json.py`"), that file is the
only one I edited. `git status --porcelain` (below) also lists only these two tracked paths plus
harness-written notes.

### 2. Mutation-sensitivity — proven, not asserted

Saved the pre-mutation diff (`/tmp/pre_mutation.diff`, 66 lines). Mutated the helper's body back to
the buggy substring form:

```python
def reports_exactly_one_file(stderr_text):
    ...
    return "1 file(s)" in stderr_text     # mutated
```

Ran the test file — the named control **and** the live assertion both fail by name:

```
FAIL case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (scans the real repo root, not the tmp fixture with its single file) scanning …/.harness/*/features/*/feature.{json,yaml,yml} — 41 file(s)
FAIL control: rejects 41 file(s)
FAIL control: rejects 21 file(s)
FAIL control: rejects 11 file(s)
4 FAILURE(S): [..., 'control: rejects 41 file(s)', 'control: rejects 21 file(s)', 'control: rejects 11 file(s)']
EXIT=1
```

Restored the helper's body by hand-edit (never `git restore`/`git checkout --`) to
`return re.search(r"\b1 file\(s\)", stderr_text) is not None`, then compared the restored diff against
the saved pre-mutation diff byte-for-byte:

```
$ diff /tmp/pre_mutation.diff /tmp/post_restore.diff && echo IDENTICAL
IDENTICAL
```

Re-ran green:

```
$ python3 .claude/skills/harness/bin/test-validate-feature-json.py
...
ALL PASS
EXIT=0
```

### 3. Shared-predicate property — demonstrated, not asserted

```
$ grep -n "reports_exactly_one_file" .claude/skills/harness/bin/test-validate-feature-json.py
41:def reports_exactly_one_file(stderr_text):
359:              not reports_exactly_one_file(r.stderr), r.stderr)
373:def case_reports_exactly_one_file_rejects_substring_match():
374:    """Control for reports_exactly_one_file, independent of the live tree's feature-
378:          reports_exactly_one_file("41 file(s) swept") is False, "")
380:          reports_exactly_one_file("21 file(s) swept") is False, "")
382:          reports_exactly_one_file("11 file(s) swept") is False, "")
384:          reports_exactly_one_file("0 file(s) swept") is False, "")
386:          reports_exactly_one_file("1 file(s) swept") is True, "")
665:    case_reports_exactly_one_file_rejects_substring_match()
```

`\b1 file\(s\)` appears exactly once in the file, at line 45 (the helper's own body) — confirmed by
`grep -n 'file\(s\)'` over the whole file: the only other literal `"1 file(s)"` occurrences are the
two POSITIVE assertions at (now) lines 334 and 370, both left byte-identical per the non-goals — they
assert against real single-file tmp fixtures, not the live repo count, so a substring test there is
correct and unrelated to this defect. No second copy of the regex exists anywhere in the file.

### 4. `test-validate-feature-json.py` exits 0

```
$ python3 .claude/skills/harness/bin/test-validate-feature-json.py
...
PASS control: rejects 41 file(s)
PASS control: rejects 21 file(s)
PASS control: rejects 11 file(s)
PASS control: rejects 0 file(s)
PASS control: accepts 1 file(s)
...
ALL PASS
EXIT=0
```

### 5. `--kind unit` gate — the gate the merge turned red

```
$ HARNESS_PROJECT_DIR="$PWD" bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit
...
PASS test-validate-feature-json.py
...
ok    complete board: exits 0
...
17/17 cases passed  (test-sync-agent-adapters.py, and every other suite in the run, all green)
...
39/39 checks passed  (test-gh-cost-log.py)
...
EXIT=0
```

Full run: every suite listed `PASS`/`ALL PASS`/`N/N passed`; exit code `0`. (Full output at
`artifact://2529`, elided here for length.)

### 6. FEAT-43 source untouched — `code_grade.py` still 53/53

```
$ python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/code_grade.py
...
PASSING: 53
EXIT=0
```

53 functions, zero below grade 4, matching the required baseline. No source-file change occurred
(only the test file was touched).

### 7. New test function clears the test file's own grading bar, no allowlist entry

```
$ python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/test-validate-feature-json.py
...
FUNCTION
PATH: ".claude/skills/harness/bin/test-validate-feature-json.py"
LINE: 41
QUALNAME: reports_exactly_one_file
GRADE: 5
BAR: 3
RESULT: PASS
...
FUNCTION
PATH: ".claude/skills/harness/bin/test-validate-feature-json.py"
LINE: 373
QUALNAME: case_reports_exactly_one_file_rejects_substring_match
GRADE: 4
BAR: 3
RESULT: PASS
...
PASSING: 44
EXIT=0
```

Both the helper and the new control case pass on their own merit (grade 5 and grade 4 respectively
against a bar of 3), with no allowlist entry added by me. Two pre-existing failures survive
unrelated to this change — `case_t15_red` (grade 2) and `main` (grade 2) — confirmed present in the
unmodified HEAD content too, graded under the real filename (so the same BAR: 3 applies) by
temporarily reverting via `git apply -R /tmp/pre_mutation.diff`, grading, then restoring via
`git apply /tmp/pre_mutation.diff` (verified identical to the working diff via
`git diff /tmp/pre_mutation.diff <(git diff -- test-validate-feature-json.py)`, no output = clean):

```
$ git apply -R /tmp/pre_mutation.diff && python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/test-validate-feature-json.py | grep -B6 'RESULT: FAIL'
...QUALNAME: case_t15_red...  GRADE: 2  BAR: 3  RESULT: FAIL
...QUALNAME: main...          GRADE: 2  BAR: 3  RESULT: FAIL
$ git apply /tmp/pre_mutation.diff   # restore, confirmed byte-identical
```

`main`'s ABC nudges from 39.0 (HEAD) to 40.0 (one more case call) but was already failing before this
change and stays failing after — not a regression introduced by this remediation, and out of this
task's scope (the dispatch's in-scope surface is the assertion, the helper, and one new case).

### 8. `git status --porcelain` — only the one test file plus harness-written artifacts

```
$ git status --porcelain
 M .claude/skills/harness/bin/test-validate-feature-json.py
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q13-cycle-29-substring-gate.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-substring-c29.md
```

The `feature.json` M and both `??` entries pre-date my dispatch (the Q13 ruling and the cycle-29
cycles bump, and an earlier receipt from a prior — reverted — attempt at this same task). None were
created or modified by me.

### 9. `git rev-parse HEAD`

```
$ git rev-parse HEAD
f9a4233c47fced65c2a7eb63ff3949884b65ccdb
```

**Does not match** the dispatch's stated `1d292c2b2e22486fd7ad47fa9021ddec880dabcb`. See BLUF above —
`f9a4233` is one commit ahead of `1d292c2`, pre-dates this dispatch, contains no source change, and I
performed no HEAD-moving command. Flagging as an open question rather than silently accepting either
SHA as ground truth.

### 10. Main checkout clean

```
$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/
?? .harness/harness/features/FEAT-43-code-risk-grading/
?? .harness/harness/features/FEAT-44-omp-context-advisory/
?? .harness/harness/features/PR-922-omp-supervision/
?? .harness/logs/...
?? .harness/notes/...
```

No **tracked** modification — every entry is `??` (untracked). Satisfies the constraint.

## Final exact text

**Import block** (`.claude/skills/harness/bin/test-validate-feature-json.py:11-15`):
```python
import json
import os
import re
import subprocess
import sys
import tempfile
```

**Helper** (lines 41-45):
```python
def reports_exactly_one_file(stderr_text):
    """True iff stderr reports EXACTLY one file swept via a word-boundary match,
    never a substring match against a larger rendered count (a plain `in` test
    would wrongly accept "41 file(s)" because it contains "1 file(s)")."""
    return re.search(r"\b1 file\(s\)", stderr_text) is not None
```

**Changed assertion** (lines 356-358, inside `case_root_resolves_through_harness_boundary_not_the_retired_variable`):
```python
        check("case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep "
              "(scans the real repo root, not the tmp fixture with its single file)",
              not reports_exactly_one_file(r.stderr), r.stderr)
```

**New control case** (lines 373-386):
```python
def case_reports_exactly_one_file_rejects_substring_match():
    """Control for reports_exactly_one_file, independent of the live tree's feature-
    directory count. A plain substring test would wrongly accept "41 file(s)" since
    it contains "1 file(s)"; this proves the shared predicate does not."""
    check("control: rejects 41 file(s)",
          reports_exactly_one_file("41 file(s) swept") is False, "")
    check("control: rejects 21 file(s)",
          reports_exactly_one_file("21 file(s) swept") is False, "")
    check("control: rejects 11 file(s)",
          reports_exactly_one_file("11 file(s) swept") is False, "")
    check("control: rejects 0 file(s)",
          reports_exactly_one_file("0 file(s) swept") is False, "")
    check("control: accepts 1 file(s)",
          reports_exactly_one_file("1 file(s) swept") is True, "")
```

**`main()` registration** (line 665, immediately after
`case_root_resolves_through_harness_boundary_not_the_retired_variable()`):
```python
    case_reports_exactly_one_file_rejects_substring_match()
```
