# FEAT-2622 main-session build receipt

Under DEC-174, every task ran `main-session-direct`. The base is `3e979ae3`.

## Tasks

| Task | Commit | Verify |
|---|---|---|
| T-01 | `0daddfc4` | exit 0; red-first 16 of 16 (`notes/fail-first-T-01.md`) |
| T-02 | `e1df4ca7` | exit 1 on the SC-14 block only; red-first 5 of 5 (`notes/fail-first-T-02.md`) |
| T-03 | `8caea5f8` | exit 0; "agent bodies ok; SC-13 red at the schema-only state" |
| T-04 | `19fafeef` | exit 0; "guidance ok" |
| T-05 | `b7cf91bc` | exit 0; "decisions ok" |

## Deviations from the signed task text

1. **T-01, an added fixture key.** In `tests/unit/test-validate-digest-plan-rollup.py`, `write_fan_in` copies a fixed key tuple from each witness finding into the record-panel fan-in. `exposure` was added to that tuple. Without it, T-02's writer refuses the fan-in and `bug2582-producer-witness` turns red. The file is in T-01's list, and no expected value changed.
2. **T-02, the SC-14 block.** Base's `test-plan-merge.py` aborts its process pool on a ValueError in the f10 case before it prints a report, so the block's harness cannot find the line it asserts. The red it asserts was measured directly, by running base's `case_f59_record_panel_writes_from_a_lead_digest` alone against the built writer: `FAIL  record-panel exits 0 on a well-formed lead digest`, rc=5, naming exposure. Detail is in `notes/fail-first-T-02.md`.
3. **T-05, no "Amended by" lines.** Step 2 asked for an "Amended by DEC-260" line appended to DEC-206 and to DEC-123. DEC-205 ended that convention: an entry states current truth, and a correction rewrites the entry it corrects. No other entry carries such a line. DEC-206's and DEC-123's clauses are rewritten in place, so both name the practicality rule, and the verify passes without the appended lines.

## SIMPLIFY pass

As in BUG-2582, the main session ran the four angles itself, read-only, over `3e979ae3..b7cf91bc`.

- **Reuse.** One predicate (`is_discounted`, `is_non_gating`, `practicality_fault`) lives in `panel_findings.py`. `validate-digest.py`, `record-panel` and `shape_faults` all call it, and `gates_signature` now reads the same `is_non_gating`. Nothing is duplicated.
- **Simplification.** Applied: the code-grade splits below.
- **Efficiency.** Empty. Each check is one pass over a digest's findings list.
- **Altitude.** Left as is. Digest refusals sit in `validate-digest.py` beside the other semantic gates. The panel-row ceiling sits in the row shape, and the writer refusal sits in `record-panel`.

### Code grade

`code-grade.py --base 3e979ae3` graded four changed functions at 2, against a bar of 4: `exposure_faults`, `shape_faults`, `_practicality_errors` and `_discounted_verdict_errors`. They were split, with no change in behaviour:
- `_exposure_key_faults` and `_exposure_value_faults`;
- `_exposure_row_faults`;
- `_severity_errors` and `_unrated_errors`;
- `_severity_max_errors` and `_reviewer_fail_errors`.

After the split, every changed function passes. The T-01 and T-02 suites were re-run after the apply.
