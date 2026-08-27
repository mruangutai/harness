# T-04 receipt — harness-backend-dev

BLUF: `harness_root()` is deleted from `factory_config.py` and every production caller now
resolves through `harness_boundary.resolve_root(<own bin dir>)`. The override-return
normalisation landed with a RED-then-GREEN test. Both plan-verify greps are clean and the unit
suite is fully green. `--kind all` has exactly one real failure outside the anticipated 6
`[hook]` cases: `test-check-state.py` (4 sub-cases + module FAIL), caused by this same T-04
delete but blocked from repair by DEC-174 (it tests `check-state.sh`, a gate script). VERDICT is
FAIL for that reason — not because production code is wrong.

## What changed (production)
- `factory_config.py`: `harness_root()`/`_PROBE` deleted. `FLEET_PATH` now built from
  `harness_boundary.resolve_root(_BIN_DIR)`. `sys` import dropped (now unused).
- `board_lifecycle.py`: 5 call sites (`:671,922,934,1034,1121` at HEAD) repointed; `_BIN_DIR` +
  `import harness_boundary` added.
- `factory_claim.py`: `FEATURES_ROOT` repointed; `_BIN_DIR` added.
- `feature-worktree.py`: `resolve_repo("harness")` repointed via the existing lazy
  `_harness_boundary()` helper; `_BIN_DIR` added.
- `gh_cost_log.py`: `_log_path()` repointed; `_BIN_DIR` + `import harness_boundary` added
  (replaces `import factory_config`, which was used only for `harness_root()`).
- `worktree_terminal.py`: prose only (no production call sites, per plan intent) at :112-113,301.
- `harness_boundary.py`: `resolve_root`'s override branch wrapped in `os.path.abspath` (the
  normalisation). Stale prose in `resolve_fleet`'s lazy-import comment (describing
  factory_config's now-deleted CLAUDE_PROJECT_DIR/SPEC.md behaviour) rewritten to describe
  reality. Top-level imports still exactly `os, re, sys` (AST-verified, see digest).

## Unplanned repairs (necessitated by the delete, evidence-driven, not scope creep)
Discovered by actually running the suite, not by grep — the plan's own grep only found the bare
NAME `harness_root`, not the functional `CLAUDE_PROJECT_DIR`-keyed fixtures that depended on
`harness_root()`'s old CLAUDE_PROJECT_DIR-honouring, never-raises behaviour:
- `layout_migration.py` / `layout_fixtures.py`: removed the now-dead `factory_config.py` "docs"
  reader-table row — that file no longer builds any SPEC.md path at all, so no regex on its text
  can ever match again. Docs surface stays covered by its other two rows. **This is an audited,
  cross-feature (FEAT-20) governance table — flagged for lead review, not asserted as final.**
- `test-board-lifecycle.py`, `test-feature-worktree.py`, `test-worktree-terminal.py`,
  `test-post-merge-sweep.py`, `test-factory-integration.py`, `test-gh-sync.py`: fixtures that set
  `CLAUDE_PROJECT_DIR` and/or relied on `factory_config._PROBE`/SPEC.md to redirect root now set
  `HARNESS_PROJECT_DIR` and/or write `.harness/team-config.yaml` (MARKER), matching what
  `resolve_root` actually reads. One of these (`test-post-merge-sweep.py` case (i), a linked-
  worktree scenario) was a **real correctness bug**, not cosmetic: the old CLAUDE_PROJECT_DIR
  override was silently correcting for `feature-worktree.py`'s structurally-wrong owner_root in
  that scenario; without the swap, `remove` would refuse a real removal (verified: it failed
  loud, not silent — no destructive fail-open occurred).
- `test-context-watch-cli.py`: 3 prose sites reworded; the `HARNESS_ROOT_SLUG` constant left
  untouched as instructed (uppercase, case-sensitive grep does not match it).

## NOT fixed — DEC-174
`test-check-state.py` has the identical class of bug (2 fixtures lack `HARNESS_PROJECT_DIR`/
MARKER coverage: INV-27's "unjudgeable tree" case and INV-29's fleet-declared-repo/SC-17(c)
cases — 4 sub-case failures). `check-state.sh` is a gate script (explicitly listed off-limits in
my dispatch); its test is "their tests" under AGENTS.md's DEC-174 carve-out. I made the ONE prose
edit my dispatch explicitly authorized (renaming the bare `harness_root` mentions at :2479,:2553
so the plan's first verify grep is clean) and touched nothing else in that file — no logic, no
env vars, no fixture data.

## Verify — verbatim tail (full run, `--kind all`, this checkout)
```
FAIL - (x.2) an unjudgeable tree -> exit 1, INV-27 CANNOT VERIFY
      injection prerequisites are unset, and both degrade silently.
        VIOLATION  INV-31: core.hooksPath is unset, not .claude/skills/harness/hooks — no harness hook runs on this clone. Fix: git config core.hooksPath .claude/skills/harness/hooks
        note       no .harness/glossary.md — the domain's ubiquitous language is unrecorded (DEC-162). pm authors it, seeded from shipped features' pinned vocabulary.

ok - (x.3) an applicable clean tree -> NO INV-27 line
...
FAIL - INV-29 (e) a Done feature's worktree in a SECOND fleet-declared repository produces an INV-29 line from ONE run
...
FAIL - INV-29 (f.7) SC-17(c): the printed command RUNS and exits 0
      saw: exit=3 inside_fixture=True ...
FAIL - INV-29 (f.8) SC-17(c): and that worktree is GONE afterwards
      saw: exit=3 inside_fixture=True ...
FAIL test-check-state.py
```
This run's `test-validate-digest.py` showed 0 `[hook]` failures (registry was clean during the
run window) — `ALL PASSED`. The dispatch's warned-about 6 `[hook]` failures are a live-claim
artifact, not deterministic; when they DO appear they are exactly those 6 and nothing else, per
the lead's own measurement — I did not touch that file.

Grep clauses (byte-for-byte against the plan verify):
```
$ grep -rn "harness_root" $B/    -> no output, clean
$ grep -q "HARNESS_PROJECT_DIR" $B/factory_config.py -> no match, clean
```

## Test case that could no longer be expressed
`test-factory-config.py`'s case (21) tested factory_config's OWN three-tier CLAUDE_PROJECT_DIR
discard-and-fallback logic — that logic no longer exists in this file (delegated whole to
`harness_boundary.resolve_root`). Repointed to assert the equivalent HARNESS_PROJECT_DIR/MARKER
discard-and-fallback via `harness_boundary.resolve_root(fc._BIN_DIR)` directly, PLUS a new
assertion that `factory_config.FLEET_PATH` is built from that same resolved root — strengthening
rather than merely relocating the case. No case was deleted.
