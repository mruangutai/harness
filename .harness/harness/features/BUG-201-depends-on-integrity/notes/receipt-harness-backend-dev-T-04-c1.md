# Receipt — harness-backend-dev — T-04 (BUG-201-depends-on-integrity)

## Task
T-04 · Add the live-corpus non-regression guard to the depends_on unit test.
Only file touched: `tests/unit/test-plan-depends-on.py` (appended to; T-01's ten
pre-existing checks are untouched and stay green).

## Verify command (cross-checked against plan.yaml's own T-04 `verify:` block — identical)

```
python3 tests/unit/test-plan-depends-on.py && python3 tests/unit/test-harness-yaml-corpus.py
```

## What was added

- One shared `walk(root)` function: globs `<root>/.harness/harness/features/*/plan.yaml`,
  calls `harness_yaml.load_plan` on each, returns `(files_found, failures)` where
  `failures` is `[(path, message), ...]` for every path that raised.
- Case A (live corpus): resolves the repo root the same way
  `tests/unit/test-harness-yaml-corpus.py` does (`HARNESS_PROJECT_DIR` or
  `CLAUDE_PROJECT_DIR`, else `os.getcwd()`), runs `walk` against it, asserts
  `count >= 67` (never `== 67`) and zero failures, naming every failing path in
  the detail.
- Case B (paired detector): builds a throwaway root under
  `tempfile.TemporaryDirectory`, containing one
  `.harness/harness/features/FEAT-XX/plan.yaml` whose single task's
  `depends_on: [T-99]` is dangling, runs the SAME `walk`, and asserts exactly
  one failure naming that path.

Both cases run through the one `walk(root)` function; no second inlined walk exists.

## Literal final lines of the verify run (both suites, observed this run)

```
12/12 checks passed.
```
```
16/16 checks passed.
```

Full observed output included the live-corpus case:

```
ok  the live plan corpus loads cleanly (68 files found, floor 67)
ok  the same walk reports exactly one failure naming the throwaway dangling plan
```

**Actual live-corpus file count observed: 68** (>= the 67 floor; the plan's own
`intent:` text and D-04 both note the corpus grows as features are added — this
feature's own signed `plan.yaml` is the 68th file, consistent with panel finding
PF-7beea12ebdabef0e2f946b763f7be080 already recorded in plan.yaml). The count is
asserted as a floor (`>= 67`), never as `== 67`, and is printed from the counted
value, never a frozen literal.

## Scope discipline

No self-dependency check, no cycle detection, no ordering policy added. `walk`
only calls `harness_yaml.load_plan` and records raises — pure referential-integrity
enforcement inherited from T-03's rule, nothing added here.

## Files touched

- `tests/unit/test-plan-depends-on.py` (append only)

## git status --porcelain (observed after edit)

Only `tests/unit/test-plan-depends-on.py` reflects this task's edit (shown as
`??` because T-01 created it earlier and it remains untracked pending the
orchestrator's commit). The three `M` entries
(`.claude/skills/harness/bin/harness_yaml.py`, this feature's `plan.yaml`,
`tests/integration/test-plan-merge.py`) and the T-01/T-02/T-03 receipts are
sibling-task artifacts, not touched by T-04.
