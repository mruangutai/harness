# Receipt — main session — FEAT-2229 T-01 and T-02 (main-session-direct, DEC-174)

**BLUF.** T-01 landed as 447c2bd5 (station 77eb4125) and T-02 as 0716f498 (station 7877efcb). Both
literal verifies exit 0, `code-grade.py --base dfa52536 --head HEAD` exits 0 with no function below
bar, and check-state shows no FEAT-2229 violation. Generic task workers acting as the main
session's hands built the two tasks in parallel to one shared contract; their file sets were
disjoint. The main session integrated, verified and committed.

| Task | Verify | Red first |
|---|---|---|
| T-01 | unit 40/40, integration 91/91 (≈12 s) | `notes/red-first-T-01.md`: unit 13/40, integration 42/90 on unchanged source |
| T-02 | `test-plan-team.py` 182/182 (≈3.5 s) | `notes/red-first-T-02.md`: 30 of 153 failing pre-edit; 30 mutation witnesses each redden their own assertion |

## Main-session integration changes

- `plan_merge/check.py` `_is_draft` reads `factory_config.FINISHED_STATIONS` instead of a local
  `TERMINAL_STATIONS` tuple. The FEAT-61 structure lock refused the respelled station literal
  (test-checker-structure-locks.py). `is_finished()` was not used because it raises on a plan with
  no `status`.
- `tests/integration/canonical-reader-classification.json`: a row for
  `plan_merge/check.py::_era` (`load_harness_json`, canonical). The audit reports 0 unresolved.
- `.harness/harness.json` `decision_dispositions_era_start: "2026-11-22T01:58:29Z"` (the instant it
  was set). `templates/harness.json` is `null`.

## Full matrix at the T-02 tip (before the lock fix, then re-run)

- `run-unit-tests --kind unit`: rc 0.
- `run-unit-tests --kind integration`: rc 1 only on test-checker-structure-locks.py (the station
  literal above). After the fix: structure-locks rc 0, T-01 verify rc 0, test-plan-merge rc 0.
- check-plan-routes rc 0; check-instruction-paths 0 violations; layout_migration rc 0;
  check-skill-weight rc 0.

## Decisions to put before the panel

- harness-pm Mode 2 names `<repo-relative DECISIONS.md path>` in its `git show` instruction, not
  the literal harness path. An unanchored literal path trips check-instruction-paths (DEC-214),
  and segment repositories have their own DECISIONS.md.
- The validator-lead rule sits in `## The gate`, the plan's file anchor, rather than a separate
  "assessment" section.

## Known, not this feature's

`plan-merge.py check` on this plan reports 2 failures: T-01's `create: true` entries now name
existing files. FEAT-2225's shipped plan fails the same way (T-04 `create: true`). This is the
tool's existing behaviour once a created file exists. CI does not run plan-merge check on landed
plans. It is a backlog candidate, not a FEAT-2229 defect.
