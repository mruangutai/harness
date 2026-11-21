# BUG-20261006 fix c2 evidence (main session, DEC-174), 2026-11-21

Validate run `2026-11-21-2-validator` (pin `a80b9ef3`) returned **BLOCKED**, with a substantive FAIL and two must_fix items.

## 1. High (T-01 / SC-01): LABEL bypassed `resolve_binding`

**Before.** `_label_record_owner` treated a record whose `factory.repo` string equalled the audited repository as an owner. It never called the authoritative resolver. QA c4 (`notes/review-harness-qa-c4.md`) executed four resolver-refused variants, and in each one `reconcile --apply` still added `abandoned` to #17:

- A: undeclared in the fleet.
- C: served config with sync off.
- D: served config unavailable.
- E: served config naming another repository.

**Regression (`9d4f1cb9`, committed red first).** `tests/integration/test-board-lifecycle.py` `_LABEL_BINDINGS` runs both `audit` and `reconcile --apply` on six fixtures:

- **Foreign collision.** A record bound to `acme/other`: no finding, no write, no residual.
- **Refused bindings A, C, D and E.** No `LABEL: issue #17` finding, no `issue edit`, and a report-only `FEAT-BOUND's tickets cannot be judged` residual.
- **Valid control B.** Declared in the fleet, and the served config has sync on and names `acme/widget`. Gives the finding and exactly one label write. This replaces c1's positive case, which QA showed was really variant A, an undeclared binding.

**Base** (pre-fix `board_lifecycle.py`, first run of `9d4f1cb9`): A, C, D and E FAIL; foreign collision and B PASS. This matches the QA c4 table row for row.

**Fix (`587e591b`).** For a record bound to the audited repository, `_label_record_owner(root, feat_dir, doc, repo_name)` now:

1. Takes the repository from `feature_schema.resolve_binding(doc, root)`, the same call and `FleetError` handling STATUS uses.
2. Turns a refusal into `invalid feature binding: <resolver error>`, a report-only residual.
3. Applies the mirror evidence and provenance checks only after the resolver has accepted the binding.

Two cases skip the resolver:

- A record bound to another repository is skipped before resolution, because it can never own this repository's numbers.
- An unbound record resolves through the owner binding.

**Mutant.** M-STRING restores the pre-c2 rule that trusts the `factory.repo` string (`bound_repo = repo_name`). Result: **KILLED**, with A, C, D and E FAIL and `test-board-lifecycle.py` rc 1. The source was restored byte-for-byte.

## 2. QA return contract (form, low)

This item is a reader-return defect inside the validator team, not a source change. The fix run re-dispatches the readers and needs a schema-valid QA return. This cycle changes no source for it.

## Green (`587e591b`)

- `test-board-lifecycle.py`: rc 0, all six binding variants PASS.
- `code-grade.py --base fbff8150 --head 587e591b`: all 24 changed functions PASS their bars.
- pyflakes is clean on the touched files.
- Configured kinds: unit 61/61 files and integration 87/87 files, both exit 0.
- `check-plan-routes.py --canonical-reader-audit`: **misread here.** I took the "0 unresolved" summary line as clean, but the checker exited 2 with two CLASSIFICATION findings. Both c1 and c2 read the summary through `| tail`, which hid the exit code. See the post-pin correction below.
- `check-instruction-paths.py`: 68 files, 0 violations.

## Post-pin correction (after validate PASS at `91f1d0c6`; found by CI on PR #2231)

**What CI's `checks` job found.** The canonical-reader audit failed on two rows:

- The live `board_lifecycle.py::_label_owned_numbers` `load_feature_json` site had no inventory row.
- The `_recorded_issue_numbers::json_file#1` row was stale. Fix c1 removed that function.

**Correction.** In `tests/integration/canonical-reader-classification.json`, the stale row was replaced by a row for the live site:

- category `load_feature_json`, disposition `canonical`, `main-session-direct`;
- owned by this plan's T-01, whose files already list `board_lifecycle.py`.

Afterwards the audit exits 0 (measured on its own exit code this time), and the plan-route gate exits 0.

**Scope.** This changes classification metadata only; no behaviour changes. The reviewed reader call is byte-identical to the one the readers validated at `91f1d0c6`.

**Handoff header.** `notes/handoff-validate.md` also had its `seq` corrected from 3 to 7, the number of runs recorded when it was written, which INV-40 requires.

**Local CI gate reproduction, each step's own exit code:** `validate-feature-json` 0, plan routes 0, reader audit 0, instruction paths 0, layout 0, `check-state` 0.
