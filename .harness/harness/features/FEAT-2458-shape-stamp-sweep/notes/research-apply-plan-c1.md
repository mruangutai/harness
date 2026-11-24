# FEAT-2458 — reader wave c1 applied

**All eight panel findings are applied to BRIEF.md and plan.yaml. `record-panel` exited 0, and so did `check` (2 tasks, 7 anchors, 0 failures).** No `APPROVAL-RESET:` receipt was printed, because the plan is still pending, so `gh-sync` was not called. The two form findings are `resolved`. The six substance and proportionality findings stay `open` for the lead to re-gate T-01 and T-02.

## Dispositions

| PF | Kind / sev | Disposition | What changed |
|---|---|---|---|
| 9ad7c484 prefix match deletes wrong stamp | substance high | applied (open, re-gate T-01/T-02) | T-01 intent: `classify_feature` matches ids exactly. It checks the harness `names` first, then each `_fleet_segments` segment's names, and still routes through `_landed_classification`. It never calls `_match_landed_id`, `_planning_segment` or `_resolve_landed`. `classify`/`classify_all` are untouched. New rows (i) absent-prefix → unresolved/absent and (j) exact fleet beats a longer harness id → terminal. T-01 verify gained an AST check that `classify_feature` calls `_landed_classification` and none of the three prefix helpers; that check was proven on three synthetic bodies. T-02 fixture adds FEAT-912-stamp-absent-longer at Done, and assert (7) requires the absent stamp to be kept. New D-03 records exact identity as the rejected-alternative decision. SC-01/02/03 reworded. |
| dd345693 undecodable landed record aborts sweep | substance med | applied (open, re-gate T-01/T-02) | Premise reproduced: on a real committed `\xff` blob, `subprocess.run(text=True)` raised UnicodeDecodeError. T-01 step 2 wraps only `_landed_blob_text`'s cat-file call in `except UnicodeDecodeError` and returns `"unparseable"`. Row (k) covers it. T-02 fixture adds FEAT-909-stamp-bad, which sorts before the done stamp. Assert (8) requires that stamp to be kept with one unresolved, non-absent line, and (4) requires the later done stamp to still be removed. SC-01/03/05 reworded. |
| d1451124 SC-11 post-merge UAT | form med | fixed in place, resolved_by T-02 | SC-11 is deleted. Verification gaps now names the real-checkout listing as a post-merge operational check that gates nothing (DEC-74). T-02 traces drop SC-11, and its closing paragraph is reworded. |
| 464bf3e6 missing keep rows | form low | fixed in place, resolved_by T-01 | `decisions_affected` gained keep rows for DEC-221, DEC-191 and DEC-252. Their clauses are single-line verbatim substrings, as `check` requires. T-01/T-02 intents now cite the DECs they read. DEC-74 needs no row, because no `uat` SC remains. |
| 74d8eda7 + bb8bb7d3 FEATURE_CLASSES | proportionality task low + substance low | applied together (open) | T-01 publishes no tuple and asserts literal klass values. The docstring surface line no longer names it. |
| 7dd2962d `_landed_names` extraction | proportionality task low | applied (open) | The extraction mandate is dropped, and T-01 now forbids modifying `_resolve_landed`. Exact identity also makes the shared lookup inapplicable. |
| 007b122a SC-06 re-checks verify greps | proportionality task low | applied (open) | SC-06 keeps only the reads-no-records clause. Helper removal is now carried behaviourally by SC-07: the T-07 contract compares the registry and inventory against `_scan_reader_tree(ROOT)` plus `_t07_extra_findings`. [INFERENCE] I did not run the extra-finding path against a tree where the helper survives. |

## Draft questions

- Q-01 (`not_terminal` spelling) is still an operator question. Dropping FEATURE_CLASSES removes the published tuple but keeps the literal.
- Q-02 (removal lines) is still an operator question. No finding touched it.

## Notes

- The DEC-191 clause carries backticks verbatim, as other plans' clauses do; `check` compares raw substrings.
- The check-state `--changed` VIOLATION lines on every write (BRIEF not approved; INV-37 has no build-entry receipt) are the expected pre-signature state. This apply step did not cause them.
