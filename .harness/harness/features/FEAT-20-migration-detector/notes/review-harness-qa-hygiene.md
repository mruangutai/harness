# QA gate — PR #385 (detector hygiene) at a714bd0

## BLUF
FAIL. The suite is green (all 27 registered test files pass, `run-unit-tests.sh --kind all`
exit 0; `check-state.sh` exit 0, no INV-27 line — the real repo tree is unmigrated so both
surfaces are CLEAN) but the green is a false signal: `test-check-state.py` contains **17
duplicated top-level `def`s** spanning a whole shadowed block, lines 528–1661, re-pasted
verbatim at 1662–2899. 16 of the 17 pairs are byte-identical (confirmed by SHA-256 over each
extracted range). The 17th, `case_x` — the one function this PR's `#382` commit message claims
to have consolidated onto `layout_fixtures.py` — is NOT identical, and Python's late binding
means the **executing** copy (`case_x` at :2719) is the OLD, pre-#382, hand-duplicated-STUBS
version, never the `layout_fixtures`-based one at :1585. The #382 fix did not take effect in
this file. Independently corroborated: `.harness/features/FEAT-20-migration-detector/observations/harness-validator-lead.md`
(run `2026-08-14-5-validator`, same SHA) reached the identical diagnosis with the same line
coordinates while I was mid-investigation — two independent reads landed on the same
17-name/528–1661 finding, which raises confidence this is real, not a misreading.

Worse than dead code: the shadowed `case_x` at :1585 is not simply an orphaned old copy — it is
a **chimera**. Its docstring is the INV-27 layout-invariant docstring, it imports
`layout_fixtures`/`layout_migration` and binds `MARKER_REL`/`FLEET_TEXT`/`STUBS` from them, but
its actual test body (`(l1)`–`(l8)`) is a duplicate of `case_l`'s INV-22 run-budget assertions
(`case_l` lives intact and correct at :456–525). `STUBS`, `FLEET_TEXT`, `MARKER_REL` are bound
and never read in that block. So there is no salvageable "refactored INV-27 case" sitting in the
dead copy to promote — deleting the executing copy (:2719) to "keep the #382 refactor" would
delete INV-27 test coverage outright, not fix it.

## 1. Suites + live gate
- `run-unit-tests.sh --kind all`: exit 0. All 15 unit + 12 integration scripts print
  `PASS <file>`, 106/106 checks in `test-factory-integration.py`'s own tally, no `FAIL` or
  `MISCONFIGURED` line anywhere in the log. `test-check-state.py` and `test-layout-migration.py`
  both `PASS` — the drift detector (registration check) at the top of `run-unit-tests.sh` also
  passed, so no stray `test-*.py` is unregistered.
- `test-check-plan-routes.py` is part of the `all` run above (case_01–case_25j2 all `ok`/`PASS`).
- Live gate entry point: `git ls-files '*check-state.sh'` and `find . -name check-state.sh` both
  return exactly one file, `.claude/skills/harness/bin/check-state.sh` — there is no separate
  `bin/check-state.sh` wrapper; CLAUDE.md's Conventions reference to `bin/check-state.sh` is
  shorthand for this same path, not a second entry point. Invoked via `CLAUDE_PROJECT_DIR`. Run
  against the real repo: **exit 0**, zero `INV-27` lines. The real tree carries the fleet marker
  (`.harness/factory/fleet.yaml` exists) so D-04 applicability is true, but no coupled reader has
  migrated yet, so both surfaces are CLEAN and INV-27 is silent by design (SC-12).

## 2. The #382 defect, re-measured
- (a) Executing `case_x`: line **2719** (Python binds the last of two top-level defs; only one
  call site, `.../test-check-state.py:2883` `ok_x = case_x()`).
- (b) Does it reference `layout_fixtures`? **No.** It hardcodes the same legacy-only `STUBS`
  dict inline (byte-identical to the pre-#382 `3c75aa6` `case_x`, modulo the `run_cs`→`run`
  rename — see (d)).
- (c) 17 top-level names doubled: `case_m, case_m2, case_m3, case_n, case_p, case_q, case_t,
  case_r, _factory_tree, case_s, case_o, case_u, _inv26_fixture, _run_with_gh, case_v, case_w,
  case_x`. SHA-256 over each extracted def range: **16/17 pairs identical**; only `case_x`
  differs (`a0cf383871` vs `3b3bb3fd89`).
  - Shadow region: **[528, 1661]** (dead, never executes).
  - Live region: **[1662, 2899]** (executes).
- (d) Executing `case_x` calls the module-level `run()` (defined once, :50). `run_cs` does not
  survive anywhere in the file (`grep -c run_cs` → 0) — it was renamed to `run` globally, and
  that rename is the ONLY change between the dead `case_x` (:1585, minus the chimera swap) and
  the pre-#382 original at `3c75aa6:1585`.

## 3. Fixture equality (layout_fixtures.py vs pre-#382 inline copies)
No weakening found. `layout_fixtures.py`'s `STUB` dict (both `legacy` and `migrated` forms, all
7 keys), `FEATURES_READERS`, `DOCS_READERS`, and `FLEET_TEXT` are byte-identical to the inline
copies at `3c75aa6` in both `test-check-state.py`'s old `case_x` STUBS-as-legacy-only projection
and `test-layout-migration.py`'s STUB/READERS/FLEET_TEXT (diffed directly, no key or byte
drift). `layout_migration.MARKER` (`os.path.join(".harness", "factory", "fleet.yaml")`) is
unchanged at `a714bd0` vs `3c75aa6`. Consolidation, where it landed (everywhere except the dead
`case_x`), is faithful.

## 4. #379 falsification probe — result: CONFIRMED, and stronger than empirical
At `a714bd0`, `check-state.sh`'s INV-27 block calls `_lmod.blame(_srep)` directly
(`check-state.sh:1301,1304,1325`) — the identical function `render()` calls
(`layout_migration.py:319`). Structurally the two call sites cannot diverge; there is one
function, not two policies kept in sync by discipline.

Empirical probe: could not build the exact tree requested (MIXED surface + a `neither`-tagged
reader) — `scan()`'s branch order makes that combination unreachable: any reader tagged
`unreadable` or `neither` forces `CANNOT_VERIFY`, checked *before* the MIXED branch, so a MIXED
verdict never coexists with such a reader. I built the nearest real-divergence case instead:
`features` surface, evidence both shapes present, one reader `[both]` (`team-config.yaml`), one
reader `[unreadable]` (`check-domain.sh` absent), cause `unreadable`.
- **3c75aa6** (reproduced from source, `old_layout_migration.py` in scratch): `render()` names
  both readers — `team-config.yaml [both]; check-domain.sh [unreadable]`. Reproducing
  `check-state.sh`'s old `_cv_wording`/`_tagged('unreadable')` clause names **only**
  `check-domain.sh [unreadable]` — the `[both]` reader is silently dropped from the
  session-entry wording that old code actually rendered. **Diverges**, as issue #379 claimed.
- **a714bd0**: both call sites (`blame()` directly) return
  `team-config.yaml [both]; check-domain.sh [unreadable]` — **identical**.
Fixture files and reproduction script kept under scratch only (not committed); pointers on
request.

## 5. CANNOT_VERIFY wording — live confirmation + coverage gap
Confirmed live (same probe as §4): the new wording still names the responsible reader(s)
correctly, including a `[both]`-tagged reader on a `CANNOT_VERIFY` surface, which the narrower
old per-form filter would have dropped.
**Coverage gap:** `grep -n "blame\|379" test-layout-migration.py test-check-state.py` → zero
hits. The one existing case that exercises this branch, `case_x` `(x.2)` at
`test-check-state.py:2802` (`ok = code == 1 and any("CANNOT VERIFY" in l and "[neither]" in l
for l in ls)`), uses a tree with exactly **one** blame-worthy reader. Old and new logic agree
trivially on a single-reader tree (both name the one `neither` reader), so `(x.2)` passes under
both the pre- and post-`#379` policy — it does not, and never did, discriminate the fix. No test
in the diff pins the unified blame policy against the specific failure mode #379 fixed
(a second, differently-tagged reader silently dropped from one call site). This is
correct-today, not pinned-against-regression.

## TEST-MATRIX
`matrix_ok: false`. This is a `logic` change (T-01/plan.yaml, `execution_mode:
main-session-direct`, DEC-174 carve-out) touching the test files themselves, so unit presence
is the floor — and unit presence is nominally there (test files exist, registered, green) but
**the diff's own advertised behavior change (#382's case_x consolidation) never executed**, and
nothing in the suite would have caught a shadowed duplicate definition (Python raises no error
on redefinition; `run-unit-tests.sh`'s drift detector only checks *files*, not in-file
duplicate `def`s). That is a hole in the floor itself, not just a gap above it.

## SC evidence
No `BRIEF.md`/`plan.yaml` SC ids were supplied for this hygiene PR in my dispatch scope (only a
plan.yaml for the parent FEAT-20 feature, whose T-01/T-02 predate #385). I did not attempt to
map SCs to this specific PR; flagging as an open question rather than inventing traceability.

## Findings summary (severity)
1. **BLOCKING** — `test-check-state.py` :528–2899 must be de-duplicated. Delete shadow region
   `[528, 1661]`; the surviving `case_x` at (currently) `:2719` still needs #382 applied by hand
   (switch it to `layout_fixtures`/`lm.MARKER`) since it is the one that actually runs INV-27
   coverage.
2. **Finding** — no test discriminates the #379 blame-unification fix from its pre-fix
   narrower-filter behavior; add a case with two differently-tagged blame-worthy readers on one
   `CANNOT_VERIFY` surface (my scratch probe is a ready template).
3. **Advisory** — `docs/harness/DECISIONS.md` diff documents the #366 narrowing but records
   nothing about #379/#382/#383; not required, noted for completeness.

## Files touched
None in the source repo (read-only, as instructed). Scratch reproduction artifacts under
`/private/tmp/claude-501/.../scratchpad/probe379/` (not committed, disposable).
