# Receipt — validate-substring-c29-positives (cycle 29, positive-site widening)

## BLUF

Both surviving positive `"1 file(s)" in …` checks now route through the shared
`reports_exactly_one_file()` predicate. The permanent synthetic control gained a second
function (`case_reports_exactly_one_file_models_the_real_cli_line`) that drives the
predicate with the CLI's *actual* `scanning ... — N file(s)` line shape (from
`validate-feature-json.py:52-53`), not just toy strings — this is what proves the
positive sites no longer fail open, since the live fixtures legitimately have one file
and cannot themselves demonstrate the bug. Full suite green, unit runner green, no new
code-grade failures, one shared regex literal, no allowlist entries, worktree HEAD
untouched, main checkout clean of tracked modifications.

## Final text of the two changed assertions

`case_migrated_depth_discovery_scans_the_segment_layout` (lines 333-334):
```python
        check("case_migrated_depth: the sweep reports ONE file, not zero",
              reports_exactly_one_file(r.stderr), r.stderr)
```

`case_root_resolves_through_harness_boundary_not_the_retired_variable` (lines 369-370):
```python
        check("case_root_resolves: HARNESS_PROJECT_DIR + team-config.yaml IS honoured",
              reports_exactly_one_file(r2.stderr), r2.stderr)
```
Both `check(...)` message strings and both `r.stderr` / `r2.stderr` detail arguments are
byte-identical to the pre-existing text; only the boolean predicate changed. The negative
assertion at line 359 (`not reports_exactly_one_file(r.stderr)`) and everything else in
both functions is untouched.

## Extended control (final text, lines 373-409)

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


def case_reports_exactly_one_file_models_the_real_cli_line():
    """The toy strings above prove the regex; this proves it against the ACTUAL
    shape validate-feature-json.py emits (see its `scanning ... — N file(s)` print),
    so the control models the real call sites (case_migrated_depth_discovery_...
    and case_root_resolves_...), not just an abstract substring. Synthetic strings
    only — no sweep, no disk read, no live feature-directory count."""
    real_root = "/Users/x/GitHub/harness"
    scanning_line = (f"scanning {real_root}/.harness/*/features/*/"
                      "feature.{json,yaml,yml} — 41 file(s)")
    check("control: rejects the real 41 file(s) scanning line "
          "(this is the exact fail-open shape the redirected-root bug renders)",
          reports_exactly_one_file(scanning_line) is False, scanning_line)
    one_line = scanning_line.replace("41 file(s)", "1 file(s)")
    check("control: accepts the real 1 file(s) scanning line",
          reports_exactly_one_file(one_line) is True, one_line)
    hundred_one_line = scanning_line.replace("41 file(s)", "101 file(s)")
    check("control: rejects the real 101 file(s) scanning line",
          reports_exactly_one_file(hundred_one_line) is False, hundred_one_line)
    multiline = f"some warning on stderr\n{one_line}\ntrailing noise"
    check("control: accepts 1 file(s) embedded in a multi-line stderr blob",
          reports_exactly_one_file(multiline) is True, multiline)
```

Both registered in `main()` (lines 688-689):
```python
    case_reports_exactly_one_file_rejects_substring_match()
    case_reports_exactly_one_file_models_the_real_cli_line()
```

I split the original single control into two functions rather than growing one, to keep
each under the ABC/cyclomatic bar without an allowlist entry (see grades below: both
GRADE 4, PASS).

## Acceptance evidence

### 1. No more `"1 file(s)" in` anywhere

```
$ grep -n '"1 file(s)" in' test-validate-feature-json.py
(no output)
$ echo $?
1
```
Grep's own exit is 1 (no match found) — the literal substring test is gone from every
assertion site.

### 2. `reports_exactly_one_file` — helper, all 3 call sites, control

```
41:def reports_exactly_one_file(stderr_text):
334:              reports_exactly_one_file(r.stderr), r.stderr)
359:              not reports_exactly_one_file(r.stderr), r.stderr)
370:              reports_exactly_one_file(r2.stderr), r2.stderr)
373:def case_reports_exactly_one_file_rejects_substring_match():
374:    """Control for reports_exactly_one_file, independent of the live tree's feature-
378:          reports_exactly_one_file("41 file(s) swept") is False, "")
380:          reports_exactly_one_file("21 file(s) swept") is False, "")
382:          reports_exactly_one_file("11 file(s) swept") is False, "")
384:          reports_exactly_one_file("0 file(s) swept") is False, "")
386:          reports_exactly_one_file("1 file(s) swept") is True, "")
389:def case_reports_exactly_one_file_models_the_real_cli_line():
400:          reports_exactly_one_file(scanning_line) is False, scanning_line)
403:          reports_exactly_one_file(one_line) is True, one_line)
406:          reports_exactly_one_file(hundred_one_line) is False, hundred_one_line)
409:          reports_exactly_one_file(multiline) is True, multiline)
688:    case_reports_exactly_one_file_rejects_substring_match()
689:    case_reports_exactly_one_file_models_the_real_cli_line()
```
Three call sites confirmed: line 334 (positive, `case_migrated_depth...`), line 359
(negative, `case_root_resolves...` first check), line 370 (positive, `case_root_resolves...`
second check).

Regex literal occurs exactly once:
```
$ grep -Fn 'r"\b1 file\(s\)"' test-validate-feature-json.py
45:    return re.search(r"\b1 file\(s\)", stderr_text) is not None
$ grep -Fc 'r"\b1 file\(s\)"' test-validate-feature-json.py
1
```

### 3. Mutation-sensitivity re-proven after widening

Pre-mutation diff saved to `/tmp/pre_mutation.diff` (101 lines). Helper body hand-edited
to `return "1 file(s)" in stderr_text` (line 45), rest of file untouched. Ran:
```
$ python3 .claude/skills/harness/bin/test-validate-feature-json.py
...
  6 FAILURE(S): ['case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (scans the real repo root, not the tmp fixture with its single file)', 'control: rejects 41 file(s)', 'control: rejects 21 file(s)', 'control: rejects 11 file(s)', 'control: rejects the real 41 file(s) scanning line (this is the exact fail-open shape the redirected-root bug renders)', 'control: rejects the real 101 file(s) scanning line']
exit=1
```
Named lines from the run:
```
FAIL case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (scans the real repo root, not the tmp fixture with its single file) scanning /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.harness/*/features/*/feature.{json,yaml,yml} — 41 file(s)
FAIL control: rejects 41 file(s)
FAIL control: rejects 21 file(s)
FAIL control: rejects 11 file(s)
FAIL control: rejects the real 41 file(s) scanning line (this is the exact fail-open shape the redirected-root bug renders) scanning /Users/x/GitHub/harness/.harness/*/features/*/feature.{json,yaml,yml} — 41 file(s)
FAIL control: rejects the real 101 file(s) scanning line scanning /Users/x/GitHub/harness/.harness/*/features/*/feature.{json,yaml,yml} — 101 file(s)
```
Two of the six failures are the new realistic-line control cases
(`control: rejects the real 41 file(s) scanning line`,
`control: rejects the real 101 file(s) scanning line`).

Restored the helper body by hand to `return re.search(r"\b1 file\(s\)", stderr_text) is not None`
(line 45 only — never `git restore`/`git checkout --`). Re-ran:
```
$ python3 .claude/skills/harness/bin/test-validate-feature-json.py
...
ALL PASS
$ echo $?
0
```
Restore is byte-identical to the pre-mutation state:
```
$ git diff -- test-validate-feature-json.py > /tmp/post_restore.diff
$ diff /tmp/pre_mutation.diff /tmp/post_restore.diff
(no output)
$ echo $?
0
```

### 4. Positive sites proven no longer fail-open

The mutated (substring) predicate, applied to the new synthetic `41 file(s)` scanning
line, evaluates to `True` — i.e. it wrongly *accepts* the fail-open shape:
`"1 file(s)" in "scanning .../feature.{json,yaml,yml} — 41 file(s)"` is `True`. That
acceptance is exactly what the new control case
(`control: rejects the real 41 file(s) scanning line`) catches — it failed under the
mutant (see §3) and passes under the correct regex predicate.

The live positive assertions themselves (`case_migrated_depth_discovery_scans_the_segment_layout`
and the second check in `case_root_resolves_through_harness_boundary_not_the_retired_variable`)
cannot demonstrate this on their own: their tmp fixtures legitimately contain exactly one
`feature.json`, so `r.stderr`/`r2.stderr` always renders `1 file(s)` — never `41 file(s)` —
regardless of which predicate is used. Only a redirected-root regression would make them
render a multi-digit count, and by definition that regression is what this whole cycle is
about guarding against without relying on it actually occurring in a live run. The synthetic
control is what carries the proof; this is exactly why it was extended with the real-line
shape rather than left as toy strings.

### 5. Full test suite exits 0

```
$ python3 .claude/skills/harness/bin/test-validate-feature-json.py
...
PASS t15_d_an_empty_agent_string_is_refused_so_the_check_is_on_the_value
PASS t15_e_the_positional_rule_is_load_bearing
     (red proof counts: original 1, mutant 0)

ALL PASS
$ echo $?
0
```

### 6. Unit test runner exits 0

```
$ HARNESS_PROJECT_DIR="$PWD" bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit
...
917:PASS test-validate-feature-json.py
...
ok    blocking QA blocks failed suite
ok    advisory QA always passes
PASS test-gate-policy.py
$ echo $?
0
```

### 7. FEAT-43 untouched — `code-grade.py` grading `code_grade.py`

```
$ python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/code_grade.py
...
PASSING: 53
```
No `RESULT: FAIL` lines in the full output — all 53 functions PASS, none below grade 4.

### 8. `code-grade.py` grading the test file — helper and control grades

```
QUALNAME: reports_exactly_one_file       GRADE: 5   RESULT: PASS
QUALNAME: case_reports_exactly_one_file_rejects_substring_match   GRADE: 4   RESULT: PASS
QUALNAME: case_reports_exactly_one_file_models_the_real_cli_line  GRADE: 4   RESULT: PASS
...
PASSING: 45
```
Pre-existing failures, unchanged and NOT introduced by this cycle:
```
QUALNAME: case_t15_red   GRADE: 2   RESULT: FAIL   SEVERITY: med
QUALNAME: main           GRADE: 2   RESULT: FAIL   SEVERITY: med
```
These two are the sole `RESULT: FAIL` lines in the output; both existed before this
dispatch's edits (`main`'s ABC=41.0 is driven by the full case-call list, which every
prior cycle already extended, and `case_t15_red`'s FAIL is from FEAT-31 T-15's red-proof
scaffold, unrelated to this change). No function I added or edited (`reports_exactly_one_file`,
the two positive `check(...)` call sites, the two control functions) newly fails. No
allowlist entry was added anywhere.

### 9. `git diff --stat` — attributable file

```
$ git -C <worktree> diff --stat
 .../harness/bin/test-validate-feature-json.py      | 55 ++++++++++++++++++++--
 .../FEAT-43-code-risk-grading/feature.json         |  4 +-
 2 files changed, 54 insertions(+), 5 deletions(-)
```
Only `test-validate-feature-json.py` is attributable to this dispatch. The `feature.json`
cycles-28→29 hunk is pre-existing (present before this dispatch started) and is not mine.

### 10. `git status --porcelain` (worktree)

```
 M .claude/skills/harness/bin/test-validate-feature-json.py
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q13-cycle-29-substring-gate.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-2026-08-30-03-validate-substring-c29-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-substring-c29.md
```
No scratch files of mine. The three untracked files pre-date this dispatch (sibling
receipts/answers from concurrent cycle-29 agents on this same feature); this dispatch adds
only its own receipt at the path named in its brief.

### 11. `git rev-parse HEAD` — untouched

```
$ git -C <worktree> rev-parse HEAD
f9a4233c47fced65c2a7eb63ff3949884b65ccdb
```
Matches the expected value exactly; HEAD was never moved.

### 12. Main checkout clean of tracked modifications

```
$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/
?? .harness/harness/features/FEAT-43-code-risk-grading/
?? .harness/harness/features/FEAT-44-omp-context-advisory/
?? .harness/harness/features/PR-922-omp-supervision/
?? .harness/logs/2026-08-25.md
?? .harness/logs/2026-08-29.md
?? .harness/notes/analysis-path-accessors-2026-08-26.md
?? .harness/notes/analysis-pr-922-omp-supervision-2026-08-28.md
?? .harness/notes/analysis-pr-922-omp-supervision-c1-2026-08-28.md
?? .harness/notes/grilling-845-one-vocabulary-2026-08-25.md
?? .harness/notes/grilling-root-resolution-2026-08-26.md
?? .harness/notes/probe-746-foreground-dispatch-2026-08-26.md
?? .harness/notes/triage-decisions-authority-2026-08-26.md
```
Every entry is `??` (untracked); no `M`/`A`/`D` tracked-modification line anywhere.
