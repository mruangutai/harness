# Receipt — harness-backend-dev — T-02 — c1

## BLUF
`factory_claim._main` no longer reads a single fleet-level board. Everything board-shaped —
station validation, the targeted `--issue` lookup, the poll query, and the winner-only
`project_field_set` — is now scoped per repository, resolved through
`factory_config.board_for(fleet, repo_name)`. A two-repo fleet on two different boards polls
both, claims off the repository the winning candidate was actually found on, and an empty
`--repo`-filtered poll reports "no work available" (exit 1) rather than falling through to a
silent success. `test-factory-claim.py`'s fixture is migrated to the per-repo board shape and
carries 6 new cases (17 new checks) proving the per-repository scoping against recorded gh call
arguments, not just call counts.

## Restructure, as implemented
1. **Served repos** — `repos_to_serve`: every `fleet["repos"]` entry, filtered to `--repo` when
   given. An unknown `--repo` propagates `factory_config.repo_entry`'s own `FleetError`
   ("repository not in fleet") — no second message written.
2. **Per-board resolve + validate** (`factory_claim.py:218-238`) — for each served repo,
   `factory_config.board_for` resolves its board, then the same three-station validation runs
   against THAT board, naming that repo's `owner`/`project {number}` in the refusal. The
   superseded whole-run-invariant comment was replaced with the per-board invariant that now
   holds, moved with the code (task's explicit MOVE instruction).
3. **Reads** (`:240-269`) — targeted mode: one `issue_board_item_id` call per served repo, in
   fleet order, first non-`None` id wins; a miss now names every board searched
   (`", ".join(dict.fromkeys(...))`, ordered, deduplicated). Poll mode: one `project_items` call
   per served repo, each query built from that repo's own `station_field`/`ready` option.
4. **Merge, de-dup, tie-break** (`:271-290`) — candidates keyed on `(repo_name, issue_number)` via
   `_repo_name_of(item)` (unchanged helper), de-duplicated before the sort, then sorted on
   `(issue_number, repo_index)` where `repo_index` is the repository's position in
   `fleet["repos"]` — the documented tie-break, stated in a comment.
5. **Candidate loop** (`:295-`) unchanged; it was already repo-scoped via `entry =
   factory_config.repo_entry(fleet, repo_name)`, so no board value was read inside it.
6. **Step 6 rebind** (`:373-`) — `winner_board = boards[repo_name]` (the WINNER's own tag, from
   the `winner` tuple), never the last repo the per-repo loop visited. `project_field_set` now
   takes all four values (`owner`, `number`, `station_field`, `stations["building"]`) from
   `winner_board`.

## Test migration
`good_fleet_dict` moved to the per-repo shape (`repo_dict`/`repo_board` helpers); every existing
case runs against it unchanged (96 pre-existing checks stayed green). Added `REPO_B`/`BOARD_B`/
`STATION_FIELD_B` and two new fleet builders (`two_repo_fleet`, `same_board_two_repo_fleet`), and
extended `Recorder` with `board_field_options`/`items_by_board` (keyed by `(owner, number)`,
falling back to the old single-board dicts) so a test can give two boards different option sets
or item lists without touching any existing case.

New section **P** (6 cases, 17 checks), each asserting on recorded gh call arguments per P-14/
G-02 discipline, not just counts:
- **P1** — poll queries both boards; each query's field/ready-option text is board-specific.
- **P2** — a candidate on repo A is claimed with exactly one `project_field_set` call, addressed
  to A's `(owner, number)`, never B's.
- **P3** — station validation failing on repo B names B's `owner project {number}` and NOT A's.
- **P4** — `--repo` filters served repos: every `project_field_options`/`project_items` call
  targets only that repo's board.
- **P5** — two entries sharing one board number: two `project_items` calls recorded (both entries
  query it), but `issue_view` runs once and `project_field_set` runs once — the duplicate never
  entered the candidate loop.
- **P6 (SC-13's sole evidence)** — a two-board fleet, `--repo` naming the one with an empty ready
  station: `stdout == ""`, `"no work available"` on stderr, exit `factory_cli.EXIT_NOTHING` (1).

## TDD discipline note (disclosed per P-13)
Production code for this task was written before the new P-cases were added — out of order (same
lapse pattern as T-01, disclosed there too). Reconstructed RED honestly: hashed the edited
`factory_claim.py` (`sha256: 5d02c4c4a45ed4f246fe7adb2a9064979e4ea2ea7e62240b478061cc16eccb50`),
swapped in `git show HEAD:` (the pre-task version, which still reads `fleet["board"]`
unconditionally), and ran the already-written `test-factory-claim.py` against it with the new
per-repo-only fixture. The old code's `fleet["board"]` read raised `KeyError` on the very first
case (M1) — an unhandled exception, trapped by `factory_cli.run`'s wrapper, exits 2 not 1 — and
the failure cascaded through nearly every case (M1/M2/M3/M6/M7/M8 all failed, several with
tracebacks from `json.loads("")`) before the run itself crashed on an unrelated `json.loads`
call. That is unambiguous RED: the pre-task loader cannot serve the new fixture shape at all.
Restored the edited file, re-verified the hash matched
(`5d02c4c4a45ed4f246fe7adb2a9064979e4ea2ea7e62240b478061cc16eccb50`, unchanged), and confirmed
`git status --porcelain` showed only the intended two-file diff. Then ran GREEN: 113/113 checks
pass in `test-factory-claim.py` standalone, and the full unit suite below.

## tests_added
17 new checks (6 new cases, P1-P6). 96 pre-existing checks in this file stayed green against the
migrated fixture (113 total, up from 96).

## Verify — exact command, VERBATIM output

Command:
```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Full verbatim stdout+stderr is long (741 lines); the load-bearing lines for this task:

```
...
73/73 checks passed.
PASS test-factory-config.py
...
113/113 checks passed.
PASS test-factory-claim.py
...
ALL PASS
PASS test-validate-feature-json.py
EXIT=0
```

No `FAIL` line appears anywhere in the run (`grep -c FAIL` over the captured output returns 0,
excluding the word "FAIL" that never occurs — verified by grep). `EXIT=0` confirms the whole
suite passed. (The `factory: decompose: unexpected failure: RuntimeError: boom...` line mid-run
is expected stderr from a fault-injection fixture inside `test-factory-decompose.py`, unrelated
to this task, immediately followed by `PASS test-factory-decompose.py`.)

## HARD BOUNDS respected
- `.harness/factory/fleet.yaml` not touched (T-07's).
- `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-state.sh` not touched
  (DEC-174 carve-out).
- `factory_config.station(fleet, key)` (two-argument form) untouched — still present, unused by
  this task.
- `factory_config.py` not touched.

## Open items for downstream
- T-03/T-04 (factory_decompose, factory_land) still read `fleet["board"]` directly today (not
  this task's files) — unaffected by this change since this task only touched `factory_claim.py`
  and its test.
- No defect found in `factory_config.py` from T-01 that would need reporting per this task's
  instructions.
