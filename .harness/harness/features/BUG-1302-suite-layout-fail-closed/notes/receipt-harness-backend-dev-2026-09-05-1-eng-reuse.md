# REUSE angle — BUG-1302-suite-layout-fail-closed plan draft

BLUF: two real findings. T-04's intent hand-spells the git-fixture idiom that
`base_git_fixture`/`git_commit` already provide (med). T-01/T-02 each independently
spell "locate a FunctionDef by name and count node kinds inside it" with no shared
helper, even though the surrounding ast-parse-reuse instruction is otherwise correct
(low). Everything else asked to resolve — hand-rolled assertions, verify clauses
duplicating existing scripts, and the `sole_implementations` guarded-read relationship —
resolves CLEAN or observation-only, per instruction.

## F1 — T-04 fixture reinvents `base_git_fixture`/`git_commit` — MED
- Task/SC: T-04, REQ-04
- File:line — plan.yaml T-04 step 2 (intent lines 216–224); existing helpers at
  `tests/unit/test-suite-layout.py:178` (`base_git_fixture`) and `:195` (`git_commit`).
- Cost: the intent spells `tempfile.mkdtemp`, `git init -b main -q`, `git add -A`,
  and the `git -c user.email=... -c user.name=... commit -q -m` invocation inline —
  a third, hand-copied spelling of an idiom the file already names twice (case 1–10
  all call `base_git_fixture()`/`git_commit(td)`). A change to the commit invocation
  (e.g. a third `-c` flag, a different default branch name) now has three sites to
  edit in lockstep instead of two.
- Verified it serves T-04 exactly: `base_git_fixture(include_self=False)` creates only
  `.harness/team-config.yaml` (extension `.yaml`, not in `SOURCE_EXTENSIONS`, so
  `_violations_callers` never opens it) plus `tests/unit/test-unit.py`,
  `tests/integration/test-integration.py`, `tests/manual/probe-fixture.py` (all under
  `tests/`, filtered by `rel.startswith("tests/")` before any read, `test-suite-layout.py:160`).
  None of these can perturb `_violations_callers`'s result set for the fixture root.
  `include_self=False` correctly avoids adding a fifth tracked `.py` under
  `.claude/skills/harness/bin/` that is irrelevant to this fixture and unrelated to the
  hazard under test.
  Ordering also lines up: `base_git_fixture` only creates files, it does not commit
  (`git_commit` is the separate, explicit commit step) — so "write `deleted.py` and
  `binary.py` → `git_commit(td)` → `unlink(deleted.py)`" is exactly the same
  create-then-commit-then-uncommitted-delete sequence every existing case already uses
  (e.g. case 1, `test-suite-layout.py:205–228`).
- Recommended change: replace the inline `tempfile.mkdtemp`/`git init`/`git add -A`/
  `git commit` spelling in T-04 step 2 with `td = base_git_fixture(include_self=False)`
  followed by writing `deleted.py` and `binary.py`, then `git_commit(td)`, then
  `deleted.py.unlink()`.

## F2 — locate-FunctionDef-and-count is spelled twice, no shared helper — LOW
- Task/SC: T-01, T-02, REQ-02, REQ-01, REQ-06
- File:line — plan.yaml T-01 step 3 (intent lines 72–77), T-02 step 3 (intent lines
  121–131).
- Resolution of the parse question: the plan establishes exactly ONE named ast parse —
  T-01 creates it (`Path(__file__).read_text()` parsed with `ast`), T-02 step 3 says
  "using the ast module imported by T-01 and the same … parse" and T-03 step 3 says
  "using the ast parse already present in the file" — both correctly instructed to
  reuse rather than re-parse. That part is CLEAN.
- What is NOT shared: the sub-operation "locate the FunctionDef named X, then count
  node kinds inside it" is written out independently in T-01 (locate
  `_is_inside_tests`, count `ast.Constant` nodes valued `".."`) and T-02 (locate
  `_literal_key_present`, count `ast.Call`/`ast.Constant` nodes) — the same
  walk-and-match-by-name logic, restated per task, with no named helper (e.g.
  `_find_functiondef(tree, name)`) either one is told to define and the other to call.
- Cost: two lock-step spellings of "find this FunctionDef in the tree" — a change to
  how the lookup handles e.g. nested/duplicate definitions has to be made twice, and
  T-02's copy is the one nobody is looking at once T-01 lands.
- Recommended change: have T-01's step 3 define a small named helper,
  `_find_functiondef(tree, name)` (walk `ast.walk(tree)`, return the first
  `ast.FunctionDef` whose `.name == name`), and have T-02's step 3 call it instead of
  re-deriving the same lookup. T-03 locates a different node shape (an `ast.If`) so it
  is not a fit for this helper and is correctly left alone.

## Resolved CLEAN (no finding)
- **Assertion helpers (T-01–T-04):** every task names an exact `check()` call
  (`check("b5 corpus…")`, `check("b4 corpus…")`, `check("case 11 behavioural…")`,
  `check("b14: …")`) — none hand-rolls `assert`/`print`+`failures.append` in place of
  the existing `check(name, cond, detail)` at `test-suite-layout.py:37`.
- **`verify:` clauses vs. existing scripts:** T-01/T-02/T-04's verify clauses are
  `python3 <file> && grep -q "<check name>" <file>` and T-05's adds a `grep -c` count —
  none reimplements a check an existing repository script already performs.
  `check-plan-routes.py` (SC-10) is out of scope per the dispatch.

## Observation, not a finding (per instruction, no scope-widening recommended)
`sole_implementations()` (`test-suite-layout.py:42–52`) already carries a guarded-read
idiom for the same hazard class T-04's `_violations_callers` now guards against:
`path.read_text(errors="replace")` (silently substitutes bad bytes, never raises) versus
T-04's new `try/except (OSError, UnicodeDecodeError)` (catches and reports the path).
Same file, same hazard class (unreadable/undecodable tracked source), two different
handling policies. Concrete cost: a future policy change to how this file treats
unreadable sources (e.g. "always report, never silently substitute") has two spellings
to update, and `sole_implementations` at line 48 is the one nobody will think to revisit
because it doesn't name the hazard the way T-04's new branch does. Not recommending any
change to `sole_implementations` — out of this feature's scope.

## Confirmations
Read-only throughout: wrote nothing under `tests/`, did not touch `plan.yaml` or
`BRIEF.md`, ran no test suite (`test-suite-layout.py` / `test-run-unit-tests-layout.py`
were read, never executed).
