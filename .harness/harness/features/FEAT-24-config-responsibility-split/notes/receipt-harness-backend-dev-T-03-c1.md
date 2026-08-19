# Receipt — harness-backend-dev — T-03 (c1)

## Verdict

T-03's OWN verify: GREEN. All six touched files pass in full (114/114, 181/181, 64/64, 106/106,
113/113-across-six-sections, 30/30). The four verify-pinned ok-lines survive verbatim. No
existing assertion was weakened, deleted or renumbered. `test-check-domain.py`'s 113 is the sum
of its own six printed section totals (12+27+20+10+30+14), re-derived after the fix — an earlier
`grep -c "^ok\|^FAIL"` count of 117 in an intermediate pass included 4 lines that were `FAIL`, not
`ok`, before the board blocks were dropped; corrected here rather than left standing.

**The wider `bin/run-unit-tests.sh` sweep found one pre-existing failure outside my scope** —
`test-no-distribution.py`, two cases, caused by T-07's own fixture not yet matching the
`fleet.yaml` edit T-07 already landed on this branch (`d177bab`). Detail and evidence in section
12. Not mine to fix (`DO NOT TOUCH`); raised as a blocking `open_question`.

## 1. Verify-block cross-check

The verify block pasted in the dispatch is byte-identical to `plan.yaml` T-03's `verify:` field
(`plan.yaml:602-624`). No mismatch.

## 2. Re-derived site list

Re-grepped every file for `board:` at the dispatch's cited commit state (962417a + d177bab on
this branch). The dispatch's table was accurate; one correction: `test-factory-land.py`'s
`good_fleet_dict` board block is a Python dict literal (`:52-57`), not YAML text, same for
`two_repo_fleet_dict` (`:86-91`, `:96-104`). No sites beyond the dispatch's table were found.

| File | Sites confirmed |
|---|---|
| `test-factory-claim.py` | `repo_dict` (`:189-190`) — one shared builder, used by all per-repo fixtures |
| `test-factory-decompose.py` | `:157`, `:180`, `:192`, `:1108` (the `bad_fleet["repos"][0]["board"]...` mutation site — confirmed) |
| `test-factory-land.py` | `good_fleet_dict` (`:52-57`), `two_repo_fleet_dict` (`:86-91`, `:96-104`) |
| `test-factory-integration.py` | `fleet_dict` (`:350-354`), `:1013-1017`/`:1019-1025` (case H's `fleet_two`), `ready_option` read at `:660`→now `702` after edits |
| `test-check-domain.py` | `:458`, `:503`, `:555`, `:644` — confirmed exact |
| `test-factory-workspace.py` | `:53-58` (one `good_fleet_dict`) |

## 3. T-03 verify — literal output

```
--- test-factory-claim.py tail ---
ok    (P6) SC-13: exit code is EXIT_NOTHING (1), not a silent 0

114/114 checks passed.
--- test-factory-decompose.py tail ---
ok    (T-03) the station-validation read is against A's board and field, never B's

181/181 checks passed.
--- test-factory-land.py tail ---
ok    (T04-1) no gh call of any kind was recorded against B's board number

64/64 checks passed.
--- test-factory-integration.py tail ---
ok    (H) at least one recorded gh call names the served repository's own board number (proves the check above has power)

106/106 checks passed.
--- test-check-domain.py tail ---
ok    with the module absent AND no manifest, DEC-101 still fails OPEN, loudly

14/14 worktree-boundary cases passed.
T-03 GREEN
```

Zero `FAIL` lines across all five suites; all five exited 0.

## 4. `test-factory-workspace.py` — literal output (not run by T-03's verify)

```
ok    (A) missing checkout: exits 0
ok    (A) missing checkout: first call is clone
ok    (A) missing checkout: some later call checks out the issue branch
ok    (A) missing checkout: no fetch
ok    (B) existing checkout: exits 0
ok    (B) existing checkout: fetch is called
ok    (B) existing checkout: clone is never called
ok    (C) missing checkout: final command checks out the issue branch
ok    (C) existing checkout: final command checks out the issue branch
ok    (D) origin carries the ref: final checkout tracks origin
ok    (D) origin carries the ref: no command names both the issue branch and origin/<default_branch> together (the T-07 divergence bug)
ok    (E) origin has no ref: final checkout is created off origin/<default_branch>
ok    (F) existing local branch tracking origin: checked out as-is, not recreated with -b
ok    (F2) local branch diverges from origin (cut from default_branch): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (cut from default_branch): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (cut from default_branch): still exits 0 (repaired, not refused)
ok    (F2) local branch diverges from origin (no upstream at all): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (no upstream at all): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (no upstream at all): still exits 0 (repaired, not refused)
ok    (G) unlisted repo: exits 2
ok    (G) unlisted repo: zero git calls
ok    (H) a failing git command exits non-zero
ok    (I) happy path: stdout is exactly one JSON object
ok    (I) happy path: payload has path and branch
ok    (I) happy path: payload path is absolute
ok    (J) unlisted repo refusal: nothing on stdout
ok    (J) unlisted repo refusal: exactly one stderr line
ok    (J) unlisted repo refusal: that line names the repository
ok    (J) unlisted repo refusal: exits 2
ok    (K) a plain RuntimeError from run_git exits 2, not 1

30/30 checks passed.
```

## 5. What changed in `test-factory-workspace.py`

Dropped the `board:` block from `good_fleet_dict` (`:53-58` before, now `:53-59` with a comment).
`name` and `default_branch` are the only keys the fixture carries. Nothing else changed — grepped
the file for `board_for`, `product_config`, `board_station` and confirmed zero matches both
before and after the edit, matching the dispatch's own measurement. No stub was added because
nothing in this file resolves a board.

## 6. What changed in `_FAKE_GH_SRC`

**Symptom observed first, before any fix**: with `fleet_dict()`'s board removed and no stub
added, `(G2) -B --track form: workspace exits 0 against real git` (an unrelated case sharing the
fixture builder) turned into every decompose/claim/land case failing with
`factory: <tool>: fleet key invalid: repos[acme/widget].board — the board is no longer declared
in fleet.yaml`. Once `fleet_dict()` was fixed to drop `board`, the SAME cases instead failed with
`fake_gh: unhandled argv: ['api', 'repos/acme/widget/contents/.harness/harness.json', '-f',
'ref=main', '--jq', '.content']` — the fallthrough `bad()` at the bottom of `_FAKE_GH_SRC`'s
`main()`, confirming the `api` handler had no branch for `contents` before this task, exactly as
the dispatch predicted.

Three changes to `_FAKE_GH_SRC`:

1. **Added `import base64`** at the top of the stub script.
2. **Added a `repos/<owner>/<name>/contents/<path>` branch** inside the existing
   `if argv and argv[0] == "api":` block. It resolves the repo from the URL, looks up
   `state["product_configs"][repo]`, base64-encodes the JSON document, and returns it via
   `--jq .content` (matching `factory_gh.file_at_ref`'s exact argv shape) or as
   `{"content": ...}` otherwise. A repo with no staged config gets a `404` via `bad()` — fail
   loud, not fail open.
3. **Added `Backlog` and `Done`** to the graphql field-resolve `options` array and to the
   `item-edit` `mapping` dict, so D-06's five-key stations validate against a board that actually
   offers all five (decompose's `_validate_stations` checks every declared station, not just the
   three D-02-era names).

Also added a `product_configs` field to `write_state()`'s state dict (default:
`default_product_configs()`, a `{repo: {"github": {"board": <five-station board>}}}` mapping),
so every case that does not explicitly override it gets one for free.

## 7. The ledger

| File | Case | Disposition | Destination |
|---|---|---|---|
| `test-factory-integration.py` | `(D-config) success: payload carries repos, each with its own board, and no fleet-level board` — asserted `payload["repos"][0]["board"]["number"] == 9` | **INVERTED** (the one authorized exception) | Renamed to `(D-config) success: payload carries repos, and no board on either the fleet or any repos entry`; now asserts `"board" not in payload and "board" not in payload["repos"][0]` — pins absence at both levels instead of asserting a contract T-02 item 3 deleted |
| `test-factory-integration.py` | `ready_option = fleet_data["repos"][0]["board"]["stations"]["ready"]` (test-side helper, not an ok-line) | relocated | `ready_option = default_board()["stations"]["ready"]` — same value, read from the same fixture shape `product_configs` now serves |
| Every other case in all six files | board fixture source | **migrated** | Board now comes from `factory_config.product_config` (in-process files) or the fake gh `contents` endpoint (`test-factory-integration.py`), never `repos[].board`. Ok-line text unchanged in every case except the one inversion above |

No `removed` row lacks a destination.

## 8. Per-file summary

- **`test-factory-claim.py`**: `repo_dict` keeps `board` as a test-side-only carrier;
  `_split_boards` strips it before the fleet reaches disk and builds the map `run_main`
  monkeypatches `factory_config.product_config` with. `repo_board()` extended to the five-key
  stations map. Added the one authorized case, `factory_claim reads default_branch from the
  fleet entry before any clone exists`, asserting the recorded `default_branch_sha` branch
  argument equals the value read from the fleet fixture object itself (`db_fleet["repos"][...]`
  ). The fixture deliberately uses `default_branch="trunk-fixture"`, not the file's shared
  `DEFAULT_BRANCH` ("main") constant, so a call site hardcoding `"main"` instead of reading
  `entry["default_branch"]` cannot pass by coincidence.
  **Mutation proof**: mutated `factory_claim.py:355` from
  `factory_gh.default_branch_sha(repo_name, entry["default_branch"])` to
  `factory_gh.default_branch_sha(repo_name, "main")`, predicted only the new case would redden,
  ran the suite — `FAIL  factory_claim reads default_branch from the fleet entry before any
  clone exists` / `1 of 114 FAILING`, exactly as predicted — restored the file, re-verified the
  sha256 matched the pre-mutation value, and confirmed
  `git status --porcelain -- factory_claim.py` is empty. 114 checks, 0 failures.
- **`test-factory-decompose.py`**: module-scope `_STUB_BOARDS` dict + `product_config` stub +
  `write_fleet()` helper (splits board off before writing, registers it). `good_fleet_dict` and
  `two_repo_fleet_dict` extended to five stations; `Recorder.field_options` extended to five
  options (`_validate_stations` already validated all declared keys, unchanged source — this
  file's own board fixtures were previously under-specified for D-06). 181 checks, 0 failures.
- **`test-factory-land.py`**: same `_split_boards`/monkeypatch pattern as claim, inlined in
  `run_main` (this file's fleet is built once per call, not via a shared write helper).
  `good_fleet_dict`/`two_repo_fleet_dict` extended to five stations. 64 checks, 0 failures.
- **`test-factory-integration.py`**: `fleet_dict()` drops `board`; new `default_board()` /
  `default_product_configs()` helpers; `write_state()` gains a `product_configs` default; the
  fake `gh`'s `contents` endpoint and graphql options/mapping extended as in item 6. Case H
  builds two per-repo product configs explicitly so the "never names the other repository's
  board number" assertion still has power. 106 checks, 0 failures.
- **`test-check-domain.py`**: four `board:` blocks dropped, `default_branch` kept. No stub added
  — `resolve_fleet` never resolves a board. 117 checks across all sections, 0 failures.
- **`test-factory-workspace.py`**: one `board:` block dropped, no stub. 30 checks, 0 failures.

## 9. No-network-call rule — discharged

Re-derived with a pattern that catches every `base_env(...)` call omitting `gh_bin=`, not just
the two literal forms I first grepped for (that first pass missed (D-workspace)). The complete
set of `test-factory-integration.py` cases that run with `FACTORY_GH` unset (would resolve the
real `gh` on `PATH` if reached) is: (B) missing `--fleet` — the `claim` tool exits at fleet load,
before any gh call; (D-config) — `config --show` (`factory_config.py:349-351`) prints
`fleet["repos"]` verbatim and never calls `board_for`/`product_config`/`file_at_ref`, confirmed by
reading `factory_config._main`; (D-workspace), (G1), (G2) — the `workspace` tool only, which
`factory_workspace.py`'s own module docstring (lines 38-41) confirms imports neither `factory_gh`
nor `gh_issues`. Every other case that runs decompose, claim or land points `FACTORY_GH` at the
fake. No case added or touched by this task reaches a real network call.

## 10. `_STUB_BOARDS` reset property (`test-factory-decompose.py`)

`_STUB_BOARDS` is module-scope and mutated by `write_fleet()` on every call, keyed by repo name —
it has no per-case reset. The D4-4 typo case (`bad_fleet["repos"][0]["board"]["stations"]["ready"]
= "Redy"`) writes a poisoned board for `REPO` into it. This is safe only because the very next
fixture in file order that touches `REPO` (the T-03 two-repo case, `two_repo_fleet_dict`) also
calls `write_fleet()`, which overwrites `_STUB_BOARDS[REPO]` with a clean board before any
assertion runs. This is an ordering property, not a structural guard — a future case inserted
between D4-4 and the T-03 case that reused `REPO` without its own `write_fleet()` call would
silently inherit the typo'd board. Recorded here rather than left for the next author to
discover; not fixed, since T-02's own guidance for this file family (`clear_product_config_memo`)
targets the DIFFERENT contamination class of stale successful reads across cases, not a
test-side stub map, and restructuring `_STUB_BOARDS` into a per-call-site parameter is a larger
change than this task's add-nothing-else rule allows.

## 12. `bin/run-unit-tests.sh` sweep — a pre-existing red outside my scope, found and NOT touched

T-03's own verify covers five suites by name; T-02's intent states the stronger guarantee ("T-02
and T-03 land in ONE commit, so the red window never exists in recorded history"). I ran the full
registered suite (`bin/run-unit-tests.sh`) to check that guarantee, not just the five named
suites.

**Result: `test-no-distribution.py` FAILS**, with two cases —
`every_repo_declares_its_own_board` and `kaya_ai_is_paired_with_board_2` — both asserting that
the LIVE `.harness/factory/fleet.yaml`'s `mruangutai/kaya-ai` entry carries a `board:` block. It
does not: the on-disk `fleet.yaml` was already migrated to the boardless shape by `d177bab`
("[harness:t-07 part A item 1] The board leaves fleet.yaml") before my dispatch started, and
`test-no-distribution.py`'s own fixture, per `plan.yaml:57-62`, is carried in **T-07**
(`main-session-direct` lane, `DO NOT TOUCH` for me) specifically because it "asserts the shape
of the same fleet.yaml edit and splitting them would leave a red assertion between two tasks."
D-10 requires kaya's own PR (T-09) to merge before T-07 removes the board from `fleet.yaml`, and
per that same note the fleet.yaml edit landed ahead of `test-no-distribution.py`'s own fixture
update — the two are out of the order D-10 states.

I did not edit `test-no-distribution.py`, `fleet.yaml`, or `check-state.sh`, per the dispatch's
DO NOT TOUCH list. This failure predates my session: `fleet.yaml` and `d177bab` were both on the
branch before I started, and `test-no-distribution.py` imports none of the six modules or test
files I touched (`grep -n "^import\|^from"` shows only `os`, `re`, `subprocess`, `sys` — it reads
`fleet.yaml` directly, not through `factory_config`). Raised as a blocking `open_question` below;
T-03's own verify does not run this file, so `task_verify` for T-03 is unaffected, but a
full-suite claim of "the red window never exists" does not hold at this commit until T-07's own
fixture lands.

Every other suite `bin/run-unit-tests.sh` runs is green (197 `PASS` lines, one `FAIL` block —
`test-no-distribution.py`'s two cases above).

## 13. Scope note — sixth file

Per the dispatch, `test-factory-workspace.py` was migrated even though it appears in no task's
`files:` list. Reported here rather than silently absorbed.

## Files touched

- `.claude/skills/harness/bin/test-factory-claim.py`
- `.claude/skills/harness/bin/test-factory-decompose.py`
- `.claude/skills/harness/bin/test-factory-land.py`
- `.claude/skills/harness/bin/test-factory-integration.py`
- `.claude/skills/harness/bin/test-check-domain.py`
- `.claude/skills/harness/bin/test-factory-workspace.py`

No production code touched. Not committed — the pen is the lead's.
