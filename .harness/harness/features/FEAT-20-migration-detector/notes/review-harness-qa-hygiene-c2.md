# QA confirmation pass — PR #385 at 6296149 (c2)

## BLUF
**PASS.** All three must-fixes are independently confirmed landed at 6296149, and the suite is now
demonstrated (not merely asserted) to bind the #382 consolidation via a live mutation-kill. `main()`
runs the identical 26-case set at 3c75aa6 and 6296149 — nothing lost in the 1134-line deletion. A-2
(unpinned regression guard for #379) remains open exactly as the validator left it: a legitimate,
disclosed residual, not a new defect. `matrix_ok: true`.

## 1. M-2 — CONFIRMED, sweep independently re-run
AST-parsed `test-check-state.py` at 6296149: **0 top-level names (`def`/`class`) defined more than
once** — top-level assignments were not in scope of this check, only function/class defs, which is
what the shadow defect was. Independently swept every `*.py` in `.claude/skills/harness/bin/`
(**51 files**, `len(glob.glob(...))` printed, not eyeballed) with a standalone AST script never
touching the fix commit's own tooling: **0 files with a duplicate top-level def/class.** `def case_x`
appears exactly once (:1585), `case_l` once (:456), `case_m` once (:528).
`grep -c run_cs` → 0. `case_x` body (:1585-1707) imports `layout_fixtures as lf` and
`layout_migration as lm`, uses `lm.MARKER`, `lf.FLEET_TEXT`, `lf.STUB` — the live copy is the
`layout_fixtures`-based one, not case_l's chimera. File is 1751 lines (was 2899).

## 2. Green is now evidence — demonstrated by mutation
Mutated `layout_fixtures.STUB[".harness/team-config.yaml"]["legacy"]` in a scratch copy of the
6296149 tree (git-archive export, never the source checkout). Reran `test-check-state.py`:
**exit 1**, subcase `(x.3) an applicable clean tree -> NO INV-27 line` → **FAIL** (the mutated stub
now disagrees with `check-state.sh`'s own `team-config.yaml` stub, so the "clean" fixture stops
being clean). x.1/x.2/x.4/x.5 still pass, confirming the failure is localized to the consolidation
edge, not noise. Restored the mutation and confirmed `diff` against the untouched source file at
`/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/layout_fixtures.py` is
byte-identical, and reran to exit 0. **Mutation applied and suite ran** — both asserted, not one.
The shadow-era objection ("passes equally with two copies") no longer holds: there is one copy, and
perturbing it moves the suite.

## 3. M-1 — divergence non-reproducible, probed at both call sites
Re-derived `check-state.sh`'s wording logic (:1295-1319) into a standalone Python function and ran
it against constructed `SurfaceReport`s alongside `layout_migration.render()`'s logic (:293-320),
both calling the literal same `layout_migration.blame()`:

| cause | render() named | check-state named | sets equal |
|---|---|---|---|
| undeclared-segment (reader tagged `migrated` vs single evidence `legacy`) | `[('readerA.py','migrated')]` | same | **True** |
| no-evidence (`both`-tagged reader, reachable per `scan()` branch order :245 before :248) | `[('readerBoth.py','both')]` | same | **True** |
| no-rows (readers=[] by construction, `scan()`:233) | `[]` | `[]`, text has no trailing separator | **True** |

Judged on the (path, form) pair sets, not the punctuation (render() joins with `"; p [f]"` per
reader, check-state.sh joins with `", "` after an em dash — confirmed both formats above, ignored
for the equality judgment as instructed). At source: `check-state.sh:1318` computes `_named` via
`_lmod.blame(_srep)` inside `_cv_wording`, called for **every** entry in the closed 5-cause table
(:1302-1312) — there is no per-cause skip left. This is the same function object called on the same
report at both sites, so the earlier divergence is not merely unreproduced here, it is structurally
foreclosed by the M-1 fix (one shared function, no second filter).

## 4. Suites and gates — every exit code separately
- `run-unit-tests.sh --kind all`: **exit 0**. 27/27 registered `test-*.py` files `PASS`, includes
  `test-check-state.py` and `test-layout-migration.py`; `test-factory-integration.py` 106/106; no
  `FAIL`/`MISCONFIGURED` line; drift detector (unregistered file check) green.
- `test-check-domain.py`: **exit 0**, 14/14.
- `test-check-plan-routes.py`: **exit 0**, `ALL PASS`.
- `test-validate-digest.py`: **exit 0**, 2/2 + `ALL PASSED`.
- Live `check-state.sh` against the real repo (`CLAUDE_PROJECT_DIR` set, HEAD=6296149): **exit 0**,
  zero `INV-27` lines — marker present, no reader migrated, both surfaces CLEAN by design, matching
  the two prior panels.
- No dedicated `test-dispatch-guard.py` exists in the tree (pre-existing condition, not introduced
  by this diff — noted, not a finding against #385).

## 5. Regression — case set diff, 3c75aa6 vs 6296149
`main()` bodies are **byte-identical** between `3c75aa6:1729-1771` and `6296149:1709-1751`: same 26
calls (`case_a` through `case_x`, including `case_m2`/`case_m3`), same all-ok conjunction, same exit
logic. No case dropped by the 1134-line deletion.

## 6. A-2 — still open, correctly so
`grep -n "blame\|379" test-check-state.py test-layout-migration.py` at 6296149: **zero hits**,
unchanged from the FAIL round. Nothing pins the unified blame policy (#379/M-1) against future
regression by name; the only coverage is incidental (case_x's x.1/x.2 exercise MIXED/CANNOT_VERIFY
trees but were not written to discriminate the fix). This is a legitimate residual the operator may
have chosen not to close — not re-filed as blocking.

## 7. M-3 — DEC-194 restore and index regen, both falsified
`docs/harness/DECISIONS.md:5840-5859` (the DEC-194 body) is **byte-identical** between 3c75aa6 and
6296149 (direct `diff`) — the in-place "narrowed under issue #366" clause from `a714bd0` is gone,
restored verbatim. `### DEC-194 amendment 2` is appended at the file's tail (:5920+), using the same
`### DEC-NNN amendment N (date)` mechanism as amendment 1. **"Index regenerated" falsified as true,
not merely diffed for content:** ran `gen-decisions-index.py --stdout` (its own documented read-only
mode) against the scratch tree and diffed its output against the *committed*
`docs/harness/DECISIONS-INDEX.md` at 6296149 — **byte-identical**, exit 0. The generator reproduces
the committed file exactly; the mechanism was actually re-run, not just hand-edited to match it.
`plan.yaml:660-669` rewords the same clause consistently, citing `DEC-194 am.2`.

## TEST-MATRIX
`matrix_ok: true`. `logic` change (T-01/T-02, `main-session-direct`, DEC-174 carve-out); unit
presence is the floor. Both touched test files (`test-check-state.py`, `test-layout-migration.py`)
are themselves in the diff (P-05 — not pre-existing coverage happening to sit nearby), both green,
and §2 above demonstrates the suite actually discriminates the change rather than passing vacuously.

## SC evidence
No BRIEF.md/plan.yaml SC ids scoped to PR #385 specifically (same as prior round — a post-ship
hygiene branch on parent FEAT-20's T-01/T-02, which predate it). Not inventing traceability.

## Findings summary
- No blocking or high findings. M-1/M-2/M-3 confirmed closed at 6296149.
- Advisory (carried, not new): A-2 (blame/#379 regression pin) remains unaddressed — legitimate per
  operator's prior calibration on the correct-today-not-pinned class.

## Files touched
This artifact only:
`.harness/features/FEAT-20-migration-detector/notes/review-harness-qa-hygiene-c2.md`. Nothing in
source (read-only per dispatch). Scratch: git-archive export of 6296149 under
`/private/tmp/claude-501/.../scratchpad/tree6296149/`, mutation probe script `probe_m1.py` — both
disposable, not committed.
