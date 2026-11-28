# BUG-2582 build receipt: main-session-direct (DEC-174)

All five tasks are `execution_mode: main-session-direct`. The main session built them in the product checkout on `feat/BUG-2582-plan-station-and-rollup`, from base `e6960865`, in the order the plan's dependencies require: T-01, T-04, T-05, T-02, T-03.

| Task | Commit | Verify |
|---|---|---|
| T-01 apply converts a station-only record; INV-34 names it | `8a4ee262` | exit 0: unit file all PASS, `harness_yaml.py` byte-identical to base, "red-first ok", `test-plan-merge.py`, `test-harness-yaml.py` and `test-check-state-plans.py` pass |
| T-04 witness: plan start on an apply-written stub, then conversion | `8eae6be8` | exit 0: 63 of 63 cases, "red-first ok" (stub-convert-after-start fails at base with apply exit=5) |
| T-05 the plan team's apply step runs `set-panel` | `445d2d6b` | exit 0: "apply step ok"; the producer check shows only its two baseline FAIL lines |
| T-02 the plan-team reader carve-out | `6c50f925` | exit 0: 27 of 27 unit cases, "red-first ok", `test-validate-digest.py` ALL PASSED |
| T-03 DEC-123, DEC-254 and DEC-228 amended; SPEC and harness-team | `48cfcefd` | exit 0: "decisions ok"; the generated index matches the file |

## Test-first evidence

- `notes/fail-first-T-01.md` and `notes/fail-first-T-02.md` record RED against the unchanged tree, then GREEN.
- T-04's red proof is in its own verify: with base `union.py` swapped into the private bin, `stub-convert-after-start` fails with apply exit=5 and the loader diagnostic, while the other two cases pass.
- T-03 is `docs` and T-05 is `config`; both are exempt.

## Deviations from the signed task text

1. **T-01's finished-station fixture.** The proposal now carries the same finished station as the base. With `status: plan` it stopped at the plain-key CONFLICT (7) and never reached conversion. Details in `notes/fail-first-T-01.md`.
2. **T-01's `CHECK_STATE_REV` archive.** It now covers `.claude/skills/harness`, not just `bin/`, because the checker reads its sibling `schemas/` at startup.
3. **T-05's `plan-phase.md` bullet.** "Both verbs are pm's" now reads "All three verbs", since `set-panel` joined `record-panel` and `check`. The task said "change nothing else in that section"; leaving "Both" would have made the sentence false. The producer check's FAIL set is unchanged.
4. **T-02's fixture root.** It carries `.harness/team-config.yaml` and `harness.json`, so the producer witness's `plan-merge.py` calls resolve the fixture as their root.

## Orchestrator record fix

After plan run 01 closed, the main session (as orchestrator) had not run `plan-phase.md`'s post-run `record-panel --digest <run_dir>/digest.md`. INV-32 then reported the `goalcheck` reader as unrecorded. It was recorded at T-03's commit:
- `panel.readers` now lists all four readers;
- approval stayed `approved`;
- all 6 findings stayed `resolved`;
- check-state reports 0 violations.

## SIMPLIFY pass

Under DEC-174 the main session ran the four angles itself, read-only, over `e6960865..48cfcefd`.

- **Reuse.**
  - `_creation_seed` repeats the two literal approval lines `_seed_new_plan` writes. Folding them would change `_seed_new_plan`, which the signed task does not touch. Left as is.
  - The test's `materialize_checker` is a widened copy of `test-check-state-inv35.py`'s. That is test-local, so it was left as is.
- **Simplification.** Applied: `_plan_reader_carveout` and `_carveout_rows` each rebuilt the team-digest findings list. It is now built once and passed down.
- **Efficiency.** Empty. The carve-out runs only for a product-lead `team: plan` digest with a reader at FAIL, and only reads `feature.json` and `plan.yaml` once.
- **Altitude.** Left as is. The conversion sits in the writer, and the loader pair stays byte-identical (D-01). The carve-out sits in the roll-up it qualifies.

### Code grade

`code-grade.py` graded five changed functions below the bar of 4: `_convert_station_only` (2), `apply_merge`, `_dump_merged`, `_candidate_reason` and `_worst_member` (3 each). All five were at 4 on base. They were split into small helpers:
- `_convert_then_reset`;
- `_converts`, `_without_top_key`, `_creation_seed` and `_seeded_after_feature`;
- `_mark_converted`;
- `_open_row_reason`;
- `_ranked_member_verdict`.

Every changed function now grades 4 or 5. After the last edit, the T-01, T-02 and T-04 literal verifies all exit 0.

## Fix round 1 (validate run 2026-11-27-02, ESCALATE)

The operator's rulings are in `notes/answers-2026-11-27-validate-c1.md`.

- **MF-1, fixed in full (the operator's choice).** All three parts are in `validate-digest.py`:
  - (a) `_slot_reason` requires exactly one entry per reader slot; a skipped one counts.
  - (b) Each slot's persona must match `PLAN_READER_PERSONAS`, the team file's own spellings. `bug2582-reader-personas-match-team-file` fails if `teams/plan.yaml` drifts from it. A constant was chosen over a live team-file read: no `bin/` code reads team files, and the canonical-reader inventory has no exemption class for one.
  - (c) `_carveout_feature_dir` refuses relief when the hook's live `harness_mission` is set and is not `plan`. Offline, `feature.json` decides alone (OQ-3).
  - The new cases `deny-missing-slot`, `deny-persona-swap` and `deny-dispatch-mission-patch` are each red against the c1171867 validator (accepted with no errors) and green now. The first persona-swap fixture was refused at c1171867 for a different reason, so it was replaced by a wrong-persona scope slot with slot-spelled findings, which c1171867 accepted.
- **MF-2.** Both catches are narrowed: `(FeatureJsonError, OSError)` and `(YamlParseError, OSError)`. `PlanSchemaError` subclasses `YamlParseError`.
- **MF-3.** The ledgered amendment `T-02.files` adds `tests/integration/canonical-reader-classification.json`. Two canonical rows were added: `_carveout_plan::load_feature_json#1` and `_carveout_plan::load_plan#1`.
- **MF-4.** The DEC-123 index ruling is now 28 words and still names the carve-out. DEC-123 and SPEC now state MF-1's roster and mission conditions.
- **MF-5.** The test's `main()` is split into case tables. `case_producer_witness` (grade 2) and `_carveout_plan` (grade 3, after MF-1c added a branch) were split too.
- **Advisory added.** `bug2582-guard-eng-lead-plan-steps`: an eng-lead digest with plan reader steps is still refused. It was first named `other-lead-eng-plan-steps`, which collided with the T-02 verify's prefix match on `PASS bug2582-other-lead-eng`, so it was renamed.

After the last edit:
- `test-validate-digest-plan-rollup.py`: 34 of 34 pass.
- The T-02 literal verify exits 0, with "red-first ok" and ALL PASSED.
- `test-check-plan-routes.py`, `test-broad-catch-census.py`, `test-checker-structure-locks.py` and `test-gen-decisions-index.py` all exit 0.
- The T-03 verify prints "decisions ok".
- Every changed function meets its grade bar. The only sub-bar function in `validate-digest.py` is the untouched, pre-existing `reviewed_python_change` (grade 2).
