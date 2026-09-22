# FEAT-63 build divergences — the broad-exception sweep

Built main-session-direct (DEC-174). The bar (BRIEF SC-01, D-04): the eight
`tests/integration/test-check-state*.py` suites keep the receipts below except one ruled,
red-first divergence — INV-23 reporting CANNOT RUN when `feature_schema` is unimportable.

## Baseline receipts — at 950b2f04 (pin), worktree clean, run from the worktree root

sha256 of each stream, first 16 hex; every stderr is the empty-stream digest.

| suite | exit | stdout | stderr |
|---|---|---|---|
| `test-check-state.py` | 0 | `8fb2fb685ce1ec93` | `e3b0c44298fc1c14` |
| `test-check-state-entry.py` | 0 | `c1a7332f7b889f68` | `e3b0c44298fc1c14` |
| `test-check-state-plans.py` | 0 | `bf722335294598a6` | `e3b0c44298fc1c14` |
| `test-check-state-handoff.py` | 0 | `509f0d8ecf22dbca` | `e3b0c44298fc1c14` |
| `test-check-state-worktrees.py` | 0 | `9be634f33e8e2f5a` | `e3b0c44298fc1c14` |
| `test-check-state-inv26.py` | 0 | `be17fb78d64bdfe5` | `e3b0c44298fc1c14` |
| `test-check-state-records.py` | 0 | `7d82e406f1e5df9e` | `e3b0c44298fc1c14` |
| `test-check-state-feat59.py` | 0 | `a7108ea889731b1d` | `e3b0c44298fc1c14` |

(`records` differs from FEAT-62's pin only by the INV-46 label #1864 landed; `feat59`'s
receipt is the pre-FEAT-63 one — see the single divergence below.)

## After T-01 (b8fa0dfb) — receipts

All eight `SAME`. `test-check-state-table.py` ALL PASSED. `--consolidation-audit` 0 findings.
Broad catches in check-state.py: 47 → 27.

## After T-02 (0d9f2220) — receipts

Seven `SAME`; `test-check-state-feat59.py` stdout differs by exactly two ADDED lines, the new
cases `(63.a)` and `(63.b)` (diffed against the same suite run on the T-01 tree: `90a91,92`,
additive only; exit 0 both). Broad catches: 27 → **0**. Bare `except:`: 0.

## After T-03 — receipts

All eight as after T-02. The T-03 gate — `test-check-state-table.py` then
`test-check-plan-routes.py` then `--consolidation-audit` — green; 31 `feat62`/`feat63` mutant
cases pass. `code-grade.py --base 804d68b8`: 28 graded, 0 below bar.

## Ruled divergences

| id | what | where it shows | why | ruling |
|---|---|---|---|---|
| D-1 | INV-23 reports `note INV-23 CANNOT RUN for <feature.json>: feature_schema.py did not import (<Type>: <text>) …` instead of grading the whole file against a hard-coded 300-line budget. NOTE-level, the row's own severity. | Only when `feature_schema` fails to import: the new `case_feat63_inv23_import_boundary` (isolated bin copy with a raising `feature_schema.py`). No shipped fixture provokes it, so the eight receipts are otherwise unchanged. | Grilling 2026-09-21, ruled loud: a silently applied budget nobody maintained is the fail-open shape this wave removes. | Accepted; red-first (63.a red on the T-01 tree, green on T-02). |

## Plan deviations, disclosed

- **Twelve spawns → eleven through `Ctx.spawn`.** The twelfth is the bootstrap's clean-
  interpreter root probe (`_resolve_root`, before `Ctx` exists by construction); it keeps its own
  `_subprocess.run`, narrowed alongside its import guard to `(ImportError, ValueError)`. The plan's
  "all twelve" is therefore eleven plus one that cannot be routed.
- **`RepoModuleError` also covers a CALL boundary.** `harness_boundary.call_repo_module(module,
  attr, *args)` gives a sibling's raise the same type at call time (worktree_terminal
  `.classify_all`, check-skill-weight `.scan`, validate-digest `.validate`, layout_migration
  `.scan` after its own `LayoutTableError`): those siblings' contract is "never raises", so an
  exception out of them is a defect, and the existing comment at INV-29 says why a defect must
  not take every other invariant down with it. D-02 named load; the call boundary is the same
  decision applied to the same class of module. `load_repo_module` also imports BY NAME
  (`path=None`) so the seven `_invNN_import` helpers load through the one function.
  Both are one broad catch each, in harness_boundary — its post-T-02 count is 6 and the
  allowlist is frozen there (D-03: "observed post-T-01 count when T-03 lands" — the observed
  count when T-03 landed).
- **Eleven re-parses → deleted; four loud ones → `Ctx.record_error`.** INV-17/21/28/44 re-parsed
  feature.json to render their OWN parse finding beside INV-6's. Deleting them would drop a row
  (forbidden by D-04); re-parsing would trip SC-05's lock. `Ctx.record_error(feat)` hands them
  the exception the context's one parse raised, so the bytes are identical and the parse
  happens once.
- **The reads lock learned `spawn`.** With every git/gh read behind `Ctx.spawn`, FEAT-62's
  `_SPAWN_CALLEES` no longer saw them and the resource lock went blind (its own misdeclared-
  resource mutants went green for the wrong reason). `spawn` is added to the callee set; the live
  table passed unchanged, i.e. every row's `git:`/`gh:` declaration still matches what it spawns.
- **Order of context loads.** `_load_config` now runs before `_load_eras` (eras read the parsed
  config). The only observable interleave — the config-invalid finding vs. an era finding — cannot
  co-occur: an invalid config resolves no era.
- **`Ctx` is built before the selection is resolved** so `--changed` reads the dirty tree through
  the context's boundary and its one `git rev-parse`. Building it prints nothing; a selector
  error still exits before any finding (table suite unchanged).

## The census, sized at landing (T-03)

check-state.py 0. Frozen: bash-write-guard 6, board-station 1, branch-create-gate 4,
check-domain 24, check-omp-port 4, check-plan-routes 2, check-skill-weight 1, dispatch-guard 9,
factory_decompose 1, feature-record 1, feature_schema 1, gh-close-gate 3, gh-sync 3,
gh_cost_log 2, handoff_done_when 2, handoff_policy 1, **harness_boundary 6** (4 + the load and
call boundaries), harness_yaml 3, inflight_registry 3, inject-expertise 2, merge-gate 5,
plan-sign-gate 2, post-merge-sweep 5, run-unit-tests 2, run_identity 1, upgrade-config 1,
validate-digest 18, worktree_terminal 7. Total outside check-state: 120 (118 legacy + 2 minted
here). Wave 4 burns it down.
