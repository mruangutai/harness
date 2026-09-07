# Receipt — harness-backend-dev — T-01 (c1)

Task: T-01 — write failing unit coverage for BUG-1290's per-repository claim resolution.
Only `tests/unit/test-factory-claim.py` was touched; no production file was edited.

## What changed

1. Docstring (`:7-8`, `:14-16`): reworded the FEATURES_ROOT sentence to describe the
   monkeypatched `factory_config.features_root` seam; deleted the paragraph describing the
   two module-scope pinned-default cases.
2. Deleted the two module-scope cases (old `:58-68`) plus their introducing comment (old
   `:54-57`) that pinned the unpatched `FEATURES_ROOT` default. Not weakened — removed outright.
3. Added `REPO_KAYA = "acme/kaya-ai"`, `REPO_HARNESS_SEG = "acme/harness"`,
   `SEG_FEATURE = "FEAT-99-seg"` fixture constants.
4. `build_features_root()` now lays out a harness root: `.harness/widget/features/{FEAT-01-demo,
   FEAT-02-block}` (REPO's own segment, carrying the pre-existing fixtures unchanged in content)
   plus two new segment roots, `.harness/kaya-ai/features/FEAT-99-seg` (task T-77 depends_on
   unresolvable T-88) and `.harness/harness/features/FEAT-99-seg` (task T-77, clear) — same
   feature id, different DAG, per step 4.
5. Added `fixture_features_root(repo_name)`, a FUNCTION of `repo_name`
   (`repo_name.split("/", 1)[-1]` joined under the fixture harness root) — never a constant or
   dict lookup, per the D-01/T-05 mandate.
6. `run_main()` now takes `features_root_fn=None`, defaulting to `fixture_features_root`, and
   monkeypatches `factory_config.features_root` (module attribute `fc.features_root`) instead of
   `claim.FEATURES_ROOT`; restore is conditional on whether the attribute pre-existed (so a
   pre-T-03 tree correctly leaves `factory_config` with no `features_root` attribute after
   every call, and a post-T-03 tree restores the real production function).
7. B5-ter's absent-root case now passes `features_root_fn=lambda repo_name: absent_root` instead
   of swapping the module-level `FEATURES_ROOT` global.
8. Added six new cases, `BUG-1290 5a` through `5f`, each wrapped in try/except reporting through
   `check()`, verbatim per the dispatch's SC-01..SC-06 mapping.

## Why ~19 pre-existing cases now also FAIL (expected, not a regression)

`factory_claim.py` is untouched in this task — it still reads its own hardcoded module-level
`FEATURES_ROOT` constant (the real checkout's `.harness/harness/features`), never
`factory_config.features_root`. Removing the `claim.FEATURES_ROOT` swap (step 3, mandatory) means
every existing case that depends on this file's own FEAT-01-demo/FEAT-02-block fixtures being
readable (M3/M6/M7, B1, B3, B4, B5, B5-bis, B5-ter, X) now sees the real repository's actual
`.harness/harness/features` (which has no such directories) and gets `no_plan`. This is the
intended shape of a pure test-first task per the dispatch's step 3: T-03 makes `factory_claim.py`
consult `factory_config.features_root` per candidate, which restores every one of these to green
using the very same `fixture_features_root` patch already installed here. The task's own verify
command checks only for the six new markers, not overall suite health.

## Verify — run verbatim, per plan.yaml T-01 (cross-checked, matches dispatch exactly)

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root && out=$(python3 tests/unit/test-factory-claim.py 2>&1); rc=0; for m in 5a 5b 5c 5d 5e 5f; do printf '%s\n' "$out" | grep -q "^FAIL  BUG-1290 $m" || { echo "MISSING RED: $m"; rc=1; }; done; test $rc -eq 0
```

Exit code: `0` (PASS — every marker present).

Actual FAIL lines matching the six markers (verbatim from the run):

```
FAIL  BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
        (1, '', 'factory: claim: skip #950 — issue #950 carries a feature: label that resolves, but no plan could be read at /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root/.harness/harness/features/FEAT-99-seg/plan.yaml - the feature directory or its plan.yaml is missing or unparseable\nfactory: claim: no claimable work\n')
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
        (1, '', 'factory: claim: skip #951 — issue #951 carries a feature: label that resolves, but no plan could be read at .../FEAT-99-seg/plan.yaml - ...\nfactory: claim: skip #952 — issue #952 carries a feature: label that resolves, but no plan could be read at .../FEAT-99-seg/plan.yaml - ...\nfactory: claim: no claimable work\n')
FAIL  BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
        (1, 'factory: claim: skip #953 — issue #953 carries a feature: label that resolves, but no plan could be read at .../FEAT-01-demo/plan.yaml - ...\nfactory: claim: no claimable work\n', '/var/folders/.../claim-harness-.../.harness/zzz-missing-segment/features/FEAT-01-demo/plan.yaml')
FAIL  BUG-1290 5d: owner-qualified name ending in harness resolves to .harness/harness/features
        AttributeError("module 'factory_config' has no attribute 'features_root'")
FAIL  BUG-1290 5e: factory_claim exposes no FEATURES_ROOT attribute
        '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root/.harness/harness/features'
FAIL  BUG-1290 5f: the owner-strip derivation lives in exactly one place, factory_config.py
        {'factory_claim.py': 0, 'feature-worktree.py': 1, 'factory_config.py': 1}
```

`5f`'s counts match the plan's own measurement at eb9d044e exactly (`feature-worktree.py`: 1,
`factory_config.py`: 1, `factory_claim.py`: 0).

## Note on the workflow (not a defect — see G-18 in my own Expertise)

My first attempt at this edit used a relative path (`tests/unit/test-factory-claim.py`) and landed
on the main checkout's copy of the file instead of the worktree's. Caught it via
`git status --porcelain` in both trees before verifying, reverted the main checkout with
`git checkout -- tests/unit/test-factory-claim.py` (that tree had no other pending changes to this
file), and redid the whole edit against the absolute worktree path shown above. Confirmed clean
afterward in both trees.
