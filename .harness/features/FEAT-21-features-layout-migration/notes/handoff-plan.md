# Handoff — FEAT-21-features-layout-migration, plan → build — written at 62fef85, seq-2

## Next

The main session writes both approval blocks (BRIEF.md `## Approval`, plan.yaml `approval:`); no
further plan work is owed. Then: all 10 tasks are `execution_mode: main-session-direct`, so there
is no eng segment to dispatch — hand them to layer 0 as dependency-ordered segments, T-01 alone
first (its own commit, issue #387's parity test), then T-02..T-10 as the single atomic commit that
T-09 lands and verifies. Expect FEAT-20's T-01/T-02 hand-off shape.

## Trust

- The three ruled edits landed and I verified each at source: T-06's and T-10's region-anchored Q3
  clauses, `lanes.measurement` crediting pm, T-10's sha anchors — plan.yaml:608-618, :886-896, :16
  — verified-at 62fef85
- Both new clauses are RED today, so they can report failure: case_22a asserts exit code and
  `"FEAT-A" in r.stderr` only, no path text (test-check-plan-routes.py:549-551), and
  `migrated_depth` occurs 0 times in test-validate-feature-json.py — I ran both counts —
  verified-at 62fef85
- The plan is route-clean and unsigned: `check-plan-routes.py` reports 0 violations across 1 plan,
  `approval.status: pending` — I ran it after the revision — verified-at 62fef85
- `tests.yml`'s "returns 8" is FALSE at base and T-10 corrects it rather than dating it: `git
  ls-files '.harness/features/*/PLAN.md' '.harness/features/*/plan.yaml'` returns 19 at HEAD, 8 at
  eafc8ad — I ran both — verified-at 62fef85. `git check-ignore -v .harness/features` still exits 1
- Detector and INV-27 are GREEN at base, all-legacy: `layout_migration.py` exits 0 with both
  surfaces `CLEAN — evidence legacy` over 20 feature dirs, `check-state.sh` exits 0 with no INV-27
  line — I ran both — verified-at 62fef85
- `harness` is ALREADY a declared segment, so NO fleet.yaml edit belongs in this feature —
  `layout_migration.py:144-161` derives it from `harness.json` `github.repo`, independently of
  fleet.yaml where `mruangutai/harness` is deliberately absent (DEC-174 am.1) — verified-at 62fef85
- The four Q1 override sites break for real post-move and three are invisible to a literal sweep —
  `test-factory-cli.py:151-153` (module-scope open, ImportError kills the suite), `gh-sync.py:729`
  (three-level climb), `validate-feature-json.py:41` (scans zero files silently),
  `branch-create-gate.sh:77-78`, `.gitignore:7` — I read all five — verified-at 62fef85
- The plan run's consolidated digest is GONE — the revision reused `runs/2026-08-14-1-product/` and
  overwrote it. Substance survives in runs/2026-08-14-1-eng/digest{,-recheck}.md and both
  notes/review-harness-ui-reviewer-*.md — I listed the dir — verified-at 62fef85

## Dead ends

- The docs surface, `docs/harness/**`, and the three DOCS reader rows — unit 4's atomic commit; I
  enumerated all 42 files across the ten tasks and none appears — verified-at 62fef85
- The two MIXED-FOREVER items (`gen-decisions-index.py` docstring, `harness_boundary.py` comments)
  — intended behaviour until unit 4, not false positives — layout_migration.py docstring — verified-at 62fef85
- Re-adding `mruangutai/harness` to fleet.yaml — see Trust; a decision, not a convenience
- Reopening Q1-Q6/Q8 — the operator ruled all of them in one pass —
  notes/answers-2026-08-14-signature.md — verified-at 62fef85
- A prototype: `harness-visual-designer` ruled `prototype_required: false` on its own inspection —
  every surface is CLI diagnostic text — verified-at 62fef85

## Working set

- `.harness/features/FEAT-21-features-layout-migration/plan.yaml` (10 tasks, 8 decisions, lanes)
- `.harness/features/FEAT-21-features-layout-migration/BRIEF.md` (14 SCs)
- `.harness/features/FEAT-21-features-layout-migration/STATE.md` (three builder advisories)
- `.harness/features/FEAT-21-features-layout-migration/notes/answers-2026-08-14-signature.md`
- `.claude/skills/harness/bin/layout_migration.py` (pattern rule, MIXED-FOREVER rule, reader table)
