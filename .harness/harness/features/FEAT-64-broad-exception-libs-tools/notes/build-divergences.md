# FEAT-64 — build divergences ledger

Every deliberate byte difference between the compared corpus at `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` and the
build head, with the ruling. Anything not listed here is byte-identical (stdout digest, stderr digest and exit status
match — see `red-first-receipts.md`).

## A. Suite output differences (the 27 compared suites)

**Exact bytes: `notes/byte-evidence.md`** (validate c0, GC-64-01). For every suite it records the raw and the
normalised digests of both streams and prints EVERY differing line verbatim, zero context. "Normalised" means
exactly two substitutions — the tree's absolute path → `<ROOT>`, a `…/T/tmpXXXXXXXX` tempfile directory → `<TMP>` —
and nothing else. Across all 27 suites exactly EIGHT lines are removed; every one is listed below with its
replacement. Everything else that differs is an added line. stderr is normalised-identical in 26 suites; the
27th is `test-check-skill-weight.py` (unittest's own progress dots and `Ran N tests`, A2).

| Kind | Suite | Old bytes (removed) | New bytes | Ruling |
|---|---|---|---|---|
| A3 retitled case | `test-board-station.py` | `PASS  board-station exits 0 when set_station raises a non-BoardError exception` | `PASS  board-station exits 0 when set_station's gh returns a body that does not decode (GhError)` | the old title pinned the broad catch; the fixture (a non-JSON exit-0 body) is unchanged and is now the documented `factory_gh.GhError` class. Same rc, same `ERROR -` line asserted |
| A2 count | `test-check-omp-port.py` | `26/26 cases passed` | `27/27 cases passed` | +1 FEAT-64 case |
| A2 count (stderr) | `test-check-skill-weight.py` | `......` / `Ran 6 tests in 0.019s` | `.......` / `Ran 7 tests in 0.020s` (the duration varies per run on both trees) | +1 FEAT-64 unittest case |
| A2 count | `test-upgrade-config.py` | `12/12 cases passed.` | `13/13 cases passed.` | +1 |
| A2 count | `test-gh-cost-log.py` | `39/39 checks passed` | `43/43 checks passed` | +4 |
| A2 count | `test-handoff-policy.py` | `20 passed, 0 failed` | `21 passed, 0 failed` | +1 |
| A4 corpus count | `test-harness-yaml-corpus.py` | `ok    every shipped YAML parses (101 files across 2 roots: .harness=97, .claude/skills/harness/teams=4)` | at a CLEAN checkout of `220feabb` (the sha `byte-evidence.md`'s header names): `ok    every shipped YAML parses (104 files across 2 roots: .harness=100, .claude/skills/harness/teams=4)` | the corpus is every tracked `*.yaml`/`*.yml` under `.harness/` (JSON is not counted). `git diff --name-status a4a3d7f8 220feabb -- '.harness/**/*.yaml' '.harness/**/*.yml'` adds exactly THREE, all FEAT-64's own record: `…/FEAT-64-broad-exception-libs-tools/plan.yaml`, `…/runs/validate-validator/state.yaml` (c0 panel), `…/runs/validate-c1-validator/state.yaml` (c1 panel). Every later committed `runs/validate-cN-validator/state.yaml` raises the count by one more; the commits after `220feabb` up to the pin touch only notes and `feature.json`, so the count at the pin equals this one. (validate c1 GC-64-04: the earlier text named `feature.json` and an evidence run made in a working tree holding the untracked `runs/plan-product/state.yaml` — both corrected from the recorded delta.) |
| A1 added lines | every T-01/T-02/T-03 suite | — | the `PASS`/`ok` rows listed verbatim in `byte-evidence.md` under each suite | red-first cases required by T-01/T-02/T-03; each demonstrated red before its production edit (receipts §2) |
| A5 tempfile names | factory-decompose, harness-yaml, harness-boundary (stderr) | `/T/tmpXXXX/…` | `/T/tmpYYYY/…` | `tempfile` names; `byte-evidence.md` shows the normalised stderr digests EQUAL for all three, so the path is the only difference |

Seven suites are byte-identical raw: `test-gh-sync-abandon`, `-open`, `-record`, `-start-task`, `test-inflight-registry`,
`test-run-unit-tests-kinds`, `test-gh-sync-build-entry`.

## B. Production-behaviour differences (deliberate, outside the compared corpus' pins)

| # | File | Old | New | Ruling |
|---|---|---|---|---|
| B1 | `gh-sync.py` `first_open_child` | `raise RuntimeError(raw)` → operator line `… child list unreadable, card not moved: <gh stderr>` | `raise factory_gh.GhError(argv, None, "", raw, "sub-issue list unreadable", raw, "re-run ship once gh is reachable")` → `… card not moved: sub-issue list unreadable: <gh stderr> — re-run ship once gh is reachable` | T-02 intent: expose the typed class. `GhError.__init__` builds `str()` from `factory_cli.body`, so the line carries the canonical grammar. The suite pins `#40` and `child list unreadable` only; the card stays in the FAILED bucket |
| B2 | `board_lifecycle.py` `audit_findings` — **REVERTED** (validate c0, CR-64-01/GC-64-03; operator ruling: out of FEAT-64's signed files) | `raise factory_gh.GhError("github.repo is not declared -- pin it …")` — ONE positional to a seven-parameter `__init__`, a `TypeError` at raise time | unchanged: the file is byte-identical to `a4a3d7f8` | the defect is filed as **#1897**. What FEAT-64 DOES change on that path (board declared, `github.repo` absent) is the ship audit's handling of it, measured with `_resolve_board` stubbed to `(None, <board>)` and `gh-sync._ship_audit("acme/widget")`: baseline returned with stderr `gh-sync: ERROR - the board audit could not run: GhError.__init__() missing 6 required positional arguments: 'status', 'stdout', 'stderr', 'what', 'value', and 'next_step'\n`; head raises `TypeError` with the same message and prints nothing — the narrowed audit catch (T-02 intent) no longer hides a programming defect. Ruling: this is the exposure the feature exists for; the fix lands in #1897's own lane |
| B3 | `factory_gh.run_gh` (T-01) → `test-board-lifecycle.py` c4 (stays after B2's revert: it pins T-01's signed `run_gh` change, not B2) | a non-JSON exit-0 body reached `_fresh_board_station_field` / the link block as `ArtifactAccessError`, rendered `an UNEXPECTED ArtifactAccessError …` | `run_gh` converts it to `GhError` (chained), rendered `gh api graphql failed: … GitHub response: invalid JSON …` | the two c4 class-name pins (`"UNEXPECTED" in stderr and "ArtifactAccessError" in stderr`) asserted the pre-FEAT-64 leak. Replaced by `"invalid JSON" in stderr and "UNEXPECTED" not in stderr`; the exit-4 and `record 42` pins — the case's contract — are untouched. The KeyError/TypeError shapes named in c4's prologue still take the UNEXPECTED branch |
| B4 | `check-plan-routes.py` `MODULE_LOADER_HOME` | `("…/harness_boundary.py", "load_repo_module")` | `("…/harness_boundary.py", "_load_repo_module")` | T-01 made `load_repo_module` run its body inside `_as_repo_module_failure` (the ONE broad catch the load and call boundaries share, keeping harness_boundary at exactly two). FEAT-61 D-08's lock reports the *innermost* function around the `spec_from_file_location` call, so the home symbol is the private body. The invariant — one spec call under bin/ — is unchanged; the finding text still points callers at `load_repo_module`; the D-08 mutants in `test-check-plan-routes.py` still fail for their own finding |
| B5 | `harness_boundary.run_dir_grant_globs` | module-level `import harness_yaml` | function-local `import harness_yaml` | surfaced by `test-run-unit-tests-layout.py`: its fixture bin copies `harness_boundary.py` without `harness_yaml.py`, and the module-level import turned every fixture run into "no harness root could be resolved". Same lazy shape `resolve_fleet` already uses for `factory_config` |
| B6 | `run-unit-tests.py` `_resolve_root` | `except Exception: return ""` | `except (ModuleNotFoundError, ValueError): return ""` + FEAT-64 comment | T-02 intent; matches `check-state.py`'s copy from FEAT-63. The DEC-234 prologue comment above it is byte-for-byte; the four gate copies narrow in FEAT-65 |
| B7 | `post-merge-sweep.py` | per-record `except Exception` → `ERROR handling …` exit 0; module-level `except Exception` → `ERROR: …` exit 0 | both removed; `_run_step` converts `(OSError, subprocess.SubprocessError)` from the two child processes into the same `ERROR handling <path>: …` line and leaves the record standing | T-02 intent verbatim. `worktree_terminal.classify` already absorbs its own git failures; there is no other expected failure the removed catches were reached by |

## C. Comment moves

All silence rationales moved with their handlers byte-for-byte. New facts are separate prose marked `FEAT-64`
(board-station's module docstring paragraph; c4's prologue in `test-board-lifecycle.py`; `_load_plan_once`'s block;
`MODULE_LOADER_HOME`'s block; the `BROAD_CATCH_CEILINGS` block). The `run-unit-tests.py` DEC-234 prologue and its
reciprocal comment are unchanged.
