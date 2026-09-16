# Receipt — harness-backend-dev — T-03 — c1

## Result
GREEN. All three verify suites exit 0; `FEATURES_ROOT` is absent from `factory_claim.py`.

## Changes (exactly the three files T-03 names)

- `.agents/skills/harness/bin/factory_config.py` (edited via its hardlinked, git-tracked twin
  `.claude/skills/harness/bin/factory_config.py`): added `segment_of(repo_name)` and
  `features_root(repo_name)` beside `workspace_path`. `features_root` binds `seg = segment_of(repo_name)`
  to a paren-free local before the `os.path.join(harness_boundary.resolve_root(_BIN_DIR), ".harness",
  seg, "features")` call, per A-01 — no inline `segment_of(repo_name)` call inside the join. No new
  import added; reused existing `_BIN_DIR` and `harness_boundary` import. `workspace_path` rewritten to
  call `segment_of` instead of restating `repo_name.split("/", 1)[-1]`; its docstring corrected to
  attribute the "one place that derivation exists" property to `segment_of`. `harness_boundary.py` not
  touched.
- `.agents/skills/harness/bin/feature-worktree.py`: `resolve_repo` (:64-87) now computes
  `segment = factory_config.segment_of(repo)` instead of the inline `repo.split("/", 1)[-1]`. The
  `repo == "harness"` early return (:67-69) is untouched — it still returns the literal `"harness"`
  segment before reaching any shared call. Return contract `(owner_root, segment, default_branch)`
  unchanged.
- `.agents/skills/harness/bin/factory_claim.py`: deleted the `FEATURES_ROOT` module global and its
  "Overridable for tests" comment, and the docstring paragraph describing the hardcoded
  `.harness/harness/features` resolution. No alias, no fallback, no new refusal path introduced.
  `_BlockerCache` no longer takes a features root at construction (`_BlockerCache()`, construction site
  updated at the former :341/:334); every method now takes `repo` and resolves the root per call via
  `factory_config.features_root(repo)`. `_plans` and `_issue_maps` are now keyed on the `(repo, feature)`
  tuple, never on `feature` alone (D-02). `plan_path`'s path stays `os.path.abspath(...)`. `root_exists`
  now takes `repo` and checks that repo's own resolved root, so the existing `no_plan` reason still
  names the exact path tried for that candidate. `_blocker_gate` (which already received `repo` as a
  parameter) now threads it through every cache call: `plan_loaded`, `plan_path`, `root_exists`, `task`,
  `issue_number`.

`_BIN_DIR` and the `harness_boundary` import in `factory_claim.py` are left in place even though they
are now otherwise unused inside that module — the task's cited deletion range (`FEATURES_ROOT` global
and its comment) explicitly excluded `_BIN_DIR`'s own line, so this is an intentional scope boundary,
not an oversight. Flagging as an observation, not fixing (out of T-03's named scope).

## Hardlink check

`stat -f '%i'` on both the `.claude/...` and `.agents/...` paths, run after each edit:

```
factory_claim.py:    203802709 / 203802709  (match)
factory_config.py:   203802711 / 203802711  (match)
feature-worktree.py: 203802718 / 203802718  (match)
```

All three inode pairs match — the hardlink survived every edit.

## Verify command (run verbatim, exit 0)

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root && python3 tests/unit/test-factory-claim.py && python3 tests/integration/test-factory-integration.py && python3 tests/integration/test-feature-worktree.py && python3 -c "import sys; t = open('.agents/skills/harness/bin/factory_claim.py').read(); sys.exit(1 if 'FEATURES_ROOT' in t else 0)"
```

Output tallies:

- `tests/unit/test-factory-claim.py`: **124/124 checks passed**, exit 0. Includes, verbatim:
  ```
  ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
  ok    BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
  ok    BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
  ok    BUG-1290 5d: owner-qualified name ending in harness resolves to .harness/harness/features
  ok    BUG-1290 5e: factory_claim exposes no FEATURES_ROOT attribute
  ok    BUG-1290 5f: the owner-strip derivation lives in exactly one place, factory_config.py
  ```
  All six `BUG-1290 5a`..`5f` cases are `ok`; zero `FAIL` lines anywhere in the output.
- `tests/integration/test-factory-integration.py`: **131/131 checks passed**, exit 0. Includes,
  verbatim: `ok    (F) claim exits 0` and `ok    (H) claim against the two-board fleet exits 0` —
  T-02's two claim cases are now `ok`, not `FAIL`.
- `tests/integration/test-feature-worktree.py`: all `PASS` lines, ends `PASS test-feature-worktree.py`,
  exit 0.
- Final `python3 -c ...` FEATURES_ROOT-absence check: exit 0 (the string is absent).
- Combined `&&`-chained command: `OVERALL_EXIT=0`.

## Acceptance checklist

- `segment_of` and `features_root` at module level in `factory_config.py`; `features_root` binds `seg`
  to a paren-free local before the join (A-01). ✓
- `workspace_path` calls `segment_of`; docstring corrected. `feature-worktree.py:resolve_repo` takes its
  segment from `factory_config.segment_of`; `repo == "harness"` early return unchanged. ✓
- `FEATURES_ROOT` gone from `factory_claim.py` — no alias, no fallback, no new refusal path.
  `_BlockerCache` keys both `_plans` and `_issue_maps` on `(repo, feature)`. ✓
- Verify command ran verbatim, exit 0; per-suite tallies and T-01/T-02's named cases confirmed `ok`
  above. ✓
- Hardlink confirmed intact for all three edited bin files. ✓
- Only the three named production files changed (confirmed via `git status --porcelain`: the other
  modified/untracked paths — `plan.yaml`, `feature.json`, `STATE.md`, the two test files, and prior
  T-01/T-02 receipts/observations — are sibling artifacts, not touched by this task). ✓
