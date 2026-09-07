# Receipt — harness-backend-dev — REUSE angle, plan surface — BUG-1290-factory-claim-repo-root

BLUF: one real finding. T-04's `verify:` clause hand-rolls, a third time, a check the tree
already performs twice for the same fact ("the real tree's `features` layout surface is
CLEAN"). Everything else on the plan surface — the T-01 fixture extension, the D-01 resolver,
T-03's deletion of `FEATURES_ROOT`, T-04's reader-row retarget — reuses existing helpers
(`build_features_root()`, `write_yaml`/`write_json`, the source-scan drift-guard style) rather
than re-implementing them. No edits made; BRIEF.md, plan.yaml, and every file under
`.agents/skills/harness/bin/` and `tests/` are byte-unchanged.

## R-01

- id: R-01
- severity: low
- targets: T-04
- file/line: `plan.yaml` T-04 `verify:` (the `python3 -c "...layout_migration...scan('.').surfaces['features']..."` clause)
- summary: T-04's verify inline-probes `layout_migration.scan('.').surfaces['features'].verdict
  == CLEAN` on the real tree, but this exact fact — the real tree's `features` surface is CLEAN
  with migrated evidence — is already asserted by `tests/integration/test-layout-migration.py`
  case 22 (`:421-429`, checked against `render()`'s `"features: CLEAN — evidence migrated"`
  line), which T-04's own verify already runs as its first conjunct
  (`python3 tests/integration/test-layout-migration.py`). The same fact is asserted a third way
  by CI itself (`.github/workflows/tests.yml:231-272`, greeping `render()`'s `"layout: N
  surface(s) clean"` line) and a fourth way by `check-state.sh` INV-27
  (`:2315-2367`, reading the module's structured `Result` directly, same as T-04's inline
  probe).
- concrete cost: four independent spellings of one fact (`scan().surfaces['features'].verdict`,
  case 22's parsed `render()` line, CI's greeped `render()` line, INV-27's structured read) that
  a future change to `layout_migration`'s verdict/evidence text must keep in lockstep; T-04's
  inline probe is the one of the four with no name and no comment, so it is the one nobody
  remembers to update, and it duplicates a check the task's own first verify conjunct already
  runs.
- alternative: drop the inline `python3 -c` probe from T-04's verify; the first conjunct
  (`python3 tests/integration/test-layout-migration.py`) already fails on this fact via case 22.
  If the plan wants failure attribution specific to the `features` surface, name case 22 in the
  verify comment instead of re-deriving the same check inline.
- gates_signature: false — this is a verify-clause simplification, not a correctness gap; T-04
  is still fully covered by case 22 either way.

## Checked, no finding

- D-01's shared resolver: confirmed `factory_config.py` and `harness_boundary.py` neither
  already implement a `repo name -> features root` join — `FLEET_PATH`/`resolve_root` build
  unrelated joins. Not a re-implementation.
- T-01 step 4's fixture-tree extension: the intent says "Extend `build_features_root()`" by
  name (`tests/unit/test-factory-claim.py:336-374`), reusing its existing `write_yaml`/
  `write_json` helpers rather than hand-building a parallel tree. Correct reuse, no finding.
- The out-of-scope segment derivations named in the BRIEF (`post-merge-sweep.sh:163`,
  `quarantine.py:109`, `worktree_terminal.py:107-129`, `feature_schema.py:231`) each already
  implement their own segment logic independently of `feature-worktree.py:resolve_repo` and of
  each other — a real duplication in the tree, but explicitly SETTLED as out of scope for this
  bug; not re-litigated here.
- T-03's `FEATURES_ROOT in text` grep (verify) vs. T-01's SC-05 `hasattr` case: different
  properties (source text vs. runtime attribute), not a duplicate — an alias would fail the
  grep but pass the hasattr check on its declared name, so both check something the other
  cannot.

files_touched: none — receipt only.
