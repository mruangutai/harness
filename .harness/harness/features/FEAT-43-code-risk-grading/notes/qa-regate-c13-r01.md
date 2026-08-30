# QA re-gate — FEAT-43 code risk grading, post R-01 (SIMPLIFY finding)

**Result: PASS.** Both configured active kinds re-run at or above baseline with non-vacuous
binding to all seven changed files. The independently re-run mutation on `commit_oid`'s
leading-`-` guard fails a named assertion in `test-validate-digest.py`, proving the negative
test is live; the source was restored byte-identical (md5 match + identical `git diff --stat`)
and both suites re-verified green afterward.

## Change type

`cross_module` — `code_grade.commit_oid` is now the single seam three independent call sites
(`code-grade.py` CLI base/head args, `validate-digest.py:resolve_reviewed_commit`) route through;
a defect in the seam propagates across module boundaries. Matrix requires `unit` + `integration`
for `cross_module`; both are configured active, neither added beyond the floor.

## Per-kind table

| kind | required/added | command (verbatim) | state | count |
|---|---|---|---|---|
| unit | required (matrix: cross_module.always) | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | satisfied | 29/29 scripts pass, 0 fail, exit 0 |
| integration | required (matrix: cross_module.always) | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | satisfied | 28/28 scripts pass, 0 fail, exit 0 |
| functional | excluded (DEC-187, `cmd: null`) | n/a | excluded-with-signature (soft skip, not blocked, not passed) | n/a |

Baseline was unit 29/29, integration 28/28 — reproduced exactly, no regression. Raw run logs:
`/tmp/qa_unit_full.log` (1443 lines), `/tmp/qa_integration_full.log` (1906 lines) — full,
un-elided captures via redirected file (the hub-relayed console output silently elides long
runs mid-stream; do not trust script counts read off the hub transcript, only off a file).

Script-level count method: `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays in `run-unit-tests.sh`
hold 29 and 28 entries respectively (drift-checked against `harness.json`
`test_kinds.integration.detect` on every invocation — that check ran and passed both times,
silently, as part of the script's own preamble). Grepping `^PASS test-*.py$` and de-duplicating
(some suites print an internal test case whose name happens to start `PASS test-<file>`, e.g.
`test-code-grade.py`'s own case named `PASS test-code-grade` and
`test-code-grade-cli.py`'s case `PASS test-code-grade-cli`) gives the true unique script
counts: 29 unit, 28 integration. Zero `^FAIL test-` lines in either run.

## Seven-file discovery audit

| file | kind | binding |
|---|---|---|
| `code_grade.py` | unit | `test-code-grade.py` loads it via `importlib.util.spec_from_file_location("code_grade", …/code_grade.py)` (line 12) and exercises `commit_oid` and grading directly (24 references) |
| `code-grade.py` | integration | `test-code-grade-cli.py` — `SCRIPT = Path(__file__).with_name("code-grade.py")`, subprocess-contract tests (11 references); also loaded by `test-code-grade.py` as `code_grade_cli` for in-process checks |
| `validate-digest.py` | integration | `test-validate-digest.py` loads it via `importlib.util.spec_from_file_location("_validator_under_test", VALIDATE)` (line 1838) and directly calls `resolve_reviewed_commit` (12 references incl. `check_resolve_reviewed_commit_guard`) |
| `test-code-grade.py` | unit (is the test) | self — ran as `test-code-grade.py`, PASS |
| `test-code-grade-cli.py` | integration (is the test) | self — ran as `test-code-grade-cli.py`, PASS |
| `test-validate-digest.py` | integration (is the test) | self — ran as `test-validate-digest.py`, PASS, includes the new `check_resolve_reviewed_commit_guard` |
| `test-check-plan-routes.py` | integration (is the test) | self — ran as `test-check-plan-routes.py`, PASS. Diff here is unrelated to the R-01 seam: pure helper extraction inside `case_27` (`_owner_branch`, `_case_27_owner_manifest`, `_case_27_unreadable`), zero `code_grade`/`code-grade` references (`grep -c` = 0). Its own suite running green is its coverage; nothing else in the diff calls into it. |

No file lacks binding coverage.

## R-01 seam checks (executed, not read)

1. **`commit_oid` reached from all three call paths** — confirmed by grep + read:
   `code-grade.py:162` (`code_grade.commit_oid(root, args.base)`), `code-grade.py:163`
   (`…args.head`), `validate-digest.py:544` (`commit_oid(".", revision)` inside
   `resolve_reviewed_commit`). All three are exercised by the suites above (satisfied, not
   merely present).

2. **`code-grade.py` exit 2 + exact message** — ran directly in the worktree:
   ```
   $ python3 .claude/skills/harness/bin/code-grade.py --base zzzznotarealrev --head HEAD
   usage: code-grade.py [-h] [--base BASE] [--head HEAD] [--json] [paths ...]
   code-grade.py: error: invalid Git commit revision: zzzznotarealrev
   EXIT=2

   $ TREE_OID=$(git rev-parse HEAD^{tree})   # 69e159a7fe88bbb7ff9d8b655df15deaa74d8d17
   $ python3 .claude/skills/harness/bin/code-grade.py --base "$TREE_OID" --head HEAD
   usage: code-grade.py [-h] [--base BASE] [--head HEAD] [--json] [paths ...]
   code-grade.py: error: invalid Git commit revision: 69e159a7fe88bbb7ff9d8b655df15deaa74d8d17
   EXIT=2
   ```
   Both the bogus revision and the non-commit (tree) OID exit 2 with the exact required message.

3. **`resolve_reviewed_commit` returns `None`, not a raise; returns `bytes` on success** —
   loaded `validate-digest.py` via `importlib.util` and called it directly:
   ```
   >>> m.resolve_reviewed_commit('zzzznotarealrev')
   unresolvable -> None <class 'NoneType'>
   >>> m.resolve_reviewed_commit('HEAD')
   HEAD -> <class 'bytes'> 40 b'e5024ae24e'
   ```
   No exception on the unresolvable case; `HEAD` resolves to a 40-byte hex OID as `bytes`, so
   `reviewed_python_change`'s byte-string contract is unaffected.

## Independent mutation re-proof (self-executed, not taken on the eng-lead's report)

- md5 of `code_grade.py` **before**: `41c52c1ed215897a6ebd60606af5489a`
- Mutation applied: line 282 changed from
  `if not isinstance(revision, str) or revision.startswith("-"):` to
  `if not isinstance(revision, str):` (removed the leading-`-` guard).
- md5 of `code_grade.py` **after mutation**: `d76626b957580fd4b430136f6a4c54d0` (confirms the
  mutation actually changed bytes on disk).
- Ran `python3 test-validate-digest.py` against the mutant. Real exit code (measured
  directly, not through a pipe): `REAL_EXIT=1`.
- **Exact failing assertion, quoted verbatim from the run:**
  ```
  FAIL  code-grade and review-policy gates
        option-like revision must not invoke Git at all
  1 FAILING.
  ```
  This is `check_resolve_reviewed_commit_guard`'s second assertion: with the `-` guard gone,
  `commit_oid("--upload-pack=touch /tmp/pwned")` falls through to `subprocess.run`, and the
  traced call list is non-empty. The test is not vacuous.
- Restored `code_grade.py` from the pre-mutation copy. md5 **after restore**:
  `41c52c1ed215897a6ebd60606af5489a` — matches the pre-mutation md5 exactly.
- `git -C <worktree> diff --stat -- .claude/skills/harness/bin/code_grade.py` after restore:
  `26 ++++++++++++++++++++++----  |  1 file changed, 22 insertions(+), 4 deletions(-)` —
  identical to the diff stat recorded before the mutation was applied. Byte-identical restore
  proven two ways, as required.
- Re-ran both suites green after restoring:
  - unit: `UNIT_EXIT=0`, 29/29 scripts pass, 0 fail (`/tmp/qa_unit_postrestore.log`)
  - integration: `INTEGRATION_EXIT=0`, 28/28 scripts pass, 0 fail (`/tmp/qa_integration_postrestore.log`)

## `git status --short` at the end

```
 M .claude/skills/harness/bin/code-grade.py
 M .claude/skills/harness/bin/code_grade.py
 M .claude/skills/harness/bin/test-check-plan-routes.py
 M .claude/skills/harness/bin/test-code-grade-cli.py
 M .claude/skills/harness/bin/test-code-grade.py
 M .claude/skills/harness/bin/test-validate-digest.py
 M .claude/skills/harness/bin/validate-digest.py
 M .harness/harness/features/FEAT-43-code-risk-grading/STATE.md
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
 M .harness/harness/features/FEAT-43-code-risk-grading/notes/handoff-validate.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q2-cycle-11-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q3-cycle-13-overrun.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q4-simplify-routing.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q5-simplify-apply-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-validate-fix-c13-qa-validator.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-efficiency-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-reuse-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c11.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c13-r01.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-altitude-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplification-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.html
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.md
```

Exactly the seven modified source/test files under test remain modified, unrelated feature
bookkeeping unchanged, nothing staged.

## Phase 1 vs Phase 2 (anti-bias note)

Phase 1 (BRIEF/plan-only, before reading the diff) expected: unit + integration coverage on
whatever module resolves a reviewed commit revision to an OID, a CLI-level negative test for a
bogus/non-commit revision, and a negative test proving an option-like (`-`-prefixed) revision
is rejected before shelling out to Git. All three are present in the diff (`test-code-grade.py`,
`test-code-grade-cli.py`, `test-validate-digest.py:check_resolve_reviewed_commit_guard`) — no
gap between what was expected and what exists.
