# Receipt — T-04 fleet product-config reachability report

Task: T-04 (FEAT-56-central-onboarding-model). Files touched: exactly
`.claude/skills/harness/bin/factory_config.py` and `tests/unit/test-fleet-product-config.py`, both
in the task's declared `files:` list. Cross-checked plan.yaml T-04's `intent:` and `verify:`
verbatim against the dispatch text — byte-identical, no mismatch.

## 1. Pre-change RED (test written before production code)

`tests/unit/test-fleet-product-config.py` was written first, calling `fc.product_config_report`
at module scope. Run before `factory_config.py` was touched:

```
Traceback (most recent call last):
  File ".../tests/unit/test-fleet-product-config.py", line 136, in <module>
    report_a = fc.product_config_report(fleet)
               ^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'factory_config' has no attribute 'product_config_report'
EXIT:1
```

A hard failure (AttributeError), not a passing-vacuously run — RED-CAPABILITY PROOF (i) satisfied.

## 2. Production change

Added `product_config_report(fleet)` immediately after `product_config` and before `board_for` in
`factory_config.py`; added `--check-product-configs` and `--repo` to `_main()`, delegating to a
new `_check_product_configs(fleet, repo_name)` helper; added `import sys` (module previously had
none). No `check-state.sh`/invariant change — a comment on the new flag states why, naming the
board-audit once-at-onboarding precedent, per the intent.

## 3. Verify — run exactly as specified (env -u HARNESS_AGENT_TYPE prefix only permitted deviation)

Command:
```
cd .../FEAT-56-central-onboarding-model && \
  env -u HARNESS_AGENT_TYPE python3 tests/unit/test-fleet-product-config.py && \
  env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-config.py
```

Each script run SEPARATELY, `$?` captured immediately after each, `^FAIL ` lines counted
separately (not by tail-reading the chained `&&` output):

### Script 1 — tests/unit/test-fleet-product-config.py — exit=0, FAIL-line count=0

```
ok    (a) two declared repos, both succeed -> every entry ok, ok count 2, unreachable 0
ok    (a)/(d) len(report) equals len(fleet['repos'])
ok    (b) the FIRST entry, asserted individually, is not ok and names repo and ref
ok    (b) the SECOND entry, asserted individually, is ok with an empty detail
ok    (b)/(d) len(report) equals len(fleet['repos'])
ok    (c) invalid JSON content -> entry not ok, detail names the invalid-JSON failure
ok    (c)/(d) len(report) equals len(fleet['repos'])
ok    every entry carries exactly repo/ref/path/ok/detail, path is _PRODUCT_CONFIG_PATH
ok    product_config_report preserves fleet['repos'] declaration order
ok    (e) --check-product-configs exits 2 (EXIT_REFUSED) under a failing stub
ok    (e) stdout under failure parses as ONE JSON payload with declared/ok/unreachable/members
ok    (e) exactly one stderr line is written for the one unreachable member
ok    (e) --check-product-configs returns without SystemExit under an all-succeeding stub
ok    (e) stdout under success parses as ONE JSON payload with declared/ok/unreachable/members
ok    (e) no stderr line is written when nothing is unreachable

15/15 checks passed.
```

### Script 2 — tests/unit/test-factory-config.py — exit=0, FAIL-line count=0

```
ok    (1) load_fleet round-trips repos[0].name
ok    (1) load_fleet round-trips workspace_root
ok    (3) a repos entry has no board — this is the correct shape now
ok    (2) schema is not factory-fleet/1
ok    (2b) workspace_root is a filesystem root
ok    (8b) a leftover top-level board key raises FleetError
ok    (9) repos is missing
ok    (10) a repo entry lacks a slash in its name
ok    (11) workspace_root is not absolute
ok    (8b) a leftover top-level board key raises FleetError
ok    (8b) the message names key 'board' exactly
ok    (8b) the next_step names the whole-fleet key, not repos[].board
ok    (8b) the next_step points at github.board
ok    (8b) the next_step no longer points at repos[].board
ok    (12) repos is empty
ok    (13) repos is not a list
ok    (14) a repo entry lacks default_branch
ok    (14d) workspace_root is missing
ok    (14c) repos[].board.number is a bool, not an int
ok    (6)/(28b) validate_board coerces a digit string number to an int
ok    (15) at least 9 FleetError messages were collected
ok    (15) FleetError message obeys C-3 (x9, one per collected message)
ok    (16) repo_entry finds the listed repo
ok    (17) repo_entry raises FleetError for an unlisted name
ok    (17) the message names the unlisted name
ok    load_fleet rejects a repos entry carrying a board key
ok    load_fleet still requires repos[].name, repos[].default_branch and workspace_root
ok    validate_board accepts the ordered lowercase station list, returns the board, and carries
      stations as a tuple of the six
ok    validate_board rejects a station list missing each of backlog/plan/ready/building/review/done
ok    validate_board refuses a declaration that renames each of the six stations
ok    validate_board refuses the six names rotated by 1..5
ok    validate_board refuses the pre-FEAT-41 six-key MAPPING
ok    validate_board's stations remedy names all six station names to write
ok    (X) validate_board rejects the five-station declaration carried before FEAT-33
ok    (X) validate_board rejects a seventh station that adds abandoned
ok    (X) feature-schema.json declares NO status key — the second vocabulary is gone
ok    (X) MANDATED_STATIONS is exactly the six lowercase stations, in board order
ok    (X) TERMINAL_MARKER is the lowercase terminal name and is NOT a seventh station
ok    station_column(...) exact-value checks for each of the six stations
ok    (X) every mandated station round-trips through station_column to a column that lowercases
      back to it
ok    station_column raises FleetError on 'abandoned'/'Done'/'Icebox'/''/'DONE'
ok    station_names returns the six mandated stations as a tuple
ok    board_for raises naming the file and the key: (eight malformed shapes)
ok    board_for raises when the product config declares no board
ok    board_for resolves through product_config
ok    product_config reads the remote at default_branch with no checkout on disk
ok    product_config raises naming repo, path and ref when the remote read fails
ok    product_config raises naming repo, path and ref when the remote content is not JSON
ok    product_config raises naming repo, path and ref when the remote content is a JSON list,
      not a mapping
ok    product_config never falls back to a checkout
ok    product_config never falls back to a checkout on disk when the remote read fails
ok    product_config memoises a successful read: a second board_for makes no second remote read
ok    product_config memoisation: a failing read is not cached and the next call succeeds
ok    (29) board_station returns the derived column for a station the repo's board declares
ok    (30) board_station raises FleetError on an unknown key
ok    (31) board_for on an unlisted repository raises FleetError
ok    (31) the message names the unlisted repository
ok    (20) FLEET_PATH is an absolute path
ok    (21) a HARNESS_PROJECT_DIR with no MARKER is discarded (x4 sub-checks)
ok    (22) workspace_path joins workspace_root with the name after the slash (x2 sub-checks)
ok    (23) --show over a good fleet exits 0, stdout is one JSON payload with 'repos' (x3)
ok    (24) --show over an invalid fleet: no stdout, one stderr line, exit 2 (x3)
ok    (X) SC-18 static fleet-reader enumeration self-test and assertions (x3)
ok    (X) issue #208: unparseable fleet.yaml raises FleetError, names the file path (x2)

114/114 checks passed.
```

(Full verbatim console text is reproducible by re-running the command; both counts above were
captured from the actual run via `grep -c '^FAIL '` on each script's own output file, not by
reading the tail of the chained command.)

### Chained verify string, run literally (with the mandated env prefix)

```
$ cd .../FEAT-56-central-onboarding-model && \
  env -u HARNESS_AGENT_TYPE python3 tests/unit/test-fleet-product-config.py && \
  env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-config.py
[... 15/15 then 114/114, printed above ...]
FINAL_EXIT:0
```

## 4. RED-CAPABILITY PROOF (ii) — mutant copy, case (e) reddens, (a)-(d) stay green

Built a temp copy OUTSIDE the worktree, under `/tmp/factory-config-mutant/` (a fresh
`mktemp`-style dir under the system temp root, never inside the worktree), containing only the
mutated `factory_config.py` — its dependencies (`factory_cli`, `factory_gh`,
`harness_boundary`, …) resolved from the real worktree bin dir via `sys.path` fallback, so only
`factory_config.py` itself differs from the real module. In that copy, deleted exactly:

```python
    if unreachable_count or len(report) != len(fleet["repos"]):
        sys.exit(factory_cli.EXIT_REFUSED)
```

Confirmed removed: `grep -n "sys.exit(factory_cli.EXIT_REFUSED)" /tmp/factory-config-mutant/factory_config.py`
returned no match (grep exit 1).

Pointed a copy of the test suite at the mutant module (`sys.path` prepended with the mutant dir,
`HARNESS_PROJECT_DIR` set to the real worktree root so `harness_boundary.resolve_root` still
finds `.harness/team-config.yaml`) and ran it:

```
ok    (a) two declared repos, both succeed -> every entry ok, ok count 2, unreachable 0
ok    (a)/(d) len(report) equals len(fleet['repos'])
ok    (b) the FIRST entry, asserted individually, is not ok and names repo and ref
ok    (b) the SECOND entry, asserted individually, is ok with an empty detail
ok    (b)/(d) len(report) equals len(fleet['repos'])
ok    (c) invalid JSON content -> entry not ok, detail names the invalid-JSON failure
ok    (c)/(d) len(report) equals len(fleet['repos'])
ok    every entry carries exactly repo/ref/path/ok/detail, path is _PRODUCT_CONFIG_PATH
ok    product_config_report preserves fleet['repos'] declaration order
FAIL  (e) --check-product-configs exits 2 (EXIT_REFUSED) under a failing stub
        (False, None)
ok    (e) stdout under failure parses as ONE JSON payload with declared/ok/unreachable/members
ok    (e) exactly one stderr line is written for the one unreachable member
ok    (e) --check-product-configs returns without SystemExit under an all-succeeding stub
ok    (e) stdout under success parses as ONE JSON payload with declared/ok/unreachable/members
ok    (e) no stderr line is written when nothing is unreachable

1 of 15 FAILING.
```

Post-change FAIL-line count under the mutant: **1** (`(e) --check-product-configs exits 2
(EXIT_REFUSED) under a failing stub`) — exactly the check coupled to the deleted `sys.exit` line.
Pre-change FAIL-line count (section 1 above): the whole run aborted on `AttributeError` before any
`FAIL`/`ok` line printed — 0 `^FAIL ` lines, 0 `^ok ` lines, a hard abort. All 14 other checks —
including every (a)/(b)/(c)/(d) check — stayed `ok`, and the SECOND (e)-payload/stderr checks
also stayed `ok` because they assert only shape, not the exit code. This is the predicted, single
discriminated failure: the gate is not vacuous.

The temp dir (`/tmp/factory-config-mutant/`) was removed afterward (`shutil.rmtree`).
`git status --porcelain` in the worktree, taken after cleanup, shows only:

```
 M .claude/skills/harness/bin/factory_config.py
 M .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
?? tests/unit/test-fleet-product-config.py
```

The `plan.yaml` line is NOT this task's write — I never opened plan.yaml for writing, and it is
outside T-04's declared `files:`. It is observed, not investigated further, consistent with
concurrent sibling/lead activity in the same worktree (the roster showed
`ShipCentralOnboarding.BuildT04` — harness-eng-lead — "Checkpointing run state before dispatch"
running concurrently). The receipt itself will be the third `??` entry once this file is written.
No other stray file exists; the mutant copy left nothing behind in the worktree at any point (it
was built entirely under `/tmp`).

## 5. Conventions check

Read `tests/unit/test-factory-config.py` in full before writing the new suite. Mirrored: the same
`_anchor_*` sys.path preamble, the same `FAILS`/`RAN`/`check()` accounting (including the
memo-clearing-as-first-statement convention), and the same `patched_file_at_ref` contextmanager
shape swapping `fc.factory_gh.file_at_ref` on the imported module object. No second convention
introduced.
