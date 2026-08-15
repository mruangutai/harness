# QA adequacy review — FEAT-12 — d543809 (inherited gate, not re-run)

**matrix_ok: true, inherited from `runs/qagate-validator/digest.md` — the matrix gate is NOT re-run
here.** This note answers the three named adequacy probes only.

## Probe 1 — detect/runner disagreement: CONFIRMED, live defect, rank medium

Verified directly (not just re-citing the qagate note):

- `.harness/harness.json` `test_kinds.integration.detect` is a literal two-file list —
  `.claude/skills/harness/bin/test-check-state.py|.claude/skills/harness/bin/test-factory-integration.py`
  — it does **not** glob-match `test-check-plan-routes.py` or `test-upgrade-config.py`.
- `unit.detect` is the glob `.claude/skills/harness/bin/test-*.py`, which **does** match both files.
- `run-unit-tests.sh:17,18`: `test-check-plan-routes.py` and `test-upgrade-config.py` are in
  `INTEGRATION_SCRIPTS`, **not** in `UNIT_SCRIPTS`. `--kind unit` never executes either file.

**Consequence, concretely:** a future gate that derives required kinds from a diff via `detect`
(rather than reading each SC's declared `evidence:`, as this run manually did) would classify a
change to either file as `unit`-kind, run `--kind unit`, and that command **structurally cannot**
execute the file that carries the evidence — it isn't in `UNIT_SCRIPTS` at all. This isn't "ran the
wrong command and got lucky," it's "the derived command's script list excludes the file by
construction." SC-02's and SC-10's own evidence would be silently unexecuted on the next change that
touches only those two files, while `detect`-based tooling reports success. This run avoided the
trap only because a human/qa read the SC table by hand; nothing in `harness.json` would catch a
future run that didn't. Ranked **medium**: it's a config-vs-runner disagreement in the object the
next several features will lean on to derive kinds, not a defect in this feature's own diff.

## Probe 2 — `test-check-plan-routes.py` token sweep at d543809: CONFIRMED clean, single surviving hit

`grep -n -E "harness-deploy|deploy\.sh|harness-registry|registry\.json"` over the file at `d543809`
returns exactly **one** hit: line 573, `os.path.join(td, "fake_root", ".harness", "registry.json")`
— the synthetic-registry fixture inside `case_21`, the legitimate exemption `ALLOW_LIST` names.

Checked the two locations the intent named as rewritten (old lines 558, 958-959) directly: both now
read as commentary about `$HOME/.harness/` holding the 2026-08-10 backup archives and about
`wayfind.py`'s upward-walk probe — no `deploy.sh`/`harness-deploy`/`harness-registry` token survives
at either site. **No stale/false reference survives; the synthetic fixture is the only occurrence.**
This is a distinct, independently-checked claim from item 4 (revertibility risk), not a re-litigation
of it.

## Probe 3 — adequacy of `test-no-distribution.py`'s 18 assertions

Counted at the file: case1×5, case2×2, case3×4, case4×7 = 18, matching the dispatch.

**One assertion is vacuous by construction, not merely currently unexercised:**
`case3_absence_no_registry_json_under_harness` (`tnd.py:161-167`) walks `os.path.join(ROOT,
".harness")` — **this repository's own** `.harness/` directory — for a stray `registry.json`. But
`deploy.sh`'s writer (confirmed at `f9488a2:.../deploy.sh:46-47,246-259`) only ever wrote
`$HOME/.harness/registry.json` (migrating from `$HOME/.gsd/harness-registry.json`) — **never** a
project-scoped `<repo>/.harness/registry.json`. Nothing in this repo's own `.harness/` tree has ever
held that file, in any commit, before or after this feature. The assertion has been trivially true
since before FEAT-12 existed and would stay true even if the registry mechanism had never been
deleted at all — it tests a location the feature never touched. **It could be deleted with the suite
staying green, and unlike the paired absence checks in case1/case2/case4, it never had anything to
detect.** This is distinct from SC-02b (the real, `$HOME`-scoped claim), which the BRIEF correctly
marks `verify: inspection` precisely because a test reading `$HOME` would be machine-dependent — the
BRIEF's own reasoning for excluding SC-02b from automation is the same reasoning that makes this
in-repo scan pointless; it was pointed at the wrong directory to begin with.

The other 17 checked by reasoning (no mutation performed — AUDIT mode, author nothing):

- **case1 (5):** both absence checks (`deploy.sh` tracked-anywhere, `harness-deploy.md` exists) are
  real state transitions — the files genuinely existed pre-feature and are genuinely gone now — not
  vacuous. The three presence checks (`six other command doors`, `check-plan-routes.py`,
  `factory_workspace.py`) are DEC-169 scan-reached pairings against the two absence checks: they
  guard against a mutant that over-deletes the `commands/`/`bin/` directories and would make the
  absence checks pass vacuously from an empty dir. Real dirs, never at risk of enumerating empty.
- **case2 (2):** already mutation-proven by qa (`ALLOW_LIST` removal → red; case2's own
  `reached_fleet_yaml` guard). Not redone.
- **case3 (3 of 4, excl. the one above):** `fleet_yaml_safe_loads`, `exactly_two_repos`,
  `kaya_default_branch_is_master` all assert real, previously-false-or-absent content
  (`fleet.yaml`'s repo list) that this feature's T-06 actually wrote. Not vacuous.
- **case4 (6 of 7, excl. the mutation-proven precedence check):** `no_dec12_heading`,
  `exactly_one_dec113_heading`, `no_dec12_references_under_docs`, `exactly_one_dec113_index_row`,
  `no_dec12_index_row` all scan real content that was true before the strike and false after (DEC-12
  genuinely had a heading, citations, and an index row before this feature). Not vacuous.
  `no_stale_marker_reintroduced` is the closest analog to the case3 finding above — the marker
  mechanism was actually removed by #202, *before* FEAT-12's own commits — so it protects against a
  regression this feature didn't itself cause. Unlike the registry check, though, it scans the
  correct file/location and would genuinely fire if the marker returned; it is a real (if
  feature-external) regression guard, not a wrong-location vacuity. Noted, not ranked as a defect.

## Findings, ranked

1. **[medium] `test_kinds.integration.detect` cannot ever match `test-check-plan-routes.py` or
   `test-upgrade-config.py`, and `unit.detect` does — so a `detect`-driven kind derivation would
   route SC-02's/SC-10's evidence to a command (`--kind unit`) that structurally never runs them.**
   Live config defect, not scoped to this diff — belongs to whoever owns `harness.json`'s
   `test_kinds` table. Not a `must_fix` for FEAT-12 (the plan didn't touch `test_kinds`, and this
   run's own qa gate did not fall into the trap), but it should not sit unrecorded — the next
   feature that touches either file and relies on automatic kind derivation will.
2. **[low] `case3_absence_no_registry_json_under_harness` (`test-no-distribution.py:161-167`) scans
   the wrong directory and has been vacuously true since before this feature started.** The real
   claim (SC-02b, `$HOME/.harness/registry.json` gone) is correctly left to inspection per the
   BRIEF's own machine-independence reasoning; this in-repo check adds no coverage of it and could
   be deleted with zero suite impact. Low severity: it costs nothing today (the real claim is
   already correctly handled elsewhere as inspection), but it is dead weight presented as a live
   check, and a future reader crediting it as "automated coverage of the registry deletion" would be
   wrong.

Neither finding is a `must_fix` — remedying either inside a signed plan/config the team didn't
scope here would be new work, not a gap this run introduces. Both are decision questions for the
lead/pm, with a recommendation attached above.

## Coverage gaps (Phase 1 expectation vs. what runs)

Derived from BRIEF's Success Criteria before reading `qa-FEAT-12-qagate.md`'s own framing, then
cross-checked against it — same conclusion both ways: **5 of 11 SCs (SC-02b, SC-04, SC-05, SC-06,
SC-09) are `verify: inspection`/`uat` and no test kind in this repo can reach them** (BRIEF's own
"Verification gaps" section says the same — `component`/`ui`/`eval`/`typecheck` all have `cmd: null`
and none would help regardless, since nothing in `test_kinds` reaches outside
`CLAUDE_PROJECT_DIR`). `matrix_ok: true` is a statement about the six automated SCs
(SC-01, SC-02, SC-03, SC-07, SC-08, SC-10), not about the feature as a whole — worth restating
because a reader skimming only `matrix_ok: true` could over-credit it.

## SC evidence (unchanged from the inherited gate, restated for findability)

| SC | Test | State |
|---|---|---|
| SC-01 | `run-unit-tests.sh` full run | satisfied |
| SC-02 | `test-check-plan-routes.py::case_21` under `--kind integration` | satisfied (Probe 1 flags the *derivation path* to this command, not the result) |
| SC-03 | `test-no-distribution.py::case3` (3 of its 4 assertions; the 4th is Probe 3's finding) | satisfied |
| SC-07 | `test-no-distribution.py::case2`, mutation-proven | satisfied |
| SC-08 | `test-no-distribution.py::case4` (6 of 7; precedence check mutation-proven) | satisfied |
| SC-10 | `test-upgrade-config.py` cases 6/7 under `--kind integration`, mutation-proven | satisfied (same Probe 1 caveat) |
| SC-02b, SC-04, SC-05, SC-06, SC-09 | none — inspection/uat by design | n/a to qa, per BRIEF |

## Items 1–4 from the dispatch

- 1, 2: SETTLED by qa's mutants — agree, not re-litigated.
- 3: OPEN, low, agree as-is — pm's to correct the case-20/case-21 label.
- 4: OPEN, low, agree as-is — exactly one file (`test-check-plan-routes.py`), `ALLOW_LIST` is
  path-scoped by plan design, remedy would require re-scoping `ALLOW_LIST` which the plan forbids.
