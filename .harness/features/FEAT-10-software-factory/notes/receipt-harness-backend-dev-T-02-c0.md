# Receipt — harness-backend-dev — T-02 — c0

## Task
FEAT-10-software-factory T-02: Add the fleet loader module and its unit test
(`.harness/features/FEAT-10-software-factory/plan.yaml:281`).

## What landed
- `.claude/skills/harness/bin/factory_config.py` — new. `harness_root()`/`FLEET_PATH`
  (absolute, three-tier resolution copied from `check-plan-routes.py`'s `_resolve_root` and
  `run-unit-tests.sh`'s header comment, probing `docs/harness/SPEC.md`), `workspace_path`,
  `FleetError`, `load_fleet`, `repo_entry`, `station`, and a `--show` CLI entry behind
  `if __name__ == "__main__":` wrapped in `factory_cli.run("config", _main,
  expected=(FleetError,))`.
- `.claude/skills/harness/bin/test-factory-config.py` — new. Plain python3 script, no pytest,
  53 checks, `N/N checks passed.` sibling summary form. Writes fixtures into
  `tempfile.TemporaryDirectory()`, never reads the real fleet.yaml.
- `.claude/skills/harness/bin/run-unit-tests.sh` — one line changed: `test-factory-config.py`
  appended to the existing `UNIT_SCRIPTS` array (line 58 before append; the rest of the diff
  in this file is pre-existing held dirt from T-11, untouched by me).

## Extra — the summary-line retrofit (bounded, ruled by the lead)
Confirmed the STOP CONDITION did not fire: both `test-factory-cli.py` and `test-factory-gh.py`
had exactly the single-`check()`-helper / single-`FAILS += 1`-site shape the lead measured, so
the retrofit proceeded. Four lines changed per file, not three as I first wrote and then
corrected here: a module-level `RAN = 0`, `global FAILS` widened to `global FAILS, RAN`, `RAN +=
1` added inside `check()`, and the final `print` changed to the `{RAN - FAILS}/{RAN} checks
passed.` / `{FAILS} of {RAN} FAILING.` sibling form (matching `test-team-catalog.py:248` /
`test-harness-yaml-corpus.py:247`). Nothing else in either file was touched; no case was added,
removed or changed.
Confirmed post-retrofit: `test-factory-cli.py` → `33/33 checks passed.`;
`test-factory-gh.py` → `76/76 checks passed.`

## TDD
RED confirmed first: running `test-factory-config.py` before `factory_config.py` existed raised
`ModuleNotFoundError: No module named 'factory_config'` (exit via traceback, not a per-case
FAIL — the module genuinely did not exist). Implementation was then written to make every case
pass.

That first green was not treated as sufficient evidence on its own (a suite that never watched
an individual assertion fail proves less than one that has). Three targeted mutants were then
introduced one at a time and reverted after each was observed to fail the corresponding new
case, before the final diff was taken:
  - `board.number` guard narrowed to `not isinstance(number, int)` (dropping the `bool`
    exclusion) → case "(14c) board.number is a bool, not an int" went FAIL, 1 of 52 FAILING.
  - `board.stations` guard's `not all(stations.get(k) ...)` clause deleted → case "(14b)
    board.stations carries an empty value" went FAIL, 1 of 52 FAILING.
  - `workspace_root` defaulted to `"/tmp"` before the missing-check (masking absence) → case
    "(14d) workspace_root is missing" went FAIL, 1 of 52 FAILING.
Each mutation was reverted immediately after the observed failure; the file was diffed against
its pre-mutation copy afterward and found identical. Each mutant reported "1 of 52 FAILING" —
not 53 — because the C-3 grammar loop runs one `check()` per *collected* `FleetError` message
(`for m in RAISED_MESSAGES`), so suppressing one raise removes both the case's own check and its
grammar-loop check while the bad-case loop itself still contributes one; net effect is 53 total
minus 1 (the raise never happened) = 52 checks that ran, 1 of them FAIL. Confirmed no debris was
left behind by the mutation runs: `git status --porcelain
.claude/skills/harness/bin/` afterward shows only the files listed below plus pre-existing held
dirt, no stray `.mut` copies.

## Baseline (before my change)
`--kind unit` → 5 files, exit 0. `--kind integration` → 13 files, exit 0. Verified directly
before writing `factory_config.py`.

## verify — cross-checked against plan.yaml:294, matches verbatim
```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t02.txt 2>&1; s=$?; grep -q "^PASS test-factory-config.py$" /tmp/v-t02.txt && [ "$s" -eq 0 ]
```

**Result: PASS.** `$s` (run-unit-tests.sh's own exit code) = 0. `grep -q "^PASS
test-factory-config.py$"` matched. Full verbatim tail of `/tmp/v-t02.txt`:

```
ok    (24) --show over an invalid fleet writes nothing to stdout
ok    (24) --show over an invalid fleet writes exactly one stderr line
ok    (24) --show over an invalid fleet exits 2

53/53 checks passed.
PASS test-factory-config.py
```

Also ran `--kind integration` after the change as a regression check: exit 0,
`grep -cE '^PASS test-.*\.py$'` on its output = 13 (same file count as baseline, unchanged).

Also ran the real CLI against the real fleet: `python3
.claude/skills/harness/bin/factory_config.py --show` against the actual
`.harness/factory/fleet.yaml` (read-only, never mutated) produced one JSON object on stdout with
`board` and `repos` keys, nothing on stderr, exit 0.

## Not touched
`check-state.sh`, `test-check-state.py` (DEC-174 carve-out, T-08 withheld) — did not read-to-edit
or write either. `factory_gh.py` — not imported; T-02 never needed GitHub access (R-01).
No `git add`/`git commit`. No live `gh`/`git` call — every path in the test is a tempdir fixture
or (for the real-fleet CLI smoke check above) a read-only `--show` against the existing,
already-committed `fleet.yaml`.

## Files touched
- `.claude/skills/harness/bin/factory_config.py` (new)
- `.claude/skills/harness/bin/test-factory-config.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` (one line: `UNIT_SCRIPTS` append)
- `.claude/skills/harness/bin/test-factory-cli.py` (retrofit: 3 lines)
- `.claude/skills/harness/bin/test-factory-gh.py` (retrofit: 3 lines)
