# Receipt — harness-backend-dev — FEAT-43-code-risk-grading — validate-fix-c13-r01

## What changed

R-01 applied, and only R-01: `code_grade.py`'s commit resolver is now the single
implementation of commit resolution; the other two call sites became adapters over it.

- `.claude/skills/harness/bin/code_grade.py` — `_commit_oid` (line 281) promoted to the
  public seam `commit_oid(repo_root, revision)`, byte-for-byte identical body. Both internal
  callers in `gated_set` (lines 369-370) updated to the new name. `grep -r _commit_oid` across
  the whole worktree finds it nowhere left in source — the only remaining hit is the CLI file
  fixed in the same edit (below); every other hit is historical prose in
  `.harness/harness/features/FEAT-43-code-risk-grading/{STATE.md,notes/*}` that narrates the
  old name and is out of scope for this task.
- `.claude/skills/harness/bin/code-grade.py` — local `_commit_oid` (old lines 26-37) deleted
  entirely. `main` now calls `code_grade.commit_oid(root, args.base)` /
  `code_grade.commit_oid(root, args.head)` (new lines 162-163). The surrounding
  `except ValueError as error: parser.error(str(error))` is untouched, so CLI error text and
  exit status are unchanged. **One intentional behavior addition**: the deleted local copy
  lacked the `isinstance(revision, str)` guard the seam carries. That guard is strictly
  stronger and unreachable from `argparse` (which always yields `str`), so nothing
  CLI-observable changes — confirmed by the spot-checks below.
- `.claude/skills/harness/bin/validate-digest.py` — `resolve_reviewed_commit` (line 541) is
  now a five-line adapter: `commit_oid(".", revision).encode()`, `ValueError` caught and
  translated to `None`. Three hazards named in the dispatch, all handled:
  - **Name shadowing** avoided by `from code_grade import commit_oid` (added at line 32,
    beside the existing `sys.path.insert` block), not `import code_grade` — the local
    variable `code_grade = seen.get("code_grade")` at line ~767 of `validate()` is untouched
    and does not collide with a module binding.
  - **cwd semantics** preserved exactly: the old code ran `git rev-parse` with no `-C`
    (resolves against process cwd); the adapter passes `"."` as `repo_root`, and
    `commit_oid` builds `git -C .`, which is the same resolution target.
  - **bytes vs str** preserved: the seam returns `str`; the adapter `.encode()`s it back to
    `bytes` before returning, so `reviewed_python_change`'s two consumers (the `git diff`
    argv at lines 560-561, which already mixed bytes oids with str argv elements in the
    pre-existing code, and the `.py` check at line 566, which tests the diff's own stdout,
    not these values) see no type change. No caller or test depends on `bytes` beyond argv
    positioning, so nothing else needed to change.
  - `reviewed_python_change`'s "reviewed range could not be resolved to commit revisions."
    message is unchanged — still reached whenever either resolution returns `None`.

## TDD (Step 0)

The one genuinely new observable behavior: an option-like revision (leading `-`) is now
rejected by `resolve_reviewed_commit` **before Git is ever invoked**, not merely resolved to
a Git error. The pre-existing `check_reviewed_range` test only proved the *result* (`None`)
via the `--end-of-options` trick, which already made Git itself refuse the value — it never
asserted Git was *not run*.

Added `check_resolve_reviewed_commit_guard` to `test-validate-digest.py` (new lines
1798-1819), wired into `run_code_grade_cases` (new line 1847). It traces
`validator.subprocess.run` and asserts both `result is None` and `calls == []` for
`resolve_reviewed_commit("--upload-pack=touch /tmp/pwned")`.

**RED, run against the unmodified code** (`python3 .claude/skills/harness/bin/test-validate-digest.py`):

```
FAIL  code-grade and review-policy gates
        option-like revision must not invoke Git at all
...
1 FAILING.
```

**GREEN after steps 1-3 applied** (same command): `ALL PASSED.`, exit 0.

## Verification — real counts, run from the worktree root

```
$ python3 .claude/skills/harness/bin/test-code-grade.py
PASS test-code-grade
exit=0
```

```
$ python3 .claude/skills/harness/bin/test-code-grade-cli.py
PASS test-code-grade-cli
exit=0
```

```
$ python3 .claude/skills/harness/bin/test-validate-digest.py
...
14/14 hook cases passed.
...
24/24 T-09 cases passed.
...
2/2 template cases passed.

ALL PASSED.
exit=0
```
(`grep -c '^ok'` on the full output: 107; `grep -c '^FAIL'`: 0.)

## Acceptance — single implementation

`grep -r -- "--end-of-options"` across `.claude/skills/harness/bin/` returns exactly one Git
invocation, in `code_grade.py:285`. The other three hits are: an assertion string in
`test-code-grade-cli.py:158`, an assertion string in `test-code-grade.py:177`, and a docstring
sentence in `test-validate-digest.py:1801` — none of them invoke Git.

## Behavioral spot-check (run against the fixed CLI)

```
$ python3 .claude/skills/harness/bin/code-grade.py --base bogus-revision-xyz --head HEAD
usage: code-grade.py [-h] [--base BASE] [--head HEAD] [--json] [paths ...]
code-grade.py: error: invalid Git commit revision: bogus-revision-xyz
exit=2

$ python3 .claude/skills/harness/bin/code-grade.py --base "$(git rev-parse HEAD^{tree})" --head HEAD
usage: code-grade.py [-h] [--base BASE] [--head HEAD] [--json] [paths ...]
code-grade.py: error: invalid Git commit revision: 69e159a7fe88bbb7ff9d8b655df15deaa74d8d17
exit=2
```

Both a bogus revision and a resolvable-but-non-commit revision (a tree OID) fail the same
way: same error text shape, same exit code 2 (`parser.error` unconditionally exits 2). Commit-only
resolution (the `^{commit}` peel) is intact.

## Working tree

`git -C <worktree> status --short` under `.claude/skills/harness/bin/` still shows exactly the
same seven modified files as before this task (`code-grade.py`, `code_grade.py`,
`test-check-plan-routes.py`, `test-code-grade-cli.py`, `test-code-grade.py`,
`test-validate-digest.py`, `validate-digest.py`) — I touched four of the seven
(`code-grade.py`, `code_grade.py`, `validate-digest.py`, `test-validate-digest.py`); the other
three were already modified by prior B-01..B-08 remediation and I left them untouched. No new
source file was created, nothing is staged (`staged 0`), and no commit was made.

## Scope notes

- Historical narrative files under `.harness/harness/features/FEAT-43-code-risk-grading/{STATE.md,notes/*}`
  still say `_commit_oid` by name — that is prior-cycle prose describing what existed at the
  time it was written, not source, and rewriting it is out of scope for a one-fix ceiling.
- No other SIMPLIFY finding, B-01..B-08 remediation, or unrelated issue was touched.
- Not committed, not staged, per the constraint that the orchestrator holds the commit pen.

## Behavior other than internal structure

None. Every named contract clause holds: commit-only resolution (`^{commit}` peel) is
unchanged; `--end-of-options` still guards the sole Git invocation; option-like revisions are
still rejected — now provably before Git is invoked, which is a strictly *earlier* rejection
point with an identical outward result (`ValueError` / `None`), not a new outward failure
mode; `code-grade.py`'s `ValueError`-driven CLI error text and exit status are byte-identical;
`validate-digest.py:resolve_reviewed_commit` still returns `None` on any failure and still
feeds the same "reviewed range could not be resolved to commit revisions." message.
