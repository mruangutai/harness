# Receipt — harness-backend-dev — FEAT-43 wave 2, CLI-owned files

Task: T-03 (CLI surface, exit statuses, report fields) + T-08 (grade-as-finding cutover), REQ-11,
SC-14, SC-17. Files owned and edited: `.claude/skills/harness/bin/code-grade.py`,
`.claude/skills/harness/bin/test-code-grade-cli.py`, `.claude/skills/harness-code-review/SKILL.md`.

## Item A — CR-02 + UI-01: bar-relative severity, one vocabulary

Root cause: `_record`'s severity was a literal `{1: "high", 2: "med"}` map, blind to `bar`, so a
gated below-bar grade-3 PRODUCTION record (blocks via `_status`) printed no `SEVERITY:` line and
JSON `"severity": null`. `harness-code-review/SKILL.md` named only grades 1 and 2, so a reviewer
following it to the letter could not discover the grade-3 blocking case.

Fix, test-first:
- Added `_blocks(grade, bar) = grade < bar and grade != 2` — the exact predicate `_status` already
  used, now shared. `_status` refactored to call it (semantics unchanged; same boolean expression).
- Added `_severity(grade, bar)`: `"high"` when `_blocks`, else `"med"` when `grade == 2`, else
  `None`. Bar-relative, not grade-literal — verified by mutation (below).
- `_record` now computes `severity = _severity(grade.grade, bar)`.
- `harness-code-review/SKILL.md:63-71` rewritten: every blocking gated record (below bar, not
  grade 2) gets a **high** finding and `code_grade: fail`; explicitly states this is not only grade
  1 ("not grade 2" — the phrase a new test binds against); grade-2 stays **med** /
  `code_grade: grade_2`.

RED confirmed before the fix (`test-code-grade-cli.py`):
```
FAIL src/grade-three.py bar-relative severity present: expected True, got False
FAIL src/grade-three.py JSON bar-relative severity: expected 'high', got None
```
New named cases added to `test_bars_follow_test_kinds`: `src/grade-three.py` (production grade 3,
bar 4, blocks) now asserted `SEVERITY: high` / `"severity": "high"`; `checks/grade-three.py` (test
kind, grade 3, bar 3, passes) asserted **no** `SEVERITY:` line / `"severity": null` — this is the
bar-relative discriminator. Grade-4 (no severity) and grade-2 (`med`, unchanged) also asserted per
row. New `test_review_skill_states_severity_vocabulary()` reads the real
`harness-code-review/SKILL.md` and asserts on `SEVERITY: high`, `code_grade: fail`, `not grade 2`,
`code_grade: grade_2` verbatim, binding the guidance text so the three surfaces cannot drift.

## Item B — CR-01, CLI half: `_diff_paths` complexity

`_diff_paths` (grade 3, driver cognitive) was the sixth of six grade-3 production functions failing
the tool's own bar. Extracted three cohesive helpers along the `-z --name-status` parse seam:
`_run_name_status_diff` (subprocess call + error), `_name_status_entries` (generator: rename/copy
double-field consumption), `_is_changed_python` (deletion/`.py`-suffix predicate). `_diff_paths` now
composes them with a one-line filtered `sorted(...)`. Behaviour identical: same sorted path list,
same `ValueError` on non-zero git status, same `surrogateescape` decoding, same deletion/rename
handling — proven by the unchanged `test_diff_and_determinism` (including the git-wrapper enumeration
and cross-cwd cases) staying green, and by the mutation proof below.

RED confirmed before refactor — new `test_diff_paths_complexity()` graded the shipped
`code-grade.py` in paths mode through the `code_grade` API and asserted `grade >= 4` per qualname;
`_diff_paths` failed (`grade 3`) and the not-yet-existing helper names failed presence.

## Verification run and reported

- **Paths mode**, `code-grade.py` graded against itself — quoted per qualname (`GRADE:` line):
  `_blocks 5`, `_severity 5`, `_record 5`, `_run_name_status_diff 5`, `_name_status_entries 4`,
  `_is_changed_python 5`, `_diff_paths 5`, `_status 5`. All modified/added functions ≥ 4. (Exit
  status of this paths-mode run not used as acceptance — pre-existing `main` at grade 2 is untouched
  and out of scope; correctly still surfaces `SEVERITY: med` / `REASON REQUIRED: main`.)
- `python3 .claude/skills/harness/bin/test-code-grade-cli.py` → `PASS test-code-grade-cli`, exit 0.
  Named cases still green: SC-14 pair (`REASON REQUIRED: grade_two` present for the gated grade-2
  path; `"REASON REQUIRED" in clean.stdout` is `False` for the test-kind grade-3 pass path), and
  SC-17's four `test_bars_follow_test_kinds` boundary discriminators (`src/grade-four.py` grade 4/
  bar 4 PASS, `src/grade-three.py` grade 3/bar 4 FAIL, `checks/grade-three.py` grade 3/bar 3 PASS,
  `checks/grade-two.py` grade 2/bar 3 FAIL) — each now additionally carries the bar-relative severity
  assertion.
- `python3 .claude/skills/harness/bin/sync-agent-adapters.py --check` → exit 0, no drift (T-05's
  verify: line, required because `harness-code-review/SKILL.md` is adapter-mirrored).

## Mutation proofs (both restored byte-identical, confirmed via `md5sum` + `git status --porcelain`)

1. **Severity mutation** — changed `_severity` from `_blocks(grade, bar)` to a grade-literal
   `grade == 1` check. Caught by exactly the bar-relative discriminator:
   `FAIL src/grade-three.py bar-relative severity present` and
   `FAIL src/grade-three.py JSON bar-relative severity`. A grade-literal fix does NOT leave every
   test green — confirms the tests bind the acceptance, not just the happy path.
2. **`_diff_paths` helper mutation** — dropped the deletion-filter branch in `_is_changed_python`
   (`return path.endswith(".py")` only). Caught by
   `FAIL deleted file never ungraded: expected False, got True` plus three cascading failures in
   `test_diff_and_determinism`.

Restore verified both times: `md5sum` of the restored file matched the known-good snapshot exactly,
and `git status --porcelain` showed only the legitimate cumulative diff against the pin (no residual
mutation artifact).

## Constraints honored

- `_status` exit-status semantics (0/1/2/3 and their triggers) unchanged — same boolean expression,
  now shared via `_blocks`.
- No signature, message string, or report field name removed/renamed. `_record`'s dict shape,
  `_text`'s line labels, and the JSON keys are unchanged.
- `code_grade` enum untouched (`{pass, fail, grade_2, n_a}`) — did not touch `validate-digest.py`.
- Ran only my own three named-file checks; never touched `code_grade.py`, `gate_policy.py`,
  `check-plan-routes.py`, `.harness/harness.json`, or any sibling's test file. Never ran range-mode
  `--base/--head` grading of files a sibling may be mid-editing.
- One incident: mid-mutation-proof I ran `git checkout -- code-grade.py` intending to restore my own
  edit, which instead reverted the file to the pin (HEAD), discarding my legitimate refactor. Caught
  immediately by re-reading the file; redid the three edits from scratch, re-verified GREEN, then
  redid both mutation proofs using file-snapshot restore (`cp`/`write`, never `git checkout`) as
  specified. Working tree is uncommitted; HEAD was never moved.
- No scratch files left (`/tmp/code-grade-good.py` removed after use).

```yaml
VERDICT: PASS
DIGEST:
  headline: gated below-bar non-grade-2 records now surface SEVERITY:high/code_grade:fail in text, JSON and reviewer guidance, and _diff_paths plus its extracted helpers all grade 4 or better
  tests_added: 6
  suite: pass
  task: T-03
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .claude/skills/harness/bin/code-grade.py
    - .claude/skills/harness/bin/test-code-grade-cli.py
    - .claude/skills/harness-code-review/SKILL.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s2.md
```
