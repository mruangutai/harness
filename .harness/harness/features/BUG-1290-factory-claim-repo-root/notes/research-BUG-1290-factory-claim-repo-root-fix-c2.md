# Fix cycle 2 — closing the goal-check's verify-integrity gaps (BUG-1290)

**All five findings applied; every verify I wrote or rewrote was RUN at `eb9d044e` and is red there
while the plan's pre-existing commands are green.** The plan gained one task (`T-05`, the mutation
proof) and no criterion was weakened. `check-plan-routes.py` exits 0, 0 violations;
`approval.status` is `pending`; no `panel:` key; all five `verify:` blocks are literal `|`.

## Dispositions

| id | Disposition | What changed |
|---|---|---|
| F-02 | applied | New `T-05` (`tests/unit/test-factory-claim-mutation.py`, depends_on `T-03`) performs the revert-mutation and captures the evidence; `SC-08` rewritten to name it |
| F-03 | applied | `T-01` `verify:` now requires a per-case `FAIL` marker for all six new cases; `T-01` intent pins the `BUG-1290 5x:` naming and per-case exception-to-`check()` reporting |
| F-05 | applied | `T-04` `verify:` pairs the suite with a reader-row probe; `SC-09` and `T-04` step 3 say why the suite alone is insufficient. No test file edited |
| F-06 | applied | `SC-06`, `D-03` and `T-01` step 5f re-expressed around the owner-strip BEHAVIOUR; `D-03` `because` states the measurement and the residue |
| F-01 | applied | `D-01` `choice` now names the deviation against `#1290`'s Scope bullet as well as the grilling wording. Shape untouched |

## Measurements, all at `eb9d044e` on the worktree

- **Baseline.** `tests/unit/test-factory-claim.py` → exit 0, 120 `ok` lines, **0** `FAIL` lines.
  `tests/integration/test-layout-migration.py` → exit 0, case 22 `ok`.
- **F-03.** The rewritten `T-01` command over that output prints `MISSING RED: 5a`…`5f` and the
  final `test $rc -eq 0` exits 1. The old `test $? -ne 0` form would have been satisfied by any
  single red case; this one cannot be.
- **F-06.** Pattern
  `\brepo\w*\s*\.\s*(?:r?split|r?partition)\s*\(\s*["']/["']|\bbasename\s*\(\s*repo\w*`
  over the three scanned files: `factory_claim.py` **0**, `feature-worktree.py` **1** (`:86`),
  `factory_config.py` **1** (`:386`). No false positive on `factory_claim.py:84`
  (`url.rstrip("/").split("/")`), `feature-worktree.py:203` or `:278`. So it is red today for the
  derivation `D-01` cites, and `rsplit`/`partition`/`rpartition`/`basename` re-derivations are
  caught. Residue (renamed subject, index slice, fourth module) is written into `D-03 because`.
- **F-05.** The probe → `READER ROW PROBE: FAIL`, exit 1, readers
  `{… factory_claim.py: migrated …}` with `factory_config.py` absent — while the suite is green.
  The three pattern-ladder clauses hold on the existing row (`legacy` matches the legacy control,
  not the migrated one; `migrated` matches the migrated control), so the red is exactly the
  membership/classification clause, not a broken control.
- **F-02.** `python3 tests/unit/test-factory-claim-mutation.py` → exit 2, "can't open file", **no
  marker line** — which is why `T-05`'s verify greps for `BASELINE 3/3 ok` **and**
  `MUTATION PROOF: 3/3 cases reddened` rather than trusting a status (a missing file mimics
  discrimination). The mutation MECHANISM was measured directly instead: with a proxy installed on
  `factory_claim.factory_config` that discards `features_root`'s argument, and the suite's own
  monkeypatch applied **afterwards**, a `mruangutai/kaya-ai` candidate resolves to
  `…/.harness/harness/features` and `MUTANT ACTIVE` prints. Attribute delegation is at call time,
  so the mutant survives the suite's patch — that is what makes `SC-08` reachable.

## Consequences worth knowing

- `T-01` step 3 now REQUIRES the suite's `factory_config.features_root` patch to be a *function of*
  `repo_name` (not a dict or a constant). `T-05`'s mutant works by freezing that argument; a
  constant patch would make mutant and correct code indistinguishable.
- **Write route deviation, deliberate.** The dispatch named `plan-merge.py apply` as the only
  route. `apply` is ADD-ONLY and exits 7 on a changed value (`plan-merge.py:738`, `:1218`), so the
  six field rewrites went through `plan-merge.py amend --expect-sha256 --value-file`, the verb
  BUG-1128 added for exactly this; `apply` added `T-05`. No `Edit`/`Write`/redirect touched
  `plan.yaml`.

## Open questions

- **Q1 (blocking, unchanged, not mine to close):** `D-01`'s shape deviation rides to the operator
  at signature. F-01 only added the ticket clause to its text.
- **Q2 (non-blocking):** `F-04` (a *weakened* replacement of the two deleted module-scope cases is
  forbidden in prose only) and `F-07`/`F-08` were not in this dispatch and are untouched.
