# Receipt — harness-backend-dev — validate-remediate-c14-eng-s5

Task: T-09 (consolidated verification's `case_20_validate_digest_py_probes_the_manifest`
false positive). File owned: `.claude/skills/harness/bin/test-check-plan-routes.py`.

## A. RED — reproduce before fixing

`python3 .claude/skills/harness/bin/test-check-plan-routes.py` before any change:

```
1 FAILURE(S): ['case_20_validate_digest_py_probes_the_manifest']
```

Mechanism reproduced in isolation (fifth-draft's `logical_lines`, run standalone over
`validate-digest.py`): the naive `depth += raw.count("(") + raw.count("[") - raw.count(")")
- raw.count("]")` counter goes positive at physical line 283 —
`_QUOTE_STARTS_AFTER = set(",:[{ \t") | {None}` — and never recovers. Measured: the
resulting "logical line" starts at physical line 283 and is **48,393 characters** long
(matches the assignment's own figure exactly). `validate-digest.py` has **zero** real root
probes — confirmed none of the six PREDICATES (`os.access(`, `os.path.isdir(`,
`os.path.isfile(`, `os.path.exists(`, `os.stat(`, `Path(`) occurs anywhere in that file.
This was a false positive in the joiner, not a defect in `validate-digest.py`.

## B. The fix

`logical_lines(text, is_python)` now dispatches: `.py` sources route through
`_logical_lines_python`, built on `tokenize.generate_tokens` (Python's own lexer — a
bracket inside a STRING or COMMENT token never touches bracket depth, because it's never
seen as a bare `(`/`[`/`)`/`]` token). `.sh` sources keep the prior draft's bracket-count
joiner (`_logical_lines_shell`) **unchanged**.

**Why `.sh` is scoped out of tokenize, not exempted from scanning:** bin/ holds real POSIX
shell (`branch-create-gate.sh`, `check-expertise.sh`, `dispatch-guard.sh`,
`inject-expertise.sh`, `run-unit-tests.sh`) alongside bash-shebanged files that are
Python inside a heredoc (`check-domain.sh`). Measured directly: feeding all 11 `*.sh`
files in `bin/` through Python's tokenizer, **5 of 11 raise `tokenize.TokenError`** on
ordinary, correct bash (heredocs, ANSI-C quoting) that has nothing to do with a root
probe — forcing tokenize onto them would turn five clean files red for the wrong reason.
Every `.sh`/`.py` file is still scanned; only the parser choice is file-type-aware. This
is a parser-selection decision, not a coded exemption — no file was added to any skip
list, and `logical_lines`'s external contract (joined logical lines as single-line
strings) is unchanged.

**Tokenizer failure is loud, never silent.** `_scan_file` catches
`(tokenize.TokenError, SyntaxError)` around the `.py` path only and returns `("error",
detail)`; `_report_scan_result` turns that into a **failing** `check(f"case_20_{key}_tokenizes",
False, ...)`, not a silent `continue`. Verified none of the `.py` files in `bin/` actually
hit this path today (all 41 non-`test-*.py` files there tokenize cleanly, including
`validate-digest.py` itself — the bug was in bracket-depth counting, not lexability).

**No newly revealed real violation.** Running the corrected joiner over every `.py`/`.sh`
file in `bin/` produces the same two matching files as before (`board-station.py`,
`gh-sync.py`), both still naming `team-config.yaml` (`disagree == []` for both). No file
newly appears with a `.harness` probe missing `team-config.yaml`.

**Detector-not-blind guard.** `case_20_the_detector_is_not_blind` still requires
`seen_any >= 2`. After the fix `seen_any == 2` (validate-digest.py's false contribution is
gone; `board-station.py` and `gh-sync.py` remain) — passes, at the stated boundary.

## C. Direct unit assertion on `logical_lines` (binds the fix)

`_assert_logical_lines_fixture()` builds a 3-case fixture: (a) `A = set(",:[{ \t")` — a
bracket inside a string literal; (b) `# a stray unmatched bracket in a comment (` — a
bracket inside a comment; (c) a genuine multi-line `os.path.isdir(...)` call that must
still come back as one line. Asserts the exact expected joining:
`['A = set(",:[{ \\t")', 'B = 1', 'C = 2', 'result = os.path.isdir( os.path.join(derived, ".harness") )']`.
Registered as `check("case_20_logical_lines_is_string_and_comment_aware", ...)`, folded
into `case_20`'s return.

## D. Mutation proof

Snapshotted the fixed file to `/tmp/test-check-plan-routes.snapshot.py` (non-git). Mutated
`logical_lines`'s dispatcher to `return _logical_lines_shell(text)` unconditionally
(forcing the fifth-draft naive counter for every file, including `.py`). Re-ran the suite:

```
FAIL case_20_logical_lines_is_string_and_comment_aware expected [...], got
  ['A = set(",:[{ \\t") B = 1 # a stray unmatched bracket in a comment ( C = 2 result = os.path.isdir( os.path.join(derived, ".harness") )']
FAIL case_20_validate_digest_py_probes_the_manifest validate-digest.py: 1 of 1 root
  probe(s) do not name team-config.yaml -> [...]
2 FAILURE(S): ['case_20_logical_lines_is_string_and_comment_aware',
  'case_20_validate_digest_py_probes_the_manifest']
```

Both the false-positive regression and the new direct assertion fire, as required.
Restored from the snapshot: `md5sum` before mutation and after restore both
`77cff9d7d78cb2ebbe1075c4039c0ffb`; `git status --porcelain` after restore shows the file
back to its normal "modified" entry (no diff-of-diff, re-ran the full suite green
afterward — see section E).

## E. Grading — paths mode, `code-grade.py`

`.claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/test-check-plan-routes.py`.
`BAR: 3` confirmed from the tool's own output for every function in this test file (test
bar, not the source bar of 4). All new/modified qualnames grade at or above 3:

| qualname | cyclomatic | cognitive | ABC | grade | result |
|---|---|---|---|---|---|
| `case_20` | 2 | 1 | 13.3 | 4 | PASS |
| `case_20._logical_lines_shell` | 4 | 6 | 13.7 | 4 | PASS |
| `case_20._logical_lines_python` | 10 | 14 | 20.3 | 3 | PASS |
| `case_20.logical_lines` | 1 | 1 | 2.2 | 5 | PASS |
| `case_20._assert_logical_lines_fixture` | 1 | 0 | 3.7 | 5 | PASS |
| `case_20._scan_file` | 10 | 5 | 17.0 | 3 | PASS |
| `case_20._report_scan_result` | 2 | 1 | 6.4 | 5 | PASS |
| `case_20._scan_all_files` | 7 | 13 | 14.5 | 3 | PASS |

First attempt at the fix (a single flat `logical_lines` doing both dispatch and the
tokenize loop inline in `case_20`) graded `case_20` and `case_20.logical_lines` at grade 2
(FAIL) — decomposed into the 8 functions above to bring every one to grade ≥3. This is
the file's own second engineering pass within this dispatch, not a violation of the
3-attempt ceiling (the ceiling is for repair loops on a broken behavior; this was a
grading-bar pass on an already-correct, already-green fix).

Pre-existing debt, unrelated to this change, confirmed still present and NOT introduced by
me (functions I never touched): `case_18` (grade 2), `case_19` (grade 1), `case_22` (grade
2), `case_23` (grade 1), `case_24` (grade 1), `case_25` (grade 2), `case_26` (grade 1),
`_case_27_owner_manifest` (grade 2) — all `RESULT: FAIL` in the same run, all at line
numbers and function bodies I did not edit. Paths-mode overall exit status was not used as
acceptance, per instructions — only the per-qualname grades of functions I touched were.

## F. Five focused suites — final line + exit status

```
python3 .claude/skills/harness/bin/test-check-plan-routes.py  -> "ALL PASS"          exit 0
python3 .claude/skills/harness/bin/test-code-grade.py          -> "PASS test-code-grade"     exit 0
python3 .claude/skills/harness/bin/test-code-grade-cli.py      -> "PASS test-code-grade-cli"  exit 0
python3 .claude/skills/harness/bin/test-gate-policy.py         -> "ok    advisory QA always passes"  exit 0
python3 .claude/skills/harness/bin/test-validate-digest.py     -> "ALL PASSED."         exit 0
```

## G. `git status --porcelain` (worktree)

```
 M .claude/skills/harness-code-review/SKILL.md
 M .claude/skills/harness/bin/check-plan-routes.py
 M .claude/skills/harness/bin/code-grade.py
 M .claude/skills/harness/bin/code_grade.py
 M .claude/skills/harness/bin/gate_policy.py
 M .claude/skills/harness/bin/test-check-plan-routes.py
 M .claude/skills/harness/bin/test-code-grade-cli.py
 M .claude/skills/harness/bin/test-code-grade.py
 M .claude/skills/harness/bin/test-validate-digest.py
 M .claude/skills/harness/bin/validate-digest.py
 M .harness/harness/features/FEAT-43-code-risk-grading/STATE.md
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q6-cycle-20-remediation-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q7-cycle-25-preemptive-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s1.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s1b.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s2.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3b.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-validate-remediate-c14-eng-s4.md
```

Every entry other than `M .claude/skills/harness/bin/test-check-plan-routes.py` predates
this dispatch (sibling engineers' work, plan bookkeeping). My own receipt at this path is
the only new entry I add. `files_touched` below lists only what I wrote.

## H. HEAD commit facts (read-only, no action taken)

`git rev-parse HEAD` = `0666c01a07a844ceb4a2bdfa7504ce4ef74536fb`.

```
git log -1 --format='%H %ad %an %s' --date=iso 0666c01a07a844ceb4a2bdfa7504ce4ef74536fb
0666c01a07a844ceb4a2bdfa7504ce4ef74536fb 2026-08-28 16:51:54 -0700 Mike Ruangutai chore: record FEAT-43 final panel FAIL and the operator briefing
```

`git show --stat --oneline 0666c01a07a844ceb4a2bdfa7504ce4ef74536fb`: 27 files changed,
2384 insertions(+), 80 deletions(-), every path under
`.harness/harness/features/FEAT-43-code-risk-grading/` (STATE.md, feature.json, answers/,
notes/, ship-review artifacts) — no source file under `.claude/skills/harness/bin/` is
touched. Bookkeeping-only, as the dispatch stated; no source drift to reconcile.

## Acceptance checklist

- `logical_lines` is string- and comment-aware for `.py` via `tokenize`; no file added to
  any exemption list; nothing outside `test-check-plan-routes.py` was edited.
- Direct assertion on `logical_lines` covers bracket-in-string, bracket-in-comment, and a
  genuine multi-line join — binds the fix (section C, D).
- Tokenizer failure reported via a failing `check`, never swallowed (section B).
- `case_20_the_detector_is_not_blind` holds, `seen_any == 2` (section B).
- No newly revealed real violation (section B).
- All five focused suites exit 0 (section F).
- New/modified functions grade ≥3, the file's own bar (section E).
- Mutation proof with named failing cases, byte-identical non-git restore (section D).
- HEAD-commit facts reported verbatim, read-only (section H).
- Working tree uncommitted; no scratch files (`/tmp/test-check-plan-routes.snapshot.py`
  lives outside the repo and is not part of the worktree).
