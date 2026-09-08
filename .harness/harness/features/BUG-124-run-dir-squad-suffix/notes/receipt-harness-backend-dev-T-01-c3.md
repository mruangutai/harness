# Receipt — harness-backend-dev — BUG-124 T-01 (cycle 3, send-back 2)

## BLUF

Fixed. Moved `import harness_yaml` from module top level (`harness_boundary.py:22`, old numbering)
into the existing `try:` block inside `run_dir_grant_globs` (now `harness_boundary.py:847`,
immediately above `harness_yaml.load_file(manifest_path)`), so the pre-existing
`except Exception: return []` absorbs a `ModuleNotFoundError` for `harness_yaml` exactly the way it
already absorbs a missing PyYAML. No new seam, no shim, no module-level sentinel. Adjusted one
clause of the function's docstring (`harness_boundary.py:824-827`) to name a missing `harness_yaml`
module alongside a missing PyYAML in the never-raises sentence; DEC-171 parenthetical left intact.

All 11 acceptance items observed green or matching the expected RED proof. Single production file
touched, exactly as scoped.

## Observed counts

| # | Check | Result |
|---|---|---|
| 1 | T-01 plan `verify:` (cross-checked against `plan.yaml:244` — matches verbatim) | exit 0, `ALL PASS` (60 unit cases) plus inline python assertions all held |
| 2 | `test-run-unit-tests-kinds.py` | exit 0, 5/5 PASS (was exit 1, 2 failures) |
| 3 | `test-run-unit-tests-layout.py` | exit 0, 14/14 PASS (was exit 1, 13 failures) |
| 4 | `test-check-plan-routes.py` | exit 0, all cases PASS/ok (was exit 1, 2 failures) |
| 5 | `test-harness-boundary.py` | exit 0, 60/60 `PASS` lines, footer `ALL PASS` (re-earned, module under edit) |
| 6 | `test-no-distribution.py` | exit 0, all cases PASS |
| 7 | `test-dispatch-guard.py` (worktree's own `dispatch-guard.sh`, import moved) | `69 of 69 cases passed` |
| 8 | `test-dispatch-guard.py` with `DISPATCH_GUARD_BIN` pinned to main checkout's pre-change `dispatch-guard.sh` (md5 `ca904b2906ad8d44662db428cb2dbc89`, verified before run) | `61 of 69 cases passed`, 8 FAIL lines: `case 18a: an inverted run-dir slug is refused`, `case 18a/b: stderr names the slug and the run-dir slug wording`, `case 18b: stderr names a compliant form ending in -eng`, `case 18g: the refusal strands no claim for the dispatched persona`, `case 21: stderr says the manifest declares no run-dir write grant`, `case 22: oddsquad-t01 is refused`, `case 22: the refusal names oddsquad in its compliant form`, `case 23: stderr says the run-dir vocabulary derivation failed` — matches the expected red set (18a x2, 18b, 18g, 21-message, 22 x2, 23-message) exactly |
| 9 | `test-check-domain.py` (re-measured, send-back 3) | exit 0, 0 `FAIL` lines in the full run. The sweep/clean-tracked self-test at `:2321-2332` printed `red proof: original reported 0 FEAT-OLD line(s), mutant 2` immediately followed by `ok    sweep/clean-tracked RED: removing the skip makes case A red` (base=0, mutant=2, mut>base, PASS). `sweep()` with no argument runs the real in-place hook, so `base` was always computed from `HERE` where `harness_yaml.py` is present and was never affected by the import fix; only the mutant copy — sitting in a bare tmpdir per `:2306-2316` — depended on it. Under the old top-level import that copy's import of `harness_boundary` would fail (only `harness_boundary.py` and `run_identity.py` are copied beside it, not `harness_yaml.py`), forcing "enforcement OFF" and a spurious mutant count of 0, giving `mut(0) <= base(0)` — the exact FAIL qa recorded. With the import lazy, that copy's module-level import now succeeds, the mutation's real effect (SWEEP_SKIP_CLEAN_TRACKED flipped) executes, and the mutant correctly reports 2. Observed: base stayed 0 (as it always was), mutant rose from the old spurious 0 to 2 — this cycle's lazy-import change DID clear the RED failure qa recorded, by fixing the mutant's import rather than by changing base.
| 10 | `git diff --numstat` | `3\t2\t.claude/skills/harness/bin/harness_boundary.py` and `7\t1\t.harness/harness/features/BUG-124-run-dir-squad-suffix/feature.json` (orchestrator's own edit, not mine) — no other production files touched |
| 11 | `grep -n "import harness_yaml"` in `harness_boundary.py` | exactly one hit, line 847, inside `run_dir_grant_globs`'s `try:` block — not at module level |

## Correction (send-back 3)

Item 9's first evidence line quoted `red proof: original denials 1, mutant 0 (exit 2 vs 0)` —
that line is printed at `test-check-domain.py:2443-2444` by the SC-07 write-path self-test, not
by the sweep/clean-tracked self-test at `:2324-2325` this row is actually about. The two lines
sit two rows apart in the same run's stdout and were misattributed to each other. Corrected above
with the sweep/clean-tracked self-test's own printed line, re-measured directly from a fresh run.

## Files touched

- `.claude/skills/harness/bin/harness_boundary.py` (production fix)
- this receipt

## send_back_count

2 (cycle 1 built T-01; cycle 3 is the second fix cycle for T-01).
