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

## Fix round 1

Source: validate run 02 (FAIL, MF-1 to MF-5). Operator rulings are in `notes/answers-2026-11-28-validate-c1.md`. Every fix ran main-session-direct.

- **MF-1 (substance, high, T-01).** An open discounted panel row now relieves a plan-team reader FAIL only when the digest's current finding with the same PF id is also discounted at a non-gating severity. The change is `_matched_row_reason` and `_discounted_non_gating` in `validate-digest.py`. The resolved-row path is unchanged.
  - **Test first.** `practicality-carveout-stale-row-current-high-denied` (a high, plausible/regression current finding over an open contrived/no_worse med row) was FAIL at the pin, with relief granted and "no errors".
  - **Mutation.** With the fix applied, removing the digest-side `_discounted_non_gating(item)` conjunct turns that case red again, and only that case.
- **MF-2 (substance, med, T-01).**
  - **New case.** `practicality-discounted-high-medmax-capped`: a discounted high finding at PASS with `severity_max: med`, so no aggregate check fires.
  - **Isolation.** Each refusal case now requires the rule's own message at its own location (`findings[0]`, `must_fix[0]`, `severity_max`, `VERDICT FAIL`).
  - **Clean acceptance.** Acceptance cases run on a security-reviewer fixture that validates clean and require no error at all. The relief case requires a clean digest too.
  - **Mutation.** Removing the `_severity_errors` call turns four cases red, the new medmax case among them. Before this round, by the code reviewer's reading, no case caught that removal.
  - Neither new case name ends in refused/relieved/carried, so T-01's red-first count stays 16 as signed.
- **MF-3 (form, T-05).** DEC-123's carve-out clause was rewritten in place (DEC-205). The matched row may now be resolved, or open with both the row and the current finding discounted at a non-gating severity; a stale discounted row whose current finding is not discounted keeps worst-wins. DEC-260's D-06 bullet says the same. The index was regenerated, with anchors only.
- **MF-4 (form, T-03/T-04).** The signed-text routing clause and "never raise a severity" now appear in `harness-product-lead.md` and the `teams/plan.yaml` lead comment. "never raising a severity and never revising kind" now appears in the `teams/validate.yaml` lead bullet.
- **MF-5 (form, T-04).** `harness-tdd-enforcement` now says the absence of exotic-input tests elsewhere "is neither a coverage gap nor a finding". `harness-verification-rules` now says "Tests target the code's plausible inputs".

### Ledger note: closing run 02

`feature-record.py close-run` from this worktree refused run 02's digest: the lead yielded it against the control plane's pre-feature schema (VAL-OQ-02), and the worktree's schema requires `exposure`. That is D-04's known residual, a lead run open while this feature's own schema change is live in the worktree. The run was closed with the control plane's `feature-record.py`, the validator its digest was yielded under, with verdict FAIL recorded. Run 03 will close the same way until the merge.
