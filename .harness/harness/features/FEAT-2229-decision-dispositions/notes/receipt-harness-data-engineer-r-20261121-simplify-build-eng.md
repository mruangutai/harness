# Receipt: harness-data-engineer, SIMPLIFICATION angle, r-20261121-simplify-build-eng

BLUF: 3 low, nonblocking findings, all in `plan_merge/check.py`. No gate failure. No source edited.

## Inspected
Full `git diff dfa52536..6c4da464` for `harness_yaml.py`, `plan_merge/{check,panel,union}.py` and `.harness/harness.json`. Also the structure of `tests/unit/test-decision-disposition-schema.py` and `tests/integration/test-plan-decision-dispositions.py`, the `test-plan-team.py` section 10 diff, and `canonical-reader-classification.json`. Angle: `angle-simplification.md`, with the deletion test. `delete-first.md` read and applied.

## Findings
- **S-1, check.py `_heading_level(line, dec=None)` (~l.204 of the diff, `_heading_level`):** one function has two jobs. With `dec` it asks "does this heading name `dec`", and without it, "what level is this heading". The cost is a boolean-ish zero return plus a regex built per line. Alternative: `_heading_level(line)` plus a separate `_names_dec(line, dec)` used only by `_Authority.section`. Apply-eligible (dev-ops, check.py), purely cosmetic.
- **S-2, check.py `_row_faults`, `_replacement_faults`, `_disposition_faults` (ctx tuple):** the positional tuple `(authority, plan_ids, owned)` is passed through three functions. They unpack it (`authority, plan_ids, owned = ctx`) or index it (`ctx[0]`). Cost: the reader has to track positional meaning across three signatures. Alternative: a small `typing.NamedTuple`, or compute `plan_ids` and `owned` on `_Authority`. Apply-eligible, low.
- **S-3, check.py `_successor_fault(row, authority, plan_ids)` vs `harness_yaml._successor_fault(row)`:** same name in the two modules, with different meaning. harness_yaml checks the shape of a successor. check checks whether it resolves. Cost: a grep or traceback is ambiguous. Alternative: rename check's to `_successor_unresolved`. Apply-eligible, low.

## Checked and not flagged (deletion test)
- check.py `isinstance(row, dict)` guards and `.get(...)` on rows are NOT redundant with the loader's row validation. `check` loads with `harness_yaml.load_file`, which does not call `validate_plan_doc`. Deleting those guards would crash on a malformed row.
- `DEC_ID_RE` / `SUCCESSOR_RE` in harness_yaml vs `INDEX_ROW_RE` in check match different things: id shape, successor shape, and index row. Not duplicates.
- `_instant` serves both the era and the stamp. `_eligibility` / `_era` / `_is_draft` each have distinct callers. Loader-vs-check absence split is stated and settled (D-01 / DEC-254).
- union.py `_refuse_drafted_at_write` is called at three sites (the apply path, the seed path, and before the last-writer-wins switch). The comment states the present fact, and the repeated call is the anchor, not trimmable.
- panel.py `OWNED_KEYS` row: one line, load-bearing. harness.json: key plus note, settled.
- canonical-reader-classification.json: one generated-style row for `_era`, expected. Tests (flag-only lane): table-driven helpers, no duplication found.

## Skips
Did not run `code-grade.py` (no tools/suites per contract). Hand grading: the new functions are short and single-purpose. The largest are `_disposition_faults` (about 5 branches), `_row_faults` and `_era`, none of which I judge below the production bar by reading. [INFERENCE]

## Status
No source edited, no suite run, no commit. Only write: this receipt.

## Addendum: prose, template, agent and docs paths (same SIMPLIFICATION angle)

Coverage: git diff dfa52536..6c4da464 for patch-lane.md, teams/plan.yaml, teams/validate.yaml, templates/harness.json, templates/plan.yaml, .harness/harness.json, DECISIONS-INDEX.md, DECISIONS.md (DEC-188 rewrite, DEC-254), SPEC.md (4 hunks), .omp/agents/harness-pm.md, harness-validator-lead.md. Read-only, flag-only lane (skills/roles NOBODY, docs product/documentor). No source edited.

Findings (1 additional, low, nonblocking):
- **P-1** `.harness/harness/docs/SPEC.md` (new "Decision dispositions are part of the declaration" block in section 11.2, and the "At validate, pm also grades..." block near section 11.6) vs `DECISIONS.md` DEC-254 ("One record, existing machinery", "Creation, not signature, determines the era", "Landing is a separate falsifiable outcome") vs DEC-188's rewritten third paragraph. The same mechanical check list (index resolution, STRUCK keep/amend refusal, verbatim clause in own section, successor resolution, owning task, era rule, pm landing rule) is restated in three docs places. Cost: any later rule tweak (e.g. era boundary, STRUCK matching) needs 3 doc edits and the copies can drift. Prompts in separate dispatches (plan.yaml, pm, validator) are excluded because they cannot share context. Alternative: keep the full contract in DEC-254 only; reduce the DEC-188 paragraph and SPEC 11.2/11.6 to a two-line summary plus "see DEC-254". Owner: product/documentor, flag-only.

Checked, not flagged:
- DECISIONS-INDEX.md: ~50 `@offset` rows shifted mechanically by DEC-188/DEC-254 growth; generated, not authored duplication.
- templates/harness.json and `.harness/harness.json` `_..._note` strings: one key's in-place doc, matching the neighbouring `_seam_era_start_note` precedent.
- patch-lane.md, validate.yaml and validator-lead lines: one short line each, no restatement beyond a pointer.
- pm Mode 2 `<repo-relative DECISIONS.md path>`: settled per dispatch.
