# Review — BUG-1055-code-grade-absent-path — code — c0

**Verdict: PASS.** Stage 1 (spec compliance) and Stage 2 (quality) both clear. One `low`
advisory note, no `must_fix`. `code-grade.py --base 9f2a070 --head e353c7e` reports
`PASSING: 3`, zero `SEVERITY:` lines — `_tree_has_path` grade 5, `check_base_source_absent_from_worktree`
grade 3, `test_absent_new_path_grades_the_range` grade 4.

## Stage 1 — spec compliance

Spec = `issue://1055` + `notes/handoff-plan.md` (written pre-implementation at 9f2a070; no
BRIEF/plan.yaml, per the BUG precedent already ruled). File set confirmed via
`git diff --stat 9f2a070..e353c7e`: `code_grade.py`, `test-code-grade.py`,
`test-code-grade-cli.py`, plus `feature.json`/`notes/handoff-plan.md` (spec records, not
logic) — matches the dispatch's expected set exactly, no extra files.

- Every line of the `code_grade.py` diff serves the one decided fix: delete the
  English-message match (`"exists on disk, but not in" in result.stderr`), replace with the
  structural `git ls-tree --name-only -z` probe the plan's "Dead ends" section names as the
  correct discriminator (absence ⇒ exit 0 + empty; failure ⇒ non-zero). No scope creep.
- Both explicitly-named dead ends were avoided: no second string match added
  (`code_grade.py:334` has zero `in result.stderr` calls left), and `code-grade.py` (the CLI
  entry point, unchanged in this diff) still has no `except RuntimeError` — a real failure
  still crashes loudly rather than being swallowed into a clean exit.
- Test-first, both matrix kinds present: `check_base_source_absent_from_worktree` (unit,
  `test-code-grade.py:454`) and `test_absent_new_path_grades_the_range` (integration,
  `test-code-grade-cli.py:290`), matching the plan's stated `unit` + bug-class `integration`
  requirement.
- **RED-before-fix independently reproduced** (not taken on the plan's word): copied the
  pre-fix `code_grade.py`@9f2a070 into a scratch dir alongside the new e353c7e test files and
  ran them unmodified.
  - Unit: crashes with `RuntimeError: fatal: path 'added.py' does not exist in '<oid>'` at
    the old `code_grade.py:323` (`raise RuntimeError(result.stderr.strip())`) — matches the
    ticket's exact defect.
  - Integration: 3 of 4 assertions fail against the old code — `"no crash…" expected False,
    got True`, `"the masked finding is reported" expected True, got False` — i.e. the crash
    happens and it swallows the later `added_risky` finding, precisely the masking behaviour
    the ticket describes.
- **GREEN-after-fix and masking restored end-to-end, run directly in the worktree** (not
  inferred from the CI claim of 473/588 passing): `python3 test-code-grade.py` →
  `PASS test-code-grade`; `python3 test-code-grade-cli.py` → `PASS test-code-grade-cli`.
  `test_absent_new_path_grades_the_range` is the concrete masking-restoration proof: commits
  `added_clean.py` (fine) then `added_risky.py` (21-clause `and` chain, gate-failing) at
  head, `git rm`s both so they are absent from the worktree, grades the historical range, and
  the CLI now reports `QUALNAME: added_risky` / `RESULT: FAIL` / exit 1 instead of crashing
  before reaching it — sorted-order masking is fixed, verified by execution.

## Stage 2 — quality, fail-open hunt

**Central question — is `_tree_has_path` fail-open anywhere?** Built a scratch repo (pure
`git`/`subprocess` plumbing, no working-tree writes needed) and ran the actual
`git --literal-pathspecs ls-tree --name-only -z <ref> -- <path>` invocation the code uses,
against every case the dispatch named. All verified by execution, not by reading:

| Case | Result | Fail-open? |
|---|---|---|
| Bad/ambiguous ref | `ls-tree` exits 128, `_tree_has_path` raises | No |
| Ref resolves to a blob, not a tree | `ls-tree` exits 128 (`not a tree object`) → raises | No |
| Corrupt blob object (target file's own object corrupted) | `git show` fails; `ls-tree` reads the **tree**, not the blob, succeeds non-empty → `_tree_has_path` = True → original `git show` error re-raised, unmasked | No |
| Corrupt tree object | Both `git show` and `ls-tree` fail identically (`invalid object type`) → raises | No |
| Blob unreadable (permission-denied loose object, tree intact) | `git show` fails (`bad object`); `ls-tree` still lists the entry from the tree → `_tree_has_path` = True → original error re-raised | No |
| Submodule gitlink path | `git show` fails (`bad object`, gitlink isn't a blob); `ls-tree` lists it (mode 160000 entry) → `_tree_has_path` = True → original error re-raised | No |
| Symlink entry | Both `show`/`ls-tree` succeed (symlink target content is itself a blob) — never reaches the probe | N/A |
| Path is a directory in the tree | `ls-tree` prints the dir name, non-empty (True) — moot anyway, `_changed_python_files` only ever yields blob paths from `git diff --name-status` | No |
| Path outside the repository | Both `show`/`ls-tree` reject with `fatal: … is outside repository` (128) → raises | No |
| Path with leading `./` | `ls-tree` normalizes and matches (`file.py`) regardless of `--literal-pathspecs` | No |

No scratch case produced a real error silently read as absence. `_tree_has_path` returning
`False` only ever occurred when the path was genuinely absent from the ref's tree.

**Pathspec handling (Q2).** `--literal-pathspecs` is passed to the `ls-tree` probe only —
`grep` confirms a single occurrence in the file, and it is correctly unneeded elsewhere
(`git show <ref>:<path>` doesn't use pathspec matching; `_changed_python_files`'s `git diff`
takes no `-- path` argument). Verified present-and-matched for glob metacharacters
(`*`, `?`, `[]`), a leading `:` and a leading `-`, and the suite's own tab+newline fixture
(`odd\told\nname.py`, exercised transitively by the pre-existing `check_nul_safe_changed_files`
rename test, which now flows through this same probe on its base-side miss). Also verified
the converse — a **genuinely absent** path containing those same metacharacters does not
false-positive match an unrelated sibling file (`star*.py` query against a tree holding
`starX.py`/`staractual.py`: empty, correctly absent).

**`--literal-pathspecs` is load-bearing, not decorative** — confirmed by omitting it in a
side-by-side scratch run: querying a tree that genuinely contains `:colon.py` for that exact
path *without* the flag returns **empty with exit 0** (git tries to parse `:colon.py` as
pathspec magic and it doesn't match) — that is precisely the fail-open class the ticket
fixes, reintroduced by dropping one flag. The shipped code includes it at
`code_grade.py:317`.

**`-z` / emptiness test.** `return bool(result.stdout.strip(b"\0"))` (`code_grade.py:323`) —
for a single match, stdout is `b"name\0"`; stripping the delimiter still leaves a non-empty
`bytes`, so `bool()` is `True`. Empty result is `b""` → `False`. No mismatch between the `-z`
terminator and the `strip(b"\0")` emptiness check.

**Cost (Q3).** Confirmed at source: `_tree_has_path` is only called from inside `_git_show`'s
non-zero-return branch (`code_grade.py:334`), so the happy path (path present, `git show`
succeeds) is exactly one subprocess call, unchanged. `gated_set`/`_resolve_base_source`
(`code_grade.py:400-404`) call `_git_show` once or twice (rename fallback, pre-existing
behaviour) — no new doubling.

**Error re-raise fidelity (Q4) — `low`, execution-verified.**
`code_grade.py:334-336`: when `_tree_has_path` returns `False` (genuine absence), the
original `git show` stderr is correctly discarded in favour of `None` — intended. When
`_tree_has_path` returns `True` (path present, `show` failed for another reason), the
*original* `git show` stderr is re-raised verbatim — correct, verified above (corrupt blob,
permission-denied, gitlink cases all surface the `git show` message). But when
`_tree_has_path` **itself** raises (the `ls-tree` probe also can't resolve the ref), the
exception that reaches the caller is `ls-tree`'s stderr, not `git show`'s. Scratch comparison
for a bad ref: `git show` says `fatal: invalid object name 'not-a-real-ref'.`; `git ls-tree`
says `fatal: Not a valid object name not-a-real-ref` — similar but not identical wording, and
for this failure class *neither* message names the file path, so no path context is lost
here specifically, but the substitution is a general code-shape issue: a maintainer chasing
the resulting `RuntimeError` sees the second subcommand's diagnostic, not the first's.
**Not reachable in the shipped call chain** — `gated_set` resolves every `ref` through
`commit_oid()` (`^{commit}`-verified) before it ever reaches `_git_show`/`_tree_has_path`, so
a bad-ref double-failure can only be hit by calling `_git_show` directly with an unvalidated
ref, which is exactly what the new unit test does on purpose to exercise the raise branch.
Advisory only; does not gate.

## Not reported (ruled out already)

No BRIEF/plan.yaml (BUG precedent). DEC-174 main-session-direct/human-executed nature of the
change. `code-grade: pass` for all three gated records — no `must_fix` from the grader.

```yaml
VERDICT: PASS
DIGEST:
  headline: Structural git-ls-tree probe correctly replaces the English-message match; no fail-open found across 10 execution-verified failure modes, masking restoration proven end to end by running the new tests against both pre-fix and post-fix code.
  severity_max: low
  findings: 1
  must_fix: []
  spec_violations: []
  reviewed: "9f2a070..e353c7e"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1055-code-grade-absent-path/notes/review-harness-code-reviewer-c0.md
```
