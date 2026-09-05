# Receipt — harness-backend-dev — T-02 — BUG-1286-test-tree-enforcement

## Task
T-02: Prove the runner presents the refusal before any test sentinel runs.
File changed: `tests/integration/test-run-unit-tests-layout.py` (only file touched).

## What was added
- `git_tree()`: builds `tree()`, then makes it a real checkout (`git init -b main -q`,
  commit via `git_commit()` using `-c user.email=t@example.com -c user.name=t -q -m fixture`),
  so `.claude/skills/harness/bin/suite_layout.py` is tracked at its real relative path —
  the self-ownership precondition `tracked_paths()` requires (D-03) to enforce
  repository-wide (T-01).
- `git_tree()` also seeds and commits a fixture stand-in at the exact D-05 documented-exception
  path (`.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts`).
  Without it, `suite_layout._registry_findings()` runs unconditionally whenever `tracked_paths()`
  succeeds (independent of self-ownership; see `suite_layout.py` line 149) and reports
  "documented exception is no longer tracked" for every synthetic git fixture that lacks the
  one real DOCUMENTED_EXCEPTIONS entry — which would falsely redden the clean (case 1) and
  untracked-control (case 5) cases the task specifies as `returncode == 0`. This was caught by
  first running the suite without the fixture stand-in (both cases FAILed with that
  MISCONFIGURED line); adding the stand-in file made both green, which is the expected/intended
  clean-tree behavior per the task's own stated expectations.
- Five cases, all additive; every pre-existing case/expectation in the file is unchanged:
  1. clean `git_tree()`: `--kind all` returns 0, both `PASS test-unit.py`/`PASS test-integration.py`
     present.
  2. one tracked rogue (`.harness/tools/test_rogue.py`, committed): asserts `returncode == 2`
     AND the file named on a `MISCONFIGURED:` stderr line AND `"PASS test-unit.py"` absent from
     stdout — the ordering guarantee.
  3. three tracked rogues in different directories (`.harness/a`, `.harness/b`, `.harness/c`):
     asserts all three appear on `MISCONFIGURED:` lines and in sorted path order.
  4. `.git` replaced by an empty directory: `returncode == 2`, `"cannot enumerate tracked files
     under"` in stderr, no `"PASS test-"` sentinel in stdout.
  5. untracked control (rogue written, never `git add`ed): `returncode == 0`, both sentinels run.

## Ordering-guarantee mutation proof (not part of the file; throwaway script, discarded)
Built a temp copy of the fixture tree, patched a COPY of `run-unit-tests.sh` (never the real
file — confirmed via `git status --porcelain -- .claude/skills/harness/bin/run-unit-tests.sh`
returning empty afterward) to suppress the layout early-exit, simulating a fail-open reordering
defect. Reran case 2's exact predicate against that mutant:
```
returncode: 0
STDOUT: ----- test-unit.py (exit 0, 0.02s) -----
PASS test-unit.py
...
case2-style assertion result (should be False under this reordering mutation): False
```
The assertion correctly reddens under the reordering mutant, confirming it is not a vacuous
check — this is the coverage the task exists to add (G-07/P-07 discipline).

## Verify (verbatim, from worktree root)

Command run — matches T-02's `verify:` in `plan.yaml` line 866 exactly:
```
python3 tests/integration/test-run-unit-tests-layout.py
```

Output:
```
PASS clean layout 
PASS runs unit 
PASS runs integration 
PASS bogus refused 
PASS unknown kind refused 
PASS empty unit 
PASS empty integration 
PASS duplicate 
PASS planted 
PASS git clean tree runs both sentinels 
PASS git tracked rogue refused before sentinels 
PASS git three tracked rogues reported in sorted path order 
PASS git enumeration failure refused before sentinels 
PASS git untracked rogue is not reported and both sentinels run 
EXIT_STATUS:0
```
Exit status: 0. All 14 checks (9 pre-existing + 5 new) PASS, 0 FAIL.

## Scope check
- `git -C <worktree> status --porcelain`:
  ```
   M .claude/skills/harness/bin/suite_layout.py
   M .harness/harness/features/BUG-1286-test-tree-enforcement/STATE.md
   M .harness/harness/features/BUG-1286-test-tree-enforcement/feature.json
   M .harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml
   M tests/integration/test-run-unit-tests-layout.py
   M tests/unit/test-suite-layout.py
  ?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-backend-dev-T-01-c1.md
  ```
  Only `tests/integration/test-run-unit-tests-layout.py` is mine (T-02's sole declared file).
  `suite_layout.py`, `tests/unit/test-suite-layout.py`, and the feature-tracking files
  (STATE.md, feature.json, plan.yaml, T-01's receipt) are T-01's/other agents' concurrent work,
  not touched or reverted by this task.
- HEAD unchanged: `5eebad669e323dab3f17c81795f1fde9e11e9f50`.
- Nothing staged (`git diff --cached --stat` empty); nothing committed.

## Note on tooling
The `edit` tool twice reported a stale internal hash (`#A48D` vs the disk content it also
displayed, which matched) for this file; rather than fight it, used `write` (full-file
overwrite) to apply both the initial content and the follow-up fix, verifying disk state via
`read`/`cat` and `git status --porcelain` after each write. Final on-disk content is confirmed
correct by the verify run above.
