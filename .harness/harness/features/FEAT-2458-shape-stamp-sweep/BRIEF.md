# BRIEF — FEAT-2458-shape-stamp-sweep Sweep finished features' shape-sweep stamps

## Problem

Every governed run leaves a per-feature high-water mark, `.harness/.shape-sweep-stamp.<FEAT>`, in
the main checkout (check-domain.py's post-mode sweep, #2026; DEC-180). Nothing ever deletes one. At
f8896091 the main checkout held 40 of them beside the plain `.harness/.shape-sweep-stamp`; 34 belonged
to features already finished on `main`, 5 to features with no directory on `main`, and 1 to live work
(grilling probe, `notes/grilling-shape-stamp-sweep-2026-11-23.md` in the main checkout). The files are
gitignored, so `git status` never shows them; they grow by one per feature forever, and the operator
can only tell which are safe to delete by re-running the landed-state classification by hand
(GitHub #2458).

## Done when — by perspective

**operator** — After a merge, the stamp of every feature that is finished on the default branch is
gone, and nothing else is touched: the shared stamp, a live feature's stamp and any stamp whose
feature cannot be classified all stay. Each stamp kept because it could not be classified is named
once, with the reason, and a dry run shows me what would go without deleting anything.

**code maintainer** — The post-merge hook and the INV-29 gate decide "is this feature finished on the
default branch" through one public predicate, and I find no second copy of that rule, nor of the
repository-argument helper, in the hook.

## Success criteria

- SC-01 (code maintainer): `worktree_terminal.classify_feature(root, feature_id)` returns a
  `(klass, reason)` pair with klass in `terminal`, `unresolved`, `not_terminal` and a non-empty
  reason: `terminal` for a feature landed at `done` and for a landed signed DEC-174 direct-build
  BRIEF; `not_terminal` for a feature landed at an unfinished station; `unresolved` whose reason
  does not contain `absent` for an unparseable landed `feature.json`, for a landed `feature.json`
  whose bytes are not valid UTF-8, and for a landed station outside the vocabulary; `unresolved`
  whose reason contains `absent` for an id with no landed directory, including an id that is a
  strict prefix of a different feature landed at `done` (exact id, never prefix). Each case is its
  own assertion in `tests/integration/test-worktree-terminal.py`, and qa shows that file red before
  `classify_feature` exists.
  verify: automated        evidence: integration
- SC-02 (code maintainer): a fleet feature whose directory lands only under
  `.harness/<fleet segment>/features/` resolves through the existing fleet segment list:
  `classify_feature` returns `terminal` when it landed at `done` there and `not_terminal` when it
  landed at an unfinished station, never `unresolved`/absent — including when
  `.harness/harness/features/` holds a different, longer id it is a prefix of. Asserted in
  `tests/integration/test-worktree-terminal.py` against a fixture fleet.yaml.
  verify: automated        evidence: integration
- SC-03 (operator): run without `--dry-run` against a fixture main checkout holding the plain
  stamp and stamps for a `done` feature, a `building` feature, a never-landed id (beside a
  different feature landed at `done` whose id it prefixes) and a feature whose landed
  `feature.json` is not valid UTF-8 (its stamp sorting before the `done` one), the sweep deletes
  the `done` feature's stamp and leaves the other four present with their bytes unchanged.
  Asserted in `tests/integration/test-post-merge-sweep.py`; qa shows the deletion assertion red
  before the sweep step exists.
  verify: automated        evidence: integration
- SC-04 (operator): with `--dry-run` on the same fixture, every stamp file (the plain stamp
  included) is still present with its bytes unchanged after the run, and the output names the
  `done` feature's stamp as one that would be removed. Asserted in
  `tests/integration/test-post-merge-sweep.py`.
  verify: automated        evidence: integration
- SC-05 (operator): on both the dry and the real run, the sweep output carries exactly one line
  naming the never-landed id's stamp, carrying `unresolved` and `absent`, and exactly one line
  naming the non-UTF-8 feature's stamp, carrying `unresolved` and not `absent`; no output line
  names the `building` feature's stamp. Asserted in `tests/integration/test-post-merge-sweep.py`.
  verify: automated        evidence: integration
- SC-06 (code maintainer): at `review_sha`, `git show <review_sha>:.claude/skills/harness/bin/post-merge-sweep.py`
  shows a stamp sweep that decides deletion only from `worktree_terminal.classify_feature`,
  reading no `plan.yaml`, `feature.json`, `BRIEF.md` or station name itself. The reviewer cites
  the stamp-sweep function.
  verify: inspection
- SC-07 (code maintainer): the route registry no longer carries the deleted helper:
  `check-plan-routes.py` `T07_TERMINAL_REMEDIES` has no
  `post-merge-sweep.py::_repo_arg_for_segment::load_fleet#1` key,
  `tests/integration/canonical-reader-classification.json` has no row with that id, and
  `tests/integration/test-check-plan-routes.py` passes at `review_sha` — its T-07
  terminal-contract case compares the registry, the inventory and the live AST, so a
  `post-merge-sweep.py` that still read the fleet through a private helper would fail it.
  verify: automated        evidence: integration
- SC-08 (code maintainer): at `review_sha`, `git show <review_sha>:.claude/skills/harness/bin/worktree_terminal.py`
  carries a module docstring whose public-surface line names `classify_feature` and
  `repo_arg_for_segment` beside `CLASSES`, `classify` and `classify_all`, and
  `post-merge-sweep.py` no longer claims that worktree_terminal exposes only `CLASSES` and `classify`.
  verify: inspection
- SC-09 (code maintainer): no integration regression: every pre-existing case in
  `tests/integration/test-worktree-terminal.py` (including its worktree prefix cases, whose
  semantics stay unchanged), `tests/integration/test-post-merge-sweep.py`,
  `tests/integration/test-check-plan-routes.py` and `tests/integration/test-checker-structure-locks.py`
  (whose live-tree census holds `post-merge-sweep.py` and `worktree_terminal.py` at zero broad
  catches) passes at `review_sha` (each exits 0 with no `FAIL` line at b788e9da, BRIEF pending).
  verify: automated        evidence: integration
- SC-10 (code maintainer): the unit-level locks on the changed files still hold:
  `tests/unit/test-broad-catch-census.py` (the ceiling table keeps both files at zero) and
  `tests/unit/test-no-distribution.py` (the sweep's main-checkout resolver survives) pass at
  `review_sha` (both exit 0 at b788e9da, BRIEF pending).
  verify: automated        evidence: unit

## Verification gaps

- none: every automated criterion rests on an active kind with a runner (`integration` for SC-01
  to SC-05, SC-07 and SC-09; `unit` for SC-10). `component` and `ui` are unresolved with no runner,
  but this feature touches no `.tsx`, story or browser surface they would cover. The real main
  checkout's stamp population is not a criterion: SC-03 to SC-05 carry the pre-merge proof on a
  fixture, and the operator may list `.harness/.shape-sweep-stamp*` after merge as a post-merge
  operational check, which gates nothing (DEC-74 makes UAT a pre-ship blocker, so no `uat`
  criterion is staged).

## Constraints

- BLOCKS — DEC-174: `post-merge-sweep.py` is a hook body, and `worktree_terminal.py` and
  `check-plan-routes.py` are gate-imported, so every task is `main-session-direct`; the main
  session builds and a human reads the diff (ticket #2458 R2, operator ruling).
- BLOCKS — FEAT-34 D-02 (the shared predicate recorded in `worktree_terminal.py`'s docstring): a
  stamp is deleted only when `classify_feature` reports its feature finished on the default branch
  by the existing landed rule (`_landed_classification`: landed `plan.yaml` station `is_finished`,
  or a signed DEC-174 direct-build BRIEF). No new rule, and no copy of the rule in the hook.
- SUPPLIES — DEC-180: the per-feature stamp is check-domain.py's high-water mark; a missing mark
  falls back to `SWEEP_WINDOW_S`, so deleting a finished feature's mark costs nothing. This feature
  does not change how check-domain.py writes or reads stamps.
- SUPPLIES — DEC-238: the sweep already removes stale pins and leaked `node_modules`, honouring
  `--dry-run`; the stamp step follows the same shape and sits beside them in `main()`.
- SUPPLIES — #2056: the fleet segment list (`_fleet_segments`, the list `_planning_segment` walks),
  so a fleet feature such as FEAT-01-kaya-platform under `.harness/kaya/features/` is found, not
  read as absent. A stamp names a full feature id, so `classify_feature` matches directory names
  exactly; the worktree-only unique-prefix rule (`_match_landed_id`) stays with `classify`.
- Absent folds into `unresolved` with a reason that says absent (operator's choice over a fourth
  `exempt_absent` result). The operator accepts that the three never-landed stamps (BUG-2110,
  FEAT-1559, FEAT-2081) print one line on every merge until someone deletes them.
- The plain `.harness/.shape-sweep-stamp` is never touched.

## Out of scope

- Deleting the stamp inside `feature-worktree.py remove` — the ticket rejected it: it misses the
  existing stamps, worktrees removed by hand, and direct builds with no worktree.
- Deleting the 3 never-landed stamps (BUG-2110, FEAT-1559, FEAT-2081) automatically — absent means a
  human decides.
- Changing how `check-domain.py` writes or reads stamps.

## Approval

status: pending
approved-by:
date:
