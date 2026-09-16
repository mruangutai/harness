# SIMPLIFICATION receipt — BUG-1699-lifecycle-cards

## Conclusion

One eligible simplification remains in the committed product diff `60b8d4d99f50edab6a63352ea43ebbc4ffc09750..212ad9ca`; no source or test was changed by this inspection. The already-applied SIMP-01 removal in `check-state.py` is not re-raised.

## Findings

- **SIMP-02**
  - **File / line:** `.claude/skills/harness/bin/board_lifecycle.py:1009-1014`
  - **Summary:** `STATION` and `STATUS` execute the same `gh_board.set_station` call with the same two data fields.
  - **Concrete cost:** Two branches encode one station-repair operation; a later change to its arguments, ordering, or error behavior must be kept synchronized and can drift.
  - **Concrete alternative:** Replace the two branches with `if finding.kind in {"STATION", "STATUS"}:` around the existing call; leave `REASON` and `LABEL` branches unchanged.
  - **Eligibility:** Eligible: this is a local code-side fold-in, preserves the identical `issue_number`/`expected` invocation and existing branch order, and deletes or weakens no assertion.

## Inspection coverage

Inspected the complete committed product diff, excluding the feature ledger, STATE, plan, BRIEF, and prior receipts as directed. Relevant lifecycle consolidation was reviewed at `board_lifecycle.py:429-1014`, `check-state.py:2222-2424`, `gh-sync.py:1447-1512`, `gh_board.py:115-154`, and `plan-merge.py:782-930,2015-2140`, with its changed instruction and test surfaces. No other substantive SIMPLIFICATION finding remains.

## Open questions

- none
