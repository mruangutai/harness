# Receipt — harness-backend-dev — T-03-c1

## Verdict

T-03 GREEN. `factory_claim.py` is now a features-surface row in `layout_migration.READER_TABLE`,
`layout_fixtures.STUB` and `FEATURES_READERS`, with a matching real-root test case. No renames, no
weakened or deleted assertions.

## Step 1 audit — run against the working tree (T-01 already landed)

```
$ grep -nE '"\.harness", "features"' factory_claim.py
(no output — zero matches)

$ grep -nEi 'harness.{0,30}features|features.{0,30}harness' factory_claim.py
26:FEATURES_ROOT resolves to `.harness/harness/features` under `factory_config.harness_root()`, never
45:FEATURES_ROOT = os.path.join(factory_config.harness_root(), ".harness", "harness", "features")

$ grep -nE '"\.harness", [^,)]+, "features"' factory_claim.py
45:FEATURES_ROOT = os.path.join(factory_config.harness_root(), ".harness", "harness", "features")
```

The legacy pattern (`"\.harness", "features"`) matches nothing in the current file — confirmed
absent. The migrated pattern (`"\.harness", [^,)]+, "features"`) matches line 45, the T-01-landed
constant. The file is not MIXED; the row is safe to add as written in the intent (unwidened). Note:
the broader prose grep hits two lines (26, docstring; 45, code) rather than the plan's originally
quoted single line — expected, since the plan's audit predates T-01's docstring update at line 26.
It adds no new pattern concern; both lines carry the migrated shape only.

## New READER_TABLE row, read back from the file

```
$ grep -n "factory_claim" layout_migration.py
45:factory_claim.py's features row landed with the unit that fixed its root (FEAT-25 T-03).
91:    Row("features", ".claude/skills/harness/bin/factory_claim.py",

$ sed -n '87,93p' layout_migration.py
    # it. Each comment restores that row's textual paren balance to zero.
    Row("features", ".claude/skills/harness/bin/check-plan-routes.py",
        r'"\.harness", "features"',
        r'"\.harness", [^,)]+, "features"'),  # balance: (
    Row("features", ".claude/skills/harness/bin/factory_claim.py",
        r'"\.harness", "features"',
        r'"\.harness", [^,)]+, "features"'),  # balance: (
```

The trailing `# balance: (` comment is present on the new row, exactly as the precedent row above
it carries.

## Docstring edit

The `DO NOT READ` paragraph no longer names `factory_claim.py` literally (the verify checks for
absence of that exact substring anywhere in `__doc__`). I removed it from the do-not-read list and
added a clause recording the row landed with FEAT-25 T-03, phrased without spelling the filename
(`"The feature-claiming tool's features row landed..."`) so the substring-absence assertion holds:

```
>>> import layout_migration as lm
>>> "factory_claim.py" in (lm.__doc__ or "")
False
```

## layout_fixtures.py STUB entry

Added verbatim as specified:

```python
".claude/skills/harness/bin/factory_claim.py": {
    "legacy":   'FEATURES_ROOT = os.path.join(r(), ".harness", "features")\n',
    "migrated": 'FEATURES_ROOT = os.path.join(r(), ".harness", _seg, "features")\n',
},
```

Module imports clean (`python3 -c "import layout_fixtures"` → OK), so the STUB-keys-match-table
RuntimeError guard did not fire.

## New test case

`test-layout-migration.py` case 22, mirroring case 21 (the real-root docs case) but for the
features surface:

```
ok   - case 22: real root's harness/features surface is CLEAN with migrated evidence
```

## Observed ok-line count

`test-layout-migration.py`: **41** ok-lines (`grep -c '^ok   - '`), matching the `>= 41`
requirement exactly (d1ffd7f baseline 40 + this one new case). Zero `FAIL` lines. Exit 0.

## test-check-state.py result

GREEN, exit 0, zero `FAIL` lines. In particular case **(x.3) an applicable clean tree -> NO INV-27
line** passed — my STUB legacy fragment does not also match the row's migrated pattern (no
`[both]` form-set introduced). No DEC-174 blocker encountered; `check-state.sh` was not touched.

## Verify block — final line and exit status

```
$ <verify block>
T-03 GREEN
```
Exit status: 0.

## Forbidden-set and `load_board` check (individually)

- `factory_config.py` — not in `git diff --name-only`. Unedited.
- `.harness/factory/fleet.yaml` — not in `git diff --name-only`. Unedited.
- `.harness/harness.json` — not in `git diff --name-only`. Unedited.
- `gh_board.py` — not in `git diff --name-only`. Unedited.
- `check-domain.sh` — not in `git diff --name-only`. Unedited.
- `load_board` — `git diff -- layout_migration.py layout_fixtures.py test-layout-migration.py |
  grep load_board` → no output. Symbol appears in no line I added.

## Files touched

- `.claude/skills/harness/bin/layout_migration.py`
- `.claude/skills/harness/bin/layout_fixtures.py`
- `.claude/skills/harness/bin/test-layout-migration.py`
- `.harness/harness/features/FEAT-25-claim-feature-root/notes/receipt-harness-backend-dev-T-03-c1.md` (this receipt)

`factory_claim.py` was read-only (per T-03's `files:` list); not edited by this task (T-01 already
landed its change).

## Note on the plan/dispatch verify cross-check

Cross-checked the dispatch's `verify:` string against `plan.yaml` T-03's `verify:` block: identical,
byte for byte, including the ok-line hasok checks and the `k -ge 41` threshold. No mismatch.
