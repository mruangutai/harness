# Grilling — check-state.py broad-exception sweep (wave 3) — 2026-09-21

## Destination
`check-state.py` carries zero `except Exception` clauses. Every remaining handler catches the
type its boundary actually raises; every silent handler has its reason written beside it; the
consolidation audit refuses a new broad catch and a new re-parse of a runner-shared source.
The eight `tests/integration/test-check-state*.py` suites keep their receipts except the ruled
divergences below.

## Mission
mission: plan
reason: the cause is known and the files are named, but the work adds an enforcement surface
(two audit rules), changes one grade from silent to loud (INV-23's budget fallback), and adds a
typed error to a shared boundary (`harness_boundary.load_repo_module`) that other scripts call.
confirmed-by: operator

## Settled
- Scope → `check-state.py`'s 47 sites only. The 121 sites in the other eleven bin/ scripts are
  a later wave; hooks have fail-open-by-design contracts that need their own rulings.
- Silent handlers → not consolidated into a shared handler: **the re-parse is deleted**. Eleven
  sites re-load `feature.json`/`harness.json` that `Ctx.record(feat)` / `Ctx._load_config` already
  parsed and already report once (INV-6; the harness.json validity violation). Each such row reads
  the context; a `None` doc means "skip — the context has already said why". No new finding.
- Environment boundaries → one `Ctx.spawn(argv)` returning the completed process or `None` on
  `(OSError, subprocess.SubprocessError)`; the DEC-138 "environmental precondition" comment lives
  there once. All twelve `subprocess.run` calls go through it (five are unguarded today and would
  crash the gate if `git` were absent). `gh auth status` becomes one cached `ctx.gh_ok()` (probed
  twice today, INV-26 and INV-30). The runner's second `git rev-parse` reads `ctx.git_top`.
- Board read (INV-26 `board_stations_for`) → keeps its documented silence, narrowed to
  `gh_board.BoardError`.
- Repo-module imports (seven `_invNN_import` sites, `Ctx.validate_digest`, INV-40's plan-merge
  load) → `harness_boundary.load_repo_module` wraps anything raised while loading into one typed
  `RepoModuleError`; callers catch that and keep reporting CANNOT RUN. The one broad catch lives
  at the boundary, outside check-state.
- Module-level `import handoff_done_when` (L82) → `ImportError`; its absence is a context-load
  finding (D-3 position), which INV-17 already prints.
- INV-23's `feature_schema` import (L1974) → `ImportError` and **reports** CANNOT RUN instead of
  grading with a hard-coded budget of 300 — the one behaviour change; ruled loud.
- `read()` (L99) → `OSError`; contract unchanged (absent or unreadable → `None`).
- Bootstrap `_resolve_root` (L48) → kept as designed (import fails → clean-interpreter probe);
  narrowed to `ImportError`, reason written.
- `station_of` (L128) → reads the context's parsed plan; `""` semantics for every unknowable case
  kept byte-for-byte.
- Loud reporters (~22) → narrowed to the loader's typed error: `FeatureJsonError`,
  `ArtifactAccessError`, `FleetError`, `YamlParseError`, the sibling module's own error class
  where it has one (`BoardError`, worktree_terminal's, check-skill-weight's) — verified per site.
- Frozen allowlist (ruled after dispatch, relayed to the planner) → the census lock also
  freezes every other bin/ script at its current broad-catch count (118 total at 950b2f04 by
  AST — `except Exception` or bare `except:`; the "121" first quoted was a text grep that
  counted comment mentions); above the frozen count is a finding, below is fine. Nobody adds
  a 119th while wave 4 is pending.
- Sequence → wave 3 (this) → wave 4 (the 118, hooks' fail-open contract ruled per hook) →
  the grader/review-skill extension, calibrated on the clean baseline.
- Locks → (1) `_SHARED_SOURCE_LOADERS` in check-plan-routes.py gains `load_feature_json` and
  `load_harness_json` (today `{"load_plan"}`, which is why the audit was green with sixteen
  re-parses present); (2) a census rule: `except Exception` (and bare `except:`) count in
  check-state.py is zero. Both red-first with mutants, like FEAT-62's.
- Receipts → byte-identity over the eight suites is the bar. Expected divergences, each a ruled,
  red-first entry in the build ledger: INV-23's new CANNOT RUN line when feature_schema is
  absent (only if a fixture provokes it); any fixture that relied on a silent skip now visibly
  skipping is NOT expected — a row that stops printing something is a defect.
- Comments → move with their code (the reason for each silence becomes the comment on the one
  place that silence now lives); never reworded.
- Build → main-session-direct under DEC-174; Harness plans, reviews and goal-checks.

## Not yet specified
- Whether `Ctx.spawn` also owns the `timeout=` values the gh calls pass today (60s on the
  milestone read) or leaves them per call.
- Whether `RepoModuleError` carries the original exception type name in its message (the
  CANNOT RUN lines print `type(e).__name__` today — the receipts decide).

## Out of scope
- The 118 broad-catch sites outside check-state.py (wave 4).
- Turning any environment silence into a finding — an offline machine must not red the gate.
- The grader/review-skill extension (the wave after).

## Facts I verified (so pm does not re-derive them)
- 47 `except Exception` handlers in check-state.py at 950b2f04; 25 swallow (assign/return/
  continue), 22 append a finding — census script over the AST, main session.
- 16 calls to `artifact_accessors.load_feature_json`/`load_harness_json` inside invariant bodies;
  `Ctx.record` and `Ctx._load_config` already parse both once and report the parse failure.
- 12 `subprocess.run` calls; 7 guarded, 5 not (L1397 git show, L1415 git log, L1666
  check-omp-port, L3771 git config, L4651 git status).
- Typed errors exist and wrap OSError/decode: `ArtifactAccessError`, `FeatureJsonError`,
  `FleetError` (artifact_accessors.py), `YamlParseError` (harness_yaml.py L37, L257),
  `BoardError` (gh_board.py L26).
- `_SHARED_SOURCE_LOADERS = {"load_plan"}` (check-plan-routes.py L1790).
- `harness_boundary.load_repo_module` is the sole `spec_from_file_location` in bin/ (FEAT-61
  D-08 lock) — the one place a typed load error can be minted.
- Per-file broad-catch census at 950b2f04 (AST; `except Exception` or bare `except:`):
  bash-write-guard 6, board-station 1, branch-create-gate 4, check-domain 24, check-omp-port 4,
  check-plan-routes 2, check-skill-weight 1, check-state 47, dispatch-guard 9,
  factory_decompose 1, feature-record 1, feature_schema 1, gh-close-gate 3, gh-sync 3,
  gh_cost_log 2, handoff_done_when 2, handoff_policy 1, harness_boundary 4, harness_yaml 3,
  inflight_registry 3, inject-expertise 2, merge-gate 5, plan-sign-gate 2, post-merge-sweep 5,
  run-unit-tests 2, run_identity 1, upgrade-config 1, validate-digest 18, worktree_terminal 7.
  Total 165; outside check-state 118. harness_boundary may move by one when RepoModuleError
  lands (T-01) — the allowlist is sized from HEAD when the lock lands (T-03), not from this list.
