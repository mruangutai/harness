# FEAT-64 — build divergences ledger

Every deliberate byte difference between the compared corpus at `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` and the
build head, with the ruling. Anything not listed here is byte-identical (stdout digest, stderr digest and exit status
match — see `red-first-receipts.md`).

## A. Suite output differences (the 27 compared suites)

Twenty suites differ from the baseline, all in one of four additive ways; seven are byte-identical
(`test-gh-sync-abandon`, `-open`, `-record`, `-start-task`, `test-inflight-registry`, `test-run-unit-tests-kinds`,
`test-gh-sync-build-entry`).

| Kind | Where | Old bytes | New bytes | Ruling |
|---|---|---|---|---|
| A1 added case lines | every T-01/T-02/T-03 suite | — | `PASS`/`ok` lines carrying `FEAT-64`, `feat64`, `(n) …`, `hook_guard_…`, `linked_worktrees_…`, `run_dir_grant_globs_…`, `resolve_fleet_…`, `FEAT-64 BE-11/12` | red-first cases required by T-01/T-02/T-03; each was demonstrated red before its production edit (receipts) |
| A2 count lines | check-omp-port, upgrade-config, gh-cost-log, handoff-policy, check-skill-weight (stderr `Ran N tests`) | `26/26`, `12/12`, `39/39`, `20 passed`, `Ran 6 tests` | `27/27`, `13/13`, `43/43`, `21 passed`, `Ran 7 tests` | consequence of A1 |
| A3 retitled case | `test-board-station.py` case 7 | `PASS  board-station exits 0 when set_station raises a non-BoardError exception` | `PASS  board-station exits 0 when set_station's gh returns a body that does not decode (GhError)` | the old title pinned the broad catch; the fixture (a non-JSON exit-0 body) is unchanged and is now the documented `factory_gh.GhError` class. Same rc, same `ERROR -` line asserted |
| A4 corpus count | `test-harness-yaml-corpus.py` | `101 files across 2 roots: .harness=97` | `103 files across 2 roots: .harness=99` | FEAT-64's own `plan.yaml` and `feature.json` under `.harness/harness/features/` |
| A5 tmp paths on stderr | factory-decompose, harness-yaml, harness-boundary | `/T/tmpXXXX/…` | `/T/tmpYYYY/…` | `tempfile` names; not a byte the build controls |

## B. Production-behaviour differences (deliberate, outside the compared corpus' pins)

| # | File | Old | New | Ruling |
|---|---|---|---|---|
| B1 | `gh-sync.py` `first_open_child` | `raise RuntimeError(raw)` → operator line `… child list unreadable, card not moved: <gh stderr>` | `raise factory_gh.GhError(argv, None, "", raw, "sub-issue list unreadable", raw, "re-run ship once gh is reachable")` → `… card not moved: sub-issue list unreadable: <gh stderr> — re-run ship once gh is reachable` | T-02 intent: expose the typed class. `GhError.__init__` builds `str()` from `factory_cli.body`, so the line carries the canonical grammar. The suite pins `#40` and `child list unreadable` only; the card stays in the FAILED bucket |
| B2 | `board_lifecycle.py` `audit_findings` | `raise factory_gh.GhError("github.repo is not declared -- pin it …")` (ONE positional to a seven-parameter `__init__` — a `TypeError` at raise time, which ship's broad audit catch reported as "the board audit could not run: __init__() missing …") | seven-argument form: `GhError([], None, "", "", "github.repo is not declared", "harness.json", "pin it in harness.json before auditing")` | a latent defect the broad catch hid; the narrowed audit catch would have surfaced it as a traceback. Fixed in passing, one raise, no other line of the module touched. `board_lifecycle.py` is not in FEAT-64's file scope; recorded here for the reviewer |
| B3 | `factory_gh.run_gh` (T-01) → `test-board-lifecycle.py` c4 | a non-JSON exit-0 body reached `_fresh_board_station_field` / the link block as `ArtifactAccessError`, rendered `an UNEXPECTED ArtifactAccessError …` | `run_gh` converts it to `GhError` (chained), rendered `gh api graphql failed: … GitHub response: invalid JSON …` | the two c4 class-name pins (`"UNEXPECTED" in stderr and "ArtifactAccessError" in stderr`) asserted the pre-FEAT-64 leak. Replaced by `"invalid JSON" in stderr and "UNEXPECTED" not in stderr`; the exit-4 and `record 42` pins — the case's contract — are untouched. The KeyError/TypeError shapes named in c4's prologue still take the UNEXPECTED branch |
| B4 | `check-plan-routes.py` `MODULE_LOADER_HOME` | `("…/harness_boundary.py", "load_repo_module")` | `("…/harness_boundary.py", "_load_repo_module")` | T-01 made `load_repo_module` run its body inside `_as_repo_module_failure` (the ONE broad catch the load and call boundaries share, keeping harness_boundary at exactly two). FEAT-61 D-08's lock reports the *innermost* function around the `spec_from_file_location` call, so the home symbol is the private body. The invariant — one spec call under bin/ — is unchanged; the finding text still points callers at `load_repo_module`; the D-08 mutants in `test-check-plan-routes.py` still fail for their own finding |
| B5 | `harness_boundary.run_dir_grant_globs` | module-level `import harness_yaml` | function-local `import harness_yaml` | surfaced by `test-run-unit-tests-layout.py`: its fixture bin copies `harness_boundary.py` without `harness_yaml.py`, and the module-level import turned every fixture run into "no harness root could be resolved". Same lazy shape `resolve_fleet` already uses for `factory_config` |
| B6 | `run-unit-tests.py` `_resolve_root` | `except Exception: return ""` | `except (ModuleNotFoundError, ValueError): return ""` + FEAT-64 comment | T-02 intent; matches `check-state.py`'s copy from FEAT-63. The DEC-234 prologue comment above it is byte-for-byte; the four gate copies narrow in FEAT-65 |
| B7 | `post-merge-sweep.py` | per-record `except Exception` → `ERROR handling …` exit 0; module-level `except Exception` → `ERROR: …` exit 0 | both removed; `_run_step` converts `(OSError, subprocess.SubprocessError)` from the two child processes into the same `ERROR handling <path>: …` line and leaves the record standing | T-02 intent verbatim. `worktree_terminal.classify` already absorbs its own git failures; there is no other expected failure the removed catches were reached by |

## C. Comment moves

All silence rationales moved with their handlers byte-for-byte. New facts are separate prose marked `FEAT-64`
(board-station's module docstring paragraph; c4's prologue in `test-board-lifecycle.py`; `_load_plan_once`'s block;
`MODULE_LOADER_HOME`'s block; the `BROAD_CATCH_CEILINGS` block). The `run-unit-tests.py` DEC-234 prologue and its
reciprocal comment are unchanged.
