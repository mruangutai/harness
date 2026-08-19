# REUSE angle — FEAT-25 simplify pass — receipt

BLUF: No REUSE findings. The diff adds one new file-reading seam (`_plan()`), one new blocker-gate
branch (`no_plan`), one new `READER_TABLE` row, and one new `STUB` entry — each either extends an
existing per-file mechanism in place (not a parallel reimplementation) or is a one-off idiom that
matches surrounding style without an importable equivalent already in the tree.

## What I checked, and found clean

1. **`_BlockerCache.plan_path()` / `_plan()` (`factory_claim.py:99-111`)** — builds
   `os.path.abspath(os.path.join(self._features_root, feature, "plan.yaml"))`. Checked
   `gh-sync.py` (lines 157-294) for an existing feature-dir → plan-path helper it might duplicate:
   `gh-sync.py` takes an already-resolved `feat_dir` argument and does inline
   `os.path.join(feat_dir, "plan.yaml")` at each call site — it is not a `features_root`+`feature`
   combinator itself, so there is no shared function being re-spelled here. No other module in
   `.claude/skills/harness/bin/*.py` exposes a `features_root(name) -> path` helper. Not flaggable.

2. **`os.path.abspath(...)` idiom** — grepped every non-test use of `os.path.abspath` in
   `bin/*.py` (board-station.py:50/101, check-plan-routes.py:495, factory_config.py:46,
   harness_boundary.py:125, gh-sync.py x4, merge-settings.py:227, layout_migration.py:219,
   render-map.py:151, upgrade-config.py:172, wayfind.py:49). Each is a local one-off, not an
   importable helper. `plan_path()`'s use matches the tree's existing style rather than
   duplicating a shared function.

3. **`no_plan` error message text (`factory_claim.py:190-199`)** — grepped for "does not exist" /
   "missing or unparseable" / "not readable" across `bin/*.py`: `check-plan-routes.py:385`,
   `gh-sync.py:218`, `wayfind.py:111` each have their own inline die/print message, no shared
   formatter exists anywhere in the tree. Not a restatement of an existing helper.

4. **`layout_migration.py`'s new `READER_TABLE` row for `factory_claim.py`** — this is the
   intended shape: every other reader in the table (check-plan-routes.py, check-state.sh, etc.) is
   its own `Row(...)` entry with the same two-regex shape by design; adding one more row is the
   mechanism working as built, not a duplicate of another row's content.

5. **`layout_fixtures.py`'s new `STUB["...factory_claim.py"]` entry** — same reasoning: STUB is a
   per-file dict by design (module raises at import if STUB keys and READER_TABLE keys diverge —
   LEAVE item 6), so one more entry is not reuse of an existing entry.

6. **Module-scope `FEATURES_ROOT` re-derivation in `test-factory-claim.py`** (the two `check()`
   calls right after `check()` is defined) — independently recomputes
   `os.path.join(fc.harness_root(), ".harness", "harness", "features")` to compare against the
   unpatched `claim.FEATURES_ROOT`. This looks like restating the constant, but it is the test's
   whole point per D-04 (an oracle independent of the constant it is checking) — flagging it would
   be arguing with a settled decision, not a REUSE finding.

No proposal is made; nothing to check against `verify:` clauses.
