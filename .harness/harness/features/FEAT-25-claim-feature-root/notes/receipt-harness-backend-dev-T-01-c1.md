# Receipt — T-01 — harness-backend-dev

## Dispatch verify vs plan.yaml — cross-checked

Extracted `plan.yaml`'s `tasks[T-01].verify` with `yaml.safe_load` into a standalone script and
diffed it byte-for-byte against the dispatch's `verify:` block: **identical**, no mismatch. Ran
that extracted script (not a re-typed copy) as the actual verify.

## Result

Ran verbatim via:
```
CLAUDE_PROJECT_DIR=/Users/molchairuangutai/GitHub/harness bash <extracted-plan.yaml-verify-script>
```
Output:
```
T-01 GREEN
```
`verbatim exit=0`

## Files touched (complete list)

- `.claude/skills/harness/bin/factory_claim.py`
- `.claude/skills/harness/bin/test-factory-claim.py`
- `.claude/skills/harness/bin/test-factory-integration.py`
- `.harness/harness/features/FEAT-25-claim-feature-root/notes/receipt-harness-backend-dev-T-01-c1.md` (this file)

No probe edit was used — the RED evidence was observed by adding the two module-scope test cases
first and running the suite against the unmodified `factory_claim.py`, in the order the task
prescribes. No revert/restore cycle was needed, so there is no byte-restore to verify beyond the
final `git status --porcelain` below (unchanged from session start aside from the three edited
files).

## Ordering actually followed

1. Added the two module-scope cases to `test-factory-claim.py` (unmodified `factory_claim.py:43`
   still read `os.path.join(factory_config.harness_root(), ".harness", "features")`).
2. Ran `python3 test-factory-claim.py` — both new cases FAILed (verbatim below), 114 pre-existing
   `ok` lines unaffected, exit 1.
3. Edited `factory_claim.py:43` (three-segment join) and its docstring (lines 25-27).
4. Re-ran `test-factory-claim.py` — both new cases now `ok`, 116 total `ok` lines, exit 0.
5. Edited `test-factory-integration.py` fixture joins (FEAT-INTEG-HAPPY, FEAT-INTEG-TWOBOARD) and
   its module docstring paragraph.
6. Ran `test-factory-integration.py` — 106 `ok` lines, 0 FAIL, exit 0.
7. Ran the T-01 `verify:` block extracted verbatim from `plan.yaml` — printed `T-01 GREEN`, exit 0.

## Red-first evidence — verbatim

Command: `cd .claude/skills/harness/bin && python3 test-factory-claim.py 2>&1 | grep -A2 'unpatched FEATURES_ROOT'`

```
FAIL  the unpatched FEATURES_ROOT default is the migrated harness features tree
        '/Users/molchairuangutai/GitHub/harness/.harness/features'
FAIL  the unpatched FEATURES_ROOT default names a directory that exists
        '/Users/molchairuangutai/GitHub/harness/.harness/features'
```

Full-run counts at that point (command: `python3 test-factory-claim.py; echo exit=$?`):
`exit=1`, 114 `ok` lines (all pre-existing cases, unaffected), 2 `FAIL` lines (the two new cases).
This confirms `check()` records a FAIL and continues rather than raising — all 116 cases ran to
completion in one pass.

## New ok-line texts added (complete list — matches the plan's enumeration, nothing extra)

- `the unpatched FEATURES_ROOT default is the migrated harness features tree`
- `the unpatched FEATURES_ROOT default names a directory that exists`

## Observed ok-line counts (final, post-edit)

- `test-factory-claim.py`: **116** (114 baseline + 2 new)
- `test-factory-integration.py`: **106** (baseline unchanged, no new cases added by T-01)
- `test-layout-migration.py`: **40** (unedited by T-01; re-ran post-edit to confirm SC-07's third
  suite was not disturbed by the constant change — unchanged)

Baselines re-confirmed at `d1ffd7f` (current `main`, unmoved) before editing:
`test-factory-claim.py` 114, `test-factory-integration.py` 106, `test-layout-migration.py` 40 —
all three match the plan's pinned counts exactly.

## Coupling check — other consumers of `FEATURES_ROOT` or the legacy path

`grep -rln 'FEATURES_ROOT' .claude/skills/harness/bin` → only `factory_claim.py`,
`test-factory-claim.py`, `test-factory-integration.py` — the three files T-01 authorises. No other
script reads the constant.

`grep -rln '"\.harness", "features"' .claude/skills/harness/bin` → also matches
`layout_migration.py`, `layout_fixtures.py`, `test-layout-migration.py` (T-03's legacy-regex
fixture for the layout detector, explicitly out of scope for T-01 and unaffected by this change)
and `test-gh-sync.py` (a different tool's own unrelated fixture paths, does not import or read
`factory_claim.FEATURES_ROOT`). None of these are in T-01's `files:` list and none were edited.

## Verify block — final line and exit status, verbatim

```
T-01 GREEN
```
`verbatim exit=0`

## Forbidden set — checked individually

- `factory_config.py` — not in `git diff --name-only`. Unedited.
- `.harness/factory/fleet.yaml` — not in `git diff --name-only`. Unedited.
- `.harness/harness.json` — not in `git diff --name-only`. Unedited.
- `gh_board.py` — not in `git diff --name-only`. Unedited.
- `check-domain.sh` — not in `git diff --name-only`. Unedited.
- `load_board` — `git diff | grep -E '^\+' | grep -c load_board` → `0`. Appears in no line I added.

## Held dirt — untouched

`git status --porcelain` before and after this task shows the same pre-existing modified/untracked
entries (`harness-eng-lead.md`, `harness-product-lead.md`, `harness-validator-lead.md`,
`DECISIONS.md`, `SPEC.md`, `FEAT-26-pr-linkage-recorded/`, `FEAT-27-expertise-repository-tier/`)
unchanged by this run — none staged, none edited, none reverted.

## No git operations performed

No `git add`, `git commit`, `git stash`, or `git checkout` of any path was run. All edits are in
the working tree only.
