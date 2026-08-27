# Receipt — harness-backend-dev — T-02

Delete `wayfind.root` and move `wayfind.py`'s `cfg()` onto `harness_boundary.root_above`,
closing the bare-`.harness`-directory fail-open.

## RED — verbatim stdout+stderr, run against the UNTOUCHED `wayfind.py` (pre-edit)

Command: `python3 .claude/skills/harness/bin/test-wayfind.py`

```
FAIL case_1_wayfind_directory_probe_resolves_real_root expected cfg() to resolve the real, MARKER-carrying root and return its github.repo ('acme/real-root'); got repo=None exit_code=1 stderr="wayfind: cannot read /private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/f42-wayfind-real-8x1yzkq0/decoy_child/.harness/harness.json ([Errno 2] No such file or directory: '/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/f42-wayfind-real-8x1yzkq0/decoy_child/.harness/harness.json')\n"
PASS case_2_wayfind_no_marker_dies_nonzero

1 FAILURE(S): ['case_1_wayfind_directory_probe_resolves_real_root']
EXIT=1
```

Why this is the expected red shape, and not a bug in the test: under the untouched
`root()`, resolution from a start point below `decoy_child` walks up and stops at
`decoy_child` itself — it merely checks `os.path.isdir(<d>/.harness)`, and
`decoy_child/.harness` exists as a bare directory with no `team-config.yaml`. `cfg()`
then tries to open `decoy_child/.harness/harness.json`, which does not exist, and
`die()`s. That is the fail-open this task exists to close: the decoy wins over the
real, MARKER-carrying root three levels further up. The FAIL line names
`case_1_wayfind_directory_probe_resolves_real_root`, which contains the required token
`wayfind_directory_probe` for the task's own verify grep.

`case_2_wayfind_no_marker_dies_nonzero` already PASSes pre-edit — the untouched `root()`
also dies (for its own, unrelated reason: it walks to `/` and calls `die()`) when no
directory named `.harness` exists at all above the start point. That case is retained
post-edit as the companion assertion that the fix does not turn "no marker anywhere"
into a fail-open either.

## GREEN — after replacing `root()` with `harness_boundary.root_above` in `cfg()`

Command: `python3 .claude/skills/harness/bin/test-wayfind.py`

```
PASS case_1_wayfind_directory_probe_resolves_real_root
PASS case_2_wayfind_no_marker_dies_nonzero

ALL PASS
```

Observed exit status: `0`.

## VERIFY — verbatim stdout+stderr, `plan.yaml`'s T-02 `verify:` block

Command form used — the task's `verify:` block saved verbatim to
`/tmp/f42-t02-verify.sh` and run with `bash /tmp/f42-t02-verify.sh`:

```
cd "$(git rev-parse --show-toplevel)"
B=.claude/skills/harness/bin
N=.harness/harness/features/FEAT-42-one-root-resolver/notes
python3 $B/test-wayfind.py || exit 1
grep -q "HARNESS_PROJECT_DIR" $B/wayfind.py && { echo "chain survives"; exit 1; }
grep -qE "^def root\(" $B/wayfind.py && { echo "root() survives"; exit 1; }
grep -rqE "FAIL.*wayfind_directory_probe" $N/receipt-*.md || { echo "SC-10: no red receipt"; exit 1; }
echo T-02-OK
```

Verbatim stdout+stderr, unedited:

```
PASS case_1_wayfind_directory_probe_resolves_real_root
PASS case_2_wayfind_no_marker_dies_nonzero

ALL PASS
T-02-OK
```

Observed exit status: `0`.

## Changes

- `.claude/skills/harness/bin/wayfind.py`: deleted `root()` (previously at `:46-53`)
  entirely — no forwarder left in its place (D-01). Its single call site, `cfg()`,
  now calls `harness_boundary.root_above(os.getcwd())` and calls the module's existing
  `die()` when that returns `None`. Added `import harness_boundary` beside the existing
  `import gh_issues as ghi`, reusing the `sys.path.insert` at `:32` that already exists
  for that importer rather than adding a second path-setup site. Neither
  `HARNESS_PROJECT_DIR` nor `CLAUDE_PROJECT_DIR` appears anywhere in the file any more.
- `.claude/skills/harness/bin/test-wayfind.py`: new, in the sibling idiom
  (`test-no-distribution.py`) — module-level `failures`, `check(name, cond, detail)`,
  plain `case_N_...` functions, `main` exits 1 on failure, runnable directly with
  `python3`, no pytest. Not registered in `run-unit-tests.sh` — T-03 owns that, per its
  own intent (see notes below).

## Decisions recorded (reversible, mine to make)

- **cwd/env isolation and restoration.** `_run_cfg_from` chdirs into the case's start
  directory and clears `HARNESS_PROJECT_DIR`/`CLAUDE_PROJECT_DIR` for the duration of the
  call, restoring both cwd and the prior environment values in a `finally` — so one case
  cannot leak into the next, and so a real value either variable happens to carry on the
  machine running this suite cannot mask the probe under test (the walk is supposed to
  start from cwd alone, per the intent).
- **`cfg()` invoked directly, not through the full `main()` CLI**, to avoid any `gh`
  subprocess dependency in the test — `cfg()` is the exact function under test and the
  first thing every subcommand calls.
- **Oracle values are distinctive literals** (`"acme/real-root"`, a repo name that
  appears nowhere else in the fixture) rather than anything derived from
  `harness_boundary` itself, so the assertion cannot pass by construction.
- **Case 1's decoy carries no `harness.json`** (only spec-required: no
  `team-config.yaml`). Under the untouched `root()` this makes the old code `die()`
  rather than silently resolving to a wrong-but-present repo string — still a clean red,
  and the receipt above explains why that is the correct red shape rather than an
  artifact of the fixture.

## Notes for the reviewer / T-03

- Confirmed by reading `run-unit-tests.sh` and `harness.json:105` (per this task's
  instructions — not touched): the unit-test detect glob at `harness.json:105` already
  includes `.claude/skills/harness/bin/test-*.py`, so `test-wayfind.py` needs no new glob
  entry. `run-unit-tests.sh` itself was not touched, per this task's file scope; the T-01
  receipt already flags that its own drift detector does not yet know about
  `test-harness-boundary.py`, and the same applies here — T-03 owns wiring both in.
- `harness_boundary.py` was not modified by this task; only imported.
