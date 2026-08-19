# REUSE angle — FEAT-25 plan.yaml — receipt

Reader: harness-backend-dev, flag-only, no edits applied.

## Findings

No REUSE findings against the must_fix/advisory bar. Checked and cleared:

- **T-01's `FEATURES_ROOT` literal join** does not duplicate an existing helper.
  `factory_config.workspace_path` (factory_config.py:222) is the only candidate and D-01
  already rules it out correctly (needs a loaded fleet + repo name per candidate, joins onto
  `workspace_root` not `harness_root`). Grepped every `.py` in this dir for an existing
  three-segment `.harness/harness/features` constant in production code — none exists; every
  other hit is a test-fixture literal (`test-check-domain.py`, `test-check-plan-routes.py`,
  `test-factory-cli.py`, `test-check-state.py`), not a reusable function.
- **T-01's two new module-scope cases** correctly reuse `test-factory-claim.py`'s existing
  `check()` helper (line 34) rather than inventing a new assertion printer — the plan says so
  explicitly ("Use the file's existing check() helper").
- **T-02's `plan_path()` / `plan_loaded()` / `root_exists()`** on `_BlockerCache` are genuinely
  new surface — no existing `os.path.isdir` check or path-builder is present in
  `factory_claim.py` or `factory_config.py` to reuse instead. `plan_loaded()` is required to
  route through `task()`'s existing cache-population path rather than re-implementing the
  YAML load, which the plan states explicitly (T-02 intent, item 1) — this is correct reuse,
  not a duplication to flag.
- **T-03's `layout_fixtures.STUB` entry and `FEATURES_READERS`** — the plan correctly notes
  `FEATURES_READERS` "needs no edit" because it already derives from `READER_TABLE`
  (`layout_fixtures.py:63`, `FEATURES_READERS = [r.path for r in _lm.READER_TABLE if r.surface
  == "features"]`). No hand-rolled duplicate list is introduced.
- **T-03's test-layout-migration.py case 22** is instructed to mirror the existing case 21
  (real root's docs surface, `test-layout-migration.py:392-399`) rather than inventing new
  scan/select/assert scaffolding — confirmed the precedent exists and is structurally
  parallel (surface report lookup → verdict/evidence assertion).
- **The trailing "balance:" comment convention** T-03 asks for on the new READER_TABLE row is
  not a new pattern — it copies the existing `check-plan-routes.py` row immediately above it
  (`layout_migration.py:87-90`), which the plan cites as precedent. Correct reuse, not
  duplication-to-flag.

## Advisory on the record — CONFIRMED

The carried advisory (`factory_claim.py:25-27`, `test-factory-claim.py:5`,
`test-factory-integration.py:31` — three prose corrections with no gating `verify:` clause) is
confirmed, not new. Read T-01's verify block directly: its only grep against `factory_claim.py`
targets the comma-form code line (`os.path.join(factory_config.harness_root(), ".harness",
"harness", "features")`); nothing greps the docstring's prose sentence at lines 25-27. Same for
`test-factory-integration.py:31`'s docstring paragraph — the file-level grep at the bottom of
T-01's verify (`grep -q '"\.harness", "features"' test-factory-integration.py`) only checks the
two fixture `feat_dir =` join lines (confirmed at `test-factory-integration.py:673,1039`), not
the docstring prose above it. `test-factory-claim.py:5`'s prose ("this repository's own
`.harness/features/`") is likewise ungated. All three are backtick/slash-form path mentions in
prose; the grep clauses that exist are comma-form code patterns and structurally cannot match
them. No REUSE angle beyond confirming this is already carried as intended.

## No must_fix / no advisory items from this angle

Empty return on new findings — the plan reuses existing helpers (`check()`, `FEATURES_READERS`,
the balance-comment convention, `task()`'s cache path) everywhere reuse was available, and adds
new surface (`FEATURES_ROOT`'s join, `_BlockerCache`'s three new methods) only where D-01/D-02
already establish no existing function fits.
