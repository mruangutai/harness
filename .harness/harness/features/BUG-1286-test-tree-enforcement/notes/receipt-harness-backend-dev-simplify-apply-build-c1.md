# Receipt — simplify apply (backend-dev) — BUG-1286-test-tree-enforcement

## BLUF

Both simplify findings applied, behaviour-preserving, proved by three instruments plus
the T-03 verify string. Unit suite 341/0/27 files, integration suite 14/0, census
before/after byte-identical (diff rc=0), T-03 verify exits 0. HEAD unchanged at
`d2ccea0a`, nothing staged or committed.

## Apply 1 — narrative comment (SIMPLIFICATION, F-3)

`tests/unit/test-suite-layout.py:251` (now lines 251-252).

Before:
```
# Case 5: the existing non-git legal_tree() is unaffected by the new clause.
```

After:
```
# Case 5: a non-git tree is unaffected by the tracked-outside-tests clause, which
# never fires without a .git index.
```

Comment-only; no assertion, fixture, or code touched. Wrapped across two lines to keep
line width in the surrounding style.

## Apply 2 — fold extension conjunct into `is_test_shaped` (ALTITUDE, F-1)

`tests/manual/suite-census.py`:

1. Added `is_test_shaped` to the existing `from suite_layout import (...)` block
   (line 15-21). `AGNOSTIC_NAME_PATTERNS`, `DOCUMENTED_EXCEPTIONS`,
   `RESTRICTED_NAME_PATTERNS`, `SOURCE_EXTENSIONS` kept, unreordered, per the signed
   constraint (T-03 needs the tuples themselves for `_vocabulary_paths`'s
   extension-free selection). `SOURCE_EXTENSIONS` has no other use site in the file
   after this edit but stays imported per the task's stated contract with
   `suite_layout`.
2. `_disposition` (was line 92-93, now 92-93):

Before:
```python
    if restricted and not agnostic and os.path.splitext(path)[1] not in SOURCE_EXTENSIONS:
        return "out-of-vocabulary"
```

After:
```python
    if restricted and not agnostic and not is_test_shaped(path):
        return "out-of-vocabulary"
```

Equivalence reproduced: `is_test_shaped(path) == agnostic or (restricted and ext in
SOURCE_EXTENSIONS)`. Under `not agnostic` (already gated by the branch condition), this
collapses to `restricted and ext in SOURCE_EXTENSIONS`, so `not is_test_shaped(path)`
collapses to `not restricted or ext not in SOURCE_EXTENSIONS`. Conjoined with the
already-true `restricted`, the `not restricted` disjunct is vacuous, leaving exactly
`ext not in SOURCE_EXTENSIONS` — identical to the original inline conjunct. Confirmed
empirically by the byte-identical census diff below (rerun against every tracked path
in the repo, not just a spot check).

`_vocabulary_paths` untouched — still selects on basename patterns with no extension
filter, per T-03's intent.

## Verification

### 1. Unit suite
```
env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.sh --kind unit
```
rc=0. `^PASS ` count: 341. `^FAIL ` count: 0. File count (from pool summary line
`pool: 8 workers, 27 files, 2.09s wall`): 27. Matches stated baseline exactly.

### 2. Integration suite
```
env -u HARNESS_AGENT_TYPE python3 tests/integration/test-run-unit-tests-layout.py
```
rc=0. `^PASS ` count: 14. `^FAIL ` count: 0. Matches stated baseline exactly.

### 3. Census byte-diff
Baseline captured before apply 2 landed (apply 1 does not touch `suite-census.py`, so
apply 1's edit was already present; apply 2 was isolated via `git stash push -- tests/manual/suite-census.py`,
baseline taken, then `git stash pop` to restore apply 2):
```
python3 tests/manual/suite-census.py tree-audit --ref HEAD > /tmp/census-before.txt; rc=0
```
After apply 2 restored:
```
python3 tests/manual/suite-census.py tree-audit --ref HEAD > /tmp/census-after.txt; rc=0
diff /tmp/census-before.txt /tmp/census-after.txt; diff rc=0
```
Empty diff — apply 2 changed no observable census output. No row disposition, sort
order, or TOTAL/OUTSIDE/VIOLATIONS line changed.

### 4. T-03 verify (verbatim, cross-checked against plan.yaml:904 — identical)
```
out=$(python3 tests/manual/suite-census.py tree-audit --ref HEAD) && printf '%s\n' "$out" | grep -q 'probe-session-accessors\.ts.*documented-exception'
```
rc=0.

## Git state

```
$ git status --porcelain
 M .harness/harness/features/BUG-1286-test-tree-enforcement/STATE.md          (sibling)
 M .harness/harness/features/BUG-1286-test-tree-enforcement/feature.json      (sibling)
 M tests/integration/test-run-unit-tests-layout.py                           (sibling)
 M tests/manual/suite-census.py                                              (mine — apply 2)
 M tests/unit/test-suite-layout.py                                           (mine — apply 1)
 ?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-matrix-gate-c1.md
 ?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-matrix-gate-c2.md
 ?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-backend-dev-T-02-fix-c1.md
 ?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-backend-dev-simplify-altitude-build-c1.md
 ?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-backend-dev-simplify-reuse-build-c1.md
 ?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-data-engineer-simplify-efficiency-build-c1.md
 ?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-dev-ops-simplify-simplification-build-c1.md
 ?? .harness/harness/features/BUG-1286-test-tree-enforcement/observations/harness-backend-dev.md
 ?? .harness/harness/features/BUG-1286-test-tree-enforcement/observations/harness-documentor.md

$ git rev-parse HEAD
d2ccea0a686bbff06f2b3782e7fe346340bcb503
```
HEAD unchanged; nothing staged; nothing committed. The other modified/untracked entries
are concurrent sibling agent activity (T-02 fix, other simplify-angle receipts, QA
notes), not touched by this dispatch.

## One-fix ceiling

Not invoked — both suites stayed green on first application, no fix needed.
