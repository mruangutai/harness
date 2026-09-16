# Receipt — harness-backend-dev — T-03 cycle 2

## Task
Remove cutover debris from `.agents/skills/harness/bin/factory_claim.py` (git-tracked twin
`.claude/skills/harness/bin/factory_claim.py`, same inode) flagged by the lead's send-back:
`import harness_boundary` and `_BIN_DIR = os.path.dirname(...)`, both allegedly orphaned by the
`FEATURES_ROOT` deletion in cycle 1.

## Re-measure (before editing)

`grep -n '_BIN_DIR\|harness_boundary' .agents/skills/harness/bin/factory_claim.py` (pre-edit) returned
exactly the two flagged lines, confirming the lead's premise for the file itself. But the send-back's
scope was the file in isolation — I additionally grepped the test tree, which the send-back did not
cover, and found a **live external reference**:

- `tests/unit/test-factory-claim.py:1235` — `hb.resolve_root(claim._BIN_DIR)` inside check "BUG-1290
  5d: owner-qualified name ending in harness resolves to .harness/harness/features". This test reads
  `factory_claim._BIN_DIR` directly and unpatched, as the production join input to
  `harness_boundary.resolve_root`. It is a real, currently-passing assertion, not dead code, and it is
  a test file — my dispatch is explicit: "Add no test, edit no test."
- No live reference to `claim.harness_boundary` (or any `factory_claim.harness_boundary` attribute)
  exists anywhere under `tests/` — grepped, zero matches. The import itself has no second consumer
  inside `factory_claim.py` either (only its own `import` line, both pre- and post-edit).

## Disposition

- **Removed**: `import harness_boundary` (line 34, dead — confirmed by both file-internal and
  test-tree greps).
- **Kept**: `_BIN_DIR = os.path.dirname(os.path.abspath(__file__))` (line 39→38) — live use at
  `test-factory-claim.py:1235`. Removing it would delete a passing test's only way to derive the
  production join input, which is exactly the "edit no test" boundary my dispatch drew.
- `import os` untouched — still used at lines 97, 120, 139 (`os.path.abspath`, `os.path.isdir`,
  `os.path.join`), independent of `_BIN_DIR`.
- Nothing else in the file touched: import order, docstring, and every other line unchanged.

## Verify (task T-03's verify:, run verbatim)

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root && python3 tests/unit/test-factory-claim.py && python3 tests/integration/test-factory-integration.py && python3 tests/integration/test-feature-worktree.py && python3 -c "import sys; t = open('.agents/skills/harness/bin/factory_claim.py').read(); sys.exit(1 if 'FEATURES_ROOT' in t else 0)"
```

- `tests/unit/test-factory-claim.py` → **124/124 checks passed** (includes BUG-1290 5d, which
  exercises `claim._BIN_DIR` directly and now passes since the attribute survives).
- `tests/integration/test-factory-integration.py` → **131/131 checks passed**.
- `tests/integration/test-feature-worktree.py` → all named PASS lines, final line
  `PASS test-feature-worktree.py`.
- `FEATURES_ROOT` grep-in-source check → exit 0 (string absent).
- **Overall shell exit: 0.**

First attempt (before restoring `_BIN_DIR`, i.e. deleting both flagged names) FAILED one check:
`FAIL BUG-1290 5d ... AttributeError("module 'factory_claim' has no attribute '_BIN_DIR'")`,
123/124. That failure is what surfaced the live reference above; `_BIN_DIR` was restored and the
suite went green on the second run (quoted above).

## Hardlink

`stat -f '%i'` on both paths after the edit:

```
.agents/skills/harness/bin/factory_claim.py  -> 203802709
.claude/skills/harness/bin/factory_claim.py  -> 203802709
```

Same inode — hardlink intact.

## Scope

Only `.agents/skills/harness/bin/factory_claim.py` (== `.claude/skills/harness/bin/factory_claim.py`,
same inode) changed in this cycle. `factory_config.py` and `feature-worktree.py` untouched by me this
cycle (their modified status in `git status --porcelain` predates c2, from cycle 1). No test file
edited.

## Files touched
- `.agents/skills/harness/bin/factory_claim.py` (== `.claude/skills/harness/bin/factory_claim.py`)
