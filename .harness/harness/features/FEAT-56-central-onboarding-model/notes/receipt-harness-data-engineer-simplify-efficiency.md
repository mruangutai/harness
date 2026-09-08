# EFFICIENCY angle — FEAT-56 simplify pass

**Verdict: clean. No findings.** All five questions answered below with evidence/measurement.

## 1. Is the memo reached on the paths that matter?

`product_config_report` (factory_config.py:328-353) loops `fleet["repos"]` once and calls
`product_config(fleet, name)` exactly once per member. `product_config`'s memo key is
`(repo_name, ref)` (factory_config.py:299-301) — within one report pass no key is ever inserted
before it is looked up again, so the memo genuinely never hits *inside* a report run. That is
correct, not waste: each member is read once because the report needs each member's config
once.

Where it pays for itself: `board_for` (factory_config.py:356+) calls `product_config` too, keyed
on the same `(repo_name, ref)`. `_check_product_configs` runs in the same Python process as
`_main()`, and after `--check-product-configs` populates `_product_config_memo` for every member
it touched, any LATER call to `board_for` for one of those same members *in that same process*
is served from the memo — zero extra network calls. But `_check_product_configs` calls
`_check_product_configs(...); return` (factory_config.py:487-491) and `_main()` returns
immediately after — no `board_for` call follows it in `_main()`'s own body. So within a single
CLI invocation of `factory_config.py --check-product-configs`, the warmed memo is never
consumed by anything else in that process — the process exits right after. The memo only pays
off for a caller that imports `factory_config` as a library and calls both
`product_config_report` and `board_for` in the same process (e.g. a future orchestrator script),
not for the CLI entry point added here. This is accurately described by the docstring at
factory_config.py:336-337 ("does not clear or consult the process memo itself") — it doesn't
claim the CLI path reuses it. Not a finding: the memo's failure-to-pay-off here is a property of
`_main()` doing nothing after the check, not of a bug in the report or the memo.

## 2. Per-member work that is loop-invariant?

Traced `product_config_report`'s loop body (factory_config.py:341-352): per member it reads
`entry["name"]`, `entry["default_branch"]`, calls `product_config`, and builds a dict literal.
`_PRODUCT_CONFIG_PATH` is read but not computed — it's a module-level string constant
(factory_config.py:269), so referencing it per iteration is a dict/attribute lookup, not
recomputed work. `ref` comes from `entry["default_branch"]`, which varies per entry by
definition (different repos can have different default branches) — not invariant. No
loop-invariant computation was found; nothing here could be hoisted out of the loop.

## 3. `--repo` narrowing: full-fleet scan before narrowing

`_check_product_configs` (factory_config.py:451-476) calls `repo_entry(fleet, repo_name)` first
(a linear scan over `fleet["repos"]` to validate the name), then narrows with a list
comprehension over `fleet["repos"]` again (factory_config.py:461) — two linear passes over the
same list before the real work starts.

Fleet size, read from `.harness/factory/fleet.yaml`: **2 declared repos**
(`mruangutai/kaya-ai`, `mruangutai/harness-factory-smoke`). Two linear scans of length 2 is 4
comparisons total, dwarfed by the one real network read `--repo` then makes. This is exactly
the case the dispatch pre-empts: "a list scan over a handful of entries, unmeasurable" — I
confirm that reading and do not flag it. Even at a fleet 100x larger (200 members), two O(n)
passes over an in-memory list of dicts is single-digit microseconds against a network round
trip measured in tens to hundreds of milliseconds; the ratio only gets more lopsided as fleet
size grows, since each additional member also adds an unavoidable network read that dominates
the walk cost by orders of magnitude.

## 4. Startup / hot-path cost

- **Import cost**: the diff adds one import (`import sys`, factory_config.py:31), a stdlib
  module already loaded by the Python runtime — zero incremental cost. No new import of
  `factory_gh` or any network-capable module was added to the top of the file (both were
  already imported pre-diff for `product_config`'s existing use). No module-level work runs at
  import time — `product_config_report`, `_check_product_configs` and the new argparse flags are
  all inside function bodies, not executed at import.
- **check-state.sh reachability**: grepped `check-state.sh` for `check-product-configs` and
  `check_product_configs` — zero matches. `check-state.sh` imports `factory_config` (lines 80,
  1888, 2028) only for `TERMINAL_MARKER` and `MANDATED_STATIONS`, both pre-existing module
  constants unrelated to this diff, and never calls `product_config_report`,
  `_check_product_configs`, or passes `--check-product-configs` anywhere. Confirmed by grep, not
  assumed: the dispatch's claim holds.
- Grepped every other caller of `factory_config` (`plan-merge.py`, `gh_board.py`,
  `worktree_terminal.py`, `harness_boundary.py`, `layout_fixtures.py`, `gh-sync.py`,
  `layout_migration.py`, `factory_workspace.py`, `check-plan-routes.py`,
  `check-domain.sh`, `post-merge-sweep.sh`, `feature-worktree.py`, `board_lifecycle.py`,
  `factory_decompose.py`, `factory_claim.py`, `factory_land.py`, `board-station.py`) — none of
  these reference `check-product-configs`/`check_product_configs`/`product_config_report`
  either. The new flag is reachable only by an operator invoking
  `factory_config.py --check-product-configs` directly; nothing runs it at session entry or on
  every write.

## 5. Test suite network calls and wall-clock

`tests/unit/test-fleet-product-config.py` never calls the real `factory_gh.file_at_ref`. Every
scenario goes through `patched_file_at_ref` (lines 52-61), a context manager that monkeypatches
`fc.factory_gh.file_at_ref` on the imported module object to an in-memory stub
(`stub_all_ok`, `stub_first_gherror_second_ok`, `stub_first_not_json_second_ok`) before calling
`product_config_report` or `fc._main()`, and restores the original after. No `gh` subprocess, no
socket, no `factory_gh` internals reached. `run_main` (lines 84-101) calls `fc._main()`
in-process, not via `factory_cli.run` or a subprocess — confirmed by reading the function body.

Measured wall-clock of the file's own run, subprocess-timed from outside the interpreter
(`env -u HARNESS_AGENT_TYPE python3 tests/unit/test-fleet-product-config.py`, invoked via
`subprocess.run` under `time.time()`): **0.125s**, all 15/15 checks passing, exit 0. That
includes CPython interpreter startup and module import, not just test body execution — a
fraction of a second, matching the dispatch's own "not a finding" bar exactly.

## Findings

`[]` — none. All five questions resolve to "no waste": the memo behaves as designed and simply
isn't consumed further within the single-shot CLI path (a property of `_main()`'s control flow,
not a defect); no loop-invariant work is repeated per member; the `--repo` double-scan is over a
2-entry list and unmeasurable against the network read it precedes; nothing runs at startup or
on any hot/session-entry path; and the test suite is fully faked with a 0.125s wall-clock run.
