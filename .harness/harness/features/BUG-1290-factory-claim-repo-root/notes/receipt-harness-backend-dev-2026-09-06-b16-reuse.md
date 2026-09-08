# REUSE angle — BUG-1290 B-16 simplify pass

**Verdict: empty pass.** No re-implementation found in the diff. Findings: `[]`.

## Checked and ruled out

1. **`_run_5b_scenario()`** (`tests/unit/test-factory-claim.py:1188-1205`) — builds its fleet
   entirely from existing fixture helpers already in this file: `good_fleet_dict`, `repo_dict`,
   `issue_data`, `board_item`, and dispatches through `run_main` (:403). It restates no fixture
   logic; it is the exact body 5b's `try:` block previously held, hoisted into a function so 5g
   can call it too. No lockstep-editing cost — there is exactly one copy of the scenario now,
   down from the implicit duplicate 5g would otherwise have needed to write inline.

2. **`_5b_property_holds()`** (`:1208-1223`) — a fresh predicate over `(code, out, err)` specific
   to this scenario's two-repo/one-feature-id shape (checks `issue == 952`, `"951" in err`,
   `"unresolvable blocker" in err`, `"no plan could be read" not in err`). Compared against the
   two candidates named in the dispatch: `_normalize_reason` (:971) normalises embedded issue
   numbers in skip-reason text for a pairwise-distinctness check — unrelated shape and purpose.
   `r3_case` (:616) builds and runs a two-issue R3 fixture, not a result predicate. Neither is
   restated here; this predicate owns a genuinely new assertion, not a duplicate of an existing
   one.

3. **`_FeatureOnlyIssueMapCache`** (`:1306-1313`) — subclasses the real `claim._BlockerCache`
   (`.claude/skills/harness/bin/factory_claim.py:82`) and overrides only `issue_number` (:132),
   collapsing its `(repo, feature)` key to `feature` alone via `super().issue_number(canonical,
   ...)`. It reaches the real seam (inherits and delegates to the production method) rather than
   reimplementing the cache's read/write logic — the alternative (a bespoke stand-in duplicating
   `_BlockerCache`'s internals) would be the actual REUSE violation, and this avoids it.

4. **The save/swap/restore-in-`finally` shape** at `:1315-1320` (`saved_blocker_cache =
   claim._BlockerCache; claim._BlockerCache = ...; try: ... finally: restore`) mirrors the
   idiom already used for `fc.features_root` inside `run_main` (:413-415, restored :441-443) and
   for `harness_yaml.load_plan` (:920). It is not, however, a call to a *named* helper the file
   already owns — `patch_gh`/`unpatch_gh` (:176-185) are specific to the fixed `PATCHED` list of
   `factory_gh` functions and do not generalize to an arbitrary single-attribute swap without
   themselves being rewritten. Inlining the same three-line idiom here is consistent with how the
   file already handles the `load_plan` case, not a new duplicate spelling of a generalizable
   helper. No finding.

## Not flagged (per shared context, out of scope for this angle)

- The differing `depends_on` fixture ids (T-88 kaya / T-99 harness) — recorded dead end.
- The `name_X` + try/except idiom — file-wide settled convention.
