# Receipt — harness-backend-dev — BUG-2161 T-01 fix round c1

Base (review_sha): 1ef80c260aed1e288981a9cbea842b7c394c0419
Fix commit: see "Commit SHA" at the foot (recorded after the commit, in a follow-up receipt-only commit).

## Red first (pre-fix runs, same tests, unmodified production code)

F1 — red tests: unit `F1 station write refused: runs/ pruned = False, and the gap is reported`;
integration `station write refused (plan.yaml absent): runs/ is preserved, nothing is pruned, no
plan.yaml appears, and the gap is reported`. Pre-fix output:
`FAIL F1 station write refused: runs/ pruned = False, and the gap is reported` (unit; 5 FAILED total)
and `FAIL  station write refused (plan.yaml absent) ...` with stdout
`gh-sync: FAILED — station not recorded, .../plan.yaml is absent` followed by runs/ removed (integration; 7 FAILED total).

GC-01 — red tests: unit `GC-01 source/task alias|source/parent alias, --yes|dry run, no --close-sources:
ZERO writes name #N ...` (4 FAIL pre-fix, e.g. `FAIL GC-01 source/task alias, --yes, no --close-sources`);
integration `source/task alias|source/parent alias, --yes: exits 0 and ZERO gh calls name #N` plus the
gap-report checks for --yes and dry run (6 FAIL pre-fix). Paired positive (`--close-sources --yes`:
commented once, closed once, reseated, labelled) passed pre- and post-fix.

## What changed (`.claude/skills/harness/bin/gh-sync.py`)

- `cmd_abandon`: prunes `runs/` only if the station already read abandoned or `_record_station` returned
  True; otherwise prints `gh-sync: FAILED — runs/ not pruned ...` and keeps runs/ (exit status unchanged, 0).
- GC-01: new `_hold_back_sources` / `_report_held_sources`. Without `--close-sources`, a plan.yaml source that
  is also a task issue or the parent is removed from the acting record (no comment, detach, close, label,
  board write) and reported as `gh-sync: GAP - #N ... re-run with --close-sources`, dry run included.
  `_abandon_plan`/`_source_plan` and all non-alias behaviour and order are untouched; with the flag the
  existing overlap handling stands. `_report_abandon_gaps` gained `held` so a held parent does not print
  "no parent recorded".
- Tests: unit `Seams(station_ok=)` + GC-01/F1 cases; integration GC-01/F1 cases. The pre-existing #1996
  prune test (`FEAT-06-abandon-adopted`) staged no plan.yaml, i.e. a refused station write, which F1 now
  correctly keeps; its fixture now calls `add_plan_station` (assertion unchanged).
- Untouched: F2 order, F3, T-02 docs, ship suite, gh-close-gate.py.

## Signed verify (worktree root, verbatim)

`python3 tests/unit/test-gh-sync-abandon-sources.py && python3 tests/integration/test-gh-sync-abandon.py && python3 tests/integration/test-gh-sync-ship.py`
Result: exit 0; all three suites `ALL PASSED` / no FAIL lines (286 PASS/ok lines).

## Commit SHA

Fix commit (code, tests, receipt): 0474ae66ac6a9dc378da7006365e49b04eb85a52
(a second receipt-only commit records this line; `git log` on this path shows it.)

## Review tip

Review tip (head_sha): b5929a92e87a7792ddaa7ea99e3f849a699a82ab

- Code fix commit (code, tests, receipt): 0474ae66ac6a9dc378da7006365e49b04eb85a52 — the only commit changing `gh-sync.py` and tests.
- Receipt-only commit: b5929a92e87a7792ddaa7ea99e3f849a699a82ab — records the fix SHA above; no code or test change.
- This annotation was added after that tip, left uncommitted to avoid a recursive SHA self-reference; no further commit was made and no checks were rerun in this form-only loopback. Signed-verify evidence above is from the code fix commit and is unchanged.
