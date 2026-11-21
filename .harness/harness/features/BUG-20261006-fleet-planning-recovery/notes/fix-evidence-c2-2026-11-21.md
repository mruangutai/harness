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
- `check-plan-routes.py --canonical-reader-audit`: 0 unresolved reader sites.
- `check-instruction-paths.py`: 68 files, 0 violations.
