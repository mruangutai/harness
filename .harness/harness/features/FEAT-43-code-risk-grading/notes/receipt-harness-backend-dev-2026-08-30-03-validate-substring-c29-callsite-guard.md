# Receipt — validate-substring-c29 · guard the call sites, not just the helper

**BLUF:** Added a source-level AST guard (`_rendered_count_substring_compares` +
`case_no_bare_rendered_count_substring_outside_the_helper`) to
`.claude/skills/harness/bin/test-validate-feature-json.py`. It parses the file's OWN
source at test time and asserts no `in`/`not in` comparison anywhere has a left-operand
string literal shaped like a rendered count (`\d+ file\(s\)`). Reverting any of the three
call sites (334/359/370, original numbering) or the helper body itself back to the bare
substring predicate now fails a NAMED case even though the two existing controls only
ever exercise the helper's behavior, never its call sites. All three legitimate
`in r.stderr` predicates (lines 241, 260, 336) are structurally exempt because their left
operands ("'branch'", "REQUIRED", ".harness/*/features/") do not match the count shape —
proven by inspection, not by an allowlist.

## Change

- `import ast` added, alphabetically first in the stdlib block (before `json`).
- New module-level helper + case inserted immediately after the two existing controls
  (`case_reports_exactly_one_file_rejects_substring_match`,
  `case_reports_exactly_one_file_models_the_real_cli_line`), before the FEAT-26 section
  comment. Registered in `main()` right after the second control.

Final text (verbatim, current file):

```python
def _rendered_count_substring_compares(source):
    """Line numbers of `in`/`not in` comparisons whose LEFT operand is a string
    literal shaped like a rendered count ("N file(s)") — the exact bare-substring
    predicate reports_exactly_one_file exists to replace. Walks the parsed AST,
    never raw text, so docstrings and check() detail strings (not Compare nodes)
    cannot trigger it, and the three legitimate `in r.stderr` predicates elsewhere
    in this file (testing "'branch'", "REQUIRED", ".harness/*/features/") cannot
    either, since none of those left operands match the rendered-count shape."""
    hits = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Compare):
            continue
        if not any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops):
            continue
        left = node.left
        if (isinstance(left, ast.Constant) and isinstance(left.value, str)
                and re.fullmatch(r"\d+ file\(s\)", left.value)):
            hits.append(node.lineno)
    return hits


def case_no_bare_rendered_count_substring_outside_the_helper():
    """Guard for reports_exactly_one_file's own call sites (FEAT-43): reverting any
    of them back to `"1 file(s)" in r.stderr` leaves the helper itself correct and
    both controls above still green, since neither exercises a call site — every
    control passes and the regression is invisible. This asserts the property on
    THIS FILE'S OWN SOURCE instead: no bare rendered-count substring comparison may
    survive anywhere outside reports_exactly_one_file's own regex-based body."""
    with open(__file__, "r", encoding="utf-8") as f:
        source = f.read()
    hits = _rendered_count_substring_compares(source)
    check("no bare rendered-count substring compare outside reports_exactly_one_file",
          hits == [], f"offending line(s): {hits}")
```

Registration in `main()`, immediately after
`case_reports_exactly_one_file_models_the_real_cli_line()`:

```python
    case_no_bare_rendered_count_substring_outside_the_helper()
```

## Acceptance evidence

### A. Per-call-site mutation proof (the point of this dispatch)

**Site 1 (original line 334, current 335 after the `ast` import shift):**
mutated to `"1 file(s)" in r.stderr, r.stderr)`.

```
FAIL no bare rendered-count substring compare outside reports_exactly_one_file offending line(s): [335]
1 FAILURE(S): ['no bare rendered-count substring compare outside reports_exactly_one_file']
```
Restored by hand; re-run: `ALL PASS`, exit 0. `diff pre_mutation.diff post1.diff` → empty (`DIFF_IDENTICAL`).

**Site 2 (original 359, current 360), negative predicate:**
mutated to `"1 file(s)" not in r.stderr, r.stderr)`.

```
FAIL case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (scans the real repo root, not the tmp fixture with its single file) ...
FAIL no bare rendered-count substring compare outside reports_exactly_one_file offending line(s): [360]
2 FAILURE(S): [...]
```
(This mutation ALSO breaks the existing case itself, because `"1 file(s)"` is a substring
of `"41 file(s)"` — exactly the fail-open shape this whole guard exists to prevent — and
the new guard independently names the same regression at the source level.)
Restored by hand; re-run: `ALL PASS`, exit 0. `diff pre_mutation.diff post2.diff` → empty.

**Site 3 (original 370, current 371):**
mutated to `"1 file(s)" in r2.stderr, r2.stderr)`.

```
FAIL no bare rendered-count substring compare outside reports_exactly_one_file offending line(s): [371]
1 FAILURE(S): ['no bare rendered-count substring compare outside reports_exactly_one_file']
```
Restored by hand; re-run: `ALL PASS`, exit 0. `diff pre_mutation.diff post3.diff` → empty.

### B. Helper-level mutation still caught

`reports_exactly_one_file` body reverted to `return "1 file(s)" in stderr_text`:

```
FAIL case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (...)
FAIL control: rejects 41 file(s)
FAIL control: rejects 21 file(s)
FAIL control: rejects 11 file(s)
FAIL control: rejects the real 41 file(s) scanning line (this is the exact fail-open shape the redirected-root bug renders)
FAIL control: rejects the real 101 file(s) scanning line
FAIL no bare rendered-count substring compare outside reports_exactly_one_file offending line(s): [46]
7 FAILURE(S): [...]
```
Restored by hand; re-run: `ALL PASS`, exit 0. `diff pre_mutation.diff postB.diff` → empty.

### C. Guard does not over-fire

Green run includes, by name:
```
PASS cli_invalid_file_stderr_names_branch          (line 241: "'branch'" in r.stderr)
PASS cli_jsonschema_unavailable_stderr_names_required  (line 260: "REQUIRED" in r.stderr)
PASS case_migrated_depth: the scanning line names the migrated glob  (line 336: ".harness/*/features/" in r.stderr)
```
None of these three fires the AST rule: their `Compare.left` values are `"'branch'"`,
`"REQUIRED"`, and `".harness/*/features/"` — none matches `re.fullmatch(r"\d+ file\(s\)", ...)`,
so the rule structurally cannot match them (verified by inspection of the rule and by these
three passing in every green run above, including after all four mutation rounds were
restored).

### D. Grep checks

```
$ grep -Fc 'r"\b1 file\(s\)"' .claude/skills/harness/bin/test-validate-feature-json.py
1
$ grep -n '"1 file(s)" in' .claude/skills/harness/bin/test-validate-feature-json.py
(no output)
$ echo $?
1
```

### E. Full test file, final state

```
$ python3 .claude/skills/harness/bin/test-validate-feature-json.py
... [74 PASS lines including the new guard] ...
     (red proof counts: original 1, mutant 0)

ALL PASS
$ echo $?
0
```

### F. Unit test suite

```
$ HARNESS_PROJECT_DIR="$PWD" bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit
... PASS test-gate-policy.py [last of the run] ...
$ echo $?
0
```

### G. Self-grade of `code_grade.py`

```
$ python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/code_grade.py
...
PASSING: 53
```
No `RESULT: FAIL` line.

### H. Grade of the modified test file

```
QUALNAME: _rendered_count_substring_compares         GRADE: 3   BAR: 3   RESULT: PASS
QUALNAME: case_no_bare_rendered_count_substring_outside_the_helper   GRADE: 5   BAR: 3   RESULT: PASS
...
PASSING: 47
```
Only two `RESULT: FAIL` lines remain, both pre-existing:
```
QUALNAME: case_t15_red   RESULT: FAIL   SEVERITY: med
QUALNAME: main           RESULT: FAIL   SEVERITY: med
```
No new failing function introduced; no allowlist entry added.

### I. Worktree git state

```
$ git -C <worktree> diff --stat
 .../harness/bin/test-validate-feature-json.py      | 92 +++++++++++++++++++++-
 .../FEAT-43-code-risk-grading/feature.json         |  4 +-
 2 files changed, 91 insertions(+), 5 deletions(-)
$ git -C <worktree> status --porcelain
 M .claude/skills/harness/bin/test-validate-feature-json.py
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q13-cycle-29-substring-gate.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-2026-08-30-03-validate-substring-c29-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-2026-08-30-03-validate-substring-c29-positives.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-substring-c29.md
$ git -C <worktree> rev-parse HEAD
f9a4233c47fced65c2a7eb63ff3949884b65ccdb
```
Only the test file is attributable to this dispatch. The `feature.json` cycle 28→29 hunk
and the untracked answers/receipts are prior sibling work, not mine.

### J. Main checkout

```
$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/
?? .harness/harness/features/FEAT-43-code-risk-grading/
?? .harness/harness/features/FEAT-44-omp-context-advisory/
?? .harness/harness/features/PR-922-omp-supervision/
?? .harness/logs/2026-08-25.md
?? .harness/logs/2026-08-29.md
?? .harness/notes/... (five more untracked notes)
```
No `M` (tracked-modified) lines — no tracked modification, only pre-existing untracked
scratch files unrelated to this dispatch.

## Task / verify

No PLAN `T-NN` task id was carried in this dispatch (it is a targeted lead-directed guard
addition, not a plan task); the acceptance criteria above ARE the verify command set and
all were run and quoted above.
